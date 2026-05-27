# 02: Ship a SQLMesh Change

This tutorial uses the official `TobikoData/sqlmesh-examples` repository and the `001_sushi/2_moderate` project.

## 1. Clone the example repo

```bash
git clone https://github.com/TobikoData/sqlmesh-examples.git
cd sqlmesh-examples/001_sushi/2_moderate
```

## 2. Initialize sqlmesh-spec-kit

Install from PyPI first:

```bash
sqlmesh-specify init sushi-moderate --engine duckdb --target .
sqlmesh-specify doctor --target .
```

To test unreleased changes from `main`, run the same commands directly from GitHub:

```bash
uvx --from git+https://github.com/duckcode-ai/sqlmesh-spec-kit.git sqlmesh-specify init sushi-moderate --engine duckdb --target .
uvx --from git+https://github.com/duckcode-ai/sqlmesh-spec-kit.git sqlmesh-specify doctor --target .
```

## 3. Write and approve the spec

Create `specs/001-customer-segments/spec.md`.

The spec should use exact status `approved` only after human approval:

```markdown
**Status:** approved

## Acceptance Criteria

- AC1: When `sushimoderate.customer_segments` is queried, the system shall return one row per customer from `sushimoderate.customers`.
- AC2: Where a customer's latest lifetime revenue is at least 100, the system shall classify the customer as `vip`.
- AC3: Where a customer's latest lifetime revenue is at least 25 and less than 100, the system shall classify the customer as `repeat`.
- AC4: Where a customer has no lifetime revenue below 25, the system shall classify the customer as `new`.
- AC5: When SQLMesh validation runs, the system shall include unit-test evidence and plan/apply evidence for the new model.
```

Validate it:

```bash
sqlmesh-specify validate specs/001-customer-segments/spec.md
```

## 4. Write and approve the plan

Create `specs/001-customer-segments/plan.md` only after the spec is approved.

The plan should list exactly the implementation files:

```text
models/customer_segments.sql
tests/test_customer_segments.yaml
```

It should include:

- target environment: `dev`
- changed model: `sushimoderate.customer_segments`
- change category: non-breaking
- restatement required: no
- forward-only decision: no
- SQLMesh evidence: `sqlmesh test` and `sqlmesh plan dev --auto-apply --no-prompts`

Set status to `approved` only after human approval.

## 5. Write tasks

Create `specs/001-customer-segments/tasks.md` only after the plan is approved.

Every task should map to AC ids and stop if implementation requires files outside the approved plan.

## 6. Implement the model

Create `models/customer_segments.sql`:

```sql
MODEL (
  name sushimoderate.customer_segments,
  kind FULL,
  cron '@daily',
  grain customer_id,
  audits (
    not_null(columns=[customer_id, segment]),
    unique_values(columns=[customer_id])
  ),
);

WITH latest_revenue AS (
  SELECT
    customer_id,
    revenue,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ds DESC) AS revenue_rank
  FROM sushimoderate.customer_revenue_lifetime
)

SELECT
  c.customer_id::INT AS customer_id,
  CASE
    WHEN COALESCE(lr.revenue, 0) >= 100 THEN 'vip'
    WHEN COALESCE(lr.revenue, 0) >= 25 THEN 'repeat'
    ELSE 'new'
  END::TEXT AS segment,
  COALESCE(lr.revenue, 0)::DOUBLE AS lifetime_revenue,
  c.status::TEXT AS status,
  c.zip::TEXT AS zip
FROM sushimoderate.customers AS c
LEFT JOIN latest_revenue AS lr
  ON c.customer_id = lr.customer_id
  AND lr.revenue_rank = 1;
```

Create `tests/test_customer_segments.yaml` with rows that verify `vip`, `repeat`, and `new`.

## 7. Validate and execute

```bash
sqlmesh-specify ci --target .
sqlmesh test
sqlmesh plan dev --auto-apply --no-prompts
```

Expected evidence:

- `sqlmesh-specify ci`: 0 errors
- `sqlmesh test`: customer-segments unit test passes
- `sqlmesh plan dev`: `sushimoderate__dev.customer_segments` is added, full-refreshed, and audits pass

## 8. Review and close

Write `specs/001-customer-segments/review.md` with:

- final diff
- AC-to-evidence table
- SQLMesh test output
- SQLMesh plan/apply output
- notes on backfill/restatement behavior

Then mark `tasks.md` status `done`. Mark `spec.md` status `shipped` only after the team accepts the result.
