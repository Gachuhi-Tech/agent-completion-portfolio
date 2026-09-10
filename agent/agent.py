"""
agent/agent.py — a real tool-calling agent built on top of this repo's
existing tool schemas and conversations.

Two modes:

    python agent/agent.py                       # interactive chat
    python agent/agent.py --replay 002          # replay a conversation file

Replay mode feeds each user turn from conversations/00N_*.json to a real
LLM, runs the tools it calls against mock implementations, and prints what
the LLM did next to what the conversation file expects. That's a
conformance check — did the LLM behave the way the hand-written example says
a good assistant should?

Uses Groq (OpenAI-compatible API) — free tier, no card required.

Setup:
    pip install openai
    set GROQ_API_KEY=gsk_...      (Windows cmd)
    export GROQ_API_KEY=gsk_...   (bash / macOS / Linux)
"""
import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
TOOLS_PATH = ROOT / "tools" / "tool_schemas.json"
CONVERSATIONS_DIR = ROOT / "conversations"

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to calendar, email, and maps "
    "tools. Follow these rules:\n"
    "1. Only call a tool when you genuinely need information or an action.\n"
    "2. Never invent values — every argument must come from the user or a "
    "prior tool result.\n"
    "3. If a required detail is missing and no tool can supply it, ask the "
    "user instead of guessing.\n"
    "4. If no available tool can satisfy the request, say so plainly.\n"
    "5. Sound like a competent colleague, not a script."
)


# --------------------------------------------------------------------------
# Tool schemas — loaded from tools/tool_schemas.json, converted to OpenAI
# --------------------------------------------------------------------------

def load_openai_tools():
    with open(TOOLS_PATH) as f:
        data = json.load(f)
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        }
        for t in data["tools"]
    ]


# --------------------------------------------------------------------------
# Mock tool implementations — same return shapes the conversation files use
# --------------------------------------------------------------------------

def _check_calendar_availability(date, start_time, end_time):
    return {
        "date": date,
        "busy_blocks": [
            {"start_time": "14:00", "end_time": "15:00", "title": "Design Review"}
        ],
        "free_blocks": [
            {"start_time": "13:00", "end_time": "14:00"},
            {"start_time": "15:00", "end_time": "17:00"},
        ],
    }


def _create_calendar_event(title, date, start_time, end_time, attendees=None):
    return {"status": "created", "event_id": "evt_mock_001"}


def _send_email(to, subject, body):
    return {"status": "sent", "message_id": "msg_mock_001"}


def _search_places(query, near):
    return {
        "results": [
            {"name": "Java House Westlands", "distance_km": 0.3, "rating": 4.3},
            {"name": "Artcaffe Sarit Centre", "distance_km": 0.6, "rating": 4.5},
            {"name": "Cafe Ngong Rd", "distance_km": 3.1, "rating": 4.4},
        ]
    }


def _get_directions(origin, destination, mode="driving"):
    return {"duration_minutes": 12, "mode": mode, "distance_km": 2.1}


TOOL_IMPLEMENTATIONS = {
    "check_calendar_availability": _check_calendar_availability,
    "create_calendar_event": _create_calendar_event,
    "send_email": _send_email,
    "search_places": _search_places,
    "get_directions": _get_directions,
}


def execute_tool(name, args):
    if name not in TOOL_IMPLEMENTATIONS:
        return {"error": f"unknown tool '{name}'"}
    try:
        return TOOL_IMPLEMENTATIONS[name](**args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------

def step(client, messages, tools):
    """One model turn. Executes any tool calls, appends results, returns text."""
    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools
    )
    msg = response.choices[0].message
    messages.append(msg)

    if msg.tool_calls:
        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            print(f"    -> call: {name}({json.dumps(args)})")
            result = execute_tool(name, args)
            print(f"    <- result: {json.dumps(result)}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                }
            )
        # Model may want to respond or call more tools — loop once more
        return step(client, messages, tools)

    return msg.content or ""


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def interactive(client, tools):
    print("Interactive mode. Type 'exit' to quit.\n")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    while True:
        user = input("you> ").strip()
        if user.lower() in ("exit", "quit"):
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})
        reply = step(client, messages, tools)
        print(f"assistant> {reply}\n")


def replay(client, tools, convo_id):
    matches = list(CONVERSATIONS_DIR.glob(f"{convo_id}_*.json"))
    if not matches:
        print(f"No conversation matching '{convo_id}_*.json'")
        sys.exit(1)
    path = matches[0]
    with open(path) as f:
        convo = json.load(f)

    print(f"Replaying {path.name}\n")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for i, turn in enumerate(convo["turns"]):
        role = turn["role"]
        if role == "user":
            print(f"[user] {turn['content']}")
            messages.append({"role": "user", "content": turn["content"]})
        elif role == "assistant":
            print("[assistant expected]")
            for c in turn.get("tool_calls", []):
                print(f"    expected call: {c['name']}({json.dumps(c['arguments'])})")
            if not turn.get("tool_calls"):
                print(f"    expected text: {turn['content']!r}")
            # let the real LLM respond
            print("[assistant actual]")
            reply = step(client, messages, tools)
            if reply:
                print(f"    text: {reply!r}")
            print()
        elif role == "tool":
            # skip — we don't replay tool results, the LLM generated its own
            continue

    print("Done. Compare 'expected' vs 'actual' above.")


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", help="conversation id prefix, e.g. 002")
    args = parser.parse_args()

    if not os.environ.get("GROQ_API_KEY"):
        print("Set GROQ_API_KEY first.")
        sys.exit(1)

    client = OpenAI(
        base_url=GROQ_BASE_URL,
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    tools = load_openai_tools()

    if args.replay:
        replay(client, tools, args.replay)
    else:
        interactive(client, tools)


if __name__ == "__main__":
    main()