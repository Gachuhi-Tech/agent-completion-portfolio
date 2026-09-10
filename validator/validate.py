"""
Validates every conversation file in conversations/ against:
  1. tools/tool_schemas.json  - is each tool_call's name/arguments valid?
  2. basic structural rules   - does every tool result follow a matching call?

This only catches FORMAT problems. It says nothing about whether a
conversation is actually well-written - that's a human judgment call
against PLAYBOOK.md.

Usage:
    pip install jsonschema
    python validator/validate.py
"""
import json
import sys
from pathlib import Path

from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parent.parent
TOOLS_PATH = ROOT / "tools" / "tool_schemas.json"
CONVERSATIONS_DIR = ROOT / "conversations"


def load_tools():
    with open(TOOLS_PATH) as f:
        data = json.load(f)
    return {tool["name"]: tool for tool in data["tools"]}


def check_conversation(path, tools):
    errors = []
    with open(path) as f:
        convo = json.load(f)

    turns = convo.get("turns")
    if not turns:
        return [f"no 'turns' array found"]

    pending_calls = []  # tool names called but not yet matched to a result

    for i, turn in enumerate(turns):
        role = turn.get("role")

        if role not in ("user", "assistant", "tool"):
            errors.append(f"turn {i}: unknown role '{role}'")
            continue

        if role in ("assistant", "user") and pending_calls:
            # a new assistant/user turn means any earlier call that never
            # got a result is itself an error, not just a missing result
            for leftover in pending_calls:
                errors.append(f"turn {i}: earlier call to '{leftover}' never got a result")
            pending_calls = []

        if role == "assistant":
            for call in turn.get("tool_calls", []):
                name = call.get("name")
                args = call.get("arguments", {})
                if name not in tools:
                    errors.append(f"turn {i}: unknown tool '{name}'")
                    continue
                schema = tools[name]["parameters"]
                try:
                    validate(instance=args, schema=schema)
                except ValidationError as e:
                    errors.append(f"turn {i}: '{name}' arguments invalid - {e.message}")
                pending_calls.append(name)

        if role == "tool":
            name = turn.get("name")
            if name not in tools:
                errors.append(f"turn {i}: tool result references unknown tool '{name}'")
                continue
            # match against ANY still-pending call, not just the immediately
            # preceding turn - one assistant turn can make several calls, so
            # several tool turns in a row are legitimate
            if name in pending_calls:
                pending_calls.remove(name)
            else:
                errors.append(
                    f"turn {i}: tool result for '{name}' doesn't match any pending tool call"
                )

    for leftover in pending_calls:
        errors.append(f"end of conversation: call to '{leftover}' never got a result")

    return errors


def main():
    if not TOOLS_PATH.exists():
        print(f"Can't find {TOOLS_PATH}")
        sys.exit(1)

    tools = load_tools()
    files = sorted(CONVERSATIONS_DIR.glob("*.json"))

    if not files:
        print(f"No conversation files found in {CONVERSATIONS_DIR}")
        sys.exit(1)

    total_errors = 0
    for path in files:
        errors = check_conversation(path, tools)
        status = "PASS" if not errors else "FAIL"
        print(f"[{status}] {path.name}")
        for e in errors:
            print(f"    - {e}")
        total_errors += len(errors)

    print(f"\n{len(files)} conversation(s) checked, {total_errors} issue(s) found.")
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()