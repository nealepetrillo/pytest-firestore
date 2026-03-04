# pytest-firestore

A [pytest](https://docs.pytest.org/) plugin that manages a Google Cloud Firestore emulator instance for your test session. It starts the emulator before tests run, sets the `FIRESTORE_EMULATOR_HOST` environment variable so client libraries connect automatically, and tears everything down when the session ends.

Supports [pytest-xdist](https://pypi.org/project/pytest-xdist/) out of the box — multiple workers share a single emulator process via file-lock coordination.

## Requirements

- Python >= 3.12
- pytest >= 7.0
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud` CLI) with the Firestore emulator component:

```bash
gcloud components install cloud-firestore-emulator
```

## Installation

```bash
pip install pytest-firestore
```

To also install a Firestore client for use with the convenience fixtures:

```bash
pip install pytest-firestore[client]
```

## Quick start

Request the `firestore_emulator` fixture in any test. The emulator starts once per session.

```python
def test_write_and_read(firestore_emulator):
    from google.cloud import firestore

    db = firestore.Client(project=firestore_emulator.project)
    db.collection("users").document("alice").set({"name": "Alice"})
    doc = db.collection("users").document("alice").get()
    assert doc.to_dict()["name"] == "Alice"
```

Or use the ready-made client fixtures (requires `google-cloud-firestore`):

```python
def test_with_client(firestore_client):
    firestore_client.collection("items").document("1").set({"n": 1})
    assert firestore_client.collection("items").document("1").get().exists


async def test_async(firestore_async_client):
    await firestore_async_client.collection("items").document("2").set({"n": 2})
    doc = await firestore_async_client.collection("items").document("2").get()
    assert doc.exists
```

## Fixtures

| Fixture | Scope | Description |
|---|---|---|
| `firestore_emulator` | session | Starts the emulator and returns an `EmulatorInfo` object. Sets `FIRESTORE_EMULATOR_HOST` for the duration of the session. |
| `firestore_client` | function | Returns a `google.cloud.firestore.Client` connected to the emulator. Skips if `google-cloud-firestore` is not installed. |
| `firestore_async_client` | function | Returns a `google.cloud.firestore.AsyncClient` connected to the emulator. Skips if `google-cloud-firestore` is not installed. |

### `EmulatorInfo`

The `firestore_emulator` fixture yields an `EmulatorInfo` dataclass with the following attributes:

| Attribute | Type | Description |
|---|---|---|
| `host` | `str` | Emulator hostname (e.g. `"localhost"`) |
| `port` | `int` | Emulator port (e.g. `8080`) |
| `project` | `str` | GCP project ID (e.g. `"test-project"`) |
| `host_port` | `str` | Combined `"host:port"` string |

## Configuration

Settings can be provided via CLI flags or `pyproject.toml` / `pytest.ini`. CLI flags take precedence over ini values.

| CLI flag | ini option | Default | Description |
|---|---|---|---|
| `--firestore-host` | `firestore_emulator_host` | `localhost` | Emulator bind host |
| `--firestore-port` | `firestore_emulator_port` | `8080` | Emulator port. Use `0` to auto-select a free port. |
| `--firestore-project` | `firestore_project_id` | `test-project` | GCP project ID passed to the emulator |
| `--firestore-timeout` | `firestore_emulator_timeout` | `15` | Seconds to wait for the emulator to accept connections |

### Example `pyproject.toml`

```toml
[tool.pytest.ini_options]
firestore_emulator_host = "localhost"
firestore_emulator_port = "0"          # auto-select a free port
firestore_project_id = "my-test-project"
firestore_emulator_timeout = "30"
```

### Example CLI usage

```bash
pytest --firestore-port 0 --firestore-project my-project
```

## Using with pytest-xdist

No extra configuration is needed. When tests run under xdist, the plugin detects worker processes and coordinates through a shared lock file so that only the first worker starts the emulator. All other workers join the existing instance. When the last worker finishes, the emulator is terminated.

```bash
pytest -n auto
```

## Auto-port selection

Set the port to `0` to have the plugin pick a free port automatically. This is useful in CI environments where port conflicts may occur:

```bash
pytest --firestore-port 0
```

## Environment variable

While the session fixture is active, `FIRESTORE_EMULATOR_HOST` is set to `host:port`. This is the standard variable that `google-cloud-firestore` client libraries check to route traffic to the emulator instead of production. The original value (if any) is restored after the session ends.

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run unit tests (no gcloud required)
pytest tests/test_emulator_unit.py tests/test_plugin_unit.py -v

# Run integration tests (requires gcloud + emulator component)
pytest tests/test_plugin_integration.py -v

# Lint and type-check
ruff check .
mypy pytest_firestore
```

## License

MIT — see [LICENSE](LICENSE).
