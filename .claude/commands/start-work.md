# Start Work — Activate Cyclops

Activate Cyclops to execute the latest plan.

## Instructions for Cerebro

```
Agent(subagent_type="cyclops", prompt="""
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
  - Delegate code to Wolverine
  - Delegate UI to Storm
  - Consult Forge for architecture decisions
  - Accumulate wisdom after each task
  - Verify results independently before marking complete
  - Update boulder.json after each task
  - Report when all tasks are done with verification evidence
""")
```
