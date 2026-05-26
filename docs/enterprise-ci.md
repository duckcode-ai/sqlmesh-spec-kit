# Enterprise CI

Recommended checks:

```bash
ruff check src tests
mypy src tests
pytest
python -m build --sdist --wheel
python -m twine check dist/*
sqlmesh-specify ci --target .
```

PR evidence should include:

- spec, plan, and tasks lifecycle status
- `sqlmesh plan <env>` output
- audit and test results
- unexpected backfill/restatement review
- downstream owner approval when needed
- apply/promote evidence before marking a spec `shipped`
