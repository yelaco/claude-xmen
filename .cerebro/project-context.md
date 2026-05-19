# Cerebro Project Context

**Indexed At:** 2026-05-19
**Repository:** hkt-claude

## Stack

- Language/runtime: Markdown-first Claude Code template with Bash hooks and JSON schemas
- Frameworks: Claude Code native `.claude/agents`, `.claude/commands`, and hooks
- Package manager: None
- Test framework: None (validated via `/cerebro-doctor` and JSON parsing)
- Build system: None

## Entrypoints

- Application: `CLAUDE.md` — Cerebro identity, intent gate, team roster, runtime rules
- Slash commands: `.claude/commands/*.md` — 5 workflows
- Agent personas: `.claude/agents/*.md` — 9 agents (Tab-selectable in Claude Code UI)
- Runtime state: `.cerebro/` — plans, notepads, boulder, pending-todos
- Stop hook: `.claude/hooks/check-pending-todos.sh`
- Settings: `.claude/settings.json` — hook registration and permissions

## Commands

- Install: copy `.claude/`, `.cerebro/`, and `CLAUDE.md` into a target repo
- Test: run `/cerebro-doctor` in Claude Code
- Focused test: `python3 -m json.tool .cerebro/agent-models.json` and `python3 -m json.tool .cerebro/schemas/boulder.schema.json`
- Lint: `git diff --check`
- Typecheck: Not applicable
- Build: Not applicable
- Run/dev: open Claude Code in the target project and use slash commands

## Architecture

- `CLAUDE.md` — Cerebro identity, intent routing, model resolution, runtime rules, command list
- `.claude/agents/` — 9 specialist persona files with YAML frontmatter; directly Tab-selectable and injected programmatically
- `.claude/commands/` — 5 slash command workflows: `cerebro-index`, `cerebro-plan`, `cerebro-start-work`, `cerebro-doctor`, `to-me-my-x-men`
- `.cerebro/agent-models.json` — Per-agent model routing map; required before every Agent spawn
- `.cerebro/templates/plan.md` — Canonical plan schema (Professor X writes to this format; Cyclops executes from it)
- `.cerebro/templates/project-context.md` — Template for this file
- `.cerebro/schemas/boulder.schema.json` — JSON Schema for `.cerebro/boulder.json` execution state
- `.cerebro/plans/` — Plans created by Professor X (output)
- `.cerebro/notepads/{plan-name}/` — Accumulated wisdom per plan (conventions, commands, decisions, gotchas, failures, verification, issues)
- `.cerebro/boulder.json` — Resumable execution state (created/updated by Cyclops)
- `.cerebro/.pending-todos` — Wolverine/Storm active todo tracking (stop hook enforced)
- `docs/guide/` — Usage documentation: overview, workflow, orchestration, model-routing, agent-mapping, cerebro-workflow

## Conventions

- File organization: Claude Code behavior under `.claude/`; runtime state and templates under `.cerebro/`; docs under `docs/`
- Naming: agent files match agent name in persona frontmatter; commands use `cerebro-` prefix except `/to-me-my-x-men`
- Agent frontmatter: name, description, model fields required in each `.claude/agents/*.md`
- Model tiers: `opus` for complex planning/review (Professor X, Emma Frost, Forge); `sonnet` for execution (Cyclops, Wolverine, Storm, Beast); `haiku` for lightweight search (Nightcrawler, Sage)
- Agent spawning: always read `.cerebro/agent-models.json` first, resolve `model = models[agent-name] || default_model`, pass as `model=` to `Agent()`
- Parallel by default: Nightcrawler + Sage spawn simultaneously; independent Wolverine/Storm tasks spawn simultaneously
- Task result envelope: workers report via `TASK_RESULT:` block (STATUS, TASK, SUMMARY, FILES CHANGED, TESTS RUN, VERIFICATION, LEARNINGS)
- Wisdom accumulation: Cyclops extracts learnings after each task into `.cerebro/notepads/{plan-name}/`
- Verification: Cyclops independently verifies task completion by reading files and running commands — never trusts worker self-report alone
- Error handling: high-risk autonomous work asks user confirmation before proceeding
- Testing: `/cerebro-doctor` validates command names, model routing, agent frontmatter, JSON schemas, stale references

## Risky Areas

- Command namespace — stale built-in planning or start-work command references can collide with Claude Code built-ins; `/cerebro-doctor` catches this
- Model routing drift — agent frontmatter models and `.cerebro/agent-models.json` must stay aligned; schema validation catches mismatches
- Boulder state corruption — malformed `.cerebro/boulder.json` breaks resume behavior; validate against `boulder.schema.json` before use
- Stale pending todos — `.cerebro/.pending-todos` with content blocks final responses permanently; manual cleanup may be needed if a session crashes
- Approval gate enforcement — Cyclops must pause before delegating gated tasks; ignoring this voids approval semantics
- Task result envelope format — malformed or missing `TASK_RESULT:` blocks prevent Cyclops verification; tasks appear to fail silently
- Doctor command — must avoid embedding legacy command tokens in a way that makes its own stale-reference check false-positive

## Agent Notes

- Prefer: update `/cerebro-doctor` whenever workflow files, schemas, or command names change
- Prefer: read `CLAUDE.md` → `.cerebro/agent-models.json` → relevant agent `.md` before spawning any agent
- Prefer: read `.cerebro/project-context.md` before planning or execution; read existing notepads for the current plan
- Avoid: adding new project commands without the `cerebro-` prefix unless intentionally branded
- Avoid: spawning agents sequentially when tasks are independent
- Open questions: whether to eventually alias `/to-me-my-x-men` to `cerebro-assemble` while keeping original for branding

## Read First (Priority Order)

**Before any task:**
1. `CLAUDE.md` — intent gate, agent roster, model routing, runtime rules
2. `.cerebro/agent-models.json` — resolve model before every Agent spawn
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
10. `.claude/hooks/check-pending-todos.sh` — stop hook enforcement
