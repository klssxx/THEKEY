from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRY_PATH = ROOT / "scripts" / "portable_entry.py"
LAUNCHER_PATH = ROOT / "portable" / "windows" / "TheKeyLauncher.cs"
LAUNCHER_MANIFEST_PATH = ROOT / "portable" / "windows" / "TheKeyLauncher.manifest"
PORTABLE_BUILD_PATH = ROOT / "scripts" / "build-portable.ps1"
HERO_PATH = ROOT / "portable" / "windows" / "assets" / "THEKEY_hero_chess.png"
ICON_PATH = ROOT / "portable" / "windows" / "assets" / "THEKEY_app_icon.png"
HOTSPOT_MAP_PATH = ROOT / "docs" / "build-week" / "PIXEL_PERFECT_HOTSPOTS.json"
PIXEL_VERIFIER_PATH = ROOT / "scripts" / "verify-pixel-ui.ps1"


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

    assert "Template = CreateCardTemplate()" in source
    assert "disabled = new Trigger { Property = UIElement.IsEnabledProperty, Value = false }" in source
    assert "disabled.Setters.Add(new Setter(UIElement.OpacityProperty, 0.68));" in source
    assert "Foreground = Theme.Brush(Theme.Text)" in source
    assert "Foreground = Theme.Brush(Theme.MutedText)" in source


def test_launcher_buttons_are_bilingual():
    source = LAUNCHER_PATH.read_text(encoding="utf-8")

    labels = (
        "Seleccionar y analizar / Select & Analyze",
        "Verificar / Verify",
        "Reparar / Repair",
        "Demo para jueces / Judge demo",
        "Ver resultados /\\nView results",
        "Resultados / Results",
        "Ajustes / Settings",
        "PRÓXIMAMENTE / SOON",
    )
    for label in labels:
        assert label in source


def test_premium_launcher_uses_native_adaptive_layout_and_real_activity_state():
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    build = PORTABLE_BUILD_PATH.read_text(encoding="utf-8")

    assert HERO_PATH.is_file()
    assert HERO_PATH.stat().st_size > 100_000
    assert ICON_PATH.is_file()
    assert ICON_PATH.stat().st_size > 100_000
    assert "BuildSidebar()" in launcher
    assert "BuildHero()" in launcher
    assert "BuildOperationCards()" in launcher
    assert "BuildActivityPanel()" in launcher
    assert "BuildSystemPanel()" not in launcher
    assert "Sin actividad todavía / No activity yet" in launcher
    assert 'sourceHero = Join-Path $repoRoot' in build
    assert 'sourceIcon = Join-Path $repoRoot' in build
    assert "sourceVideo" not in build
    assert "cinematic_sha256" not in build
    assert "Copy-Item -LiteralPath $sourceHero -Destination $packageRoot" in build
    assert "Copy-Item -LiteralPath $sourceIcon -Destination $packageRoot" in build
    assert "-Filter '__pycache__'" in build
    assert "SystemParameters.WorkArea" in launcher
    assert "WindowStartupLocation.CenterScreen" in launcher
    assert "BuildShell()" in launcher
    assert "ResizeMode = ResizeMode.CanResize" in launcher
    assert 'CreateUpcomingCard("THE KING"' in launcher
    assert "ShowModes" in launcher
    assert "ACTIVIDAD RECIENTE / RECENT ACTIVITY" in launcher
    assert "REPAIR_READY" in launcher
    assert "apply-consent apply_verified_repairs" in launcher
    assert "Reiniciar demo / Restart demo" in launcher
    assert "Cancelar operación aislada / Cancel isolated operation" in launcher
    assert 'Arguments = "/PID " + processId + " /T /F"' in launcher


def test_native_dashboard_scales_real_controls_without_a_screenshot_dependency():
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
    build = PORTABLE_BUILD_PATH.read_text(encoding="utf-8")
    assert "THEKEY_UI_REFERENCE.png" not in launcher
    assert "Viewbox scaler" in launcher
    assert "Child = rootGrid" in launcher
    assert "Stretch = Stretch.Uniform" in launcher
    assert "CaptureComposition(canonicalShell, 1448, 1086, capturePath, captureDpi)" in launcher
    assert "TheKeyLauncher.manifest" in build
    assert '"/win32manifest:$launcherManifest"' in build
    assert "$sourceUiReference" not in build


def test_launcher_structures_real_results_and_streams_backend_progress():
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")

    assert "BuildEvidenceResultCard" in launcher
    assert "PROYECTO / PROJECT" in launcher
    assert "HALLAZGOS / FINDINGS" in launcher
    assert "DECISIÓN / DECISION" in launcher
    assert "EVIDENCIA / EVIDENCE" in launcher
    assert "BeginOutputReadLine" in launcher
    assert "BeginErrorReadLine" in launcher
    assert "ReadToEnd()" not in launcher
    assert "HandleWindowClosing" in launcher
    assert "TerminateProcessTree" in launcher


def test_portable_launcher_declares_per_monitor_dpi_awareness():
    manifest = LAUNCHER_MANIFEST_PATH.read_text(encoding="utf-8")

    assert "PerMonitorV2" in manifest
    assert "true/pm" in manifest


def test_native_visual_verifier_captures_the_adaptive_dashboard():
    verifier = PIXEL_VERIFIER_PATH.read_text(encoding="utf-8")

    assert "NATIVE_RENDER_CAPTURED" in verifier
    assert "native canonical dashboard composition" in verifier
    assert "the same native visual tree is rendered at the requested device-pixel density" in verifier
    assert "[ValidateSet(96, 120, 144, 192)]" in verifier
    assert "THEKEY_NATIVE_UI" not in verifier


def test_pixel_perfect_hotspots_cover_every_visible_action():
    mapping = json.loads(HOTSPOT_MAP_PATH.read_text(encoding="utf-8"))
    assert mapping["canvas"] == {"width": 1448, "height": 1086}
    expected = {
        "home",
        "analyze",
        "tools",
        "results",
        "modes",
        "logs",
        "settings",
        "select_analyze",
        "verify",
        "repair",
        "judge_demo",
        "view_results",
        "the_king",
        "checkmate",
    }
    regions = {region["id"]: region for region in mapping["regions"]}
    assert expected <= regions.keys()
    for region in mapping["regions"] + mapping["window_regions"]:
        assert region["width"] > 0 and region["height"] > 0
        assert 0 <= region["x"] < 1448
        assert 0 <= region["y"] < 1086
        assert region["x"] + region["width"] <= 1448
        assert region["y"] + region["height"] <= 1086
