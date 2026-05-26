from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sqlmesh_specify.cli import main
from sqlmesh_specify.sqlmesh_artifacts import validate_sqlmesh_project


def test_validate_sqlmesh_reports_clean_minimal_project(minimal_sqlmesh_project: Path) -> None:
    report = validate_sqlmesh_project(minimal_sqlmesh_project)
    assert report.error_count == 0
    assert "AUDITS_MISSING" not in {finding.code for finding in report.findings}


def test_validate_sqlmesh_errors_without_config(tmp_path: Path) -> None:
    (tmp_path / "models").mkdir()
    report = validate_sqlmesh_project(tmp_path)
    assert "SQLMESH_CONFIG_MISSING" in {finding.code for finding in report.findings}


def test_validate_sqlmesh_errors_without_models(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text("default_gateway: local\n")
    report = validate_sqlmesh_project(tmp_path)
    assert "MODELS_DIR_MISSING" in {finding.code for finding in report.findings}


def test_validate_sqlmesh_warns_without_audits_or_tests(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text("default_gateway: local\n")
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "example.sql").write_text("MODEL (name x.y, kind FULL); SELECT 1 AS id;")
    report = validate_sqlmesh_project(tmp_path)
    codes = {finding.code for finding in report.findings}
    assert "AUDITS_MISSING" in codes
    assert "TESTS_DIR_MISSING" in codes


def test_validate_sqlmesh_cli(minimal_sqlmesh_project: Path) -> None:
    result = CliRunner().invoke(
        main, ["validate", "sqlmesh", "--target", str(minimal_sqlmesh_project)]
    )
    assert result.exit_code == 0
    assert "SQLMesh project validation" in result.output
