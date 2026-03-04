---
name: pytest
description: >
  Comprehensive pytest expertise for writing, configuring, debugging, and optimizing Python tests.
  Use when: (1) Writing new pytest tests, fixtures, or conftest.py files, (2) Configuring pytest
  (pyproject.toml, pytest.ini, CLI options, markers), (3) Debugging test failures, collection
  issues, or fixture errors, (4) Parametrizing tests or fixtures, (5) Setting up mocking/patching
  with pytest-mock or monkeypatch, (6) Parallel test execution with pytest-xdist,
  (7) Async testing with pytest-asyncio, (8) Browser testing with pytest-playwright,
  (9) Database testing with pytest-postgresql, (10) Selecting or recommending pytest plugins,
  (11) Migrating from unittest to pytest, (12) CI pipeline configuration for pytest.
---

# Pytest

## Fixture Patterns

### Scopes
`function` (default) > `class` > `module` > `package` > `session`

Higher scopes execute first. Teardown in reverse order. Dynamic scope via callable:
```python
@pytest.fixture(scope=lambda fixture_name, config: "session" if config.getoption("--reuse") else "function")
```

### Yield Fixtures (preferred teardown)
```python
@pytest.fixture
def db_conn():
    conn = create_connection()
    yield conn           # test runs here
    conn.close()         # teardown
```

### Factory Fixtures
```python
@pytest.fixture
def make_user(db):
    created = []
    def _make(name, role="user"):
        u = User(name=name, role=role)
        db.add(u)
        created.append(u)
        return u
    yield _make
    for u in created:
        db.delete(u)
```

### Autouse
```python
@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
```

### Parametrized Fixtures
```python
@pytest.fixture(params=["sqlite", "postgres"], ids=["sqlite", "pg"])
def db(request):
    return connect(request.param)
```

### Override Hierarchy
conftest.py fixtures override parent directory. Module-level overrides conftest.

### Request Introspection
```python
@pytest.fixture
def data(request):
    marker = request.node.get_closest_marker("data_file")
    if marker:
        return load(marker.args[0])
```

## Parametrization

### Basic
```python
@pytest.mark.parametrize("input,expected", [("3+5", 8), ("2+4", 6)])
def test_eval(input, expected):
    assert eval(input) == expected
```

### Cartesian Product (stacked decorators)
```python
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_foo(x, y): ...  # 4 tests
```

### With Marks and IDs
```python
@pytest.mark.parametrize("val,expected", [
    pytest.param("ok", True, id="happy-path"),
    pytest.param("", False, marks=pytest.mark.xfail, id="empty"),
])
```

### Indirect (route through fixture)
```python
@pytest.mark.parametrize("db", ["sqlite", "pg"], indirect=True)
def test_query(db): ...
```

### Dynamic via Hook
```python
def pytest_generate_tests(metafunc):
    if "db" in metafunc.fixturenames:
        metafunc.parametrize("db", get_db_configs(), indirect=True)
```

## Assertions

### Exception Testing
```python
with pytest.raises(ValueError, match=r"invalid.*input"):
    do_something()

# With custom validation (v8.4+)
with pytest.raises(APIError, check=lambda e: e.status == 404):
    api.get("/missing")
```

### Floating Point
```python
assert 0.1 + 0.2 == pytest.approx(0.3)
assert result == pytest.approx(expected, rel=1e-3)
```

### Warnings
```python
with pytest.warns(DeprecationWarning, match="old_func"):
    old_func()
```

### Custom Assertion Helpers
```python
def assert_valid_response(resp, status=200):
    __tracebackhide__ = True  # hide from traceback
    assert resp.status_code == status
    assert resp.json() is not None
```

## Skip & XFail

```python
@pytest.mark.skip(reason="not implemented")
@pytest.mark.skipif(sys.platform == "win32", reason="unix only")
@pytest.mark.xfail(reason="known bug", strict=True)  # strict: xpass = FAIL

pytest.importorskip("pandas", minversion="2.0")
pytest.skip("reason", allow_module_level=True)  # skip entire module
```

## Markers

Register to avoid warnings and enable `--strict-markers`:
```toml
[tool.pytest.ini_options]
markers = ["slow: slow tests", "integration: integration tests"]
```

