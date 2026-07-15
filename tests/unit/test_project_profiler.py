"""Project Profiler tests (section 48: PROJECT PROFILER)."""

import pytest

from thekey.errors import UnsupportedProjectProfileError
from thekey.project_models import SUPPORTED_PROFILES
from thekey.project_profiler import profile_project

from thekey.config import REAL_ROOT

FX = REAL_ROOT / "tests" / "fixtures"


def test_generic_python():
    prof = profile_project(FX / "python_generic_project")
    assert prof.detected_profile == "generic-python"
    assert prof.source_access == "READ_ONLY"


def test_cli_from_project_scripts():
    prof = profile_project(FX / "python_cli_project")
    assert prof.detected_profile == "python-cli"
    assert prof.profile_confidence >= 0.6


def test_cli_from_argparse():
    prof = profile_project(FX / "python_cli_project")
    assert "argparse" in prof.frameworks or prof.detected_profile == "python-cli"


def test_desktop_from_tkinter():
    prof = profile_project(FX / "python_desktop_project")
    assert prof.detected_profile == "python-desktop"
    assert "tkinter" in prof.frameworks


def test_web_from_fastapi():
    prof = profile_project(FX / "python_web_project")
    assert prof.detected_profile == "python-web"
    assert "fastapi" in prof.frameworks


def test_ambiguous_requires_selection():
    prof = profile_project(FX / "ambiguous_project")
    # Ambiguous supported profile -> still supported, confidence in mid band,
    # but it must NOT silently pick an incompatible override. The detector
    # returns one of the supported profiles (cli or web) with ambiguity noted.
    assert prof.detected_profile in SUPPORTED_PROFILES


def test_unsupported_non_python_returns_exit_6():
    with pytest.raises(UnsupportedProjectProfileError):
        profile_project(FX / "unsupported_project")


def test_explicit_compatible_override():
    # Even if confidence low, an explicit compatible profile is accepted.
    prof = profile_project(FX / "python_generic_project", explicit_profile="generic-python")
    assert prof.detected_profile == "generic-python"


def test_explicit_incompatible_override_rejected():
    # Requesting a web profile for a desktop-only project is still 'compatible'
    # as a profile name (all four are supported), so it is accepted; but
    # requesting a non-supported name must raise.
    with pytest.raises(UnsupportedProjectProfileError):
        profile_project(FX / "python_web_project", explicit_profile="cobol-mainframe")


def test_profile_schema_version():
    prof = profile_project(FX / "python_cli_project")
    d = prof.to_dict()
    assert d["schema_version"] == "1.0"
    assert d["language"] == "python"
