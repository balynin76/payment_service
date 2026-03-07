# src/core/exceptions.py

class AppError(Exception):
    """Базовый класс для всех ожидаемых ошибок приложения"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Ресурс (заказ, платёж и т.д.) не найден"""
    pass


class BusinessLogicError(AppError):
    """Нарушение бизнес-правил (переплата, неверный статус, отрицательная сумма и т.д.)"""
    pass


# Можно добавить ещё, если захочешь расширить позже
class ValidationError(AppError):
    """Ошибка валидации входных данных (можно использовать вместо Pydantic-ошибок)"""
    pass


class AcquiringError(AppError):
    """Проблемы на стороне банка (необязательно, но удобно для distinguish)"""
    pass