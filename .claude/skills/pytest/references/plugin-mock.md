# pytest-mock

Requires: pytest>=6.2.5, Python>=3.9

Thin wrapper around `unittest.mock` with automatic cleanup at test end.

## Installation
```bash
pip install pytest-mock
```

## The `mocker` Fixture

### Patching Methods
```python
def test_example(mocker):
    # Basic patch (replaces with MagicMock)
    mock_fn = mocker.patch("mymodule.some_function")
    mock_fn.return_value = 42

    # Patch object attribute
    mocker.patch.object(MyClass, "method", return_value="mocked")

    # Patch multiple
    mocker.patch.multiple("mymodule", func1=mocker.DEFAULT, func2=mocker.DEFAULT)

    # Patch dictionary
    mocker.patch.dict("os.environ", {"KEY": "value"})

    # Stop all / reset all
    mocker.stopall()
    mocker.resetall()  # calls reset_mock() on all mocked objects + create_autospec mocks
```

### Spy (call-through, real code executes)
```python
def test_spy(mocker):
    spy = mocker.spy(mymodule, "real_function")
    result = mymodule.real_function(21)

    spy.assert_called_once_with(21)
    assert result == 42  # real return value

    # Spy attributes
    spy.spy_return          # last return value
    spy.spy_return_list     # all return values (3.13+)
    spy.spy_exception       # last exception or None

    # Iterator spy (3.15+) -- pass duplicate_iterators=True to mocker.spy
    spy = mocker.spy(mymodule, "iter_function", duplicate_iterators=True)
    spy.spy_return_iter     # duplicate of last returned iterator
```
Works with methods, classmethods, staticmethods, and async functions.

### Selective Spy Stopping (3.10+)
```python
def test_stop_spy(mocker):
    spy = mocker.spy(Foo, "bar")
    foo = Foo()
    assert foo.bar() == 42
    assert spy.call_count == 1
    mocker.stop(spy)           # stop this specific spy
    assert foo.bar() == 42
    assert spy.call_count == 1  # no longer tracked
```

### Stub (standalone mock)
```python
def test_stub(mocker):
    callback = mocker.stub(name="on_complete")
    do_something(on_complete=callback)
    callback.assert_called_once_with("result")

    # Async stub
    async_cb = mocker.async_stub(name="async_callback")
```

### Scope-Specific Fixtures
- `mocker` -- function scope (default)
- `class_mocker` -- class scope
- `module_mocker` -- module scope
- `package_mocker` -- package scope
- `session_mocker` -- session scope

### Mock Utilities (via mocker)
`mocker.Mock`, `mocker.MagicMock`, `mocker.NonCallableMagicMock`, `mocker.PropertyMock`,
`mocker.AsyncMock`, `mocker.ANY`, `mocker.DEFAULT`, `mocker.call`, `mocker.sentinel`,
`mocker.mock_open`, `mocker.seal`, `mocker.create_autospec`

### Type Annotations
```python
from pytest_mock import MockerFixture, MockType, AsyncMockType

def test_typed(mocker: MockerFixture) -> None:
    mock: MockType = mocker.patch("mymodule.func")
```

### Key Differences: patch vs spy vs stub

| | patch | spy | stub |
|---|---|---|---|
| Replaces original | Yes | No | N/A (standalone) |
| Real code runs | No | Yes | No |
| Tracks calls | Yes | Yes | Yes |
| Best for | Isolating deps | Verifying calls | Callbacks |

## Configuration

| INI Option | Default | Description |
|------------|---------|-------------|
| `mock_use_standalone_module` | `false` | Use PyPI `mock` instead of `unittest.mock` |
| `mock_traceback_monkeypatch` | `true` | Enhanced assertion failure reporting for mock calls |

`mock_traceback_monkeypatch` auto-disables with `--tb=native`.

## Important Notes
- **No context manager usage**: `with mocker.patch(...)` produces a warning. Use `mocker.patch.context_manager` for legitimate CM mocking.
- **Patch location matters**: Patch where the name is *looked up*, not where it's *defined*. If `mymodule` does `from os import remove`, patch `mymodule.remove`, not `os.remove`.
- **Auto-cleanup**: All patches undone after test -- no manual cleanup needed.

---

## pytest-automock (Record/Replay)

Separate plugin for recording real calls and replaying them as mocks.

```bash
pip install pytest-automock
```

### Phase 1: Generate mocks (unlocked)
```bash
pytest --automock-unlocked
```
Records real calls to `tests/mocks/` directory.

### Phase 2: Run with mocks (locked, default)
```bash
pytest
```
Replays recorded mocks without calling real code.

### Usage
```python
# conftest.py
@pytest.fixture(autouse=True)
def _mocks(automock):
    with automock((mymod, "Network")):
        yield
    # Or string notation:
    with automock("mymod.Network"):
        yield
```

### automock Parameters
- `*targets` -- object pairs `(module, "Name")` or dot-notation strings
- `storage` -- mock storage path (default: `"tests/mocks"`)
- `override_name` -- custom mock filename
- `unlocked` -- override CLI mode
- `remove` -- delete test mock before running
- `encode`/`decode` -- custom serialization (default: pickle + gzip)

### Caveats
- **Order-dependent**: call sequences must match exactly between recording and replay
- **Non-deterministic content fails**: time-dependent args, changing serialization
- **No support for**: dunder methods, generators, context managers
- CLI: `--automock-unlocked`, `--automock-remove`
