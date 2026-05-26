"""Confluence Cloud bridge for sqlmesh-specify knowledge artifacts."""
from __future__ import annotations

import base64
import html
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml


class ConfluenceError(RuntimeError):
    """Raised when Confluence integration cannot complete safely."""


@dataclass(frozen=True)
class ConfluenceConfig:
    """Confluence Cloud connection settings."""

    base_url: str
    email: str
    api_token: str


@dataclass(frozen=True)
class ConfluencePage:
    """Normalized Confluence page fields used by sqlmesh-specify."""

    page_id: str
    title: str
    space_id: str | None
    space_key: str | None
    version: int
    page_url: str
    storage: str


@dataclass(frozen=True)
class PublishedPage:
    """Result of creating or updating a Confluence page."""

    page_id: str
    title: str
    page_url: str
    created: bool


class ConfluenceApi(Protocol):
    """Methods required by spec publishing helpers."""

    def get_page(self, page_id: str) -> ConfluencePage:
        """Fetch a Confluence page with storage-format body."""

    def resolve_space_id(self, space_key: str) -> str:
        """Resolve a Confluence space key to a v2 API space id."""

    def create_page(
        self,
        *,
        space_id: str,
        title: str,
        storage: str,
        parent_id: str | None = None,
    ) -> PublishedPage:
        """Create a Confluence page with storage-format body."""

    def update_page(self, *, page_id: str, title: str, storage: str) -> PublishedPage:
        """Update an existing Confluence page with storage-format body."""


