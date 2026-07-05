# Receipts

**Every durable fact carries provenance.** Not as metadata in a database — as a visible
tag at the end of the line, in the markdown your agents actually read:

```
- Lease renews in September.  [src: self | 2026-03 | firm | review:2026-08]
- Landlord likely selling next year.  [src: assistant | 2026-05 | hunch | 3mo]
```

Four fields: **source** (document, `self`, or `assistant`), **date confirmed**,
**trust tier** (`firm` / `stated` / `inferred` / `hunch`), and **TTL** (when to
re-check).

## Why receipts beat memory

An agent memory without provenance is a rumor mill: everything it ever heard, at equal
weight, forever. Receipts give the system three abilities rumor mills lack:

1. **Calibrated trust.** A `hunch` may color a suggestion; only `firm`/`stated` facts
   should drive actions with side effects. The tier is *in the context window* when
   the agent reads the fact — the model sees how much to trust each line.
2. **Honest staleness.** Facts expire. A lapsed TTL demotes a fact to unverified until
   re-confirmed — so your agent stops confidently citing last year's salary.
3. **Auditability.** "Why did you think that?" has a mechanical answer: follow the tag.

## The lint

The `provenance-lint` skill sweeps a knowledge base and reports: untagged facts, lapsed
TTLs, weak-tier facts being cited as firm, and contradictions. Counts first, worst
offenders second, one screenful. It reports by default and fixes only on request —
and it never invents a source.

## Rules that keep it honest

- **Supersede, don't stack** — when a fact changes, update the line; history lives in
  version control.
- **Corrections keep both dates** — so "what did the system believe in March?" stays
  answerable.
- **Sensitive values are pointers** — the receipt cites a document in your secrets
  store; the fact line carries no raw identifier. The [perimeter](perimeter.md)
  enforces this mechanically.

Full spec: [`conventions/provenance.md`](https://github.com/YOUR-GITHUB-USER/nambikkai/blob/main/conventions/provenance.md)
