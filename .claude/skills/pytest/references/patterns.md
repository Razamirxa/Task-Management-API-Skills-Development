# Testing Patterns by Domain

## Table of Contents

1. [API Testing](#api-testing)
2. [Database Testing](#database-testing)
3. [File System Testing](#file-system-testing)
4. [CLI Testing](#cli-testing)
5. [Exception Testing](#exception-testing)
6. [Time-dependent Testing](#time-dependent-testing)

## API Testing

### FastAPI Testing

```python
import pytest
from fastapi.testclient import TestClient
from myapp import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_endpoint(client):
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_post_with_auth(client):
    response = client.post(
        "/items",
        json={"name": "test"},
        headers={"Authorization": "Bearer token123"}
    )
    assert response.status_code == 201

@pytest.fixture
async def async_client():
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/async-items")
    assert response.status_code == 200
```

### Flask Testing

```python
import pytest
from myapp import create_app

@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_login(client):
    response = client.post("/login", data={
        "username": "test",
        "password": "secret"
    })
    assert response.status_code == 302
```

### External API Mocking

```python
import responses
import requests

@responses.activate
def test_external_api():
    responses.add(
        responses.GET,
        "https://api.example.com/data",
        json={"result": "success"},
        status=200
    )

    result = requests.get("https://api.example.com/data")
    assert result.json() == {"result": "success"}

# With pytest-httpx for async
@pytest.mark.asyncio
async def test_async_api(httpx_mock):
    httpx_mock.add_response(json={"data": "value"})
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        assert response.json() == {"data": "value"}
```

## Database Testing

### SQLAlchemy Testing

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.models import Base

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_create_user(db_session):
    user = User(name="test")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### Transaction Rollback Pattern

```python
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

## File System Testing

### Using tmp_path

```python
def test_file_creation(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    assert file.read_text() == "hello"

def test_directory_structure(tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file = subdir / "data.json"
    file.write_text('{"key": "value"}')
    assert file.exists()

@pytest.fixture
def project_dir(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").touch()
    (src / "main.py").write_text("def main(): pass")
    return tmp_path
```

### Mocking File Operations

```python
from unittest.mock import mock_open, patch

def test_read_file():
    with patch("builtins.open", mock_open(read_data="file content")):
        with open("any_file.txt") as f:
            assert f.read() == "file content"

def test_write_file():
    m = mock_open()
    with patch("builtins.open", m):
        with open("output.txt", "w") as f:
            f.write("test data")
    m().write.assert_called_once_with("test data")
```

## CLI Testing

### Using click.testing

```python
from click.testing import CliRunner
from myapp.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_command(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

def test_cli_with_input(runner):
    result = runner.invoke(cli, ["create"], input="project_name\n")
    assert result.exit_code == 0

def test_cli_with_isolation(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])
        assert Path("config.yaml").exists()
```

### Using subprocess

```python
import subprocess

def test_script_execution():
    result = subprocess.run(
        ["python", "script.py", "--arg", "value"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "expected output" in result.stdout
```

## Exception Testing

```python
import pytest

def test_raises_exception():
    with pytest.raises(ValueError):
        raise ValueError("error")

def test_exception_message():
    with pytest.raises(ValueError, match="invalid.*input"):
        raise ValueError("invalid user input")

def test_exception_attributes():
    with pytest.raises(CustomError) as exc_info:
        raise CustomError(code=404, message="Not found")
    assert exc_info.value.code == 404
    assert exc_info.value.message == "Not found"

def test_does_not_raise():
    # Verify no exception is raised
    try:
        safe_function()
    except Exception:
        pytest.fail("Unexpected exception raised")
```

## Time-dependent Testing

### Using freezegun

```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2024-01-15 12:00:00")
def test_frozen_time():
    assert datetime.now().year == 2024
    assert datetime.now().month == 1

@freeze_time("2024-01-01")
def test_with_frozen_date():
    result = get_current_quarter()
    assert result == "Q1"

# As fixture
@pytest.fixture
def frozen_time():
    with freeze_time("2024-06-15"):
        yield

def test_with_fixture(frozen_time):
    assert datetime.now().month == 6
```

### Mocking time

```python
from unittest.mock import patch
import time

@patch("time.time", return_value=1700000000)
def test_timestamp(mock_time):
    assert time.time() == 1700000000

@patch("time.sleep")
def test_no_actual_sleep(mock_sleep):
    time.sleep(100)  # Returns immediately
    mock_sleep.assert_called_once_with(100)
```
