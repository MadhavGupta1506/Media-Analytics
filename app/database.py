from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Normally load from .env or config
DATABASE_URL = "sqlite+aiosqlite:///./media_platform.db"  # Async SQLite for dev
# Example for Postgres in prod:
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL, echo=True, future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
