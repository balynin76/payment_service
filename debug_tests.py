#!/usr/bin/env python
"""Скрипт для диагностики проблем с тестами"""

import importlib
import inspect
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))


def inspect_module(module_path):
    """Инспектирует модуль и выводит информацию"""
    try:
        module = importlib.import_module(module_path)
        print(f"\n=== {module_path} ===")

        # Находим все классы
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_path:
                print(f"\nКласс: {name}")
                print(f"  Методы: {[m for m in dir(obj) if not m.startswith('_')]}")
                print(f"  Сигнатура __init__: {inspect.signature(obj.__init__)}")

        return True
    except Exception as e:
        print(f"Ошибка при импорте {module_path}: {e}")
        return False


# Инспектируем ключевые модули
inspect_module("src.infrastructure.acquiring.fake_client")
inspect_module("src.services.payment_service")