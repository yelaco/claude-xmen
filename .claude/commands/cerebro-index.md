# Cerebro Index - Build Project Context

Create or refresh `.cerebro/project-context.md` for this repository.

## Instructions for Cerebro

This command is an onboarding/indexing workflow. It may write only `.cerebro/project-context.md`.

Read `.cerebro/agent-models.json`, `.cerebro/templates/project-context.md`, Nightcrawler, and Sage. Resolve models from the map.

Skills are optional. If repository, documentation, language, or framework skills are available, use them only to improve indexing precision. If unavailable, continue with Nightcrawler, Sage, and local repo inspection.

Run Nightcrawler and Sage in parallel:

```
[Read .cerebro/agent-models.json]
[Read .cerebro/templates/project-context.md]
[Read .claude/agents/nightcrawler.md]
[Read .claude/agents/sage.md]

Agent(subagent_type="general-purpose", model="[models.nightcrawler || default_model]", prompt="""
[nightcrawler.md content]

---

Index this repository for future Cerebro work. Return:
- directory structure and major subsystems
- app/test/config entrypoints
- package/build/test/lint/typecheck commands found in manifests or docs
- coding and testing conventions
- risky areas requiring extra verification
- files that future agents should read first
""")

Agent(subagent_type="general-purpose", model="[models.sage || default_model]", prompt="""
[sage.md content]

---

From local manifests and docs, identify likely framework/library context and summarize:
- relevant ecosystem conventions
- likely best-practice verification commands
- version-specific gotchas visible from dependency manifests
Do not invent dependencies not present in the repository.
""")
```

After both return:

1. Read existing `.cerebro/project-context.md` if it exists.
2. Fill `.cerebro/templates/project-context.md` with discovered facts.
3. Write `.cerebro/project-context.md`.
4. Keep unknown fields as `Unknown`.
5. Do not modify source code or project configuration.
6. Report the indexed stack, commands, and top risky areas.
