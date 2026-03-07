from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Payment Service",
    description="Тестовое задание — сервис платежей",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {
        "message": "Payment Service is running",
        "docs": "/docs",
        "status": "ok"
    }


@app.get("/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )