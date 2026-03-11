# src/api/v1/payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal

from src.core.exceptions import NotFoundError, BusinessLogicError
from src.services.payment_service import PaymentService
from src.dependencies import get_payment_service     # если создал файл

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentCreateRequest(BaseModel):
    order_id: int = Field(..., gt=0, description="ID существующего заказа")
    amount: Decimal = Field(..., gt=0, description="Сумма платежа")
    type: Literal["cash", "acquiring"] = Field(..., description="Тип оплаты")


@router.post(
    "/",
    summary="Создать платёж для существующего заказа",
    status_code=status.HTTP_201_CREATED
)
async def create_payment(
    request: PaymentCreateRequest,  # ← в body JSON
    service: PaymentService = Depends(get_payment_service)
):
    try:
        payment_id = await service.create_payment(
            order_id=request.order_id,
            amount=request.amount,
            payment_type=request.type
        )
        return {"payment_id": payment_id}
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{payment_id}/confirm")
async def confirm_acquiring(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    try:
        result = await service.confirm_acquiring_payment(payment_id)
        return result
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except BusinessLogicError as e:
        raise HTTPException(400, str(e))


@router.post("/{payment_id}/refund")
async def refund(
    payment_id: int,
    amount: Decimal,                # можно в body или query
    service: PaymentService = Depends(get_payment_service)
):
    try:
        result = await service.refund_payment(payment_id, amount)
        return result
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except BusinessLogicError as e:
        raise HTTPException(400, str(e))