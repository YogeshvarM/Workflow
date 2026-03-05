---
description: "Scan the codebase to identify all pandas usage and non-vectorised code. Produces a migration audit report."
agent: "agent"
tools: ["codebase", "search", "readFile"]
---

# Analyse Codebase for Pandas & Non-Vectorised Code

You are a senior data engineering analyst. Your job is to audit this codebase and produce a migration audit report.

## Your Task

1. **Search the entire codebase** for all files that import or use `pandas`
2. **For each file found**, identify:
   - All `pandas` imports
   - All DataFrame creation points (`pd.read_csv`, `pd.DataFrame()`, etc.)
   - All non-vectorised patterns:
     - `iterrows()`
     - `apply(axis=1)` or `apply(func)` on DataFrames
     - Python `for` loops that iterate over DataFrame rows
     - Row-by-row conditional logic using `.loc[]` in loops
     - `at[]` / `iat[]` in loops
   - All merge/join operations
   - All groupby operations
   - All concat operations
3. **Rate each file** by migration complexity: LOW / MEDIUM / HIGH
   - LOW: Simple reads, filters, groupbys with standard aggregations
   - MEDIUM: Multiple joins, complex groupby-apply, moderate row-wise logic
   - HIGH: Heavy row-wise iteration, complex apply functions, interleaved pandas and business logic
4. **Suggest a migration order** (easiest first to build confidence)

## Output Format

Create a file called `docs/migration-audit.md` with this structure:

```markdown
# Migration Audit Report
Generated: <date>

## Summary
- Total files using pandas: X
- Total non-vectorised patterns found: X
- Estimated complexity: X files LOW, X files MEDIUM, X files HIGH

## Recommended Migration Order
1. `path/to/file.py` - LOW - reason
2. `path/to/file.py` - MEDIUM - reason
...

## Detailed File Analysis

### `path/to/file.py`
- **Complexity**: LOW/MEDIUM/HIGH
- **Pandas imports**: list them
- **Non-vectorised patterns found**:
  - Line X: `iterrows()` - description
  - Line X: `apply(axis=1)` - description
- **Migration notes**: specific things to watch out for
```

## Rules

- Do NOT modify any code in this step
- Do NOT suggest code changes yet
- Only analyse and report
- Be thorough - check every Python file
- Include line numbers for all findings
