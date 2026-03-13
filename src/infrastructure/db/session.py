from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import MetaData
from src.core.config import settings

# Базовый класс для моделей
Base = declarative_base()

# Метаданные
metadata = MetaData()

# АСИНХРОННЫЙ движок (важно: URL должен быть с +asyncpg)
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,  # Убедитесь, что в URL есть +asyncpg
    echo=True,
)

# Асинхронная фабрика сессий
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """Зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """Создание таблиц в базе данных"""
    print("→ Создание таблиц...")

    # ПРАВИЛЬНЫЙ АСИНХРОННЫЙ КОД:
    async with engine.begin() as conn:
        # Для создания таблиц используем run_sync
        await conn.run_sync(Base.metadata.create_all)

    print("→ Таблицы созданы")