# Nambikkai — vision & roadmap (living doc)

_Owner's working vision, captured 2026-07-17. Explicitly NOT gospel — evolving, to be reasoned
with. Sessions: read this before proposing anything. When the owner adds or revises a point,
update THIS file — roadmap thoughts do not live in chat or life-os handoffs anymore._

## The product in one line
A journal that maps what you feel, who shaped it, and what you've concluded about them —
keeping receipts so the picture of your life stays honest and revisable.

## Audience & voice (owner steering, 2026-07-18)
- **Built for individuals** — one person, their own device, their own life. Teams/groups are
  third-horizon at most; nothing in the MVP assumes an org.
- **Layman-first wording everywhere a user reads.** People in general don't know what
  "provenance" is. Engine jargon (provenance, bitemporal, ledger, redaction, egress) stays in
  technical docs and code; the UI says things like "believed then / know now", "keeps receipts",
  "your words never leave this device". Technical framing is fine for technical folks — but the
  product speaks human.
- **Copy sounds like a person, not a machine.** No em-dashes in on-screen copy (they read as
  AI-written); plain sentences, ordinary words. Prompt phrasing follows the journaling research
  (research/2026-07-14-journal-grounding.md), not invention: invite a *specific* feeling word,
  capture the antecedent, keep the "why" light so it never becomes rumination.
- **Prompt hints stay.** The small grey hints under each question earn their place — they give
  permission ("no need to be sure") rather than instruct.
- **A short usage guide before the first entry** _(owner, 2026-07-18 — ACCEPTED, built)._
  People shouldn't land on a blank form and have to guess what this is for. A brief, skippable
  orientation before they kick things off: what the four questions are for, that mess is fine,
  that nothing leaves the device. Never a gate, never a tour that must be completed.

## First principles (owner, 2026-07-18)
- **No machine ever tells a user what they feel.** No predictive models, no markov-chain
  mood-forecasting, no sentiment score asserted as fact. Feelings are not to be trifled with;
  the product's power is each individual realising their truths for themselves. Nambikkai hands
  people tools — never conclusions. Wherever the engine digests (import M4, timeline M6),
  machine output is a *question offered* ("does this sound right to you?"), never a label
  asserted. The user confirms, edits, or dismisses; only their answer enters the record.
  **Settled 2026-07-18: no machine-coloured days, ever.** The mood graph from the early mock
  (days tinted by feeling-word, a tone line drawn across the month) is dead and stays dead.
  The month grid marks only *you wrote here* and *a truth changed here*. This was the last
  open question against this principle and it is now closed, not deferred (ADR 003).
- **Against the feed, for connection.** Human connectivity is needed at an all-time high.
  Algorithms today think for us and feed us what we want, not what we humans need — connection
  to nature, to one another, to ourselves. Nambikkai exists to restore that: nambikkai in
  themselves, in others, in the world.
