# 01: Initialize a SQLMesh Repo

```bash
sqlmesh-specify init analytics --engine duckdb --target .
sqlmesh-specify doctor --target .
sqlmesh-specify validate sqlmesh --target .
```

Record:

- the SQLMesh config file used
- engine preset
- first gaps from doctor
- where specs will live
