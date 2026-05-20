# Agent Model and Effort Routing

Cerebro supports project-level model and reasoning effort maps at `.cerebro/agent-models.json`.

The model map uses Claude Code aliases instead of pinned dated model IDs. The effort map uses portable reasoning effort aliases:

```json
{
  "default_model": "sonnet",
  "default_effort": "medium",
  "models": {
    "professor-x": "opus",
    "cyclops": "sonnet",
    "wolverine": "sonnet",
    "nightcrawler": "haiku"
  },
  "efforts": {
    "professor-x": "high",
    "cyclops": "medium",
    "wolverine": "medium",
    "nightcrawler": "low"
  }
}
```

## Resolution Rule

Before spawning an agent, Cerebro should:

1. Read `.cerebro/agent-models.json`.
2. Look up `models[agent-name]`.
3. Fall back to `default_model`.
4. Look up `efforts[agent-name]`.
5. Fall back to `default_effort`.
6. Pass the resolved model as the Agent invocation `model` parameter.
7. Pass the resolved effort as the Agent invocation `reasoning_effort` parameter when supported by the current agent runtime.

Example:

```text
Agent(
  subagent_type="general-purpose",
  model="sonnet",
  reasoning_effort="medium",
  prompt="[wolverine.md content]\n\n---\n\nYour task:\n..."
)
```

Use `low` for search and lookup agents, `medium` for execution and orchestration, and `high` for planning, review, and architecture consultation.

## Claude Code Precedence

Claude Code resolves subagent model selection in this order:

1. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable, if set
2. Per-invocation `model` parameter
3. Subagent file `model` frontmatter
4. Main conversation model

That means `.cerebro/agent-models.json` works through the per-invocation model parameter, but it is still overridden by `CLAUDE_CODE_SUBAGENT_MODEL`. Reasoning effort should follow the per-invocation `reasoning_effort` parameter when the agent runtime exposes it.