- **The builder's own story moves the platform.** From life-os, the work with AI, where that took
  him — that arc (how Nambikkai started, shifted, and where it's headed) is the narrative spine
  for telling the product's story. Not needed now; never forgotten.

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

### 6 · Reflection (owner decisions, 2026-07-18 — accepted, ADR 003)
The loop that makes a journal worth keeping: your past writing, brought back to you at the
moment it's relevant. Three decisions fix its shape.

- **Silent juxtaposition is the default.** While writing or reading, related past entries can
  be revealed beside the current one — your own words, raw, nothing else. No summary, no theme
  name, no score on screen. The pairing *is* the insight, and you're the one who has it.
- **Pull, never push.** A faint mark says there's something related. You click, or you don't.
  Nothing pops up mid-sentence.
- **A gentle-question layer, opt-in and off by default.** When switched on, the app may ask a
  soft question about what surfaced — "does this still sound right to you?" — drawn from a
  small set of phrases a human wrote. It never states what you felt. Your answer is the only
  thing that enters the record; a dismissed question leaves no trace.
- **Matching is local.** Semantic search on the device (sqlite-vec plus a small local model).
  The model is fetched once by an explicit, checksummed step, never silently at runtime, and
  no entry text is ever sent anywhere to be matched. The index is derived and rebuildable;
  the ledger stays the only source of truth.

## Second horizon
- **Habits, holistically:** good habits compound; log manually AND (opt-in, reasonable) fetch
  natively — screen time, sleep, etc. from phone systems — when the user says they want to cut
  down or build up. One holistic view.
- **Habit-app integrations (owner, 2026-07-18):** lean on the apps people already use rather
  than rebuilding them — Strava for running, AllTrails for hikes, and whatever else is commonly
  used per activity (survey per habit type before building). Imported activities compound with
  the user's own notes and habits where they fit, so a bigger picture forms. Opt-in per source,
  source-agnostic schema, manual entry always the fallback (see docs/commodity-map.md: Health
  Auto Export REST push, ActivityWatch local API — same pattern, more sources).
- **Basic-needs reflection:** sleep · diet · exercise · relationships · comfort (Maslow-ish fit
  TBD) — show where a user may be lacking and what they might do.
- **Good-news feed:** objectively good news only — restoration-of-faith good, not
  counter-negative good ("war ended" ≠ the bar; "thing got genuinely better" is).

## Folded from life-os — proven there, adopted here (owner, 2026-07-19)
_life-os is the R&D bench; these patterns earned their keep in daily use. Folded as product
direction — each still lands through its own charter, none silently jumps the sequencing
at the bottom of this file._

- **Capture-anywhere (the biggest proven win).** life-os's highest-volume, most-durable loop
  is zero-friction phone capture: write plainly, and the *place* you write decides what
  it is (the Journal room needs no prefix — place over prefix; the 7-topics→4-rooms
  simplification). The journal needs its own capture surface beyond the browser,
  phone-first, no grammar for the default case. This promotes the charter's parked
  "Telegram bridge" from OUT to **first post-MVP charter candidate** — slot before or
  alongside habits, owner's call (flagged, not silently resequenced). Evidence: 100+
  captures/day on flood days; capture held even on days everything else slipped.
- **Promote-to-truth (the life-os-save pattern).** life-os's lesson: good synthesis dies in the
  chat it was written in unless promoted back into the spine. The journal's version: one
  gesture from any entry or reflection answer — "keep this as a truth" — drafts a truth
  (dated, provenance attached) for the user to confirm or edit. The user's tap writes it;
  nothing auto-files.
- **The engine room made visible (Keeper's-Note + Freehold patterns).** For a product
  whose brand is trust, the engine's own receipts deserve a surface: what ran locally
  (imports, index rebuilds, backups) and the network doors — "zero outbound calls this
  session, verified" as a live check, not a promise in copy. Machine words about the
  MACHINE are fine; the line stays absolute for words about the person.
- **Backups where silence is a finding.** life-os's vault backup failed six nights running
  for a dumb reason (the Mac was asleep) and only a liveness meter caught it. Nambikkai's
  backup story (currently manual) adopts the rule: scheduled local backup + a liveness
  check where "the job didn't run" surfaces as loudly as "the job failed". Sleep-aware
  scheduling from day one.
- **Question discipline for loose ends (the Mailbox clarify-loop).** Uncertainty-gated,
  hard-capped per sitting (life-os caps 2 per batch), always dismissible, never re-asked in
  the same breath. M4's loose-end popups adopt the cap as doctrine — today's 12-question
  demo guard becomes a product rule with a real (smaller) number.
- **Notification doctrine, if reminders ever ship (the Butler pattern).** Quiet hours · a
  hard daily cap · user-set loudness classes · a dismissal is permanent. Second-horizon
  reminders inherit this shape; "gentle" is a mechanism, not a tone.
- **A return ritual, pull-first (the briefs pattern, inverted).** life-os's morning/evening
  briefs prove cadence compounds. The journal's version must obey ADR 003: an opt-in
  weekly "look back" assembled ONLY from the user's own words (entries returned, truths
  that changed, on-this-day), surfaced as a quiet marker on open — never a push, never a
  summary in the machine's voice. This is also where the reflection loop's
  "feedback doubles the effect" science gets its cadence.

### Looked at in life-os, deliberately NOT folded
- **Brain-power-style scores on the person.** A number grading the user's inner life
  violates the first principle outright. Engine health may have a meter; the person
  never does (the owner's own operator-meter idea stays a life-os experiment, not a product
  feature, unless it re-enters as pure self-report the user authors).
- **Push briefs / proactive messages into the user's day.** life-os's owner opted in as an
  operator; a journal user didn't. Pull stays the default (ADR 003).
- **The daemon fleet / supervisor complexity.** life-os needs it; a single local app doesn't.
  Every moving part spends trust budget.
- **Cost/token metering surfaces.** Tier 1 makes no runtime API calls; there is nothing
  to meter and nothing to show.

## Third horizon (bigger bets, need design)
- **Group-chat companion:** an opt-in bot deployed into shared chats (friends/family/colleagues)
  recording sentiments and life events, feeding each linked member's own journal.
- **Open human platform:** real humans sharing good and bad truths, filterable (age, occupation,
  location…) so people find truths general or near to their lives. **Bot-free as much as
  possible — feeds are populated by humans.**

## Going public — domains, identity, first wave (owner, 2026-07-19)
- **Domains bought:** `journal.example` = the journal (human-facing, layman copy, warm) ·
  `engine.example` = the engine room (trust gate, MCP server, provenance spec, builder
  docs). Split confirmed by the owner.
- **Identity:** publish under a **separate org identity** — new GitHub org + email on the
  nambikkai domains. The doctrine's "identity door" opens; personal accounts stay
  isolated, no leak crossover. The `[publisher TBD]` in PITCH/README resolves to the org.
  **Org created 2026-07-19: `github.com/<org>`** (email spine live on
  engine.example via Cloudflare catch-all → org inbox).
- **First wave (publishable from the current repo):** landing pages on both domains ·
  the trust-gate MCP server (check/redact/tag_fact/lint, stdlib-only, corpus-bound) ·
  the Claude Code plugin + skills (redaction gate, incident-to-eval, provenance-lint).
- **Queued behind it (a real job, days not hours):** extract + scrub the Telegram
  machinery from life-os (rooms / session broker / butler / triage / thread-aware I/O) into a
  standalone publishable component. It lives tangled in personal infra today; extraction
  goes through the perimeter + a red-team pass before any flip.
- **Standalone-extraction doctrine (owner, 2026-07-19).** The working repos (this one and
  ~/life-os) are the TEST GROUND — nothing ever publishes from them directly, and neither repo
  ever flips public. Every public component is a clean-room extraction into its own repo
  under the org: **fresh git history** (no inherited commits — old history can carry
  personal paths and mistakes), its own CI, its own copy of the corpus binding (the corpus
  is synthetic, so it travels), versioned releases, LICENSE, and a red-team pass before
  the first flip and each release. The test ground then consumes the published package
  back as a dependency where practical — so what we ship is what we ourselves run, one
  version behind the bleeding edge, never the bleeding edge itself.
- **Claims discipline binds the public surface:** state plainly what's built (egress
  perimeter, not input; recall limits published); the weekly audit red-teams the public
  repos before and after each flip. Nothing overclaims — trust is the brand.

## Velocity doctrine (owner, 2026-07-19)
- **Charter mode.** The owner approves a charter's goal once; sessions build it
  end-to-end with NO per-stone check-ins. Tests + goldens are the gate, not nods.
- **Session close = a ≤10-line delta in STATUS.** No narratives, no word-vomit recaps.
  The owner reads deltas async and steers by exception.
- **NOT loosened:** the product's own privacy doctrine (stage-only autonomy for the
  app's agents, no machine feeling-labels), remote push, and public flips — those three
  stay on the owner's word, always.

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
surfaces → Sentiment timeline → Reflection loop v1 (local semantic, ADR 003) → habits → the rest.
