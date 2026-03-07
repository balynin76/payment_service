from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,  # ← это обязательно добавить
    async_sessionmaker,
    create_async_engine,
)

from ...core.config import settings

# Движок
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Сессия
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,  # ← теперь это определено
    expire_on_commit=False,
)


# Dependency для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Создание таблиц
async def create_tables():
    from src.infrastructure.db.models import Base  # ← абсолютный импорт от корня src

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы (или уже существовали)")