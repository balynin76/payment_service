from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Сумма заказа")


class OrderResponse(BaseModel):
    id: int
    amount: Decimal
    paid_amount: Decimal = Field(..., ge=0)
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # позволяет конвертировать из SQLAlchemy модели