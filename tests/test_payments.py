import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_payment(client):
    """Тест создания платежа"""
    # Сначала создаем заказ
    order_response = await client.post("/api/v1/orders/", json={
        "user_id": 1,
        "amount": 500.00,
        "description": "Оплата заказа"
    })
    
    if order_response.status_code >= 400:
        print(f"\nCreate order error: {order_response.text}")
    
    assert order_response.status_code in [200, 201]
    order_data = order_response.json()
    print(f"Order response: {order_data}")
    order_id = order_data["order_id"]
    
    # Создаем платеж
    payment_data = {
        "order_id": order_id,
        "amount": 500.00,
        "type": "cash"
    }
    
    response = await client.post("/api/v1/payments/", json=payment_data)
    
    if response.status_code >= 400:
        print(f"\nCreate payment error: {response.text}")
        try:
            error_data = response.json()
            print(f"Error details: {error_data}")
        except:
            pass
    
    assert response.status_code in [200, 201]
    data = response.json()
    print(f"Payment response: {data}")
    
    # Проверяем, что в ответе есть payment_id (не order_id)
    assert "payment_id" in data
    assert data["payment_id"] == 1
    # order_id может не быть в ответе, это нормально
