from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,  # ← это обязательно добавить
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from ...core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,  # ← теперь это определено
    expire_on_commit=False,
)

if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,
        max_overflow=0
    )
else:
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    from src.infrastructure.db.models import Base  # ← абсолютный импорт от корня src

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы (или уже существовали)")