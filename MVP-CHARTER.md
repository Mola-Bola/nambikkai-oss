# Nambikkai MVP — web app charter (2026-07-17)

_Owner-authorised: full MVP fleshed out at once, web-app first, testable end-to-end. Solo-builder
mode: ship testable vertical slices the owner can open in a browser and critique — depth without a
touchable picture is useless. Decisions T1 + T2 taken (below). VISION.md is the source of truth._

## Decisions taken (2026-07-17, owner)
- **T1 · Names:** user's choice — alias-first suggestion, real names allowed; all local.
  Roles-enforcement applies only at egress (exports, anything leaving the device). Engine gains
  a per-field policy for journal tables.
- **T2 · Architecture:** design the tiered split NOW as an ADR (M1) — local core forever;
  social/feeds/group-bot are future separate opt-in services that never receive ledger contents.
- **Calibration:** licensed corpora + synthetic personas. Owner's own journals = optional, never
  a gate.

## Shape
Local web app: **Python backend (FastAPI)** wrapping the existing engine (hash-chained ledger,
provenance, redaction net, classifier) + **React/Vite/TS frontend**. Everything on localhost;
zero external calls at runtime. One command to run (`make dev` or equivalent). SQLite for
queryable views, the chained jsonl ledger stays the source of truth.

## Stones (each ends OWNER-TESTABLE in the browser)

**M0 · Housekeeping:** merge `journal-pivot` with the two tweaks (fix stale "riding the life-OS"
line; publisher name → TBD placeholder) · commit VISION.md + CLAUDE.md · push on owner's word.

**M1 · ADR:** `docs/adr/001-tiered-architecture.md` (local core vs future social tier, what may
never cross the line) + `002-identity-policy.md` (T1). Short, decisive, binding on later stones.

**M2 · Skeleton + capture:** app boots; directed journaling screen (feeling · why · who/what
caused it · what helps) + loose free-form mode. Entries land in the chained ledger with
provenance. TEST: owner writes a real entry in the browser.

**M3 · Persona model + map:** personas (people/pets/things; alias or name per T1) with
involvement (±), helped/shaped, thought-then vs think-now, relevance flag. Entries mentioning a
persona attach to its thread. Map/list view. TEST: owner creates personas, sees threads.

**M4 · Import & digestion (the wedge):** drop/paste old journals (txt/md first) → digest into
dated entries, personas, sentiment, timeline. Unknown personas/events → a loose-ends queue,
NEVER blocking. On app open: gentle popups ("You mentioned X — who are they?"), answer or
dismiss. TEST: owner imports something real (or the synthetic demo set) and watches the map fill.

**M5 · Truths ledger:** beliefs formed about personas (done / done-to), valid-from/valid-to
visible ("believed then / know now"); "what I'd share with them" drafts stored privately,
resurfaced on that persona's reappearance or revisit. TEST: owner records a truth, revises it,
sees the receipt.

**M6 · Sentiment timeline:** the big-picture surface — one-sentence highlights/sentiments on a
scrollable life timeline. TEST: owner sees their imported + written life at a glance.

**M7 · Demo data + polish:** synthetic persona/journal demo set (corpus-derived, clearly
labelled DEMO, one-click wipe) so testing never needs real data. UI pass. Battery: engine suites
+ new goldens (capture schema, import mapping, chain tamper, egress-policy).

## Rules
- Engine reuse over rewrite — the ledger/redaction/provenance code exists; wrap it.
- A journal, never therapy — copy and code. Ethics gate binds (no scraping, nothing regurgitated).
- No fixture rendered as live: demo data is labelled and wipeable, never default-on.
- Owner tests after EVERY stone; his critique steers the next before it starts. Small commits.

## Acceptance (the owner's test, end of charter)
Open browser → write a directed entry → import an old journal → see personas + timeline appear →
answer one loose-end popup → record and revise a truth → wipe demo data. All local, all fast.

## OUT (next charters)
Reflection loop v1 (corpus-calibrated) · habits · needs view · good-news feed · social platform ·
group bot · mobile packaging · Telegram bridge for the app.
