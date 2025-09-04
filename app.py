"""
FastAPI App Creation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .lifespan import lifespan
from .routers import auth, media, root

def create_app() -> FastAPI:
    app = FastAPI(
        title="Media Platform Backend",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(root.router, tags=["root"])
    app.include_router(auth.router, tags=["auth"])
    app.include_router(media.router, tags=["media"])

    return app