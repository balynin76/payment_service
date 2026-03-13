import pytest
from sqlalchemy import text
from src.infrastructure.db.models import Base
from tests.conftest import test_engine

@pytest.mark.asyncio
async def test_tables_created():
    """Проверка что таблицы действительно создаются"""
    print("\n=== Testing table creation ===")
    
    # Проверяем метаданные
    tables = list(Base.metadata.tables.keys())
    print(f"Tables in metadata: {tables}")
    assert 'orders' in tables
    assert 'payments' in tables
    
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Проверяем, что таблицы созданы в БД
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        db_tables = [row[0] for row in result.fetchall()]
        print(f"Tables in database: {db_tables}")
        
        assert 'orders' in db_tables
        assert 'payments' in db_tables
    
    print("✅ Tables created successfully in database")
