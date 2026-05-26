"""Brownfield onboarding diagnostics for SQLMesh projects."""
from __future__ import annotations

from pathlib import Path

from sqlmesh_specify.lifecycle import relpath
from sqlmesh_specify.reporting import Finding, ValidationReport
from sqlmesh_specify.sqlmesh_artifacts import CONFIG_FILENAMES


def doctor_project(target_dir: Path) -> ValidationReport:
    """Inspect a SQLMesh repo and report adoption gaps without changing files."""
    findings: list[Finding] = []
    if not any((target_dir / name).exists() for name in CONFIG_FILENAMES):
        findings.append(
            Finding(
                "error",
                "SQLMESH_CONFIG_MISSING",
                "No config.yaml, config.yml, or config.py found. Run doctor at a SQLMesh root.",
                relpath(target_dir, target_dir),
            )
        )
        return ValidationReport("sqlmesh-specify doctor", tuple(findings))

    checks = [
        (
            target_dir / ".sqlmesh-specify" / "constitution.md",
            "SQLMESH_SPECIFY_MISSING",
            "No .sqlmesh-specify/constitution.md found. Run `sqlmesh-specify init`.",
        ),
        (target_dir / "CLAUDE.md", "AGENT_CONTEXT_MISSING", "No CLAUDE.md found."),
        (target_dir / "specs", "SPECS_DIR_MISSING", "No specs/ directory found."),
        (
            target_dir / ".sqlmesh-specify" / "agents",
            "AGENTS_DIR_MISSING",
            "No .sqlmesh-specify/agents/ directory found.",
        ),
        (target_dir / "audits", "AUDITS_DIR_MISSING", "No audits/ directory found."),
        (target_dir / "tests", "TESTS_DIR_MISSING", "No tests/ directory found."),
    ]
    for path, code, message in checks:
        if not path.exists():
            findings.append(Finding("warning", code, message, relpath(path, target_dir)))

    models_dir = target_dir / "models"
    if not models_dir.exists():
        findings.append(
            Finding("error", "MODELS_DIR_MISSING", "No models/ directory found.", "models")
        )
    else:
        sql_count = len(list(models_dir.rglob("*.sql")))
        py_count = len(list(models_dir.rglob("*.py")))
        findings.append(
            Finding(
                "info",
                "MODEL_INVENTORY",
                f"Found {sql_count} SQL model file(s) and {py_count} Python model file(s).",
                relpath(models_dir, target_dir),
            )
        )
        if sql_count + py_count == 0:
            findings.append(
                Finding(
                    "error",
                    "NO_MODEL_FILES",
                    "models/ has no .sql or .py model files.",
                    "models",
                )
            )

    if not findings:
        findings.append(Finding("info", "DOCTOR_OK", "No adoption gaps found."))
    return ValidationReport("sqlmesh-specify doctor", tuple(findings))
