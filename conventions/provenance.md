# Receipts — the provenance & validity convention

Every load-bearing fact in an agent-readable knowledge base carries where it came
from, when it was confirmed, how much to trust it, and when to re-check it. A fact
without a receipt is treated as unverified — the `provenance-lint` skill flags it.

## The tag

Append to the end of any line that states a durable fact:

```
[src: NAME | YYYY-MM | TIER | TTL]
```

Examples (all synthetic):

```
- Employer pension scheme is the XYZ fund; details in the vault.  [src: onboarding-pack.pdf | 2026-01 | firm | 12mo]
- Lease renews in September.  [src: self | 2026-03 | firm | review:2026-08]
- Landlord likely selling next year.  [src: assistant | 2026-05 | hunch | 3mo]
```

## Fields

| Field | Meaning | Values |
|---|---|---|
| `NAME` | Where it came from | a source filename · `self` (owner stated it) · `assistant` (the AI inferred it) · a short label |
| `YYYY-MM` | When confirmed/captured | month precision; use `YYYY-MM-DD` only when the day matters |
| `TIER` | How much to trust it | `firm` (documented) · `stated` (owner said so) · `inferred` (derived) · `hunch` (speculative) |
| `TTL` | When to re-check | `evergreen` · `permanent` · `expired` (terminal) · `<N>mo` · `<N>d` · `review:YYYY-MM` |

## Rules

1. **Tier gates usage.** A `hunch` may inform a suggestion; only `firm`/`stated` facts
   drive actions with side effects. If a weak-tier fact is being cited as if firm,
   that's a lint finding.
2. **Supersede, don't stack.** When a fact changes, update the line and its receipt.
   The old value lives in version control, not in the file. (Reconcile-don't-append.)
3. **Stale means re-check, not delete.** A lapsed TTL demotes the fact to unverified
   until re-confirmed.
4. **Corrections keep both dates.** If a fact was wrong, the fix's receipt records when
   the truth was learned — so "what did the system believe in March?" stays answerable.
5. **Sensitive values are pointers.** The receipt can cite a document in your secrets
   store; the fact line itself carries no raw identifier. The gate enforces this
   mechanically; write as if it didn't.
