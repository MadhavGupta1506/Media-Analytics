# app/routers/media.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from pathlib import Path
import aiofiles
import json
from collections import defaultdict
from datetime import timedelta
from ..utils.rate_limit import rate_limit_ip_media


from .. import models, schemas, database, security
from ..redis_client import redis_client
from ..utils.cache import get_cached, set_cached
from ..utils.rate_limit import rate_limit_ip_media

router = APIRouter(prefix="/media", tags=["media"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=schemas.MediaOut)
async def upload_media(
    title: str = Form(...),
    type: schemas.MediaType = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    file_ext = Path(file.filename).suffix
    filename = f"{uuid4()}{file_ext}"
    filepath = UPLOAD_DIR / filename

    contents = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    media = models.MediaAsset(title=title, type=type, file_url=str(filepath))
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


@router.get("/{media_id}/stream-url")
async def get_stream_url(
    media_id: str,
    expires_in: int = Query(600, description="Expiry time in seconds"),
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    # verify existence
    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    # create stream token (sync function)
    token = security.create_stream_token(media_id, expires_delta=timedelta(seconds=expires_in))
    base = "http://127.0.0.1:8000"  # optionally use request.base_url if passed
    url = f"{base}/media/stream/{media_id}?token={token}"
    return {"stream_url": url, "expires_in": expires_in}


@router.get("/stream/{media_id}", responses={200: {"content": {"application/octet-stream": {}}}})
async def stream_media(
    media_id: str,
    token: str = Query(..., description="Presigned token"),
    request: Request = None,
    db: AsyncSession = Depends(database.get_db),
):
    # verify token (raises HTTPException 401 if invalid/expired)
    verified_id = security.verify_stream_token(token)
    if str(media_id) != verified_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # log view
    ip = request.client.host if request and request.client else None
    log = models.MediaViewLog(media_id=media_id, viewed_by_ip=ip)
    db.add(log)
    await db.commit()

    return FileResponse(media.file_url, media_type="application/octet-stream")


@router.post("/{media_id}/view")
async def log_media_view(
    media_id: str,
    request: Request,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    # rate-limiter: per-IP per-media
    client_ip = request.client.host
    await rate_limit_ip_media(client_ip,media_id)

    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    ip = request.client.host if request.client else None
    view_log = models.MediaViewLog(media_id=media_id, viewed_by_ip=ip)
    db.add(view_log)
    await db.commit()

    return {"message": "View logged", "media_id": media_id}

@router.get("/{media_id}/analytics")
async def media_analytics(
    media_id: str,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    # try cache
    cache_key = f"analytics:{media_id}"
    cached = None
    if redis_client:
        val = await redis_client.get(cache_key)
        if val:
            return json.loads(val)

    # compute
    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    logs_result = await db.execute(select(models.MediaViewLog).where(models.MediaViewLog.media_id == media_id))
    logs = logs_result.scalars().all()

    total_views = len(logs)
    unique_ips = len({log.viewed_by_ip for log in logs if log.viewed_by_ip})

    views_per_day = defaultdict(int)
    for log in logs:
        day = log.timestamp.date().isoformat()
        views_per_day[day] += 1

    payload = {
        "total_views": total_views,
        "unique_ips": unique_ips,
        "views_per_day": dict(views_per_day),
    }

    # set cache (stringify)
    if redis_client:
        await redis_client.set(cache_key, json.dumps(payload), ex=60)  # 60s TTL

    return payload
