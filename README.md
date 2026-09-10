# Agent Completion Portfolio — Multi-Turn Tool-Use Conversations

A hand-built set of multi-turn conversations between a user and an AI assistant that uses function-calling tools (calendar, email, maps) to get things done — plus the tool schemas, quality rubric, and validator behind them.

Built while preparing for "LLM Trainer – Agent Function Call" contractor role (Agent Completion / AC data generation for a foundational LLM company).

**Demonstrates:** multi-turn tool-use design · function-call schema validation · ambiguity and failure handling · rubric-driven evaluation · Python (JSON Schema validation)

## Why this exists

That kind of role is really asking one question: can you design realistic multi-turn conversations where an assistant calls the right tools, in the right order, for the right reasons — and just as importantly, recognizes when it *shouldn't* call a tool at all, or can't complete the request? A pile of bulk-generated transcripts doesn't demonstrate that. A small, deliberately varied, hand-written set — checked against a rubric that's also part of this repo — does.

## Start here

1. Read `PLAYBOOK.md` — the 8 rules every conversation is written against. It's short.
2. Read `conversations/002_reschedule_meeting.json` — the clearest single example of the judgment this role tests: noticing what's missing and asking before acting.
3. Run `python validator/validate.py` — see the structural checks pass.

## Structure

```
tools/tool_schemas.json     5 mock tools across 3 "apps": calendar, email, maps
PLAYBOOK.md                 the quality rubric every conversation is written and checked against
conversations/               the hand-written conversations, one JSON file each
validator/validate.py       checks every conversation file against the schemas + structural rules
```

## Coverage

The set is designed to span the six judgment calls this role tests. Written so far:

| # | Scenario | Demonstrates | Status |
|---|----------|--------------|--------|
| 001 | Book a coffee meeting | Multi-step chained tool use (rule 3) | ✅ |
| 002 | Reschedule a call | Ask before assuming (rule 5) | ✅ |
| 003 | "Has she replied yet?" | Recognize infeasibility (rule 4) | 🚧 |
| 004 | Plain Q&A | Don't call a tool you don't need (rule 1) | planned |
| 005 | Tool returns an error | Handle failure (rule 6) | planned |
| 006 | Open slot | Gap the first five don't cover | planned |

🚧 = in progress. Planned = scoped but not yet written.

## Running the validator

```bash
pip install jsonschema
python validator/validate.py

It only catches format problems (bad JSON, wrong arguments, orphaned tool results) — not writing quality. That's a human judgment call against `PLAYBOOK.md`.

## Design notes

**One conversation per rule.** The playbook has eight rules; rules 1–6 each map to a distinct judgment call — chained tool use, ask-before-acting, infeasibility, no-tool-needed, failure recovery, and one open slot. I built them one at a time so each conversation could actually demonstrate its rule, rather than producing a pile that all exercised the same easy path.

**"Ambiguous" isn't always about the assistant.** My first draft of 002 had the user ask to move "our meeting" — which implies a specific existing event, but nothing in the tool set can look up an existing meeting. The fix wasn't the assistant's behavior; the assistant was behaving correctly given a broken premise. The fix was rewriting the user's line. Some ambiguity problems are really "the scenario is asking for a capability that doesn't exist" problems in disguise.

**What's next.** 003 (infeasibility), 004 (no tool needed), 005 (tool failure recovery), and one open slot. Same rule each time: one conversation per judgment call, written so I can explain every turn.
