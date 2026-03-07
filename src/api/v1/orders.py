# src/api/v1/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models.order import Order

router = APIRouter(prefix="/orders", tags=["orders (для тестирования)"])

@router.post(
    "/",
    summary="Создать новый заказ",
    response_model=dict,
    status_code=201
)
async def create_order(
    amount: float = 1000.0,  # можно сделать через body, но для простоты query
    db: AsyncSession = Depends(get_db)
):
    """
    Создаёт тестовый заказ с заданной суммой.
    В реальном проекте здесь был бы более полный body с товарами и т.д.
    """
    try:
        order = Order(amount=Decimal(str(amount)))
        db.add(order)
        await db.commit()
        await db.refresh(order)

        return {
            "order_id": order.id,
            "amount": str(order.amount),
            "status": order.status.value,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания заказа: {str(e)}")


@router.get("/{order_id}", summary="Получить информацию о заказе")
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return {
        "order_id": order.id,
        "amount": str(order.amount),
        "paid_amount": str(order.paid_amount),
        "status": order.status.value,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }