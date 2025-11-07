"""
Task Manager Pro - Main Application
FastAPI приложение с полной интеграцией Vault
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import timedelta
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import structlog

from .core.config import settings
from .core.database import init_db, get_db, check_db_connection, engine
from .core.redis_client import redis_client
from .core.security import (
    authenticate_user, create_access_token, get_current_user,
    get_current_active_admin, get_password_hash, revoke_token
)
from .core.keycloak import keycloak_client, init_keycloak_from_vault
from .core.vault import vault_client
from .models.models import User, Task, Tag, PriorityEnum, StatusEnum
from .schemas import schemas

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

# Prometheus метрики
REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_REQUESTS = Gauge('http_requests_active', 'Active requests')
DB_CONNECTIONS = Gauge('database_connections_active', 'Active DB connections')


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("application_starting")
    
    # Startup
    try:
        # Инициализация БД
        init_db()
        
        # Проверка соединений
        if not check_db_connection():
            raise Exception("Database connection failed")
        
        if not redis_client.ping():
            raise Exception("Redis connection failed")
        
        # Создание admin пользователя из Vault
        with engine.begin() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE username = :username"),
                                {"username": settings.admin_username})
            if result.scalar() == 0:
                logger.info("creating_admin_user")
                conn.execute(
                    text("""
                        INSERT INTO users (username, email, hashed_password, full_name, is_active, is_admin)
                        VALUES (:username, :email, :password, :full_name, true, true)
                    """),
                    {
                        "username": settings.admin_username,
                        "email": f"{settings.admin_username}@taskmanager.local",
                        "password": get_password_hash(settings.admin_password),
                        "full_name": "System Administrator"
                    }
                )
                logger.info("admin_user_created", username=settings.admin_username)
        
        logger.info("application_started")
        
    except Exception as e:
        logger.error("application_startup_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")
    redis_client.close()
    logger.info("application_stopped")


# FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics Middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware для сбора метрик"""
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    ACTIVE_REQUESTS.dec()
    
    return response


# ==================== HEALTH ENDPOINTS ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Базовая проверка здоровья"""
    return {"status": "healthy", "version": settings.api_version}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Проверка готовности (все зависимости доступны)"""
    checks = {
        "database": check_db_connection(),
        "redis": redis_client.ping(),
        "vault": vault_client.client.is_authenticated() if vault_client.client else False
    }
    
    if not all(checks.values()):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )
    
    return {"status": "ready", "checks": checks}


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus метрики"""
    DB_CONNECTIONS.set(engine.pool.checkedout())
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ==================== AUTHENTICATION ====================

@app.post("/api/auth/login", response_model=schemas.Token, tags=["Authentication"])
async def login(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    Credentials берутся из Vault
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Сохраняем сессию в Redis
    redis_client.set_session(
        access_token,
        {
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        }
    )
    
    logger.info("user_logged_in", user_id=user.id, username=user.username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }


@app.post("/api/auth/logout", tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_user)):
    """Выход из системы"""
    # Здесь можно добавить логику отзыва токена
    logger.info("user_logged_out", user_id=current_user.id)
    return {"message": "Successfully logged out"}


@app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


# ==================== USERS ====================

@app.post("/api/users", response_model=schemas.UserResponse, tags=["Users"])
async def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Создание нового пользователя (только для админов)"""
    # Проверка уникальности
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Создание пользователя
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_admin=user_data.is_admin
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("user_created", user_id=user.id, username=user.username)
    
    return user


@app.get("/api/users", response_model=list[schemas.UserResponse], tags=["Users"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Список пользователей"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ==================== TASKS ====================

@app.post("/api/tasks", response_model=schemas.TaskResponse, status_code=201, tags=["Tasks"])
async def create_task(
    task_data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание новой задачи"""
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status=task_data.status,
        due_date=task_data.due_date,
        owner_id=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Инвалидируем кэш
    redis_client.flush_pattern("tasks:list:*")
    
    logger.info("task_created", task_id=task.id, user_id=current_user.id)
    
    return task


@app.get("/api/tasks", response_model=list[schemas.TaskResponse], tags=["Tasks"])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Список задач с фильтрацией и кэшированием"""
    cache_key = f"{current_user.id}:{skip}:{limit}:{status}:{priority}"
    
    # Проверяем кэш
    cached = redis_client.get_cached_tasks_list(cache_key)
    if cached:
        logger.debug("cache_hit", key=cache_key)
        return cached
    
    # Запрос к БД
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    # Сериализация для кэша
    tasks_dict = [schemas.TaskResponse.model_validate(task).model_dump() for task in tasks]
    
    # Кэшируем на 5 минут
    redis_client.cache_tasks_list(cache_key, tasks_dict, expire=300)
    
    return tasks


@app.get("/api/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение задачи по ID"""
    # Проверяем кэш
    cached = redis_client.get_cached_task(task_id)
    if cached:
        return cached
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Кэшируем
    task_dict = schemas.TaskResponse.model_validate(task).model_dump()
    redis_client.cache_task(task_id, task_dict)
    
    return task


@app.put("/api/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление задачи"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Обновляем поля
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Инвалидируем кэш
    redis_client.invalidate_task_cache(task_id)
    
    logger.info("task_updated", task_id=task_id, user_id=current_user.id)
    
    return task


@app.delete("/api/tasks/{task_id}", status_code=204, tags=["Tasks"])
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление задачи"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    # Инвалидируем кэш
    redis_client.invalidate_task_cache(task_id)
    
    logger.info("task_deleted", task_id=task_id, user_id=current_user.id)


# ==================== STATISTICS ====================

@app.get("/api/stats", response_model=schemas.StatsResponse, tags=["Statistics"])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика по задачам пользователя"""
    from sqlalchemy import func
    
    total = db.query(func.count(Task.id)).filter(Task.owner_id == current_user.id).scalar()
    completed = db.query(func.count(Task.id)).filter(
        Task.owner_id == current_user.id,
        Task.completed == True
    ).scalar()
    
    by_status = db.query(Task.status, func.count(Task.id)).filter(
        Task.owner_id == current_user.id
    ).group_by(Task.status).all()
    
    by_priority = db.query(Task.priority, func.count(Task.id)).filter(
        Task.owner_id == current_user.id
    ).group_by(Task.priority).all()
    
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "active_tasks": total - completed,
        "by_status": {status: count for status, count in by_status},
        "by_priority": {priority: count for priority, count in by_priority}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
