"""Validate sqlmesh-spec-kit lifecycle artifacts."""
from __future__ import annotations

import re
from pathlib import Path

from sqlmesh_specify.ears import classify_ears
from sqlmesh_specify.reporting import Finding, ValidationReport
from sqlmesh_specify.validate import _extract_ac_lines

_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(?P<status>.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_AC_ID_RE = re.compile(r"\bAC(?P<num>\d+[A-Za-z]?)\b")
_REQUIRED_PLAN_SECTIONS = (
    "## Architecture",
    "## Files to add",
    "## Files to modify",
    "## Files to delete",
    "## Tests",
    "## Downstream impact",
)
_SPEC_STATUSES = frozenset({"draft", "approved", "shipped", "superseded"})
_PLAN_STATUSES = frozenset({"proposed", "approved", "superseded"})
_TASKS_STATUSES = frozenset({"in progress", "done"})
_SPEC_STATUSES_ALLOWING_PLAN = frozenset({"approved", "shipped"})
_PLAN_STATUSES_ALLOWING_TASKS = frozenset({"approved"})


def validate_lifecycle(target_dir: Path) -> ValidationReport:
    """Validate spec -> plan -> tasks traceability for a SQLMesh project."""
    findings: list[Finding] = []
    specs_dir = target_dir / "specs"
    if not specs_dir.exists():
        return ValidationReport(
            "sqlmesh-specify project validation",
            (
                Finding(
                    "warning",
                    "PROJECT_NO_SPECS_DIR",
                    "No specs/ directory found. Run `sqlmesh-specify init` before using the "
                    "enterprise workflow.",
                    relpath(specs_dir, target_dir),
                ),
            ),
        )

    spec_dirs = sorted(path for path in specs_dir.iterdir() if path.is_dir())
    if not spec_dirs:
        findings.append(
            Finding(
                "warning",
                "PROJECT_NO_SPECS",
                "specs/ exists but contains no feature specs yet.",
                relpath(specs_dir, target_dir),
            )
        )

    for spec_dir in spec_dirs:
        findings.extend(_validate_spec_dir(spec_dir, target_dir))

    return ValidationReport("sqlmesh-specify project validation", tuple(findings))


def _validate_spec_dir(spec_dir: Path, target_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    spec_path = spec_dir / "spec.md"
    plan_path = spec_dir / "plan.md"
    tasks_path = spec_dir / "tasks.md"

    if not spec_path.exists():
        return [
            Finding(
                "error",
                "SPEC_MISSING",
                "Spec directory is missing spec.md.",
                relpath(spec_path, target_dir),
            )
        ]

    spec_text = spec_path.read_text()
    ac_lines = _extract_ac_lines(spec_text)
    ac_ids = _extract_referenced_ac_ids(spec_text)
    spec_status = _read_status(spec_text)
    findings.extend(
        _validate_status(
            status=spec_status,
            allowed_statuses=_SPEC_STATUSES,
            missing_code="SPEC_STATUS_MISSING",
            invalid_code="SPEC_STATUS_INVALID",
            artifact_name="spec.md",
            path=spec_path,
            target_dir=target_dir,
        )
    )

    if not ac_lines:
        findings.append(
            Finding(
                "error",
                "SPEC_NO_ACCEPTANCE_CRITERIA",
                "spec.md has no Acceptance Criteria section.",
                relpath(spec_path, target_dir),
            )
        )
    for line_no, line in ac_lines:
        if classify_ears(line) is None:
            findings.append(
                Finding(
                    "error",
                    "SPEC_NON_EARS_AC",
                    f"Acceptance criterion on line {line_no} is not EARS-formatted.",
                    relpath(spec_path, target_dir),
                )
            )
    if ac_lines and not ac_ids:
        findings.append(
            Finding(
                "warning",
                "SPEC_UNLABELED_ACS",
                "Acceptance criteria should use stable AC ids such as AC1, AC2, AC3.",
                relpath(spec_path, target_dir),
            )
        )

    if plan_path.exists():
        findings.extend(_validate_plan(plan_path, spec_status, ac_ids, target_dir))
    if tasks_path.exists():
        findings.extend(_validate_tasks(tasks_path, plan_path, ac_ids, target_dir))

    return findings


def _validate_plan(
    plan_path: Path,
    spec_status: str | None,
    ac_ids: set[str],
    target_dir: Path,
) -> list[Finding]:
    findings: list[Finding] = []
    plan_text = plan_path.read_text()
    plan_status = _read_status(plan_text)

    if not _status_allows(spec_status, _SPEC_STATUSES_ALLOWING_PLAN):
        findings.append(
            Finding(
                "error",
                "PLAN_BEFORE_SPEC_APPROVAL",
                "plan.md exists before spec.md is marked exactly `approved` or `shipped`.",
                relpath(plan_path, target_dir),
            )
        )
    findings.extend(
        _validate_status(
            status=plan_status,
            allowed_statuses=_PLAN_STATUSES,
            missing_code="PLAN_STATUS_MISSING",
            invalid_code="PLAN_STATUS_INVALID",
            artifact_name="plan.md",
            path=plan_path,
            target_dir=target_dir,
        )
    )
    for section in _REQUIRED_PLAN_SECTIONS:
        if section.lower() not in plan_text.lower():
            findings.append(
                Finding(
                    "error",
                    "PLAN_SECTION_MISSING",
                    f"plan.md is missing required section `{section}`.",
                    relpath(plan_path, target_dir),
                )
            )

    findings.extend(_validate_ac_traceability(ac_ids, plan_text, plan_path, target_dir, "plan.md"))
    return findings


def _validate_tasks(
    tasks_path: Path,
    plan_path: Path,
    ac_ids: set[str],
    target_dir: Path,
) -> list[Finding]:
    findings: list[Finding] = []
    tasks_text = tasks_path.read_text()
    plan_text = plan_path.read_text() if plan_path.exists() else ""
    plan_status = _read_status(plan_text)
    tasks_status = _read_status(tasks_text)

    if not plan_path.exists():
        findings.append(
            Finding(
                "error",
                "TASKS_WITHOUT_PLAN",
                "tasks.md exists before plan.md.",
                relpath(tasks_path, target_dir),
            )
        )
    elif not _status_allows(plan_status, _PLAN_STATUSES_ALLOWING_TASKS):
        findings.append(
            Finding(
                "error",
                "TASKS_BEFORE_PLAN_APPROVAL",
                "tasks.md exists before plan.md is marked exactly `approved`.",
                relpath(tasks_path, target_dir),
            )
        )
    findings.extend(
        _validate_status(
            status=tasks_status,
            allowed_statuses=_TASKS_STATUSES,
            missing_code="TASKS_STATUS_MISSING",
            invalid_code="TASKS_STATUS_INVALID",
            artifact_name="tasks.md",
            path=tasks_path,
            target_dir=target_dir,
        )
    )

    if "## Task list" not in tasks_text:
        findings.append(
            Finding(
                "error",
                "TASKS_SECTION_MISSING",
                "tasks.md must include a `## Task list` section.",
                relpath(tasks_path, target_dir),
            )
        )
    findings.extend(
        _validate_ac_traceability(ac_ids, tasks_text, tasks_path, target_dir, "tasks.md")
    )
    return findings


def _validate_ac_traceability(
    ac_ids: set[str],
    text: str,
    path: Path,
    target_dir: Path,
    artifact_name: str,
) -> list[Finding]:
    if not ac_ids:
        return []
    referenced = _extract_referenced_ac_ids(text)
    findings: list[Finding] = []
    for ac_id in sorted(ac_ids):
        if ac_id not in referenced:
            findings.append(
                Finding(
                    "error",
                    "AC_NOT_TRACED",
                    f"{artifact_name} does not reference {ac_id}.",
                    relpath(path, target_dir),
                )
            )
    return findings


def _validate_status(
    *,
    status: str | None,
    allowed_statuses: frozenset[str],
    missing_code: str,
    invalid_code: str,
    artifact_name: str,
    path: Path,
    target_dir: Path,
) -> list[Finding]:
    if status is None:
        return [
            Finding(
                "error",
                missing_code,
                f"{artifact_name} must include a `Status:` line.",
                relpath(path, target_dir),
            )
        ]
    if status not in allowed_statuses:
        allowed = ", ".join(f"`{value}`" for value in sorted(allowed_statuses))
        return [
            Finding(
                "error",
                invalid_code,
                f"{artifact_name} has invalid status `{status}`. Allowed statuses: {allowed}.",
                relpath(path, target_dir),
            )
        ]
    return []


def _read_status(text: str) -> str | None:
    match = _STATUS_RE.search(text)
    if match is None:
        return None
    return " ".join(match.group("status").strip().lower().split())


def _status_allows(status: str | None, allowed_statuses: frozenset[str]) -> bool:
    return status in allowed_statuses


def _extract_referenced_ac_ids(text: str) -> set[str]:
    return {f"AC{match.group('num')}" for match in _AC_ID_RE.finditer(text)}


def relpath(path: Path, base: Path) -> str:
    """Return a stable display path relative to the target project when possible."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)
