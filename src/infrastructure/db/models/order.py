from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class Order(Base):
    __tablename__ = "orders"

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        String(30), default=OrderStatus.PENDING, nullable=False
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )