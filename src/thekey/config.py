"""Resolved repository paths and global constants.

Paths are derived from the package location so the engine works both from a
source checkout and from an installed wheel. No path here points at the
protected historical THEKEY framework.
"""

from __future__ import annotations

import os
from pathlib import Path

# Root of this repository (src/thekey/config.py -> parents[2] = repo root)
REPO_ROOT = Path(__file__).resolve().parents[2]

# Source tree.
SRC_ROOT = REPO_ROOT / "src"
THEKEY_PKG = SRC_ROOT / "thekey"

# Governance artifacts.
GOVERNANCE_ROOT = REPO_ROOT / "governance"
POLICIES_DIR = GOVERNANCE_ROOT / "policies"
SCHEMAS_DIR = GOVERNANCE_ROOT / "schemas"

# Prompts / kernel.
PROMPTS_DIR = REPO_ROOT / "prompts"
SYSTEM_KERNEL_FILE = PROMPTS_DIR / "system-kernel.txt"
CYCLE_PROTOCOL_FILE = PROMPTS_DIR / "cycle-protocol.txt"
CONTEXT_TEMPLATE_FILE = PROMPTS_DIR / "context-template.txt"

# Phase contracts.
PHASES_DIR = REPO_ROOT / "phases"

# Runtime artifact roots.
RUNS_DIR = REPO_ROOT / "runs"
WORKSPACES_DIR = REPO_ROOT / "workspaces"

# Default policy used by the canonical demo.
DEFAULT_POLICY_ID = "local-python-demo"
DEFAULT_POLICY_FILE = POLICIES_DIR / "local-python-demo.yaml"

# Schema files.
POLICY_SCHEMA_FILE = SCHEMAS_DIR / "policy.schema.json"
PHASE_CONTRACT_SCHEMA_FILE = SCHEMAS_DIR / "phase-contract.schema.json"
OPERATOR_TURN_SCHEMA_FILE = SCHEMAS_DIR / "operator-turn.schema.json"

# Example demo app (intentionally contains a defect in the ORIGINAL file; it
# must never be modified by any run).
DEMO_APP_DIR = REPO_ROOT / "examples" / "demo_app"
DEMO_APP_SOURCE = DEMO_APP_DIR / "calculator.py"

# MVP release version.
VERSION = "0.1.0"

# Environment override hook (mainly for tests).
def _env_path(name: str, default: Path) -> Path:
    val = os.environ.get(name)
    if val:
        return Path(val).resolve()
    return default


RUNS_DIR = _env_path("THEKEY_RUNS_DIR", RUNS_DIR)
WORKSPACES_DIR = _env_path("THEKEY_WORKSPACES_DIR", WORKSPACES_DIR)
REPO_ROOT = _env_path("THEKEY_REPO_ROOT", REPO_ROOT)
