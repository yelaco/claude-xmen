# Cerebro Plan - Activate Professor X

Plan this work: $ARGUMENTS

## Instructions for Cerebro

Read `.cerebro/agent-models.json`, then read Professor X's persona and activate interview-based planning.

Resolve `model = models["professor-x"] || default_model` and `reasoning_effort = efforts["professor-x"] || default_effort`. If the map is missing or invalid, use `opus` and `high` for Professor X.

```
[Read .cerebro/agent-models.json]
[Read .claude/agents/professor-x.md]

Agent(subagent_type="general-purpose", model="[models.professor-x || default_model]", reasoning_effort="[efforts.professor-x || default_effort]", prompt="""
[professor-x.md content]

---

The user wants to: $ARGUMENTS

Begin the planning process now:

1. Start by asking your first clarifying question (one question only)
2. As the interview progresses, spawn Nightcrawler and Sage in parallel to research - inject their personas from .claude/agents/, use general-purpose subagents, and pass models and reasoning efforts from .cerebro/agent-models.json
3. After the interview, consult Beast for gap analysis (mandatory) - read .claude/agents/beast.md, spawn as general-purpose with model and reasoning effort from .cerebro/agent-models.json
4. Write the plan to .cerebro/plans/ with scope, tasks, verification commands, risk level, and approval gates
5. Offer Emma Frost validation if the user wants high accuracy, or run it automatically for destructive/security/data/production work - read .claude/agents/emma-frost.md, spawn as general-purpose with model and reasoning effort from .cerebro/agent-models.json
6. End by asking the user to approve the plan before running /cerebro-start-work when approval is required

Plan files must include:
- Objective and non-goals
- Assumptions and decisions
- Risk level: LOW | MEDIUM | HIGH
- Approval gates, if any
- Acceptance criteria with concrete pass/fail checks
- Task list with exact files, action, owner, and verification command
- Rollback or recovery notes for risky work

Use `.cerebro/templates/plan.md` as the canonical schema. Do not save the plan until Beast findings have been addressed. Run Emma Frost automatically when risk level is HIGH.

Start with your first clarifying question now.
""")
```
