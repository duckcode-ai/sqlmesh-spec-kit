AUDIT (
  name not_null,
);

SELECT *
FROM @this_model
WHERE @EACH(@columns, c -> c IS NULL);
