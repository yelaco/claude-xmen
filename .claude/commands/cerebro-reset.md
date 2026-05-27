# Cerebro Reset — Clear Runtime State

Wipe the Cerebro runtime and start fresh. This command destroys all execution history, plans, notepads, and active state. Use it when a run is irreparably stuck or you want a clean slate before a new mission.

## Instructions for Cerebro

This is a **Cerebro-led single-flow operation**. Do NOT create an agent team. Do NOT spawn teammates. Handle everything directly, like `/cerebro-doctor`.

---

### 1. Scan Runtime State

Inventory what exists across all runtime directories:

```bash
python3 - <<'PY'
from pathlib import Path

runtime = {
    "boulder.json":       Path(".cerebro/boulder.json"),
    ".pending-todos":     Path(".cerebro/.pending-todos"),
    "plans/":             Path(".cerebro/plans"),
    "notepads/":          Path(".cerebro/notepads"),
    "team-runs/":         Path(".cerebro/team-runs"),
}

rows = []
for label, p in runtime.items():
    if not p.exists():
        rows.append((label, "absent — nothing to remove"))
        continue
    if p.is_file():
        size = p.stat().st_size
        rows.append((label, f"FILE  {size} bytes"))
    else:
        files = list(p.rglob("*"))
        items = [f for f in files if f.is_file()]
        rows.append((label, f"DIR   {len(items)} file(s)"))

for label, info in rows:
    print(f"  {label:<20} {info}")
PY
```

---

### 2. Warn the User

Present the scan result, then output this warning **verbatim** before asking for confirmation:

```
WARNING: /cerebro-reset will permanently delete all Cerebro runtime state:

  • .cerebro/boulder.json      — active plan and execution checkpoint
  • .cerebro/.pending-todos    — pending todos (may be blocking the stop hook)
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
python3 - <<'PY'
import shutil
from pathlib import Path

targets = [
    Path(".cerebro/boulder.json"),
    Path(".cerebro/.pending-todos"),
    Path(".cerebro/plans"),
    Path(".cerebro/notepads"),
    Path(".cerebro/team-runs"),
]

removed = []
skipped = []
for p in targets:
    if not p.exists():
        skipped.append(str(p))
        continue
    if p.is_file():
        p.unlink()
    else:
        shutil.rmtree(p)
    removed.append(str(p))

print("Removed:")
for r in removed:
    print(f"  {r}")
if skipped:
    print("Skipped (absent):")
    for s in skipped:
        print(f"  {s}")
PY
```

---

### 4. Recreate Empty Directories

Restore the directory stubs so the runtime is immediately usable again:

```bash
mkdir -p .cerebro/plans .cerebro/notepads .cerebro/team-runs
```

---

### 5. Verify

Confirm the runtime is clean:

```bash
python3 - <<'PY'
from pathlib import Path

checks = {
    "boulder.json absent":      not Path(".cerebro/boulder.json").exists(),
    ".pending-todos absent":    not Path(".cerebro/.pending-todos").exists(),
    "plans/ empty":             Path(".cerebro/plans").is_dir() and not any(Path(".cerebro/plans").iterdir()),
    "notepads/ empty":          Path(".cerebro/notepads").is_dir() and not any(Path(".cerebro/notepads").iterdir()),
    "team-runs/ empty":         Path(".cerebro/team-runs").is_dir() and not any(Path(".cerebro/team-runs").iterdir()),
}

all_pass = True
for label, ok in checks.items():
    status = "PASS" if ok else "FAIL"
    if not ok:
        all_pass = False
    print(f"  {status}  {label}")

if not all_pass:
    raise SystemExit(1)
print("Runtime clean.")
PY
```

---

### 6. Summary

Report the outcome:

```
Cerebro runtime reset complete.

  boulder.json      — cleared
  .pending-todos    — cleared
  plans/            — cleared
  notepads/         — cleared
  team-runs/        — cleared

The runtime is ready for a new mission. Run /cerebro-index to rebuild project context, or /cerebro-plan to start a new plan.
```
