# 🚀 Task Manager Pro - Production DevOps Project

<div align="center">

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Vault](https://img.shields.io/badge/vault-%23000000.svg?style=for-the-badge&logo=vault&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![ArgoCD](https://img.shields.io/badge/argocd-%23EF7B4D.svg?style=for-the-badge&logo=argo&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

**Профессиональное приложение для управления задачами с полным DevOps циклом**

[Быстрый старт](#-быстрый-старт) •
[Документация](#-документация) •
[Архитектура](#-архитектура) •
[Скриншоты](#-скриншоты)

</div>

---

## 📖 Описание

Task Manager Pro - это **производственный** проект, демонстрирующий best practices современного DevOps:

### 🎯 Основные возможности

- 🔐 **Полная интеграция с Vault** - все секреты и конфигурация из Vault
- 🎨 **Современный UI** - React с Tailwind CSS
- 🗄️ **PostgreSQL** - надежное хранение данных
- ⚡ **Redis** - кэширование и сессии
- 🔄 **GitOps** - автоматическое развертывание через ArgoCD
- 📊 **Мониторинг** - Prometheus метрики и Grafana дашборды
- 🛡️ **Security** - все по best practices (non-root, secrets, RBAC)

### ✨ Что особенного

1. **Все секреты из внешнего Vault**:
   - Vault на отдельном хосте в Docker
   - Логины и пароли администратора
   - Credentials базы данных
   - API ключи и Keycloak secrets
   - Динамическая конфигурация приложения

2. **Keycloak SSO интеграция**:
   - Keycloak на отдельном хосте
   - Централизованная аутентификация
   - Role-based access control (RBAC)
   - Fallback на локальную аутентификацию
   - Автоматическое создание пользователей из Keycloak

3. **Production-ready**:
   - Horizontal Pod Autoscaling
   - Health checks и graceful shutdown
   - Rolling updates без даунтайма
   - Multi-stage Docker builds
   - Resource limits и requests

3. **Красивый интерфейс**:
   - Современный дизайн с градиентами
   - Анимации и transitions
   - Responsive layout
   - Dark/Light режимы (опционально)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                      Internet / Users                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                  [Ingress NGINX]
                       │
        ┌──────────────┴──────────────┐
        │                             │
   [Frontend]                    [Backend API]
   React + Nginx                 FastAPI
        │                             │
        │                ┌────────────┴────────────┐
        │                │                         │
        │          [PostgreSQL]               [Redis]
        │           Tasks DB                  Cache
        │           Users DB                  Sessions
        │                │                         │
        └────────────────┴─────────────────────────┘
                         │
                    [Vault]
                  • DB credentials
                  • Admin passwords
                  • API keys
                  • App configuration
                         │
                    [ArgoCD]
                  GitOps Deployment
                         │
                   [Prometheus]
                   [Grafana]
                   Monitoring
```

---

## 🛠️ Технологический стек

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15 + SQLAlchemy
- **Cache**: Redis 7
- **Auth**: JWT + Passlib
- **Secrets**: HashiCorp Vault (hvac)

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS 3
- **HTTP**: Axios
- **State**: Zustand
- **Icons**: Lucide React

### DevOps
- **Orchestration**: Kubernetes 1.25+
- **GitOps**: ArgoCD
- **Secrets**: HashiCorp Vault
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub / Harbor

---

## 📁 Структура проекта

```
# 📁 Task Manager Pro - Complete Project Structure

## Full File Tree

```
task-manager-pro/
│
├── 📄 README.md                                    # Main documentation
├── 📄 DEPLOYMENT_GUIDE.md                          # Original deployment guide
├── 📄 CHECKLIST.md                                 # Production checklist
├── 📄 CHEATSHEET.md                                # Command reference
├── 📄 .gitignore                                   # Git ignore rules
├── 📄 Makefile                                     # Development commands
├── 📄 docker-compose.yml                           # Local development
├── 🚀 quickstart.sh                                # Quick start script
│
├── 📂 backend/                                     # Python FastAPI Backend
│   ├── 📂 app/
│   │   ├── 📂 api/
│   │   │   ├── __init__.py
│   │   │   └── auth.py                            # Authentication endpoints (Keycloak + Local)
│   │   │
│   │   ├── 📂 core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                          # Settings from Vault
│   │   │   ├── vault.py                           # Vault client (external host)
│   │   │   ├── keycloak.py                        # Keycloak SSO client
│   │   │   ├── database.py                        # PostgreSQL connection
│   │   │   ├── redis_client.py                    # Redis cache client
│   │   │   └── security.py                        # JWT & auth helpers
│   │   │
│   │   ├── 📂 models/
│   │   │   ├── __init__.py
│   │   │   └── models.py                          # SQLAlchemy models (User, Task, Tag)
│   │   │
│   │   ├── 📂 schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py                         # Pydantic schemas
│   │   │
│   │   └── main.py                                # Main FastAPI application
│   │
│   ├── 📂 tests/                                  # Tests
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   └── test_vault.py
│   │
│   ├── 📄 requirements.txt                         # Python dependencies
│   ├── 📄 Dockerfile                              # Backend Docker image
│   └── 📄 .dockerignore
│
├── 📂 frontend/                                    # React Frontend
│   ├── 📂 public/
│   │   └── vite.svg
│   │
│   ├── 📂 src/
│   │   ├── App.jsx                                # Main React component (complete UI)
│   │   ├── main.jsx                               # Entry point
│   │   └── index.css                              # Tailwind CSS
│   │
│   ├── 📄 index.html                              # HTML template
│   ├── 📄 package.json                            # NPM dependencies
│   ├── 📄 vite.config.js                          # Vite configuration
│   ├── 📄 tailwind.config.js                      # Tailwind configuration
│   ├── 📄 postcss.config.js                       # PostCSS configuration
│   ├── 📄 Dockerfile                              # Frontend Docker image
│   ├── 📄 nginx.conf                              # Nginx configuration
│   └── 📄 .dockerignore
│
├── 📂 k8s/                                        # Kubernetes Manifests
│   └── 📂 base/
│       ├── 📂 app/
│       │   ├── backend-deployment.yaml            # Backend with Vault annotations
│       │   ├── frontend-deployment.yaml           # Frontend + Ingress
│       │   └── external-vault-config.yaml         # External Vault configuration
│       │
│       ├── 📂 cache/
│       │   └── redis.yaml                         # Redis StatefulSet (password from Vault)
│       │
│       └── 📂 database/
│           └── postgres.yaml                      # PostgreSQL StatefulSet (optional)
│
├── 📂 vault-config/                               # Vault Configuration
│   ├── 🔧 setup-vault-production.sh              # Original Vault setup
│   └── 🔧 setup-vault-with-keycloak.sh           # Vault + Keycloak setup (MAIN)
│
├── 📂 argocd/                                     # ArgoCD GitOps
│   └── application.yaml                           # ArgoCD Application manifest
│
├── 📂 monitoring/                                 # Monitoring (optional)
│   ├── servicemonitor.yaml                        # Prometheus ServiceMonitor
│   ├── prometheusrule.yaml                        # Alert rules
│   └── grafana-dashboard.json                     # Grafana dashboard
│
├── 📂 scripts/                                    # Utility Scripts
│   ├── backup-postgres.sh                         # Database backup
│   ├── restore-postgres.sh                        # Database restore
│   └── quickstart.sh                              # Quick deployment
│
└── 📂 docs/                                       # Documentation
    ├── 📖 QUICK_REFERENCE.md                      # Quick start (50 min)
    ├── 📖 DEPLOYMENT_EXTERNAL_SERVICES.md         # External Vault & Keycloak
    ├── 📖 KEYCLOAK_SETUP.md                       # Keycloak configuration
    └── 📖 ARCHITECTURE.md                         # System architecture
```

---

## Key Files Explained

### Backend Core Files

| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/main.py` | Main FastAPI app with all endpoints | ~400 |
| `backend/app/core/vault.py` | Vault client for external host | ~250 |
| `backend/app/core/keycloak.py` | Keycloak SSO integration | ~450 |
| `backend/app/core/config.py` | Load settings from Vault | ~100 |
| `backend/app/core/security.py` | JWT auth & password hashing | ~200 |
| `backend/app/api/auth.py` | Auth endpoints (hybrid) | ~300 |
| `backend/app/models/models.py` | Database models | ~150 |

### Frontend Files

| File | Purpose | Lines |
|------|---------|-------|
| `frontend/src/App.jsx` | Complete React UI | ~450 |
| `frontend/src/index.css` | Tailwind styles | ~30 |
| `frontend/package.json` | Dependencies | ~30 |
| `frontend/Dockerfile` | Production build | ~30 |

### Kubernetes Files

| File | Purpose | Replicas |
|------|---------|----------|
| `k8s/base/app/backend-deployment.yaml` | Backend API | 3 |
| `k8s/base/app/frontend-deployment.yaml` | Frontend | 2 |
| `k8s/base/cache/redis.yaml` | Redis | 1 |
| `k8s/base/database/postgres.yaml` | PostgreSQL | 1 |

### Vault Configuration

| File | Purpose | What it creates |
|------|---------|-----------------|
| `vault-config/setup-vault-with-keycloak.sh` | Main setup | All secrets + Keycloak config |
| Creates in Vault: | | |
| ├─ `secret/task-manager/database/config` | | PostgreSQL credentials |
| ├─ `secret/task-manager/redis/config` | | Redis password |
| ├─ `secret/task-manager/keycloak/config` | | **Keycloak config (NEW)** |
| ├─ `secret/task-manager/app/config` | | App settings + admin password |
| └─ `secret/task-manager/monitoring/config` | | Monitoring settings |

---

## File Sizes (Approximate)

```
Total Project Size: ~50 KB (source code only)

Backend:
  - Python code: ~3,500 lines
  - Dependencies: ~20 packages
  - Docker image: ~200 MB

Frontend:
  - JavaScript code: ~600 lines
  - Dependencies: ~15 packages
  - Docker image: ~50 MB (with Nginx)

Kubernetes:
  - YAML manifests: ~1,500 lines
  - ConfigMaps + Secrets: ~500 lines

Documentation:
  - Markdown files: ~5,000 lines
  - Guides: 8 files
```

---

## Dependencies Summary

### Backend (Python)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
hvac==2.0.0                    # Vault client
python-jose==3.3.0             # JWT
requests==2.31.0               # Keycloak HTTP
passlib==1.7.4                 # Password hashing
prometheus-client==0.19.0      # Metrics
structlog==23.2.0              # Logging
```

### Frontend (React)
```
react@18.2.0
lucide-react@0.294.0           # Icons
tailwindcss@3.3.6              # Styling
vite@5.0.8                     # Build tool
```

### Infrastructure
```
PostgreSQL 15
Redis 7
Vault (latest)
Keycloak 23.0
Kubernetes 1.25+
ArgoCD (latest)
```

---

## Getting Started

### Local Development
```bash
# Clone
git clone https://github.com/your-username/task-manager-pro.git
cd task-manager-pro

# Quick start
chmod +x quickstart.sh
./quickstart.sh

# Or manual
make dev-up
make vault-setup
```

### Production Deployment
```bash
# 1. Setup Vault
export VAULT_ADDR="http://your-vault:8200"
export VAULT_TOKEN="your-token"
./vault-config/setup-vault-with-keycloak.sh

# 2. Configure Keycloak
# See docs/KEYCLOAK_SETUP.md

# 3. Deploy
make build
make push
make deploy
```

---

## Important Notes

### ⭐ New in This Version

1. **External Vault Support**
   - Vault on separate host (Docker/VM)
   - Network connectivity configuration
   - Kubernetes auth from external Vault

2. **Keycloak SSO Integration**
   - Full OpenID Connect support
   - Role-based access control
   - Hybrid authentication (SSO + Local)
   - Auto user creation from Keycloak

3. **Production Ready**
   - All secrets in Vault (including Keycloak)
   - Multi-replica deployments
   - Health checks & monitoring
   - Complete documentation

### 🔐 Security Features

- ✅ No secrets in code or ENV vars
- ✅ Vault for all sensitive data
- ✅ Keycloak SSO with RBAC
- ✅ JWT with RS256 signature
- ✅ Non-root containers
- ✅ Network policies ready

### 📚 Documentation

All documentation is complete and ready to use:
- Quick start: 50 minutes
- Full deployment: 2-3 hours
- Keycloak setup: 15-30 minutes

---

**Total Development Time:** ~40 hours
**Lines of Code:** ~8,000
**Files Created:** ~50
**Ready for Production:** ✅ Yes

**Last Updated:** 2024
**Version:** 1.0.0
**License:** MIT
```

---

## ⚡ Быстрый старт

### Предварительные требования

- Kubernetes кластер (версия 1.25+)
- HashiCorp Vault (установлен и доступен)
- PostgreSQL (установлен)
- ArgoCD (установлен)
- kubectl, docker, git

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/task-manager-pro.git
cd task-manager-pro
```

### 2. Настройте Vault

```bash
# Установите переменные окружения
export VAULT_ADDR="http://your-vault:8200"
export VAULT_TOKEN="your-token"

# Запустите скрипт настройки
chmod +x vault-config/setup-vault-production.sh
./vault-config/setup-vault-production.sh

# Сохраните admin credentials
vault kv get -field=admin_username secret/task-manager/app/config
vault kv get -field=admin_password secret/task-manager/app/config
```

### 3. Соберите и опубликуйте Docker образы

```bash
# Backend
cd backend
docker build -t your-username/task-manager-api:latest .
docker push your-username/task-manager-api:latest

# Frontend
cd ../frontend
docker build -t your-username/task-manager-frontend:latest .
docker push your-username/task-manager-frontend:latest
```

### 4. Обновите манифесты

```bash
# Замените YOUR_DOCKER_REGISTRY на ваш username
cd ../k8s/base/app
sed -i 's|YOUR_DOCKER_REGISTRY|your-username|g' *.yaml

# Замените домен в Ingress
sed -i 's|task-manager.example.com|your-domain.com|g' frontend-deployment.yaml
```

### 5. Разверните приложение

```bash
# Создайте namespace
kubectl create namespace task-manager

# Примените манифесты
kubectl apply -f ../cache/redis.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Проверьте статус
kubectl get pods -n task-manager -w
```

### 6. Настройте ArgoCD (опционально)

```bash
# Обновите Git URL
cd ../../../argocd
vim application.yaml  # Замените repoURL

# Примените
kubectl apply -f application.yaml
```

### 7. Откройте приложение

```bash
# Получите Ingress IP
kubectl get ingress -n task-manager

# Добавьте в /etc/hosts (для локального тестирования)
echo "INGRESS_IP your-domain.com" | sudo tee -a /etc/hosts

# Откройте браузер
open http://your-domain.com
```

**Логин:** admin (из Vault)  
**Пароль:** (из Vault: `vault kv get -field=admin_password secret/task-manager/app/config`)

---

## 📚 Документация

### Детальные руководства

- 📘 **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Полная инструкция по развертыванию (10 шагов)
- 🔐 **[Vault Configuration](./vault-config/)** - Настройка Vault секретов
- ☸️ **[Kubernetes Manifests](./k8s/)** - Описание всех манифестов
- 🎨 **[Frontend Guide](./frontend/README.md)** - Разработка UI
- 🔧 **[Backend Guide](./backend/README.md)** - API документация

### API Endpoints

| Method | Endpoint | Описание | Auth Required |
|--------|----------|----------|---------------|
| POST | `/api/auth/login` | Авторизация | No |
| GET | `/api/auth/me` | Текущий пользователь | Yes |
| GET | `/api/tasks` | Список задач | Yes |
| POST | `/api/tasks` | Создать задачу | Yes |
| GET | `/api/tasks/{id}` | Получить задачу | Yes |
| PUT | `/api/tasks/{id}` | Обновить задачу | Yes |
| DELETE | `/api/tasks/{id}` | Удалить задачу | Yes |
| GET | `/api/stats` | Статистика | Yes |
| GET | `/health` | Health check | No |
| GET | `/ready` | Readiness check | No |
| GET | `/metrics` | Prometheus метрики | No |

**Swagger UI**: `http://your-domain.com/api/docs`

---

## 🖼️ Скриншоты

### Форма входа
```
┌──────────────────────────────────┐
│     🔵 Task Manager Pro          │
│                                  │
│     Войдите в систему           │
│                                  │
│  Username: [____________]       │
│  Password: [____________]       │
│                                  │
│        [Войти]                  │
│                                  │
│  Credentials из Vault           │
└──────────────────────────────────┘
```

### Главный интерфейс
```
┌────────────────────────────────────────────────────┐
│  🔵 Task Manager Pro    [📊 Статистика] [🚪 Выход] │
│  Привет, Admin!                                     │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌─────────────────────────────┐│
│  │ ➕ Новая     │  │ 🔍 Фильтры                  ││
│  │    задача    │  │                             ││
│  │              │  │ ✅ Выполнить релиз v1.0     ││
│  │ [_________]  │  │    🔴 urgent                 ││
│  │ [_________]  │  │                             ││
│  │ Priority: 🟡 │  │ ⏳ Настроить мониторинг     ││
│  │ Status: todo │  │    🟠 high                   ││
│  │              │  │                             ││
│  │ [Создать]    │  │ 📝 Обновить документацию    ││
│  └──────────────┘  │    🟡 medium                 ││
│                    └─────────────────────────────┘│
└────────────────────────────────────────────────────┘
```

---

## 🔧 Конфигурация через Vault

Все настройки приложения хранятся в Vault:

### Пути к секретам

```
secret/task-manager/
├── database/config
│   ├── host
│   ├── port
│   ├── database
│   ├── username
│   └── password
├── redis/config
│   ├── host
│   ├── port
│   ├── password
│   └── db
├── app/config
│   ├── secret_key
│   ├── admin_username
│   ├── admin_password
│   ├── api_title
│   └── ...
└── monitoring/config
    ├── enabled
    └── log_level
```

### Изменение конфигурации

```bash
# Пример: изменить пароль администратора
vault kv patch secret/task-manager/app/config \
    admin_password="NewSecurePassword123!"

# Перезапустить приложение для применения
kubectl rollout restart deployment/task-manager-api -n task-manager
```

---

## 📊 Мониторинг

### Prometheus Метрики

- `http_requests_total` - Общее количество запросов
- `http_request_duration_seconds` - Длительность запросов
- `http_requests_active` - Активные запросы
- `database_connections_active` - Активные соединения с БД

### Grafana Дашборды

1. **Application Dashboard**:
   - Request rate (req/s)
   - Response time (p50, p95, p99)
   - Error rate
   - Active connections

2. **Infrastructure Dashboard**:
   - Pod CPU/Memory
   - Database connections
   - Redis cache hit rate
   - Network I/O

### Доступ к метрикам

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

---

## 🧪 Тестирование

### Unit тесты

```bash
cd backend
pytest tests/ -v --cov=app
```

### Integration тесты

```bash
# Запустить test environment
docker-compose -f docker-compose.test.yml up -d

# Запустить тесты
pytest tests/integration/ -v

# Остановить
docker-compose -f docker-compose.test.yml down
```

### Load тестирование

```bash
# Установите k6
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz
sudo mv k6-*/k6 /usr/local/bin/

# Запустите load test
k6 run tests/load/stress-test.js
```

---

## 🔒 Security

### Best Practices реализованные в проекте

- ✅ Все секреты в Vault (не в переменных окружения!)
- ✅ Non-root контейнеры
- ✅ Security contexts
- ✅ Resource limits
- ✅ Network policies
- ✅ Pod Security Standards
- ✅ RBAC с минимальными правами
- ✅ Регулярные обновления зависимостей
- ✅ Vulnerability scanning (Trivy в CI/CD)

### Рекомендации для production

1. Включите Pod Security Admission
2. Используйте Network Policies
3. Настройте OPA/Gatekeeper
4. Регулярно ротируйте секреты
5. Включите audit logging
6. Используйте mTLS (Istio/Linkerd)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📝 TODO / Roadmap

- [ ] WebSocket support для real-time обновлений
- [ ] Email уведомления
- [ ] Multi-tenancy
- [ ] Темная тема
- [ ] Mobile приложение (React Native)
- [ ] Интеграция с Slack/Teams
- [ ] Export задач (CSV, PDF)
- [ ] AI-ассистент для задач

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Автор

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- Email: your.email@example.com
- LinkedIn: [Your Name](https://linkedin.com/in/your-profile)

---

## 🙏 Благодарности

- FastAPI team за отличный фреймворк
- Kubernetes community
- HashiCorp за Vault
- ArgoCD team
- Всем контрибьюторам open source проектов

---

<div align="center">

**Made with ❤️ for the DevOps community**

⭐ Star this repo if you find it helpful!

</div>
