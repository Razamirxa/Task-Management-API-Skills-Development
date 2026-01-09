"""
Task Management Models using SQLModel

SQLModel combines SQLAlchemy and Pydantic, giving us:
- Database table definitions (table=True)
- Request/Response schemas (without table=True)
- Type validation
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# Base model with shared fields (NOT a table)
class TaskBase(SQLModel):
    """Base Task model with common fields"""
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")


# Database table model
class Task(TaskBase, table=True):
    """Task database table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# Request schema for creating tasks
class TaskCreate(TaskBase):
    """Schema for creating a new task (request body)"""
    pass


# Response schema for reading tasks
class TaskRead(TaskBase):
    """Schema for reading a task (response)"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Request schema for full update (PUT)
class TaskUpdate(SQLModel):
    """Schema for full task update (PUT) - all fields required"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus


# Request schema for partial update (PATCH)
class TaskPatch(SQLModel):
    """Schema for partial task update (PATCH) - all fields optional"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
