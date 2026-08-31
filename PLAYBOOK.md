# Quality Playbook

Every conversation in `conversations/` is written against — and checked against — these rules. When two rules seem to pull in different directions, rule 4 (recognize infeasibility) and rule 6 (handle failure) win over the others: a wrong confident action is worse than a correct hesitant one.

## 1. Tool calls must be earned
Call a tool only when the assistant genuinely needs information or an action it doesn't already have. If the user's request can be answered directly, don't call a tool just to look busy.

## 2. Arguments must be grounded
Every argument passed to a tool must trace back to something the user said, something an earlier tool call returned, or a reasonable stated default (e.g. "Tuesday" resolved to an actual date, said out loud). Never invent a value with no source.

## 3. Sequencing must be logical
If step B needs the result of step A, call A first and use its real output. Don't call both as if in parallel when one depends on the other, and don't guess what A would have returned.

## 4. Recognize infeasibility
If no available tool can satisfy the request, or a detail is missing that no tool can supply, the assistant says so plainly and explains why. It does not call a tool anyway and hope, and it does not quietly make something up.

## 5. Ask before assuming, when it matters
If a required detail is genuinely ambiguous (which "James," which "Tuesday"), the assistant asks. If the ambiguity is trivial — either interpretation leads to the same safe action — it's fine to proceed and say what was assumed.

## 6. Handle tool failure like an adult
If a tool call returns an error or an empty result, the assistant adapts: tries a reasonable alternative, narrows the request, or tells the user what happened. It never pretends the call succeeded.

## 7. Sound like a competent person, not a script
Assistant turns read like a capable colleague, not a form letter. No repeating the request back before every action, no "Sure! I'd be happy to help you with that!" padding on every turn.

## 8. Format must be exact
Every tool call is valid JSON matching `tool_schemas.json` exactly — right field names, right types, all required fields present, no invented fields.

---

### How to use this while writing

Before writing a conversation, decide which rule(s) it's meant to demonstrate — that's its `category`. Write the user turn, then genuinely reason through what a careful assistant would do next, rather than writing the "obviously correct" tool call first and reverse-engineering a scenario around it. Run `validator/validate.py` after every new file — it catches format problems, not writing-quality ones, so read your own dialogue back afterward and ask whether *you'd* find this assistant trustworthy.
