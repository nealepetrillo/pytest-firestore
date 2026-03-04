# Pytest API Reference

## Table of Contents
- [Constants](#constants)
- [Core Functions](#core-functions)
- [Exception & Warning Testing](#exception--warning-testing)
- [Markers](#markers)
- [Fixture Decorator](#fixture-decorator)
- [Request Object](#request-object)
- [Config Object](#config-object)
- [Collection Tree](#collection-tree)
- [Reporting Objects](#reporting-objects)
- [Hook Functions](#hook-functions)
- [Metafunc Object](#metafunc-object)
- [Parser Object](#parser-object)
- [Stash](#stash)
- [Exit Codes](#exit-codes)

## Constants

- `pytest.__version__` -- version string
- `pytest.version_tuple` -- version as tuple
- `pytest.HIDDEN_PARAM` (v8.4+) -- pass to `ids` to hide param sets from test names

## Core Functions

### `pytest.approx(expected, rel=None, abs=None, nan_ok=False)`
Floating-point comparison with tolerance. Default rel=1e-6, abs=1e-12.
Supports: floats, complex, Decimal, sequences, dicts, numpy arrays.
```python
assert 0.1 + 0.2 == pytest.approx(0.3)
assert [0.1 + 0.2, 0.2 + 0.4] == pytest.approx([0.3, 0.6])
```

### `pytest.fail(reason="", pytrace=True)`
Explicitly fail. `pytrace=False` suppresses traceback.

### `pytest.skip(reason="", allow_module_level=False)`
Skip current test. `allow_module_level=True` for module-level skip.

### `pytest.importorskip(modname, minversion=None, reason=None, exc_type=None)`
Import or skip. Returns the module. `exc_type` (v8.2+) filters exceptions.

### `pytest.xfail(reason="")`
Immediately mark as expected failure.

### `pytest.exit(reason="", returncode=None)`
Exit entire test process. Default returncode is `ExitCode.INTERRUPTED`.

### `pytest.main(args=None, plugins=None)`
Run pytest in-process. Returns exit code.
**Gotcha**: Multiple calls won't reflect file changes due to import caching.

### `pytest.param(*values, id=None, marks=None)`
Wrap parametrize values with custom id/marks. `id` accepts `HIDDEN_PARAM` (v8.4+).

### `pytest.register_assert_rewrite(*names)`
Register modules for assertion rewriting. Call before import in conftest.py.

### `pytest.freeze_includes()`
Module list for cx_Freeze packaging.

## Exception & Warning Testing

### `pytest.raises(expected_exception, *, match=None, check=None)`
Context manager for exception assertions.
- `match`: regex against message + PEP-678 notes
- `check` (v8.4+): callable returning bool for custom validation
- Yields `ExceptionInfo` with `.type`, `.value`, `.tb`

```python
with pytest.raises(ValueError, match=r"invalid.*"):
    raise ValueError("invalid input")
```

### `pytest.RaisesGroup`
For `BaseExceptionGroup`/`ExceptionGroup` assertions.

### `pytest.warns(expected_warning=Warning, *, match=None)`
Context manager for warning assertions. Returns list of `WarningMessage`.
Unmatched warnings re-emitted on close (v8.0+).

### `pytest.deprecated_call(match=None)`
Assert code triggers `DeprecationWarning`/`PendingDeprecationWarning`.

## Markers

### Built-in Marks

```python
@pytest.mark.parametrize(argnames, argvalues, indirect=False, ids=None, scope=None)
@pytest.mark.skip(reason=None)
@pytest.mark.skipif(condition, *, reason)       # reason required
@pytest.mark.xfail(condition=False, *, reason=None, raises=None, run=True, strict=False)
@pytest.mark.usefixtures(*names)                # no effect on fixtures themselves
@pytest.mark.filterwarnings(filter)             # Python warning filter format
```

**xfail details**: `strict=False` shows xfailed/xpass without failing. `strict=True` fails on unexpected pass. `run=False` marks without executing.

### Custom Marks
`@pytest.mark.name(args, kwargs=value)` -- creates `Mark` with `.args`, `.kwargs`.
Register in config to suppress warnings and enable `--strict-markers`.

## Fixture Decorator

```python
@pytest.fixture(scope="function", params=None, autouse=False, ids=None, name=None)
```
- `scope`: `"function"` | `"class"` | `"module"` | `"package"` | `"session"` | callable
- `params`: list for parametrization (access via `request.param`)
- `autouse`: activate for all tests in scope
- `ids`: custom parameter identifiers (list or callable)
- `name`: override fixture name

## Request Object

### Attributes
- `request.param` -- current parametrize value
- `request.param_index` -- index of current param
- `request.fixturename`, `request.scope`
- `request.config` -- Config object
- `request.function`, `request.cls`, `request.instance`, `request.module`
- `request.path` (pathlib.Path), `request.fspath` (py.path.local)
- `request.node` -- collection node
- `request.keywords` -- keywords/markers mapping

### Methods
- `request.addfinalizer(func)` -- register teardown
- `request.applymarker(marker)` -- add marker to current test
- `request.getfixturevalue(argname)` -- dynamically get fixture value

## Config Object

### Key Attributes
- `config.rootpath` (pathlib.Path) -- root directory
- `config.inipath` (pathlib.Path|None) -- config file path
- `config.option` -- parsed CLI options namespace
- `config.pluginmanager` -- plugin manager
- `config.stash` -- typed key-value store

### Key Methods
- `config.getoption(name, default=None)` -- CLI option value
- `config.getini(name)` -- ini-option value
- `config.addinivalue_line(name, line)` -- append to linelist ini-option

## Collection Tree

`Session` > `Package` > `Module` > `Class` > `Function`/`Item`

### Item (Function) key attributes/methods
- `item.nodeid` -- unique ID like `test_file.py::TestClass::test_method[param]`
- `item.name`, `item.originalname`, `item.path`
- `item.function`, `item.cls`, `item.module`
- `item.own_markers`, `item.keywords`
- `item.add_marker(marker)`
- `item.iter_markers(name=None)`, `item.get_closest_marker(name)`
- `item.user_properties` -- list of (name, value) from `record_property`

## Reporting Objects

### TestReport
- `report.nodeid`, `report.outcome` ("passed"/"failed"/"skipped")
- `report.when` ("setup"/"call"/"teardown")
- `report.longrepr`, `report.longreprtext`
- `report.duration` (float seconds)
- `report.passed`, `report.failed`, `report.skipped` (bool)
- `report.capstdout`, `report.capstderr`, `report.caplog`

### ExceptionInfo
- `excinfo.type`, `excinfo.value`, `excinfo.tb`
- `excinfo.match(pat)` -- assert string repr matches regex
- `excinfo.exconly()` -- exception string only

## Hook Functions

### Initialization
- `pytest_addoption(parser, pluginmanager)` -- register CLI options/ini settings
- `pytest_configure(config)` -- after options parsed
- `pytest_sessionstart(session)` -- before collection
- `pytest_sessionfinish(session, exitstatus)` -- after all tests
- `pytest_unconfigure(config)` -- before exit

### Collection
- `pytest_collect_file(parent, file_path)` -- return Collector or None
- `pytest_collect_directory(path, parent)` -- before traversing directory
- `pytest_collection_modifyitems(session, config, items)` -- modify items in-place
- `pytest_deselected(items)` -- items deselected by -k/-m
- `pytest_generate_tests(metafunc)` -- dynamic parametrization
- `pytest_make_parametrize_id(config, val, argname)` -- custom param IDs
- `pytest_pycollect_makemodule(module_path, parent)`, `pytest_pycollect_makeitem(collector, name, obj)`
- `pytest_itemcollected(item)`

### Execution
- `pytest_runtest_protocol(item, nextitem)` -- full test protocol
- `pytest_runtest_setup(item)`, `pytest_runtest_call(item)`, `pytest_runtest_teardown(item, nextitem)`
- `pytest_runtest_makereport(item, call)` -- create TestReport
- `pytest_fixture_setup(fixturedef, request)`, `pytest_fixture_post_use(fixturedef, request)`

### Reporting
- `pytest_terminal_summary(terminalreporter, exitstatus, config)`
- `pytest_report_header(config, start_path)`
- `pytest_report_teststatus(report, config)` -- return (category, shortletter, verbose)
- `pytest_warning_recorded(warning_message, when, nodeid, location)`
- `pytest_assertion_pass(item, lineno, orig, expl)` -- requires `enable_assertion_pass_hook = true`

### Debugging
- `pytest_internalerror(excrepr, excinfo)`
- `pytest_exception_interact(node, call, report)` -- PDB interaction
- `pytest_enter_pdb(config, pdb)`, `pytest_leave_pdb(config, pdb)`

### Hook Implementation Decorators
```python
@pytest.hookimpl(wrapper=True)          # hook wrapper (yield exactly once)
@pytest.hookimpl(tryfirst=True)         # run before other implementations
@pytest.hookimpl(trylast=True)          # run after other implementations
```
Hook wrappers execute around other implementations. Simplest: `return (yield)`.

**Constraint**: hooks other than `pytest_runtest_*` must not raise exceptions.

## Metafunc Object

Used in `pytest_generate_tests(metafunc)`:
- `metafunc.fixturenames` -- requested fixture names
- `metafunc.function`, `metafunc.cls`, `metafunc.module`, `metafunc.config`
- `metafunc.parametrize(argnames, argvalues, indirect=False, ids=None, scope=None)`

## Parser Object

Used in `pytest_addoption(parser)`:
- `parser.addoption(*opts, **attrs)` -- register CLI option (argparse API)
- `parser.addini(name, help, type=None, default=None)` -- types: `"string"`, `"pathlist"`, `"args"`, `"linelist"`, `"bool"`
- `parser.getgroup(name, description="")` -- get/create option group

## Stash

Typed key-value store on Config, Item, etc:
```python
my_key = pytest.StashKey[str]()
config.stash[my_key] = "value"
val: str = config.stash[my_key]
```

## Exit Codes

```python
class ExitCode(enum.IntEnum):
    OK = 0                  # all tests passed
    TESTS_FAILED = 1        # some tests failed
    INTERRUPTED = 2         # user interrupted (Ctrl+C)
    INTERNAL_ERROR = 3      # internal pytest/plugin error
    USAGE_ERROR = 4         # bad CLI options or config
    NO_TESTS_COLLECTED = 5  # no tests found
```
