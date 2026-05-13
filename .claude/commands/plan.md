# Plan — Activate Professor X

Plan this work: $ARGUMENTS

## Instructions for Cerebro

Read Professor X's persona, then activate for interview-based planning:

```
[Read .claude/agents/professor-x.md]

Agent(subagent_type="general-purpose", prompt="""
[professor-x.md content]

---

The user wants to: $ARGUMENTS

Begin the planning process now:

1. Start by asking your first clarifying question (one question only)
2. As the interview progresses, spawn Nightcrawler (Explore subagent_type) and Sage (general-purpose) in parallel to research — inject their personas from .claude/agents/
3. After the interview, consult Beast for gap analysis (mandatory) — read .claude/agents/beast.md, spawn as general-purpose
4. Write the plan to .cerebro/plans/
5. Offer Emma Frost validation if the user wants high accuracy — read .claude/agents/emma-frost.md, spawn as general-purpose
6. End by telling the user to run /start-work

Start with your first clarifying question now.
""")
```
