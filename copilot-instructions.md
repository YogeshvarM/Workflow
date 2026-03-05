# Project: Pandas to Polars Migration

## Objective

This project is undergoing a performance refactoring initiative. The goal is to migrate data processing code from **pandas** to **polars** and convert non-vectorised operations into vectorised equivalents wherever possible.

## Why This Migration

- Pandas row-by-row loops (`iterrows`, `apply` with axis=1, python for-loops over DataFrames) are slow and memory-inefficient
- Polars uses Apache Arrow columnar format, lazy evaluation, and automatic multi-threading
- Vectorised operations avoid Python interpreter overhead and run at native speed

## Technology Stack

- **Current**: Python, pandas, numpy
- **Target**: Python, polars (with lazy API preferred), numpy (where needed)
- **Testing**: pytest (all existing tests must pass after refactoring)

## Migration Rules (MUST follow)

1. **Never mix pandas and polars in the same function** - each function should use one or the other during transition
2. **Prefer polars lazy API** (`pl.scan_csv`, `.lazy()`, `.collect()`) over eager where possible
3. **Replace all `iterrows()` and row-wise `apply()`** with polars expressions or `map_elements` only as last resort
4. **Replace `pd.read_csv`** with `pl.read_csv` or `pl.scan_csv`
5. **Replace `df.merge()`** with `df.join()` using polars syntax
6. **Replace `groupby().apply()`** with `group_by().agg()` using polars expressions
7. **Replace `df.loc[]` / `df.iloc[]`** with `df.filter()` and `df.select()`
8. **Replace `pd.concat()`** with `pl.concat()`
9. **Replace `fillna()`** with `fill_null()` or `fill_nan()`
10. **Keep the same function signatures** - input/output types may change but the interface contract stays the same
11. **Add type hints** for all polars DataFrames and Series (`pl.DataFrame`, `pl.LazyFrame`, `pl.Series`)
12. **Write a brief comment** on any non-obvious polars expression explaining what the pandas equivalent was

## Common Pandas-to-Polars Translations

| Pandas | Polars |
|---|---|
| `df['col']` | `df.select('col')` or `df['col']` |
| `df[df['col'] > 5]` | `df.filter(pl.col('col') > 5)` |
| `df.groupby('col').agg({'val': 'sum'})` | `df.group_by('col').agg(pl.col('val').sum())` |
| `df.apply(func, axis=1)` | `df.with_columns(...)` using expressions |
| `df.merge(other, on='key')` | `df.join(other, on='key')` |
| `pd.concat([df1, df2])` | `pl.concat([df1, df2])` |
| `df.sort_values('col')` | `df.sort('col')` |
| `df.rename(columns={...})` | `df.rename({...})` |
| `df.drop_duplicates()` | `df.unique()` |
| `df.isna()` | `df.is_null()` |

## Vectorisation Patterns

- Replace `for idx, row in df.iterrows()` → polars expressions with `with_columns`
- Replace `df['result'] = df.apply(lambda row: ..., axis=1)` → `df.with_columns(pl.when(...).then(...).otherwise(...))`
- Replace nested python loops over DataFrames → `join` + `group_by` + `agg` chains
- Replace `np.where(condition, a, b)` on pandas → `pl.when(condition).then(a).otherwise(b)`

## File Organisation

- Refactored files go in the same location as originals (in-place replacement)
- Each refactored module must have a corresponding test file
- Keep a migration log in `docs/migration-log.md`