Select: `pytest -m "not slow"`, `pytest -m "slow and integration"`

## Monkeypatch Quick Reference

```python
monkeypatch.setattr("module.func", mock_func)
monkeypatch.setattr(obj, "attr", value)
monkeypatch.setenv("KEY", "val")
monkeypatch.delenv("KEY", raising=False)
monkeypatch.setitem(dict_obj, "key", "val")
monkeypatch.syspath_prepend("/path")
monkeypatch.chdir("/tmp")
```

## Output & Debugging

```
pytest -v                    # verbose test names
pytest -vv                   # verbose + detailed diffs
pytest -x                    # stop on first failure
pytest --maxfail=3           # stop after 3 failures
pytest --pdb                 # debugger on failure
pytest --tb=short            # short tracebacks
pytest -r fEs                # summary: failed, Errors, skipped
pytest --durations=10        # 10 slowest tests
pytest -s                    # disable capture (see prints)
pytest --lf                  # rerun last failures
pytest --sw                  # stepwise mode
```

## Plugin Selection Guide

**Need parallel execution?** → See [plugin-xdist.md](references/plugin-xdist.md)
- `-n auto` for CPU parallelism, `--dist=loadscope` to keep module tests together

**Need mocking?**
- Simple patching → use built-in `monkeypatch` fixture
- Call tracking/spies/stubs → See [plugin-mock.md](references/plugin-mock.md) (pytest-mock)
- Record/replay → See [plugin-mock.md](references/plugin-mock.md) (pytest-automock)

**Need async testing?** → See [plugin-asyncio.md](references/plugin-asyncio.md)
- Config: `asyncio_mode = "auto"` for zero-decorator async tests

**Need browser testing?** → See [plugin-playwright.md](references/plugin-playwright.md)
- Sync: pytest-playwright, Async: pytest-playwright-asyncio

**Need database fixtures?** → See [plugin-postgresql.md](references/plugin-postgresql.md)
- Factory pattern with `load` for schema, `postgresql_noproc` for Docker/CI

**Need something else?** → See [plugin-catalog.md](references/plugin-catalog.md)
- 1,745+ official plugins organized by category

**Other deep plugins** → See [plugin-misc.md](references/plugin-misc.md)
- pytest-stub, pytest-tmp-files, pytest-venv, pytest-bigquery-mock, pytest-bg-process

## Configuration Quick Start

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-ra -q --strict-markers --import-mode=importlib"
testpaths = ["tests"]
markers = ["slow: slow tests", "integration: integration tests"]
filterwarnings = ["error", "ignore::DeprecationWarning"]
log_cli = true
log_cli_level = "INFO"
```

Config precedence: pytest.toml / .pytest.toml > pytest.ini / .pytest.ini > pyproject.toml > tox.ini > setup.cfg

For full config options → See [configuration.md](references/configuration.md)

## Reference Files

- **[api-reference.md](references/api-reference.md)** -- API signatures, markers, hooks, exit codes, collection tree
- **[configuration.md](references/configuration.md)** -- Config files, all INI options, all CLI flags, env vars
- **[fixtures-reference.md](references/fixtures-reference.md)** -- Built-in fixtures: capture, logging, monkeypatch, tmp_path, cache, pytester
- **[advanced-patterns.md](references/advanced-patterns.md)** -- Plugin dev, hook writing, custom collection, unittest compat, CI, import modes
- **[plugin-catalog.md](references/plugin-catalog.md)** -- 1,745+ plugins organized by category
- **[plugin-xdist.md](references/plugin-xdist.md)** -- Parallel execution, distribution modes, worker management
- **[plugin-mock.md](references/plugin-mock.md)** -- pytest-mock (mocker fixture, spy, stub) + pytest-automock
- **[plugin-asyncio.md](references/plugin-asyncio.md)** -- Async testing, modes, event loop scope
- **[plugin-playwright.md](references/plugin-playwright.md)** -- Browser testing (sync + async), fixtures, config
- **[plugin-postgresql.md](references/plugin-postgresql.md)** -- PostgreSQL fixtures, factories, Docker, SQLAlchemy
- **[plugin-misc.md](references/plugin-misc.md)** -- stub, tmp-files, venv, bigquery-mock, bg-process
