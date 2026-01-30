# Инструкция по установке Code Agent

## Системные требования

- **Операционная система**: Linux, macOS, Windows (с WSL2)
- **Python**: 3.11 или выше
- **Git**: 2.0 или выше
- **Docker**: 20.10+ (опционально)
- **Docker Compose**: 2.0+ (опционально)

## Вариант 1: Установка через Docker (Рекомендуется)

### Шаг 1: Установка Docker

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
```

#### Windows
```bash
# Установите WSL2 и Docker Desktop
# https://docs.docker.com/desktop/windows/install/
```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/your-username/code-agent.git
cd code-agent
```

### Шаг 3: Конфигурация

```bash
# Создайте файл .env
cp env.example .env

# Отредактируйте .env и добавьте свои credentials
nano .env
```

Минимальная конфигурация:
```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=username/repository
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

### Шаг 4: Сборка и запуск

```bash
# Сборка образа
docker-compose build

# Проверка установки
docker-compose run code-agent version

# Запуск команды
docker-compose run code-agent process-issue 1
```

## Вариант 2: Локальная установка

### Шаг 1: Установка Python 3.11+

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
```

#### macOS
```bash
brew install python@3.11 git
```

#### Windows (WSL2)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
```

### Шаг 2: Клонирование и настройка

```bash
# Клонирование
git clone https://github.com/your-username/code-agent.git
cd code-agent

# Автоматическая настройка
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Скрипт setup.sh выполнит:
- Создание виртуального окружения
- Установку всех зависимостей
- Установку code-agent пакета
- Создание .env файла

### Шаг 3: Ручная настройка (если setup.sh не работает)

```bash
# Создание виртуального окружения
python3.11 -m venv venv

# Активация
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate  # Windows

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Установка пакета
pip install -e .

# Создание .env
cp env.example .env
nano .env
```

### Шаг 4: Проверка установки

```bash
# Активируйте venv если ещё не активировано
source venv/bin/activate

# Проверьте версию
code-agent version

# Проверьте помощь
code-agent --help
```

## Получение необходимых токенов и ключей

### GitHub Personal Access Token

1. Перейдите на https://github.com/settings/tokens
2. Нажмите **Generate new token** → **Generate new token (classic)**
3. Выберите scopes:
   - `repo` (полный доступ к репозиториям)
   - `workflow` (для управления GitHub Actions)
4. Скопируйте токен (он показывается один раз!)

### OpenAI API Key

1. Зарегистрируйтесь на https://platform.openai.com
2. Перейдите в **API Keys**: https://platform.openai.com/api-keys
3. Создайте новый ключ
4. Скопируйте ключ

### Yandex GPT API Key (опционально)

1. Зарегистрируйтесь в Yandex Cloud: https://cloud.yandex.ru
2. Создайте сервисный аккаунт
3. Получите API ключ
4. Найдите Folder ID в консоли Yandex Cloud

## Настройка GitHub Actions

Для автоматической работы в вашем репозитории:

1. Скопируйте `.github/workflows/` в ваш репозиторий
2. Добавьте secrets в настройках репозитория:
   - Settings → Secrets and variables → Actions
   - New repository secret
   - Добавьте:
     - `OPENAI_API_KEY` (или `YANDEX_API_KEY` + `YANDEX_FOLDER_ID`)
     - `LLM_PROVIDER` (openai или yandex)

`GITHUB_TOKEN` доступен автоматически.

## Настройка локального репозитория

Для работы Code Agent с вашим репозиторием:

```bash
# Клонируйте ваш репозиторий
git clone https://github.com/username/your-repo.git
cd your-repo

# Настройте git
git config user.name "Code Agent Bot"
git config user.email "code-agent@example.com"

# Запустите Code Agent
code-agent process-issue 123 --repo-path .
```

## Проверка установки

### Проверка CLI

```bash
code-agent version
code-agent --help
```

### Проверка зависимостей

```bash
# Проверка Python версии
python --version  # должно быть 3.11+

# Проверка пакетов
pip list | grep -E "(openai|pygithub|gitpython|typer)"
```

### Проверка конфигурации

```bash
# Создайте тестовый файл
cat > test_config.py << 'EOF'
from code_agent.config import settings
print(f"GitHub Repo: {settings.github_repo}")
print(f"LLM Provider: {settings.llm_provider}")
print(f"Max Iterations: {settings.max_iterations}")
EOF

# Запустите проверку
python test_config.py
rm test_config.py
```

## Решение проблем

### Проблема: "ModuleNotFoundError: No module named 'code_agent'"

**Решение**:
```bash
# Убедитесь что venv активирован
source venv/bin/activate

# Переустановите пакет
pip install -e .
```

### Проблема: "Permission denied" при запуске Docker

**Решение**:
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиньтесь или выполните
newgrp docker
```

### Проблема: "API key is invalid"

**Решение**:
- Проверьте что .env файл существует и содержит корректные ключи
- Проверьте что ключ OpenAI активен
- Проверьте баланс на аккаунте OpenAI

### Проблема: Git authentication failed

**Решение**:
```bash
# Настройте SSH ключи или используйте HTTPS с токеном
git config --global credential.helper store

# Или используйте SSH
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # Добавьте на GitHub
```

## Следующие шаги

После успешной установки:

1. Прочитайте [README.md](../README.md) для примеров использования
2. Изучите [ARCHITECTURE.md](./ARCHITECTURE.md) для понимания системы
3. Создайте тестовый Issue в вашем репозитории
4. Запустите `code-agent process-issue <number>`

## Дополнительная настройка

### Настройка промптов

Отредактируйте `config/prompts.yaml` для кастомизации поведения LLM.

### Настройка лимитов

В `.env` файле:
```env
MAX_ITERATIONS=10  # Увеличить лимит итераций
```

### Настройка логирования

```env
LOG_LEVEL=DEBUG  # Для детального вывода
```

## Обновление

### Docker
```bash
git pull
docker-compose build
```

### Локальная установка
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
pip install -e .
```

