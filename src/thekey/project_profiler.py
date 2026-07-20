"""Project profiler: detect supported Python and Windows .NET profiles.

Detection is conservative and evidence-based. It does NOT classify from a single
filename. Confidence drives the decision:
  >= 0.85  -> recommend one profile
  0.60-0.85 -> ambiguous but supported; require explicit user selection
  < 0.60    -> UNSUPPORTED_PROJECT_PROFILE (exit 6) unless an explicit
               compatible profile is supplied and validates.

Mixed incompatible signals (e.g. both a GUI framework and a web framework with
conflicting entrypoints and no clear dominant) are not guessed: they return
UNSUPPORTED_PROJECT_PROFILE.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .errors import UnsupportedProjectProfileError
from .project_loader import inspect_project
from .project_models import (
    _PROFILE_SIGNALS,
    SUPPORTED_PROFILES,
    ProjectInspection,
    ProjectProfile,
)

# Non-Python / unsupported signal files.
_UNSUPPORTED_MARKERS = [
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
]


def _recognized_non_python_profile(
    inspection: ProjectInspection, root: Path
) -> ProjectProfile | None:
    """Return supported profile records for non-Python local projects."""
    names = {Path(rel).name for rel in inspection.canonical_hashes}
    markers = {
        "package.json": ("javascript", "Node.js / JavaScript", "node-javascript"),
        "Cargo.toml": ("rust", "Rust / Cargo", "rust-cargo"),
        "go.mod": ("go", "Go module", "go-module"),
        "pom.xml": ("java", "Java / Maven", "java-maven"),
    }
    for marker, (language, label, profile_name) in markers.items():
        if marker not in names:
            continue
        text = _read_text_safe(root / marker)
        test_configuration: dict[str, object] = {"test_roots": inspection.test_roots}
        if marker == "package.json":
            try:
                package = json.loads(text)
                scripts = package.get("scripts", {})
                scripts = scripts if isinstance(scripts, dict) else {}
            except json.JSONDecodeError:
                scripts = {}
            test_configuration.update({
                "has_test_script": isinstance(scripts.get("test"), str),
                "has_build_script": isinstance(scripts.get("build"), str),
            })
        elif marker == "Cargo.toml":
            test_configuration["has_tests"] = any(
                Path(rel).parts[0] == "tests" or "#[test]" in _read_text_safe(root / rel)
                for rel in inspection.canonical_hashes if rel.endswith(".rs")
            )
        elif marker == "go.mod":
            test_configuration["has_tests"] = any(
                Path(rel).name.endswith("_test.go") for rel in inspection.canonical_hashes
            )
        else:
            test_configuration["has_tests"] = any(
                str(Path(rel)).replace("\\", "/").startswith("src/test/")
                for rel in inspection.canonical_hashes
            )
        return ProjectProfile(
            project_id=_project_id(root),
            project_name=root.name,
            source_root=str(root),
            language=language,
            detected_profile=profile_name,
            profile_confidence=0.98,
            profile_evidence=[f"{marker}: recognized {label} manifest"],
            packaging={"manifest": marker},
            test_configuration=test_configuration,
            git={
                "detected": inspection.git_detected,
                "head": inspection.git_head,
                "dirty": inspection.git_dirty,
            },
            warnings=list(inspection.warnings),
        )
    return None


def _dotnet_profile(inspection: ProjectInspection, root: Path) -> ProjectProfile | None:
    """Return a high-confidence .NET profile when a project file proves it.

    This is intentionally based on ``.csproj`` content rather than directory
    names.  A stray Python utility in a Windows application must not cause the
    application itself to be classified as a Python target.
    """
    projects = sorted(
        rel for rel in inspection.canonical_hashes
        if Path(rel).suffix.casefold() == ".csproj"
    )
    if not projects:
        return None
    primary = projects[0]
    text = _read_text_safe(root / primary)
    is_windows = bool(
        re.search(r"<TargetFrameworks?>[^<]*-windows", text, re.IGNORECASE)
        or re.search(r"<UseWinUI>\s*true\s*</UseWinUI>", text, re.IGNORECASE)
        or "Microsoft.WindowsAppSDK" in text
    )
    is_console = bool(
        re.search(r"<OutputType>\s*Exe\s*</OutputType>", text, re.IGNORECASE)
        or any(Path(rel).name == "Program.cs" for rel in inspection.canonical_hashes)
    )
    profile_name = (
        "dotnet-windows" if is_windows
        else "dotnet-console" if is_console
        else "dotnet-library"
    )
    frameworks = re.findall(r"<TargetFrameworks?>([^<]+)</TargetFrameworks?>", text)
    packages = re.findall(r'<PackageReference\s+Include="([^"]+)"', text)
    entrypoints = sorted(
        rel for rel in inspection.canonical_hashes
        if Path(rel).name in {"App.xaml", "Program.cs", "MainWindow.xaml"}
    )
    return ProjectProfile(
        project_id=_project_id(root),
        project_name=root.name,
        source_root=str(root),
        language="csharp",
        detected_profile=profile_name,
        profile_confidence=0.98,
        profile_evidence=[
            (
                f"{primary}: Windows target / WinUI application marker"
                if is_windows else f"{primary}: SDK-style .NET project"
            ),
            *[f"{primary}: target={value}" for value in frameworks[:3]],
        ],
        frameworks=sorted({"WinUI" if is_windows else ".NET", *packages}),
        entrypoints=entrypoints,
        test_configuration={
            "test_roots": inspection.test_roots,
            "project_files": projects,
            "test_projects": [
                rel for rel in projects
                if "test" in Path(rel).stem.casefold()
                or "Microsoft.NET.Test.Sdk" in _read_text_safe(root / rel)
            ],
            "build_command": "dotnet build --no-restore --configuration Release",
        },
        packaging={"csproj": primary, "target_frameworks": frameworks},
        git={
            "detected": inspection.git_detected,
            "head": inspection.git_head,
            "dirty": inspection.git_dirty,
        },
        warnings=list(inspection.warnings),
    )


def _read_text_safe(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def _scan_for_imports_and_markers(
    inspection: ProjectInspection, root: Path
) -> dict[str, dict]:
    """Collect evidence: which profile signals appear in source/metadata."""
    evidence: dict[str, dict] = {
        name: {"imports": [], "markers": [], "metadata_markers": []}
        for name in ("python-cli", "python-desktop", "python-web")
    }
    # Metadata markers (pyproject [project.scripts] / console_scripts).
    for rel in inspection.metadata_files:
        p = root / rel
        txt = _read_text_safe(p)
        for mk in _PROFILE_SIGNALS["python-cli"]["metadata_markers"]:
            if mk in txt:
                evidence["python-cli"]["metadata_markers"].append(f"{rel}:{mk}")
    # Source scanning for imports + markers.
    for rel, hsh in inspection.canonical_hashes.items():
        if not str(rel).endswith(".py"):
            continue
        p = root / rel
        txt = _read_text_safe(p)
        for profile, table in _PROFILE_SIGNALS.items():
            for imp in table.get("imports", []):
                pat = re.compile(rf"(^|\n)\s*import\s+{re.escape(imp)}\b|from\s+{re.escape(imp)}\b")
                if pat.search(txt):
                    evidence[profile]["imports"].append(f"{rel}:import:{imp}")
            for mk in table.get("markers", []):
                if mk in txt:
                    evidence[profile]["markers"].append(f"{rel}:marker:{mk}")
    return evidence


def _score(evidence: dict) -> dict[str, float]:
    """Heuristic confidence 0..1 per supported profile (not a probability).

    Signal-driven: a single clear framework import is a strong, high-confidence
    signal. Metadata markers ([project.scripts]) are definitive for CLI.
    """
    scores: dict[str, float] = {}
    for profile, ev in evidence.items():
        s = 0.0
        if profile == "python-cli":
            if ev["metadata_markers"]:
                s = 0.95
            elif ev["imports"]:
                s = 0.85
            elif ev["markers"]:
                s = 0.70
        else:  # python-desktop / python-web
            if ev["imports"]:
                s = 0.92
            elif ev["markers"]:
                s = 0.75
        scores[profile] = min(1.0, s)
    # generic-python baseline only when no specialized signal.
    specialized = max(scores.values()) if scores else 0.0
    scores["generic-python"] = 0.55 if specialized < 0.6 else 0.0
    return scores


def profile_project(
    source: str | Path,
    *,
    explicit_profile: str | None = None,
    scan_limits: dict | None = None,
) -> ProjectProfile:
    root = Path(source).expanduser().resolve()
    inspection = inspect_project(root, scan_limits)
    dotnet_profile = _dotnet_profile(inspection, root)
    if dotnet_profile is not None:
        return dotnet_profile
    recognized_non_python = _recognized_non_python_profile(inspection, root)
    if recognized_non_python is not None:
        return recognized_non_python
    evidence = _scan_for_imports_and_markers(inspection, root)
    scores = _score(evidence)

    # Unsupported marker: a clearly non-Python project with no Python signals.
    has_python = any(
        str(rel).endswith(".py") for rel in inspection.canonical_hashes
    )
    non_python = [m for m in _UNSUPPORTED_MARKERS
                  if any(Path(rel).name == m for rel in inspection.canonical_hashes)]
    # Single-file / loose Python: one or more .py files with NO packaging
    # metadata and NO specialized framework signals => single-file-python.
    # Detected early so it is not misclassified as generic-python.
    has_packaging = any(
        Path(rel).name in ("pyproject.toml", "setup.py", "setup.cfg")
        for rel in inspection.canonical_hashes
    )
    specialized_signal = any(
        any(imp in _read_text_safe(root / rel)
            for table in _PROFILE_SIGNALS.values()
            for imp in table.get("imports", []))
        for rel in inspection.canonical_hashes
        if str(rel).endswith(".py")
    ) or any(
        any(mk in _read_text_safe(root / rel)
            for table in _PROFILE_SIGNALS.values()
            for mk in table.get("markers", []))
        for rel in inspection.canonical_hashes
        if str(rel).endswith(".py")
    )
    if has_python and not has_packaging and not specialized_signal and not non_python:
        return ProjectProfile(
            project_id=_project_id(root),
            project_name=root.name,
            source_root=str(root),
            detected_profile="single-file-python",
            profile_confidence=0.90,
            profile_evidence=[
                f"{n} python file(s) without packaging metadata"
                for n in [
                    str(sum(
                        1 for r in inspection.canonical_hashes
                        if str(r).endswith(".py")
                    ))
                ]
            ][:1],
            entrypoints=inspection.detected_entrypoints,
            test_configuration={"test_roots": inspection.test_roots},
            git={
                "detected": inspection.git_detected,
                "head": inspection.git_head,
                "dirty": inspection.git_dirty,
            },
            warnings=list(inspection.warnings),
            packaging={},
        )

    if non_python and not has_python:
        prof = ProjectProfile(
            project_id=_project_id(root),
            project_name=root.name,
            source_root=str(root),
            detected_profile="unsupported",
            unsupported_reasons=[
                f"Non-Python project markers detected: {non_python}",
                "No Python sources found.",
            ],
        )
        if explicit_profile in SUPPORTED_PROFILES:
            # User insists; allow only if at least one Python file exists.
            if has_python:
                prof.detected_profile = explicit_profile
                prof.unsupported_reasons = []
            else:
                raise UnsupportedProjectProfileError(
                    "Explicit profile requested but no Python sources present."
                )
        else:
            raise UnsupportedProjectProfileError(
                "Target is not a recognizable Python project: "
                + "; ".join(prof.unsupported_reasons)
            )
        return prof

    # Determine best supported profile (excluding unsupported branch).
    ranked = sorted(
        ((p, s) for p, s in scores.items() if p in SUPPORTED_PROFILES),
        key=lambda kv: kv[1], reverse=True,
    )
    best_profile, best_score = (ranked[0] if ranked else ("generic-python", 0.0))

    # Ambiguity: two supported profiles within 0.1 of each other and both >=0.6.
    ambiguous = False
    if len(ranked) >= 2:
        top, second = ranked[0][1], ranked[1][1]
        if second >= 0.60 and (top - second) < 0.10:
            ambiguous = True

    if explicit_profile:
        if explicit_profile not in SUPPORTED_PROFILES:
            raise UnsupportedProjectProfileError(
                f"Explicit profile {explicit_profile!r} is not supported."
            )
        # Explicit compatible override wins (validated as compatible: it must
        # not contradict a clearly-opposed signal, but we accept user choice).
        chosen = explicit_profile
        conf = float(scores.get(chosen, 0.0))
        if conf < 0.60:
            # Allow but record warning; user takes responsibility.
            pass
    elif best_score >= 0.85 and not ambiguous:
        chosen = best_profile
        conf = best_score
    elif ambiguous or 0.60 <= best_score < 0.85:
        # Ambiguous but supported -> require explicit selection later.
        chosen = best_profile
        conf = best_score
    else:
        # < 0.60 and no explicit override -> unsupported.
        if not has_python:
            raise UnsupportedProjectProfileError(
                "Target is not a recognizable Python project (no signals)."
            )
        chosen = "generic-python"
        conf = max(best_score, 0.50)

    # Build profile evidence list.
    ev_list: list[str] = []
    for k, v in evidence.get(chosen, {}).items():
        ev_list.extend(v[:5])

    frameworks = sorted({
        imp.split(":")[-1]
        for imp in evidence.get(chosen, {}).get("imports", [])
    })

    return ProjectProfile(
        project_id=_project_id(root),
        project_name=root.name,
        source_root=str(root),
        detected_profile=chosen,
        profile_confidence=conf,
        profile_evidence=ev_list[:20],
        frameworks=frameworks,
        entrypoints=inspection.detected_entrypoints,
        test_configuration={"test_roots": inspection.test_roots},
        git={
            "detected": inspection.git_detected,
            "head": inspection.git_head,
            "dirty": inspection.git_dirty,
        },
        warnings=list(inspection.warnings),
        packaging=_detect_packaging(inspection, root),
    )


def _detect_packaging(inspection: ProjectInspection, root: Path) -> dict:
    pkg = {}
    for rel in inspection.metadata_files:
        if Path(rel).name == "pyproject.toml":
            txt = _read_text_safe(root / rel)
            if "[project]" in txt:
                pkg["pyproject_project"] = True
            if "[build-system]" in txt:
                pkg["build_system"] = True
        if Path(rel).name == "setup.py":
            pkg["setup_py"] = True
        if Path(rel).name == "setup.cfg":
            pkg["setup_cfg"] = True
    return pkg


def _project_id(root: Path) -> str:
    import hashlib

    h = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:12]
    return f"PROJECT-{root.name.upper().replace('-', '_')[:20]}-{h[:6]}"
