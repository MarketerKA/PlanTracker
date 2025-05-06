# E2E Tests for PlanTracker Frontend

Автоматизированные тесты на основе Selenium для проверки функциональности фронтенда.

## Установка

```bash
# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

## Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с генерацией HTML-отчета
pytest --html=report.html
```

## Структура проекта

- `conftest.py` - Конфигурация pytest и фикстуры
- `tests/` - Тестовые сценарии
- `pages/` - Page Objects для страниц приложения
- `utils/` - Вспомогательные утилиты 