# Agent Completion Portfolio — Multi-Turn Tool-Use Conversations

A hand-built set of multi-turn conversations between a user and an AI assistant that uses function-calling tools (calendar, email, maps) to get things done — plus the tool schemas, quality rubric, and validator behind them.

Built while preparing for Turing's "LLM Trainer – Agent Function Call" contractor role (Agent Completion / AC data generation for a foundational LLM company).

## Why this exists

That kind of role is really asking one question: can you design realistic multi-turn conversations where an assistant calls the right tools, in the right order, for the right reasons — and just as importantly, recognizes when it *shouldn't* call a tool at all, or can't complete the request? A pile of bulk-generated transcripts doesn't demonstrate that. A small, deliberately varied, hand-written set — checked against a rubric that's also part of this repo — does.

## Structure

```
tools/tool_schemas.json     5 mock tools across 3 "apps": calendar, email, maps
PLAYBOOK.md                 the quality rubric every conversation is written and checked against
conversations/               the hand-written conversations, one JSON file each
validator/validate.py       checks every conversation file against the schemas + structural rules
```

## Progress

- [x] Tool schemas defined
- [x] Playbook / rubric written
- [x] Validator built and tested
- [x] 001 — multi-step chained tool use (book a meeting: check calendar → find a venue → create event → send email)
- [ ] 002 — ambiguous request the assistant should ask about before acting
- [ ] 003 — request the assistant should correctly recognize as infeasible
- [ ] 004 — plain conversation, no tool needed
- [ ] 005 — a tool call returns an error/empty result and the assistant recovers
- [ ] 006 — (open slot — pick a gap the first five don't cover)

## Running the validator

```bash
pip install jsonschema
python validator/validate.py
```

It only catches format problems (bad JSON, wrong arguments, orphaned tool results) — not writing quality. That's a human judgment call against `PLAYBOOK.md`.

## Design notes

*(fill in as the set grows: why these 3 apps, what turned out harder to write than expected, what you'd add next)*
