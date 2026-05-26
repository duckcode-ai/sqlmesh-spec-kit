# Reviewing Audits and Tests

Use this when checking SQLMesh validation coverage.

Checklist:

- Map every acceptance criterion to at least one test, audit, review check, or plan artifact.
- Prefer SQLMesh audits for data quality invariants that must run with the project.
- Check tests cover changed model grain, joins, edge cases, and downstream contracts.
- Block when evidence is missing or not tied to AC ids.
