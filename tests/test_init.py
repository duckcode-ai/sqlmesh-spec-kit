from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sqlmesh_specify.cli import main
from sqlmesh_specify.init import SUPPORTED_ENGINES


def test_cli_help_lists_commands() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ["init", "doctor", "validate", "report", "ci", "jira", "confluence"]:
        assert command in result.output


def test_init_succeeds_on_minimal_sqlmesh_project(minimal_sqlmesh_project: Path) -> None:
    result = CliRunner().invoke(
        main,
        ["init", "demo", "--engine", "duckdb", "--target", str(minimal_sqlmesh_project)],
    )
    assert result.exit_code == 0, result.output
    assert (minimal_sqlmesh_project / ".sqlmesh-specify" / "constitution.md").exists()
    assert (minimal_sqlmesh_project / ".sqlmesh-specify" / "commands" / "sqlmesh.plan.md").exists()
    assert (minimal_sqlmesh_project / "CLAUDE.md").exists()
    assert (minimal_sqlmesh_project / "specs" / ".gitkeep").exists()


def test_init_refuses_non_sqlmesh_target(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main, ["init", "demo", "--engine", "duckdb", "--target", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert "config.yaml" in result.output


def test_init_force_overwrites_existing(minimal_sqlmesh_project: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(
        main, ["init", "demo", "--engine", "duckdb", "--target", str(minimal_sqlmesh_project)]
    ).exit_code == 0
    sentinel = minimal_sqlmesh_project / ".sqlmesh-specify" / "sentinel.txt"
    sentinel.write_text("old")
    result = runner.invoke(
        main,
        ["init", "demo", "--engine", "duckdb", "--target", str(minimal_sqlmesh_project), "--force"],
    )
    assert result.exit_code == 0, result.output
    assert not sentinel.exists()


def test_each_engine_preset_initializes(tmp_path: Path) -> None:
    runner = CliRunner()
    for engine in SUPPORTED_ENGINES:
        project = tmp_path / engine
        (project / "models").mkdir(parents=True)
        (project / "models" / "example.sql").write_text(
            "MODEL (name x.y, kind FULL); SELECT 1 AS id;"
        )
        (project / "config.yaml").write_text("default_gateway: local\n")
        result = runner.invoke(main, ["init", "demo", "--engine", engine, "--target", str(project)])
        assert result.exit_code == 0, result.output
        constitution = (project / ".sqlmesh-specify" / "constitution.md").read_text()
        plan = (project / ".sqlmesh-specify" / "templates" / "plan-template.md").read_text()
        assert f"BEGIN {engine.upper()} ADDITIONS" in constitution
        assert f"BEGIN {engine.upper()} PLAN ADDITIONS" in plan
