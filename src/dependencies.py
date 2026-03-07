# src/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.acquiring.fake_client import FakeAcquiringClient
from src.services.payment_service import PaymentService
from src.infrastructure.db.session import get_db   # предполагаю, что у тебя есть такая функция

def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    acquiring_client = FakeAcquiringClient()
    return PaymentService(session=db, acquiring=acquiring_client)