# The Perimeter

**Enforcement lives at the harness boundary, not in the app.**

One scoping note before the mechanics: this is an **egress** perimeter. It guards
data leaving — file writes, shell args, MCP payloads. The inbound edge (untrusted
content steering the agent — prompt injection) is a different perimeter, on the
roadmap and honestly not built. One edge, done properly, beats two edges implied.

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

## What regex cannot see — the classifier tier

Regex cannot recognize a free-text name, a bare money amount, or a street address.
That's the documented `known_gap` class in the corpus — published debt, not a hole we
hide. Details: [Rule pack & known gaps](../reference/patterns.md).

Since N-001 there is an **opt-in second tier** for exactly those shapes:

```
NAMBIKKAI_CLASSIFIER=1        # requires ANTHROPIC_API_KEY in the env
```

When the deterministic sweep comes back clean on a high-risk tool (file writes, MCP
egress — deliberately not Bash), a small LLM (Haiku) reads the payload for
names/money/addresses. Properties, honestly stated:

- **Warn-tier only.** Findings log + announce; nothing blocks. Promotion to a blocking
  tier happens only after the live calibration test passes and you opt in — judge
  before dispatch.
- **Fail-open.** Missing key, timeout, malformed response → the call proceeds and a
  `CLASSIFIER-ERROR` line lands in the log. Your session never wedges on a cloud hiccup.
- **The trade is explicit.** Enabling it sends tool-call text to the Anthropic API —
  that is itself egress. Off by default for exactly that reason; with it off, the gaps
  stay documented debt, same as before.
- **The corpus still binds it.** `known_gap` cases tagged `classifier: "expected"` are
  its contract; the calibration in `tests/test_guard.py` asserts them whenever a key is
  present, and masking is asserted so the alert log can't become the leak.
