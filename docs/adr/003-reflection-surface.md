# ADR 003 · Reflection surface: juxtaposition first, questions offered, models local

- **Status:** accepted (owner decision 2026-07-18)
- **Binds:** the reflection loop (R2–R6) and every later surface where the engine
  digests a user's words — import (M4), the timeline (M6), habits, and anything after.

## Context

VISION's first principle is absolute: **no machine ever tells a user what they feel.**
Reflection is where that principle is easiest to break, because the useful thing to do
with a year of someone's writing is exactly the dangerous thing — notice a pattern and
name it. "You seem to spiral every time work goes quiet" is a sentence the engine could
produce and must never produce.

So the question for this charter was not *whether* to reflect, but what shape reflection
takes such that the user does the concluding and the machine only does the fetching.

Separately, matching entries by meaning implies a model. The obvious paths — an API call
to a hosted embedding model, or a library that downloads weights on first use — both
break ADR 001's rule 3 (tier 1 makes no runtime network calls). That needed deciding
before any code, not after.

## Decision

### 1 · Juxtaposition is the default surface

The primary reflection surface is **silent side-by-side**: while writing or reading an
entry, related past entries can be revealed next to it. The related entries are shown as
**raw user text and nothing else** — no summary, no theme name, no synthesised sentence,
no similarity score on screen. Zero machine-authored words.

It is **pull-based**. A faint indicator says related writing exists; the user clicks to
see it. No popups, no interruptions, no auto-expansion, nothing that arrives uninvited
while someone is mid-sentence.

The juxtaposition itself carries the meaning. Two of the user's own entries beside each
other is an observation the user makes, not one the engine hands them.

### 2 · The gentle-question layer is opt-in and asks, never asserts

A second layer may phrase a soft question about what was surfaced. It is:

- **off by default**, enabled only in Settings by the user's deliberate act;
- **question-form only** — "does this still sound right to you?", never "you felt X";
- **never diagnostic and never therapeutic** in vocabulary, per the standing doctrine;
- **drawn from a fixed, reviewed phrase set**, not generated per entry, so no sentence
  ever reaches a user that a human did not write and approve.

Only the user's **answer** enters the record. A question the engine asked is not a fact,
is not stored as an appraisal, and never becomes an input to a later question. If the
user dismisses it, nothing is written at all.

### 3 · Matching runs locally, and the model arrives by an explicit act

Relevance is computed on-device with a small local embedding model plus sqlite-vec.

- The model is **never fetched at runtime**. It arrives through a documented, one-time
  `make model` step that the user or builder runs deliberately, and the downloaded files
  are **checksummed** against values recorded in the repo before they are trusted.
- With no model present the app still runs; matching falls back to a deterministic
  local method that needs no download (see Consequences).
- The vector index is a **derived view**. It is rebuildable from the ledger at any time,
  it is never the source of truth, and deleting it loses nothing.

## The line that may never be crossed

1. **No machine-authored words about a user's inner life reach a screen.** The
   juxtaposition surface renders the user's own text, verbatim, or renders nothing.
2. **No asserted feeling-labels anywhere**, including tooltips, headings, aria-labels and
   export. A golden test asserts this against the reflection surfaces' copy.
3. **The engine's questions are not records.** Only user answers are written to a stream.
4. **No entry text leaves the device to be embedded.** Embedding is a local computation
   or it does not happen.
5. The index never becomes load-bearing. If the ledger and the index disagree, the
   ledger wins and the index is rebuilt.

## Consequences

- Two embedding backends exist behind one interface: a deterministic **lexical** backend
  (pure standard library, no download, always available) and a **static-embedding**
  backend used once `make model` has run. Vectors from the two are not interchangeable,
  so the index records which backend and dimension wrote it and rebuilds on a mismatch
  rather than silently mixing two spaces.
- Relevance fixtures are published in the repo and asserted in the test battery, with
  the known gaps and known overmatches named rather than hidden. A matcher that quietly
  degrades is worse than one with documented limits.
- `make model` is documented and optional. CI and the default test run must pass without
  it, which keeps the offline promise honest and testable.
- The mood-graph question (STATUS, "two deliberate departures") is closed by point 1:
  no machine-coloured days, ever. That is now settled doctrine, not an open item.
