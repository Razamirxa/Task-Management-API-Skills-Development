---
name: pytest
description: Comprehensive Python testing skill using pytest framework. Use when writing, running, or debugging Python tests, creating fixtures, parametrizing tests, mocking dependencies, measuring coverage, or any pytest-related task. Triggers include requests like "write tests for this function", "add unit tests", "create test fixtures", "mock this dependency", "run pytest", or "check test coverage".
---

# Pytest Testing Skill

> **Note**: Updated for pytest 8.x/9.x (latest: 9.0.2). Requires Python 3.10+.

## Quick Start

### Basic Test Structure

```python
# test_example.py
import pytest

def test_function_returns_expected():
    result = my_function(2, 3)
    assert result == 5

def test_raises_exception():
    with pytest.raises(ValueError):
        my_function(-1, 0)

class TestMyClass:
    def test_method_one(self):
        obj = MyClass()
        assert obj.method() == "expected"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest test_example.py

# Run specific test
pytest test_example.py::test_function_returns_expected

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "test_login"

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# NEW in 8.x/9.x:
# Read test paths from file
pytest @tests.txt

# Show traceback for xfail results
pytest --xfail-tb

# List skipped tests individually (don't group by reason)
pytest --no-fold-skipped

# Force short summary regardless of verbosity
pytest --force-short-summary

# Show execution time per test
pytest --console-output-style=times
```

## Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    return {"name": "John", "email": "john@example.com"}

@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn  # Use yield for cleanup
    conn.close()

def test_user_name(sample_user):
    assert sample_user["name"] == "John"

# Fixture scopes: function (default), class, module, session
@pytest.fixture(scope="module")
def expensive_resource():
    return load_large_dataset()
```

## Parametrization

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected
```

## Mocking

```python
from unittest.mock import Mock, patch, MagicMock

# Patch a function
@patch("mymodule.external_api_call")
def test_with_mock(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = my_function()
    assert result == "ok"
    mock_api.assert_called_once()

# Patch as context manager
def test_with_context_mock():
    with patch("mymodule.get_data") as mock_get:
        mock_get.return_value = [1, 2, 3]
        assert process_data() == 6

# Mock object methods
def test_mock_object():
    mock_obj = Mock()
    mock_obj.method.return_value = 42
    assert mock_obj.method() == 42

# Mock async functions
@pytest.mark.asyncio
async def test_async_mock():
    with patch("mymodule.async_fetch") as mock_fetch:
        mock_fetch.return_value = AsyncMock(return_value={"data": "value"})
        result = await my_async_function()
        assert result["data"] == "value"
```

## Markers

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    # Run with: pytest -m slow
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_specific():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_known_failure():
    assert False

# NEW in 8.3+: Select tests by marker keyword arguments
@pytest.mark.device(name="device1", timeout=10)
def test_device():
    pass
# Run with: pytest -m "device(name='device1')"
# Supports: int, str, bool, None values
```

## Subtests (9.0+)

Native subtest support for when values aren't known at collection time:

```python
import pytest

def test_with_subtests(subtests):
    """Each subtest failure is reported individually"""
    for i in range(5):
        with subtests.test(msg=f"item {i}", i=i):
            assert i % 2 == 0  # Fails for odd numbers

def test_dynamic_data(subtests):
    """Useful when test data comes from external source"""
    data = fetch_test_data()  # Unknown at collection
    for item in data:
        with subtests.test(id=item["id"]):
            assert validate(item)
```

## Exception Groups (8.4+)

Test `ExceptionGroup` with `pytest.RaisesGroup`:

```python
import pytest

def test_exception_group():
    with pytest.RaisesGroup(ValueError):
        raise ExceptionGroup("errors", [ValueError("error1")])

def test_multiple_exceptions():
    with pytest.RaisesGroup(ValueError, TypeError):
        raise ExceptionGroup("errors", [
            ValueError("val error"),
            TypeError("type error")
        ])

def test_nested_groups():
    with pytest.RaisesGroup(pytest.RaisesGroup(ValueError)):
        raise ExceptionGroup("outer", [
            ExceptionGroup("inner", [ValueError("nested")])
        ])

def test_exception_matching():
    with pytest.RaisesGroup(ValueError, match="specific") as exc_info:
        raise ExceptionGroup("errors", [ValueError("specific error")])
    assert len(exc_info.value.exceptions) == 1
```

## Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == "expected"

@pytest.fixture
async def async_client():
    async with AsyncClient() as client:
        yield client
```

## conftest.py

Place shared fixtures in `conftest.py`:

```python
# conftest.py
import pytest

@pytest.fixture
def app():
    return create_app(testing=True)

@pytest.fixture
def client(app):
    return app.test_client()
```

## Configuration

### Native TOML Configuration (9.0+)

```toml
# pyproject.toml - NEW native TOML syntax
[tool.pytest]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]

# Strict mode - enables all strictness checks at once
strict = true
# Or individually:
strict_markers = true
strict_config = true

# Output customization
console_output_style = "times"  # Show execution time
truncation_limit_lines = 10
truncation_limit_chars = 500
```

```toml
# pytest.toml or .pytest.toml - dedicated config file (9.0+)
[pytest]
testpaths = ["tests"]
addopts = "-v"
```

### Legacy INI Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --cov=src --cov-report=term-missing
```

### Coverage Configuration

```ini
[coverage:run]
source = src
omit = */tests/*
```

## Capture Fixtures

```python
# Standard capture fixtures
def test_capture_stdout(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

def test_capture_binary(capfdbinary):
    import sys
    sys.stdout.buffer.write(b"\x00\x01")
    captured = capfdbinary.readouterr()
    assert captured.out == b"\x00\x01"

# NEW in 8.4+: Tee capture - capture AND pass through
def test_tee_capture(capteesys):
    """Captures output while still displaying it"""
    print("visible and captured")
    captured = capteesys.readouterr()
    assert "visible" in captured.out
```

## Breaking Changes (8.x/9.x)

Be aware of these breaking changes when upgrading:

```python
# ❌ FAILS in 8.4+: Async tests without plugin
@pytest.mark.asyncio
async def test_async():  # Now fails instead of warn+skip
    await some_async_func()
# ✅ FIX: Install pytest-asyncio

# ❌ FAILS in 8.4+: Tests returning values
def test_returns_value():
    return True  # Now fails instead of warning
# ✅ FIX: Use assertions, don't return values

# ❌ FAILS in 8.4+: Test functions with yield
def test_with_yield():
    yield  # Now explicit error
# ✅ FIX: Use fixtures for setup/teardown

# ❌ REMOVED: Python 3.8/3.9 support
# pytest 8.4+ requires Python 3.9+
# pytest 9.0+ requires Python 3.10+
```

## Best Practices

1. **One assertion per test** - Keep tests focused
2. **Descriptive names** - `test_user_login_with_invalid_password_returns_401`
3. **Arrange-Act-Assert** - Structure tests clearly
4. **Isolate tests** - No dependencies between tests
5. **Use fixtures** - Avoid repetitive setup code
6. **Mock external dependencies** - APIs, databases, file systems
7. **Use subtests** - For dynamic test data unknown at collection time (9.0+)
8. **Use strict mode** - Enable `strict = true` in config (9.0+)

## References

- **Fixtures**: See [references/fixtures.md](references/fixtures.md) for advanced fixture patterns
- **Mocking**: See [references/mocking.md](references/mocking.md) for complex mocking scenarios
- **Patterns**: See [references/patterns.md](references/patterns.md) for testing patterns by domain
- **New Features**: See [references/pytest-8x-9x.md](references/pytest-8x-9x.md) for detailed 8.x/9.x features
