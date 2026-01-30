# 🚀 Quick Start Guide

Запустите Code Agent за 5 минут!

## Вариант 1: Docker (самый быстрый) 🐳

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/code-agent.git
cd code-agent

# 2. Создайте .env файл
cat > .env << EOF
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/repository
OPENAI_API_KEY=your_openai_key_here
LLM_PROVIDER=openai
EOF

# 3. Запустите!
docker-compose build
docker-compose run code-agent --help
docker-compose run code-agent process-issue 1
```

## Вариант 2: Локально (для разработки) 💻

```bash
# 1. Клонируйте и установите
git clone https://github.com/your-username/code-agent.git
cd code-agent
./scripts/setup.sh

# 2. Активируйте venv
source venv/bin/activate

# 3. Настройте .env (отредактируйте созданный файл)
nano .env

# 4. Запустите!
code-agent --help
code-agent process-issue 1
```

## Вариант 3: Makefile команды 🔧

```bash
# Установка
make install-dev

# Запуск тестов
make test

# Линтинг
make lint

# Форматирование
make format

# Docker
make docker-build
make docker-run
```

## Получение токенов 🔑

### GitHub Token
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Выберите: `repo`, `workflow`
4. Скопируйте токен

### OpenAI API Key
1. https://platform.openai.com/api-keys
2. Create new secret key
3. Скопируйте ключ

## Первый Issue 📝

Создайте Issue в вашем репозитории:

```markdown
Title: Add hello world function

Description:
Create a function that returns "Hello, World!"

Requirements:
- Function name: hello_world()
- Returns string
- Add docstring
- Add test
```

Затем:
```bash
code-agent process-issue 1 --repo-path /path/to/your/repo
```

## GitHub Actions (автоматический режим) ⚡

1. Скопируйте workflows:
```bash
cp -r .github/workflows /path/to/your/repo/.github/
```

2. Добавьте secrets в GitHub:
   - Settings → Secrets and variables → Actions
   - Add: `OPENAI_API_KEY`, `LLM_PROVIDER`

3. Создайте Issue и добавьте метку `code-agent`

4. Всё! Агент автоматически создаст PR

## Проверка работы ✅

```bash
# Версия
code-agent version

# Помощь
code-agent --help

# Обработка Issue
code-agent process-issue 123

# Ревью PR
code-agent review-pr 456

# Исправление PR
code-agent fix-pr 456 --feedback "Add tests"
```

## Что дальше? 🎯

- 📖 Читайте [README.md](README.md) для подробностей
- 🏗️ Изучите [ARCHITECTURE.md](docs/ARCHITECTURE.md) для понимания системы
- 💡 Смотрите [EXAMPLES.md](docs/EXAMPLES.md) для примеров
- 🎬 Попробуйте [DEMO.md](DEMO.md) сценарии

## Проблемы? 🐛

- Проверьте [Issues](https://github.com/your-username/code-agent/issues)
- Создайте новый Issue с описанием проблемы
- Смотрите [INSTALLATION.md](docs/INSTALLATION.md) для troubleshooting

## Минимальные требования 📋

- Python 3.11+
- Git 2.0+
- GitHub Token
- OpenAI API Key (или YandexGPT)
- 2GB RAM
- Интернет соединение

---

**Готово!** Теперь вы можете автоматизировать разработку! 🎉

