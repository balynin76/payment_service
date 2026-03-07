# src/infrastructure/acquiring/fake_client.py
"""
Фейковый клиент эквайринга для тестового задания.
В реальном проекте здесь был бы httpx.AsyncClient к API банка.
"""

import random
import uuid
from decimal import Decimal
from typing import Dict, Any


class FakeAcquiringClient:
    def __init__(self):
        # Хранилище: bank_payment_id → данные платежа
        self._payments: Dict[str, Dict[str, Any]] = {}

    async def start_payment(self, order_ref: str, amount: Decimal) -> str:
        """
        Имитирует создание платежа в банке.
        Возвращает уникальный bank_payment_id.
        """
        payment_id = str(uuid.uuid4())
        self._payments[payment_id] = {
            "order_ref": order_ref,
            "amount": amount,
            "status": "pending",
            "created_at": "fake-timestamp",  # можно добавить datetime.now()
        }
        return payment_id

    async def check_payment(self, bank_payment_id: str) -> Dict[str, Any]:
        """
        Имитирует проверку статуса платежа.
        ~80% шанс на успех, чтобы было интересно тестировать оба исхода.
        """
        if bank_payment_id not in self._payments:
            return {"status": "not_found", "reason": "Платёж не найден"}

        payment = self._payments[bank_payment_id]

        if payment["status"] != "pending":
            return payment  # уже обработан ранее

        # Симуляция ответа банка
        if random.random() < 0.80:  # 80% успех
            payment["status"] = "success"
            payment["reason"] = "Успешно оплачено"
        else:
            payment["status"] = "failed"
            payment["reason"] = "Отклонено банком (тестовая ошибка)"

        return payment

    async def refund(self, bank_payment_id: str, amount: Decimal) -> bool:
        """
        Имитирует возврат средств.
        В 95% случаев "успех", чтобы не усложнять тесты.
        """
        if bank_payment_id not in self._payments:
            return False

        # Можно добавить логику: если уже refunded полностью → отказ
        # Но для простоты всегда ок
        return random.random() < 0.95  # почти всегда успех