# Pytest Built-in Fixtures Reference

## Table of Contents
- [Output Capture](#output-capture)
- [Logging](#logging)
- [Monkeypatch](#monkeypatch)
- [Temporary Files](#temporary-files)
- [Cache](#cache)
- [Warnings](#warnings)
- [Configuration Access](#configuration-access)
- [Test Metadata](#test-metadata)
- [Plugin Testing](#plugin-testing)
- [Subtests](#subtests)

## Output Capture

### capsys / capsysbinary
Capture `sys.stdout`/`sys.stderr` as text (capsys) or bytes (capsysbinary).
```python
def test_output(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == ""

    with capsys.disabled():
        print("this goes to real stdout")
```

### capfd / capfdbinary
Capture at file descriptor level (fd 1/2). Catches subprocess output too.
Same API: `readouterr()` and `disabled()`.

### capteesys
Capture sys.stdout/stderr while simultaneously passing through to real streams.

**Capture modes** (CLI `--capture=`):
- `fd` (default): file descriptor level
- `sys`: sys.stdout/stderr only
- `tee-sys`: capture + passthrough
- `no` (`-s`): disable all capture

## Logging

### caplog
```python
def test_logging(caplog):
    import logging
    with caplog.at_level(logging.INFO):
        logging.info("hello %s", "world")

    assert "hello world" in caplog.text
    assert caplog.records[0].levelname == "INFO"
    assert caplog.record_tuples == [("root", logging.INFO, "hello world")]
```

**Properties:**
- `.text` -- formatted output string
- `.records` -- list of `logging.LogRecord`
- `.record_tuples` -- list of `(logger_name, level, message)`
- `.messages` -- list of formatted messages
- `.handler` -- the LogCaptureHandler

**Methods:**
- `set_level(level, logger=None)` -- set capture threshold
- `at_level(level, logger=None)` -- context manager for temporary level
- `get_records(when)` -- records from `"setup"`/`"call"`/`"teardown"`
- `filtering(filter)` -- context manager to add temporary filter (v7.5+)
- `clear()` -- reset captured records

## Monkeypatch

```python
def test_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.delenv("HOME", raising=False)

def test_attr(monkeypatch):
    monkeypatch.setattr("os.path.sep", "/")
    monkeypatch.setattr(MyClass, "method", lambda self: 42)

def test_dict(monkeypatch):
    monkeypatch.setitem(config, "debug", True)
    monkeypatch.delitem(config, "secret", raising=False)

def test_path(monkeypatch):
    monkeypatch.syspath_prepend("/custom/path")
    monkeypatch.chdir("/tmp")
```

**All methods:**
- `setattr(target, name, value, raising=True)` -- also accepts dotted string path
- `delattr(target, name, raising=True)`
- `setitem(mapping, key, value)` / `delitem(mapping, key, raising=True)`
- `setenv(name, value, prepend=None)` -- `prepend` joins with separator char
- `delenv(name, raising=True)`
- `syspath_prepend(path)` -- prepends + refreshes import caches
- `chdir(path)`
- `context()` -- classmethod returning scoped context manager
- `undo()` -- manually undo (auto-called at teardown)

**Caveat**: Avoid patching builtins like `open()`/`compile()` -- breaks pytest. Use `context()` to isolate.

## Temporary Files

### tmp_path (function-scoped)
```python
def test_files(tmp_path):
    p = tmp_path / "myfile.txt"
    p.write_text("content", encoding="utf-8")
    assert p.read_text(encoding="utf-8") == "content"
```

### tmp_path_factory (session-scoped)
```python
@pytest.fixture(scope="session")
def shared_data(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "config.json"
    fn.write_text('{"key": "value"}')
    return fn
```
- `mktemp(basename, numbered=True)` -- create temp dir
- `getbasetemp()` -- return base temp path

Path pattern: `{temproot}/pytest-of-{user}/pytest-{num}/{testname}/`
Override root: `PYTEST_DEBUG_TEMPROOT` env var.

**Legacy**: `tmpdir` / `tmpdir_factory` return `py.path.local`. Disable with `-p no:legacypath`.

**With xdist**: subprocess temp dirs auto-isolated under single run dir.

## Cache

Persists across runs in `.pytest_cache/`.
```python
def test_incremental(pytestconfig):
    cache = pytestconfig.cache
    val = cache.get("myprefix/lastval", None)
    cache.set("myprefix/lastval", 42)
```

- `cache.get(key, default)` -- retrieve (key format: `"namespace/key"`)
- `cache.set(key, value)` -- store (JSON-serializable)
- `cache.mkdir(name)` -- directory for file storage (no "/" in name)

CLI: `--cache-show`, `--cache-clear`, `--lf`, `--ff`, `--nf`, `--sw`

## Warnings

### recwarn
```python
def test_warnings(recwarn):
    warnings.warn("msg", UserWarning)
    assert len(recwarn) == 1
    w = recwarn.pop(UserWarning)
    assert str(w.message) == "msg"
    assert w.category == UserWarning
```
- `recwarn.list` -- list of `WarningMessage`
- `recwarn.pop(category)` -- pop first of category
- `recwarn.clear()`

## Configuration Access

### pytestconfig (session-scoped)
```python
def test_config(pytestconfig):
    val = pytestconfig.getoption("--myopt")
    ini = pytestconfig.getini("markers")
```

### doctest_namespace
Dict injected into doctest namespace:
```python
@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace["np"] = numpy
```

## Test Metadata

### record_property
```python
def test_example(record_property):
    record_property("example_key", 1)  # appears in JUnit XML
```

### record_testsuite_property (session-scoped)
```python
def test_suite(record_testsuite_property):
    record_testsuite_property("ARCH", "x86_64")
```

## Plugin Testing

### pytester
For testing pytest plugins. Enable: `pytest_plugins = ["pytester"]`

```python
def test_my_plugin(pytester):
    pytester.makepyfile("""
        def test_example():
            assert 1 + 1 == 2
    """)
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*::test_example PASSED*"])
```

**File creation:** `makepyfile()`, `makeconftest()`, `makeini()`, `makefile(ext)`, `maketoml()`, `makepyprojecttoml()`
**Directory:** `mkdir(name)`, `mkpydir(name)`, `path` (pathlib.Path)
**Execution:** `runpytest()`, `runpytest_inprocess()`, `runpytest_subprocess()`, `inline_run()`
**RunResult:** `.ret` (return code), `.stdout`/`.stderr` (LineMatcher), `.assert_outcomes()`
**LineMatcher:** `.fnmatch_lines()`, `.re_match_lines()`, `.no_fnmatch_line()`

## Subtests

Built-in since v9.0 (previously `pytest-subtests` plugin).
```python
def test_with_subtests(subtests):
    for i in range(5):
        with subtests.test(msg=f"case {i}", i=i):
            assert i % 2 == 0  # failures reported individually as SUBFAILED
```

- Execute during runtime (not collection time)
- Cannot be individually targeted by CLI or `--last-failed`
- Use `verbosity_subtests` config for output control
- Type annotation: `pytest.Subtests`
