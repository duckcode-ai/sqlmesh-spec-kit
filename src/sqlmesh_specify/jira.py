"""Jira Cloud bridge for sqlmesh-specify artifacts."""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml


class JiraError(RuntimeError):
    """Raised when Jira integration cannot complete safely."""


@dataclass(frozen=True)
class JiraConfig:
    """Jira Cloud connection settings."""

    base_url: str
    email: str
    api_token: str


@dataclass(frozen=True)
class JiraSubtask:
    """Existing Jira subtask summary."""

    key: str
    summary: str


@dataclass(frozen=True)
class JiraIssue:
    """Normalized Jira issue fields used by sqlmesh-specify."""

    key: str
    summary: str
    description: str
    project_key: str
    issue_url: str
    labels: tuple[str, ...]
    components: tuple[str, ...]
    priority: str | None
    issue_type: str | None
    status: str | None
    subtasks: tuple[JiraSubtask, ...]


@dataclass(frozen=True)
class TaskItem:
    """Task parsed from tasks.md."""

    task_id: str
    description: str
    checked: bool
    validates: str | None


@dataclass(frozen=True)
class CreatedSubtask:
    """Result for a task pushed to Jira."""

    task_id: str
    summary: str
    key: str | None
    created: bool


class JiraClient:
    """Small Jira Cloud REST client backed by the Python standard library."""

    def __init__(self, config: JiraConfig) -> None:
        self._config = config

    def get_issue(self, issue_key: str) -> JiraIssue:
        """Fetch an issue and normalize fields needed by the bridge."""
        fields = ",".join(
            [
                "summary",
                "description",
                "project",
                "labels",
                "components",
                "priority",
                "issuetype",
                "status",
                "subtasks",
            ]
        )
        raw = self._request_json(
            "GET",
            f"/rest/api/3/issue/{quote(issue_key)}?fields={quote(fields)}",
        )
        return _parse_issue(raw, self._config.base_url)

    def attach_file(self, issue_key: str, path: Path) -> str:
        """Attach a file to a Jira issue and return the uploaded filename."""
        if not path.exists() or not path.is_file():
            raise JiraError(f"attachment file not found: {path}")

        boundary = f"sqlmesh-specify-{uuid.uuid4().hex}"
        filename = path.name
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_bytes = path.read_bytes()
        body = b"".join(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                ).encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )
        self._request_json(
            "POST",
            f"/rest/api/3/issue/{quote(issue_key)}/attachments",
            body=body,
            headers={
                "Accept": "application/json",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "X-Atlassian-Token": "no-check",
            },
        )
        return filename

    def add_comment(self, issue_key: str, text: str) -> None:
        """Add a plain-text comment to a Jira issue."""
        self._request_json(
            "POST",
            f"/rest/api/3/issue/{quote(issue_key)}/comment",
            json_body={"body": text_to_adf(text)},
        )

    def create_subtask(
        self,
        *,
        parent_issue_key: str,
        project_key: str,
        issue_type_name: str,
        summary: str,
        description: str,
    ) -> str:
        """Create a Jira subtask and return its issue key."""
        response = self._request_json(
            "POST",
            "/rest/api/3/issue",
            json_body={
                "fields": {
                    "project": {"key": project_key},
                    "parent": {"key": parent_issue_key},
                    "issuetype": {"name": issue_type_name},
                    "summary": summary,
                    "description": text_to_adf(description),
                    "labels": ["sqlmesh-specify"],
                }
            },
        )
        if not isinstance(response, dict):
            raise JiraError("Jira did not return an object for the created subtask.")
        key = response.get("key")
        if not isinstance(key, str):
            raise JiraError("Jira did not return a key for the created subtask.")
        return key

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, object] | None = None,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        data = body
        request_headers = {
            "Authorization": _basic_auth(self._config.email, self._config.api_token),
            "Accept": "application/json",
        }
        if json_body is not None:
            data = json.dumps(json_body).encode()
            request_headers["Content-Type"] = "application/json"
        if headers:
            request_headers.update(headers)

        request = Request(
            f"{self._config.base_url.rstrip('/')}{path}",
            data=data,
            headers=request_headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=30) as response:
                response_body = response.read()
        except HTTPError as error:
            detail = error.read().decode(errors="replace")
            raise JiraError(f"Jira API request failed with HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise JiraError(f"Jira API request failed: {error.reason}") from error

        if not response_body:
            return {}
        parsed = json.loads(response_body.decode())
        if not isinstance(parsed, (dict, list)):
            raise JiraError("Jira API returned an unexpected JSON response.")
        return parsed


def config_from_env() -> JiraConfig:
    """Load Jira Cloud credentials from environment variables."""
    base_url = os.environ.get("JIRA_BASE_URL", "").strip()
    email = os.environ.get("JIRA_EMAIL", "").strip()
    api_token = os.environ.get("JIRA_API_TOKEN", "").strip()
    missing = [
        name
        for name, value in (
            ("JIRA_BASE_URL", base_url),
            ("JIRA_EMAIL", email),
            ("JIRA_API_TOKEN", api_token),
        )
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise JiraError(f"Missing Jira environment variable(s): {joined}")
    return JiraConfig(base_url=base_url.rstrip("/"), email=email, api_token=api_token)


def make_jira_client() -> JiraClient:
    """Create a Jira client from environment variables."""
    return JiraClient(config_from_env())


def pull_issue_to_spec(
    *,
    client: JiraClient,
    issue_key: str,
    target_dir: Path,
    slug: str | None = None,
    force: bool = False,
) -> Path:
    """Create a local spec directory from a Jira issue."""
    issue = client.get_issue(issue_key)
    specs_dir = target_dir / "specs"
    specs_dir.mkdir(exist_ok=True)
    spec_dir = specs_dir / f"{_next_spec_number(specs_dir)}-{_slug_for_issue(issue, slug)}"
    if spec_dir.exists() and not force:
        raise JiraError(f"spec directory already exists: {spec_dir}")
    spec_dir.mkdir(parents=True, exist_ok=True)

    (spec_dir / "jira.yml").write_text(_jira_yml(issue, spec_dir, target_dir))
    spec_path = spec_dir / "spec.md"
    if spec_path.exists() and not force:
        raise JiraError(f"spec.md already exists: {spec_path}")
    spec_path.write_text(_spec_from_issue(issue))
    return spec_dir


def attach_artifacts(
    *,
    client: JiraClient,
    issue_key: str,
    files: list[Path],
    comment: bool = True,
) -> list[str]:
    """Attach local artifacts to a Jira issue."""
    if not files:
        raise JiraError("No files were provided to attach.")

    uploaded: list[str] = []
    for path in files:
        uploaded.append(client.attach_file(issue_key, path))

    if comment:
        client.add_comment(
            issue_key,
            "sqlmesh-specify attached approved artifact(s):\n"
            + "\n".join(f"- {filename}" for filename in uploaded),
        )
    return uploaded


def create_subtasks_from_tasks(
    *,
    client: JiraClient,
    issue_key: str,
    tasks_path: Path,
    issue_type_name: str = "Sub-task",
    include_done: bool = False,
    dry_run: bool = False,
) -> list[CreatedSubtask]:
    """Create Jira subtasks from a sqlmesh-specify tasks.md file."""
    if not tasks_path.exists() or not tasks_path.is_file():
        raise JiraError(f"tasks file not found: {tasks_path}")

    issue = client.get_issue(issue_key)
    tasks = parse_tasks(tasks_path.read_text())
    existing = {
        _extract_task_id_from_summary(subtask.summary): subtask
        for subtask in issue.subtasks
        if _extract_task_id_from_summary(subtask.summary) is not None
    }

    results: list[CreatedSubtask] = []
    for task in tasks:
        if task.checked and not include_done:
            continue

        summary = _subtask_summary(task)
        existing_subtask = existing.get(task.task_id)
        if existing_subtask is not None:
            results.append(
                CreatedSubtask(
                    task_id=task.task_id,
                    summary=summary,
                    key=existing_subtask.key,
                    created=False,
                )
            )
            continue

        if dry_run:
            results.append(
                CreatedSubtask(task_id=task.task_id, summary=summary, key=None, created=False)
            )
            continue

        key = client.create_subtask(
            parent_issue_key=issue.key,
            project_key=issue.project_key,
            issue_type_name=issue_type_name,
            summary=summary,
            description=_subtask_description(task, tasks_path),
        )
        results.append(CreatedSubtask(task_id=task.task_id, summary=summary, key=key, created=True))

    return results


def sync_spec_dir(
    *,
    client: JiraClient,
    issue_key: str,
    spec_dir: Path,
    issue_type_name: str = "Sub-task",
    dry_run: bool = False,
) -> tuple[list[str], list[CreatedSubtask]]:
    """Attach approved artifacts and create Jira subtasks for a spec directory."""
    files = [path for path in (spec_dir / "spec.md", spec_dir / "plan.md") if path.exists()]
    uploaded: list[str] = []
    if files and not dry_run:
        uploaded = attach_artifacts(client=client, issue_key=issue_key, files=files)

    subtasks: list[CreatedSubtask] = []
    tasks_path = spec_dir / "tasks.md"
    if tasks_path.exists():
        subtasks = create_subtasks_from_tasks(
            client=client,
            issue_key=issue_key,
            tasks_path=tasks_path,
            issue_type_name=issue_type_name,
            dry_run=dry_run,
        )

    return uploaded, subtasks


_TASK_RE = re.compile(
    r"^\s*-\s+\[(?P<checked>[ xX])\]\s+(?:\*\*)?(?P<id>T[-_]?\d+)(?:\*\*)?\s+[—-]\s+"
    r"(?P<description>.+?)\s*$"
)
_VALIDATES_RE = re.compile(r"^\s*-\s+\*\*Validates:\*\*\s+(?P<validates>.+?)\s*$")
_SUBTASK_ID_RE = re.compile(r"^\[sqlmesh-specify (?P<id>T-\d+)\]")


def parse_tasks(text: str) -> list[TaskItem]:
    """Parse sqlmesh-specify task list entries from tasks.md."""
    tasks: list[TaskItem] = []
    current_index: int | None = None

    for line in text.splitlines():
        task_match = _TASK_RE.match(line)
        if task_match is not None:
            task = TaskItem(
                task_id=_normalize_task_id(task_match.group("id")),
                description=task_match.group("description").strip(),
                checked=task_match.group("checked").lower() == "x",
                validates=None,
            )
            tasks.append(task)
            current_index = len(tasks) - 1
            continue

        validates_match = _VALIDATES_RE.match(line)
        if validates_match is not None and current_index is not None:
            previous = tasks[current_index]
            tasks[current_index] = TaskItem(
                task_id=previous.task_id,
                description=previous.description,
                checked=previous.checked,
                validates=validates_match.group("validates").strip(),
            )

    return tasks


def text_to_adf(text: str) -> dict[str, object]:
    """Convert plain text to a minimal Atlassian Document Format document."""
    content: list[dict[str, object]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        content.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line}],
            }
        )
    if not content:
        content.append({"type": "paragraph", "content": [{"type": "text", "text": " "}]})
    return {"type": "doc", "version": 1, "content": content}


