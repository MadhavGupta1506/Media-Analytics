from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import uuid4
import os

from .. import models, schemas, database, security

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/media", response_model=schemas.MediaOut)
def upload_media(
    title: str = Form(...),
    type: schemas.MediaType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4()}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    media = models.MediaAsset(title=title, type=type, file_url=filepath)
    db.add(media)
    db.commit()
    db.refresh(media)

    return media


@router.get("/media/{media_id}/stream-url")
def generate_stream_url(
    media_id: str,
    request: Request,
    db: Session = Depends(database.get_db),
    _current_user: models.AdminUser = Depends(security.get_current_user),
):
    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    token = security.create_stream_token(media_id)
    stream_url = f"{request.base_url}media/stream/{media_id}?token={token}"

    return {"stream_url": stream_url}


@router.get("/media/stream/{media_id}")
def stream_media(
    media_id: str,
    token: str,
    request: Request,
    db: Session = Depends(database.get_db),
):
    verified_id = security.verify_stream_token(token)
    if str(media_id) != verified_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    media = db.query(models.MediaAsset).filter(models.MediaAsset.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    log = models.MediaViewLog(media_id=media_id, viewed_by_ip=request.client.host)
    db.add(log)
    db.commit()

    return FileResponse(media.file_url)
