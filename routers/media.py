"""
Media Routes
"""
import secrets
import time
import hmac
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config
from ..database import get_db
from ..models import AdminUser, MediaAsset, MediaViewLog
from ..schemas import MediaOut
from ..security import get_current_user, sign_stream_token

router = APIRouter()

ALLOWED_TYPES = {"video", "audio"}

@router.post("/media", response_model=MediaOut, status_code=201)
async def create_media(
    title: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = type.lower()
    if t not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="type must be 'video' or 'audio'")

    safe_name = f"{int(time.time())}_{secrets.token_hex(6)}_{file.filename}"
    dest_path = config.UPLOAD_DIR / safe_name
    with dest_path.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    file_url = str(dest_path)

    asset = MediaAsset(title=title, type=t, file_url=file_url, uploaded_by=current_user.id)
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get("/media/{media_id}/stream-url")
async def get_stream_url(media_id: int, current_user: AdminUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    asset = await db.get(MediaAsset, media_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media not found")

    expires_in = 10 * 60  # 10 minutes
    exp_ts = int(time.time()) + expires_in
    sig = sign_stream_token(media_id, exp_ts)

    url = f"/stream?media_id={media_id}&exp={exp_ts}&sig={sig}"
    return {"stream_url": url, "expires_at_unix": exp_ts}

@router.get("/stream")
async def stream_media(request: Request, media_id: int, exp: int, sig: str, db: AsyncSession = Depends(get_db)):
    now = int(time.time())
    if now > exp:
        raise HTTPException(status_code=403, detail="Link expired")

    expected_sig = sign_stream_token(media_id, exp)
    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(status_code=403, detail="Invalid signature")

    asset = await db.get(MediaAsset, media_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media not found")

    client_ip = request.client.host if request.client else "unknown"
    log = MediaViewLog(media_id=media_id, viewed_by_ip=client_ip)
    db.add(log)
    await db.commit()

    path = Path(asset.file_url)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(path)