def _parse_issue(raw: dict[str, Any] | list[Any], base_url: str) -> JiraIssue:
    if not isinstance(raw, dict):
        raise JiraError("Jira issue response was not an object.")
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        raise JiraError("Jira issue response did not include fields.")

    key = _string(raw.get("key"), "issue key")
    project = _mapping(fields.get("project"))
    priority = _optional_name(fields.get("priority"))
    issue_type = _optional_name(fields.get("issuetype"))
    status = _optional_name(fields.get("status"))
    components = tuple(
        name
        for item in _list(fields.get("components"))
        if (name := _optional_name(item)) is not None
    )
    labels = tuple(value for value in _list(fields.get("labels")) if isinstance(value, str))
    subtasks = tuple(_parse_subtask(item) for item in _list(fields.get("subtasks")))

    return JiraIssue(
        key=key,
        summary=_string(fields.get("summary"), "summary"),
        description=adf_to_text(fields.get("description")),
        project_key=_string(project.get("key"), "project key"),
        issue_url=f"{base_url.rstrip('/')}/browse/{key}",
        labels=labels,
        components=components,
        priority=priority,
        issue_type=issue_type,
        status=status,
        subtasks=subtasks,
    )


def _parse_subtask(value: object) -> JiraSubtask:
    mapping = _mapping(value)
    fields = _mapping(mapping.get("fields"))
    return JiraSubtask(
        key=_string(mapping.get("key"), "subtask key"),
        summary=_string(fields.get("summary"), "subtask summary"),
    )


