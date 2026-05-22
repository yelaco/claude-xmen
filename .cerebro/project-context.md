# Cerebro Project Context

**Indexed At:** 2026-05-19
**Repository:** hkt-claude

## Stack

- Language/runtime: Markdown-first Claude Code template with Bash hooks and JSON schemas
- Frameworks: Claude Code native `.claude/agents`, `.claude/commands`, hooks, and experimental agent teams
- Package manager: None
- Test framework: None (validated via `/cerebro-doctor` and JSON parsing)
- Build system: None

## Entrypoints

- Application: `CLAUDE.md` — Cerebro identity, intent gate, team roster, runtime rules
- Slash commands: `.claude/commands/*.md` — 5 workflows
- Agent personas: `.claude/agents/*.md` — 9 agents (Tab-selectable in Claude Code UI)
- Runtime state: `.cerebro/` — plans, team run manifests, notepads, boulder, pending-todos
- Hooks: `.claude/hooks/check-pending-todos.sh`, `.claude/hooks/check-task-result-envelope.sh`, `.claude/hooks/log-team-event.sh`
- Settings: `.claude/settings.json` — hook registration, permissions, and agent team environment flag

## Commands

- Install: copy `.claude/`, `.cerebro/`, and `CLAUDE.md` into a target repo
- Test: run `/cerebro-doctor` in Claude Code
- Focused test: `python3 -m json.tool .claude/settings.json`, `python3 -m json.tool .cerebro/schemas/boulder.schema.json`, and `python3 -m json.tool .cerebro/schemas/team-run.schema.json`
- Lint: `git diff --check`
- Typecheck: Not applicable
- Build: Not applicable
- Run/dev: open Claude Code in the target project and use slash commands

## Architecture

- `CLAUDE.md` — Cerebro identity, intent routing, agent team lead rules, command list
- `.claude/agents/` — 9 native specialist role files with YAML frontmatter; used as agent-team teammate definitions
- `.claude/commands/` — 5 slash command workflows: `cerebro-index`, `cerebro-plan`, `cerebro-start-work`, `cerebro-doctor`, `to-me-my-x-men`
- `.cerebro/templates/plan.md` — Canonical plan schema (Professor X drafts in this format; Cerebro writes and executes it through Cyclops decisions)
- `.cerebro/templates/project-context.md` — Template for this file
- `.cerebro/schemas/boulder.schema.json` — JSON Schema for `.cerebro/boulder.json` execution state
- `.cerebro/templates/team-run.json` — Template for per-workflow team run manifests
- `.cerebro/schemas/team-run.schema.json` — JSON Schema for team run manifests
- `.cerebro/plans/` — Plans written by Cerebro from Professor X drafts
- `.cerebro/team-runs/` — Team run manifests that record teammates, ownership, tasks, mailbox decisions, approvals, verification, and cleanup
- `.cerebro/notepads/{plan-name}/` — Accumulated wisdom per plan (conventions, commands, decisions, gotchas, failures, verification, issues)
- `.cerebro/boulder.json` — Resumable execution state (created/updated by Cyclops)
- `.cerebro/.pending-todos` — Wolverine/Storm active todo tracking (stop hook enforced)
- `docs/guide/` — Usage documentation: overview, workflow, orchestration, model-routing, agent-mapping, cerebro-workflow

## Conventions

