# src/api/v1/payments.py
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal

from src.services.payment_service import PaymentService
from src.dependencies import get_payment_service   # или как у тебя настроено

router = APIRouter(prefix="/payments", tags=["Payments"])

class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0, description="ID существующего заказа")
    amount: Decimal = Field(..., gt=0, description="Сумма платежа")
    type: Literal["cash", "acquiring"] = Field(..., description="Тип оплаты")


@router.post("/", summary="Создать платёж для заказа", response_model=dict)
async def create_payment(
    data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service)
):
    try:
        payment_id = await service.create_payment(
            order_id=data.order_id,
            amount=data.amount,
            payment_type=data.type
        )
        return {"status": "created", "payment_id": payment_id}
    except Exception as e:
        # здесь можно добавить обработку NotFoundError / BusinessLogicError
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/confirm", summary="Подтвердить эквайринг-платёж")
async def confirm_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    result = await service.confirm_acquiring_payment(payment_id)
    return result


@router.post("/{payment_id}/refund", summary="Сделать возврат (полный/частичный)")
async def refund_payment(
    payment_id: int,
    amount: Decimal = Body(..., gt=0),
    service: PaymentService = Depends(get_payment_service)
):
    result = await service.refund_payment(payment_id, amount)
    return result