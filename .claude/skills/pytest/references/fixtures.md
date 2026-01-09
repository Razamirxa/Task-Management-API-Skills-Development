# Advanced Pytest Fixtures

## Table of Contents

1. [Fixture Scopes](#fixture-scopes)
2. [Fixture Factories](#fixture-factories)
3. [Parameterized Fixtures](#parameterized-fixtures)
4. [Fixture Dependencies](#fixture-dependencies)
5. [Dynamic Fixtures](#dynamic-fixtures)
6. [Autouse Fixtures](#autouse-fixtures)
7. [Fixture Finalization](#fixture-finalization)
8. [Capture Fixtures](#capture-fixtures)

## Fixture Scopes

```python
import pytest

# Function scope (default) - created for each test
@pytest.fixture(scope="function")
def per_test_data():
    return {"count": 0}

# Class scope - shared across tests in a class
@pytest.fixture(scope="class")
def class_resource():
    resource = ExpensiveResource()
    yield resource
    resource.cleanup()

# Module scope - shared across all tests in a module
@pytest.fixture(scope="module")
def db_connection():
    conn = database.connect()
    yield conn
    conn.disconnect()

# Session scope - shared across entire test session
@pytest.fixture(scope="session")
def app_config():
    return load_config()
```

## Fixture Factories

```python
@pytest.fixture
def make_user():
    created_users = []

    def _make_user(name, email=None):
        user = User(name=name, email=email or f"{name}@test.com")
        created_users.append(user)
        return user

    yield _make_user

    # Cleanup all created users
    for user in created_users:
        user.delete()

def test_multiple_users(make_user):
    admin = make_user("admin", "admin@test.com")
    guest = make_user("guest")
    assert admin.name == "admin"
    assert guest.email == "guest@test.com"
```

## Parameterized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    db = create_database(request.param)
    yield db
    db.drop()

def test_query(database):
    # Runs 3 times, once for each database type
    result = database.execute("SELECT 1")
    assert result == 1

# With IDs for better test names
@pytest.fixture(params=[
    pytest.param({"debug": True}, id="debug-mode"),
    pytest.param({"debug": False}, id="production-mode"),
])
def app_config(request):
    return request.param
```

## Fixture Dependencies

```python
@pytest.fixture
def base_config():
    return {"host": "localhost", "port": 5000}

@pytest.fixture
def database_config(base_config):
    return {**base_config, "db_name": "test_db"}

@pytest.fixture
def app(database_config):
    return create_app(database_config)

def test_app_runs(app):
    assert app.is_running()
```

## Dynamic Fixtures

```python
# Using request.getfixturevalue
@pytest.fixture
def dynamic_resource(request):
    resource_type = request.param
    resource = request.getfixturevalue(f"{resource_type}_fixture")
    return resource

# Conditional fixture behavior
@pytest.fixture
def conditional_setup(request):
    if hasattr(request, "param"):
        return setup_with_param(request.param)
    return default_setup()

# Accessing test context
@pytest.fixture
def test_aware_fixture(request):
    test_name = request.node.name
    test_module = request.module.__name__
    return {"test": test_name, "module": test_module}
```

## Autouse Fixtures

```python
# Automatically used by all tests in module
@pytest.fixture(autouse=True)
def reset_state():
    global_state.reset()
    yield
    global_state.cleanup()

# Autouse with scope
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
```

## Fixture Finalization

```python
# Using yield (preferred)
@pytest.fixture
def resource_with_cleanup():
    resource = acquire_resource()
    yield resource
    resource.release()

# Using request.addfinalizer
@pytest.fixture
def resource_with_finalizer(request):
    resource = acquire_resource()
    request.addfinalizer(resource.release)
    return resource

# Multiple finalizers
@pytest.fixture
def complex_resource(request):
    r1 = create_resource_1()
    request.addfinalizer(r1.cleanup)

    r2 = create_resource_2()
    request.addfinalizer(r2.cleanup)

    return r1, r2
```

## Capture Fixtures

Built-in fixtures for capturing stdout/stderr output:

```python
# capsys - capture sys.stdout/stderr
def test_output(capsys):
    print("hello world")
    captured = capsys.readouterr()
    assert captured.out == "hello world\n"
    assert captured.err == ""

# capfd - capture at file descriptor level
def test_fd_output(capfd):
    import os
    os.write(1, b"fd output")
    captured = capfd.readouterr()
    assert "fd output" in captured.out

# capsysbinary - binary capture
def test_binary_output(capsysbinary):
    import sys
    sys.stdout.buffer.write(b"\x00\x01\x02")
    captured = capsysbinary.readouterr()
    assert captured.out == b"\x00\x01\x02"

# capfdbinary - binary fd-level capture
def test_binary_fd(capfdbinary):
    import os
    os.write(1, b"\xff\xfe")
    captured = capfdbinary.readouterr()
    assert captured.out == b"\xff\xfe"
```

### Tee Capture (pytest 8.4+)

The `capteesys` fixture captures output while still displaying it to the terminal:

```python
def test_tee_capture(capteesys):
    """Output is visible AND captured"""
    print("Debug: Starting test")  # Shows in terminal
    result = complex_operation()
    print(f"Debug: Result = {result}")  # Shows in terminal

    captured = capteesys.readouterr()
    assert "Starting test" in captured.out
    assert f"Result = {result}" in captured.out

def test_long_running_debug(capteesys):
    """Great for debugging long operations"""
    for i in range(10):
        print(f"Step {i}/10")  # Visible in real-time
        do_step(i)

    captured = capteesys.readouterr()
    assert captured.out.count("Step") == 10
```

### Capture Fixture Comparison

| Fixture | Level | Binary | Tee | Available Since |
|---------|-------|--------|-----|-----------------|
| `capsys` | sys.stdout/stderr | No | No | Always |
| `capfd` | File descriptor | No | No | Always |
| `capsysbinary` | sys.stdout/stderr | Yes | No | pytest 3.0 |
| `capfdbinary` | File descriptor | Yes | No | pytest 3.0 |
| `capteesys` | sys.stdout/stderr | No | Yes | pytest 8.4 |

### Disabling Capture

```python
def test_disable_capture(capsys):
    print("captured")
    with capsys.disabled():
        print("NOT captured - visible in terminal")
    print("captured again")

    captured = capsys.readouterr()
    assert "captured\ncaptured again\n" == captured.out
```
