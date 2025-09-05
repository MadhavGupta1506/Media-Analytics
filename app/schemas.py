from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


# -------- Enums --------
class MediaType(str, Enum):
    video = "video"
    audio = "audio"


# -------- Auth Schemas --------
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------- Media Schemas --------
class MediaBase(BaseModel):
    title: str
    type: MediaType


class MediaCreate(MediaBase):
    file_url: str


class MediaOut(MediaBase):
    id: int
    file_url: str
    created_at: datetime

    class from_attributes:
        orm_mode = True

class StreamURL(BaseModel):
    stream_url: str
    

# -------- Analytics Schemas --------
class AnalyticsData(BaseModel):
    media_id: int
    total_views: int
    unique_viewers: int
    average_watch_time: float  # in seconds 
