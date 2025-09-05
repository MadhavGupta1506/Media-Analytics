from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from pathlib import Path
from collections import defaultdict
import aiofiles

from .. import models, schemas, database, security

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


# -------- Upload Media --------
@router.post("/media", response_model=schemas.MediaOut)
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


# -------- Generate Stream URL --------
@router.get("/media/{media_id}/stream-url", response_model=schemas.StreamURL)
async def generate_stream_url(
    media_id: str,
    request: Request,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    token = await security.create_stream_token(media_id)
    stream_url = f"{request.base_url}media/stream/{media_id}?token={token}"

    return {"stream_url": stream_url}


# -------- Stream Media --------
@router.get("/media/stream/{media_id}")
async def stream_media(
    media_id: str,
    request: Request,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),  # ✅ use normal JWT auth
):
    # Fetch media asynchronously
    result = await db.execute(
        select(models.MediaAsset).where(models.MediaAsset.id == media_id)
    )
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Log view asynchronously
    log = models.MediaViewLog(
        media_id=media_id,
        viewed_by_ip=request.client.host if request.client else None
    )
    db.add(log)
    await db.commit()

    return FileResponse(media.file_url)

# -------- Log Media View (Optional Manual Call) --------
@router.post("/media/{media_id}/view")
async def log_media_view(
    media_id: str,
    request: Request,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    result = await db.execute(select(models.MediaAsset).where(models.MediaAsset.id == media_id))
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    ip_address = request.client.host if request.client else "unknown"
    view_log = models.MediaViewLog(media_id=media_id, viewed_by_ip=ip_address)
    db.add(view_log)
    await db.commit()

    return {"message": "View logged successfully", "media_id": media_id, "ip": ip_address}


# -------- Get Media Analytics --------
@router.get("/media/{media_id}/analytics")
async def media_analytics(
    media_id: str,
    db: AsyncSession = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
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

    return {
        "total_views": total_views,
        "unique_ips": unique_ips,
        "views_per_day": dict(views_per_day)
    }
