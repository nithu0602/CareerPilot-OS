"""SQLAlchemy database engine, session dependency, and connection lifecycle."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _engine_connect_args(database_url: str) -> dict[str, bool]:
    """Return database-driver options required by the configured database."""
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_engine_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for future domain models."""


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request and always close it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database_connection() -> None:
    """Verify that the configured database accepts a simple connection."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def dispose_database() -> None:
    """Release all SQLAlchemy connection-pool resources during shutdown."""
    engine.dispose()
