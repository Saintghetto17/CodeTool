# 🎯 Инструкция: как запускать демо (пошагово)

## 📌 Что именно покажем на демо

- **Issue** в GitHub (как “вход” в SDLC)
- **Code Agent**: анализ issue → правки в локальном клоне → commit → попытка push/PR
- **AI Reviewer**: review diff → печать фидбэка → (опционально) summary для GitHub Actions

Важно: в реальных репозиториях часто нет прав пушить (403). Для стабильной презентации используется **DEMO_MODE** — тогда **ничего не падает**, а вместо PR сохраняются артефакты (`.code_agent_demo/*.diff`) и review делается по ним.

---

## ✅ Вариант A (рекомендуется): DEMO_MODE, “ничего не падает”

### Шаг 0. Перейти в проект

```bash
cd /home/ilyanovitskiy/CodeTool
```

### Шаг 1. Подготовить `.env`

Если используешь OpenRouter (как у нас в демо):

```bash
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=Saintghetto17/Naive-Bayes-Classifier
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_PROVIDER=openrouter
LOG_LEVEL=INFO
EOF
```

Примечания:
- `GITHUB_TOKEN` тут нужен, чтобы **читать issue**. Пушить в этот репозиторий токен всё равно не сможет — это нормально для демо.
- Если LLM временно недоступен — пайплайн не должен падать (есть fallback в коде).

### Шаг 2. Подготовить чистый локальный клон “целевого” репозитория

```bash
rm -rf target_repo_demo
git clone --depth 1 https://github.com/Saintghetto17/Naive-Bayes-Classifier.git target_repo_demo
```

### Шаг 3. Собрать Docker-образ

```bash
docker compose build
```

### Шаг 4. Запустить Code Agent на issue #1 (DEMO_MODE=1)

Эта команда:
- сделает изменения в `target_repo_demo`
- закоммитит
- попытается `git push` → если 403, **не упадёт**
- сохранит diff в `target_repo_demo/.code_agent_demo/issue-1.diff`

```bash
DEMO_MODE=1 docker compose run --rm code-agent-cli process-issue 1 --repo-path ./target_repo_demo --log-level INFO
```

Ожидаемый результат в консоли:
- сообщение `DEMO_MODE: PR was not created on GitHub (permissions)`
- путь `Local diff: .code_agent_demo/issue-1.diff`

### Шаг 5. Запустить AI Reviewer по локальному diff (PR #0)

В DEMO_MODE ревьюер умеет `review-pr 0` (ноль означает “взять последний diff-артефакт”):

```bash
DEMO_MODE=1 docker compose run --rm code-agent-cli review-pr 0 --repo-path ./target_repo_demo --log-level INFO
```

### Шаг 6. (Опционально) Сгенерировать summary как для GitHub Actions

```bash
DEMO_MODE=1 docker compose run --rm code-agent-cli generate-summary 0 --repo-path ./target_repo_demo --log-level INFO > /tmp/review_summary.md
sed -n '1,120p' /tmp/review_summary.md
```

### Шаг 7. Что именно показать судье (быстрый чек-лист)

- **GitHub Issue**: открыть issue #1 в `Saintghetto17/Naive-Bayes-Classifier`
- **Логи агента**: показать вывод `process-issue` (видно analysis → modified files → commit → push attempt)
- **Артефакт diff**: открыть файл `target_repo_demo/.code_agent_demo/issue-1.diff`
- **Логи ревьюера**: показать вывод `review-pr 0` (feedback/issues)
- **Summary**: показать `/tmp/review_summary.md`

---

## 🌐 Вариант B: “полный GitHub” (реальный PR + review в GitHub)

Это будет работать только если у токена есть права пушить. Самый простой путь:

### Шаг 1. Форкнуть репозиторий

Сделай fork `Saintghetto17/Naive-Bayes-Classifier` в свой аккаунт.

### Шаг 2. `.env` для своего форка

```bash
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=YOUR_USERNAME/Naive-Bayes-Classifier
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_PROVIDER=openrouter
LOG_LEVEL=INFO
EOF
```

### Шаг 3. Клон форка + запуск без DEMO_MODE

```bash
rm -rf target_repo_real
git clone --depth 1 https://github.com/YOUR_USERNAME/Naive-Bayes-Classifier.git target_repo_real

docker compose build
docker compose run --rm code-agent-cli process-issue 1 --repo-path ./target_repo_real --log-level INFO
```

Дальше появится реальный PR номер, и можно:

```bash
docker compose run --rm code-agent-cli review-pr <PR_NUMBER> --log-level INFO
docker compose run --rm code-agent-cli generate-summary <PR_NUMBER> --log-level INFO
```

---

## 🔧 Частые проблемы (и что делать)

### 403 на push

Это **нормально**, если репозиторий чужой. Для демонстрации просто используй **DEMO_MODE=1**.

### Permission denied при записи в `target_repo_demo`

Мы сделали так, что `code-agent-cli` по умолчанию запускается как root внутри контейнера (для “неубиваемого” демо).
