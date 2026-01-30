# Развертывание Code Agent на Cloud.ru

Подробная инструкция по развертыванию решения на платформе Cloud.ru для получения дополнительных баллов в конкурсе.

## 🎯 Цель

Развернуть Code Agent на Cloud.ru для демонстрации работы в production-окружении и получения дополнительных баллов.

## 📋 Требования

- Аккаунт на https://cloud.ru (можно использовать бесплатный период)
- Docker образ Code Agent (уже готов)
- GitHub Token
- OpenAI API Key (или Yandex GPT)

## 🚀 Вариант 1: Cloud.ru Container Service

### Шаг 1: Регистрация на Cloud.ru

1. Перейдите на https://cloud.ru
2. Нажмите "Регистрация" или "Попробовать бесплатно"
3. Заполните данные и подтвердите email
4. Активируйте бесплатный период

### Шаг 2: Создание Container Registry

1. Войдите в консоль Cloud.ru: https://console.cloud.ru
2. Перейдите в раздел **Container Registry**
3. Нажмите **Создать реестр**
4. Укажите имя: `code-agent-registry`
5. Выберите регион: `Россия-1`
6. Нажмите **Создать**

### Шаг 3: Загрузка Docker образа

```bash
# 1. Аутентификация в Cloud.ru registry
docker login cr.cloud.ru
# Введите логин и пароль от Cloud.ru

# 2. Tag образа для Cloud.ru
docker tag code-agent:latest cr.cloud.ru/code-agent-registry/code-agent:1.0.0

# 3. Push образа
docker push cr.cloud.ru/code-agent-registry/code-agent:1.0.0
```

### Шаг 4: Создание Cloud Run Service

1. В консоли Cloud.ru перейдите в **Cloud Run**
2. Нажмите **Создать сервис**
3. Заполните данные:
   - **Имя**: `code-agent-service`
   - **Регион**: `Россия-1`
   - **Образ**: `cr.cloud.ru/code-agent-registry/code-agent:1.0.0`
   - **Port**: `8080` (если планируете webhook сервер)

4. Настройте **Environment Variables**:
   ```
   GITHUB_TOKEN=<ваш_github_token>
   GITHUB_REPO=username/repository
   OPENAI_API_KEY=<ваш_openai_key>
   LLM_PROVIDER=openai
   MAX_ITERATIONS=5
   LOG_LEVEL=INFO
   ```

5. Настройте **Resources**:
   - CPU: 1 vCPU
   - Memory: 2 GB
   - Max instances: 3

6. Нажмите **Создать**

### Шаг 5: Настройка GitHub Actions для Cloud.ru

Обновите `.github/workflows/issue_handler.yml`:

```yaml
- name: Deploy to Cloud.ru
  if: success()
  run: |
    # Trigger Cloud Run job
    curl -X POST https://code-agent-service.cloud.ru/api/process-issue \
      -H "Authorization: Bearer ${{ secrets.CLOUD_RU_TOKEN }}" \
      -d '{"issue_number": ${{ github.event.issue.number }}}'
```

## 🚀 Вариант 2: Cloud.ru Kubernetes (K8s)

### Шаг 1: Создание Kubernetes кластера

1. В консоли Cloud.ru перейдите в **Kubernetes**
2. Нажмите **Создать кластер**
3. Заполните:
   - **Имя**: `code-agent-cluster`
   - **Версия K8s**: `1.28`
   - **Master**: 1 узел, 2 vCPU, 4 GB RAM
   - **Nodes**: 2 узла, 2 vCPU, 4 GB RAM каждый

4. Создайте кластер (займёт ~10 минут)

### Шаг 2: Подключение к кластеру

```bash
# Установите kubectl (если ещё не установлен)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Получите kubeconfig из консоли Cloud.ru
# Settings → Kubeconfig → Download

# Настройте kubectl
export KUBECONFIG=~/kubeconfig-code-agent.yaml
kubectl get nodes
```

### Шаг 3: Создание Kubernetes манифестов

Создайте файл `k8s/deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: code-agent

---
apiVersion: v1
kind: Secret
metadata:
  name: code-agent-secrets
  namespace: code-agent
type: Opaque
stringData:
  GITHUB_TOKEN: "your_github_token_here"
  GITHUB_REPO: "username/repository"
  OPENAI_API_KEY: "your_openai_key_here"
  LLM_PROVIDER: "openai"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-agent
  namespace: code-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: code-agent
  template:
    metadata:
      labels:
        app: code-agent
    spec:
      containers:
      - name: code-agent
        image: cr.cloud.ru/code-agent-registry/code-agent:1.0.0
        envFrom:
        - secretRef:
            name: code-agent-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        command: ["python", "-m", "code_agent.cli"]
        args: ["--help"]

---
apiVersion: v1
kind: Service
metadata:
  name: code-agent-service
  namespace: code-agent
spec:
  selector:
    app: code-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Шаг 4: Деплой в Kubernetes

```bash
# Применить манифесты
kubectl apply -f k8s/deployment.yaml

# Проверить статус
kubectl get pods -n code-agent
kubectl get svc -n code-agent

