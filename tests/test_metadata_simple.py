from src.infrastructure.db.models import Base, Order, Payment

def test_metadata_simple():
    """Простая проверка метаданных"""
    print(f"\nBase: {Base}")
    print(f"Order: {Order}")
    print(f"Payment: {Payment}")
    
    tables = Base.metadata.tables.keys()
    print(f"Tables: {list(tables)}")
    
    # Проверяем наличие таблиц
    assert 'orders' in tables, "Orders table not found"
    assert 'payments' in tables, "Payments table not found"
    
    print("✅ Models registered successfully")
    
    # Проверяем колонки
    orders_table = Base.metadata.tables['orders']
    print(f"Orders columns: {[c.name for c in orders_table.columns]}")
    
    payments_table = Base.metadata.tables['payments']
    print(f"Payments columns: {[c.name for c in payments_table.columns]}")
