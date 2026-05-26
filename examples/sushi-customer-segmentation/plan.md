# Plan: Customer Segmentation

**Author:** Example
**Date:** 2026-05-26
**Status:** approved
**Spec:** spec.md

## Architecture

Add `models/customer_segments.sql` in the `dev` environment with one row per customer.

## SQLMesh Plan

| Field | Decision |
|---|---|
| Target environment | dev |
| Change category | non-breaking |
| Forward-only decision | no |
| Restatement required | no |
| Backfill window | none |
| Snapshots affected | `sushi.customer_segments` |
| Apply/promote path | review `sqlmesh plan dev`, then apply after approval |

## Files to Add

| Path | Purpose | ACs |
|---|---|---|
| `models/customer_segments.sql` | customer segmentation model | AC1, AC2 |
| `audits/customer_segments.sql` | dormant/active classification audit | AC2 |

## Files to Modify

| Path | Purpose | ACs |
|---|---|---|
| None |  |  |

## Files to Delete

| Path | Reason | ACs |
|---|---|---|
| None |  |  |

## Audits and Tests

| Evidence | Command or artifact | ACs |
|---|---|---|
| SQLMesh plan | `sqlmesh plan dev` | AC3 |
| SQLMesh tests | `sqlmesh test` | AC1, AC2 |
| Audits | customer segment audit output | AC2 |

## Downstream Impact

Growth analytics dashboards can use the new model after promotion.

## SQLMesh Plan/Apply Evidence

Attach `sqlmesh plan dev`, audit/test output, and apply evidence before shipping.
