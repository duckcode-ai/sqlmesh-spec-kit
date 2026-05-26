# Confluence Integration

Set `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN`.

```bash
sqlmesh-specify confluence pull-page 12345 --to specs/001-change/context/source.md
sqlmesh-specify confluence publish --spec-dir specs/001-change --space-key DATA --dry-run
sqlmesh-specify confluence sync --spec-dir specs/001-change --dry-run
```

Published pages are summaries. The local spec directory remains the source of truth.
