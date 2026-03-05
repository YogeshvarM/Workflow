---
description: "Create a step-by-step migration plan for a specific file. Pass the file and migration audit as context."
agent: "agent"
tools: ["codebase", "search", "readFile"]
---

# Plan Migration for a Single File

You are a senior data engineer planning a pandas-to-polars migration.

## Context

- Read the migration audit in `docs/migration-audit.md` for background
- Focus ONLY on the file the user specifies

## Your Task

1. **Read the target file completely** - understand every function and its purpose
2. **Map every pandas operation** to its polars equivalent
3. **Identify dependencies**:
   - What other files import from this file?
   - What does this file import?
   - Will changing return types break anything downstream?
4. **Create a step-by-step plan** where each step is:
   - Small enough to test independently
   - Focused on one function or one logical group of operations
   - Has clear before/after descriptions

## Output Format

Create a file called `docs/plan-<filename>.md` with this structure:

```markdown
# Migration Plan: <filename>
Target: `path/to/file.py`

## File Overview
Brief description of what this file does.

## Dependencies
- **Imports from this file**: list files that import from here
- **This file imports**: list relevant data-processing imports

## Breaking Changes
List any interface changes that will affect other files.

## Steps

### Step 1: <Short description>
- **Function(s)**: `function_name()`
- **Current approach**: Describe the pandas code
- **Target approach**: Describe the polars replacement
- **Key translations**:
  - `pd.operation()` → `pl.operation()`
- **Risk**: LOW/MEDIUM/HIGH
- **Test**: How to verify this step works

### Step 2: <Short description>
...
```

## Rules

- Do NOT write any code yet
- Do NOT modify any files except creating the plan document
- Be specific about line numbers and function names
- Each step must be independently testable
- Flag any step where `map_elements` might be needed and explain why
