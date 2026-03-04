"""Integration tests for pytest-firestore using pytester."""

from __future__ import annotations

import shutil

import pytest

GCLOUD_AVAILABLE = shutil.which("gcloud") is not None
skip_no_gcloud = pytest.mark.skipif(
    not GCLOUD_AVAILABLE, reason="gcloud CLI not available"
)


class TestEmulatorLifecycle:
    """Test that the emulator starts, sets env vars, and port is reachable."""

    @skip_no_gcloud
    def test_emulator_starts_and_sets_env(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            import os
            import socket

            def test_env_var_set(firestore_emulator):
                host_port = firestore_emulator.host_port
                assert os.environ["FIRESTORE_EMULATOR_HOST"] == host_port

            def test_port_reachable(firestore_emulator):
                sock = socket.create_connection(
                    (firestore_emulator.host, firestore_emulator.port), timeout=2.0
                )
                sock.close()

            def test_emulator_info_properties(firestore_emulator):
                assert firestore_emulator.host == "localhost"
                assert isinstance(firestore_emulator.port, int)
                assert firestore_emulator.project == "test-project"
                hp = f"{firestore_emulator.host}:{firestore_emulator.port}"
                assert firestore_emulator.host_port == hp
            """
        )
        result = pytester.runpytest("-v", "--firestore-port=0")
        result.assert_outcomes(passed=3)


class TestConfiguration:
    """Test configuration via ini and CLI."""

    @skip_no_gcloud
    def test_custom_project_via_ini(self, pytester: pytest.Pytester) -> None:
        pytester.makeini(
            """
            [pytest]
            firestore_project_id = my-custom-project
            """
        )
        pytester.makepyfile(
            """
            def test_custom_project(firestore_emulator):
                assert firestore_emulator.project == "my-custom-project"
            """
        )
        result = pytester.runpytest("-v", "--firestore-port=0")
        result.assert_outcomes(passed=1)

    @skip_no_gcloud
    def test_cli_overrides_ini(self, pytester: pytest.Pytester) -> None:
        pytester.makeini(
            """
            [pytest]
            firestore_project_id = ini-project
            """
        )
        pytester.makepyfile(
            """
            def test_cli_override(firestore_emulator):
                assert firestore_emulator.project == "cli-project"
            """
        )
        result = pytester.runpytest(
            "-v",
            "--firestore-port=0",
            "--firestore-project=cli-project",
        )
        result.assert_outcomes(passed=1)


class TestAutoPort:
    """Test automatic port assignment."""

    @skip_no_gcloud
    def test_port_zero_assigns_free_port(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_auto_port(firestore_emulator):
                assert firestore_emulator.port != 0
                assert firestore_emulator.port > 0
            """
        )
        result = pytester.runpytest("-v", "--firestore-port=0")
        result.assert_outcomes(passed=1)


class TestClientFixtures:
    """Test that client fixtures are available."""

    @skip_no_gcloud
    def test_sync_client_fixture(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_firestore_client(firestore_client):
                assert firestore_client is not None
            """
        )
        result = pytester.runpytest("-v", "--firestore-port=0")
        # Either passed (client installed) or skipped (not installed)
        outcomes = result.parseoutcomes()
        total = outcomes.get("passed", 0) + outcomes.get("skipped", 0)
        assert total == 1

    @skip_no_gcloud
    def test_async_client_fixture(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_firestore_async_client(firestore_async_client):
                assert firestore_async_client is not None
            """
        )
        result = pytester.runpytest("-v", "--firestore-port=0")
        # Either passed (client installed) or skipped (not installed)
        outcomes = result.parseoutcomes()
        total = outcomes.get("passed", 0) + outcomes.get("skipped", 0)
        assert total == 1
