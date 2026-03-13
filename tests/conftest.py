import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Тестовая БД в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем тестовый движок
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db():
    """Переопределение зависимости БД для тестов"""
    async with TestSessionLocal() as session:
        yield session

# Подменяем зависимость get_db в приложении
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="function")
async def setup_database():
    """Создает таблицы перед каждым тестом"""
    print("\n=== Creating tables ===")
    
    # Принудительно импортируем модели
    from src.infrastructure.db.models import Order, Payment
    
    # Проверяем, какие таблицы зарегистрированы
    tables = list(Base.metadata.tables.keys())
    print(f"Tables in metadata: {tables}")
    
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")
    
    yield
    
    print("\n=== Dropping tables ===")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Tables dropped successfully")

@pytest.fixture
async def client():
    """HTTP клиент для тестирования эндпоинтов"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
