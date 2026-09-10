# Agent Completion Portfolio — Multi-Turn Tool-Use Conversations

A hand-built set of multi-turn conversations between a user and an AI assistant that uses function-calling tools (calendar, email, maps) to get things done — plus the tool schemas, quality rubric, validator, and a working agent that runs the conversations against a real LLM.

Built while preparing for "LLM Trainer – Agent Function Call" contractor role (Agent Completion / AC data generation for a foundational LLM company).

**Demonstrates:** multi-turn tool-use design · function-call schema validation · ambiguity and failure handling · rubric-driven evaluation · Python (JSON Schema validation, OpenAI-compatible tool-calling loops)

## Why this exists

That kind of role is really asking one question: can you design realistic multi-turn conversations where an assistant calls the right tools, in the right order, for the right reasons — and just as importantly, recognizes when it *shouldn't* call a tool at all, or can't complete the request? A pile of bulk-generated transcripts doesn't demonstrate that. A small, deliberately varied, hand-written set — checked against a rubric that's also part of this repo — does.

## Start here

1. Read `PLAYBOOK.md` — the 8 rules every conversation is written against. It's short.
2. Read `conversations/002_reschedule_meeting.json` — the clearest single example of the judgment this role tests: noticing what's missing and asking before acting.
3. Run `python validator/validate.py` — see the structural checks pass.
4. Run `python agent/agent.py --replay 002` — watch a real LLM try the same scenario, and compare to the hand-written bar.

## Structure

```text
tools/tool_schemas.json          5 mock tools across 3 "apps": calendar, email, maps
PLAYBOOK.md                      the quality rubric every conversation is written and checked against
conversations/                   the hand-written conversations, one JSON file each
validator/validate.py            checks every conversation file against the schemas + structural rules
agent/agent.py                   runs the conversations against a real LLM and reports drift## Structure

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

## Running the agent
 
```bash
pip install openai
set GROQ_API_KEY=gsk_...   # Windows
python agent/agent.py

Interactive chat, or `--replay 002` to run the hand-written scenario against a real model and see where it drifts. Uses Groq's free tier via its OpenAI-compatible API.

## Design notes

**Why this set, not a bulk one.** The playbook has eight rules; rules 1–6 each map to a distinct judgment call — chained tool use, ask-before-acting, infeasibility, no-tool-needed, failure recovery, and one open slot. I built them one at a time so each conversation could actually demonstrate its rule, rather than producing a pile that all exercised the same easy path.

**The conversations are a spec, and I tested against it.** I built a small agent (`agent/agent.py`) that loads the same `tool_schemas.json`, runs each conversation's user turns against a real LLM via Groq, and prints what the model actually did next to what the hand-written file expects. The first run surfaced two real bugs in the model's behavior that my hand-written files had already avoided: (1) it resolved "the coming Tuesday" to a Saturday, and (2) it claimed an email was sent without calling `send_email`. Adding the current date and an explicit "creating an event does not notify the attendee" rule to the system prompt fixed both. A third case — offering to "check for a reply" when no tool can read an inbox — still drifts, and is exactly the case `003` was written for.