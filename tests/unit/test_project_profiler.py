"""Unit tests for the single-file-python profile detection (improvement E)."""

from pathlib import Path

from thekey.project_profiler import profile_project


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_single_file_python_detected():
    prof = profile_project(FIXTURES / "single_file_app")
    assert prof.detected_profile == "single-file-python"
    assert prof.profile_confidence >= 0.85
    assert prof.language == "python"


def test_single_file_python_not_misclassified_as_generic():
    prof = profile_project(FIXTURES / "single_file_app")
    assert prof.detected_profile != "generic-python"


def test_cli_project_still_cli():
    # The pre-existing CLI fixture must still classify as python-cli.
    prof = profile_project(FIXTURES / "python_cli_project")
    assert prof.detected_profile == "python-cli"
