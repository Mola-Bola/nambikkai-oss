# Rule pack & known gaps

## v0.1 rule pack

Ordered — more specific rules win overlap ties. Masks are partial by design: enough
survives to recognize *which* value was meant, never enough to reconstruct it.

| Kind | Shape | Mask example | Mode |
|---|---|---|---|
| `nric` | SG NRIC/FIN: `[STFGM]` + 7 digits + letter | `SXXXX676B` | **block** |
| `passport` | letter + 7–8 digits; 1–2 letters + 6–7 digits + optional letter | `K123****5` | **block** |
| `phone` | AU mobile `04xx xxx xxx` | `0402 6XX XXX` | **block** |
| `account` | 12–19 digit runs (spaces/dashes ok) | `****1234` | **block** |
| `dob` | `dd/mm/yyyy`, `dd-mm-yyyy` | `MM/YYYY` | warn |
| `brokerage` | 6+ char mixed letter+digit token | `U123****45` | warn |

**Why two modes:** `dob` and `brokerage` shapes over-trigger on ordinary dates and
codes (order numbers, commit-ish strings, flight refs). Blocking them would train
users to reflexively override — which kills the perimeter. They warn and log instead,
and the corpus *asserts* each documented overmatch (`O-01…O-04`) so the noise level is
tracked, not vibes.

## Known gaps {#known-gaps}

What regex fundamentally cannot see — published as corpus cases `G-01…G-04`, asserted
as *missed* on every test run:

1. **Free-text names.** A person's name in prose is regex-invisible. The prose-level
   convention (refer to people by role, not name) is the only net until a classifier
   pass ships.
2. **Bare money amounts.** `$8,400` is indistinguishable from a price in a shopping
   note.
3. **Chat display.** No harness primitive rewrites assistant text before display — the
   Stop flag *detects and logs* chat leaks; it cannot prevent them.
4. **Semantic leakage.** "My salary is my age times three thousand" leaks with zero
   identifier shapes. Out of scope for pattern matching, stated plainly.

If a gap case ever starts passing, the self-test **fails** — forcing its promotion to
`must_mask` and an update to this page. Honesty, enforced mechanically.

## Extending the pack

Regional identifier packs (US SSN, UK NI, IN Aadhaar…) are welcome — as corpus PRs.
Bring `must_mask` cases *and* the `must_stay` cases proving your pattern doesn't eat
ordinary text. A rule without cases doesn't merge.
