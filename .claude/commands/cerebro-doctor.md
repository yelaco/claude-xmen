# Cerebro Doctor - Validate Workflow Health

Validate the Cerebro workflow configuration.

## Instructions for Cerebro

Run the checks below and report `PASS` or `FAIL` for each item. Do not modify files.

### 1. Command Namespace

```bash
find .claude/commands -maxdepth 1 -type f -name '*.md' -print | sort
```

Required:
- `.claude/commands/cerebro-doctor.md`
- `.claude/commands/cerebro-index.md`
- `.claude/commands/cerebro-plan.md`
- `.claude/commands/cerebro-reset.md`
- `.claude/commands/cerebro-setup.md`
- `.claude/commands/cerebro-start-work.md`
- `.claude/commands/cerebro-upgrade.md`
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

### 3. Native Agent Frontmatter

```bash
test -f .cerebro/scripts/validate-agent-frontmatter.py
python3 .cerebro/scripts/validate-agent-frontmatter.py
```

### 4. Native Orchestration Compatibility

```bash
test ! -f .cerebro/agent-""models.json
catch_all="general-""purpose"
model_map="agent-""models"
reasoning_param="reasoning_""effort"
dm_key="default_""model"
de_key="default_""effort"
models_lookup="models""\\["
efforts_lookup="efforts""\\["
rg -n "$catch_all|$model_map|$reasoning_param|$dm_key|$de_key|$models_lookup|$efforts_lookup" CLAUDE.md README.md .claude docs .cerebro
```

Expected: first command passes; second command has no matches.

Confirm subagent files do not contain nested spawn instructions:

```bash
rg -n "Agent\\(" .claude/agents
```

Expected: no matches.

Confirm Cyclops no longer uses direct teammate handoff contracts from the pre-team workflow:

```bash
target_key="TARGET_""AGENT"
handoff_key="HAND""OFF"
call_wolverine="CALL_""WOLVERINE"
call_storm="CALL_""STORM"
call_forge="CALL_""FORGE"
rg -n "$target_key|$handoff_key|$call_wolverine|$call_storm|$call_forge" .claude/agents/cyclops.md .claude/commands
```

Expected: no matches.

Confirm every workflow command uses agent teams:

```bash
rg -n "Create an agent team|agent team lead|teammate|team mailbox|shared task list|Team Run Manifest" .claude/commands/cerebro-index.md .claude/commands/cerebro-plan.md .claude/commands/cerebro-start-work.md .claude/commands/to-me-my-x-men.md
```

Expected: each workflow command has team-mode instructions.

### 5. Plan Template

```bash
test -f .cerebro/templates/plan.md
rg -n "Risk Level|Approval Gates|Acceptance Criteria|Owner:|TDD:|Verify:|Rollback / Recovery" .cerebro/templates/plan.md
```

Expected: all required sections and task fields are present.

### 6. Skill Policy

```bash
test -f .cerebro/docs/skill-policy.md
rg -n "Skill Policy|Skills are optional" .cerebro/cerebro-identity.md .claude/agents/wolverine.md .claude/agents/storm.md .claude/agents/sage.md
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

If `.cerebro/boulder.json` exists, validate it against the schema contract:

```bash
test -f .cerebro/scripts/validate-boulder.py
python3 .cerebro/scripts/validate-boulder.py
```

### 9. Team Run Schema

```bash
test -d .cerebro/team-runs
test -f .cerebro/templates/team-run.json
test -f .cerebro/schemas/team-run.schema.json
python3 -m json.tool .cerebro/templates/team-run.json > /dev/null
python3 -m json.tool .cerebro/schemas/team-run.schema.json > /dev/null
test -f .cerebro/scripts/validate-team-runs.py
python3 .cerebro/scripts/validate-team-runs.py
rg -n "team-runs|team-run.schema.json|Team Run Manifest|TEAM_RUN_PATCH" .cerebro/cerebro-identity.md README.md .claude/commands .claude/agents/cyclops.md .cerebro/docs .cerebro/project-context.md
```

Expected: team run manifest template/schema are valid JSON and all team workflows mention the run manifest.

### 10. Hook Wiring

```bash
python3 -m json.tool .claude/settings.json > /dev/null
test -x .claude/hooks/check-pending-todos.sh
test -x .claude/hooks/check-task-result-envelope.sh
test -x .claude/hooks/log-team-event.sh
rg -n '"Stop"|"SubagentStop"|"TaskCreated"|"TaskCompleted"|"TeammateIdle"|check-pending-todos|check-task-result-envelope|log-team-event' .claude/settings.json
```

Expected: valid settings JSON, executable hooks, worker result enforcement, stop enforcement, and team lifecycle event logging wired.

### 11. Agent Team Configuration

```bash
test -f .cerebro/scripts/check-agent-teams-enabled.py
python3 .cerebro/scripts/check-agent-teams-enabled.py
rg -n "agent team|teammate|team mailbox|shared task list|NO NESTED TEAMS|CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" .cerebro/cerebro-identity.md README.md .claude/commands .claude/agents/cyclops.md .cerebro/docs
```

Expected: experimental agent teams are enabled and team-mode guidance exists.

### 12. Stop Hook Behavior

```bash
bash .claude/hooks/check-pending-todos.sh
```

Expected: exit code `0` when no pending todos exist.

For block behavior, use a temporary backup and restore it:

```bash
test -f .cerebro/scripts/test-stop-hook.py
python3 .cerebro/scripts/test-stop-hook.py
```

Expected: hook exits `0` and outputs `{"decision": "block", ...}` while the temporary todo exists (Claude Code hooks signal blocking via JSON stdout, not exit code).

### 13. TASK_RESULT Hook Behavior

```bash
bash .claude/hooks/test-task-result-envelope.sh
```

Expected: malformed result blocks; valid result allows stopping.

### 14. Upgrade Manifest and State

Validate upgrade schemas, manifest entry structure, and upgrade state metadata. If `.cerebro/upgrade-manifest.json` or `.cerebro/upgrade-state.json` is absent, that is informational only — existing projects may not have them until `/cerebro-upgrade` has run.

```bash
test -f .cerebro/scripts/validate-upgrade-metadata.py
python3 .cerebro/scripts/validate-upgrade-metadata.py
```

Expected: schemas parse as valid JSON, manifest entries have required keys and valid ownership enum, and upgrade-state.json (if present) has all required fields. If upgrade-manifest.json is absent, section 14 exits zero with an informational message.
