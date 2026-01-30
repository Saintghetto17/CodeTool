# Архитектура Code Agent

## Обзор

Code Agent — это многокомпонентная система, реализующая автоматизированный цикл разработки ПО (SDLC) внутри GitHub. Система состоит из нескольких взаимодействующих компонентов.

## Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐         ┌──────────┐         ┌──────────────┐    │
│  │  Issues  │────────▶│   PRs    │────────▶│ GitHub       │    │
│  └──────────┘         └──────────┘         │ Actions      │    │
│       │                    │                └──────────────┘    │
│       │                    │                      │              │
│       │                    │                      │              │
└───────┼────────────────────┼──────────────────────┼──────────────┘
        │                    │                      │
        │                    │                      │
        ▼                    ▼                      ▼
┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│              │    │                 │    │                 │
│ Code Agent   │◀───│  GitHub Client  │───▶│ Reviewer Agent  │
│    (CLI)     │    │                 │    │   (Actions)     │
│              │    └─────────────────┘    │                 │
└──────────────┘            │              └─────────────────┘
        │                   │                      │
        │                   │                      │
        ▼                   ▼                      ▼
┌──────────────────────────────────────────────────────────┐
│                     LLM Services                          │
│  ┌─────────────┐              ┌──────────────┐          │
│  │   OpenAI    │              │  YandexGPT   │          │
│  │  GPT-4o-mini│              │              │          │
│  └─────────────┘              └──────────────┘          │
└──────────────────────────────────────────────────────────┘
        │                                │
        │                                │
        ▼                                ▼
┌──────────────────────────────────────────────────────────┐
│                   Git Repository                          │
│  (Локальная копия для работы Code Agent)                │
└──────────────────────────────────────────────────────────┘
```

## Основные компоненты

### 1. Code Agent (CLI)

**Назначение**: Основной агент, который читает Issues и создаёт код.

**Расположение**: `code_agent/agents/code_agent.py`

**Ключевые функции**:
- `process_issue(issue_number)` - основной метод обработки Issue
- `_modify_files()` - модификация файлов на основе LLM анализа
- `fix_pr_issues()` - исправление PR на основе обратной связи

**Процесс работы**:
1. Получает Issue через GitHub API
2. Анализирует требования через LLM
3. Определяет какие файлы нужно изменить
4. Создаёт новую ветку
5. Генерирует изменения для каждого файла через LLM
6. Коммитит и пушит изменения
7. Создаёт Pull Request

**Технологии**:
- GitPython - для работы с git
- PyGithub - для GitHub API
- LLM Service - для генерации кода

### 2. Reviewer Agent

**Назначение**: Анализирует Pull Request и предоставляет код-ревью.

**Расположение**: `code_agent/agents/reviewer_agent.py`

**Ключевые функции**:
- `review_pull_request()` - основной метод ревью
- `generate_review_summary()` - генерация markdown summary
- `_post_review()` - публикация результатов в GitHub

**Процесс работы**:
1. Получает PR diff через GitHub API
2. Получает связанный Issue
3. Анализирует изменения через LLM
4. Проверяет результаты CI/CD
5. Генерирует детальное ревью
6. Публикует ревью в PR (APPROVE/REQUEST_CHANGES)

**Интеграция с CI**:
- Анализирует результаты ruff, black, mypy, pytest
- Учитывает статус всех проверок
- Принимает решение на основе комбинированного анализа

### 3. LLM Service

**Назначение**: Единая точка интеграции с различными LLM провайдерами.

**Расположение**: `code_agent/core/llm.py`

**Архитектура**:
```python
LLMProvider (Abstract Base Class)
    ├── OpenAIProvider
    └── YandexGPTProvider
```

**Ключевые методы**:
- `generate_code_changes()` - генерация изменений кода
- `analyze_issue()` - анализ Issue
- `review_code_changes()` - ревью изменений

**Промпты**:
- Конфигурируются в `config/prompts.yaml`
- Поддержка шаблонизации с переменными
- Разделение system и user промптов

### 4. GitHub Client

**Назначение**: Обертка над GitHub API для удобной работы.

**Расположение**: `code_agent/core/github_client.py`

**Компоненты**:

#### GitHubClient
- Работа с Issues
- Работа с Pull Requests
- Получение diff и CI результатов
- Публикация комментариев и ревью

#### GitRepo
- Локальные git операции
- Создание веток
- Коммиты и пуши
- Чтение/запись файлов

**API методы**:
```python
# Issues
get_issue(issue_number)
get_issue_details(issue_number)
update_issue_labels(issue_number, labels)

