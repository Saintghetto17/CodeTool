# Примеры использования Code Agent

## Пример 1: Простая функция

### Issue #1: Добавить функцию для вычисления факториала

**Описание Issue**:
```markdown
Нужно добавить функцию `factorial(n)` в файл `utils.py`.

Требования:
- Принимает целое число n
- Возвращает факториал n
- Обрабатывает отрицательные числа (raise ValueError)
- Добавить docstring
```

### Команда
```bash
code-agent process-issue 1 --repo-path /path/to/repo
```

### Результат работы Code Agent

Code Agent создаст PR с изменениями:

```python
# utils.py
def factorial(n: int) -> int:
    """
    Calculate factorial of n.
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

### AI Reviewer анализ

```markdown
✅ Code Review: APPROVED

Отличная реализация! Код соответствует всем требованиям:
- Правильная логика вычисления факториала
- Обработка граничных случаев
- Валидация входных данных
- Хороший docstring

Рекомендации (не блокирующие):
- Можно добавить type hints для лучшей читаемости ✓ (уже есть)
- Рекомендуется добавить unit тесты
```

---

## Пример 2: Исправление бага

### Issue #2: Ошибка деления на ноль

**Описание Issue**:
```markdown
В функции `calculate_average(numbers)` в `stats.py` происходит ошибка 
деления на ноль, когда передается пустой список.

Шаги для воспроизведения:
1. Вызвать `calculate_average([])`
2. Получить ZeroDivisionError

Ожидаемое поведение:
- Для пустого списка возвращать 0.0 или raise ValueError
```

### Текущий код
```python
# stats.py
def calculate_average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers)
```

### Команда
```bash
code-agent process-issue 2
```

### Исправленный код (Code Agent)

```python
# stats.py
def calculate_average(numbers: list[float]) -> float:
    """
    Calculate average of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average value
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

### Ревью и итерация

**Первое ревью**:
```markdown
⚠️ Changes Requested

Хорошее исправление основной проблемы! Однако:

Issues:
1. Отсутствуют unit тесты для нового поведения
2. Можно добавить проверку типов (что numbers - действительно список чисел)
```

**Code Agent автоматически исправляет** (iteration 2):

```python
# stats.py
def calculate_average(numbers: list[float]) -> float:
    """
    Calculate average of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average value
        
    Raises:
        ValueError: If list is empty or contains non-numeric values
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    # Validate all elements are numeric
    if not all(isinstance(x, (int, float)) for x in numbers):
        raise ValueError("All elements must be numeric")
    
    return sum(numbers) / len(numbers)
```

И добавляет тесты:

```python
# tests/test_stats.py
import pytest
from stats import calculate_average

def test_calculate_average_normal():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0

def test_calculate_average_empty():
    with pytest.raises(ValueError, match="empty list"):
        calculate_average([])

def test_calculate_average_non_numeric():
    with pytest.raises(ValueError, match="numeric"):
        calculate_average([1, "two", 3])
```

**Второе ревью**:
```markdown
✅ APPROVED

Отличная работа! Все issues исправлены:
- Добавлена валидация типов
- Написаны comprehensive тесты
- Все тесты проходят
```

---

## Пример 3: Новая фича с REST API

### Issue #3: Endpoint для получения пользователя

**Описание Issue**:
```markdown
Нужно реализовать REST API endpoint для получения информации о пользователе.

Требования:
- GET /api/users/{user_id}
- Возвращает JSON с информацией о пользователе
- 404 если пользователь не найден
- Использовать FastAPI
- Добавить Pydantic модель для валидации
- Написать тесты
```

### Команда
```bash
code-agent process-issue 3 --repo-path /path/to/api
```

### Сгенерированный код

**models.py**:
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email")
    created_at: str = Field(..., description="Creation timestamp")
```

**api.py**:
```python
from fastapi import FastAPI, HTTPException
from models import User

app = FastAPI()

# Mock database
USERS_DB = {
    1: User(
        id=1,
        username="john_doe",
        email="john@example.com",
        created_at="2024-01-01T00:00:00Z"
    )
}

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID."""
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS_DB[user_id]
```

**test_api.py**:
```python
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_get_user_success():
    response = client.get("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "john_doe"

def test_get_user_not_found():
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

### Процесс ревью

**CI Checks**: ✅ Все проходят
- ruff: ✅
- black: ✅
- mypy: ✅
- pytest: ✅ (2 passed)

**AI Review**: 
```markdown
✅ APPROVED

Отличная реализация REST API endpoint!

Что хорошо:
- Правильное использование FastAPI
- Pydantic модели для валидации
- Обработка 404 ошибок
- Comprehensive тесты
- Type hints везде
- Хороший docstring

