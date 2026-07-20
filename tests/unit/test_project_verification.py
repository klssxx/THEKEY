from __future__ import annotations

from pathlib import Path

import pytest

from thekey import project_loader, project_repair, project_verification
from thekey.policies import PolicyEngine

ROOT = Path(__file__).resolve().parents[2]
CLI_FIXTURE = ROOT / "tests" / "fixtures" / "python_cli_project"


def test_read_only_application_inspection_authorizes_supported_python(tmp_path):
    result = project_verification.inspect_application(
        CLI_FIXTURE,
        output=tmp_path / "inspection.json",
    )

    assert result["source"]["access_mode"] == "READ_ONLY"
    assert result["profile"]["detected_profile"] == "python-cli"
    assert result["checkmate_review"]["verdict"] == "PASS"
    assert result["policy_decision"]["allowed"] is True
    assert result["next_action"] == "VERIFY_ISOLATED_COPY_WITH_EXPLICIT_TEST_CONSENT"


def test_project_verification_requires_explicit_test_execution_consent():
    with pytest.raises(PermissionError, match="Explicit consent"):
        project_verification.verify_application(CLI_FIXTURE, consent="")


def test_dotnet_console_build_is_run_in_an_isolated_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "console-app"
    app.mkdir()
    (app / "ConsoleApp.csproj").write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup>"
        "<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>"
        "</PropertyGroup></Project>",
        encoding="utf-8",
    )
    (app / "Program.cs").write_text("Console.WriteLine(\"ok\");\n", encoding="utf-8")
    (app / "README.md").write_text("# Console app\n", encoding="utf-8")
    commands: list[list[str]] = []

    def successful_dotnet(command, workspace, **_kwargs):
        commands.append(command)
        return {
            "returncode": 0,
            "timed_out": False,
            "duration_ms": 1,
            "output_sha256": "0" * 64,
            "output_bytes": 0,
            "output_excerpt": "",
        }

    monkeypatch.setattr(project_verification, "_run_bounded_command", successful_dotnet)
    result = project_verification.verify_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert result["profile"]["detected_profile"] == "dotnet-console"
    assert result["final_verdict"] == "NO_VERIFICABLE"
    assert result["gates"][1]["gate"] == "DOTNET_BUILD_PASSED"
    assert commands[0][:2] == ["dotnet", "build"]


