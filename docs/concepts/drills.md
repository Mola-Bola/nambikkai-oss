# Drills

**Every incident becomes a permanent test, the day it's resolved.**

The fire drills use real past fires. When a leak, near-miss, or false positive happens
in a Nambikkai deployment, the `incident-to-eval` skill converts it into a synthetic
corpus case — same shape, invented values — and appends it to
[`corpus/cases.json`](../reference/corpus.md). From that day on, every test run replays
it, in every implementation, forever.

## The corpus is canonical, not the code

One golden corpus binds every port of the rules. The Python hooks pass it today; a
TypeScript port, an MCP server, a Go daemon must all pass **the same file** or they
don't ship. Rules drift between languages; a shared corpus doesn't.

Four groups keep it honest:

| Group | Assertion | Meaning |
|---|---|---|
| `must_mask` | caught | the guard's job |
| `must_stay` | untouched | false-positive protection |
| `known_overmatch` | still over-triggers | documented noise — warn, never block; if it stops over-matching, the test *fails* so the docs get updated |
| `known_gap` | still missed | published blind spots; if a gap case starts passing, the test fails so it gets promoted to `must_mask` |

Asserting your own false positives and blind spots is unusual. It means the
documentation can never quietly drift from reality — the test suite enforces the
honesty, not the maintainer's diligence.

## The at-rest trick

Every sensitive-shaped token in the corpus carries a `~~` splitter
(`S12~~34567D`), stripped at runtime by the test harness. So the corpus file itself
never contains a matchable identifier — **the corpus passes its own gate.** During
development, our gate blocked our own test file for violating this. We fixed the file,
not the gate.

## Drills as the contribution model

This is also how you contribute. A PR to Nambikkai is not an opinion about regexes —
it's an incident with a shape: *"here's a synthetic case the guard should catch (or
should stop tripping on), here's the smallest rule change that makes it pass."* A rule
without cases doesn't merge. Community incidents grow the corpus; the corpus hardens
every deployment.

Recipe: [Your first incident eval](../recipes/first-incident-eval.md)
