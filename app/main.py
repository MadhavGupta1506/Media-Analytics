import uvicorn
from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, media

app = FastAPI(title="Media Platform API")

# Routers
app.include_router(auth.router)
app.include_router(media.router)



@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Run in sync mode inside async engine
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
