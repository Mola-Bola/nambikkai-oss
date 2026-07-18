# Nambikkai

**The journal that keeps receipts — and keeps them yours.**

Nambikkai is an agentic journal. You tell it what you feel, what set it off, who it
involves (by role, never by name), and what you believe about it. It keeps those
beliefs the way an accountant keeps books: every entry carries provenance, every
belief carries *valid-from* and *valid-to*, and nothing is ever silently rewritten.
Over time it can show you where an ease or an unease actually stems from — "what I
believed then" next to "what I know now" — and when something you write sits close to
something you wrote before, it can put the two side by side, in your own words, for you
to draw your own conclusion from.

Not a chat app with memory. A ledger of personal truths, with an agent in service of it.

---

## Why this exists

Held truths compound like debt. A belief about a person, formed in one bad week and
never revisited, quietly accrues interest for years — in how you read their messages,
in what you don't say at dinner. Most journaling apps store *what happened*. None keep
receipts on *what you believed*, or notice when the belief is stale.

That's the whole product: **provenance for feelings.** Psychology calls the mechanism
appraisal — emotions arise largely from what you believe about an event or a person,
and revising the appraisal revises the feeling. A bitemporal belief ledger is
reappraisal with receipts. The science on writing it down is real and honest-sized:
naming a feeling precisely is itself regulating (affect labelling), and the effects of
expressive writing roughly *double* when the writing gets feedback. The reflection loop
is our answer to that last part, with one deliberate constraint: the feedback is your
own earlier writing placed beside the new, never a machine's opinion of it.

And one line we hold everywhere, in copy and in code: **Nambikkai is a journal, never
therapy.** No diagnosis, no treatment language, anywhere. When the record looks heavy,
it suggests distance, a walk, a human — warmly, and nothing more.

## Privacy is the first feature

A journal holds the most personal data any agent system will ever touch. So the
guarantees are architecture, not marketing:

- **Local-first.** Entries live in a ledger on your machine. They never ride a commit,
  a sync, or anyone's training run. There is no cloud copy to breach.
- **People by role, never by name.** "The manager", "my spouse" — identity-class
  values are not retained, mechanically (a vault-side roles map plus a redaction net
  over every stored field).
- **Hash-chained entries.** Each row chains to the last. Yesterday's entry can't be
  quietly rewritten — by you at 2am, by a bug, or by anything else. Receipts are real.
- **The reflection loop proposes, never acts.** Stage-only autonomy, inherited from
  the trust layer this journal is built on.

## The engine room (where the trust layer went)

Nambikkai began as the extracted trust layer of a production personal life-OS — a
redaction gate, a provenance convention, a golden corpus, an MCP server. That layer
wasn't shelved; it became the journal's invisible core:

| Was (the trust layer) | Is (the journal) |
|---|---|
| Bitemporal receipts `[src \| date \| tier \| ttl]` | Entry & belief provenance — "believed then / known now" |
| Redaction gate + classifier (the perimeter) | The privacy spine: people-by-role, identity non-retention |
| The golden corpus + `incident-to-eval` flywheel | The honesty discipline — every guard provably tested, every gap published |
| Stage-only autonomy convention | The reflection loop's leash — it suggests, you decide |

The developer-facing pieces still exist and still pass their suites (`plugin/`,
`mcp/`, `corpus/`, `conventions/` — run `python3 tests/test_guard.py` and
`tests/test_mcp.py` any time). The dev-tool *positioning* retires; the mechanism is
now judged by what it protects.

## Status

Local web-app MVP (charter 2026-07-17): a FastAPI backend wrapping the engine, a
React front, everything on localhost. The builder is user #1; the product generalises
from what demonstrably works on a real life, not a persona.

- **Capture** — a `journal:` message routes to the chained truth ledger (shipped)
- **Reflection loop** — weekly, gentle-suggestive, self-distancing by design; drafts
  reviewed by the owner before a single message sends (in build)
- **Habit tracker** — gamified for *returning after a gap*, not streak-guilt; built
  for bad weeks, because those are the weeks the product exists for (after the journal
  loop earns daily use)
- **Grounding** — calibration only against licensed research corpora (ISEAR,
  Covid-ED, GoEmotions, EmpatheticDialogues) behind a binding ethics gate: no scraped
  blogs, nothing regurgitated, and user entries never leave the local spine for
  training

## What's in the box

```
nambikkai/
├── plugin/            Claude Code plugin — the redaction gate + provenance skills (the perimeter)
├── mcp/               trust-gate MCP server — check / redact / tag_fact / lint
├── corpus/            the golden corpus (synthetic, split at rest) — binds every implementation
├── conventions/       provenance receipts · trust doctrine · stage-only autonomy
├── research/          the science, market, law, and data-ethics grounding
├── tests/             self-tests: corpus drift-guard + gate + server-vs-corpus
└── docs/              the full documentation
```

## License

[MIT](LICENSE) © [publisher TBD]

---

*நம்பிக்கை (nambikkai) — Tamil: trust, faith, hope. It used to name a guardrail for
developers. It now names what a journal has to earn from a person.*
