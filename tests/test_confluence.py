"""Tests for Confluence bridge helpers."""
from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner
from pytest import MonkeyPatch

from sqlmesh_specify.cli import main
from sqlmesh_specify.confluence import (
    ConfluencePage,
    PublishedPage,
    publish_spec_dir,
    pull_page_to_context,
    storage_to_markdown,
    sync_spec_dir,
)


class FakeConfluenceClient:
    def __init__(self, page: ConfluencePage | None = None) -> None:
        self.page = page or _page()
        self.created: list[dict[str, str | None]] = []
        self.updated: list[dict[str, str]] = []

    def get_page(self, page_id: str) -> ConfluencePage:
        assert page_id == self.page.page_id
        return self.page

    def resolve_space_id(self, space_key: str) -> str:
        assert space_key == "DATA"
        return "space-123"

    def create_page(
        self,
        *,
        space_id: str,
        title: str,
        storage: str,
        parent_id: str | None = None,
    ) -> PublishedPage:
        self.created.append(
            {
                "space_id": space_id,
                "title": title,
                "storage": storage,
                "parent_id": parent_id,
            }
        )
        return PublishedPage(
            page_id="999",
            title=title,
            page_url="https://example.atlassian.net/wiki/spaces/DATA/pages/999",
            created=True,
        )

    def update_page(self, *, page_id: str, title: str, storage: str) -> PublishedPage:
        self.updated.append({"page_id": page_id, "title": title, "storage": storage})
        return PublishedPage(
            page_id=page_id,
            title=title,
            page_url=f"https://example.atlassian.net/wiki/spaces/DATA/pages/{page_id}",
            created=False,
        )


def test_cli_help_lists_confluence_group() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0, result.output
    assert "confluence" in result.output

    confluence_result = runner.invoke(main, ["confluence", "--help"])
    assert confluence_result.exit_code == 0, confluence_result.output
    assert "pull-page" in confluence_result.output
    assert "publish" in confluence_result.output
    assert "sync" in confluence_result.output


def test_storage_to_markdown_converts_basic_storage() -> None:
    markdown = storage_to_markdown(
        "<h1>Metric definitions</h1><p><strong>Owner:</strong> Finance</p>"
        "<ul><li>Net revenue excludes refunds</li></ul>"
    )

    assert "# Metric definitions" in markdown
    assert "**Owner:** Finance" in markdown
    assert "- Net revenue excludes refunds" in markdown


def test_pull_page_to_context_records_manifest(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs" / "001-player-journey"
    output_path = spec_dir / "context" / "metric-definitions.md"
    client = FakeConfluenceClient()

    page = pull_page_to_context(
        client=client,
        page_id="123",
        output_path=output_path,
    )

    assert page.title == "Player metric definitions"
    context = output_path.read_text()
    assert "# Player metric definitions" in context
    assert "Net revenue excludes refunds" in context

    manifest = yaml.safe_load((spec_dir / "confluence.yml").read_text())
    assert manifest["spec_dir"] == str(spec_dir)
    assert manifest["source_pages"][0]["page_id"] == "123"
    assert manifest["source_pages"][0]["context_file"] == str(output_path)


def test_publish_spec_dir_creates_page_and_manifest(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs" / "001-player-journey"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n\nApproved player journey spec.")
    (spec_dir / "plan.md").write_text("# Plan\n\nUpdate fct_player_performance.")
    client = FakeConfluenceClient()

    page = publish_spec_dir(
        client=client,
        spec_dir=spec_dir,
        space_key="DATA",
        parent_id="456",
    )

    assert page.created is True
    assert client.created[0]["space_id"] == "space-123"
    assert client.created[0]["parent_id"] == "456"
    assert "Approved player journey spec." in str(client.created[0]["storage"])

    manifest = yaml.safe_load((spec_dir / "confluence.yml").read_text())
    assert manifest["page_id"] == "999"
    assert manifest["space_key"] == "DATA"
    assert manifest["parent_id"] == "456"


def test_confluence_publish_dry_run_does_not_require_credentials(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    for name in ("CONFLUENCE_BASE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    spec_dir = tmp_path / "specs" / "001-player-journey"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n\nApproved spec.")

    result = CliRunner().invoke(
        main,
        [
            "confluence",
            "publish",
            "--spec-dir",
            str(spec_dir),
            "--space-key",
            "DATA",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "would create Confluence page <new>" in result.output
    assert not (spec_dir / "confluence.yml").exists()


def test_sync_spec_dir_updates_existing_page(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs" / "001-player-journey"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Spec\n\nApproved spec.")
    (spec_dir / "confluence.yml").write_text(
        yaml.safe_dump(
            {
                "page_id": "123",
                "title": "Player journey summary",
                "page_url": "https://example.atlassian.net/wiki/spaces/DATA/pages/123",
            }
        )
    )
    client = FakeConfluenceClient()

    page = sync_spec_dir(client=client, spec_dir=spec_dir)

    assert page.created is False
    assert client.updated[0]["page_id"] == "123"
    assert client.updated[0]["title"] == "Player journey summary"
    assert "Approved spec." in client.updated[0]["storage"]


def _page() -> ConfluencePage:
    return ConfluencePage(
        page_id="123",
        title="Player metric definitions",
        space_id="space-123",
        space_key="DATA",
        version=7,
        page_url="https://example.atlassian.net/wiki/spaces/DATA/pages/123",
        storage="<h1>Player metrics</h1><p>Net revenue excludes refunds.</p>",
    )