Код готов к merge!
```

---

## Пример 4: Рефакторинг кода

### Issue #4: Рефакторинг дублированного кода

**Описание Issue**:
```markdown
В файлах `user_service.py` и `product_service.py` дублируется логика 
логирования и обработки ошибок. Нужно вынести общую логику.

Требования:
- Создать базовый класс или декоратор
- Убрать дублирование
- Сохранить функциональность
```

### Команда
```bash
code-agent process-issue 4
```

### Исходный код (до)

```python
# user_service.py
import logging

class UserService:
    def get_user(self, user_id):
        logging.info(f"Getting user {user_id}")
        try:
            # logic
            return user
        except Exception as e:
            logging.error(f"Error getting user: {e}")
            raise

# product_service.py (аналогично)
class ProductService:
    def get_product(self, product_id):
        logging.info(f"Getting product {product_id}")
        try:
            # logic
            return product
        except Exception as e:
            logging.error(f"Error getting product: {e}")
            raise
```

### Рефакторинг (Code Agent)

**base_service.py** (новый файл):
```python
import logging
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def logged_operation(operation_name: str) -> Callable:
    """Decorator for logging and error handling."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logging.info(f"Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                logging.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                logging.error(f"Error in {operation_name}: {e}")
                raise
        return wrapper
    return decorator
```

**user_service.py** (после):
```python
from base_service import logged_operation

class UserService:
    @logged_operation("get user")
    def get_user(self, user_id: int):
        # logic
        return user
```

**product_service.py** (после):
```python
from base_service import logged_operation

class ProductService:
    @logged_operation("get product")
    def get_product(self, product_id: int):
        # logic
        return product
```

### Ревью

```markdown
✅ APPROVED

Отличный рефакторинг!

Improvements:
- Убрано дублирование кода
- Создан переиспользуемый декоратор
- Улучшена читаемость
- Добавлены type hints
- Функциональность сохранена (все тесты проходят)
```

---

## Пример 5: Множественные итерации

### Issue #5: Сложная валидация форм

**Описание**:
```markdown
Реализовать валидацию формы регистрации пользователя с правилами:
- Email должен быть валидным
- Пароль минимум 8 символов, 1 цифра, 1 заглавная
- Username 3-20 символов, только буквы и цифры
- Повторный пароль должен совпадать
```

### Итерация 1

Code Agent создает базовую реализацию.

**Ревью 1**:
```markdown
⚠️ Changes Requested

Issues:
1. Regex для email недостаточно строгий
2. Нет проверки на наличие спецсимволов в пароле
3. Не все edge cases покрыты тестами
```

### Итерация 2

Code Agent исправляет замечания.

**Ревью 2**:
```markdown
⚠️ Changes Requested

Issues:
1. Тесты добавлены, но некоторые падают
2. В сообщениях об ошибках опечатки
```

### Итерация 3

Code Agent исправляет тесты и опечатки.

**Ревью 3**:
```markdown
✅ APPROVED

Все замечания исправлены! Код готов к merge.
```

---

## Полезные команды для отладки

### Просмотр логов
```bash
code-agent process-issue 123 --log-level DEBUG
```

### Dry run (если бы была такая опция)
```bash
# Можно добавить в будущем
code-agent process-issue 123 --dry-run
```

### Проверка конфигурации
```bash
code-agent --help
python -c "from code_agent.config import settings; print(settings)"
```

### Тестирование на локальном репозитории
```bash
cd /path/to/test/repo
code-agent process-issue 1 --repo-path .
```

---

## Советы по использованию

### 1. Пишите детальные Issue

Чем подробнее описание, тем лучше результат:

❌ Плохо:
```markdown
Добавить валидацию
```

✅ Хорошо:
```markdown
Добавить валидацию email в форму регистрации.

Требования:
- Проверка формата email (используя regex или библиотеку)
- Возврат понятного сообщения об ошибке
- Unit тесты для валидных и невалидных случаев

Примеры:
- valid@example.com ✅
- invalid.email ❌
- @example.com ❌
```

### 2. Используйте метки

Добавьте метку `code-agent` для автоматической обработки:

```bash
# Через GitHub UI или CLI
gh issue create --label "code-agent" --title "Fix bug"
```

### 3. Следите за итерациями

Система ограничена `MAX_ITERATIONS` (по умолчанию 5). Если достигнут лимит:
- Проверьте Issue на ясность требований
- Возможно, задача слишком сложная и нужно разбить

### 4. Проверяйте результаты

Code Agent — это помощник, не замена человеку:
- Всегда проверяйте сгенерированный код
- Запускайте тесты локально
- Проверяйте безопасность

### 5. Настраивайте промпты

Для лучших результатов отредактируйте `config/prompts.yaml` под ваш проект:
- Добавьте примеры кода вашего стиля
- Укажите специфичные требования
- Добавьте контекст о вашей архитектуре

