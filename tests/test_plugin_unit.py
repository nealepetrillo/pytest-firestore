"""Unit tests for pytest_firestore.plugin (no external dependencies)."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Access the raw generator function, bypassing the pytest fixture decorator.
import pytest_firestore.plugin as _plugin_mod
from pytest_firestore._emulator import EmulatorInfo
from pytest_firestore.plugin import _get_option, _parse_host_port, pytest_addoption

_firestore_emulator_fn = _plugin_mod.firestore_emulator.__wrapped__  # type: ignore[attr-defined]


# ── _get_option ──────────────────────────────────────────────────────────


class TestGetOption:
    def _make_config(self, cli_val: Any, ini_val: Any) -> MagicMock:
        config = MagicMock()
        config.getoption.return_value = cli_val
        config.getini.return_value = ini_val
        return config

    def test_cli_precedence(self) -> None:
        config = self._make_config("from-cli", "from-ini")
        assert _get_option(config, "some_cli", "some_ini") == "from-cli"

    def test_fallback_to_ini(self) -> None:
        config = self._make_config(None, "from-ini")
        assert _get_option(config, "some_cli", "some_ini") == "from-ini"

    def test_numeric_to_str(self) -> None:
        config = self._make_config(8080, "default")
        assert _get_option(config, "some_cli", "some_ini") == "8080"


# ── _parse_host_port ────────────────────────────────────────────────────


class TestParseHostPort:
    def test_localhost(self) -> None:
        assert _parse_host_port("localhost:8080") == ("localhost", 8080)

    def test_ip_address(self) -> None:
        assert _parse_host_port("127.0.0.1:9090") == ("127.0.0.1", 9090)

    def test_invalid_format(self) -> None:
        with pytest.raises(ValueError, match="Invalid host:port"):
            _parse_host_port("no-port-here")


# ── pytest_addoption ─────────────────────────────────────────────────────


class TestPytestAddoption:
    def test_registers_options(self) -> None:
        parser = MagicMock()
        group = MagicMock()
        parser.getgroup.return_value = group

        pytest_addoption(parser)

        assert group.addoption.call_count == 4
        assert parser.addini.call_count == 4


# ── firestore_emulator fixture ───────────────────────────────────────────


class TestFirestoreEmulatorFixture:
    def _make_request(
        self, *, has_workerinput: bool = False, workerid: str = "gw0"
    ) -> MagicMock:
        config = MagicMock()
        config.getoption.return_value = None
        config.getini.side_effect = lambda key: {
            "firestore_emulator_host": "localhost",
            "firestore_emulator_port": "8080",
            "firestore_project_id": "test-project",
            "firestore_emulator_timeout": "15",
        }[key]
        if has_workerinput:
            config.workerinput = {"workerid": workerid}
        else:
            del config.workerinput
        request = MagicMock()
        request.config = config
        return request

    def test_sets_and_restores_env(self) -> None:
        request = self._make_request()
        tmp_path_factory = MagicMock()
        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        os.environ.pop("FIRESTORE_EMULATOR_HOST", None)

        with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
            instance = MockEm.return_value
            instance.start.return_value = info

            gen = _firestore_emulator_fn(request, tmp_path_factory)
            result = next(gen)

            assert result is info
            assert os.environ["FIRESTORE_EMULATOR_HOST"] == "localhost:8080"

            with pytest.raises(StopIteration):
                next(gen)

            assert "FIRESTORE_EMULATOR_HOST" not in os.environ
            instance.stop.assert_called_once()

    def test_external_emulator_skips_spawn(self) -> None:
        """When FIRESTORE_EMULATOR_HOST is set, use it without spawning."""
        request = self._make_request()
        tmp_path_factory = MagicMock()

        os.environ["FIRESTORE_EMULATOR_HOST"] = "external-host:9999"

        try:
            with (
                patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm,
                patch("pytest_firestore.plugin._wait_for_port"),
            ):
                gen = _firestore_emulator_fn(request, tmp_path_factory)
                result = next(gen)

                # Should not have spawned an emulator
                MockEm.assert_not_called()

                assert result.host == "external-host"
                assert result.port == 9999
                assert result.project == "test-project"

                with pytest.raises(StopIteration):
                    next(gen)
        finally:
            os.environ.pop("FIRESTORE_EMULATOR_HOST", None)

    def test_external_emulator_waits_for_port(self) -> None:
        """External emulator path verifies the port is reachable."""
        request = self._make_request()
        tmp_path_factory = MagicMock()

        os.environ["FIRESTORE_EMULATOR_HOST"] = "myhost:1234"

        try:
            with (
                patch("pytest_firestore.plugin.FirestoreEmulator"),
                patch("pytest_firestore.plugin._wait_for_port") as mock_wait,
            ):
                gen = _firestore_emulator_fn(request, tmp_path_factory)
                next(gen)
                mock_wait.assert_called_once_with("myhost", 1234, 15.0)

                with pytest.raises(StopIteration):
                    next(gen)
        finally:
            os.environ.pop("FIRESTORE_EMULATOR_HOST", None)

    def test_xdist_uses_shared_dir(self) -> None:
        request = self._make_request(has_workerinput=True)
        tmp_path_factory = MagicMock()
        base = MagicMock()
        tmp_path_factory.getbasetemp.return_value = base

        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
            instance = MockEm.return_value
            instance.start.return_value = info

            gen = _firestore_emulator_fn(request, tmp_path_factory)
            next(gen)

            _, kwargs = MockEm.call_args
            assert kwargs["shared_dir"] is not None

            with pytest.raises(StopIteration):
                next(gen)

    def test_no_xdist_no_shared_dir(self) -> None:
        request = self._make_request(has_workerinput=False)
        tmp_path_factory = MagicMock()

        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
            instance = MockEm.return_value
            instance.start.return_value = info

            gen = _firestore_emulator_fn(request, tmp_path_factory)
            next(gen)

            _, kwargs = MockEm.call_args
            assert kwargs["shared_dir"] is None

            with pytest.raises(StopIteration):
                next(gen)

    def test_xdist_appends_worker_id_to_project(self) -> None:
        request = self._make_request(has_workerinput=True, workerid="gw3")
        tmp_path_factory = MagicMock()
        base = MagicMock()
        tmp_path_factory.getbasetemp.return_value = base

        # Emulator returns base project; fixture adds worker suffix
        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
            instance = MockEm.return_value
            instance.start.return_value = info

            gen = _firestore_emulator_fn(request, tmp_path_factory)
            result = next(gen)

            # Emulator receives base project
            _, kwargs = MockEm.call_args
            assert kwargs["project"] == "test-project"
            # Yielded info has worker-isolated project
            assert result.project == "test-project-gw3"

            with pytest.raises(StopIteration):
                next(gen)

    def test_no_xdist_project_unchanged(self) -> None:
        request = self._make_request(has_workerinput=False)
        tmp_path_factory = MagicMock()

        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
            instance = MockEm.return_value
            instance.start.return_value = info

            gen = _firestore_emulator_fn(request, tmp_path_factory)
            result = next(gen)

            assert result.project == "test-project"
            _, kwargs = MockEm.call_args
            assert kwargs["project"] == "test-project"

            with pytest.raises(StopIteration):
                next(gen)

    def test_xdist_external_emulator_appends_worker_id(self) -> None:
        """External emulator path also gets worker-isolated project."""
        request = self._make_request(has_workerinput=True, workerid="gw1")
        tmp_path_factory = MagicMock()

        os.environ["FIRESTORE_EMULATOR_HOST"] = "external-host:9999"

        try:
            with (
                patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm,
                patch("pytest_firestore.plugin._wait_for_port"),
            ):
                gen = _firestore_emulator_fn(request, tmp_path_factory)
                result = next(gen)

                MockEm.assert_not_called()
                assert result.project == "test-project-gw1"

                with pytest.raises(StopIteration):
                    next(gen)
        finally:
            os.environ.pop("FIRESTORE_EMULATOR_HOST", None)
