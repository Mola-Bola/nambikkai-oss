# The Perimeter

**Enforcement lives at the harness boundary, not in the app.**

Detection libraries — Presidio, llm-guard, and kin — detect PII well, *where an
application remembers to call them*. Agent systems are exactly where that assumption
fails: tools are added weekly, prompts drift, and the model itself composes the calls.
The place to stand is the one chokepoint every action passes through — the harness's
hook layer.

## How it works

Nambikkai registers a `PreToolUse` hook. Before **any** file write, shell command, or
outbound MCP call executes, the payload's strings are swept against the rule pack:

```
              ┌────────────────────────────┐
  tool call → │  gate (PreToolUse hook)    │ → executes
              │                            │
              │  blocking kind found?      │
              │    → exit 2, call refused  │
              │  overmatch-prone kind?     │
              │    → logged warn, allowed  │
              └────────────────────────────┘
```

- **Block** (exit 2): high-confidence identifiers — national IDs, passports, phone
  numbers, account numbers. The call never executes; the agent receives a masked
  explanation and adapts (typically by using a pointer to your secrets store instead).
- **Warn** (logged, allowed): shapes that over-trigger — dates, mixed alphanumeric
  codes. Blocking these would cry wolf on ordinary work; the corpus asserts each one.
- **Flag** (`Stop` hook): the chat transcript can't be rewritten inline, so the
  finished turn is scanned and leaks are *logged* as masked alerts — a silent leak
  becomes a caught one.

## Properties worth noticing

- **The block is an exit code.** Not a prompt instruction the model can rationalize
  past — the harness refuses the call.
- **Nothing raw is ever echoed.** stderr, logs, and alerts carry masked snippets only.
  The guard cannot become the leak.
- **The override is a feature.** `NAMBIKKAI_ALLOW_RAW=1` downgrades a block to a
  logged warning — because writing a real value into your own vault is legitimate.
  The perimeter has a door; the door has a light over it.
- **Fail-open on malformed input, fail-loud on findings.** An unparseable payload
  never wedges your session; a real finding is never silent.

## What it cannot see

Regex cannot recognize a free-text name or a bare money amount. That's the documented
`known_gap` class in the corpus — published debt, slated for a classifier pass, not a
hole we hide. Details: [Rule pack & known gaps](../reference/patterns.md).
