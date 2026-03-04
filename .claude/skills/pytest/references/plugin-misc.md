# Miscellaneous Deep Plugins

## pytest-stub

Lightweight dependency stubbing. Replace imports without installing packages.

```bash
pip install pytest-stub
```

### Fixture usage
```python
def test_django(stub):
    stub.apply({
        "django.core.management.call_command": "[func]",     # generated function
        "django.core.management.base.BaseCommand": "[cls]",  # generated class
        "django.dummy": "[mock]",                            # MagicMock
        "cv2": "[mock_persist]",                             # persistent MagicMock
        "numpy": "[mock_persist]",
        "django.conf": {"settings": object(), "some": True}, # custom objects
    })
```

### Global stubbing (conftest.py)
```python
from pytest_stub.toolbox import stub_global
stub_global({"cv2": "[mock_persist]"})
```

**Stub types:** `[func]`, `[cls]`, `[mock]`, `[mock_persist]`, custom objects

Not a replacement for pytest-mock -- no call tracking or spec validation.

---

## pytest-tmp-files

Declarative temporary file tree creation from dictionaries.

```bash
pip install pytest-tmp-files
```

### Usage (indirect parametrization)
```python
@pytest.mark.parametrize("tmp_files,expected", [
    ({"a/b": "x", "c": "y"}, {"a/b"}),
], indirect=["tmp_files"])
def test_search(tmp_files, expected):
    # tmp_files is a pathlib.Path to root with files created
    assert (tmp_files / "a" / "b").read_text() == "x"
```

**Value types:**
- String → text file
- Bytes → binary file
- Dict → subdirectory (recursive)
- Supports symlinks, hard links, named FIFOs
- Can set permissions and modification times

---

## pytest-venv

Temporary virtual environment fixture.

```bash
pip install pytest-venv
```

### API
```python
def test_package(venv):
    venv.install("requests", upgrade=True)
    venv.install("/path/to/local/pkg", editable=True)
    version = venv.get_version("requests")

    # Properties
    venv.path     # venv root directory
    venv.bin      # bin/Scripts directory
    venv.python   # Python executable path
```

`create(system_site_packages=False, python=None, *, extra_args=None)` -- auto-called by fixture.

---

## pytest-bigquery-mock

Mock Google BigQuery client for testing without credentials.

```bash
pip install pytest-bigquery-mock
```

### Setup
```python
# conftest.py
plugins = ["pytest-bigquery-mock"]
```

### Usage
```python
@pytest.mark.bq_query_return_data([{
    "query": "SELECT * FROM dataset.table",
    "table": {
        "columns": ["id", "name"],
        "rows": [[1, "Alice"], [2, "Bob"]],
    },
}])
def test_query(bq_client_mock):
    from google.cloud import bigquery
    client = bigquery.Client()
    results = list(client.query("SELECT * FROM dataset.table").result())
    assert len(results) == 2
```

---

## pytest-bg-process

Start/stop background processes for integration tests.

```bash
pip install pytest-bg-process
```

### Configuration (pytest.ini)
```ini
[pytest]
background-cmd = redis-server
background-pid = redis.pid
background-log = redis.log
```

Or via environment variable:
```ini
[pytest]
background-cmd-env = REDIS_CMD
background-pid = redis.pid
background-log = redis.log
```
```bash
REDIS_CMD=redis-server pytest
```

Process auto-starts before tests, auto-terminates after completion.
