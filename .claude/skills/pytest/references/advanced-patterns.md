# Pytest Advanced Patterns

## Table of Contents
- [Plugin Development](#plugin-development)
- [Hook Writing Patterns](#hook-writing-patterns)
- [Custom Test Collection](#custom-test-collection)
- [unittest Integration](#unittest-integration)
- [xunit-style Setup](#xunit-style-setup)
- [CI Integration](#ci-integration)
- [Import Modes](#import-modes)
- [Project Layouts](#project-layouts)
- [Flaky Test Strategies](#flaky-test-strategies)

## Plugin Development

### Structure
Plugins contain hook functions with `pytest_` prefix. Three types:
- **Builtin**: internal `_pytest` modules
- **External**: discovered via `pytest11` entry points
- **conftest.py**: auto-discovered local plugins

### Loading Order
1. Block with `-p no:name`
2. Load builtins
3. Load `-p name` plugins
4. Load entry point plugins (unless `PYTEST_DISABLE_PLUGIN_AUTOLOAD`)
5. Load `PYTEST_PLUGINS` env var
6. Load conftest.py files

### Creating Installable Plugins
```toml
# pyproject.toml
[project.entry-points.pytest11]
myproject = "myproject.pluginmodule"
```

### Assertion Rewriting for Helpers
```python
# conftest.py
import pytest
pytest.register_assert_rewrite("mypackage.helpers")
```

### Testing Plugins
```python
pytest_plugins = ["pytester"]

def test_my_plugin(pytester):
    pytester.makeconftest('...')
    pytester.makepyfile('...')
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
```

## Hook Writing Patterns

### Basic Hook Implementation
```python
# conftest.py
def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --runslow given."""
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
```

### Hook Wrappers
```python
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield  # execute other implementations
    if report.when == "call" and report.failed:
        # do something on failure
        extra_info = item.funcargs.get("extra_info", "")
    return report
```

### Ordering
1. Wrappers execute (until yield)
2. `tryfirst=True` implementations
3. Regular implementations
4. `trylast=True` implementations
5. Wrappers resume (after yield)

### Custom Hooks
```python
# myplugin.py
def pytest_addhooks(pluginmanager):
    pluginmanager.add_hookspecs(MyHookSpec)
```

### Common Hook Patterns

**Add custom CLI option:**
```python
def pytest_addoption(parser):
    parser.addoption("--env", default="dev", choices=["dev", "staging", "prod"])

@pytest.fixture
def env(request):
    return request.config.getoption("--env")
```

**Incremental testing (skip after first failure in class):**
```python
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item

def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail(f"previous test failed ({previousfailed.name})")
```

**Custom report header:**
```python
def pytest_report_header(config):
    return f"project: myproject, env: {config.getoption('--env')}"
```

## Custom Test Collection

### Changing Discovery Conventions
```ini
[pytest]
python_files = check_*.py
python_classes = Check
python_functions = check_*
```

### Ignoring Paths
```python
# conftest.py
collect_ignore = ["setup.py", "legacy/"]
collect_ignore_glob = ["*_old.py"]
```

### Non-Python Tests (e.g., YAML)
```python
def pytest_collect_file(parent, file_path):
    if file_path.suffix == ".yaml" and file_path.name.startswith("test"):
        return YamlFile.from_parent(parent, path=file_path)

class YamlFile(pytest.File):
    def collect(self):
        raw = yaml.safe_load(self.path.open())
        for name, spec in raw.items():
            yield YamlItem.from_parent(self, name=name, spec=spec)

class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec
    def runtest(self):
        # validate spec
        ...
    def repr_failure(self, excinfo):
        return f"Test failed: {excinfo.value}"
    def reportinfo(self):
        return self.path, 0, f"usecase: {self.name}"
```

### Programmatic Deselection
```python
def pytest_collection_modifyitems(config, items):
    items[:] = [item for item in items if "slow" not in item.nodeid]
```

## unittest Integration

pytest auto-discovers `unittest.TestCase` subclasses.

**Supported:** skip decorators, setUp/tearDown, setUpClass/tearDownClass, subTest (v9.0+)
**Works:** marks (skip, skipif, xfail), autouse fixtures
**Not supported:** load_tests protocol, non-autouse fixtures directly, parametrize

### Mixing Fixtures
```python
@pytest.mark.usefixtures("my_fixture")
class TestMyStuff(unittest.TestCase):
    def test_something(self):
        ...

# Or autouse within the class:
class TestMyStuff(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup_stuff(self, tmp_path):
        self.tmp = tmp_path
```

**Note:** unittest setup/teardown runs during `call` phase, not pytest's `setup`/`teardown`.

## xunit-style Setup

```python
# Module level
def setup_module(module):    ...
def teardown_module(module): ...

# Class level (classmethods)
class TestClass:
    @classmethod
    def setup_class(cls):    ...
    @classmethod
    def teardown_class(cls): ...

    # Method level
    def setup_method(self, method): ...
    def teardown_method(self, method): ...

# Function level (module functions)
def setup_function(function): ...
def teardown_function(function): ...
```

Teardown skips if corresponding setup failed or was skipped.

## CI Integration

Pytest detects CI when `CI` or `BUILD_NUMBER` env vars are set.
In CI: output is not truncated to terminal width.

**JUnit XML for CI:**
```
pytest --junit-xml=results.xml
```

## Import Modes

### prepend (default)
Inserts containing dir at beginning of `sys.path`. Requires unique test filenames across project.

### append
Adds to end of `sys.path`. Tests run against installed package versions.

### importlib (recommended for new projects)
No `sys.path` modification. Auto-generates unique module names.
```ini
[pytest]
addopts = --import-mode=importlib
```
**Limitation:** test modules can't import each other; put utilities in app code.

## Project Layouts

### src layout (recommended)
```
pyproject.toml
src/mypkg/
tests/
```
Use `pip install -e .` for development.

### Inline layout
```
pyproject.toml
mypkg/
    tests/
```
Run via `pytest --pyargs mypkg`.

## Flaky Test Strategies

**Root causes:** shared state, timing, floating-point, thread safety, external deps

**pytest features:**
- `pytest.mark.xfail(strict=False)` -- quarantine known flaky tests
- `pytest.approx()` -- float comparison tolerance
- `PYTEST_CURRENT_TEST` env var -- debug stuck tests

**Plugins:** `pytest-rerunfailures`, `pytest-randomly`, `pytest-timeout`

**Best practices:**
- Isolate tests (no shared mutable state)
- Separate unit and integration suites
- Use proper synchronization for threaded tests
