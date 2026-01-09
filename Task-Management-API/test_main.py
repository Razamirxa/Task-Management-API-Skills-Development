"""
Tests for Task Management API

Uses in-memory SQLite database for testing to avoid
requiring Neon credentials during test runs.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session
from models import Task


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",  # In-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============== ROOT & HEALTH TESTS ==============


def test_root_endpoint(client):
    """Test that the root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ============== CREATE TASK TESTS ==============


def test_create_task(client):
    """Test creating a new task."""
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data


def test_create_task_minimal(client):
    """Test creating a task with only required fields."""
    response = client.post(
        "/tasks/",
        json={"title": "Minimal Task"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["description"] is None
    assert data["status"] == "todo"


def test_create_task_with_status(client):
    """Test creating a task with a specific status."""
    response = client.post(
        "/tasks/",
        json={"title": "In Progress Task", "status": "in_progress"}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"


def test_create_task_empty_title_fails(client):
    """Test that creating a task with empty title fails."""
    response = client.post(
        "/tasks/",
        json={"title": ""}
    )
    assert response.status_code == 422  # Validation error


# ============== READ TASK TESTS ==============


def test_read_tasks_empty(client):
    """Test reading tasks when database is empty."""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_tasks(client):
    """Test reading all tasks."""
    # Create some tasks
    client.post("/tasks/", json={"title": "Task 1"})
    client.post("/tasks/", json={"title": "Task 2"})

    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_tasks_pagination(client):
    """Test reading tasks with pagination."""
    # Create 5 tasks
    for i in range(5):
        client.post("/tasks/", json={"title": f"Task {i}"})

    # Get first 2
    response = client.get("/tasks/?limit=2")
    assert len(response.json()) == 2

    # Skip first 2, get next 2
    response = client.get("/tasks/?skip=2&limit=2")
    assert len(response.json()) == 2


def test_read_single_task(client):
    """Test reading a single task by ID."""
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "Single Task", "description": "Description"}
    )
    task_id = create_response.json()["id"]

    # Read it back
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Single Task"


def test_read_nonexistent_task(client):
    """Test reading a task that doesn't exist."""
    response = client.get("/tasks/999")
    assert response.status_code == 404


# ============== UPDATE TASK TESTS (PUT) ==============


def test_update_task_put(client):
    """Test full update of a task with PUT."""
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "Original Title"}
    )
    task_id = create_response.json()["id"]

    # Update it with PUT (all fields required)
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description",
            "status": "done"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["status"] == "done"
    assert data["updated_at"] is not None


def test_update_nonexistent_task_put(client):
    """Test PUT on a task that doesn't exist."""
    response = client.put(
        "/tasks/999",
        json={
            "title": "Title",
            "description": None,
            "status": "todo"
        }
    )
    assert response.status_code == 404


# ============== PATCH TASK TESTS ==============


def test_patch_task_title_only(client):
    """Test partial update with PATCH - only title."""
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "Original", "description": "Keep this"}
    )
    task_id = create_response.json()["id"]

    # Patch only the title
    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "New Title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Keep this"  # Unchanged


def test_patch_task_status_only(client):
    """Test partial update with PATCH - only status."""
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "My Task"}
    )
    task_id = create_response.json()["id"]

    # Patch only the status
    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["title"] == "My Task"  # Unchanged


def test_patch_nonexistent_task(client):
    """Test PATCH on a task that doesn't exist."""
    response = client.patch(
        "/tasks/999",
        json={"title": "New Title"}
    )
    assert response.status_code == 404


# ============== DELETE TASK TESTS ==============


def test_delete_task(client):
    """Test deleting a task."""
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={"title": "To Delete"}
    )
    task_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist."""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
