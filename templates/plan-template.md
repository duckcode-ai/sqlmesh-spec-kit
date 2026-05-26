# Plan: <Feature Name>

**Author:** <name>
**Date:** <YYYY-MM-DD>
**Status:** proposed
**Spec:** <relative path to spec.md>

Status must be exactly one of: `proposed`, `approved`, `superseded`.

## Architecture

<Describe the SQLMesh design. Include target environment, model ownership, dependencies, and rollout shape.>

## SQLMesh Plan

| Field | Decision |
|---|---|
| Target environment | <dev/staging/prod environment> |
| Change category | <breaking|non-breaking|forward-only|restatement> |
| Forward-only decision | <yes/no and why> |
| Restatement required | <yes/no and scope> |
| Backfill window | <none or date range> |
| Snapshots affected | <snapshot/model names> |
| Apply/promote path | <how evidence will be captured before promotion> |

## Files to Add

| Path | Purpose | ACs |
|---|---|---|
| <path> | <why this file is needed> | AC1 |

## Files to Modify

| Path | Purpose | ACs |
|---|---|---|
| <path> | <planned change> | AC1 |

## Files to Delete

| Path | Reason | ACs |
|---|---|---|
| None |  |  |

## Audits and Tests

| Evidence | Command or artifact | ACs |
|---|---|---|
| SQLMesh plan | `sqlmesh plan dev` output attached to review | AC1 |
| SQLMesh tests | `sqlmesh test` or project-specific equivalent | AC1 |
| Audits | <audit command/result or inline audit evidence> | AC2 |

## Downstream Impact

<List downstream children, dashboards, exports, semantic-layer objects, and owners to notify.>

## SQLMesh Plan/Apply Evidence

Paste or link:

- `sqlmesh plan <env>` output summary
- unexpected backfill/restatement review, if any
- audit/test evidence
- apply/promote evidence before shipping
