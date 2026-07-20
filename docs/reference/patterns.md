# Rule pack & known gaps

## v0.2 rule pack (the everyday pack)

Ordered — more specific rules win overlap ties. Masks are partial by design: enough
survives to recognize *which* value was meant, never enough to reconstruct it.

| Kind | Shape | Mask example | Mode |
|---|---|---|---|
| `email` | local@domain.tld | `m***@example.com` | warn · **prompt** |
| `nric` | SG NRIC/FIN: `[STFGM]` + 7 digits + letter | `SXXXX676B` | **block** |
| `iban` | real country code + 2 digits + 11–30 alnum (compact or 4-grouped) | `DE89****…3000` | **block** |
| `passport` | letter + 7–8 digits; 1–2 letters + 6–7 digits + optional letter | `K123****5` | **block** |
| `ssn` | US SSN, dashed `ddd-dd-dddd` only | `***-**-8121` | **block** |
| `phone` | AU mobile `04xx xxx xxx` · intl `+cc` (8–15 digits) · US `(ddd) ddd-dddd` | `0402 6XX XXX` | **block** |
| `dob` | `dd/mm/yyyy`, `dd-mm-yyyy`, ISO `yyyy-mm-dd` | `MM/YYYY` | warn |
| `account` | 12–19 digit runs (spaces/dashes ok) | `****1234` | **block** |
| `ip` | IPv4 quad | `192.*.*.*` | warn |
| `geo` | decimal lat, long pair, ≥3 decimals each | `-33.***, 151.***` | warn |
| `brokerage` | 6+ char mixed letter+digit token | `U123****45` | warn |

**Why two modes:** `dob`, `brokerage`, `ip` and `geo` shapes over-trigger on ordinary
dates, codes and version strings (order numbers, commit-ish strings, flight refs,
lockfile quads). Blocking them would train users to reflexively override — which kills
the perimeter. They warn and log instead, and the corpus *asserts* each documented
overmatch (`O-01…O-06`) so the noise level is tracked, not vibes.

**Email is warn at the gate, prompt in the app.** Emails saturate legitimate dev
payloads (commit trailers, configs, docs), so the egress gate logs rather than halts.
The journal app's save-time blur/keep question uses `PROMPT_KINDS`
(= `BLOCKING_KINDS` ∪ `{email}`): asking the person there is cheap and right.

**Why IBAN can block:** the rule is anchored on a real ISO country prefix, so bare
uppercase wire refs (which stay `brokerage`, warn) don't reach it.

## Known gaps {#known-gaps}

What regex fundamentally cannot see — published as corpus cases `G-01…G-05`, asserted
as *missed* on every test run:

1. **Free-text names.** A person's name in prose is regex-invisible. The prose-level
   convention (refer to people by role, not name) is the only net until a classifier
   pass ships.
2. **Bare money amounts.** `$8,400` is indistinguishable from a price in a shopping
   note.
3. **Bare dashed US phones.** `555-123-4567` shares its shape with part and serial
   numbers; only the anchored forms (`(415) …`, `+1 …`) are caught.
4. **Chat display.** No harness primitive rewrites assistant text before display — the
   Stop flag *detects and logs* chat leaks; it cannot prevent them.
5. **Semantic leakage.** "My salary is my age times three thousand" leaks with zero
   identifier shapes. Out of scope for pattern matching, stated plainly.

If a gap case ever starts passing, the self-test **fails** — forcing its promotion to
`must_mask` and an update to this page. Honesty, enforced mechanically.

## Extending the pack

Regional identifier packs (UK NI, IN Aadhaar, EU national IDs…) are welcome — as
corpus PRs. Bring `must_mask` cases *and* the `must_stay` cases proving your pattern
doesn't eat ordinary text. A rule without cases doesn't merge.
