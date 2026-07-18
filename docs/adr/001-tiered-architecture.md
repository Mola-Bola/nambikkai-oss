# ADR 001 · Tiered architecture: local core forever, social as separate opt-in services

- **Status:** accepted (owner decision 2026-07-17, T2; recorded 2026-07-18)
- **Binds:** every stone from M2 onward, and every future charter.

## Context

The brand is "no cloud to breach" — the journal core is local-first and that is the
product's spine, not a feature. But horizons 2–3 (good-news feed, open human platform,
group-chat companion) cannot exist without servers. Left undesigned, server needs leak
backwards into the core "just for now" and the brand dies quietly.

## Decision

Two tiers, decided now, before any server code exists:

**Tier 1 — the journal core.** Entries, personas, truths, timeline, import, reflection
drafts. Runs entirely on the user's device: chained jsonl ledger as source of truth,
SQLite for views, FastAPI bound to localhost, zero network calls at runtime. This tier
is local **forever** — not "local until we scale".

**Tier 2 — social surfaces (future).** Feed, platform, group companion. Separate
opt-in services with their own storage and their own accounts. They are clients of
nothing in tier 1.

## The line that may never be crossed

1. **Ledger contents never leave the device.** No entry, truth, persona record,
   timeline row, or draft is ever transmitted to tier 2, to telemetry, or to any
   third party. There is no "anonymised" exception.
2. Anything that ever crosses outward is **user-authored for sharing, explicitly
   exported by the user's own action**, and passes the egress policy (ADR 002).
3. Tier 1 makes **no runtime network calls** — no analytics, no update pings, no
   remote models. Calibration happens at build time against licensed corpora.
4. Device-to-device sync, if it ever exists, is a new ADR — not an amendment here.

## Consequences

- The MVP web app binds `127.0.0.1` only; a test asserts no outbound sockets.
- The engine gets one egress choke-point; every export path goes through it.
- Tier 2 can never be bolted onto the core database "because it's already there" —
  it must be built as a separate service or not at all.
