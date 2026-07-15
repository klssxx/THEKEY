"""Resolved repository paths and global constants.

Two roots are distinguished:
* REAL_ROOT  - the actual checkout (governance, schemas, prompts, source).
              Read-only assets used at runtime; never mutated by runs.
* RUNTIME_ROOT - where mutable run state lives (.thekey, runs/, workspaces/).
              Defaults to REAL_ROOT but can be redirected via the
              THEKEY_REPO_ROOT env var (used by the test suite for
              deterministic, isolated state).

No path here points at the protected historical THEKEY framework.
"""

from __future__ import annotations

import os
from pathlib import Path

# Real checkout root (src/thekey/config.py -> parents[2] = repo root).
REAL_ROOT = Path(__file__).resolve().parents[2]


def _env_path(name: str, default: Path) -> Path:
    val = os.environ.get(name)
    if val:
        return Path(val).resolve()
    return default


# Mutable runtime root (state + workspaces). Overridable for tests.
RUNTIME_ROOT = _env_path("THEKEY_REPO_ROOT", REAL_ROOT)

# Source tree (real checkout; the package itself is read-only at runtime).
SRC_ROOT = REAL_ROOT / "src"
THEKEY_PKG = SRC_ROOT / "thekey"

# Governance artifacts (real checkout).
GOVERNANCE_ROOT = REAL_ROOT / "governance"
POLICIES_DIR = GOVERNANCE_ROOT / "policies"
SCHEMAS_DIR = GOVERNANCE_ROOT / "schemas"

# Prompts / kernel (real checkout).
PROMPTS_DIR = REAL_ROOT / "prompts"
SYSTEM_KERNEL_FILE = PROMPTS_DIR / "system-kernel.txt"
CYCLE_PROTOCOL_FILE = PROMPTS_DIR / "cycle-protocol.txt"
CONTEXT_TEMPLATE_FILE = PROMPTS_DIR / "context-template.txt"

# Phase contracts (real checkout).
PHASES_DIR = REAL_ROOT / "phases"

# Runtime artifact roots (mutable; redirected in tests).
RUNS_DIR = RUNTIME_ROOT / "runs"
WORKSPACES_DIR = RUNTIME_ROOT / "workspaces"
THEKEY_DIR = RUNTIME_ROOT / ".thekey"

# Default policy used by the canonical demo.
DEFAULT_POLICY_ID = "local-python-demo"
DEFAULT_POLICY_FILE = POLICIES_DIR / "local-python-demo.yaml"

# Schema files (real checkout).
POLICY_SCHEMA_FILE = SCHEMAS_DIR / "policy.schema.json"
PHASE_CONTRACT_SCHEMA_FILE = SCHEMAS_DIR / "phase-contract.schema.json"
OPERATOR_TURN_SCHEMA_FILE = SCHEMAS_DIR / "operator-turn.schema.json"

# Example demo app (intentionally contains a defect in the ORIGINAL file; it
# must never be modified by any run).
DEMO_APP_DIR = REAL_ROOT / "examples" / "demo_app"
DEMO_APP_SOURCE = DEMO_APP_DIR / "calculator.py"

# MVP release version.
VERSION = "0.2.0"

# Backward-compatible alias: the pre-seeded 0.2.0 modules import REPO_ROOT.
REPO_ROOT = REAL_ROOT
