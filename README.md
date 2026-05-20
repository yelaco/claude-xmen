# Claude X-Men — Cerebro Orchestration Template

A self-contained Claude Code multi-agent orchestration template. Copy it into any project and get a full 9-agent AI team with planning, execution, enforcement, and session continuity — all themed around the X-Men.

Cerebro coordinates. Agents execute. You get results.

---

## Quick Start

Copy the template into your project:

```bash
# From your project root
cp -r /path/to/claude-xmen/.claude .claude
cp -r /path/to/claude-xmen/.cerebro .cerebro
cp /path/to/claude-xmen/CLAUDE.md CLAUDE.md
```

Open Claude Code and run your first command:

```
/to-me-my-x-men add a REST API for user authentication
```

Cerebro will assemble the team, research your codebase, and execute — no further input required.

---

## Commands

| Command | What it does |
|---|---|
| `/to-me-my-x-men [task]` | Full autonomous mode. Nightcrawler and Sage recon in parallel, then Cyclops drives execution to completion. |
| `/cerebro-plan [task]` | Interview-based planning. Professor X asks clarifying questions, Beast checks for gaps, Emma Frost validates. Ends with a written plan in `.cerebro/plans/`. |
| `/cerebro-start-work` | Execute the latest plan. Cyclops picks up from the last checkpoint if a session was interrupted. |
| `/cerebro-doctor` | Validate command names, model/effort routing, agent frontmatter, plan/state schemas, task result envelopes, and stop hook health. |
| `/cerebro-index` | Build `.cerebro/project-context.md` with stack, commands, conventions, entrypoints, and risky areas. |

---

## The Team

| Agent | Role | Triggers when |
|---|---|---|
| **Professor X** | Strategic planner | `/cerebro-plan` is called; needs to interview the user |
| **Beast** | Gap analyst | A plan is drafted; checks for missing cases |
| **Emma Frost** | Plan reviewer | High-stakes work; validates OKAY or REJECT |
| **Cyclops** | Execution orchestrator | `/cerebro-start-work` runs; never writes code directly |
| **Wolverine** | Code writer | Any code, tests, or bug fixes are needed |
| **Storm** | Frontend engineer | UI, components, visual engineering |
| **Forge** | Architecture consultant | Design decisions, system structure |
| **Nightcrawler** | Codebase searcher | Recon before execution; grep, pattern discovery |
| **Sage** | Docs & knowledge | Library research, API lookup, best practices |

Agents that are independent of each other run in parallel. Cerebro spawns them in a single response.

---

## How It Works

```
User
 │
 ▼
Cerebro (CLAUDE.md)
 │
 ├── /to-me-my-x-men ──► Nightcrawler + Sage (parallel recon)
 │                              │
 │                              ▼
 │                         Cyclops (orchestrator)
 │                              │
 │                   ┌──────────┴──────────┐
 │                   ▼                     ▼
 │              Wolverine               Storm
 │             (code/tests)          (UI/frontend)
 │                   │
 │              Forge / Sage (consulted on demand)
 │
 ├── /cerebro-plan ──► Professor X → Beast → Emma Frost
 │                              │
 │                              ▼
 │                    .cerebro/plans/{name}.md
 │
 └── /cerebro-start-work ────► Cyclops (reads boulder.json, resumes or inits)
```

### Session Continuity

Every plan execution is tracked in `.cerebro/boulder.json`. If Claude Code stops mid-task, `/cerebro-start-work` resumes exactly where it left off:

```
"Resuming auth-api-plan — 3 of 7 tasks complete"
```

### Wisdom Accumulation

After each delegated task, learnings are written to `.cerebro/notepads/{plan-name}/learnings.md` — conventions found, approaches that worked, gotchas hit. Every subsequent agent call receives the full accumulated context.

### Todo Enforcement

A stop hook blocks Claude from sending a final response while `.cerebro/.pending-todos` has content. Wolverine and Storm write todos at task start and remove them on completion. No silent abandonment.

---

## File Structure

```
.
├── CLAUDE.md                          # Cerebro — main agent identity
├── .claude/
│   ├── settings.json                  # Wires the stop hook
│   ├── agents/                        # 9 sub-agent definitions
│   │   ├── professor-x.md
│   │   ├── beast.md
│   │   ├── emma-frost.md
│   │   ├── cyclops.md
│   │   ├── wolverine.md
│   │   ├── storm.md
│   │   ├── forge.md
│   │   ├── nightcrawler.md
│   │   └── sage.md
│   ├── commands/                      # Slash commands
│   │   ├── cerebro-doctor.md
│   │   ├── cerebro-index.md
│   │   ├── to-me-my-x-men.md
│   │   ├── cerebro-plan.md
│   │   └── cerebro-start-work.md
│   └── hooks/
│       └── check-pending-todos.sh     # Stop hook — enforces todo completion
└── .cerebro/
    ├── agent-models.json              # Per-agent model and effort routing
    ├── schemas/
    │   └── boulder.schema.json        # Execution state schema
    ├── templates/
    │   ├── plan.md                    # Canonical Professor X plan schema
    │   └── project-context.md         # Canonical repository index schema
    ├── project-context.md             # Repository index created by /cerebro-index
    ├── plans/                         # Plans written by Professor X
    ├── notepads/                      # Per-plan wisdom (learnings, decisions)
    └── boulder.json                   # Execution state (created at /cerebro-start-work)
```

---

## Four Ways to Work

**0. Index a project**

Best when copying Cerebro into a repo for the first time or after major project changes.

```
/cerebro-index
```

Cerebro writes `.cerebro/project-context.md` with stack, entrypoints, commands, conventions, and risky areas.

**1. Autonomous (fire and forget)**

Best for clear tasks where you trust the team to figure out the details.

```
/to-me-my-x-men migrate the database layer from raw SQL to Prisma
```

Nightcrawler maps the codebase. Sage researches Prisma. Cyclops drives execution. You get a completion report.

**2. Interview-first (high confidence)**

Best for complex features where requirements need to be locked down before a line is written.

```
/cerebro-plan redesign the notification system to support real-time push
```

Professor X interviews you, Beast finds the gaps, Emma Frost validates. Then:

```
/cerebro-start-work
```

Cyclops executes the written plan with full checkpoint tracking.

**3. Direct agent selection**

Tab-complete to any agent in Claude Code for targeted use.

---

## Configuration

The stop hook is registered in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/check-pending-todos.sh"
          }
        ]
      }
    ]
  }
}
```

All tools are permitted by default (`Bash(*)`, `Read(*)`, `Write(*)`, `Edit(*)`). Restrict as needed for your environment.

### Agent Model and Effort Routing

Agent model and effort defaults live in `.cerebro/agent-models.json`. Cerebro reads this map before spawning agents, passes the resolved model as the Agent invocation `model` parameter, and passes the resolved effort as `reasoning_effort` when supported by the current agent runtime. See [docs/guide/model-routing.md](docs/guide/model-routing.md).

### Skills

Skills are optional overlays. The template ships without required skills; users can add skills later without changing the base workflow. Project-local `.cerebro` contracts, approval gates, todo discipline, model/effort routing, and result envelopes remain authoritative.

---

## Requirements

- Claude Code (claude.ai/code)
- A project with a git repo (recommended)
- No additional dependencies — pure Claude Code primitives
