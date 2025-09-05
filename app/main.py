import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, media
from .redis_client import init_redis_pool, close_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Always initialize real Redis client for your online Redis URL
    await init_redis_pool()

    yield

    # Shutdown
    await close_redis_pool()


app = FastAPI(title="Media Platform API", lifespan=lifespan)

# Routers
app.include_router(auth.router)
app.include_router(media.router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
