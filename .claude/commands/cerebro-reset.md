# Cerebro Reset — Clear Runtime State

Wipe the Cerebro runtime and start fresh. This command destroys all execution history, plans, notepads, and active state. Use it when a run is irreparably stuck or you want a clean slate before a new mission.

## Instructions for Cerebro

This is a **Cerebro-led single-flow operation**. Do NOT create an agent team. Do NOT spawn teammates. Handle everything directly, like `/cerebro-doctor`.

---

### 1. Scan Runtime State

Inventory what exists across all runtime directories:

```bash
test -f .cerebro/scripts/reset-runtime.py
python3 .cerebro/scripts/reset-runtime.py scan
```

---

### 2. Warn the User

Present the scan result, then output this warning **verbatim** before asking for confirmation:

```
WARNING: /cerebro-reset will permanently delete all Cerebro runtime state:

  • .cerebro/boulder.json      — active plan and execution checkpoint
  • .cerebro/.pending-todos    — legacy pending todos (may be blocking the stop hook)
  • .cerebro/pending-todos/    — task-scoped pending todos
  • .cerebro/plans/            — all implementation plans
  • .cerebro/notepads/         — all accumulated wisdom and learnings
  • .cerebro/team-runs/        — all team run manifests and coordination history

The following are NOT touched:
  • .cerebro/cerebro-identity.md
  • .cerebro/project-context.md
  • .cerebro/integrations/
  • .cerebro/schemas/
  • .cerebro/templates/
  • .cerebro/docs/
  • .cerebro/upgrade-manifest.json
  • .cerebro/upgrade-state.json

This cannot be undone. Type YES to confirm, or anything else to abort.
```

Wait for the user's reply. If the response is not exactly `YES` (case-sensitive), print:

```
Reset aborted. No files were changed.
```

...and stop.

---

### 3. Execute the Reset

Delete each item that exists:

```bash
python3 .cerebro/scripts/reset-runtime.py reset --confirm YES
```

---

### 4. Recreate Empty Runtime Directories

The reset helper restores `.cerebro/plans/`, `.cerebro/notepads/`, `.cerebro/team-runs/`, and `.cerebro/pending-todos/` as local ignored directories so the runtime is immediately usable again.

No separate command is needed for this step.

---

### 5. Verify

Confirm the runtime is clean:

```bash
python3 .cerebro/scripts/reset-runtime.py verify
```

---

### 6. Summary

Report the outcome:

```
Cerebro runtime reset complete.

  boulder.json      — cleared
  .pending-todos    — cleared
  pending-todos/    — cleared
  plans/            — cleared
  notepads/         — cleared
  team-runs/        — cleared

The runtime is ready for a new mission. Run /cerebro-index to rebuild project context, or /cerebro-plan to start a new plan.
```
