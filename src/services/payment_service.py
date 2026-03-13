from decimal import Decimal
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError, BusinessLogicError
from src.infrastructure.db.repositories.order_repository import OrderRepository
from src.infrastructure.db.repositories.payment_repository import PaymentRepository
from src.infrastructure.acquiring.fake_client import FakeAcquiringClient
from src.infrastructure.db.models.order import OrderStatus
from src.infrastructure.db.models.payment import PaymentStatus, PaymentType
from src.core.logger import get_logger

logger = get_logger()

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
        logger.debug("PaymentService initialized", extra={"component": "PaymentService"})

    async def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        payment_type: Literal["cash", "acquiring"],
    ) -> int:
        logger.info("Creating payment", extra={
            "order_id": order_id,
            "amount": str(amount),
            "payment_type": payment_type
        })
        
        async with self.session.begin():
            order = await self.order_repo.get_for_update(order_id)
            
            if not order:
                logger.error("Order not found", extra={"order_id": order_id})
                raise NotFoundError(f"Order {order_id} not found")

            remaining = order.amount - order.paid_amount
            if amount <= Decimal("0"):
                logger.warning("Invalid amount", extra={
                    "order_id": order_id,
                    "amount": str(amount)
                })
                raise BusinessLogicError("Сумма платежа должна быть положительной")
                
            if amount > remaining:
                logger.warning("Amount exceeds remaining", extra={
                    "order_id": order_id,
                    "amount": str(amount),
                    "remaining": str(remaining)
                })
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
                    logger.debug("Calling acquiring service", extra={
                        "order_id": order_id,
                        "amount": str(amount)
                    })
                    bank_id = await self.acquiring.start_payment(
                        order_ref=str(order_id),
                        amount=amount,
                    )
                    payment.bank_payment_id = bank_id
                    logger.info("Acquiring payment created", extra={
                        "payment_id": payment.id,
                        "bank_payment_id": bank_id
                    })
                except Exception as exc:
                    logger.error("Acquiring service error", extra={
                        "order_id": order_id,
                        "error": str(exc)
                    })
                    raise BusinessLogicError(f"Ошибка запуска платежа в банке: {exc}") from exc
            else:
                order.paid_amount += amount
                order.status = self._compute_order_status(order)
                logger.info("Cash payment processed", extra={
                    "payment_id": payment.id,
                    "order_id": order_id,
                    "new_paid_amount": str(order.paid_amount)
                })

            await self.session.commit()
            logger.info("Payment created successfully", extra={
                "payment_id": payment.id,
                "order_id": order_id
            })
            return payment.id
