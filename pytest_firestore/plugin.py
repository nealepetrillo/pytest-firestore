"""pytest plugin for GCP Firestore emulator management."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

from pytest_firestore._emulator import EmulatorInfo, FirestoreEmulator


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


@pytest.fixture(scope="session")
def firestore_emulator(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[EmulatorInfo]:
    """Start and manage a GCP Firestore emulator for the test session."""
    config = request.config

    host = _get_option(config, "firestore_host", "firestore_emulator_host")
    port = int(
        _get_option(config, "firestore_port", "firestore_emulator_port")
    )
    project = _get_option(
        config, "firestore_project", "firestore_project_id"
    )
    timeout = float(
        _get_option(
            config, "firestore_timeout", "firestore_emulator_timeout"
        )
    )

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

    # Set env var so google-cloud-firestore clients auto-connect
    old_host = os.environ.get("FIRESTORE_EMULATOR_HOST")
    os.environ["FIRESTORE_EMULATOR_HOST"] = info.host_port

    yield info

    # Restore env var
    if old_host is None:
        os.environ.pop("FIRESTORE_EMULATOR_HOST", None)
    else:
        os.environ["FIRESTORE_EMULATOR_HOST"] = old_host

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
