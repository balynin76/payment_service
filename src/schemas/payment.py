from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal, Optional


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0, description="ID существующего заказа")
    amount: Decimal = Field(..., gt=0, description="Сумма платежа")
    type: Literal["cash", "acquiring"] = Field(..., description="Тип оплаты")


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    type: str
    status: str
    bank_payment_id: Optional[str] = None
    refunded_amount: Decimal = Field(default=Decimal("0.00"))

    class Config:
        from_attributes = True