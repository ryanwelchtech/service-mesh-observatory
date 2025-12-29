"""
Database Session Management
SQLAlchemy async session configuration
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Convert postgresql:// to postgresql+asyncpg://
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create async session factory
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # In production, use Alembic migrations instead
            # await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
