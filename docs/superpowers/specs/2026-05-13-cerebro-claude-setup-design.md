# Cerebro — Claude Code Orchestration Setup

**Date:** 2026-05-13
**Status:** Approved

---

## Overview

A self-contained `.claude/` folder template that replicates oh-my-openagent's full multi-agent orchestration capabilities using only the Claude Code ecosystem. Copy into any project and the full X-Men agent team is available immediately.

---

## Goals

- Full parity with oh-my-openagent: planning workflow, execution workflow, parallel specialists, wisdom accumulation
- Hard todo enforcement via Stop hook — agents cannot give a final response with incomplete todos
- Copy/clone template — everything self-contained, no external dependencies

---

## File Layout

```
CLAUDE.md                          ← Cerebro (main agent behavior)

.claude/
├── settings.json                  ← Stop hook + permissions
├── hooks/
│   └── check-pending-todos.sh     ← Blocks response if .pending-todos non-empty
├── commands/
│   ├── to-me-my-x-men.md          ← /to-me-my-x-men [task]  full team autonomous mode
│   ├── plan.md                    ← /plan [task]             Professor X planning
│   └── start-work.md              ← /start-work              Cyclops execution
└── agents/
    ├── professor-x.md             ← Strategic planner (READ-ONLY, .cerebro/plans/ only)
    ├── cyclops.md                 ← Field commander / orchestrator (no code writing)
    ├── wolverine.md               ← Task executor (writes code, no sub-agents)
    ├── beast.md                   ← Gap analyst / consultant (READ-ONLY)
    ├── emma-frost.md              ← Plan reviewer, OKAY/REJECT (READ-ONLY)
    ├── nightcrawler.md            ← Codebase grep/traversal (READ-ONLY)
    ├── sage.md                    ← Docs/knowledge retrieval (READ-ONLY)
    ├── forge.md                   ← Architecture consultant (READ-ONLY)
    └── storm.md                   ← Frontend/visual engineering (writes UI files)

.cerebro/
├── plans/                         ← Plan .md files created by Professor X
├── notepads/                      ← Per-plan wisdom dirs: learnings, decisions, issues
├── boulder.json                   ← Execution state (created at /start-work, runtime)
└── .pending-todos                 ← Active Wolverine todo list (checked by stop hook)
```

---

## Agent Roster

Each agent file's content becomes the system prompt when spawned via `Agent(subagent_type="{name}")`.

| Agent | Role | Key Constraint |
|---|---|---|
| **Cerebro** (`CLAUDE.md`) | Central intelligence, main daily-driver | Delegates code writing, never writes files directly |
| **Professor X** | Interviews user, generates plan | READ-ONLY — writes only to `.cerebro/plans/` |
| **Beast** | Gap analysis before plan is written | Consults only — no file writes |
| **Emma Frost** | Validates plan, OKAY/REJECT loop | Consults only — no file writes |
| **Cyclops** | Reads plan, delegates, verifies results | Cannot write code — delegates everything |
| **Wolverine** | Writes code, fixes bugs, creates tests | Cannot spawn sub-agents — focused execution only |
| **Forge** | Architecture consultation | READ-ONLY — advice only |
| **Nightcrawler** | Codebase grep/search | READ-ONLY — fast traversal only |
| **Sage** | Docs, OSS, library knowledge | READ-ONLY — retrieval only |
| **Storm** | Frontend/visual engineering | Can write files — scoped to UI work |

---

## Commands

### `/to-me-my-x-men [task]`
Cerebro assembles the full team for autonomous execution. Nightcrawler explores the codebase, Sage researches relevant docs, Cyclops orchestrates, Wolverine executes. No hand-holding required.

### `/plan [task]`
Activates Professor X. Flow:
1. Professor X interviews user with clarifying questions
2. Spawns Nightcrawler + Sage for codebase/doc research
3. Consults Beast for gap analysis
4. Optionally runs Emma Frost for high-accuracy plan validation (OKAY/REJECT loop)
5. Writes final plan to `.cerebro/plans/{name}.md`
6. Guides user to `/start-work`

### `/start-work`
Activates Cyclops. Flow:
1. Check `.cerebro/boulder.json` — if exists, RESUME mode; if not, INIT mode
2. RESUME: read existing state, inject remaining tasks, continue from last checkpoint
3. INIT: find latest plan in `.cerebro/plans/`, create `boulder.json`, begin from task 1
4. Delegates tasks to specialists, accumulates wisdom in `.cerebro/notepads/{plan-name}/`

---

## Cerebro Runtime (`.cerebro/`)

| Path | Purpose | Created by |
|---|---|---|
| `plans/{name}.md` | Implementation plans | Professor X |
| `notepads/{plan-name}/learnings.md` | Patterns, conventions, successes | Cyclops after each task |
| `notepads/{plan-name}/decisions.md` | Architectural choices | Cyclops |
| `notepads/{plan-name}/issues.md` | Problems, blockers, gotchas | Cyclops |
| `boulder.json` | Execution state tracker | Cyclops at `/start-work` |
| `.pending-todos` | Active Wolverine todo list | Wolverine (cleared on completion) |

---

## Hook Enforcement

### Stop Hook — Hard Todo Blocking

**`.claude/hooks/check-pending-todos.sh`**:
- Reads `.cerebro/.pending-todos`
- If non-empty: exits `1`, injects SYSTEM REMINDER with incomplete todo list
- Claude is forced to continue — cannot give final response
- Only exits `0` (allows response) when file is empty or absent

**`.claude/settings.json`**:
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{ "type": "command", "command": "bash .claude/hooks/check-pending-todos.sh" }]
    }]
  }
}
```

### Wolverine's Contract with the Hook
- On task start: write all todos to `.cerebro/.pending-todos`
- On each completion: remove that line from the file
- File empty = all done = hook allows final response

---

## Wisdom Accumulation

After each delegated task, Cyclops:
1. Extracts learnings from the agent's response
2. Categorizes into: Conventions, Successes, Failures, Gotchas, Commands
3. Writes to `.cerebro/notepads/{plan-name}/learnings.md`
4. Passes accumulated wisdom forward in every subsequent agent prompt

This prevents repeating mistakes and ensures consistent patterns across a long execution session.

---

## What Cerebro (CLAUDE.md) Defines

- **Identity**: Central intelligence of the X-Men. Coordinates all mutant agents.
- **Ultrawork trigger**: `/to-me-my-x-men` assembles full team autonomously
- **Agent spawning**: `Agent(subagent_type="{name}", prompt="...")` — passes accumulated wisdom in every call
- **Todo discipline**: Before any final response, check `.cerebro/.pending-todos`. Stop hook enforces this hard.
- **What Cerebro does NOT do**: Write or edit code directly — that is Wolverine's job
- **Cerebro runtime**: Plans in `.cerebro/plans/`, wisdom in `.cerebro/notepads/`, state in `boulder.json`
