# Руководство по участию в разработке

Спасибо за интерес к проекту Code Agent! Мы рады вашему участию.

## Как внести вклад

### Сообщения об ошибках

Если вы нашли баг:

1. Проверьте [Issues](https://github.com/your-username/code-agent/issues), возможно он уже известен
2. Создайте новый Issue с:
   - Описанием проблемы
   - Шагами для воспроизведения
   - Ожидаемым и фактическим поведением
   - Версией Python, ОС, версией code-agent
   - Логами (без секретов!)

### Предложения улучшений

Есть идея? Создайте Issue с меткой `enhancement`:

- Опишите предлагаемую функциональность
- Объясните, почему это полезно
- Приведите примеры использования

### Pull Requests

1. **Fork репозитория**
2. **Создайте ветку**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Внесите изменения**
4. **Добавьте тесты**
5. **Запустите проверки**:
   ```bash
   black .
   ruff check --fix .
   mypy code_agent
   pytest
   ```
6. **Commit и Push**:
   ```bash
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```
7. **Создайте Pull Request**

## Стандарты кода

### Python Style Guide

Мы следуем [PEP 8](https://pep8.org/) с некоторыми дополнениями:

- **Line length**: 100 символов
- **Quotes**: Двойные кавычки для строк
- **Type hints**: Обязательны для всех функций
- **Docstrings**: Google style

### Пример кода

```python
from typing import Optional


def calculate_sum(numbers: list[int], initial: int = 0) -> int:
    """
    Calculate sum of numbers with initial value.
    
    Args:
        numbers: List of integers to sum
        initial: Initial value for sum
        
    Returns:
        Total sum
        
    Raises:
        ValueError: If numbers list is None
    """
    if numbers is None:
        raise ValueError("numbers cannot be None")
    return sum(numbers, initial)
```

### Инструменты

- **black**: Автоформатирование
- **ruff**: Линтинг
- **mypy**: Проверка типов
- **pytest**: Тестирование

## Структура коммитов

Используйте префиксы:

- `Add:` - новая функциональность
- `Fix:` - исправление бага
- `Update:` - обновление существующей функциональности
- `Remove:` - удаление кода
- `Refactor:` - рефакторинг без изменения поведения
- `Docs:` - изменения в документации
- `Test:` - добавление/изменение тестов
- `Chore:` - рутинные задачи (обновление зависимостей и т.д.)

Примеры:
```
Add: support for custom LLM providers
Fix: handle empty PR diff gracefully
Update: improve error messages in CLI
Docs: add examples for new commands
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/unit/test_llm.py

# Конкретный тест
pytest tests/unit/test_llm.py::test_openai_provider_generate

# С покрытием
pytest --cov=code_agent --cov-report=html
```

### Написание тестов

Каждая новая функция должна иметь тесты:

```python
def test_function_name():
    """Test what the function does."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

Используйте fixtures для повторяющегося кода:

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Test User"}

def test_user_processing(sample_user):
    result = process_user(sample_user)
    assert result["processed"] is True
```

## Документация

### Docstrings

Все публичные функции, классы и модули должны иметь docstrings:

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    One-line summary of the function.
    
    More detailed description if needed. Can span multiple lines.
    Explain the purpose, behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When this exception is raised
        TypeError: When this exception is raised
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
```

### Markdown документы

При добавлении новых .md файлов:

- Используйте понятные заголовки
- Добавляйте примеры кода
- Включайте ссылки на связанные документы

## Настройка окружения для разработки

### 1. Клонирование

```bash
git clone https://github.com/your-username/code-agent.git
cd code-agent
```

### 2. Виртуальное окружение

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Pre-commit hooks (опционально)

```bash
pip install pre-commit
pre-commit install
```

Это автоматически запустит линтеры перед каждым коммитом.

## Обзор архитектуры

Перед началом работы ознакомьтесь с:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - архитектура системы
- [README.md](README.md) - общее описание
- [EXAMPLES.md](docs/EXAMPLES.md) - примеры использования

Основные компоненты:
```
code_agent/
├── agents/          # Code Agent и Reviewer Agent
├── core/            # Ядро (LLM, GitHub client)
├── utils/           # Утилиты
├── config.py        # Конфигурация
└── cli.py           # CLI интерфейс
```

## Процесс ревью

### Что проверяют ревьюеры

1. **Код**:
   - Соответствие style guide
   - Качество и читаемость
   - Отсутствие багов
   - Производительность

2. **Тесты**:
   - Покрытие новой функциональности
   - Качество тестов
   - Отсутствие flaky тестов

3. **Документация**:
   - Docstrings
   - README обновлен (если нужно)
   - Примеры (если нужно)

4. **Commits**:
   - Понятные сообщения
   - Логическое разделение изменений

### Как ускорить ревью

- ✅ Пишите понятное описание PR
- ✅ Проверяйте код сами перед отправкой
- ✅ Разбивайте большие PR на маленькие
- ✅ Отвечайте на комментарии быстро
- ✅ Помечайте PR как "Ready for review"

## Лицензия

Внося вклад, вы соглашаетесь, что ваш код будет лицензирован под [MIT License](LICENSE).

## Вопросы?

- Создайте [Issue](https://github.com/your-username/code-agent/issues)
- Напишите в Discussions
- Свяжитесь с мейнтейнерами

Спасибо за ваш вклад! 🎉

