# src/services/payment_service.py
from decimal import Decimal
from typing import Literal, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import NotFoundError, BusinessLogicError
from ..infrastructure.db.models.order import Order, OrderStatus
from ..infrastructure.db.models.payment import Payment, PaymentType, PaymentStatus
from ..infrastructure.acquiring.fake_client import FakeAcquiringClient   # или реальный


class PaymentService:
    def __init__(self, session: AsyncSession, acquiring: FakeAcquiringClient):
        self.session = session
        self.acquiring = acquiring

    async def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_type: Literal["cash", "acquiring"],
    ) -> int:
        """
        Создаёт платёж + сразу подтверждает cash-платёж.
        Для acquiring — только создаёт pending-запись.
        Всё в одной транзакции с блокировкой заказа.
        """
        async with self.session.begin():
            # Блокируем заказ на изменение (предотвращаем race condition)
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

            remaining = order.amount - order.paid_amount
            if amount <= Decimal("0"):
                raise BusinessLogicError("Сумма платежа должна быть положительной")
            if amount > remaining:
                raise BusinessLogicError(
                    f"Нельзя оплатить больше остатка: {remaining} (попытка: {amount})"
                )

            payment = Payment(
                order_id=order_id,
                type=PaymentType(payment_type),
                amount=amount,
                status=PaymentStatus.PENDING if payment_type == "acquiring" else PaymentStatus.SUCCESS,
            )

            self.session.add(payment)
            await self.session.flush()  # получаем payment.id

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

    async def confirm_acquiring_payment(self, payment_id: int) -> Dict[str, Any]:
        """
        Подтверждение эквайринг-платежа (вызывается вручную или по webhook).
        Обновляет статус платежа и зачисляет деньги в заказ.
        """
        async with self.session.begin():
            stmt = (
                select(Payment)
                .where(Payment.id == payment_id)
                .options(selectinload(Payment.order))
                .with_for_update()
            )
            result = await self.session.execute(stmt)
            payment = result.scalar_one_or_none()

            if not payment:
                raise NotFoundError(f"Платёж {payment_id} не найден")

            if payment.type != PaymentType.ACQUIRING:
                raise BusinessLogicError("Подтверждать можно только эквайринг-платежи")

            if payment.status != PaymentStatus.PENDING:
                raise BusinessLogicError(
                    f"Платёж уже в статусе {payment.status} — подтверждение невозможно"
                )

            bank_response = await self.acquiring.check_payment(payment.bank_payment_id)

            if bank_response.get("status") == "success":
                payment.status = PaymentStatus.SUCCESS
                payment.order.paid_amount += payment.amount
                payment.order.status = self._compute_order_status(payment.order)
                message = "Платёж успешно подтверждён"
            else:
                payment.status = PaymentStatus.FAILED
                message = bank_response.get("reason", "Банк отклонил платёж")

            await self.session.commit()

            return {
                "payment_id": payment.id,
                "status": payment.status.value,
                "message": message,
                "order_status": payment.order.status.value,
            }

    async def refund_payment(self, payment_id: int, amount: Decimal) -> Dict[str, Any]:
        """
        Возврат средств (полный или частичный).
        Работает для cash и acquiring.
        """
        if amount <= Decimal("0"):
            raise BusinessLogicError("Сумма возврата должна быть положительной")

        async with self.session.begin():
            stmt = (
                select(Payment)
                .where(Payment.id == payment_id)
                .options(selectinload(Payment.order))
                .with_for_update()
            )
            result = await self.session.execute(stmt)
            payment = result.scalar_one_or_none()

            if not payment:
                raise NotFoundError(f"Платёж {payment_id} не найден")

            if payment.status not in (PaymentStatus.SUCCESS, PaymentStatus.PARTIALLY_REFUNDED):
                raise BusinessLogicError(
                    f"Возврат невозможен из статуса {payment.status}"
                )

            available_for_refund = payment.amount - payment.refunded_amount
            if amount > available_for_refund:
                raise BusinessLogicError(
                    f"Нельзя вернуть больше доступной суммы: {available_for_refund}"
                )

            # Имитация вызова банка (в реальном проекте — await self.acquiring.refund(...))
            if payment.type == PaymentType.ACQUIRING and payment.bank_payment_id:
                refund_ok = await self.acquiring.refund(payment.bank_payment_id, amount)
                if not refund_ok:
                    raise BusinessLogicError("Ошибка возврата в эквайринге")

            payment.refunded_amount += amount

            if payment.refunded_amount == payment.amount:
                payment.status = PaymentStatus.REFUNDED
            else:
                payment.status = PaymentStatus.PARTIALLY_REFUNDED

            # Уменьшаем paid_amount заказа
            payment.order.paid_amount -= amount
            payment.order.status = self._compute_order_status(payment.order)

            await self.session.commit()

            return {
                "payment_id": payment.id,
                "status": payment.status.value,
                "refunded_total": str(payment.refunded_amount),
                "remaining_on_payment": str(payment.amount - payment.refunded_amount),
                "order_paid_amount": str(payment.order.paid_amount),
                "order_status": payment.order.status.value,
            }

    @staticmethod
    def _compute_order_status(order: Order) -> OrderStatus:
        if order.paid_amount >= order.amount:
            return OrderStatus.PAID
        if order.paid_amount > Decimal("0"):
            return OrderStatus.PARTIALLY_PAID
        return OrderStatus.PENDING