- File organization: Claude Code behavior under `.claude/`; runtime state and templates under `.cerebro/`; docs under `docs/`
- Naming: agent files match agent name in persona frontmatter; commands use `cerebro-` prefix except `/to-me-my-x-men`
- Agent frontmatter: name, description, model, effort, and tools fields required in each `.claude/agents/*.md`
- Model tiers: `opus` for complex planning/review (Professor X, Emma Frost, Forge); `sonnet` for execution (Cyclops, Wolverine, Storm, Beast); `haiku` for lightweight search (Nightcrawler, Sage)
- Effort tiers: `high` for planning/review/architecture, `medium` for execution/orchestration/UI, and `low` for search/lookup
- Agent teams: all non-trivial workflows create a team with Cerebro as lead; teammates use existing role definitions, coordinate through the team mailbox/shared task list, and must not create nested teams
- Team run manifests: Cerebro writes `.cerebro/team-runs/{run-id}.json` for every non-trivial workflow and keeps task ownership, mailbox decisions, verification, and cleanup current
- Team lifecycle events: `TaskCreated`, `TaskCompleted`, and `TeammateIdle` hooks append compact event records to `.cerebro/team-runs/events.jsonl`
- Parallel by default: Nightcrawler + Sage spawn simultaneously; independent Wolverine/Storm tasks spawn simultaneously
- Task result envelope: workers report via `TASK_RESULT:` block (STATUS, TASK, SUMMARY, FILES CHANGED, TESTS RUN, VERIFICATION, LEARNINGS)
- Wisdom accumulation: Cerebro writes learnings from Cyclops decisions and worker results into `.cerebro/notepads/{plan-name}/`
- Verification: Cyclops decides verification steps and Cerebro runs them — never trust worker self-report alone
- Error handling: high-risk autonomous work asks user confirmation before proceeding
- Testing: `/cerebro-doctor` validates command names, native agent configuration, agent team flag, hooks, JSON schemas, stale references

## Risky Areas

- Command namespace — stale built-in planning or start-work command references can collide with Claude Code built-ins; `/cerebro-doctor` catches this
- Native agent drift — agent frontmatter, tool boundaries, or nested spawn instructions can break Claude Code compatibility; doctor validation catches mismatches
- Agent team drift — missing experimental flag or nested team guidance can break `/to-me-my-x-men`; doctor validation catches this
- Team run drift — missing or stale manifests make team coordination hard to resume; doctor validation catches schema/template drift
- Boulder state corruption — malformed `.cerebro/boulder.json` breaks resume behavior; validate against `boulder.schema.json` before use
- Stale pending todos — `.cerebro/.pending-todos` with content blocks final responses permanently; manual cleanup may be needed if a session crashes
- Approval gate enforcement — Cyclops must pause before gated tasks; ignoring this voids approval semantics
- Task result envelope format — malformed or missing `TASK_RESULT:` blocks prevent Cyclops verification; tasks appear to fail silently
- Doctor command — must avoid embedding legacy command tokens in a way that makes its own stale-reference check false-positive

## Agent Notes

- Prefer: update `/cerebro-doctor` whenever workflow files, schemas, or command names change
- Prefer: read `CLAUDE.md` → relevant `.claude/agents/*.md` before spawning any agent
- Prefer: read `.cerebro/project-context.md` before planning or execution; read existing notepads for the current plan
- Avoid: adding new project commands without the `cerebro-` prefix unless intentionally branded
- Avoid: spawning agents sequentially when tasks are independent
- Open questions: whether to eventually alias `/to-me-my-x-men` to `cerebro-assemble` while keeping original for branding

## Read First (Priority Order)

**Before any task:**
1. `CLAUDE.md` — intent gate, native agent roster, dispatch rules, runtime rules
2. `.claude/agents/{agent}.md` — native model, effort, tools, and behavior for a specialist
3. `.cerebro/project-context.md` — project orientation

**Before planning or execution:**
4. `.cerebro/plans/{latest}.md` — what is being executed
5. `.cerebro/notepads/{plan-name}/*.md` — accumulated wisdom (conventions, gotchas, decisions, failures)

**Before writing agent tasks:**
6. `.claude/agents/wolverine.md` — task result envelope format and todo discipline
7. `.claude/agents/cyclops.md` — approval gate enforcement and independent verification pattern

**Before extending the framework:**
8. `.cerebro/templates/plan.md` — canonical plan schema
9. `.cerebro/schemas/boulder.schema.json` — execution state contract
10. `.cerebro/schemas/team-run.schema.json` — team coordination audit log contract
11. `.claude/hooks/` — stop hook and TASK_RESULT envelope enforcement
