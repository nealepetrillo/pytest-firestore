"""Unit tests for pytest_firestore._emulator (no external dependencies)."""

from __future__ import annotations

import dataclasses
import json
import signal
from unittest.mock import MagicMock, patch

import pytest

from pytest_firestore._emulator import (
    EmulatorInfo,
    FirestoreEmulator,
    _find_free_port,
    _is_pid_alive,
    _terminate_process,
    _wait_for_port,
)


# ── EmulatorInfo ─────────────────────────────────────────────────────────


class TestEmulatorInfo:
    def test_host_port_property(self):
        info = EmulatorInfo(host="myhost", port=1234, project="proj")
        assert info.host_port == "myhost:1234"

    def test_frozen(self):
        info = EmulatorInfo(host="h", port=1, project="p")
        with pytest.raises(dataclasses.FrozenInstanceError):
            info.host = "other"  # type: ignore[misc]

    def test_equality(self):
        a = EmulatorInfo(host="h", port=1, project="p")
        b = EmulatorInfo(host="h", port=1, project="p")
        c = EmulatorInfo(host="h", port=2, project="p")
        assert a == b
        assert a != c


# ── _find_free_port ──────────────────────────────────────────────────────


class TestFindFreePort:
    def test_returns_port_from_socket(self):
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("0.0.0.0", 54321)
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)

        with patch("pytest_firestore._emulator.socket.socket", return_value=mock_sock):
            assert _find_free_port() == 54321
        mock_sock.bind.assert_called_once_with(("", 0))


# ── _is_pid_alive ────────────────────────────────────────────────────────


class TestIsPidAlive:
    def test_alive(self):
        with patch("os.kill") as mock_kill:
            mock_kill.return_value = None
            assert _is_pid_alive(42) is True

    def test_dead(self):
        with patch("os.kill", side_effect=ProcessLookupError):
            assert _is_pid_alive(42) is False

    def test_permission_error(self):
        with patch("os.kill", side_effect=PermissionError):
            assert _is_pid_alive(42) is True


# ── _wait_for_port ───────────────────────────────────────────────────────


class TestWaitForPort:
    def test_success_first_try(self):
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("time.monotonic", return_value=0.0), \
             patch("pytest_firestore._emulator.socket.create_connection", return_value=mock_conn):
            _wait_for_port("localhost", 8080, timeout=5.0)

    def test_success_after_retries(self):
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        # monotonic: 0 (deadline calc), 0 (first check), 0.3 (second check), 0.6 (third check)
        with patch("time.monotonic", side_effect=[0.0, 0.0, 0.3, 0.6]), \
             patch("time.sleep"), \
             patch(
                 "pytest_firestore._emulator.socket.create_connection",
                 side_effect=[OSError, OSError, mock_conn],
             ):
            _wait_for_port("localhost", 8080, timeout=5.0)

    def test_timeout_raises(self):
        # monotonic: 0 (deadline=5), 0 (first loop), then 6 (past deadline)
        with patch("time.monotonic", side_effect=[0.0, 0.0, 6.0]), \
             patch("time.sleep"), \
             patch(
                 "pytest_firestore._emulator.socket.create_connection",
                 side_effect=OSError,
             ):
            with pytest.raises(TimeoutError, match="did not start"):
                _wait_for_port("localhost", 8080, timeout=5.0)


# ── _terminate_process ───────────────────────────────────────────────────


class TestTerminateProcess:
    def test_sigterm_kills(self):
        with patch("os.kill") as mock_kill, \
             patch("pytest_firestore._emulator._is_pid_alive", return_value=False):
            _terminate_process(123)
        mock_kill.assert_called_once_with(123, signal.SIGTERM)

    def test_already_dead(self):
        with patch("os.kill", side_effect=ProcessLookupError):
            _terminate_process(123)  # should not raise

    def test_sigkill_fallback(self):
        # Process stays alive, monotonic exceeds deadline → SIGKILL
        with patch("os.kill") as mock_kill, \
             patch("pytest_firestore._emulator._is_pid_alive", return_value=True), \
             patch("time.monotonic", side_effect=[0.0, 0.0, 10.0]), \
             patch("time.sleep"):
            _terminate_process(123, timeout=5.0)
        assert mock_kill.call_count == 2
        mock_kill.assert_any_call(123, signal.SIGTERM)
        mock_kill.assert_any_call(123, signal.SIGKILL)

    def test_sigkill_race(self):
        def kill_side_effect(pid, sig):
            if sig == signal.SIGKILL:
                raise ProcessLookupError

        with patch("os.kill", side_effect=kill_side_effect), \
             patch("pytest_firestore._emulator._is_pid_alive", return_value=True), \
             patch("time.monotonic", side_effect=[0.0, 0.0, 10.0]), \
             patch("time.sleep"):
            _terminate_process(123, timeout=5.0)  # no exception


# ── FirestoreEmulator (standalone) ───────────────────────────────────────


