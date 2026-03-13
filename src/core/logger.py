import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger

# Кастомный форматтер для JSON логов
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Добавляем timestamp в ISO формате
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Добавляем название сервиса
        log_record['service'] = 'payment-service'
        
        # Уровень логирования
        log_record['level'] = record.levelname
        
        # Если есть request_id из контекста
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

def get_logger(name: str = "payment-service") -> logging.Logger:
    """Получить настроенный логгер"""
    logger = logging.getLogger(name)
    
    # Если уже настроен, возвращаем
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Создаем handler для stdout
    handler = logging.StreamHandler()
    
    # JSON форматтер
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# FastAPI middleware для логирования запросов
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем request_id для трейсинга
        request_id = str(uuid.uuid4())
        
        # Логируем входящий запрос
        logger = get_logger()
        logger.info("Request started", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        })
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Логируем успешный ответ
            logger.info("Request completed", extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(process_time * 1000, 2)
            })
            
            # Добавляем request_id в заголовки ответа
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Логируем ошибку
            logger.error("Request failed", extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(process_time * 1000, 2)
            })
            raise
