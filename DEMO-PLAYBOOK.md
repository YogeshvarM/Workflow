# Demo Playbook: Pandas → Polars Migration Workflow

> **Audience**: PM & Engineering Team
> **Duration**: ~15 minutes
> **Pre-requisite**: VS Code with GitHub Copilot enabled, the `.github/` folder and `src/sales_pipeline.py` in the project root.

---

## Setup (Before the Demo)

```
your-project/
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   └── polars-standards.instructions.md
│   ├── prompts/
│   │   ├── analyse.prompt.md
│   │   ├── plan.prompt.md
│   │   └── generate.prompt.md
│   └── agents/
│       ├── implement.agent.md
│       └── validate.agent.md
└── src/
    └── sales_pipeline.py
```

1. Copy all the files into your project
2. Open VS Code and make sure Copilot Chat is visible
3. Optionally run `python src/sales_pipeline.py` first to show how slow it is (this is a great opener for the demo)

---

## The Demo

### Opening: Show the Problem (2 min)

Open a terminal and run:

```bash
python src/sales_pipeline.py
```

Point out the timing output:

```
[5/8] Calculating revenue (iterrows - SLOW)...       Done in 12.3s
[6/8] Classifying deals (apply axis=1 - SLOW)...     Done in 8.7s
[7/8] Applying regional adjustments (loc loop - SLOW)... Done in 45.2s
```

Say: *"This is 100k rows. In production we process millions. The problem is scattered across 8 functions using iterrows, apply, and for-loops. Manually finding and rewriting all of this is tedious and error-prone. Here's how we automate it."*

---

### Step 1: Analyse — Find Every Problem (3 min)

**What to explain**: *"First, we scan the entire codebase to find every file using pandas and every non-vectorised pattern. This is a prompt file — a reusable task I invoke on demand."*

**Open Copilot Chat and type:**

```
/analyse
```

**What happens**: Copilot reads the prompt file, scans the codebase, and produces `docs/migration-audit.md` with:
- Every file that imports pandas
- Every `iterrows()`, `apply(axis=1)`, `.loc[]` loop, `groupby().apply()` found
- Line numbers for each finding
- Complexity rating per file (LOW / MEDIUM / HIGH)
- A recommended migration order

**What to show the team**: Open `docs/migration-audit.md` and walk through the findings. Point out that it found all 8 anti-patterns in `sales_pipeline.py` with exact line numbers.

**Then say**: *"We now have a complete map. No guessing. Let's plan the first file."*

**Clear the chat** (click the + icon to start a new session).

---

### Step 2: Plan — Design the Migration (3 min)

**What to explain**: *"Now we pick one file and plan how to migrate it step by step. Each step is small enough to test on its own."*

**Type in Copilot Chat:**

```
/plan #file:src/sales_pipeline.py
```

**What happens**: Copilot reads the file, maps every pandas operation to polars, checks dependencies, and produces `docs/plan-sales_pipeline.md` with steps like:

```
Step 1: Migrate calculate_revenue_slow()
  Current: iterrows() loop computing gross, discount, net
  Target: pl.with_columns() with three expressions
  Risk: LOW

Step 2: Migrate classify_deals()
  Current: apply(axis=1) calling _classify_deal_size()
  Target: pl.when().then().otherwise() chain
  Risk: MEDIUM
  ...
```

**What to show the team**: Open the plan file. Point out that each step has a clear before/after, risk level, and how to test it.

**Then say**: *"The plan doesn't touch any code. It's a document we can review before committing to anything. Now let's generate the actual code."*

**Clear the chat.**

---

### Step 3: Generate — Write All the Code (3 min)

**What to explain**: *"This is where the heavy thinking happens. We use our strongest model to write every line of polars code. But it writes into a document, not into the project files. Think of it as a blueprint."*

**Type in Copilot Chat:**

```
/generate #file:docs/plan-sales_pipeline.md
```

**What happens**: Copilot produces `docs/implementation-sales_pipeline.md` — a long markdown file containing:
- The original pandas code for each step
- The complete replacement polars code
- Verification tests for each step
- Checkboxes to track progress
- A final complete version of the entire refactored file

