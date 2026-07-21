from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRY_PATH = ROOT / "scripts" / "portable_entry.py"
LAUNCHER_PATH = ROOT / "portable" / "windows" / "TheKeyLauncher.cs"
PORTABLE_BUILD_PATH = ROOT / "scripts" / "build-portable.ps1"
HERO_PATH = ROOT / "portable" / "windows" / "assets" / "THEKEY_hero_chess.png"


def _load_entry():
    spec = importlib.util.spec_from_file_location("thekey_portable_entry", ENTRY_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_portable_entry_limits_embedded_module_execution():
    entry = _load_entry()
    assert entry._run_bounded_module(["-m", "not_allowed"]) == 2


def test_portable_evidence_verifier_rejects_printed_summary_without_artifacts(tmp_path):
    entry = _load_entry()
    evidence = {
        "judge_mode": "THEKEY Build Week Judge Mode",
        "allow": {"status": "APPLIED", "handler_call_count": 1},
        "deny": {
            "reason_code": "ROLE_NOT_ALLOWED",
            "handler_call_count": 0,
            "workspace_hash_unchanged": True,
        },
        "source": {"hash_unchanged": True},
        "receipt_binding": {
            "run_id_match": True,
            "transaction_id_match": True,
            "plan_sha256_match": True,
        },
        "production_reuse": False,
        "gates": [{"passed": True}] * 4,
        "release_decision": "RELEASE_ELIGIBLE",
        "run_path": str(tmp_path / "missing-run"),
        "run_id": "run-test",
        "transaction_id": "tx-test",
        "plan_sha256": "0" * 64,
    }
    path = tmp_path / "judge-mode-evidence.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")

    try:
        entry.verify_evidence(path)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("printed fields passed without persisted receipts")


def test_launcher_cards_keep_explicit_dark_contrast_when_disabled():
    source = LAUNCHER_PATH.read_text(encoding="utf-8")

    assert "button.Template = CreateCardTemplate();" in source
    assert "disabled.Property = UIElement.IsEnabledProperty;" in source
    assert "Color.FromRgb(24, 35, 58)" in source
    assert "heading.Foreground = Brushes.White;" in source
    assert "description.Foreground = new SolidColorBrush(Color.FromRgb(161, 176, 204));" in source


def test_launcher_buttons_are_bilingual():
    source = LAUNCHER_PATH.read_text(encoding="utf-8")

    labels = (
        "OMITIR / SKIP",
        "SELECCIONAR Y ANALIZAR / SELECT & ANALYZE",
        "Verificar / Verify",
        "Reparar / Repair",
        "Demo para jueces / Judge demo",
        "Ver resultados / View results",
        "Verificar evidencia / Verify evidence",
        "Ajustes / Settings",
        "Crear acceso / Create shortcut",
        "Ayuda CLI / CLI help",
        "PRÓXIMAMENTE / SOON",
    )
    for label in labels:
        assert label in source


def test_premium_launcher_uses_packaged_hero_and_real_activity_state():
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    build = PORTABLE_BUILD_PATH.read_text(encoding="utf-8")

    assert HERO_PATH.is_file()
    assert HERO_PATH.stat().st_size > 100_000
    assert "BuildSidebar()" in launcher
    assert "BuildHero()" in launcher
    assert "BuildSystemPanel()" in launcher
    assert "Sin actividad todavía / No activity yet" in launcher
    assert 'sourceHero = Join-Path $repoRoot' in build
    assert "Copy-Item -LiteralPath $sourceHero -Destination $packageRoot" in build
    assert "100%" not in launcher
