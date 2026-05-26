from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sqlmesh_specify.cli import main
from sqlmesh_specify.validate import _extract_ac_lines


def test_html_comments_inside_acceptance_criteria_are_ignored() -> None:
    text = """# Spec

## Acceptance Criteria

<!-- explain why this matters -->
- AC1: When the model is queried, the system shall return one row per customer.
"""
    assert _extract_ac_lines(text) == [
        (6, "When the model is queried, the system shall return one row per customer.")
    ]


def test_prose_inside_acceptance_criteria_fails(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text(
        "# Spec\n\n## Acceptance Criteria\n\n"
        "This paragraph should fail.\n"
        "- AC1: When the model is queried, the system shall return rows.\n"
    )
    result = CliRunner().invoke(main, ["validate", str(spec)])
    assert result.exit_code == 1
    assert "do not match" in result.output


def test_valid_spec_cli_passes(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text(
        "# Spec\n\n## Acceptance Criteria\n\n"
        "- AC1: When the model is queried, the system shall return rows.\n"
    )
    result = CliRunner().invoke(main, ["validate", str(spec)])
    assert result.exit_code == 0
