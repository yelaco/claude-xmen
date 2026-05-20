# Cerebro Start Work — Activate Cyclops

Activate Cyclops to execute the latest plan.

## Instructions for Cerebro

Read `.cerebro/agent-models.json`, then read Cyclops persona and activate for plan execution. Resolve `model = models["cyclops"] || default_model` and `reasoning_effort = efforts["cyclops"] || default_effort`.

```
[Read .cerebro/agent-models.json]
[Read .claude/agents/cyclops.md]

Agent(subagent_type="general-purpose", model="[models.cyclops || default_model]", reasoning_effort="[efforts.cyclops || default_effort]", prompt="""
[cyclops.md content]

---

Begin execution now.

First, check boulder state:
  cat .cerebro/boulder.json

If boulder.json EXISTS → RESUME MODE:
  - Read the existing state
  - Identify remaining tasks
  - Continue from the last completed checkpoint
  - Tell the user: "Resuming [plan name] — [N] of [total] tasks complete"

If boulder.json DOES NOT EXIST → INIT MODE:
  - Find the most recently modified file in .cerebro/plans/
  - Create .cerebro/boulder.json with initial state
  - Begin from task 1
  - Tell the user: "Starting [plan name] — [N] tasks total"

Then execute all tasks:
  - Delegate code to Wolverine — read .claude/agents/wolverine.md, spawn as general-purpose
  - Delegate UI to Storm — read .claude/agents/storm.md, spawn as general-purpose
  - Consult Forge for architecture decisions — read .claude/agents/forge.md, spawn as general-purpose
  - Enforce approval gates from the plan before delegation
  - Accumulate wisdom after each task
  - Verify results independently before marking complete
  - Never mark a task complete from worker self-report alone
  - Update boulder.json after each task
  - Report when all tasks are done with verification evidence
""")
```
