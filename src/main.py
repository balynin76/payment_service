from fastapi import FastAPI
from src.api.v1 import orders, payments
from src.core.logger import get_logger, RequestLoggingMiddleware
from src.infrastructure.db.session import engine, create_tables
from contextlib import asynccontextmanager

# Инициализируем логгер
logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт
    logger.info("Starting payment service", extra={"event": "startup"})
    await create_tables()
    logger.info("Tables created successfully", extra={"event": "startup_complete"})
    yield
    # Шатдаун
    logger.info("Shutting down payment service", extra={"event": "shutdown"})
    await engine.dispose()

# Создаем приложение
app = FastAPI(
    title="Payment Service",
    description="Сервис для обработки платежей",
    version="1.0.0",
    lifespan=lifespan
)

# Добавляем middleware для логирования
app.add_middleware(RequestLoggingMiddleware)

# Подключаем роутеры
app.include_router(orders.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")

@app.get("/health", tags=["health"])
async def health_check():
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "payment-service"}

logger.info("Application initialized", extra={"event": "app_ready"})
