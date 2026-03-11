from decimal import Decimal
from typing import Literal, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession


from src.core.exceptions import NotFoundError, BusinessLogicError
from src.infrastructure.db.repositories.order_repository import OrderRepository
from src.infrastructure.db.repositories.payment_repository import PaymentRepository
from src.infrastructure.acquiring.fake_client import FakeAcquiringClient
from src.infrastructure.db.models.order import OrderStatus
from src.infrastructure.db.models.payment import PaymentStatus, PaymentType


class PaymentService:
    def __init__(
        self,
        session: AsyncSession,
        acquiring: FakeAcquiringClient,
    ):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.payment_repo = PaymentRepository(session)
        self.acquiring = acquiring

    async def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_type: Literal["cash", "acquiring"],
    ) -> int:
        async with self.session.begin():
            order = await self.order_repo.get_for_update(order_id)

            remaining = order.amount - order.paid_amount
            if amount <= Decimal("0"):
                raise BusinessLogicError("Сумма платежа должна быть положительной")
            if amount > remaining:
                raise BusinessLogicError(
                    f"Нельзя оплатить больше остатка: {remaining} (попытка: {amount})"
                )

            payment = await self.payment_repo.create(
                order_id=order_id,
                amount=amount,
                type=PaymentType(payment_type),
                status=PaymentStatus.PENDING if payment_type == "acquiring" else PaymentStatus.SUCCESS,
            )

            if payment_type == "acquiring":
                try:
                    bank_id = await self.acquiring.start_payment(
                        order_ref=str(order_id),
                        amount=amount,
                    )
                    payment.bank_payment_id = bank_id
                except Exception as exc:
                    raise BusinessLogicError(f"Ошибка запуска платежа в банке: {exc}") from exc
            else:
                # cash — сразу зачисляем
                order.paid_amount += amount
                order.status = self._compute_order_status(order)

            await self.session.commit()
            return payment.id

    # ... остальные методы (confirm, refund) аналогично используют self.payment_repo и self.order_repo

    @staticmethod
    def _compute_order_status(order) -> OrderStatus:
        if order.paid_amount >= order.amount:
            return OrderStatus.PAID
        if order.paid_amount > Decimal("0"):
            return OrderStatus.PARTIALLY_PAID
        return OrderStatus.PENDING