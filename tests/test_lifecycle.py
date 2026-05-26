from __future__ import annotations

from pathlib import Path

from sqlmesh_specify.lifecycle import validate_lifecycle
from tests.conftest import write_lifecycle


def _codes(root: Path) -> set[str]:
    return {finding.code for finding in validate_lifecycle(root).findings}


def test_exact_valid_statuses_pass(tmp_path: Path) -> None:
    write_lifecycle(tmp_path)
    assert validate_lifecycle(tmp_path).error_count == 0


def test_disapproved_spec_does_not_allow_plan(tmp_path: Path) -> None:
    write_lifecycle(tmp_path, spec_status="disapproved")
    codes = _codes(tmp_path)
    assert "SPEC_STATUS_INVALID" in codes
    assert "PLAN_BEFORE_SPEC_APPROVAL" in codes


def test_unapproved_plan_does_not_allow_tasks(tmp_path: Path) -> None:
    write_lifecycle(tmp_path, plan_status="unapproved")
    codes = _codes(tmp_path)
    assert "PLAN_STATUS_INVALID" in codes
    assert "TASKS_BEFORE_PLAN_APPROVAL" in codes


def test_not_approved_plan_does_not_allow_tasks(tmp_path: Path) -> None:
    write_lifecycle(tmp_path, plan_status="not approved")
    codes = _codes(tmp_path)
    assert "PLAN_STATUS_INVALID" in codes
    assert "TASKS_BEFORE_PLAN_APPROVAL" in codes


def test_missing_statuses_are_explicit(tmp_path: Path) -> None:
    write_lifecycle(tmp_path, spec_status=None, plan_status=None, tasks_status=None)
    codes = _codes(tmp_path)
    assert {"SPEC_STATUS_MISSING", "PLAN_STATUS_MISSING", "TASKS_STATUS_MISSING"} <= codes


def test_missing_ac_traceability_fails(tmp_path: Path) -> None:
    spec_dir = write_lifecycle(tmp_path)
    (spec_dir / "tasks.md").write_text(
        "**Status:** in progress\n\n## Task list\n\n- [ ] T-01 - Work.\n"
    )
    assert "AC_NOT_TRACED" in _codes(tmp_path)
