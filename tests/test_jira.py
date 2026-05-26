"""Tests for Jira bridge helpers."""
from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner

from sqlmesh_specify.cli import main
from sqlmesh_specify.jira import (
    CreatedSubtask,
    JiraIssue,
    JiraSubtask,
    attach_artifacts,
    create_subtasks_from_tasks,
    parse_tasks,
    pull_issue_to_spec,
)


class FakeJiraClient:
    def __init__(self, issue: JiraIssue) -> None:
        self.issue = issue
        self.attachments: list[Path] = []
        self.comments: list[str] = []
        self.created: list[dict[str, str]] = []

    def get_issue(self, issue_key: str) -> JiraIssue:
        assert issue_key == self.issue.key
        return self.issue

    def attach_file(self, issue_key: str, path: Path) -> str:
        assert issue_key == self.issue.key
        self.attachments.append(path)
        return path.name

    def add_comment(self, issue_key: str, text: str) -> None:
        assert issue_key == self.issue.key
        self.comments.append(text)

    def create_subtask(
        self,
        *,
        parent_issue_key: str,
        project_key: str,
        issue_type_name: str,
        summary: str,
        description: str,
    ) -> str:
        assert parent_issue_key == self.issue.key
        assert project_key == self.issue.project_key
        assert issue_type_name == "Sub-task"
        key = f"{self.issue.project_key}-{len(self.created) + 200}"
        self.created.append({"summary": summary, "description": description, "key": key})
        return key


def test_cli_help_lists_jira_group() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0, result.output
    assert "jira" in result.output

    jira_result = runner.invoke(main, ["jira", "--help"])
    assert jira_result.exit_code == 0, jira_result.output
    assert "pull" in jira_result.output
    assert "attach" in jira_result.output
    assert "create-tasks" in jira_result.output
    assert "sync" in jira_result.output


def test_pull_issue_to_spec_creates_traceable_spec(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text("name: demo\nversion: '1.0.0'\nprofile: demo\n")
    client = FakeJiraClient(_issue())

    spec_dir = pull_issue_to_spec(
        client=client,  # type: ignore[arg-type]
        issue_key="NBA-123",
        target_dir=tmp_path,
    )

    assert spec_dir.name == "001-nba-123-player-journey-mart"
    spec = (spec_dir / "spec.md").read_text()
    assert "# Player journey mart" in spec
    assert "https://example.atlassian.net/browse/NBA-123" in spec
    assert "AC1: The system shall implement `NBA-123` without unrelated SQLMesh changes." in spec

    jira_yml = yaml.safe_load((spec_dir / "jira.yml").read_text())
    assert jira_yml["issue_key"] == "NBA-123"
    assert jira_yml["spec_dir"] == "specs/001-nba-123-player-journey-mart"


def test_parse_tasks_extracts_pending_items_and_validation() -> None:
    tasks = parse_tasks(
        """# Tasks

## Task list

- [ ] **T-01** — Add mart SQL. AC: AC1.
  - **Done when:** model builds
  - **Validates:** AC1, AC2

- [x] **T-02** — Add docs. AC: AC3.
  - **Validates:** AC3
"""
    )

    assert [task.task_id for task in tasks] == ["T-01", "T-02"]
    assert tasks[0].description == "Add mart SQL. AC: AC1."
    assert tasks[0].validates == "AC1, AC2"
    assert tasks[1].checked is True


def test_attach_artifacts_uploads_files_and_comments(tmp_path: Path) -> None:
    client = FakeJiraClient(_issue())
    spec = tmp_path / "spec.md"
    plan = tmp_path / "plan.md"
    spec.write_text("spec")
    plan.write_text("plan")

    uploaded = attach_artifacts(
        client=client,  # type: ignore[arg-type]
        issue_key="NBA-123",
        files=[spec, plan],
    )

    assert uploaded == ["spec.md", "plan.md"]
    assert client.attachments == [spec, plan]
    assert "spec.md" in client.comments[0]
    assert "plan.md" in client.comments[0]


def test_create_subtasks_is_idempotent(tmp_path: Path) -> None:
    tasks_path = tmp_path / "tasks.md"
    tasks_path.write_text(
        """# Tasks

## Task list

- [ ] **T-01** — Add player journey mart. AC: AC1.
  - **Validates:** AC1
- [ ] **T-02** — Add tests and docs. AC: AC2.
  - **Validates:** AC2
"""
    )
    issue = _issue(
        subtasks=(
            JiraSubtask(
                key="NBA-199",
                summary="[sqlmesh-specify T-01] Add player journey mart. AC: AC1.",
            ),
        )
    )
    client = FakeJiraClient(issue)

    results = create_subtasks_from_tasks(
        client=client,  # type: ignore[arg-type]
        issue_key="NBA-123",
        tasks_path=tasks_path,
    )

    assert results == [
        CreatedSubtask(
            task_id="T-01",
            summary="[sqlmesh-specify T-01] Add player journey mart. AC: AC1.",
            key="NBA-199",
            created=False,
        ),
        CreatedSubtask(
            task_id="T-02",
            summary="[sqlmesh-specify T-02] Add tests and docs. AC: AC2.",
            key="NBA-200",
            created=True,
        ),
    ]
    assert client.created == [
        {
            "summary": "[sqlmesh-specify T-02] Add tests and docs. AC: AC2.",
            "description": (
                f"Created from {tasks_path}\n\n"
                "Task: T-02\n"
                "Description: Add tests and docs. AC: AC2.\n"
                "Validates: AC2"
            ),
            "key": "NBA-200",
        }
    ]


def _issue(subtasks: tuple[JiraSubtask, ...] = ()) -> JiraIssue:
    return JiraIssue(
        key="NBA-123",
        summary="Player journey mart",
        description="Build a season-by-season player journey.",
        project_key="NBA",
        issue_url="https://example.atlassian.net/browse/NBA-123",
        labels=("analytics",),
        components=("SQLMesh",),
        priority="Medium",
        issue_type="Story",
        status="Ready",
        subtasks=subtasks,
    )
