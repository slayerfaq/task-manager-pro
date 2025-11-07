"""
Pydantic Schemas для валидации и сериализации
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict
from datetime import datetime
from ..models.models import PriorityEnum, StatusEnum


# ==================== AUTH SCHEMAS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    auth_type: Optional[str] = "local"  # "local" или "keycloak"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== TASK SCHEMAS ====================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    status: StatusEnum = StatusEnum.TODO
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: int
    completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== STATISTICS SCHEMAS ====================

class StatsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    active_tasks: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
