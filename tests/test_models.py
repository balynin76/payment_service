import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.models.order import Order
from src.infrastructure.db.models.payment import Payment

@pytest.mark.asyncio
async def test_models_import():
    """Проверка что модели импортируются"""
    assert Order is not None
    assert Payment is not None
    print("✅ Models imported successfully")
