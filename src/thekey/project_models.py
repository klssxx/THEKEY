"""Data models for real-project intake (THEKEY Core 0.2.0).

These are plain, serializable value objects. They carry no execution logic and
never write to disk; the loader/profiler populate them and the coordinator
persists them as project-profile.json / source-baseline.json.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Supported detected profiles (section 11).
SUPPORTED_PROFILES = {
    "generic-python",
    "python-cli",
    "python-desktop",
    "python-web",
    "single-file-python",
    "dotnet-windows",
    "dotnet-console",
    "dotnet-library",
    "node-javascript",
    "rust-cargo",
    "go-module",
    "java-maven",
}

# Packaging / framework signal tables used by the profiler (section 11).
_PROFILE_SIGNALS: dict[str, dict[str, list[str]]] = {
    "python-cli": {
        "metadata_files": ["setup.py", "setup.cfg", "pyproject.toml"],
        "metadata_markers": [
            "[project.scripts]",
            "console_scripts",
        ],
        "imports": [
            "argparse",
            "click",
            "typer",
            "fire",
        ],
        "markers": [
            "def main(",
            "if __name__ ==",
            '__spec__.name == "__main__"',
            "entry_points",
        ],
    },
    "python-desktop": {
        "imports": [
            "PySide6",
            "PyQt6",
            "PyQt5",
            "tkinter",
            "customtkinter",
            "wx",
            "kivy",
        ],
        "markers": [
            "QApplication",
            "Tk()",
            "App()",
        ],
    },
    "python-web": {
        "imports": [
            "fastapi",
            "flask",
            "django",
            "starlette",
            "sanic",
        ],
        "markers": [
            "FastAPI(",
            "Flask(",
            "django.setup(",
            "Sanic(",
            "app = FastAPI",
            "application =",
        ],
    },
}


@dataclass
class ProjectInspection:
    """Result of the read-only intake scan (section 9/10)."""

    source_root: str
    access_mode: str = "READ_ONLY"
    git_detected: bool = False
    git_head: str | None = None
    git_dirty: bool = False
    git_status_text: str = ""
    included_file_count: int = 0
    excluded_dir_count: int = 0
    symlink_findings: list[str] = field(default_factory=list)
    reparse_findings: list[str] = field(default_factory=list)
    binary_files: list[str] = field(default_factory=list)
    canonical_hashes: dict[str, str] = field(default_factory=dict)
    baseline_tree_hash: str = ""
    metadata_files: list[str] = field(default_factory=list)
    detected_entrypoints: list[str] = field(default_factory=list)
    test_roots: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scan_limits: dict[str, Any] = field(default_factory=dict)
    file_inventory: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_root": self.source_root,
            "access_mode": self.access_mode,
            "git_detected": self.git_detected,
            "git_head": self.git_head,
            "git_dirty": self.git_dirty,
            "git_status_text": self.git_status_text,
            "included_file_count": self.included_file_count,
            "excluded_dir_count": self.excluded_dir_count,
            "symlink_findings": self.symlink_findings,
            "reparse_findings": self.reparse_findings,
            "binary_files": self.binary_files,
            "canonical_hashes": self.canonical_hashes,
            "baseline_tree_hash": self.baseline_tree_hash,
            "metadata_files": self.metadata_files,
            "detected_entrypoints": self.detected_entrypoints,
            "test_roots": self.test_roots,
            "warnings": self.warnings,
            "scan_limits": self.scan_limits,
            "file_inventory": self.file_inventory,
        }


@dataclass
class ProjectProfile:
    """Validated project-profile.json (section 11)."""

    project_id: str
    project_name: str
    source_root: str
    source_access: str = "READ_ONLY"
    language: str = "python"
    detected_profile: str = "generic-python"
    profile_confidence: float = 0.0
    profile_evidence: list[str] = field(default_factory=list)
    packaging: dict[str, Any] = field(default_factory=dict)
    entrypoints: list[str] = field(default_factory=list)
    test_configuration: dict[str, Any] = field(default_factory=dict)
    frameworks: list[str] = field(default_factory=list)
    python_requirement: str = ""
    git: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unsupported_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema_version": "1.0",
            "project_id": self.project_id,
            "project_name": self.project_name,
            "source_root": self.source_root,
            "source_access": "READ_ONLY",
            "language": self.language,
            "detected_profile": self.detected_profile,
            "profile_confidence": round(self.profile_confidence, 4),
            "profile_evidence": self.profile_evidence,
            "packaging": self.packaging,
            "entrypoints": self.entrypoints,
            "test_configuration": self.test_configuration,
            "frameworks": self.frameworks,
            "python_requirement": self.python_requirement,
            "git": self.git,
            "warnings": self.warnings,
            "unsupported_reasons": self.unsupported_reasons,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectProfile":
        return cls(
            project_id=d["project_id"],
            project_name=d["project_name"],
            source_root=d["source_root"],
            source_access=d.get("source_access", "READ_ONLY"),
            language=d.get("language", "python"),
            detected_profile=d.get("detected_profile", "generic-python"),
            profile_confidence=float(d.get("profile_confidence", 0.0)),
            profile_evidence=list(d.get("profile_evidence", [])),
            packaging=d.get("packaging", {}),
            entrypoints=list(d.get("entrypoints", [])),
            test_configuration=d.get("test_configuration", {}),
            frameworks=list(d.get("frameworks", [])),
            python_requirement=d.get("python_requirement", ""),
            git=d.get("git", {}),
            warnings=list(d.get("warnings", [])),
            unsupported_reasons=list(d.get("unsupported_reasons", [])),
        )


def compute_tree_hash(canonical_hashes: dict[str, str]) -> str:
    """Deterministic hash of the included file hash records (section 10).

    Sorting by relative path ensures the same files+contents always produce
    the same baseline_tree_hash regardless of traversal order.
    """
    import hashlib

    h = hashlib.sha256()
    for rel in sorted(canonical_hashes):
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(canonical_hashes[rel].encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def load_profile(path: Path) -> ProjectProfile:
    return ProjectProfile.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