class TestFirestoreEmulatorStandalone:
    def test_fixed_port(self):
        with patch.object(FirestoreEmulator, "_launch") as mock_launch, \
             patch("pytest_firestore._emulator._wait_for_port"), \
             patch("pytest_firestore._emulator._find_free_port") as mock_free:
            mock_launch.return_value = MagicMock(pid=1)
            em = FirestoreEmulator(port=9999)
            em.start()
            mock_free.assert_not_called()
            mock_launch.assert_called_once_with("localhost", 9999, "test-project")

    def test_auto_port(self):
        with patch.object(FirestoreEmulator, "_launch") as mock_launch, \
             patch("pytest_firestore._emulator._wait_for_port"), \
             patch("pytest_firestore._emulator._find_free_port", return_value=55555):
            mock_launch.return_value = MagicMock(pid=1)
            em = FirestoreEmulator(port=0)
            info = em.start()
            assert info.port == 55555

    def test_stop_terminates(self):
        with patch.object(FirestoreEmulator, "_launch") as mock_launch, \
             patch("pytest_firestore._emulator._wait_for_port"), \
             patch("pytest_firestore._emulator._terminate_process") as mock_term:
            mock_proc = MagicMock(pid=42)
            mock_launch.return_value = mock_proc
            em = FirestoreEmulator()
            em.start()
            em.stop()
            mock_term.assert_called_once_with(42)

    def test_info_before_start_raises(self):
        em = FirestoreEmulator()
        with pytest.raises(RuntimeError, match="not been started"):
            em.info


# ── FirestoreEmulator (shared / xdist) ──────────────────────────────────


class TestFirestoreEmulatorShared:
    def _write_state(self, path, state):
        path.write_text(json.dumps(state))

    def test_first_worker_starts(self, tmp_path):
        with patch.object(FirestoreEmulator, "_launch") as mock_launch, \
             patch("pytest_firestore._emulator._wait_for_port"):
            mock_launch.return_value = MagicMock(pid=100)
            em = FirestoreEmulator(shared_dir=tmp_path)
            em.start()

        state = json.loads((tmp_path / "firestore_emulator.json").read_text())
        assert state["worker_count"] == 1
        assert state["pid"] == 100

    def test_second_worker_joins(self, tmp_path):
        self._write_state(
            tmp_path / "firestore_emulator.json",
            {"pid": 200, "host": "localhost", "port": 8080, "project": "p", "worker_count": 1},
        )
        with patch("pytest_firestore._emulator._is_pid_alive", return_value=True), \
             patch.object(FirestoreEmulator, "_launch") as mock_launch:
            em = FirestoreEmulator(shared_dir=tmp_path)
            info = em.start()
            mock_launch.assert_not_called()

        state = json.loads((tmp_path / "firestore_emulator.json").read_text())
        assert state["worker_count"] == 2
        assert info.port == 8080

    def test_stale_state_restarts(self, tmp_path):
        self._write_state(
            tmp_path / "firestore_emulator.json",
            {"pid": 999, "host": "localhost", "port": 8080, "project": "p", "worker_count": 1},
        )
        with patch("pytest_firestore._emulator._is_pid_alive", return_value=False), \
             patch.object(FirestoreEmulator, "_launch") as mock_launch, \
             patch("pytest_firestore._emulator._wait_for_port"):
            mock_launch.return_value = MagicMock(pid=300)
            em = FirestoreEmulator(shared_dir=tmp_path)
            em.start()
            mock_launch.assert_called_once()

        state = json.loads((tmp_path / "firestore_emulator.json").read_text())
        assert state["pid"] == 300
        assert state["worker_count"] == 1

    def test_stop_decrements(self, tmp_path):
        self._write_state(
            tmp_path / "firestore_emulator.json",
            {"pid": 200, "host": "localhost", "port": 8080, "project": "p", "worker_count": 2},
        )
        with patch("pytest_firestore._emulator._terminate_process") as mock_term:
            em = FirestoreEmulator(shared_dir=tmp_path)
            em.stop()
            mock_term.assert_not_called()

        state = json.loads((tmp_path / "firestore_emulator.json").read_text())
        assert state["worker_count"] == 1

    def test_stop_last_worker_terminates(self, tmp_path):
        state_path = tmp_path / "firestore_emulator.json"
        self._write_state(
            state_path,
            {"pid": 200, "host": "localhost", "port": 8080, "project": "p", "worker_count": 1},
        )
        with patch("pytest_firestore._emulator._terminate_process") as mock_term:
            em = FirestoreEmulator(shared_dir=tmp_path)
            em.stop()
            mock_term.assert_called_once_with(200)
        assert not state_path.exists()

    def test_stop_no_state_file(self, tmp_path):
        em = FirestoreEmulator(shared_dir=tmp_path)
        em.stop()  # should not raise


# ── _launch ──────────────────────────────────────────────────────────────


class TestLaunch:
    def test_command_args(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(pid=1)
            FirestoreEmulator._launch("myhost", 9090, "myproj")
            mock_popen.assert_called_once()
            cmd = mock_popen.call_args[0][0]
            assert cmd == [
                "gcloud", "emulators", "firestore", "start",
                "--host-port=myhost:9090",
                "--project=myproj",
            ]
