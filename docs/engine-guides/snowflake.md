# Snowflake guide for sqlmesh-spec-kit

## What `--engine snowflake` adds

`sqlmesh-specify init --engine snowflake` appends Snowflake-specific articles to the constitution and Snowflake-specific tables to the plan template. These cover the concerns sqlmesh-spec-kit's wedge is built around: engine-specific patterns SQLMesh Labs intentionally doesn't ship.

## What's covered

| Topic | Where |
|---|---|
| Clustering keys | Constitution Article S1 + plan additions + clustering-decisions skill |
| Engine sizing | Constitution Article S2 + plan additions |
| Query tags | Constitution Article S3 + plan additions |
| Masking & row-access policies | Constitution Article S4 + plan additions |
| Dynamic tables | Constitution Article S5 |
| Cortex / LLM-powered transformations | Constitution Article S6 |

## Clustering — the most common question

Use the `snowflake-clustering-decisions` skill (installed at `.sqlmesh-specify/skills/snowflake-clustering-decisions/SKILL.md`). The short version:

- Tables under 1 GB → no clustering
- Tables over 1 GB → cluster on the column most often in WHERE / JOIN
- Verify via `SYSTEM$CLUSTERING_INFORMATION` after first build

## Query tags — getting cost attribution right

Add to `config.yaml`:

```yaml
on-run-start:
  - "{{ set_query_tag() }}"
```

Where `set_query_tag` is a macro that emits:

```jinja
{% macro set_query_tag() %}
    {% set tag %}
        project={{ project_name }}, model={{ this.name }}, env={{ target.name }}, run_id={{ invocation_id }}
    {% endset %}
    {% do run_query("ALTER SESSION SET QUERY_TAG = '" ~ tag ~ "'") %}
{% endmacro %}
```

Then attribute cost via:

```sql
SELECT query_tag, SUM(credits_used)
FROM snowflake.account_usage.query_history
GROUP BY 1;
```

## Masking — when staging is the right boundary

The constitution requires masking at the staging layer, not the mart. Reason: marts are often built from intermediate models that have already lost track of which columns are PII. Masking at staging keeps the boundary clean.

```yaml
# models/staging/<source>/_<source>__models.yml
- name: stg_<source>__customers
  columns:
    - name: email
      meta:
        masking_policy: mask_email
```

See `models/_governance/masking_policies.sql` for the policy definitions and `tests/unit/test_masking_policies.sql` for the deterministic-fixture tests.
