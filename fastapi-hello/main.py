"""
Task Management API

A complete CRUD API for managing tasks using:
- FastAPI for the web framework
- SQLModel for database ORM
- Neon PostgreSQL for the database
- Dependency Injection for database connections
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import List

from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskRead, TaskUpdate, TaskPatch

# Create FastAPI app
app = FastAPI(
    title="Task Management API",
    description="A complete CRUD API for managing tasks with FastAPI, SQLModel, and Neon",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup"""
    create_db_and_tables()


# ============== CRUD ENDPOINTS ==============


@app.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """
    Create a new task.

    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **status**: Task status - todo, in_progress, or done (default: todo)
    """
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=List[TaskRead])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Get all tasks with pagination.

    - **skip**: Number of tasks to skip (default: 0)
    - **limit**: Maximum number of tasks to return (default: 100)
    """
    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int, session: Session = Depends(get_session)):
    """
    Get a specific task by ID.

    - **task_id**: The ID of the task to retrieve
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """
    Full update of a task (PUT).

    All fields are required. Use PATCH for partial updates.

    - **task_id**: The ID of the task to update
    - **title**: New task title (required)
    - **description**: New task description (required, can be null)
    - **status**: New task status (required)
    """
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Update all fields
    db_task.title = task_update.title
    db_task.description = task_update.description
    db_task.status = task_update.status
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.patch("/tasks/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    task_patch: TaskPatch,
    session: Session = Depends(get_session)
):
    """
    Partial update of a task (PATCH).

    Only provided fields will be updated.

    - **task_id**: The ID of the task to update
    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **status**: New task status (optional)
    """
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    # Only update provided fields
    task_data = task_patch.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """
    Delete a task by ID.

    - **task_id**: The ID of the task to delete
    """
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

    session.delete(db_task)
    session.commit()


# ============== HEALTH CHECK ==============


@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "message": "Task Management API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
