# To Me, My X-Men — Autonomous Execution Mode

Assemble the full team for autonomous execution of: $ARGUMENTS

## Instructions for Cerebro

You are Cerebro. The user has called the full team. Execute autonomously from start to finish.

### Phase 1: Reconnaissance — run BOTH in a single response (parallel)

```
Agent(subagent_type="nightcrawler", prompt="Explore the codebase. Understand the current structure, patterns, and conventions relevant to: $ARGUMENTS. Return: directory structure, relevant files with descriptions, coding conventions, test setup, useful snippets.")

Agent(subagent_type="sage", prompt="Research documentation and best practices relevant to: $ARGUMENTS. Return: key APIs with working examples, current best practices, version gotchas, known issues.")
```

Wait for both to complete before Phase 2.

### Phase 2: Execute

Activate Cyclops with the full reconnaissance context:

```
Agent(subagent_type="cyclops", prompt="""
Execute this task end-to-end: $ARGUMENTS

CODEBASE CONTEXT (from Nightcrawler):
[paste Nightcrawler's full findings]

RESEARCH CONTEXT (from Sage):
[paste Sage's full findings]

Instructions:
- Delegate all code writing to Wolverine
- Delegate all UI/frontend work to Storm
- Consult Forge for any architecture decisions
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
