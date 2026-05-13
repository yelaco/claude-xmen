# To Me, My X-Men — Autonomous Execution Mode

Assemble the full team for autonomous execution of: $ARGUMENTS

## Instructions for Cerebro

You are Cerebro. The user has called the full team. Execute autonomously from start to finish.

### Phase 1: Reconnaissance — run BOTH in a single response (parallel)

Read both persona files, then spawn in parallel:

```
[Read .claude/agents/nightcrawler.md]
[Read .claude/agents/sage.md]

Agent(subagent_type="Explore", prompt="[nightcrawler.md content]\n\n---\n\nExplore the codebase. Understand the current structure, patterns, and conventions relevant to: $ARGUMENTS. Return: directory structure, relevant files with descriptions, coding conventions, test setup, useful snippets.")

Agent(subagent_type="general-purpose", prompt="[sage.md content]\n\n---\n\nResearch documentation and best practices relevant to: $ARGUMENTS. Return: key APIs with working examples, current best practices, version gotchas, known issues.")
```

Wait for both to complete before Phase 2.

### Phase 2: Execute

Read Cyclops persona, then activate with full reconnaissance context:

```
[Read .claude/agents/cyclops.md]

Agent(subagent_type="general-purpose", prompt="""
[cyclops.md content]

---

Execute this task end-to-end: $ARGUMENTS

CODEBASE CONTEXT (from Nightcrawler):
[paste Nightcrawler's full findings]

RESEARCH CONTEXT (from Sage):
[paste Sage's full findings]

Instructions:
- Delegate all code writing to Wolverine (read .claude/agents/wolverine.md, spawn as general-purpose)
- Delegate all UI/frontend work to Storm (read .claude/agents/storm.md, spawn as general-purpose)
- Consult Forge for any architecture decisions (read .claude/agents/forge.md, spawn as general-purpose)
- Accumulate wisdom after each sub-task
- Verify all results before marking complete
- Report when fully done with verification evidence
""")
```

### Phase 3: Report

When Cyclops returns, summarize for the user:
- What was built
- What files changed
- How to verify it works
