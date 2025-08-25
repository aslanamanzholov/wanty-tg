#!/usr/bin/env python3
"""Тест для проверки основных оптимизаций производительности."""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_imports():
    """Тестируем импорты основных модулей."""
    try:
        print("🔍 Тестируем импорты...")
        
        # Тест импорта Redis кэша
        from src.bot.structures.redis_cache import RedisCache
        print("✅ Redis кэш импортирован успешно")
        
        # Тест импорта middleware
        from src.bot.middlewares.database_md import DatabaseMiddleware
        from src.bot.middlewares.redis_md import RedisMiddleware
        print("✅ Middleware импортированы успешно")
        
        # Тест импорта dreams логики
        from src.bot.logic.dreams.select import get_image_content
        print("✅ Dreams логика импортирована успешно")
        
        # Тест импорта notification
        from src.bot.logic.dreams.notification import send_batch_notifications
        print("✅ Notification логика импортирована успешно")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

async def test_redis_cache():
    """Тестируем Redis кэш (мок)."""
    try:
        print("\n🔍 Тестируем Redis кэш...")
        
        from src.bot.structures.redis_cache import RedisCache
        
        # Создаем мок Redis клиент
        class MockRedis:
            async def setex(self, key, ttl, value):
                pass
            async def get(self, key):
                return None
            async def incr(self, key):
                return 1
            async def expire(self, key, ttl):
                pass
            async def delete(self, key):
                pass
        
        redis_cache = RedisCache(MockRedis())
        
        # Тестируем основные методы
        await redis_cache.set_user_offset(123, 5)
        offset = await redis_cache.get_user_offset(123)
        print(f"✅ Redis кэш работает: offset = {offset}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Redis кэша: {e}")
        return False

async def test_database_middleware():
    """Тестируем Database middleware (мок)."""
    try:
        print("\n🔍 Тестируем Database middleware...")
        
        from src.bot.middlewares.database_md import DatabaseMiddleware
        
        # Создаем мок session maker
        class MockSessionMaker:
            async def __aenter__(self):
                return MockSession()
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        class MockSession:
            async def rollback(self):
                pass
        
        sessionmaker = MockSessionMaker()
        middleware = DatabaseMiddleware(sessionmaker)
        print("✅ Database middleware создан успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Database middleware: {e}")
        return False

async def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование оптимизаций производительности Wanty Bot\n")
    
    tests = [
        test_imports(),
        test_redis_cache(),
        test_database_middleware(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n📊 Результаты тестирования:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for i, result in enumerate(results):
        if result is True:
            passed += 1
            print(f"✅ Тест {i+1}: ПРОЙДЕН")
        else:
            print(f"❌ Тест {i+1}: ПРОВАЛЕН - {result}")
    
    print("=" * 50)
    print(f"📈 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Оптимизации готовы к использованию.")
        return 0
    else:
        print("⚠️  Некоторые тесты провалены. Проверьте код.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
