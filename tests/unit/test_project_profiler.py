"""Unit tests for the single-file-python profile detection (improvement E)."""

from pathlib import Path

import pytest

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


def test_winui_dotnet_project_is_detected_even_with_a_python_utility(tmp_path):
    (tmp_path / "App.csproj").write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup>"
        "<TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>"
        "<UseWinUI>true</UseWinUI></PropertyGroup>"
        "<ItemGroup><PackageReference Include=\"Microsoft.WindowsAppSDK\" Version=\"2.3.1\" />"
        "</ItemGroup></Project>",
        encoding="utf-8",
    )
    (tmp_path / "gen_assets.py").write_text("print('utility')\n", encoding="utf-8")

    prof = profile_project(tmp_path)

    assert prof.detected_profile == "dotnet-windows"
    assert prof.language == "csharp"
    assert prof.profile_confidence >= 0.95


def test_node_manifest_is_recognized_as_a_supported_profile(tmp_path):
    (tmp_path / "package.json").write_text('{"name":"example"}\n', encoding="utf-8")
    (tmp_path / "index.js").write_text("console.log('ok');\n", encoding="utf-8")

    prof = profile_project(tmp_path)

    assert prof.detected_profile == "node-javascript"
    assert prof.language == "javascript"


@pytest.mark.parametrize(
    ("manifest", "source", "profile_name", "language"),
    [
        ("Cargo.toml", "[package]\nname='demo'\nversion='0.1.0'\n", "rust-cargo", "rust"),
        ("go.mod", "module example.com/demo\n\ngo 1.22\n", "go-module", "go"),
        ("pom.xml", "<project><modelVersion>4.0.0</modelVersion></project>", "java-maven", "java"),
    ],
)
def test_non_python_manifests_select_their_adapter(
    tmp_path, manifest, source, profile_name, language
):
    (tmp_path / manifest).write_text(source, encoding="utf-8")

    prof = profile_project(tmp_path)

    assert prof.detected_profile == profile_name
    assert prof.language == language
