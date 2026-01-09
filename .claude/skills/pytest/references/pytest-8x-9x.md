# Pytest 8.x/9.x New Features Reference

## Table of Contents

1. [Version Compatibility](#version-compatibility)
2. [Native Subtests](#native-subtests)
3. [Exception Groups](#exception-groups)
4. [TOML Configuration](#toml-configuration)
5. [New CLI Options](#new-cli-options)
6. [Capture Enhancements](#capture-enhancements)
7. [Marker Improvements](#marker-improvements)
8. [Strict Mode](#strict-mode)
9. [Breaking Changes](#breaking-changes)

## Version Compatibility

| pytest Version | Python Required | Release Date |
|---------------|-----------------|--------------|
| 9.0.x         | 3.10+           | Nov 2025     |
| 8.4.x         | 3.9+            | Jun 2025     |
| 8.3.x         | 3.8+            | Jul 2024     |
| 8.2.x         | 3.8+            | Apr 2024     |
| 8.0.x         | 3.8+            | Jan 2024     |

## Native Subtests

Pytest 9.0 introduces native subtest support, an alternative to parametrization when test values aren't known at collection time.

```python
import pytest

def test_dynamic_values(subtests):
    """Test with values determined at runtime"""
    data = fetch_from_api()  # Unknown at collection

    for item in data:
        with subtests.test(msg=f"Testing {item['id']}", item_id=item['id']):
            assert validate(item)
            assert item['status'] == 'active'

def test_all_files_valid(subtests, tmp_path):
    """Each file tested independently"""
    files = list(tmp_path.glob("*.json"))

    for file in files:
        with subtests.test(file=file.name):
            data = json.loads(file.read_text())
            assert "required_field" in data

def test_matrix_combinations(subtests):
    """Test combinations without parametrize"""
    browsers = ["chrome", "firefox", "safari"]
    resolutions = [(1920, 1080), (1366, 768), (375, 667)]

    for browser in browsers:
        for width, height in resolutions:
            with subtests.test(browser=browser, resolution=f"{width}x{height}"):
                result = render_page(browser, width, height)
                assert result.success
```

### Subtests vs Parametrize

| Feature | `@pytest.mark.parametrize` | `subtests` |
|---------|---------------------------|------------|
| Values known at | Collection time | Runtime |
| Failure behavior | Stops at first | Continues all |
| Use case | Static test data | Dynamic data |
| Fixture support | Full | Full |

## Exception Groups

Pytest 8.4 adds `pytest.RaisesGroup` for testing Python 3.11+ `ExceptionGroup`:

```python
import pytest

# Basic usage
def test_single_exception_in_group():
    with pytest.RaisesGroup(ValueError):
        raise ExceptionGroup("errors", [ValueError("bad value")])

# Multiple exception types
def test_multiple_exception_types():
    with pytest.RaisesGroup(ValueError, TypeError):
        raise ExceptionGroup("errors", [
            ValueError("value error"),
            TypeError("type error"),
        ])

# Nested exception groups
def test_nested_groups():
    with pytest.RaisesGroup(pytest.RaisesGroup(KeyError)):
        raise ExceptionGroup("outer", [
            ExceptionGroup("inner", [KeyError("missing")])
        ])

# Match specific message
def test_match_message():
    with pytest.RaisesGroup(ValueError, match=r"invalid.*format"):
        raise ExceptionGroup("errors", [ValueError("invalid date format")])

# Access caught exceptions
def test_inspect_exceptions():
    with pytest.RaisesGroup(ValueError) as exc_info:
        raise ExceptionGroup("errors", [
            ValueError("error 1"),
            ValueError("error 2"),
        ])

    exceptions = exc_info.value.exceptions
    assert len(exceptions) == 2
    assert all(isinstance(e, ValueError) for e in exceptions)

# Strict matching (exact exception types)
def test_strict_matching():
    with pytest.RaisesGroup(ValueError, strict=True):
        # Must contain ONLY ValueError, nothing else
        raise ExceptionGroup("errors", [ValueError("only this")])
```

## TOML Configuration

### pyproject.toml (9.0+)

```toml
[tool.pytest]
# Test discovery
testpaths = ["tests", "integration_tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*", "*Tests"]
python_functions = ["test_*", "check_*"]

# Markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "unit: marks unit tests",
]

# Default options
addopts = "-v --tb=short --strict-markers"

# Strict mode (enables all strictness checks)
strict = true

# Or individual strict settings
strict_markers = true
strict_config = true
strict_parametrization_ids = true
strict_xfail = true

# Output customization
console_output_style = "times"  # Show execution time per test
truncation_limit_lines = 15
truncation_limit_chars = 800

# Logging
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s %(levelname)s %(message)s"

# Async mode (for pytest-asyncio)
asyncio_mode = "auto"

# Filtering
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]

# Minimum version
minversion = "9.0"
```

### Dedicated pytest.toml (9.0+)

```toml
# pytest.toml or .pytest.toml (hidden)
[pytest]
testpaths = ["tests"]
addopts = "-v"
markers = ["slow", "fast"]
```

## New CLI Options

### pytest 8.2+

```bash
# Read arguments from file
pytest @args.txt
# args.txt contains test paths/options, one per line

# Example args.txt:
# tests/unit/
# tests/integration/
# -v
# --tb=short
# -m "not slow"
```

### pytest 8.3+

```bash
# Show traceback for xfail results (independent of -rx)
pytest --xfail-tb

# List skipped tests individually instead of grouping
pytest --no-fold-skipped

# Select by marker keyword arguments
pytest -m "device(name='sensor1')"
pytest -m "api(version=2)"
pytest -m "feature(enabled=True)"
```

### pytest 8.4+

```bash
# Force short summary regardless of verbosity
pytest --force-short-summary

# Show execution time per test
pytest --console-output-style=times
```

## Capture Enhancements

### Tee Capture (8.4+)

The `capteesys` fixture captures output while still displaying it:

```python
def test_debug_with_capture(capteesys):
    """Output is visible during test AND captured"""
    print("Debug: Starting operation")
    result = complex_operation()
    print(f"Debug: Result = {result}")

    captured = capteesys.readouterr()
    assert "Starting operation" in captured.out
    assert f"Result = {result}" in captured.out

def test_live_logging(capteesys):
    """Useful for debugging long-running tests"""
    for i in range(100):
        print(f"Processing item {i}")  # Visible in real-time
        process_item(i)

    captured = capteesys.readouterr()
    assert captured.out.count("Processing item") == 100
```

### Capture Fixture Comparison

| Fixture | Captures | Binary | Tee (pass-through) |
|---------|----------|--------|-------------------|
| `capsys` | stdout/stderr | No | No |
| `capfd` | stdout/stderr (fd) | No | No |
| `capsysbinary` | stdout/stderr | Yes | No |
| `capfdbinary` | stdout/stderr (fd) | Yes | No |
| `capteesys` | stdout/stderr | No | Yes (8.4+) |

## Marker Improvements

### Keyword Argument Selection (8.3+)

```python
import pytest

# Define markers with keyword arguments
@pytest.mark.device(name="sensor1", protocol="mqtt", timeout=30)
def test_sensor_reading():
    pass

@pytest.mark.device(name="actuator1", protocol="http", timeout=60)
def test_actuator_command():
    pass

@pytest.mark.api(version=2, auth=True)
def test_authenticated_v2_endpoint():
    pass

@pytest.mark.api(version=1, auth=False)
def test_public_v1_endpoint():
    pass

@pytest.mark.feature(name="dark_mode", enabled=True)
def test_dark_mode():
    pass

@pytest.mark.feature(name="dark_mode", enabled=False)
def test_without_dark_mode():
    pass
```

```bash
# Select by keyword arguments
pytest -m "device(name='sensor1')"
pytest -m "device(protocol='mqtt')"
pytest -m "device(timeout=30)"
pytest -m "api(version=2)"
pytest -m "api(auth=True)"
pytest -m "feature(enabled=True)"

# Combine with boolean operators
pytest -m "device(protocol='mqtt') and not device(timeout=60)"
pytest -m "api(version=2) or api(version=3)"
```

**Supported value types:** `int`, `str`, `bool`, `None`

## Strict Mode

### Combined Strict Setting (9.0+)

```toml
[tool.pytest]
# Enable ALL strictness checks at once
strict = true
```

This is equivalent to:

```toml
[tool.pytest]
strict_markers = true      # Unknown markers are errors
strict_config = true       # Unknown config options are errors
strict_parametrization_ids = true  # Duplicate param IDs are errors
strict_xfail = true        # xfail tests that pass are errors
```

### Individual Settings

```python
# pytest.ini style
[pytest]
strict_markers = true

# Programmatic
def pytest_configure(config):
    config.addinivalue_line("strict_markers", "true")
```

## Breaking Changes

### pytest 8.4+ Breaking Changes

```python
# 1. Async tests FAIL without plugin (was: warn + skip)
@pytest.mark.asyncio
async def test_async():  # FAILS unless pytest-asyncio installed
    await asyncio.sleep(0.1)

# 2. Tests returning non-None FAIL (was: warning)
def test_bad():
    return True  # FAILS - tests must not return values

# 3. Test functions with yield cause ERROR
def test_generator():
    yield  # ERROR - use fixtures for setup/teardown

# 4. Python 3.8 support REMOVED
```

### pytest 9.0+ Breaking Changes

```python
# 1. Python 3.9 support REMOVED (requires 3.10+)

# 2. Overlapping paths deduplicated
# pytest a/ a/b  ->  pytest a/

# 3. CI mode requires non-empty env vars
# CI="" no longer activates CI mode

# 4. config.args contains only strings
# No more pathlib.Path in config.args
```

### Migration Guide

```python
# From pytest 7.x to 8.x/9.x

# OLD: Async test without plugin (worked with warning)
async def test_old():
    await something()

# NEW: Must install and configure pytest-asyncio
import pytest
@pytest.mark.asyncio
async def test_new():
    await something()

# OLD: Test returning value (worked with warning)
def test_old():
    result = compute()
    return result == expected

# NEW: Use assertions
def test_new():
    result = compute()
    assert result == expected

# OLD: Generator test (was marked xfail)
def test_old():
    setup()
    yield
    teardown()

# NEW: Use fixtures
@pytest.fixture
def resource():
    setup()
    yield
    teardown()

def test_new(resource):
    pass
```