# Pull Requests
create_pull_request(title, body, head, base)
get_pull_request(pr_number)
get_pr_diff(pr_number)
get_pr_checks(pr_number)

# Reviews
create_review(pr_number, body, event)
add_comment_to_pr(pr_number, comment)
```

### 5. Configuration System

**Назначение**: Централизованное управление конфигурацией.

**Расположение**: `code_agent/config.py`

**Технологии**:
- Pydantic Settings для валидации
- Поддержка .env файлов
- Type hints для всех настроек

**Категории настроек**:
- GitHub (токен, репозиторий)
- LLM (провайдер, API ключи, модели)
- Agent (лимиты итераций, префиксы веток)
- Features (флаги включения/выключения фичей)

### 6. CLI Interface

**Назначение**: Командная строка для взаимодействия с системой.

**Расположение**: `code_agent/cli.py`

**Технологии**:
- Typer - для CLI
- Rich - для красивого вывода

**Команды**:
```bash
code-agent process-issue <number>
code-agent review-pr <number>
code-agent fix-pr <number> --feedback "..."
code-agent generate-summary <number>
code-agent version
```

## GitHub Actions Workflows

### 1. Issue Handler

**Файл**: `.github/workflows/issue_handler.yml`

**Триггеры**:
```yaml
on:
  issues:
    types: [opened, labeled]
```

**Процесс**:
```
Issue Created/Labeled
    ↓
Checkout Repository
    ↓
Setup Python & Dependencies
    ↓
Configure Git
    ↓
Run: code-agent process-issue
    ↓
Comment on Issue (success/failure)
```

### 2. PR Review

**Файл**: `.github/workflows/pr_review.yml`

**Триггеры**:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch
```

**Jobs**:
1. **ci-checks** - запуск линтеров и тестов
2. **ai-review** - AI код-ревью (зависит от ci-checks)
3. **auto-fix** - автоматические исправления (опционально)

**Процесс**:
```
PR Created/Updated
    ↓
    ├─→ CI Checks (parallel)
    │   ├─ Ruff
    │   ├─ Black
    │   ├─ MyPy
    │   └─ Pytest
    ↓
AI Review
    ├─ Get PR diff
    ├─ Get CI results
    ├─ Run LLM analysis
    ├─ Post review
    └─ Upload summary artifact
    ↓
Auto-fix (optional)
    ├─ Check if fixes needed
    └─ Apply fixes
```

### 3. CI Pipeline

**Файл**: `.github/workflows/ci.yml`

**Триггеры**: Push и PR в main/develop

**Jobs**:
- Линтинг и форматирование
- Запуск тестов
- Сборка Docker образа
- Кэширование зависимостей

## Потоки данных

### Поток 1: Обработка Issue

```
GitHub Issue
    ↓ (webhook trigger)
GitHub Actions: Issue Handler
    ↓ (CLI command)
Code Agent
    ↓ (API request)
LLM Service
    ↓ (code generation)
Git Repository (local)
    ↓ (commit & push)
GitHub (remote)
    ↓ (API call)
Pull Request Created
```

### Поток 2: Ревью Pull Request

```
GitHub PR
    ↓ (webhook trigger)
GitHub Actions: PR Review
    ↓ (parallel execution)
    ├─→ CI Checks
    └─→ Reviewer Agent
        ↓ (API request)
    LLM Service
        ↓ (review generation)
GitHub PR (review posted)
```

### Поток 3: Итеративное исправление

```
Review Feedback
    ↓ (manual or auto trigger)
Code Agent: fix_pr_issues()
    ↓ (LLM request)
Updated Code
    ↓ (commit & push)
PR Updated
    ↓ (webhook)
PR Review (repeat)
```

