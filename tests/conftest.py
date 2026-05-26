from __future__ import annotations

import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def minimal_sqlmesh_project(tmp_path: Path) -> Path:
    src = ROOT / "tests" / "fixtures" / "minimal_sqlmesh_project"
    dst = tmp_path / "project"
    shutil.copytree(src, dst)
    return dst


def write_lifecycle(
    root: Path,
    *,
    spec_status: str | None = "approved",
    plan_status: str | None = "approved",
    tasks_status: str | None = "in progress",
) -> Path:
    spec_dir = root / "specs" / "001-demo"
    spec_dir.mkdir(parents=True)
    spec_status_line = f"**Status:** {spec_status}\n" if spec_status is not None else ""
    plan_status_line = f"**Status:** {plan_status}\n" if plan_status is not None else ""
    tasks_status_line = f"**Status:** {tasks_status}\n" if tasks_status is not None else ""
    (spec_dir / "spec.md").write_text(
        "# Demo\n\n"
        f"{spec_status_line}\n"
        "## Acceptance Criteria\n\n"
        "- AC1: When the model is queried, the system shall return one row per customer.\n"
    )
    (spec_dir / "plan.md").write_text(
        "# Plan\n\n"
        f"{plan_status_line}\n"
        "## Architecture\nAC1\n"
        "## Files to add\nAC1\n"
        "## Files to modify\nAC1\n"
        "## Files to delete\nAC1\n"
        "## Tests\nAC1\n"
        "## Downstream impact\nAC1\n"
    )
    (spec_dir / "tasks.md").write_text(
        "# Tasks\n\n"
        f"{tasks_status_line}\n"
        "## Task list\n\n"
        "- [ ] T-01 - Implement model.\n  - **Validates:** AC1\n"
    )
    return spec_dir
