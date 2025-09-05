import os
from fastapi import HTTPException
from pathlib import Path

from ..security import verify_stream_token

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))


def get_media_filepath(media: dict) -> str:
    """
    Return local filepath for media.
    """
    file_url = media.get("file_url")
    filepath = Path(file_url)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Media file not found")
    return str(filepath)


def validate_and_get_media_id_from_token(token: str) -> str:
    """
    Validate stream token and return the media_id it represents.
    """
    return verify_stream_token(token)
