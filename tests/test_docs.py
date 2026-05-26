from __future__ import annotations

import re
from pathlib import Path

from sqlmesh_specify.init import SUPPORTED_ENGINES

ROOT = Path(__file__).resolve().parents[1]


def test_readme_local_links_exist() -> None:
    _assert_local_links_exist(ROOT / "README.md", ROOT)


def test_required_docs_exist() -> None:
    for relative in [
        "docs/getting-started.md",
        "docs/methodology.md",
        "docs/enterprise-ci.md",
        "docs/sqlmesh-ai-sdlc-walkthrough.md",
        "docs/sqlmesh-memory-and-repo-hygiene.md",
        "docs/brownfield-onboarding.md",
        "docs/skills-and-sub-agents.md",
        "docs/releasing.md",
        "docs/integrations/jira.md",
        "docs/integrations/confluence.md",
        "docs/tutorials/README.md",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
    ]:
        assert (ROOT / relative).exists(), f"missing {relative}"


def test_docs_use_sqlmesh_public_interface() -> None:
    readme = (ROOT / "README.md").read_text()
    assert "sqlmesh-spec-kit" in readme
    assert "sqlmesh-specify init analytics --engine duckdb" in readme
    assert "sqlmesh-specify validate sqlmesh" in readme
    assert "sqlmesh plan <env>" in readme


def test_tutorials_exist() -> None:
    for name in [
        "01-initialize-a-sqlmesh-repo.md",
        "02-ship-a-sqlmesh-change.md",
        "03-brownfield-enterprise-adoption.md",
        "04-skills-and-agent-handoffs.md",
        "05-jira-to-spec-workflow.md",
        "06-confluence-context-workflow.md",
    ]:
        path = ROOT / "docs" / "tutorials" / name
        assert path.exists(), f"missing tutorial {name}"
        _assert_local_links_exist(path, path.parent)


def test_engine_guides_exist_for_supported_engines() -> None:
    readme = (ROOT / "README.md").read_text()
    for engine in SUPPORTED_ENGINES:
        guide = ROOT / "docs" / "engine-guides" / f"{engine}.md"
        assert guide.exists(), f"missing engine guide {engine}"
        assert f"--engine {engine}" in guide.read_text()
        assert engine in readme


def test_release_workflow_uses_trusted_publishing() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "python -m build --sdist --wheel" in workflow
    assert "python -m twine check dist/*" in workflow


def test_docs_do_not_use_old_public_names() -> None:
    text = "\n".join(
        path.read_text() for path in [ROOT / "README.md", ROOT / "docs" / "getting-started.md"]
    )
    assert "dbt-spec" not in text.lower()
    assert "--warehouse" not in text


def _markdown_links(text: str) -> list[str]:
    return re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)


def _is_external_or_anchor(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "#"))


def _assert_local_links_exist(path: Path, base: Path) -> None:
    for link in _markdown_links(path.read_text()):
        if _is_external_or_anchor(link):
            continue
        target = link.split("#", 1)[0]
        if not target:
            continue
        assert (base / target).resolve().exists(), (
            f"{path.relative_to(ROOT)} link target does not exist: {link}"
        )
