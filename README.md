# 💳 Payment Service

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/k8s-minikube-blue.svg)](https://kubernetes.io/)
[![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen.svg)](https://github.com/balynin76/payment_service/actions)
[![Coverage](https://img.shields.io/badge/coverage-73%25-yellow.svg)](https://codecov.io/gh/balynin76/payment_service)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


**Production-ready платежный сервис на FastAPI** с асинхронной архитектурой, структурированным логированием, полным покрытием тестами и готовностью к деплою в Kubernetes.

## ✨ Возможности

| | |
|---|---|
| 🔥 **FastAPI** | Современный, быстрый веб-фреймворк с автоматической документацией |
| 🔄 **Асинхронность** | SQLAlchemy 2.0 + asyncpg для максимальной производительности |
| 📦 **Docker** | Полная контейнеризация с docker-compose |
| ☸️ **Kubernetes** | Готовые манифесты для деплоя в Minikube/K8s |
| 📊 **Логирование** | Структурированные JSON логи с Request ID для трейсинга |
| 🧪 **Тестирование** | 11 интеграционных тестов с покрытием 73% |
| 🔐 **Безопасность** | Валидация данных, обработка ошибок, типизация |
| 🔄 **CI/CD** | GitHub Actions для автоматического тестирования и сборки |
| 🗄️ **База данных** | Поддержка SQLite (dev) и PostgreSQL (prod) через SQLAlchemy |
| 💳 **Платежи** | Поддержка наличных и платежей через эквайринг |

---

## 🛠 Технологии

| Компонент | Технология |
|-----------|------------|
| **Backend** | FastAPI + Python 3.11 |
| **Database** | SQLite / PostgreSQL + SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Logging** | Structured JSON logs + Request ID |
| **Testing** | Pytest + pytest-asyncio + coverage |
| **Container** | Docker + Docker Compose |
| **Orchestration** | Kubernetes + Minikube + Kustomize |
| **Code Quality** | Black, Flake8, isort, pre-commit |
| **CI/CD** | GitHub Actions |

---

## 🚀 Быстрый старт

### 📋 Требования
- Python 3.11+
- Docker (для контейнеризации)
- Minikube + kubectl (для Kubernetes)

### 🏃‍♂️ Локальный запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/balynin76/payment_service.git
cd payment_service

# 2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка переменных окружения
cp .env.example .env

# 5. Запуск сервера
uvicorn src.main:app --reload

# 6. Проверка
curl http://localhost:8000/health
# {"status":"healthy","service":"payment-service"}

🐳 Запуск в Docker

# Сборка образа
docker build -t payment-service:latest .

# Запуск контейнера
docker run -p 8000:8000 payment-service:latest

# Или через docker-compose
docker-compose up --build

☸️ Запуск в Kubernetes (Minikube)

docker build -t payment-service:latest .
minikube image load payment-service:latest
minikube image ls | grep payment

kubectl apply -f minikube-deploy-fixed.yaml
kubectl get pods -w

# В отдельном терминале
kubectl port-forward service/payment-service 8000:8000

curl http://localhost:8000/health

