"""Database engine and session configuration."""

import os
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def _is_neon_url(url: str) -> bool:
    """Check if URL is a Neon serverless PostgreSQL connection."""
    return "neon.tech" in url or "aws.neon" in url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """
    Create and cache the SQLAlchemy engine.

    Configures connection pooling appropriately for local vs Neon deployments.
    Neon uses connection pooling on their end, so we use smaller pools.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    # Parse optional pool settings
    pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

    # Neon-specific configuration
    if _is_neon_url(database_url):
        # Neon manages connection pooling; use smaller local pool
        # SSL is required for Neon
        connect_args = {"sslmode": "require"}
        engine = create_engine(
            database_url,
            pool_size=2,
            max_overflow=3,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    else:
        # Local PostgreSQL configuration
        engine = create_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
        )

    return engine


_SessionLocal: sessionmaker[Session] | None = None


def _get_session_factory() -> sessionmaker[Session]:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _SessionLocal


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.

    Usage as context manager:
        with next(get_session()) as session:
            # use session
            session.commit()

    Usage as FastAPI dependency:
        def endpoint(session: Session = Depends(get_session)):
            ...
    """
    session_factory = _get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database (create all tables)."""
    from .base import Base
    from . import tables  # noqa: F401 - import to register models

    Base.metadata.create_all(bind=get_engine())
