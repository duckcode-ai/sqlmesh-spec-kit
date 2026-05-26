from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sqlmesh_specify.cli import main
from sqlmesh_specify.doctor import doctor_project


def test_doctor_reports_adoption_gaps(minimal_sqlmesh_project: Path) -> None:
    report = doctor_project(minimal_sqlmesh_project)
    codes = {finding.code for finding in report.findings}
    assert "SQLMESH_SPECIFY_MISSING" in codes
    assert "MODEL_INVENTORY" in codes


def test_doctor_cli(minimal_sqlmesh_project: Path) -> None:
    result = CliRunner().invoke(main, ["doctor", "--target", str(minimal_sqlmesh_project)])
    assert result.exit_code == 0
    assert "sqlmesh-specify doctor" in result.output
