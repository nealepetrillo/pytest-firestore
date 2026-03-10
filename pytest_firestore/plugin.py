"""pytest plugin for GCP Firestore emulator management."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

from pytest_firestore._emulator import EmulatorInfo, FirestoreEmulator, _wait_for_port


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("firestore", "GCP Firestore emulator")
    group.addoption(
        "--firestore-host",
        dest="firestore_host",
        default=None,
        help="Emulator host (default: localhost)",
    )
    group.addoption(
        "--firestore-port",
        dest="firestore_port",
        default=None,
        type=int,
        help="Emulator port (default: 8080, use 0 for auto)",
    )
    group.addoption(
        "--firestore-project",
        dest="firestore_project",
        default=None,
        help="GCP project ID (default: test-project)",
    )
    group.addoption(
        "--firestore-timeout",
        dest="firestore_timeout",
        default=None,
        type=float,
        help="Emulator startup timeout in seconds (default: 15)",
    )
    parser.addini(
        "firestore_emulator_host",
        "Firestore emulator host",
        default="localhost",
    )
    parser.addini(
        "firestore_emulator_port",
        "Firestore emulator port",
        default="8080",
    )
    parser.addini(
        "firestore_project_id",
        "GCP project ID for emulator",
        default="test-project",
    )
    parser.addini(
        "firestore_emulator_timeout",
        "Emulator startup timeout in seconds",
        default="15",
    )


def _get_option(config: pytest.Config, cli: str, ini: str) -> str:
    """Get a config value, CLI flag takes precedence over ini."""
    cli_val = config.getoption(cli)
    if cli_val is not None:
        return str(cli_val)
    return str(config.getini(ini))


def _parse_host_port(host_port: str) -> tuple[str, int]:
    """Parse a 'host:port' string into (host, port)."""
    parts = host_port.rsplit(":", 1)
    if len(parts) != 2:
        msg = f"Invalid host:port format: {host_port!r}"
        raise ValueError(msg)
    return parts[0], int(parts[1])


@pytest.fixture(scope="session")
def firestore_emulator(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[EmulatorInfo]:
    """Start and manage a GCP Firestore emulator for the test session.

    If ``FIRESTORE_EMULATOR_HOST`` is already set in the environment (e.g. by
    a Docker service container in CI), the fixture connects to that external
    emulator instead of spawning a new process.
    """
    config = request.config
    project = _get_option(config, "firestore_project", "firestore_project_id")
    timeout = float(
        _get_option(config, "firestore_timeout", "firestore_emulator_timeout")
    )

    # Under xdist, append worker ID to project for data isolation.
    # Applied after emulator start so the shared state uses the base project.
    worker_id: str | None = None
    if hasattr(config, "workerinput"):
        worker_id = config.workerinput["workerid"]

    # If an external emulator is already running, use it directly.
    external_host = os.environ.get("FIRESTORE_EMULATOR_HOST")
    if external_host:
        host, port = _parse_host_port(external_host)
        _wait_for_port(host, port, timeout)
        isolated_project = f"{project}-{worker_id}" if worker_id else project
        yield EmulatorInfo(host=host, port=port, project=isolated_project)
        return

    host = _get_option(config, "firestore_host", "firestore_emulator_host")
    port = int(_get_option(config, "firestore_port", "firestore_emulator_port"))

    # Detect xdist worker — use the shared tmp dir above all workers' bases
    shared_dir: Path | None = None
    if hasattr(config, "workerinput"):
        root_tmp_dir = tmp_path_factory.getbasetemp().parent
        shared_dir = root_tmp_dir / ".firestore_emulator"
        shared_dir.mkdir(exist_ok=True)

    emulator = FirestoreEmulator(
        host=host,
        port=port,
        project=project,
        timeout=timeout,
        shared_dir=shared_dir,
    )

    info = emulator.start()

    # Replace project with worker-isolated version
    if worker_id:
        info = EmulatorInfo(
            host=info.host, port=info.port, project=f"{project}-{worker_id}"
        )

    # Set env var so google-cloud-firestore clients auto-connect
    os.environ["FIRESTORE_EMULATOR_HOST"] = info.host_port

    yield info

    # Restore env var
    if external_host is None:
        os.environ.pop("FIRESTORE_EMULATOR_HOST", None)
    else:
        os.environ["FIRESTORE_EMULATOR_HOST"] = external_host

    emulator.stop()


@pytest.fixture()
def firestore_client(
    firestore_emulator: EmulatorInfo,
) -> object:
    """Create a Firestore Client connected to the emulator."""
    try:
        from google.cloud import firestore
    except ImportError:
        pytest.skip("google-cloud-firestore not installed")
    return firestore.Client(project=firestore_emulator.project)


@pytest.fixture()
def firestore_async_client(
    firestore_emulator: EmulatorInfo,
) -> object:
    """Create a Firestore AsyncClient connected to the emulator."""
    try:
        from google.cloud import firestore
    except ImportError:
        pytest.skip("google-cloud-firestore not installed")
    return firestore.AsyncClient(project=firestore_emulator.project)
