from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundError
from ...db.models.payment import Payment
from .base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    async def get_by_id(self, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id).options(selectinload(Payment.order))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_update(self, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id).with_for_update()
        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()
        if not payment:
            raise NotFoundError(f"Платёж {payment_id} не найден")
        return payment

    async def create(self, **kwargs) -> Payment:
        payment = Payment(**kwargs)
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment