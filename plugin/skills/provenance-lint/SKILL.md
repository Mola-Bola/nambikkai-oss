---
name: provenance-lint
description: Sweep a markdown knowledge base for facts without provenance receipts, stale facts past their re-check date, and contradictions. Trigger when the user says "lint my vault", "provenance sweep", "check for stale facts", "which facts are unverified", or on a scheduled hygiene pass.
---

# provenance-lint

Audits a markdown knowledge base against the Nambikkai receipt convention
(`conventions/provenance.md`): every load-bearing fact carries
`[src: NAME | YYYY-MM | TIER | TTL]`.

## Steps

1. **Scope** — ask for (or infer) the root directory of the knowledge base. Default:
   the current project's context/notes directory. Never scan secrets stores.
2. **Sweep** — for every `.md` file in scope, examine lines that state durable facts
   (declarative statements about people, money, dates, decisions, status). For each:
   - 🏷️ **Untagged** — states a fact but carries no `[src: …]` receipt.
   - ⏳ **Stale** — the TTL has lapsed: `<N>mo`/`<N>d` past the date field, or
     `review:YYYY-MM` in the past. `evergreen`/`permanent`/`expired` never go stale.
   - 🔻 **Weak tier under load** — a `hunch`/`inferred` fact that other files cite as
     if firm.
   - ⚖️ **Contradiction** — two tagged facts that cannot both be true (flag, don't
     resolve — resolution is the owner's call).
3. **Report** — counts first, then the worst offenders (max 10), each as
   `file:line · finding · one-line fix`. One screenful.
4. **Fix only on request** — this skill reports by default. If the user says fix,
   apply the smallest edit: add a receipt (asking for source/tier), refresh a date
   the user confirms, or mark `review:` forward. Never invent a source.

## Output format

    ## Provenance lint — [date]
    🏷️ N untagged · ⏳ N stale · 🔻 N weak-under-load · ⚖️ N contradictions
    **Worst offenders**
    - path/file.md:12 — untagged fact ("…") — add [src: | | | ]
    …
    _Clean = one line, no theatre._

## Rules

- Never print raw sensitive values in findings — describe the line, don't quote
  identifiers (the gate hook enforces this mechanically; write as if it didn't).
- A fact without a receipt is treated as unverified, not deleted.
- Counts are honest: don't suppress findings to look green.
