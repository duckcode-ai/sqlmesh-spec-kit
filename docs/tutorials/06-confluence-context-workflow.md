# 06: Confluence Context Workflow

```bash
sqlmesh-specify confluence pull-page 12345 --to specs/001-change/context/source.md
sqlmesh-specify confluence publish --spec-dir specs/001-change --space-key DATA --dry-run
```

Use Confluence as source context and summary publishing. Keep the approved local spec directory as the implementation source of truth.
