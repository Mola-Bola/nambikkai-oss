# Commodity map — adopt what the category already proved (2026-07-18)

_Owner directive: don't reinvent the wheel; the unique core is provenance/truths/beliefs.
Everything else leans on what journaling + habit apps converged on. Two web-research passes
(journal apps · habit/QS apps), sources in the footers of each section's origin reports._

## The unique core (never outsource, never dilute)
Belief/truth ledger with valid-from/valid-to · persona mapping · import-and-digest with
loose-end popups · reflection loop · local-first privacy. Everything below exists to make the
app feel complete AROUND this core.

## Adopt into the MVP (commodity, users expect it — ranked)
1. Fast editor: markdown, autosave, edit-anytime, **backdating** (entry-date ≠ written-date —
   our bitemporal ledger does this natively; surface it, competitors do it badly)
2. Photo attachments (multiple, EXIF time/place) — media grid view
3. Instant local full-text search (SQLite FTS5)
4. **Calendar view** with entry-density dots ("year in pixels" variant) + timeline + map view
5. Tags + favorites + filters
6. **On This Day / throwback** — the #1 retention loop that isn't a streak; pure local query
7. Lossless export (JSON + Markdown + PDF) AND importers (Day One / Daylio / plain files) —
   import breadth is how Diarium wins switchers; ours feeds the digest wedge (M4) directly
8. Templates + prompt library — blank-page paralysis is the top quit reason
9. Gentle configurable reminders (easily silenced, never naggy)
10. One-tap mood: **two-stage capture** — fast valence×energy tap (Daylio speed), optional
    granular emotion word (How We Feel's 144-word model). Granular words are better provenance
    anchors for beliefs ("resentful" ≠ "bad") — this is where commodity feeds the core.
11. Location + weather stamps: capture-at-write via Open-Meteo (free, no key, has historical
    backfill), stored forever, editable — no ongoing service dependency
12. Cumulative stats + year-in-review: totals and comebacks, **no reset-to-zero streaks**
13. Passcode/biometric gate (WebAuthn platform authenticator) — cheap, expected, on-brand

## Calendar integration (the "your day pre-populated" pattern)
- v1: .ics file drop / synced-file watch, parsed with ical.js (+ ical-expander for recurrence);
  browser CORS blocks live Google/iCloud pulls — the local FastAPI backend can fetch the user's
  secret .ics URL instead (no CORS server-side), or CalDAV later via the desktop shell.
- UX to copy: **Apple Journal's suggestion-picker** — today's events shown as tap-to-insert
  chips; app stores nothing until the user taps. Privacy story + blank-page killer + every
  inserted chip carries source+timestamp = native provenance.
- End-state to aim at: the deariary pattern — the day pre-drafts itself from metadata, so a gap
  renders as "quiet days," never accusatory blanks.

## Habits (second horizon — mechanics already proven)
- **Loop Habit Tracker's exponential-smoothed strength score, not streaks** (GPL, algorithm
  minable: github.com/iSoron/uhabits) — never resets, forgives a miss, mathematically rewards
  comebacks. The 2026 category verdict: streak-reset is the #1 abandonment driver.
- Frequency schedules ("3×/week") as default · three-state days (done / skipped-with-reason /
  missed — rest is first-class) · anchor field for stacking ("after [routine]") + 2-minute
  starter · hard cap on active habits, start with 3.
- **Explicit comeback celebration** (Finch's warm return, Duolingo's welcome-back): almost
  nobody does it well — and our brand IS returning-after-a-gap. Differentiator on top of
  commodity. Bonus unique twist: revising an old belief on return is itself a rewarded
  comeback action — no app rewards re-reading, only writing.
- Life-area color-coding on actions (Finch's rainbow) for the balance/needs view — balance
  emerges from what's logged; no wheel-of-life ceremony.

## Phone-native data (honest constraints, macOS local app)
- Sleep/steps/workouts: **Health Auto Export** (iOS) → REST push to our localhost endpoint —
  the proven pipeline. Manual export.xml for backfill.
- Mac screen time: **ActivityWatch** (open source, local REST API) — solid; knowledgeC.db is
  the fragile hack. iPhone social-media minutes: weak link (Shortcuts or skip).
- Rule: every metric source-agnostic with manual entry as universal fallback.

## Skip list (category-proven dead ends)
Reset-to-zero streaks · punishment gamification (Habitica HP) · kitchen-sink factor tracking
(Bearable's 10-min logs kill adherence) · wheel-of-life as recurring ritual · opaque composite
wellness scores · cloud-LLM reading the diary (the category's own users are revolting toward
local — our brand already won this argument) · subscription/paywalled backup (top complaint
category-wide; we're local-first, say it loudly).

## Category complaint list = our checklist of trust promises
Never lose an entry · never paywall export/backup · lossless import/export always ·
no streak guilt · no naggy notifications · AI never reads entries off-device.

## Sequencing impact on MVP-CHARTER
M3 (persona) unchanged · **M4 import wedge gains competitor importers** (Day One JSON, Daylio
CSV, plain md/txt) · M5/M6 unchanged · M7 UI pass adopts: calendar view, on-this-day, tags,
search, two-stage mood, templates, export. Calendar chips + weather stamps = new M8. Habits =
its own charter after MVP, built on Loop's score model.
