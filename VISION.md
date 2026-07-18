# Nambikkai — vision & roadmap (living doc)

_Owner's working vision, captured 2026-07-17. Explicitly NOT gospel — evolving, to be reasoned
with. Sessions: read this before proposing anything. When the owner adds or revises a point,
update THIS file — roadmap thoughts do not live in chat or life-os handoffs anymore._

## The product in one line
A journal that maps what you feel, who shaped it, and what you've concluded about them —
keeping receipts so the picture of your life stays honest and revisable.

## Core loops (MVP horizon)

### 1 · Directed loose journaling
Free-form entries, gently directed by four questions: what are you feeling · why · who or what
caused it · what are you doing (or have done before) that helps. The mess is the format — never
reject an entry for shape.

### 2 · Persona mapping
- Anyone/anything can be a persona: people, pets, objects. Users assign aliases or names —
  their choice (see Tension T1).
- Each persona carries: how they've been involved (positive/negative) · how they've helped or
  shaped you · what you thought of them before vs now · whether they're still relevant.
- Loose journals that mention personas are kept in context of that persona's thread and the
  user's timeline — the entry feeds the map without extra effort.

### 3 · Truths (the appraisal ledger)
Beliefs formed about others through actions done / done-to. Held truths — positive or negative,
still carried — can be drafted as "what I'd share with them", stored privately for the user's
own later reference (resurfaced when the persona reappears or on revisit). Valid-from/valid-to
provenance underneath (the engine already does this).

### 4 · Import & digestion (the onboarding wedge)
Users dump existing journals (any format). Nambikkai digests: maps thoughts, beliefs, personas,
timeline, sentiment — WITHOUT forcing completion. Unknown personas/events become gentle
loose-end popups on open: "You mentioned Person X before — who are they?" Answer when ready,
never gated. (This is likely the killer first-run experience: instant value from life already
written, no cold start.)

### 5 · Sentiment timeline
A ledger of one-sentence highlights/sentiments — the digestible big picture of a life. The
surface where users see themselves whole.

## Second horizon
- **Habits, holistically:** good habits compound; log manually AND (opt-in, reasonable) fetch
  natively — screen time, sleep, etc. from phone systems — when the user says they want to cut
  down or build up. One holistic view.
- **Basic-needs reflection:** sleep · diet · exercise · relationships · comfort (Maslow-ish fit
  TBD) — show where a user may be lacking and what they might do.
- **Good-news feed:** objectively good news only — restoration-of-faith good, not
  counter-negative good ("war ended" ≠ the bar; "thing got genuinely better" is).

## Third horizon (bigger bets, need design)
- **Group-chat companion:** an opt-in bot deployed into shared chats (friends/family/colleagues)
  recording sentiments and life events, feeding each linked member's own journal.
- **Open human platform:** real humans sharing good and bad truths, filterable (age, occupation,
  location…) so people find truths general or near to their lives. **Bot-free as much as
  possible — feeds are populated by humans.**

## Open tensions (to reason through, not resolve by default)
- **T1 · Names vs roles.** The engine's doctrine is people-by-role / identity non-retention
  (born from the builder's own privacy bar). The product vision says users may use real names.
  Likely resolution: user-owned device, user's choice — alias-first default, names allowed
  locally, roles enforced only on anything that leaves the device. NOT yet decided.
- **T2 · Local-first vs social/cloud.** The brand is "no cloud to breach"; horizons 2–3 (feeds,
  platform, group bot) need servers. Likely resolution: tiered — journal core stays local-first
  forever; social surfaces are separate, opt-in, and never receive ledger contents. NOT yet
  decided.
- **T3 · Calibration data.** Reflection/voice calibrates on licensed corpora + synthetic
  personas. The builder's own journals are an OPTIONAL enrichment, not a gate (owner decision
  2026-07-17 — supersedes earlier "blocked on journal pages" framing everywhere it appears).

## Sequencing sanity (proposed, owner steers)
Capture (shipped) → Import & digestion (wedge) → Persona map + loose-end popups → Truths ledger
surfaces → Sentiment timeline → Reflection loop v1 (corpus-calibrated) → habits → the rest.
