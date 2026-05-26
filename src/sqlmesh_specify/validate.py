"""Implementation of `sqlmesh-specify validate`."""
from __future__ import annotations

import re
from pathlib import Path

import click

from sqlmesh_specify.ears import classify_ears

# Headers that mark the Acceptance Criteria section. Case-insensitive.
AC_SECTION_PATTERNS = [
    re.compile(r"^##+\s*acceptance\s+criteria\b", re.IGNORECASE),
    re.compile(r"^##+\s*ACs?\b", re.IGNORECASE),
]


def validate_spec(spec_path: Path) -> int:
    """Validate that a spec's Acceptance Criteria section is EARS-conformant.

    Args:
        spec_path: Path to a spec.md file.

    Returns:
        0 if all ACs conform to an EARS pattern, 1 otherwise.
    """
    text = spec_path.read_text()
    ac_lines = _extract_ac_lines(text)

    if not ac_lines:
        click.echo(
            f"warning: no Acceptance Criteria section found in {spec_path.name}",
            err=True,
        )
        return 1

    failures: list[tuple[int, str]] = []
    for line_no, line in ac_lines:
        pattern = classify_ears(line)
        if pattern is None:
            failures.append((line_no, line))

    if failures:
        click.echo(f"\n{len(failures)} AC line(s) do not match an EARS pattern:")
        for line_no, line in failures:
            click.echo(f"  line {line_no}: {line.strip()}")
        click.echo(
            "\nsee docs/ears-cheatsheet.md for the five EARS patterns and SQLMesh examples."
        )
        return 1

    click.echo(f"ok: {len(ac_lines)} AC line(s) all match an EARS pattern.")
    return 0


def _extract_ac_lines(text: str) -> list[tuple[int, str]]:
    """Find lines that look like ACs inside the Acceptance Criteria section."""
    lines = text.splitlines()
    in_ac_section = False
    in_html_comment = False
    next_section = re.compile(r"^##+\s+", re.IGNORECASE)
    ac_lines: list[tuple[int, str]] = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if any(p.match(stripped) for p in AC_SECTION_PATTERNS):
            in_ac_section = True
            continue
        if in_ac_section and next_section.match(stripped):
            # We hit the next ## section, so we're done with ACs.
            break
        if in_ac_section:
            if in_html_comment:
                if "-->" in stripped:
                    in_html_comment = False
                continue
            if stripped.startswith("<!--"):
                in_html_comment = "-->" not in stripped
                continue
            # Treat any non-empty line that doesn't start with a markdown decoration
            # as a potential AC line. Bullet markers and AC labels are stripped.
            cleaned = _clean_ac_line(stripped)
            if cleaned:
                ac_lines.append((i, cleaned))

    return ac_lines


def _clean_ac_line(line: str) -> str:
    """Strip bullets, AC prefixes, and bold/italic markers."""
    # Strip leading list markers
    line = re.sub(r"^[-*+]\s+", "", line)
    # Strip AC labels like "AC1:", "**AC1**:", "AC1 —", etc.
    line = re.sub(r"^\**AC\d*\**\s*[:\-—]\s*", "", line, flags=re.IGNORECASE)
    # Strip EARS-pattern labels like "(Ubiquitous)" or "**(Event-driven)**"
    line = re.sub(r"^\**\([^)]+\)\**\s*[—-]?\s*", "", line)
    return line.strip()
