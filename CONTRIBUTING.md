# Contributing

Use Python 3.11 or newer.

```bash
uv run --extra dev ruff check src tests
uv run --extra dev mypy src tests
uv run --extra dev pytest
uv run --extra dev python -m build --sdist --wheel
uv run --extra dev python -m twine check dist/*
```

Engine presets live in `presets/<engine>/` and may add constitution and plan sections. They must not weaken the base lifecycle gates.
