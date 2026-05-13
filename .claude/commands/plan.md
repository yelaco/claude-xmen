# Plan — Activate Professor X

Plan this work: $ARGUMENTS

## Instructions for Cerebro

Activate Professor X to create an implementation plan for the user's request.

```
Agent(subagent_type="professor-x", prompt="""
The user wants to: $ARGUMENTS

Begin the planning process now:

1. Start by asking your first clarifying question (one question only)
2. As the interview progresses, spawn Nightcrawler and Sage in parallel to research
3. After the interview, consult Beast for gap analysis (mandatory)
4. Write the plan to .cerebro/plans/
5. Offer Emma Frost validation if the user wants high accuracy
6. End by telling the user to run /start-work

Start with your first clarifying question now.
""")
```