**What to show the team**: Scroll through the implementation doc. Point out that:
- Every code block is complete and runnable (no pseudocode)
- It includes migration comments like `# Migrated from pandas: iterrows loop`
- The checkboxes let us track which steps are done

**Then say**: *"We've now spent our strong model budget writing correct code. Now a smaller, cheaper model just applies it mechanically."*

**Clear the chat.**

---

### Step 4: Implement — Apply Code Step by Step (3 min)

**What to explain**: *"Now we switch to a custom agent. This agent is deliberately restricted — it can't improvise or rewrite code. It just takes what's in the document and applies it."*

**Switch to the "Implement Migration" agent** (click the agent picker in the chat).

**Type:**

```
Apply the next step from #file:docs/implementation-sales_pipeline.md
```

**What happens**:
- Agent finds Step 1 (first unchecked checkbox)
- Replaces the `calculate_revenue_slow` function with the polars version
- Runs the verification test if one exists
- Checks off Step 1 in the implementation doc
- Stops and reports back

**What to show the team**: Show the diff in the file. Show the checkbox getting checked. Then say:

*"I review this, test it, and if it's good I send the exact same message again. It picks up Step 2 automatically."*

**Send the same message again** to show it picking up Step 2.

**Then say**: *"This continues until every checkbox is done. If something breaks, the agent stops and I decide what to do — it never tries to fix things on its own."*

---

### Step 5: Validate — Verify the Migration (1 min)

**What to explain**: *"Once all steps are done, we run the validation agent. It checks that no pandas is left, no row-by-row loops survive, and polars best practices are followed."*

**Switch to the "Validate Migration" agent.**

**Type:**

```
Validate #file:src/sales_pipeline.py
```

**What happens**: Produces a validation report:

```
| Check                    | Verdict |
|--------------------------|---------|
| No remaining pandas      | ✅      |
| No non-vectorised code   | ✅      |
| Polars best practices    | ✅      |
| Tests passing            | ✅      |
```

---

### Closing: Show the Result (1 min)

Run the refactored pipeline:

```bash
python src/sales_pipeline.py
```

Compare the timings. The operations that took 12s, 8s, 45s should now complete in under a second each.

---

## Key Talking Points for PM

| Concern | Answer |
|---|---|
| **"How long does this take per file?"** | The 5-step cycle takes about 15-20 minutes per file, including review. Manual rewriting the same file correctly could take hours. |
| **"What if the generated code is wrong?"** | The implement agent applies one step at a time. You test after each step. If something breaks, you fix just that step. You're never dealing with a massive broken changeset. |
| **"Can anyone on the team do this?"** | Yes. The workflow files are in the repo. Anyone types `/analyse`, `/plan`, `/generate` and switches to the implement agent. The intelligence is in the prompt files, not in the person's head. |
| **"What about our other projects?"** | The `.github/` folder is portable. Copy it to any repo with pandas code. Adjust `copilot-instructions.md` for project-specific details. The prompts and agents work as-is. |
| **"How do we track progress?"** | The migration audit gives us the full list. Each implementation doc has checkboxes. The validate agent confirms completion. It's all in version-controlled markdown files. |
| **"What does this cost?"** | Strong model is used only for plan + generate (2 invocations per file). All implementation uses a small/free model. Most of the token budget goes to thinking, not typing. |

---

## What Each Piece Does (Quick Reference)

```
INSTRUCTIONS (always active, you never invoke them)
├── copilot-instructions.md      → "Here's our project, here are the pandas→polars rules"
└── polars-standards.instructions.md → "For any .py file, follow these polars patterns"

PROMPTS (you invoke these with / in chat)
├── /analyse   → Scan codebase, find all problems, make audit report
├── /plan      → Plan one file's migration step by step
└── /generate  → Write all the polars code into a blueprint doc

AGENTS (you switch to these in the agent picker)
├── Implement Migration  → Apply code from blueprint, one step at a time
└── Validate Migration   → Check that migration is complete and correct
```

---

## After the Demo

1. Share the `.github/` folder with the team via the repo
2. Start with the easiest file from the audit report
3. Iterate on the prompt files as you learn what works for your codebase
4. The workflow files are just markdown — anyone can improve them
