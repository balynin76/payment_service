from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.db.session import get_db
from ...infrastructure.db.models.order import Order
from ...infrastructure.db.models.payment import Payment, PaymentType, PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-simple")
async def create_simple_payment(
    order_amount: float = 1000.0,
    payment_amount: float = 600.0,
    payment_type: str = "cash",
    db: AsyncSession = Depends(get_db),
):
    try:
        # Создаём заказ
        order = Order(amount=Decimal(str(order_amount)))
        db.add(order)
        await db.flush()  # получаем order.id

        # Создаём платёж
        payment = Payment(
            order_id=order.id,
            amount=Decimal(str(payment_amount)),
            type=PaymentType(payment_type),
        )

        if payment_type == "cash":
            payment.status = PaymentStatus.SUCCESS
            order.paid_amount += payment.amount
            if order.paid_amount >= order.amount:
                order.status = "paid"
            elif order.paid_amount > 0:
                order.status = "partially_paid"

        db.add(payment)
        await db.commit()
        await db.refresh(order)
        await db.refresh(payment)

        return {
            "order_id": order.id,
            "order_status": order.status,
            "paid_amount": float(order.paid_amount),
            "payment_id": payment.id,
            "payment_status": payment.status,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))