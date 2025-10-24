"""
Core database module for TrueMesh Provider Intelligence
"""
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


# Base class for all database models
Base = declarative_base()


def get_database_url() -> str:
    """Get the database URL for sync operations"""
    settings = get_settings()
    return settings.database_url


def get_async_database_url() -> str:
    """Get the database URL for async operations"""
    settings = get_settings()
    # Convert sync URL to async if needed
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    return url


def create_database_engine():
    """Create synchronous database engine"""
    settings = get_settings()
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def create_async_database_engine():
    """Create asynchronous database engine"""
    return create_async_engine(
        get_async_database_url(),
        echo=get_settings().database_echo,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


# Create engines
engine = create_database_engine()
async_engine = create_async_database_engine()

# Create session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def get_db() -> Session:
    """Dependency for getting synchronous database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting asynchronous database session"""
    async with AsyncSessionLocal() as session:
        yield session