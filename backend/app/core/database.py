import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Normalize database URL for async drivers
raw_url = settings.DATABASE_URL or "sqlite+aiosqlite:///./campusconnect.db"

def normalize_database_url(url: str) -> str:
    """Normalize database URL for async drivers, removing incompatible parameters like channel_binding."""
    if not url:
        return "sqlite+aiosqlite:///./campusconnect.db"
    
    # Strip channel_binding if present (unsupported by asyncpg)
    clean = url.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("?channel_binding=require", "")
    
    if clean.startswith("postgresql://"):
        return clean.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif clean.startswith("sqlite://") and not clean.startswith("sqlite+aiosqlite://"):
        return clean.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return clean

async_db_url = normalize_database_url(raw_url)

# Configure engine kwargs
engine_kwargs = {"echo": False, "future": True}
if "sqlite" in async_db_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(async_db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

