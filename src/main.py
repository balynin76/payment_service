from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.infrastructure.db.session import engine, create_tables
from src.api.v1.payments import router as payments_router
from src.api.v1.orders import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("→ Запуск приложения, создание таблиц...")
    await create_tables()                    # ← здесь создаются таблицы
    print("→ Таблицы готовы")
    yield
    # Shutdown (можно добавить закрытие соединений, если нужно)
    await engine.dispose()
    print("→ Приложение остановлено")

app = FastAPI(
    title="Payment Service",
    description="Тестовое задание — сервис платежей",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,          # ← добавляем lifespan
)

app.include_router(payments_router, prefix="/api/v1", tags=["payments"])
app.include_router(orders_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Payment Service is running",
        "docs": "/docs",
        "status": "ok"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )