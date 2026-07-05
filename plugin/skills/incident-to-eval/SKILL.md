---
name: incident-to-eval
description: Convert a failure, near-miss, or leak into a permanent regression case in the Nambikkai golden corpus (or your project's eval set). Trigger when the user says "log this incident", "that was a leak", "add this as an eval", "the guard missed something", or right after any guard failure is discovered.
---

# incident-to-eval

The drill discipline: **every incident becomes a test the day it's resolved.** A
guard without a corpus is a hope, not a guard. This skill scaffolds the case.

## Steps

1. **Capture the incident** — get from the user (or the conversation): what leaked
   or nearly leaked, through which surface (file write · shell arg · MCP payload ·
   chat reply), and what should have happened.
2. **Synthesize the case** — write a NEW input string that reproduces the *shape* of
   the failure with entirely synthetic values. NEVER copy the real leaked value.
   Insert the `~~` at-rest splitter inside any sensitive-shaped token so the corpus
   file itself never contains a matchable identifier.
3. **Classify it**:
   - Guard should catch it and now can → `must_mask` (with `kind`).
   - Guard flagged something it shouldn't have → `must_stay`.
   - Guard over-triggers on this shape but blocking would cry wolf → `known_overmatch`.
   - Guard cannot see this class yet (e.g. free-text names) → `known_gap` — honest
     debt, documented, not hidden.
4. **Assign the next id** in the group's sequence (R-xx / S-xx / O-xx / G-xx) and
   append to `corpus/cases.json` with a one-line `note` explaining the incident class.
5. **Run the self-test** — `python3 tests/test_guard.py`. A new `must_mask` case that
   fails means the rules need extending: propose the smallest pattern change, re-run,
   and only then commit both together.
6. **Record** — one line in the project's incident log (create `INCIDENTS.md` if
   absent): date · what happened · surface · case id that now guards it.

## Rules

- Synthetic values only, split at rest. The corpus must pass its own gate.
- A `known_gap` entry is a promise to revisit, not a shrug — link it from the
  incident log.
- Never weaken an existing case to make a new one pass.
