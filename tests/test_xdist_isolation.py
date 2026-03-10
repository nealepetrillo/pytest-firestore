"""Integration tests for xdist worker data isolation."""

from __future__ import annotations

import shutil

import pytest

GCLOUD_AVAILABLE = shutil.which("gcloud") is not None
skip_no_gcloud = pytest.mark.skipif(
    not GCLOUD_AVAILABLE, reason="gcloud CLI not available"
)

try:
    import xdist  # type: ignore[import-untyped]  # noqa: F401

    XDIST_AVAILABLE = True
except ImportError:
    XDIST_AVAILABLE = False

skip_no_xdist = pytest.mark.skipif(
    not XDIST_AVAILABLE, reason="pytest-xdist not installed"
)

try:
    from google.cloud import firestore  # noqa: F401

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

skip_no_firestore = pytest.mark.skipif(
    not FIRESTORE_AVAILABLE, reason="google-cloud-firestore not installed"
)


class TestXdistIsolation:
    @skip_no_gcloud
    @skip_no_xdist
    @skip_no_firestore
    def test_workers_see_only_own_data(self, pytester: pytest.Pytester) -> None:
        """With xdist, each worker gets a unique project ID so data is isolated."""
        pytester.makepyfile(
            """
            import os
            import pytest

            @pytest.mark.parametrize("run", [1, 2])
            def test_write_and_verify_isolation(firestore_client, firestore_emulator, run):
                worker = os.environ.get("PYTEST_XDIST_WORKER", "main")

                # Write a doc identifying this worker
                doc_ref = firestore_client.collection("isolation").document(worker)
                doc_ref.set({"worker": worker})

                # Read all docs - should only see our own
                docs = list(firestore_client.collection("isolation").stream())
                assert len(docs) == 1, (
                    f"Worker {worker} expected 1 doc but found {len(docs)}: "
                    f"{[d.id for d in docs]}"
                )
                assert docs[0].to_dict()["worker"] == worker
            """
        )
        result = pytester.runpytest(
            "-v", "-n", "2", "--firestore-port=0", "--dist=each"
        )
        result.assert_outcomes(passed=4)

    @skip_no_gcloud
    @skip_no_xdist
    @skip_no_firestore
    def test_worker_project_ids_are_unique(self, pytester: pytest.Pytester) -> None:
        """Each xdist worker should have a distinct project ID with worker suffix."""
        pytester.makepyfile(
            """
            import os
            import pytest

            @pytest.mark.parametrize("run", [1, 2])
            def test_project_has_worker_suffix(firestore_emulator, run):
                worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
                assert worker != "main", "Expected to run under xdist"

                # Project should end with worker ID
                assert firestore_emulator.project.endswith(f"-{worker}")
            """
        )
        result = pytester.runpytest(
            "-v", "-n", "2", "--firestore-port=0", "--dist=each"
        )
        result.assert_outcomes(passed=4)
