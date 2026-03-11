from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.exceptions import NotFoundError
from src.infrastructure.db.models.order import Order
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.payments))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_update(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.payments))
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError(f"Заказ {order_id} не найден")
        return order

    async def create(self, amount: Decimal) -> Order:
        order = Order(amount=amount)
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order)
        return order