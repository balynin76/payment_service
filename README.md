# Тестовое задание
## Описание 



```markdown
payment_service/
├── alembic/                    # миграции (если используешь)
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── orders.py       # эндпоинты заказов
│   │       └── payments.py     # эндпоинты платежей
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── infrastructure/
│   │   ├── db/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   └── session.py
│   │   └── acquiring/
│   │       └── fake_client.py
│   ├── services/
│   │   └── payment_service.py   # главная бизнес-логика
│   ├── schemas/
│   │   ├── order.py
│   │   └── payment.py
│   └── main.py
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
└── dev_payment.db              # sqlite для разработки
```
## Запуск