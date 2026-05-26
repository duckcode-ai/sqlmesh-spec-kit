"""Load packaged template assets from the installed sqlmesh-specify package."""
from __future__ import annotations

from functools import cache
from importlib import resources
from pathlib import Path

_KNOWN_ASSETS = {"memory", "templates", "presets", "skills", "commands", "agents"}


@cache
def asset_dir(kind: str) -> Path:
    """Return the on-disk path to a packaged asset directory.

    Resolves in two phases so both wheel installs and editable installs work:
      1. Look inside the installed package at `sqlmesh_specify/_assets/<kind>/`.
         This is where hatch's force-include lands assets in the wheel.
      2. Fall back to the top-level `<kind>/` directory in the source tree.
         This is the layout an editable install sees (no copy step happens).

    Args:
        kind: One of "memory", "templates", "presets", "skills", "commands", "agents".

    Returns:
        Absolute Path to the directory.

    Raises:
        ValueError: If `kind` is not a known asset directory.
        FileNotFoundError: If neither candidate location exists.
    """
    if kind not in _KNOWN_ASSETS:
        raise ValueError(f"unknown asset kind: {kind}")

    package_files = resources.files("sqlmesh_specify") / "_assets" / kind
    packaged = Path(str(package_files))
    if packaged.is_dir():
        return packaged

    # Editable install: walk up from the package's __init__.py to find the repo root,
    # which contains the top-level asset directories.
    repo_root = Path(str(resources.files("sqlmesh_specify"))).resolve().parents[1]
    editable = repo_root / kind
    if editable.is_dir():
        return editable

    raise FileNotFoundError(
        f"asset directory '{kind}' not found at {packaged} or {editable}"
    )


def load_template(name: str) -> str:
    """Read a top-level template file.

    Args:
        name: Template name without extension (e.g., "spec" loads spec-template.md).

    Returns:
        The template content as a string.
    """
    candidates = [
        asset_dir("templates") / f"{name}-template.md",
        asset_dir("templates") / f"{name}.md",
        asset_dir("templates") / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text()
    raise FileNotFoundError(f"no template found for name '{name}'")
