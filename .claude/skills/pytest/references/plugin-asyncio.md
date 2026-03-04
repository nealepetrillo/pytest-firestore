# pytest-asyncio: Async Test Support

Requires: Python>=3.10, pytest>=8.2.0

## Installation
```bash
pip install pytest-asyncio
```

## Modes

### strict (default since 0.19.0)
Must explicitly mark async tests and use `@pytest_asyncio.fixture` for async fixtures.
```python
import pytest

@pytest.mark.asyncio
async def test_something():
    result = await some_async_fn()
    assert result == expected
```

### auto
All async test functions automatically treated as asyncio tests. Both `@pytest.fixture` and `@pytest_asyncio.fixture` handled.
```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```
```python
# No decorator needed
async def test_something():
    result = await some_async_fn()
    assert result == expected
```

**auto mode is incompatible** with projects using multiple async libraries (e.g., trio).

## Event Loop Scope

Controls event loop lifetime. Default: function (max isolation).

```python
@pytest.mark.asyncio(loop_scope="module")  # shared across module
async def test_a(): ...

@pytest.mark.asyncio(loop_scope="session")  # shared across session
async def test_b(): ...
```

Available scopes: `function`, `class`, `module`, `package`, `session`

**Note:** The `scope` keyword argument to `@pytest.mark.asyncio` is deprecated. Use `loop_scope` instead (since 0.24.0).

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `asyncio_mode` | `strict` | `strict` or `auto` |
| `asyncio_default_test_loop_scope` | `function` | Default loop scope for tests |
| `asyncio_default_fixture_loop_scope` | fixture scope | Default loop scope for fixtures |
| `asyncio_debug` | `false` | Enable asyncio debug mode |

CLI overrides: `--asyncio-mode`, `--asyncio-debug`

## Async Fixtures

### strict mode
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def db_connection():
    conn = await create_connection()
    yield conn
    await conn.close()

@pytest.mark.asyncio
async def test_query(db_connection):
    result = await db_connection.execute("SELECT 1")
    assert result == 1
```

### auto mode
```python
@pytest.fixture  # works in auto mode
async def db_connection():
    conn = await create_connection()
    yield conn
    await conn.close()
```

**Important**: In strict mode, use `@pytest_asyncio.fixture` (not `@pytest.fixture`) for async fixtures. A warning is emitted if `@pytest.fixture` is used on async fixtures in strict mode.

## Event Loop Policy

Use the `event_loop_policy` fixture to test with non-default event loops (since 0.23.0):
```python
@pytest.fixture
def event_loop_policy():
    return uvloop.EventLoopPolicy()
```

## Patterns

### Parametrized async tests
```python
@pytest.mark.asyncio
@pytest.mark.parametrize("value", [1, 2, 3])
async def test_double(value):
    result = await async_double(value)
    assert result == value * 2
```

Each parametrized test case still runs **sequentially**, not concurrently.

### Class-based
```python
@pytest.mark.asyncio
class TestAsyncOps:
    async def test_op1(self):
        assert await async_op() == "result"
```

### Session-scoped async fixture
```python
@pytest_asyncio.fixture(scope="session")
async def app():
    app = await create_app()
    yield app
    await app.shutdown()
```

### Detect async tests programmatically
```python
from pytest_asyncio import is_async_test

def pytest_collection_modifyitems(items):
    for item in items:
        if is_async_test(item):
            pass  # do something with async test items
```

## Important Notes

- Tests run **sequentially** (no concurrent async test execution)
- `unittest.TestCase` subclasses **not supported** -- use `unittest.IsolatedAsyncioTestCase`
- The `event_loop` fixture has been **removed** (v1.0.0) -- use `loop_scope` and `event_loop_policy` instead
- Tasks are **cancelled** when their loop_scope ends (v1.1.0+)
- **ContextVars** propagate from async fixtures to tests (v1.1.0+ for all Python, v0.25.0 for Python>=3.11)
- Neighboring tests should use **identical loop scopes** for clarity
