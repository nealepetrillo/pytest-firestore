# pytest-xdist: Parallel & Distributed Testing

Requires: pytest>=7.0.0, execnet>=2.1.0, Python>=3.9

## Installation
```bash
pip install pytest-xdist
pip install pytest-xdist[psutil]  # for CPU detection
```

## Quick Start
```bash
pytest -n auto                    # workers = physical CPU count
pytest -n 4                       # explicit 4 workers
pytest -n logical                 # logical CPU count (requires psutil)
pytest -n 0                       # disable xdist
```

## Distribution Modes (`--dist`)

| Mode | Behavior |
|------|----------|
| `load` (default) | Dynamic: sends ~25% initially, then one-by-one to free workers |
| `loadscope` | Groups by module (functions) or class (methods), largest scopes first |
| `loadfile` | Groups by file, distributes groups atomically |
| `loadgroup` | Groups by `@pytest.mark.xdist_group("name")` marker |
| `worksteal` | Even initial distribution, then steals from busy workers |
| `each` | Sends entire suite to every worker (multi-platform testing) |
| `no` | Sequential (normal pytest) |

Default distribution mode is configurable in pytest config files (e.g., `pyproject.toml`).

```bash
pytest -n auto --dist=loadscope   # keep module/class tests together
pytest -n auto --dist=loadfile    # keep file tests together
pytest -n auto --dist=worksteal   # balanced with fixture reuse
```

### xdist_group marker
```python
@pytest.mark.xdist_group("serial")
def test_a(): ...

@pytest.mark.xdist_group("serial")
def test_b(): ...
# Both run on same worker with --dist=loadgroup
```

Multiple `xdist_group` markers on the same test are merged when assigning to groups.

### loadscope reordering (3.8.0+)
```bash
pytest -n auto --dist=loadscope --no-loadscope-reorder  # preserve original order
pytest -n auto --dist=loadscope --loadscope-reorder     # sort scopes by test count (default)
```

## CLI Options

| Option | Description |
|--------|-------------|
| `-n NUM` / `-n auto` / `-n logical` | Worker count |
| `--dist=MODE` | Distribution mode |
| `--maxprocesses=NUM` | Cap workers (with `-n auto`) |
| `--maxschedchunk=NUM` | Max tests to send per scheduling chunk (load mode) |
| `--max-worker-restart=NUM` | Max crash restarts (default: 4 x worker count) |
| `--testrunuid=UID` | Override the unique test run identifier |
| `--no-loadscope-reorder` | Disable automatic test reordering in loadscope mode |
| `--tx=SPEC` | Execution environment spec (subprocess/remote) |
| `--px=SPEC` | Proxy gateway spec for multi-worker remote execution |
| `-f` / `--looponfail` | **DEPRECATED** Re-run failures in loop until green |
| `--rsyncdir=DIR` | **DEPRECATED** Dirs to rsync to remote workers |

Custom worker count: set `PYTEST_XDIST_AUTO_NUM_WORKERS` env var or implement `pytest_xdist_auto_num_workers` hook in conftest.py (hook takes priority).

## Worker Identification

### Fixture
```python
def test_db(worker_id):
    # "gw0", "gw1", ... or "master" when not distributed
    db_name = f"test_db_{worker_id}"
```

### Environment Variables
- `PYTEST_XDIST_WORKER` -- worker name (e.g., `"gw2"`)
- `PYTEST_XDIST_WORKER_COUNT` -- total workers
- `PYTEST_XDIST_TESTRUNUID` -- unique run ID

### Programmatic
```python
from xdist import is_xdist_worker, is_xdist_controller, get_xdist_worker_id
```

## How It Works