def adf_to_text(value: object) -> str:
    """Convert a Jira ADF document, string, or null value to readable text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        node_type = value.get("type")
        if node_type == "text":
            text = value.get("text")
            return text if isinstance(text, str) else ""
        parts = [adf_to_text(child) for child in _list(value.get("content"))]
        joined = " ".join(part for part in parts if part).strip()
        if node_type in {"paragraph", "heading", "blockquote"}:
            return joined
        if node_type == "listItem":
            return f"- {joined}" if joined else ""
        if node_type in {"bulletList", "orderedList", "doc"}:
            return "\n".join(part for part in parts if part)
        return joined
    if isinstance(value, list):
        return "\n".join(adf_to_text(item) for item in value)
    return ""


def _jira_yml(issue: JiraIssue, spec_dir: Path, target_dir: Path) -> str:
    payload = {
        "issue_key": issue.key,
        "issue_url": issue.issue_url,
        "summary": issue.summary,
        "project_key": issue.project_key,
        "spec_dir": str(spec_dir.relative_to(target_dir)),
        "last_synced_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
    return yaml.safe_dump(payload, sort_keys=False)


def _spec_from_issue(issue: JiraIssue) -> str:
    today = datetime.now(UTC).date().isoformat()
    labels = ", ".join(issue.labels) if issue.labels else "none"
    components = ", ".join(issue.components) if issue.components else "none"
    description = issue.description.strip() or "No Jira description was provided."
    return f"""# {issue.summary}