## Модель данных

### Issue
```python
{
    "number": int,
    "title": str,
    "body": str,
    "state": str,
    "labels": List[str],
    "assignees": List[str],
    "created_at": datetime,
    "updated_at": datetime
}
```

### Pull Request
```python
{
    "number": int,
    "title": str,
    "body": str,
    "head": str,  # branch name
    "base": str,  # target branch
    "diff": str,  # code changes
    "files": List[File],
    "checks": List[Check]
}
```

### Review Result
```python
{
    "approved": bool,
    "feedback": str,
    "issues": List[str]
}
```

## Безопасность

### Управление секретами
- GitHub Secrets для CI/CD
- .env файл для локальной разработки
- Никогда не коммитим секреты в код

### Git конфигурация
- Отдельный bot аккаунт для коммитов
- Ограниченные права доступа
- Работа только в feature ветках

### LLM безопасность
- Валидация и очистка входных данных
- Ограничение контекста (избегаем утечки данных)
- Обработка ошибок и таймаутов

## Масштабируемость

### Горизонтальное масштабирование
- Можно запустить несколько инстансов для разных репозиториев
- Stateless архитектура (кроме git операций)

### Оптимизация производительности
- Кэширование зависимостей в CI
- Параллельное выполнение проверок
- Инкрементальная обработка (только измененные файлы)

### Ограничения
- Лимиты GitHub API (5000 req/hour)
- Лимиты LLM API (rate limits, tokens)
- MAX_ITERATIONS для предотвращения бесконечных циклов

## Расширяемость

### Добавление нового LLM провайдера

1. Создайте класс, наследующий `LLMProvider`:
```python
class CustomLLMProvider(LLMProvider):
    def generate(self, messages, temperature, max_tokens):
        # Ваша реализация
        pass
```

2. Обновите `get_llm_provider()` в `llm.py`

3. Добавьте конфигурацию в `config.py`

### Добавление новых команд CLI

1. Добавьте команду в `cli.py`:
```python
@app.command()
def new_command():
    # Ваша реализация
    pass
```

### Добавление новых проверок CI

1. Добавьте step в `.github/workflows/pr_review.yml`:
```yaml
- name: New Check
  run: your-check-command
```

## Мониторинг и логирование

### Логирование
- Уровни: DEBUG, INFO, WARNING, ERROR
- Форматирование через Rich
- Логи в stdout (можно перенаправить в файл)

### Мониторинг
- GitHub Actions logs
- Метрики CI/CD (время выполнения, success rate)
- LLM usage tracking (количество запросов, токенов)

## Тестирование

### Уровни тестирования

1. **Unit tests** (`tests/unit/`)
   - Тестируют отдельные компоненты
   - Мокают внешние зависимости
   - Быстрые и изолированные

2. **Integration tests** (`tests/integration/`)
   - Тестируют взаимодействие компонентов
   - Используют тестовые репозитории
   - Требуют реальные API ключи

3. **End-to-end tests**
   - Полный цикл: Issue → PR → Review
   - Запускаются вручную на тестовом репозитории

## Зависимости

### Основные
- openai - OpenAI API
- pygithub - GitHub API
- gitpython - Git операции
- typer - CLI
- rich - красивый вывод
- pydantic - валидация конфигурации

### Dev зависимости
- pytest - тестирование
- mypy - проверка типов
- ruff - линтинг
- black - форматирование

## Будущие улучшения

### Возможные расширения

1. **Webhook server** - реагировать на события в реальном времени
2. **База данных** - хранить историю изменений и метрики
3. **Dashboard** - веб-интерфейс для мониторинга
4. **Multi-repo support** - одновременная работа с несколькими репозиториями
5. **Advanced prompts** - более сложные промпты с примерами (few-shot)
6. **Code search** - интеграция с code search для лучшего понимания кодовой базы
7. **Incremental learning** - обучение на истории успешных изменений

### Оптимизации

1. **Кэширование LLM ответов** - для похожих запросов
2. **Параллельная обработка файлов** - ускорение генерации
3. **Streaming LLM** - отображение прогресса генерации
4. **Fine-tuning** - специализированная модель для конкретного проекта

