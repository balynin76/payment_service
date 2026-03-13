from src.infrastructure.db.models.order import OrderStatus, Order
from src.infrastructure.db.models.payment import PaymentType, PaymentStatus

def test_enum_values():
    """Проверка Enum значений"""
    print(f"\nOrderStatus.PENDING: {OrderStatus.PENDING}")
    print(f"OrderStatus.PENDING.value: {OrderStatus.PENDING.value}")
    print(f"OrderStatus.PENDING == 'pending': {OrderStatus.PENDING == 'pending'}")
    
    # Проверяем все значения
    assert OrderStatus.PENDING.value == "pending"
    assert OrderStatus.PARTIALLY_PAID.value == "partially_paid"
    assert OrderStatus.PAID.value == "paid"
    
    assert PaymentType.CASH.value == "cash"
    assert PaymentType.ACQUIRING.value == "acquiring"
    
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.SUCCESS.value == "success"
    assert PaymentStatus.FAILED.value == "failed"
    assert PaymentStatus.REFUNDED.value == "refunded"
    
    print("✅ Enum values are correct")
