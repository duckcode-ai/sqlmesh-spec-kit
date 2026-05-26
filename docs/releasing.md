# Releasing

The package is PyPI-ready through Hatchling and GitHub Trusted Publishing.

Local verification:

```bash
uv run --extra dev ruff check src tests
uv run --extra dev mypy src tests
uv run --extra dev pytest
uv run --extra dev python -m build --sdist --wheel
uv run --extra dev python -m twine check dist/*
```

Create a GitHub release tag such as `v0.1.0` to publish.
