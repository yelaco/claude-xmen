# Agent Model Routing

Cerebro supports a project-level model map at `.cerebro/agent-models.json`.

The map uses Claude Code aliases instead of pinned dated model IDs:

```json
{
  "default_model": "sonnet",
  "models": {
    "professor-x": "opus",
    "cyclops": "sonnet",
    "wolverine": "sonnet",
    "nightcrawler": "haiku"
  }
}
```

## Resolution Rule

Before spawning an agent, Cerebro should:

1. Read `.cerebro/agent-models.json`.
2. Look up `models[agent-name]`.
3. Fall back to `default_model`.
4. Pass the result as the Agent invocation `model` parameter.

Example:

```text
Agent(
  subagent_type="general-purpose",
  model="sonnet",
  prompt="[wolverine.md content]\n\n---\n\nYour task:\n..."
)
```

## Claude Code Precedence

Claude Code resolves subagent model selection in this order:

1. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable, if set
2. Per-invocation `model` parameter
3. Subagent file `model` frontmatter
4. Main conversation model

That means `.cerebro/agent-models.json` works through the per-invocation model parameter, but it is still overridden by `CLAUDE_CODE_SUBAGENT_MODEL`.
