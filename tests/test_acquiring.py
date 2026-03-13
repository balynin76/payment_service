import pytest
from decimal import Decimal
from src.infrastructure.acquiring.fake_client import FakeAcquiringClient

pytestmark = pytest.mark.asyncio

async def test_start_payment_success():
    """Тест успешного запуска платежа"""
    client = FakeAcquiringClient()
    
    # Правильные аргументы: order_ref: str, amount: Decimal
    result = await client.start_payment(
        order_ref="order_123",  # строка, не число!
        amount=Decimal("1000.00")
    )
    
    assert result is not None
    assert isinstance(result, str)  # возвращает bank_payment_id
    assert len(result) > 0

async def test_check_payment():
    """Тест проверки статуса платежа"""
    client = FakeAcquiringClient()
    
    # Создаем платеж
    bank_payment_id = await client.start_payment(
        order_ref="order_123",
        amount=Decimal("1000.00")
    )
    
    # Проверяем статус
    status = await client.check_payment(bank_payment_id)
    
    assert status is not None
    assert "status" in status
    assert status["status"] in ["pending", "success", "failed", "not_found"]

async def test_check_payment_not_found():
    """Тест проверки несуществующего платежа"""
    client = FakeAcquiringClient()
    
    status = await client.check_payment("non_existent_id")
    
    assert status["status"] == "not_found"
    assert "reason" in status

async def test_refund():
    """Тест возврата платежа"""
    client = FakeAcquiringClient()
    
    # Создаем платеж
    bank_payment_id = await client.start_payment(
        order_ref="order_123",
        amount=Decimal("1000.00")
    )
    
    # Делаем возврат
    result = await client.refund(bank_payment_id, Decimal("500.00"))
    
    assert isinstance(result, bool)  # возвращает bool
