from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings


def _make_engine():
    """Create engine with correct settings for SQLite vs PostgreSQL."""
    if settings.is_postgres:
        return create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    else:
        # SQLite needs check_same_thread=False
        return create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
        )


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables (runs on startup)."""
    async with engine.begin() as conn:
        from backend import models  # noqa
        await conn.run_sync(Base.metadata.create_all)
