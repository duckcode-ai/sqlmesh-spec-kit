"""Implementation of `sqlmesh-specify init`."""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from sqlmesh_specify.sqlmesh_artifacts import CONFIG_FILENAMES
from sqlmesh_specify.templates_loader import asset_dir

_IGNORE_JUNK = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", ".gitkeep")
SUPPORTED_ENGINES = (
    "duckdb",
    "snowflake",
    "databricks",
    "bigquery",
    "trino",
    "redshift",
    "postgres",
    "mysql",
    "mssql",
    "athena",
    "spark",
    "clickhouse",
)


def init_project(project_name: str, engine: str, target_dir: Path, force: bool) -> None:
    """Initialize SQLMesh spec assets in an existing SQLMesh project."""
    if engine not in SUPPORTED_ENGINES:
        click.echo(f"error: unknown engine '{engine}'", err=True)
        raise SystemExit(2)
    if not any((target_dir / name).is_file() for name in CONFIG_FILENAMES):
        click.echo(
            "error: no SQLMesh config.yaml, config.yml, or config.py found at "
            f"{target_dir}.\n"
            "  sqlmesh-specify init must be run inside an existing SQLMesh project.",
            err=True,
        )
        raise SystemExit(1)
    models_dir = target_dir / "models"
    if not models_dir.is_dir():
        click.echo("error: no models/ directory found in the SQLMesh project.", err=True)
        raise SystemExit(1)

    specify_dir = target_dir / ".sqlmesh-specify"
    if specify_dir.exists():
        if not force:
            click.echo(f"error: {specify_dir} already exists. Re-run with --force.", err=True)
            raise SystemExit(1)
        shutil.rmtree(specify_dir)
    specify_dir.mkdir(parents=True, exist_ok=False)

    _copy_file(asset_dir("memory") / "constitution.md", specify_dir / "constitution.md")
    additions = (asset_dir("presets") / engine / "constitution-additions.md").read_text()
    constitution_path = specify_dir / "constitution.md"
    constitution_path.write_text(
        constitution_path.read_text()
        + f"\n\n<!-- BEGIN {engine.upper()} ADDITIONS -->\n\n"
        + additions
        + f"\n\n<!-- END {engine.upper()} ADDITIONS -->\n"
    )

    templates_dst = specify_dir / "templates"
    shutil.copytree(asset_dir("templates"), templates_dst, ignore=_IGNORE_JUNK)
    plan_additions = (asset_dir("presets") / engine / "plan-additions.md").read_text()
    plan_path = templates_dst / "plan-template.md"
    plan_path.write_text(
        plan_path.read_text()
        + f"\n\n<!-- BEGIN {engine.upper()} PLAN ADDITIONS -->\n\n"
        + plan_additions
        + f"\n\n<!-- END {engine.upper()} PLAN ADDITIONS -->\n"
    )

    shutil.copytree(asset_dir("skills"), specify_dir / "skills", ignore=_IGNORE_JUNK)
    shutil.copytree(asset_dir("commands"), specify_dir / "commands", ignore=_IGNORE_JUNK)
    shutil.copytree(asset_dir("agents"), specify_dir / "agents", ignore=_IGNORE_JUNK)

    claude_template = (
        (asset_dir("templates") / "CLAUDE.md.template")
        .read_text()
        .replace("{{ project_name }}", project_name)
        .replace("{{ engine }}", engine)
    )
    claude_target = target_dir / "CLAUDE.md"
    if claude_target.exists():
        suggested = target_dir / "CLAUDE.md.sqlmesh-specify-suggested"
        suggested.write_text(claude_template)
        click.echo(f"note: {claude_target.name} already exists; wrote {suggested.name}")
    else:
        claude_target.write_text(claude_template)
        click.echo("wrote CLAUDE.md")

    (target_dir / "specs").mkdir(exist_ok=True)
    (target_dir / "specs" / ".gitkeep").touch()
    click.echo(f"\nsqlmesh-specify initialized in {target_dir}")
    click.echo(f"  engine preset: {engine}")


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
