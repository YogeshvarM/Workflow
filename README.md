# Pandas → Polars Migration: Agentic Workflow

## The Problem

Our data processing is slow because we use pandas with non-vectorised code (row-by-row loops, `iterrows`, `apply(axis=1)`). This workflow uses VS Code Copilot's custom instructions, prompt files, and agents to systematically migrate to polars with vectorised operations.

## How It Works

We separate **thinking** from **doing**. A strong model plans and writes the code. A small model mechanically applies it. This maximises quality while minimising cost.

```
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  ANALYSE │────▶│   PLAN   │────▶│ GENERATE │────▶│IMPLEMENT │────▶│ VALIDATE │
  │ (prompt) │     │ (prompt) │     │ (prompt) │     │ (agent)  │     │ (agent)  │
  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
   Scan code &      Plan one file    Write all code    Apply code       Verify no
   find targets     step by step     into a doc        step by step     pandas left
                                     ↑                 ↑
                              Strong model        Small model
                         (clear context after)  (clear context after)
```

## File Structure

```
.github/
├── copilot-instructions.md                    # Always-on project context
├── instructions/
│   └── polars-standards.instructions.md       # Auto-applied to all .py files
├── prompts/
│   ├── analyse.prompt.md                      # Step 1: Audit the codebase
│   ├── plan.prompt.md                         # Step 2: Plan one file's migration
│   └── generate.prompt.md                     # Step 3: Write all the code
└── agents/
    ├── implement.agent.md                     # Step 4: Apply code mechanically
    └── validate.agent.md                      # Step 5: Verify correctness
```

## Setup

1. Copy the entire `.github/` folder into your project root
2. In VS Code, ensure Copilot chat is enabled
3. Install polars: `pip install polars`

## The Workflow: Step by Step

### Step 1 — Analyse (Prompt File)

Open Copilot Chat. Type:

```
/analyse
```

This scans the entire codebase, finds every file using pandas, identifies non-vectorised patterns, rates each file by complexity, and produces `docs/migration-audit.md`.

**You now have a complete map of what needs to change.**

Clear the chat context (start a new session).

---

### Step 2 — Plan (Prompt File)

Pick a file from the audit report. Type:

```
/plan #file:src/data_processing.py
```

This reads the target file, maps every pandas operation to its polars equivalent, identifies dependencies, and produces `docs/plan-data_processing.md` with small testable steps.

**You now have a step-by-step plan for one file.**

Clear the chat context.

---

### Step 3 — Generate (Prompt File)

Pass the plan to your strongest model. Type:

```
/generate #file:docs/plan-data_processing.py.md
```

This writes ALL the replacement code into `docs/implementation-data_processing.md` — a long markdown document with every piece of code needed, organised by step, with checkboxes.

**The code is NOT in the project yet. It's in a blueprint document.**

Clear the chat context.

---

### Step 4 — Implement (Custom Agent)

Switch to the **Implement Migration** agent. Type:

```
Apply the next step from #file:docs/implementation-data_processing.md
```

The agent finds the first unchecked step, applies the code exactly as written, runs verification, checks off the step, and stops.

You then:
1. Review the change
2. Test it
3. Send the same prompt again — it picks up the next step
4. Repeat until all steps are checked off

---

### Step 5 — Validate (Custom Agent)

Switch to the **Validate Migration** agent. Type:

```
Validate #file:src/data_processing.py
```

This checks for any remaining pandas code, non-vectorised patterns, polars best practice violations, and runs tests. Produces a pass/fail report.

---

### Repeat for Next File

Go back to Step 2 with the next file from your audit. The audit report (`docs/migration-audit.md`) stays as your checklist.

## What Each File Does

| File | Type | Purpose |
|---|---|---|
| `copilot-instructions.md` | Instruction | Project context, translation rules, always active |
| `polars-standards.instructions.md` | Instruction | Code standards, auto-applied to all `.py` files |
| `analyse.prompt.md` | Prompt | Audit codebase, find all pandas usage |
| `plan.prompt.md` | Prompt | Create migration plan for one file |
| `generate.prompt.md` | Prompt | Write all polars code into a document |
| `implement.agent.md` | Agent | Apply code from document into project |
| `validate.agent.md` | Agent | Verify migration correctness |

## Why This Approach

1. **Instructions** = always-on context. Every request knows about the polars migration rules without you repeating them.
2. **Prompt files** = on-demand tasks. You invoke them with `/` only when needed. They do the thinking.
3. **Agents** = specialised modes. They change Copilot's behaviour entirely. The implement agent is deliberately restricted — it can't improvise.
4. **Context clearing** between steps avoids context rot and keeps each step focused.
5. **Thinking vs Doing split** lets you use your best model for the hard part (writing correct code) and a cheap model for the easy part (pasting it in).