def test_dotnet_missing_runtime_reference_has_specific_diagnostic(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "broken-dotnet"
    app.mkdir()
    (app / "App.csproj").write_text(
        "<Project Sdk=\"Microsoft.NET.Sdk\"><PropertyGroup>"
        "<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>"
        "</PropertyGroup></Project>",
        encoding="utf-8",
    )
    (app / "Program.cs").write_text("Console.WriteLine(\"ok\");\n", encoding="utf-8")
    (app / "README.md").write_text("# Broken .NET app\n", encoding="utf-8")

    def failed_dotnet(*_args, **_kwargs):
        return {
            "returncode": 1,
            "timed_out": False,
            "duration_ms": 1,
            "output_sha256": "0" * 64,
            "output_bytes": 10,
            "output_excerpt": "error NETSDK1112: runtime reference missing",
        }

    monkeypatch.setattr(project_verification, "_run_bounded_command", failed_dotnet)
    result = project_verification.verify_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert result["final_verdict"] == "NO_VERIFICABLE"
    assert result["diagnostics"][0]["code"] == "DOTNET_RUNTIME_REFERENCE_MISSING"


@pytest.mark.parametrize(
    ("name", "files", "expected_command"),
    [
        (
            "node-app",
            {
                "package.json": (
                    '{"scripts":{"build":"node --check index.js",'
                    '"test":"node test.js"}}\n'
                ),
                "index.js": "console.log('ok');\n",
                "test.js": "process.exit(0);\n",
            },
            ["npm.cmd", "run", "build", "--if-present"],
        ),
        (
            "rust-app",
            {
                "Cargo.toml": "[package]\nname='demo'\nversion='0.1.0'\n",
                "src/lib.rs": "#[test]\nfn works() { assert!(true); }\n",
            },
            ["cargo", "check", "--offline"],
        ),
        (
            "go-app",
            {
                "go.mod": "module example.com/demo\n\ngo 1.22\n",
                "demo_test.go": "package demo\nfunc TestOk(t *testing.T) {}\n",
            },
            ["go", "test", "./..."],
        ),
        (
            "maven-app",
            {
                "pom.xml": "<project><modelVersion>4.0.0</modelVersion></project>",
                "src/test/java/DemoTest.java": "class DemoTest {}\n",
            },
            ["mvn", "--offline", "--quiet", "-DskipTests", "compile"],
        ),
    ],
)
def test_non_python_adapters_execute_only_fixed_commands(
    tmp_path, monkeypatch, name, files, expected_command
):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / name
    app.mkdir()
    for relative, content in files.items():
        target = app / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    (app / "README.md").write_text("# Adapter fixture\n", encoding="utf-8")
    commands: list[list[str]] = []

    def successful_command(command, workspace, **_kwargs):
        commands.append(command)
        return {
            "returncode": 0,
            "timed_out": False,
            "duration_ms": 1,
            "output_sha256": "0" * 64,
            "output_bytes": 0,
            "output_excerpt": "",
        }

    monkeypatch.setattr(project_verification, "_run_bounded_command", successful_command)
    result = project_verification.verify_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert result["final_verdict"] == "VERIFIED", result
    assert all(gate["passed"] for gate in result["gates"])
    assert commands[0] == expected_command


def test_project_verification_runs_in_copy_and_preserves_source(tmp_path, monkeypatch):
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / ".thekey")
    before = project_verification.inspect_project(CLI_FIXTURE).baseline_tree_hash

    result = project_verification.verify_application(
        CLI_FIXTURE,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    after = project_verification.inspect_project(CLI_FIXTURE).baseline_tree_hash
    assert result["final_verdict"] == "VERIFIED"
    assert all(gate["passed"] for gate in result["gates"])
    assert result["source"]["unchanged"] is True
    assert before == after
    assert Path(result["evidence_path"]).is_file()


def test_policy_denies_project_source_write():
    decision = PolicyEngine().authorize_project_verification({
        "source_tree_hash": "1" * 64,
        "profile": "python-cli",
        "access_mode": "READ_WRITE",
        "output_scope": "THEKEY_ISOLATED_VERIFICATION_ONLY",
        "checkmate_verdict": "PASS",
    })

    assert decision["allowed"] is False
    assert decision["reason_code"] == "PROJECT_SOURCE_WRITE_DENIED"


def test_generated_build_directories_are_excluded_from_inspection(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-do-not-use")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    (tmp_path / "main.py").write_text("print('source')\n", encoding="utf-8")
    generated = tmp_path / "bin" / "x64" / "publish"
    generated.mkdir(parents=True)
    (generated / "generated.py").write_text("print('generated')\n", encoding="utf-8")

    inspection = project_verification.inspect_project(tmp_path)

    assert "main.py" in inspection.canonical_hashes
    assert not any("generated.py" in path for path in inspection.canonical_hashes)
    assert inspection.excluded_dir_count == 1


def test_copy_failure_is_a_blocked_verdict_with_source_unchanged(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / ".thekey")

    def fail_copy(*_args, **_kwargs):
        raise OSError("simulated isolated-copy failure")

    monkeypatch.setattr(project_verification, "_copy_inspected_files", fail_copy)

    result = project_verification.verify_application(
        CLI_FIXTURE,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert result["final_verdict"] == "BLOCKED"
    assert result["gates"][0]["gate"] == "ISOLATED_COPY_CREATED"
    assert result["gates"][0]["passed"] is False
    assert result["source"]["unchanged"] is True
    assert Path(result["evidence_path"]).is_file()


def test_sibling_monorepo_tests_are_bound_and_run_in_isolated_layout(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path / "not-real-root")
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "sampleapp"
    (app / "src" / "sampleapp").mkdir(parents=True)
    (app / "src" / "sampleapp" / "__init__.py").write_text(
        "def answer(): return 42\n", encoding="utf-8"
    )
    (app / "src" / "sampleapp" / "main.py").write_text(
        "import argparse\n", encoding="utf-8"
    )
    (app / "README.md").write_text("# Sample\n", encoding="utf-8")
    (app / "pyproject.toml").write_text(
        "[project]\nname='sampleapp'\nversion='1'\n"
        "[project.scripts]\nsampleapp='sampleapp.main:main'\n",
        encoding="utf-8",
    )
    tests = tmp_path / "tests" / "sampleapp"
    tests.mkdir(parents=True)
    (tests / "conftest.py").write_text(
        "import sys\nfrom pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parents[2] / 'sampleapp' / 'src'))\n",
        encoding="utf-8",
    )
    (tests / "test_answer.py").write_text(
        "from sampleapp import answer\ndef test_answer(): assert answer() == 42\n",
        encoding="utf-8",
    )

    inspection = project_verification.inspect_application(app)
    result = project_verification.verify_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert inspection["inspection"]["external_tests"]["path"] == str(tests)
    assert result["final_verdict"] == "VERIFIED", result
    assert result["source"]["unchanged"] is True
    assert result["source"]["external_tests"]["unchanged"] is True


def test_failed_tests_produce_actionable_redacted_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "broken-app"
    app.mkdir()
    (app / "calculator.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (app / "test_calculator.py").write_text(
        "from calculator import add\n\n"
        "def test_add():\n"
        "    password = 'do-not-leak-this-value'\n"
        "    assert add(2, 3) == 5, f'password={password}'\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Broken app\n", encoding="utf-8")

    result = project_verification.verify_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
    )

    assert result["final_verdict"] == "BLOCKED"
    finding = next(item for item in result["diagnostics"] if item["code"] == "TEST_FAILURE")
    assert "test_calculator.py::test_add" in finding["failed_tests"]
    assert "do-not-leak-this-value" not in finding["evidence"]
    assert "password=<redacted>" in finding["evidence"]


def test_bounded_repair_applies_only_verified_change_and_keeps_backup(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "repairable-app"
    app.mkdir()
    source = app / "calculator.py"
    source.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    (app / "test_calculator.py").write_text(
        "from calculator import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Repairable app\n", encoding="utf-8")

    result = project_repair.repair_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
        max_candidates=10,
    )

    assert result["outcome"] == "REPAIRED_AND_VERIFIED", result
    assert source.read_text(encoding="utf-8") == "def add(a, b):\n    return a + b\n"
    assert result["repair"]["before"] == "-"
    assert result["repair"]["after"] == "+"
    assert result["repair_policy_decision"]["allowed"] is True
    assert result["post_apply_verification"]["verdict"] == "VERIFIED"
    assert Path(result["backup_path"]).read_text(encoding="utf-8").endswith(
        "return a - b\n"
    )


def test_verified_project_needs_no_repair_and_is_not_modified(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    before = project_verification.inspect_project(CLI_FIXTURE).baseline_tree_hash

    result = project_repair.repair_application(
        CLI_FIXTURE,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
    )

    assert result["outcome"] == "NO_CHANGES_NEEDED"
    assert result["source_changed"] is False
    assert project_verification.inspect_project(CLI_FIXTURE).baseline_tree_hash == before


def test_policy_denies_repair_that_has_not_passed_verification():
    decision = PolicyEngine().authorize_verified_project_repair({
        "source_tree_hash": "1" * 64,
        "profile": "python-cli",
        "checkmate_verdict": "PASS",
        "access_mode": "APPLY_VERIFIED_CHANGE",
        "output_scope": "SINGLE_FILE_DETERMINISTIC_MUTATION",
        "repair_sha256": "2" * 64,
        "changed_files": ["src/app.py"],
        "verification_verdict": "BLOCKED",
    })

    assert decision["allowed"] is False
    assert decision["reason_code"] == "UNVERIFIED_PROJECT_REPAIR_DENIED"


def test_bounded_repair_fixes_missing_block_colon(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "syntax-app"
    app.mkdir()
    source = app / "answer.py"
    source.write_text("def answer()\n    return 42\n", encoding="utf-8")
    (app / "test_answer.py").write_text(
        "from answer import answer\n\ndef test_answer(): assert answer() == 42\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Syntax app\n", encoding="utf-8")

    result = project_repair.repair_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
        max_candidates=10,
    )

    assert result["outcome"] == "REPAIRED_AND_VERIFIED", result
    assert source.read_text(encoding="utf-8").startswith("def answer():\n")
    assert result["repair"]["strategy"] == "MISSING_BLOCK_COLON"


def test_bounded_repair_fixes_a_proven_literal_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "literal-app"
    app.mkdir()
    source = app / "enabled.py"
    source.write_text("def enabled():\n    return 0\n", encoding="utf-8")
    (app / "test_enabled.py").write_text(
        "from enabled import enabled\n\ndef test_enabled(): assert enabled() == 1\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Literal app\n", encoding="utf-8")

    result = project_repair.repair_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
        max_candidates=10,
    )

    assert result["outcome"] == "REPAIRED_AND_VERIFIED", result
    assert source.read_text(encoding="utf-8").endswith("return 1\n")
    assert result["repair"]["strategy"] == "SINGLE_LITERAL_BOUNDARY_MUTATION"


def test_bounded_repair_fixes_a_proven_missing_closing_delimiter(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "delimiter-app"
    app.mkdir()
    source = app / "answer.py"
    source.write_text("def answer():\n    return (40 + 2\n", encoding="utf-8")
    (app / "test_answer.py").write_text(
        "from answer import answer\n\ndef test_answer(): assert answer() == 42\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Delimiter app\n", encoding="utf-8")

    result = project_repair.repair_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
        max_candidates=10,
    )

    assert result["outcome"] == "REPAIRED_AND_VERIFIED", result
    assert source.read_text(encoding="utf-8").endswith("2\n)\n")
    assert result["repair"]["strategy"] == "MISSING_CLOSING_DELIMITER"


def test_failed_post_apply_verification_rolls_source_back(tmp_path, monkeypatch):
    monkeypatch.setattr(project_loader, "THEKEY_DIR", tmp_path / "runtime-guard")
    monkeypatch.setattr(project_loader, "REAL_ROOT", tmp_path.parent / "not-real-root")
    monkeypatch.setattr(project_verification, "THEKEY_DIR", tmp_path / "runtime")
    monkeypatch.setattr(project_repair, "THEKEY_DIR", tmp_path / "runtime")
    app = tmp_path / "rollback-app"
    app.mkdir()
    source = app / "calculator.py"
    original = "def add(a, b):\n    return a - b\n"
    source.write_text(original, encoding="utf-8")
    (app / "test_calculator.py").write_text(
        "from calculator import add\n\ndef test_add(): assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    (app / "README.md").write_text("# Rollback app\n", encoding="utf-8")
    real_verify = project_verification.verify_application
    calls = 0

    def fail_second_verification(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_verify(*args, **kwargs)
        return {"final_verdict": "BLOCKED"}

    monkeypatch.setattr(project_repair, "verify_application", fail_second_verification)

    result = project_repair.repair_application(
        app,
        consent=project_verification.PROJECT_TEST_CONSENT,
        apply_consent=project_repair.PROJECT_REPAIR_APPLY_CONSENT,
        max_candidates=10,
    )

    assert result["outcome"] == "ROLLED_BACK"
    assert result["rollback_performed"] is True
    assert result["rollback_verified"] is True
    assert result["source_changed"] is False
    assert source.read_text(encoding="utf-8") == original
