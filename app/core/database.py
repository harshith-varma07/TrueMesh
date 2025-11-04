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


# Create engines lazily
_engine = None
_async_engine = None


def get_engine():
    """Get or create the synchronous database engine"""
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def get_async_engine():
    """Get or create the asynchronous database engine"""
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_database_engine()
    return _async_engine


# Create session makers lazily
_SessionLocal = None
_AsyncSessionLocal = None


def get_session_local():
    """Get or create the session maker"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_async_session_local():
    """Get or create the async session maker"""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _AsyncSessionLocal


def get_db() -> Session:
    """Dependency for getting synchronous database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting asynchronous database session"""
    AsyncSessionLocal = get_async_session_local()
    async with AsyncSessionLocal() as session:
        yield session