class ConfluenceClient:
    """Small Confluence Cloud REST client backed by the Python standard library."""

    def __init__(self, config: ConfluenceConfig) -> None:
        self._config = config

    def get_page(self, page_id: str) -> ConfluencePage:
        """Fetch a Confluence page with storage-format body."""
        raw = self._request_json(
            "GET",
            f"/wiki/api/v2/pages/{quote(page_id)}?body-format=storage",
        )
        return _parse_page(raw, self._config.base_url)

    def resolve_space_id(self, space_key: str) -> str:
        """Resolve a Confluence space key to a v2 API space id."""
        raw = self._request_json("GET", f"/wiki/api/v2/spaces?{urlencode({'keys': space_key})}")
        if not isinstance(raw, dict):
            raise ConfluenceError("Confluence spaces response was not an object.")
        results = raw.get("results")
        if not isinstance(results, list) or not results:
            raise ConfluenceError(f"Confluence space not found for key: {space_key}")
        first = results[0]
        if not isinstance(first, dict):
            raise ConfluenceError(f"Confluence space response missing id for key: {space_key}")
        space_id = first.get("id")
        if not isinstance(space_id, str):
            raise ConfluenceError(f"Confluence space response missing id for key: {space_key}")
        return space_id

    def create_page(
        self,
        *,
        space_id: str,
        title: str,
        storage: str,
        parent_id: str | None = None,
    ) -> PublishedPage:
        """Create a Confluence page with storage-format body."""
        payload: dict[str, object] = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": storage},
        }
        if parent_id:
            payload["parentId"] = parent_id

        raw = self._request_json("POST", "/wiki/api/v2/pages", json_body=payload)
        page = _parse_page(raw, self._config.base_url)
        return PublishedPage(
            page_id=page.page_id,
            title=page.title,
            page_url=page.page_url,
            created=True,
        )

    def update_page(self, *, page_id: str, title: str, storage: str) -> PublishedPage:
        """Update an existing Confluence page with storage-format body."""
        current = self.get_page(page_id)
        raw = self._request_json(
            "PUT",
            f"/wiki/api/v2/pages/{quote(page_id)}",
            json_body={
                "id": page_id,
                "status": "current",
                "title": title,
                "body": {"representation": "storage", "value": storage},
                "version": {
                    "number": current.version + 1,
                    "message": "Updated by sqlmesh-specify",
                },
            },
        )
        page = _parse_page(raw, self._config.base_url)
        return PublishedPage(
            page_id=page.page_id,
            title=page.title,
            page_url=page.page_url,
            created=False,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, object] | None = None,
    ) -> dict[str, Any] | list[Any]:
        data = None
        headers = {
            "Authorization": _basic_auth(self._config.email, self._config.api_token),
            "Accept": "application/json",
        }
        if json_body is not None:
            data = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json"

        request = Request(
            f"{self._config.base_url.rstrip('/')}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=30) as response:
                response_body = response.read()
        except HTTPError as error:
            detail = error.read().decode(errors="replace")
            raise ConfluenceError(
                f"Confluence API request failed with HTTP {error.code}: {detail}"
            ) from error
        except URLError as error:
            raise ConfluenceError(f"Confluence API request failed: {error.reason}") from error

        if not response_body:
            return {}
        parsed = json.loads(response_body.decode())
        if not isinstance(parsed, (dict, list)):
            raise ConfluenceError("Confluence API returned an unexpected JSON response.")
        return parsed


def config_from_env() -> ConfluenceConfig:
    """Load Confluence Cloud credentials from environment variables."""
    base_url = os.environ.get("CONFLUENCE_BASE_URL", "").strip()
    email = os.environ.get("CONFLUENCE_EMAIL", "").strip()
    api_token = os.environ.get("CONFLUENCE_API_TOKEN", "").strip()
    missing = [
        name
        for name, value in (
            ("CONFLUENCE_BASE_URL", base_url),
            ("CONFLUENCE_EMAIL", email),
            ("CONFLUENCE_API_TOKEN", api_token),
        )
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise ConfluenceError(f"Missing Confluence environment variable(s): {joined}")
    return ConfluenceConfig(
        base_url=base_url.rstrip("/"),
        email=email,
        api_token=api_token,
    )


def make_confluence_client() -> ConfluenceClient:
    """Create a Confluence client from environment variables."""
    return ConfluenceClient(config_from_env())


def pull_page_to_context(
    *,
    client: ConfluenceApi,
    page_id: str,
    output_path: Path,
    spec_dir: Path | None = None,
) -> ConfluencePage:
    """Pull a Confluence page into a local markdown context file."""
    page = client.get_page(page_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_context_markdown(page))

    resolved_spec_dir = spec_dir or infer_spec_dir(output_path)
    if resolved_spec_dir is not None:
        _record_source_page(resolved_spec_dir, page, output_path)

    return page


def publish_spec_dir(
    *,
    client: ConfluenceApi | None,
    spec_dir: Path,
    space_key: str | None = None,
    space_id: str | None = None,
    parent_id: str | None = None,
    page_id: str | None = None,
    title: str | None = None,
    dry_run: bool = False,
) -> PublishedPage:
    """Create or update a Confluence summary page for a spec directory."""
    if not spec_dir.exists() or not spec_dir.is_dir():
        raise ConfluenceError(f"spec directory not found: {spec_dir}")

    manifest = read_confluence_manifest(spec_dir)
    resolved_page_id = page_id or _optional_str(manifest.get("page_id"))
    resolved_space_id = space_id or _optional_str(manifest.get("space_id"))
    resolved_space_key = space_key or _optional_str(manifest.get("space_key"))
    resolved_parent_id = parent_id or _optional_str(manifest.get("parent_id"))
    resolved_title = title or _optional_str(manifest.get("title")) or _default_title(spec_dir)
    storage = spec_dir_to_storage(spec_dir, resolved_title)

    if dry_run:
        return PublishedPage(
            page_id=resolved_page_id or "<new>",
            title=resolved_title,
            page_url="<dry-run>",
            created=resolved_page_id is None,
        )

    if client is None:
        raise ConfluenceError("Confluence client is required unless --dry-run is used.")

    if resolved_page_id is not None:
        published = client.update_page(
            page_id=resolved_page_id,
            title=resolved_title,
            storage=storage,
        )
    else:
        if resolved_space_id is None:
            if resolved_space_key is None:
                raise ConfluenceError("Provide --space-id or --space-key when creating a page.")
            resolved_space_id = client.resolve_space_id(resolved_space_key)
        published = client.create_page(
            space_id=resolved_space_id,
            title=resolved_title,
            storage=storage,
            parent_id=resolved_parent_id,
        )

    write_confluence_manifest(
        spec_dir,
        {
            **manifest,
            "space_id": resolved_space_id,
            "space_key": resolved_space_key,
            "parent_id": resolved_parent_id,
            "page_id": published.page_id,
            "page_url": published.page_url,
            "title": published.title,
            "spec_dir": _display_path(spec_dir),
            "last_synced_at": _now_iso(),
        },
    )
    return published


def sync_spec_dir(
    *,
    client: ConfluenceApi | None,
    spec_dir: Path,
    dry_run: bool = False,
) -> PublishedPage:
    """Update a previously published Confluence page for a spec directory."""
    manifest = read_confluence_manifest(spec_dir)
    page_id = _optional_str(manifest.get("page_id"))
    if page_id is None:
        raise ConfluenceError("confluence.yml is missing page_id. Run confluence publish first.")
    return publish_spec_dir(
        client=client,
        spec_dir=spec_dir,
        page_id=page_id,
        dry_run=dry_run,
    )


def read_confluence_manifest(spec_dir: Path) -> dict[str, object]:
    """Read specs/<NNN>/confluence.yml if it exists."""
    path = spec_dir / "confluence.yml"
    if not path.exists():
        return {}
    loaded = yaml.safe_load(path.read_text())
    return loaded if isinstance(loaded, dict) else {}


def write_confluence_manifest(spec_dir: Path, manifest: dict[str, object]) -> None:
    """Write specs/<NNN>/confluence.yml."""
    spec_dir.mkdir(parents=True, exist_ok=True)
    cleaned = {key: value for key, value in manifest.items() if value is not None}
    (spec_dir / "confluence.yml").write_text(yaml.safe_dump(cleaned, sort_keys=False))


def spec_dir_to_storage(spec_dir: Path, title: str) -> str:
    """Render local spec artifacts into safe Confluence storage XHTML."""
    sections = [
        f"<h1>{html.escape(title)}</h1>",
        "<p><strong>Generated by:</strong> sqlmesh-spec-kit</p>",
        f"<p><strong>Spec directory:</strong> {html.escape(_display_path(spec_dir))}</p>",
        (
            "<p>This page is a Confluence knowledge summary. The approved local "
            "<code>spec.md</code>, <code>plan.md</code>, and <code>tasks.md</code> files remain "
            "the source of truth for implementation.</p>"
        ),
    ]
    for filename in (
        "spec.md",
        "plan.md",
        "tasks.md",
        "review.md",
        "governance-review.md",
        "sqlmesh-specify-report.md",
    ):
        path = spec_dir / filename
        if path.exists() and path.is_file():
            sections.append(f"<h2>{html.escape(filename)}</h2>")
            sections.append(f"<pre>{html.escape(path.read_text())}</pre>")

    context_dir = spec_dir / "context"
    if context_dir.is_dir():
        context_files = sorted(path for path in context_dir.glob("*.md") if path.is_file())
        if context_files:
            sections.append("<h2>Confluence context pulled into this spec</h2>")
            for path in context_files:
                sections.append(f"<h3>{html.escape(path.name)}</h3>")
                sections.append(f"<pre>{html.escape(path.read_text())}</pre>")

    return "\n".join(sections)


def storage_to_markdown(storage: str) -> str:
    """Convert Confluence storage XHTML into lightweight markdown context."""
    parser = _StorageToMarkdownParser()
    parser.feed(storage)
    parser.close()
    return parser.markdown()


def infer_spec_dir(path: Path) -> Path | None:
    """Infer specs/<NNN>-<slug>/ from a file path when possible."""
    parts = path.resolve().parts
    if "specs" not in parts:
        return None
    index = parts.index("specs")
    if index + 1 >= len(parts):
        return None
    return Path(*parts[: index + 2])


def _record_source_page(spec_dir: Path, page: ConfluencePage, output_path: Path) -> None:
    manifest = read_confluence_manifest(spec_dir)
    raw_sources = manifest.get("source_pages")
    sources = raw_sources if isinstance(raw_sources, list) else []
    next_source = {
        "page_id": page.page_id,
        "title": page.title,
        "page_url": page.page_url,
        "context_file": _display_path(output_path),
        "last_synced_at": _now_iso(),
    }
    updated_sources = [
        source
        for source in sources
        if not (isinstance(source, dict) and source.get("page_id") == page.page_id)
    ]
    updated_sources.append(next_source)
    write_confluence_manifest(
        spec_dir,
        {
            **manifest,
            "spec_dir": _display_path(spec_dir),
            "source_pages": updated_sources,
            "last_synced_at": _now_iso(),
        },
    )


def _context_markdown(page: ConfluencePage) -> str:
    body = storage_to_markdown(page.storage).strip()
    return f"""# {page.title}

**Confluence page:** {page.page_url}
**Page ID:** {page.page_id}
**Synced at:** {_now_iso()}

## Context

{body}
"""


def _parse_page(raw: dict[str, Any] | list[Any], base_url: str) -> ConfluencePage:
    if not isinstance(raw, dict):
        raise ConfluenceError("Confluence page response was not an object.")
    page_id = _string(raw.get("id"), "page id")
    body = _mapping(raw.get("body"))
    storage = _mapping(body.get("storage"))
    version = _mapping(raw.get("version"))
    links = _mapping(raw.get("_links"))
    webui = links.get("webui")
    page_url = f"{base_url.rstrip('/')}{webui}" if isinstance(webui, str) else ""
    if not page_url:
        page_url = f"{base_url.rstrip('/')}/wiki/spaces/~pages/{page_id}"

    version_number = version.get("number")
    if not isinstance(version_number, int):
        version_number = 1

    return ConfluencePage(
        page_id=page_id,
        title=_string(raw.get("title"), "title"),
        space_id=_optional_str(raw.get("spaceId")),
        space_key=_optional_str(raw.get("spaceKey")),
        version=version_number,
        page_url=page_url,
        storage=_optional_str(storage.get("value")) or "",
    )


class _StorageToMarkdownParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._href: str | None = None
        self._in_pre = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag in {"h1", "h2", "h3"}:
            self._break()
            self._parts.append("#" * int(tag[1]))
            self._parts.append(" ")
        elif tag == "p":
            self._break()
        elif tag == "br":
            self._parts.append("\n")
        elif tag == "li":
            self._break()
            self._parts.append("- ")
        elif tag == "a":
            self._href = attr_map.get("href")
        elif tag == "pre":
            self._in_pre = True
            self._break()
            self._parts.append("```text\n")
        elif tag == "strong":
            self._parts.append("**")
        elif tag == "em":
            self._parts.append("_")
        elif tag == "code" and not self._in_pre:
            self._parts.append("`")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "p", "li", "ul", "ol"}:
            self._break()
        elif tag == "a":
            if self._href:
                self._parts.append(f" ({self._href})")
            self._href = None
        elif tag == "pre":
            self._parts.append("\n```")
            self._in_pre = False
            self._break()
        elif tag == "strong":
            self._trim_trailing_space()
            self._parts.append("** ")
        elif tag == "em":
            self._trim_trailing_space()
            self._parts.append("_ ")
        elif tag == "code" and not self._in_pre:
            self._trim_trailing_space()
            self._parts.append("` ")

    def handle_data(self, data: str) -> None:
        if self._in_pre:
            self._parts.append(data)
            return
        collapsed = " ".join(data.split())
        if collapsed:
            self._parts.append(collapsed)
            self._parts.append(" ")

    def markdown(self) -> str:
        text = "".join(self._parts)
        lines = [line.rstrip() for line in text.splitlines()]
        output: list[str] = []
        previous_blank = False
        for line in lines:
            blank = not line.strip()
            if blank and previous_blank:
                continue
            output.append(line)
            previous_blank = blank
        return "\n".join(output).strip() + "\n"

    def _break(self) -> None:
        if self._parts and not self._parts[-1].endswith("\n"):
            self._parts.append("\n\n")

    def _trim_trailing_space(self) -> None:
        if self._parts:
            self._parts[-1] = self._parts[-1].rstrip(" ")


def _default_title(spec_dir: Path) -> str:
    return f"sqlmesh-spec-kit: {spec_dir.name}"


def _display_path(path: Path) -> str:
    return str(path)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _basic_auth(email: str, api_token: str) -> str:
    token = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    return f"Basic {token}"


def _string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfluenceError(f"Confluence response is missing {field_name}.")
    return value


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) and value else None
