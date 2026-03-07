from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PaymentType(str, PyEnum):
    CASH = "cash"
    ACQUIRING = "acquiring"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[PaymentType] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        String(30), default=PaymentStatus.PENDING, nullable=False
    )
    bank_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="payments")