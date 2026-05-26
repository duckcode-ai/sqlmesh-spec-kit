"""Validate SQLMesh project structure for sqlmesh-spec-kit."""
from __future__ import annotations

from pathlib import Path

from sqlmesh_specify.lifecycle import relpath
from sqlmesh_specify.reporting import Finding, ValidationReport

CONFIG_FILENAMES = ("config.yaml", "config.yml", "config.py")
MODEL_SUFFIXES = (".sql", ".py")
ENGINE_DIRS = ("seeds", "macros", "external_models")


def validate_sqlmesh_project(target_dir: Path) -> ValidationReport:
    """Validate SQLMesh project structure without executing SQLMesh."""
    findings: list[Finding] = []
    config_paths = [target_dir / name for name in CONFIG_FILENAMES]
    if not any(path.exists() and path.is_file() for path in config_paths):
        findings.append(
            Finding(
                "error",
                "SQLMESH_CONFIG_MISSING",
                "No config.yaml, config.yml, or config.py found. "
                "Run this at a SQLMesh project root.",
                relpath(target_dir, target_dir),
            )
        )

    models_dir = target_dir / "models"
    if not models_dir.exists() or not models_dir.is_dir():
        findings.append(
            Finding(
                "error",
                "MODELS_DIR_MISSING",
                "No models/ directory found for SQLMesh models.",
                relpath(models_dir, target_dir),
            )
        )
    else:
        model_files = _model_files(models_dir)
        if not model_files:
            findings.append(
                Finding(
                    "error",
                    "NO_MODEL_FILES",
                    "models/ contains no .sql or .py SQLMesh model files.",
                    relpath(models_dir, target_dir),
                )
            )
        elif not _has_inline_audit_reference(model_files) and not (target_dir / "audits").is_dir():
            findings.append(
                Finding(
                    "warning",
                    "AUDITS_MISSING",
                    "No audits/ directory or inline audit references found.",
                    relpath(target_dir / "audits", target_dir),
                )
            )

    tests_dir = target_dir / "tests"
    if not tests_dir.exists() or not tests_dir.is_dir():
        findings.append(
            Finding(
                "warning",
                "TESTS_DIR_MISSING",
                "No tests/ directory found for SQLMesh tests.",
                relpath(tests_dir, target_dir),
            )
        )

    for dirname in ENGINE_DIRS:
        path = target_dir / dirname
        if not path.exists():
            findings.append(
                Finding(
                    "info",
                    f"{dirname.upper()}_DIR_MISSING",
                    f"No {dirname}/ directory found. Add one when the project needs it.",
                    relpath(path, target_dir),
                )
            )

    return ValidationReport("SQLMesh project validation", tuple(findings))


def _model_files(models_dir: Path) -> list[Path]:
    return sorted(path for path in models_dir.rglob("*") if path.suffix in MODEL_SUFFIXES)


def _has_inline_audit_reference(model_files: list[Path]) -> bool:
    for path in model_files:
        if path.suffix != ".sql":
            continue
        text = path.read_text(errors="ignore").lower()
        if "audits" in text or "audit(" in text or "audit (" in text:
            return True
    return False
