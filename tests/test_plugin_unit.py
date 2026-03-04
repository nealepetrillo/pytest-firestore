"""Unit tests for pytest_firestore.plugin (no external dependencies)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from pytest_firestore._emulator import EmulatorInfo
from pytest_firestore.plugin import _get_option, pytest_addoption

# Access the raw generator function, bypassing the pytest fixture decorator.
import pytest_firestore.plugin as _plugin_mod

_firestore_emulator_fn = _plugin_mod.firestore_emulator.__wrapped__


# ── _get_option ──────────────────────────────────────────────────────────


class TestGetOption:
    def _make_config(self, cli_val, ini_val):
        config = MagicMock()
        config.getoption.return_value = cli_val
        config.getini.return_value = ini_val
        return config

    def test_cli_precedence(self):
        config = self._make_config("from-cli", "from-ini")
        assert _get_option(config, "some_cli", "some_ini") == "from-cli"

    def test_fallback_to_ini(self):
        config = self._make_config(None, "from-ini")
        assert _get_option(config, "some_cli", "some_ini") == "from-ini"

    def test_numeric_to_str(self):
        config = self._make_config(8080, "default")
        assert _get_option(config, "some_cli", "some_ini") == "8080"


# ── pytest_addoption ─────────────────────────────────────────────────────


class TestPytestAddoption:
    def test_registers_options(self):
        parser = MagicMock()
        group = MagicMock()
        parser.getgroup.return_value = group

        pytest_addoption(parser)

        assert group.addoption.call_count == 4
        assert parser.addini.call_count == 4


# ── firestore_emulator fixture ───────────────────────────────────────────


class TestFirestoreEmulatorFixture:
    def _make_request(self, *, has_workerinput=False):
        config = MagicMock()
        config.getoption.return_value = None
        config.getini.side_effect = lambda key: {
            "firestore_emulator_host": "localhost",
            "firestore_emulator_port": "8080",
            "firestore_project_id": "test-project",
            "firestore_emulator_timeout": "15",
        }[key]
        if has_workerinput:
            config.workerinput = {}
        else:
            del config.workerinput
        request = MagicMock()
        request.config = config
        return request

    def test_sets_and_restores_env(self):
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

    def test_restores_previous_env(self):
        request = self._make_request()
        tmp_path_factory = MagicMock()
        info = EmulatorInfo(host="localhost", port=8080, project="test-project")

        os.environ["FIRESTORE_EMULATOR_HOST"] = "old-value"

        try:
            with patch("pytest_firestore.plugin.FirestoreEmulator") as MockEm:
                instance = MockEm.return_value
                instance.start.return_value = info

                gen = _firestore_emulator_fn(request, tmp_path_factory)
                next(gen)

                with pytest.raises(StopIteration):
                    next(gen)

                assert os.environ["FIRESTORE_EMULATOR_HOST"] == "old-value"
        finally:
            os.environ.pop("FIRESTORE_EMULATOR_HOST", None)

    def test_xdist_uses_shared_dir(self):
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

    def test_no_xdist_no_shared_dir(self):
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
