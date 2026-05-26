"""Shared validation report primitives."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Finding:
    """A single validation or diagnostic finding."""

    severity: Severity
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""
        data = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }
        if self.path is not None:
            data["path"] = self.path
        return data


@dataclass(frozen=True)
class ValidationReport:
    """A collection of findings for one CLI command."""

    title: str
    findings: tuple[Finding, ...] = ()

    @property
    def error_count(self) -> int:
        """Number of error findings."""
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        """Number of warning findings."""
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def info_count(self) -> int:
        """Number of info findings."""
        return sum(1 for finding in self.findings if finding.severity == "info")

    @property
    def exit_code(self) -> int:
        """Return 1 when the report has release-blocking errors."""
        return 1 if self.error_count else 0

    def with_findings(self, findings: list[Finding]) -> ValidationReport:
        """Return a copy with more findings appended."""
        return ValidationReport(self.title, self.findings + tuple(findings))

    def to_markdown(self) -> str:
        """Render the report as GitHub-flavored Markdown."""
        lines = [
            f"# {self.title}",
            "",
            "## Summary",
            "",
            f"- Errors: {self.error_count}",
            f"- Warnings: {self.warning_count}",
            f"- Info: {self.info_count}",
            "",
        ]
        if not self.findings:
            lines.extend(["No findings.", ""])
            return "\n".join(lines)

        lines.extend(["## Findings", ""])
        for finding in self.findings:
            location = f" — `{finding.path}`" if finding.path else ""
            lines.append(
                f"- **{finding.severity.upper()} [{finding.code}]**{location}: "
                f"{finding.message}"
            )
        lines.append("")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Render the report as stable JSON."""
        return json.dumps(
            {
                "title": self.title,
                "summary": {
                    "errors": self.error_count,
                    "warnings": self.warning_count,
                    "info": self.info_count,
                },
                "findings": [finding.to_dict() for finding in self.findings],
            },
            indent=2,
            sort_keys=True,
        )


def combine_reports(title: str, reports: list[ValidationReport]) -> ValidationReport:
    """Combine multiple validation reports into one."""
    findings: list[Finding] = []
    for report in reports:
        findings.extend(report.findings)
    return ValidationReport(title, tuple(findings))
