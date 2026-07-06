# Hook contract

Two hooks, wired by the plugin's `hooks/hooks.json`.

## The gate — `guard.py` (PreToolUse)

**Matchers:** `Write|Edit|MultiEdit|NotebookEdit|Bash` and
`mcp__.*__(create|copy|execute|apply|deploy|send|label|update|delete).*`

**Input:** the harness's PreToolUse JSON on stdin (`tool_name`, `tool_input`). Every
string value in `tool_input` is collected recursively and swept.

**Behavior:**

| Condition | Exit | Effect |
|---|---|---|
| no findings | 0 | call proceeds |
| blocking kind (`nric`, `passport`, `phone`, `account`) | 2 | call refused; masked explanation on stderr |
| blocking kind + `NAMBIKKAI_ALLOW_RAW=1` | 0 | call proceeds; OVERRIDE logged + announced |
| warn-only kind (`dob`, `brokerage`) | 0 | call proceeds; WARN logged |
| unparseable stdin | 0 | fail-open — never wedge a session |
| regex clean + classifier tier on + LLM finding | 0 | call proceeds; CLASSIFIER-WARN logged + announced |
| regex clean + classifier tier on + API failure | 0 | call proceeds; CLASSIFIER-ERROR logged (fail-open) |

The classifier rows apply only with `NAMBIKKAI_CLASSIFIER=1`, and only to high-risk
tools (`Write`/`Edit`/`MultiEdit`/`NotebookEdit`/`mcp__*` — not Bash). See
[The Perimeter](../concepts/perimeter.md) for the tier's full contract.

**Guarantees:** stderr and the alert log carry masked snippets only — the guard never
echoes a raw value. A logging failure never crashes the tool call.

## The flag — `flag.py` (Stop)

Reads the session transcript path from the Stop payload, extracts the final assistant
message, sweeps it for **blocking kinds only** (warn kinds would cry wolf on ordinary
replies), and appends a masked `CHAT-LEAK` line to the alert log. Always exits 0 —
detection, never interruption.

## The alert log

Default `./.nambikkai/alerts.log`, overridable via `NAMBIKKAI_LOG`. One tab-separated
line per event:

```
2026-07-05T09:14:02Z  BLOCK  tool=Write  kinds=nric  <masked 160-char window>
2026-07-05T11:40:19Z  WARN   tool=Bash   kinds=dob   <masked window>
2026-07-05T21:03:44Z  CHAT-LEAK  kinds=account  <masked window>
```

Add `.nambikkai/` to your `.gitignore` — the log is local telemetry, not history.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `NAMBIKKAI_ALLOW_RAW` | unset | `1`/`true`/`yes` downgrades blocks to logged warnings |
| `NAMBIKKAI_LOG` | `./.nambikkai/alerts.log` | alert log path |
| `NAMBIKKAI_CLASSIFIER` | unset | `1`/`true`/`yes` enables the opt-in LLM tier (needs `ANTHROPIC_API_KEY`) |
| `NAMBIKKAI_CLASSIFIER_MODEL` | `claude-haiku-4-5-20251001` | model for the classifier pass |
| `NAMBIKKAI_CLASSIFIER_TIMEOUT` | `8` | seconds before the pass fails open |
| `NAMBIKKAI_CLASSIFIER_CAP` | `16000` | chars of payload classified (beyond the cap: unclassified, documented) |
