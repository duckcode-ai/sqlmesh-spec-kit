MODEL (
  name sushi.example,
  kind FULL,
  audits (not_null(columns := (id)))
);

SELECT 1 AS id;
