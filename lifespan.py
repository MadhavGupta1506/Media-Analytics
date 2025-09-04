"""
Lifespan events for the FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from . import config
from .database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # on shutdown
