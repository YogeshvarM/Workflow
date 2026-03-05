---
applyTo: "**/*.py"
---

# Polars & Vectorisation Standards

When working with any Python file in this project, follow these standards:

## Polars Expression Best Practices

- Always use `pl.col()` for column references inside expressions
- Chain expressions rather than creating intermediate variables
- Use `.alias()` to rename expression outputs
- Prefer `with_columns` over `select` when adding columns to an existing frame
- Use `pl.lit()` for constant values inside expressions

## Performance Rules

- NEVER use `iterrows()`, `apply(axis=1)`, or python for-loops to iterate over DataFrame rows
- NEVER use `map_elements` unless there is absolutely no expression-based alternative (document why)
- ALWAYS prefer lazy evaluation: start with `scan_csv` or `.lazy()` and call `.collect()` at the end
- ALWAYS use polars native expressions instead of calling python functions row-by-row
- Use `sink_csv` / `sink_parquet` for large output to avoid collecting entire frames into memory
- For conditional logic, use `pl.when().then().otherwise()` chains, not python if/else

## Code Style

- Import polars as: `import polars as pl`
- Type hint DataFrames: `df: pl.DataFrame` or `lf: pl.LazyFrame`
- Group related transformations into single `with_columns` calls where possible
- Add a docstring to every function explaining what transformation it performs
- If the function previously used pandas, include a one-line comment: `# Migrated from pandas: <brief description of old approach>`
