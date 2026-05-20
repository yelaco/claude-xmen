# Cerebro Doctor - Validate Workflow Health

Validate the Cerebro workflow configuration.

## Instructions for Cerebro

Run the checks below and report `PASS` or `FAIL` for each item. Do not modify files.

### 1. Command Namespace

Expected command files:

```bash
find .claude/commands -maxdepth 1 -type f -name '*.md' -print | sort
```

Required:
- `.claude/commands/cerebro-doctor.md`
- `.claude/commands/cerebro-index.md`
- `.claude/commands/cerebro-plan.md`
- `.claude/commands/cerebro-start-work.md`
- `.claude/commands/to-me-my-x-men.md`

Forbidden:
- legacy built-in planning command file
- legacy built-in start-work command file

### 2. Stale Command References

Avoid embedding the legacy command literals in this file. Build them in shell:

```bash
legacy_plan="/""plan"
legacy_start="/""start-work"
legacy_plan_file=".claude/commands/""plan.md"
legacy_start_file=".claude/commands/""start-work.md"
rg -n "($legacy_plan)([[:space:]]|\\x60|$)|($legacy_start)([[:space:]]|\\x60|$)|$legacy_plan_file|$legacy_start_file" CLAUDE.md README.md .claude docs .cerebro
```

Expected: no matches, except archival docs only if intentionally retained and clearly marked historical.

### 3. Model and Effort Map

```bash
python3 -m json.tool .cerebro/agent-models.json > /dev/null
```

Expected: valid JSON.

Confirm `.cerebro/agent-models.json` contains model and effort entries for all agents:

```bash
python3 - <<'PY'
import json
from pathlib import Path
required = {
    "professor-x", "beast", "emma-frost", "cyclops", "wolverine",
    "forge", "nightcrawler", "sage", "storm",
}
data = json.loads(Path(".cerebro/agent-models.json").read_text())
models = set(data.get("models", {}))
efforts = set(data.get("efforts", {}))
missing_models = sorted(required - models)
extra_models = sorted(models - required)
missing_efforts = sorted(required - efforts)
extra_efforts = sorted(efforts - required)
valid_efforts = {"low", "medium", "high"}
invalid_efforts = sorted(
    (agent, effort)
    for agent, effort in data.get("efforts", {}).items()
    if effort not in valid_efforts
)
if missing_models or extra_models or missing_efforts or extra_efforts or invalid_efforts:
    print({
        "missing_models": missing_models,
        "extra_models": extra_models,
        "missing_efforts": missing_efforts,
        "extra_efforts": extra_efforts,
        "invalid_efforts": invalid_efforts,
    })
    raise SystemExit(1)
if data.get("default_effort") not in valid_efforts:
    print({"invalid_default_effort": data.get("default_effort")})
    raise SystemExit(1)
print("model and effort coverage ok")
PY
```

### 4. Agent Frontmatter

```bash
python3 - <<'PY'
import json
from pathlib import Path
required = {"name", "description", "model", "effort"}
data = json.loads(Path(".cerebro/agent-models.json").read_text())
model_map = data["models"]
effort_map = data["efforts"]
failed = []
for path in sorted(Path(".claude/agents").glob("*.md")):
    text = path.read_text()
    if not text.startswith("---\n"):
        failed.append((str(path), "missing frontmatter"))
        continue
    end = text.find("\n---\n", 4)
    if end == -1:
        failed.append((str(path), "unterminated frontmatter"))
        continue
    frontmatter = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    keys = set(frontmatter)
    missing = sorted(required - keys)
    if missing:
        failed.append((str(path), f"missing {missing}"))
        continue
    agent = frontmatter["name"]
    expected_model = model_map.get(agent)
    if expected_model != frontmatter["model"]:
        failed.append((str(path), f"model {frontmatter['model']} != {expected_model}"))
    expected_effort = effort_map.get(agent)
    if expected_effort != frontmatter["effort"]:
        failed.append((str(path), f"effort {frontmatter['effort']} != {expected_effort}"))
if failed:
    for item in failed:
        print(item)
    raise SystemExit(1)
print("agent frontmatter ok")
PY
```

### 5. Plan Template

```bash
test -f .cerebro/templates/plan.md
rg -n "Risk Level|Approval Gates|Acceptance Criteria|Owner:|TDD:|Verify:|Rollback / Recovery" .cerebro/templates/plan.md
```

Expected: all required sections and task fields are present.

### 6. Skill Policy

```bash
test -f docs/guide/skill-policy.md
rg -n "Skill Policy|Skills are optional" CLAUDE.md .claude/agents/wolverine.md .claude/agents/storm.md .claude/agents/sage.md docs/guide/skill-policy.md
```

Expected: core policy exists and key skill-using agents mention that skills are optional.

### 7. Project Context Template

```bash
test -f .cerebro/templates/project-context.md
rg -n "Stack|Entrypoints|Commands|Architecture|Conventions|Risky Areas|Agent Notes" .cerebro/templates/project-context.md
```

Expected: all project context sections are present.

### 8. Boulder Schema

```bash
python3 -m json.tool .cerebro/schemas/boulder.schema.json > /dev/null
```

Expected: valid JSON schema file exists.

If `.cerebro/boulder.json` exists, validate required top-level fields:

```bash
python3 - <<'PY'
import json
from pathlib import Path
state_path = Path(".cerebro/boulder.json")
schema_path = Path(".cerebro/schemas/boulder.schema.json")
if not schema_path.exists():
    print("missing schema")
    raise SystemExit(1)
if not state_path.exists():
    print("no active boulder state")
    raise SystemExit(0)
state = json.loads(state_path.read_text())
required = {
    "version", "active_plan", "plan_name", "status", "risk_level",
    "started_at", "updated_at", "completed_tasks", "remaining_tasks",
    "approval_gates", "verification_history", "current_task",
}
missing = sorted(required - set(state))
if missing:
    print({"missing": missing})
    raise SystemExit(1)
print("boulder state fields ok")
PY
```

### 9. Task Result Envelope

```bash
rg -n "TASK_RESULT:|STATUS: PASS \\| FAIL \\| BLOCKED|TESTS RUN:|VERIFICATION:" .claude/agents/wolverine.md .claude/agents/storm.md .claude/agents/cyclops.md
```

Expected: Wolverine and Storm define the envelope; Cyclops requires it.

### 10. Stop Hook

```bash
test -x .claude/hooks/check-pending-todos.sh
bash .claude/hooks/check-pending-todos.sh
```

Expected: executable hook and exit code `0` when no pending todos exist.

For block behavior, use a temporary backup and restore it:

```bash
tmp="$(mktemp)"
if [ -f .cerebro/.pending-todos ]; then cp .cerebro/.pending-todos "$tmp"; else : > "$tmp"; fi
printf "doctor temporary todo\n" > .cerebro/.pending-todos
bash .claude/hooks/check-pending-todos.sh
hook_status=$?
if [ -s "$tmp" ]; then cp "$tmp" .cerebro/.pending-todos; else rm -f .cerebro/.pending-todos; fi
rm -f "$tmp"
test "$hook_status" -eq 1
```

Expected: hook exits `1` while the temporary todo exists.