# Получить external IP
kubectl get svc code-agent-service -n code-agent
```

### Шаг 5: Запуск задачи в K8s

```bash
# Создать Job для обработки Issue
kubectl create job process-issue-1 \
  --image=cr.cloud.ru/code-agent-registry/code-agent:1.0.0 \
  --namespace=code-agent \
  -- python -m code_agent.cli process-issue 1
```

## 🚀 Вариант 3: Cloud.ru VM с Docker

### Шаг 1: Создание виртуальной машины

1. В консоли Cloud.ru перейдите в **Compute** → **Instances**
2. Нажмите **Создать инстанс**
3. Заполните:
   - **Имя**: `code-agent-vm`
   - **Образ**: `Ubuntu 22.04 LTS`
   - **Размер**: 2 vCPU, 4 GB RAM, 50 GB диск
   - **SSH ключ**: добавьте свой публичный ключ

4. Создайте инстанс

### Шаг 2: Подключение к VM

```bash
# Получите IP адрес из консоли
ssh ubuntu@<vm-ip-address>
```

### Шаг 3: Установка Docker

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker ubuntu
newgrp docker

# Проверка
docker --version
```

### Шаг 4: Деплой Code Agent

```bash
# Клонирование репозитория
git clone https://github.com/your-username/code-agent.git
cd code-agent

# Создание .env файла
cat > .env << EOF
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/repository
OPENAI_API_KEY=your_openai_key_here
LLM_PROVIDER=openai
MAX_ITERATIONS=5
LOG_LEVEL=INFO
EOF

# Сборка и запуск
docker compose build
docker compose up -d

# Проверка
docker compose ps
docker compose logs -f
```

### Шаг 5: Настройка автозапуска

```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/code-agent.service << EOF
[Unit]
Description=Code Agent Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/code-agent
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Включение и запуск сервиса
sudo systemctl enable code-agent
sudo systemctl start code-agent
sudo systemctl status code-agent
```

## 🔒 Безопасность

### 1. Secrets Management

Используйте Cloud.ru Secrets Manager:

```bash
# Создание секретов через API
curl -X POST https://api.cloud.ru/secrets \
  -H "Authorization: Bearer $CLOUD_RU_TOKEN" \
  -d '{
    "name": "code-agent-github-token",
    "value": "your_github_token"
  }'
```

### 2. Network Security

- Настройте Security Groups в Cloud.ru
- Разрешите только необходимые порты (443 для HTTPS)
- Используйте приватные сети для внутренних коммуникаций

### 3. HTTPS/TLS

Настройте SSL сертификат через Cloud.ru Certificate Manager или Let's Encrypt.

## 📊 Мониторинг

### Cloud.ru Monitoring

1. В консоли перейдите в **Monitoring**
2. Создайте dashboard для Code Agent:
   - CPU usage
   - Memory usage
   - Network traffic
   - Container restarts

### Логирование

```bash
# Просмотр логов в K8s
kubectl logs -f deployment/code-agent -n code-agent

# Просмотр логов в Docker
docker compose logs -f
```

## 💰 Стоимость

**Бесплатный период Cloud.ru** включает:
- 300₽ на первый месяц
- Бесплатные тиры для некоторых сервисов

**Примерная стоимость после бесплатного периода:**
- Cloud Run: ~500₽/месяц (при небольшой нагрузке)
- Kubernetes: ~2000₽/месяц (минимальный кластер)
- VM: ~1000₽/месяц (2 vCPU, 4GB RAM)

## 🎯 Демонстрация для конкурса

### Что показать жюри:

1. **Работающий сервис** на Cloud.ru с публичным URL
2. **Логи деплоя** и работы приложения
3. **Мониторинг** в реальном времени
4. **GitHub Integration** - создание Issue → автоматический PR
5. **Масштабируемость** - показать автоскейлинг при нагрузке

### Скриншоты для отчёта:

1. Консоль Cloud.ru с запущенным сервисом
2. Логи успешного деплоя
3. Мониторинг метрик
4. GitHub PR созданный агентом
5. Результаты CI/CD

## 🐛 Troubleshooting

### Проблема: Образ не загружается

```bash
# Проверьте аутентификацию
docker login cr.cloud.ru

# Проверьте тег
docker images | grep code-agent
```

### Проблема: Pod не стартует

```bash
# Посмотрите события
kubectl describe pod <pod-name> -n code-agent

# Проверьте логи
kubectl logs <pod-name> -n code-agent
```

### Проблема: Недостаточно ресурсов

Увеличьте лимиты в `deployment.yaml`:

```yaml
resources:
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

## 📚 Дополнительные ресурсы

- [Документация Cloud.ru](https://docs.cloud.ru/)
- [Cloud.ru API](https://api-docs.cloud.ru/)
- [Cloud.ru Support](https://support.cloud.ru/)

## ✅ Чеклист для сдачи

- [ ] Сервис развёрнут и работает на Cloud.ru
- [ ] Получен публичный URL
- [ ] Настроена интеграция с GitHub
- [ ] Сделаны скриншоты консоли
- [ ] Записано видео демонстрации (опционально)
- [ ] Подготовлен отчёт с ссылками
- [ ] Протестирована работа: Issue → PR

---

**Итого**: Развертывание на Cloud.ru даёт дополнительные баллы и демонстрирует production-ready решение! 🏆

**Версия**: 1.0.0  
**Дата**: 2024-01-29

