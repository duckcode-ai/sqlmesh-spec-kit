# Roadmap

## Phase 1: Bootstrap and Parity

- SQLMesh-native CLI, init, lifecycle validation, doctor, report, CI, Jira, Confluence, docs, templates, commands, agents, skills, examples, and release workflow.
- Validators check project shape without executing SQLMesh.
- Humans provide `sqlmesh plan`, audit, test, apply, and promote evidence.

## Phase 2: Policy Configuration

- Add `.sqlmesh-specify/config.yml`.
- Support severity overrides and project-specific policy toggles.

## Phase 3: Plan/Diff Enforcement

- Validate changed files stay inside approved `plan.md` file lists.
- Add PR evidence for changed files, AC coverage, SQLMesh plan output, tests, and downstream impact.
- Candidate command: `sqlmesh-specify validate diff --target . --base-ref main`.

## Phase 4: SQLMesh Artifact Intelligence

- Compare before/after SQLMesh manifests or state artifacts.
- Detect changed models, downstream children, removed/renamed models, grain changes, missing tests, and semantic-layer impact.

## Phase 5: Enterprise Integration Hardening

- Improve Jira/Confluence idempotency, dry-run detail, version tracking, and failure-mode tests.
- Add stronger redaction guidance before external publishing.