1. Controller spawns workers via **execnet** gateways (local or remote interpreters)
2. Each worker performs **full independent test collection** and sends test-ids to controller
3. Controller **verifies all workers collected identical tests in the same order**, then converts to index positions
4. In `each` mode, controller sends full index list to every worker
5. In `load` mode, sends ~25% round-robin initially, then one-by-one as workers finish
6. Workers reimplement `pytest_runtestloop` -- idle until receiving test instructions
7. Results transmit back to controller and forward to standard pytest hooks (`pytest_runtest_logreport`, etc.)
8. Custom distribution: implement `pytest_xdist_make_scheduler` hook

**Why workers collect individually:** Serializing test items across processes is impractical -- items contain references to functions, fixture managers, and config objects.

## Session-Scoped Fixtures with xdist

**Problem:** Each worker runs session fixtures independently, causing resource conflicts.

**Solution:** Use `filelock` for coordination:
```python
import json
from filelock import FileLock

@pytest.fixture(scope="session")
def db_schema(tmp_path_factory, worker_id):
    if worker_id == "master":
        # Not distributed, just create
        _create_schema()
        return

    root_tmp = tmp_path_factory.getbasetemp().parent
    lock = root_tmp / "db.lock"
    data_file = root_tmp / "db_ready.json"

    with FileLock(str(lock)):
        if not data_file.exists():
            _create_schema()
            data_file.write_text(json.dumps({"ready": True}))
```

### testrun_uid fixture
Unique identifier for the test run, shared across all workers. Use for creating unique resources per run. Can be overridden with `--testrunuid` CLI option.

## Per-Worker Resources

### Unique log files
```python
# conftest.py
def pytest_configure(config):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
    config.addinivalue_line("log_file", f"tests_{worker}.log")
```

### Separate databases
```python
@pytest.fixture(scope="session")
def db_url(worker_id):
    return f"postgresql://localhost/test_{worker_id}"
```

## Subprocess Execution

Run tests in a different Python interpreter:
```bash
pytest -d --tx popen//python=python3.12
pytest -d --tx 3*popen//python=python3.12   # 3 subprocess workers
```

## Remote Execution (SSH)

> **Note:** `--rsyncdir` and rsync features are deprecated since 3.0, scheduled for removal in 4.0. SSH and socket server features remain supported via execnet.

```bash
pytest -d --tx ssh=myhost --rsyncdir mypkg mypkg/tests/
```

### Socket server
```bash
pytest -d --tx socket=192.168.1.102:8888 --rsyncdir mypkg
```

### Proxy gateways (3.7.0+)
```bash
pytest -d --px id=my_proxy//socket=192.168.1.102:8888 --tx 5*popen//via=my_proxy
```

## Hooks

| Hook | Purpose |
|------|---------|
| `pytest_xdist_auto_num_workers(config)` | Custom worker count for `-n auto` |
| `pytest_xdist_make_scheduler(config, log)` | Custom test distribution scheduler |
| `pytest_xdist_getremotemodule` | Override remote worker module |
| `pytest_xdist_node_collection_finished(node, ids)` | Called when a worker finishes collection |
| `pytest_handlecrashitem(crashinfo, report, sched)` | Handle crashed test items for rescheduling |

## Known Limitations

- **No stdout capture:** `-s`/`--capture=no` does not work -- execnet cannot transfer stdout/stderr from workers
- **No PDB debugging:** `--pdb` is disabled during distributed testing. Use remote debuggers (`python-remote-pdb`, `python-web-pdb`) instead
- **Test ordering must be consistent:** All workers must collect identical tests in the same order. Avoid parametrizing with unordered collections (sets, generators) -- use lists or `sorted()`
- Tests must be **independent** -- no shared mutable state
- Test **ordering is not guaranteed** across workers
- `conftest.py` hooks run **once per worker**
- Each worker performs independent collection
- `--looponfail` is deprecated (removal in 4.0)

## Parametrize Pitfall

```python
# BAD: set ordering varies across workers -- collection mismatch error
@pytest.mark.parametrize("param", {"a", "b"})
def test_bad(param): ...

# GOOD: use a list or sorted()
@pytest.mark.parametrize("param", ["a", "b"])
def test_good(param): ...
```
