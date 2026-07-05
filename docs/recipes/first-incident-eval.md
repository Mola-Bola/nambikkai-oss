# Your first incident eval

Something slipped through — or the guard blocked something it shouldn't have. Good:
that's raw material. Ten minutes turns it into a permanent fix for everyone.

## Worked example

**The incident:** your agent wrote a meeting note containing a colleague's passport
number (pasted from an email) to a tracked file, and the gate missed it because the
number had internal spaces the passport rule didn't allow.

## 1 · Say the words

> log this incident

The `incident-to-eval` skill walks the capture: what leaked, through which surface
(file write · shell arg · MCP payload · chat reply), what should have happened.

## 2 · Synthesize — never copy

The case reproduces the **shape**, with invented values, split at rest:

```json
{
  "id": "R-11",
  "kind": "passport",
  "input": "his passport K12~~34 567 noted from the email thread",
  "note": "passport with internal spaces — missed 2026-07, file-write surface"
}
```

Rules: synthetic values only · `~~` splitter inside the sensitive token · next id in
sequence · a `note` naming the incident class.

## 3 · Run the self-test

```bash
python3 tests/test_guard.py
```

The new case **fails** — the rules can't catch it yet. That failure is the
specification.

## 4 · Smallest rule change that passes

Extend the passport pattern to tolerate internal spaces; re-run; all green — including
every previous case, so the fix didn't break the false-positive protections
(`must_stay`) or quietly close a documented gap without promoting it.

## 5 · Commit both together

Case + rule change in one commit, one line in `INCIDENTS.md`:

```
2026-07-05 · passport w/ spaces missed on file-write · guarded by R-11
```

## If it's not catchable

Free-text names, bare amounts, semantic leakage — regex can't see them. File it as
`known_gap` instead. That's not a shrug: gap cases are *asserted as missed* on every
run, so the day the rules grow, the suite forces the promotion. Published debt beats
hidden holes.