**Ticket:** {issue.issue_url}
**Author:** Jira
**Date:** {today}
**Status:** draft

## Problem

Jira issue `{issue.key}` requests: {issue.summary}

Source Jira description:

{description}

## Users

| User | Job to be done |
|---|---|
| <persona> | <one-sentence job from Jira or stakeholder review> |

## What this is

<Translate the Jira request into the SQLMesh-facing outcome. Keep this in business language before
planning SQL or YAML changes.>

## Acceptance criteria

- AC1: The system shall implement `{issue.key}` without unrelated SQLMesh changes.
- AC2: When affected SQLMesh models are parsed, the system shall preserve downstream references.
- AC3: Where grain, metrics, or semantic behavior changes, the system shall document approval.

## Out of scope

- Raw agent scratch notes are not part of the approved Jira record.
- Unrelated model cleanup is not included unless added to the approved plan.

## Constraints

- Warehouse: <fill from project preset>
- Materialization: <table|view|incremental|...>
- Grain: <one sentence — what is one row?>
- Refresh cadence: <hourly|daily|on-demand>
- Downstream consumers: <semantic layer metrics, dashboards, reverse-ETL, ML features>
- Jira priority: {issue.priority or "not set"}
- Jira issue type: {issue.issue_type or "not set"}
- Jira status: {issue.status or "not set"}
- Jira labels: {labels}
- Jira components: {components}

## Open questions

- [ ] Confirm the business owner who can approve this spec.
- [ ] Confirm affected SQLMesh models, metrics, and downstream consumers.
- [ ] Confirm the validation evidence that must be attached back to Jira.
"""


def _next_spec_number(specs_dir: Path) -> str:
    highest = 0
    for path in specs_dir.iterdir():
        if not path.is_dir():
            continue
        prefix = path.name.split("-", 1)[0]
        if prefix.isdigit():
            highest = max(highest, int(prefix))
    return f"{highest + 1:03d}"


def _slug_for_issue(issue: JiraIssue, requested_slug: str | None) -> str:
    base = requested_slug or f"{issue.key}-{issue.summary}"
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return slug[:80] or issue.key.lower()


def _subtask_summary(task: TaskItem) -> str:
    return f"[sqlmesh-specify {task.task_id}] {task.description}"[:255]


def _subtask_description(task: TaskItem, tasks_path: Path) -> str:
    lines = [
        f"Created from {tasks_path}",
        "",
        f"Task: {task.task_id}",
        f"Description: {task.description}",
    ]
    if task.validates:
        lines.append(f"Validates: {task.validates}")
    return "\n".join(lines)


def _extract_task_id_from_summary(summary: str) -> str | None:
    match = _SUBTASK_ID_RE.match(summary)
    if match is None:
        return None
    return match.group("id")


def _normalize_task_id(task_id: str) -> str:
    digits = re.sub(r"\D", "", task_id)
    return f"T-{int(digits):02d}"


def _basic_auth(email: str, api_token: str) -> str:
    token = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    return f"Basic {token}"


def _string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise JiraError(f"Jira issue response is missing {field_name}.")
    return value


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _optional_name(value: object) -> str | None:
    mapping = _mapping(value)
    name = mapping.get("name")
    return name if isinstance(name, str) else None
