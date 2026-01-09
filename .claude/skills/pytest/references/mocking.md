# Advanced Mocking in Pytest

## Table of Contents

1. [Patch Targets](#patch-targets)
2. [Mock Return Values](#mock-return-values)
3. [Mock Side Effects](#mock-side-effects)
4. [Assertions on Mocks](#assertions-on-mocks)
5. [Mocking Classes](#mocking-classes)
6. [Async Mocking](#async-mocking)
7. [pytest-mock Plugin](#pytest-mock-plugin)

## Patch Targets

```python
from unittest.mock import patch

# Rule: Patch where it's USED, not where it's DEFINED

# mymodule.py imports requests
# Patch in mymodule, not in requests
@patch("mymodule.requests.get")
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "value"}
    result = mymodule.fetch_data()
    assert result == {"data": "value"}

# Multiple patches (applied bottom-up)
@patch("mymodule.func_b")
@patch("mymodule.func_a")
def test_multiple(mock_a, mock_b):
    mock_a.return_value = 1
    mock_b.return_value = 2
    # ...

# Patch object attribute
@patch.object(MyClass, "method")
def test_method(mock_method):
    mock_method.return_value = "mocked"
    obj = MyClass()
    assert obj.method() == "mocked"

# Patch dictionary
@patch.dict("os.environ", {"API_KEY": "test-key"})
def test_with_env():
    assert os.environ["API_KEY"] == "test-key"
```

## Mock Return Values

```python
from unittest.mock import Mock, MagicMock

# Simple return value
mock = Mock(return_value=42)
assert mock() == 42

# Attribute access
mock = Mock()
mock.attribute.nested.value = 100
assert mock.attribute.nested.value == 100

# Method chaining
mock = Mock()
mock.method.return_value.process.return_value = "result"
assert mock.method().process() == "result"

# Different values on successive calls
mock = Mock(side_effect=[1, 2, 3])
assert mock() == 1
assert mock() == 2
assert mock() == 3

# PropertyMock for properties
with patch.object(MyClass, "property_name", new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "mocked_value"
```

## Mock Side Effects

```python
from unittest.mock import Mock

# Raise exception
mock = Mock(side_effect=ValueError("Invalid input"))

# Conditional side effect
def conditional_response(*args, **kwargs):
    if args[0] == "error":
        raise ValueError("Error case")
    return "success"

mock = Mock(side_effect=conditional_response)

# Side effect with different return values per call
mock = Mock(side_effect=[
    {"page": 1, "data": [1, 2]},
    {"page": 2, "data": [3, 4]},
    StopIteration,
])

# Side effect function
def track_calls(*args):
    print(f"Called with: {args}")
    return len(args)

mock = Mock(side_effect=track_calls)
```

## Assertions on Mocks

```python
from unittest.mock import Mock, call

mock = Mock()
mock("arg1", "arg2", key="value")

# Assert called
mock.assert_called()
mock.assert_called_once()
mock.assert_called_with("arg1", "arg2", key="value")
mock.assert_called_once_with("arg1", "arg2", key="value")

# Call count
assert mock.call_count == 1

# Multiple calls
mock("first")
mock("second")
mock.assert_any_call("first")
assert mock.call_args_list == [call("first"), call("second")]

# Assert not called
mock2 = Mock()
mock2.assert_not_called()

# Reset mock
mock.reset_mock()
mock.assert_not_called()
```

## Mocking Classes

```python
from unittest.mock import patch, MagicMock

# Mock entire class
@patch("mymodule.MyClass")
def test_class_mock(MockClass):
    instance = MockClass.return_value
    instance.method.return_value = "mocked"

    result = mymodule.use_class()
    MockClass.assert_called_once()

# Mock specific instance method
@patch.object(MyClass, "__init__", return_value=None)
@patch.object(MyClass, "method")
def test_instance_method(mock_method, mock_init):
    mock_method.return_value = "mocked"
    obj = MyClass()
    assert obj.method() == "mocked"

# Spec for type safety
mock = Mock(spec=RealClass)
mock.real_method()  # OK
mock.fake_method()  # AttributeError
```

## Async Mocking

```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_async_function():
    mock = AsyncMock(return_value={"data": "value"})
    result = await mock()
    assert result == {"data": "value"}

@pytest.mark.asyncio
@patch("mymodule.async_fetch", new_callable=AsyncMock)
async def test_patched_async(mock_fetch):
    mock_fetch.return_value = {"status": "ok"}
    result = await mymodule.get_data()
    assert result["status"] == "ok"

# Async context manager
@pytest.mark.asyncio
async def test_async_context():
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value="entered")
    mock.__aexit__ = AsyncMock(return_value=None)

    async with mock as value:
        assert value == "entered"

# Async iterator
@pytest.mark.asyncio
async def test_async_iter():
    mock = MagicMock()
    mock.__aiter__.return_value = iter([1, 2, 3])

    results = [item async for item in mock]
    assert results == [1, 2, 3]
```

## pytest-mock Plugin

```python
# Install: pip install pytest-mock

def test_with_mocker(mocker):
    # Patch with automatic cleanup
    mock_func = mocker.patch("mymodule.function")
    mock_func.return_value = "mocked"

    # spy - wrap real function
    spy = mocker.spy(mymodule, "real_function")
    mymodule.real_function(1, 2)
    spy.assert_called_once_with(1, 2)

    # stub - simple mock without spec
    stub = mocker.stub(name="my_stub")
    stub.return_value = 42

# Mocker fixture methods
def test_mocker_methods(mocker):
    mocker.patch("module.func")
    mocker.patch.object(obj, "method")
    mocker.patch.dict(dictionary)
    mocker.patch.multiple(target, attr1=1, attr2=2)
    mocker.stopall()  # Stop all patches
```
