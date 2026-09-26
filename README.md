# Nambikkai

**A local-first journal that keeps receipts.**

Nambikkai is a journal app that runs entirely on your own machine. You write what you
feel, what set it off, who it involves, and what you believe about it. It stores those
beliefs the way an accountant keeps books: every entry is append-only and hash-chained,
every belief has a *valid-from* and *valid-to*, and nothing is silently rewritten. When
something you write sits close to something you wrote before, it can put the two side
by side, in your own words, so you can draw your own conclusion.

It is a journal, not therapy. There is no diagnosis or treatment language anywhere in
the code or the copy, and no machine ever tells the user what they feel.

---

## What is built

A working local web app: a FastAPI backend and a React + TypeScript frontend, both bound
to `127.0.0.1`, with no network calls at runtime.

| Area | What it does |
|---|---|
| **Capture** | Guided entries (feeling · why · who or what · what helps) or free writing, stored in a hash-chained ledger with provenance on every record. |
| **People & things** | Anyone or anything can be tracked by alias or name, with "what I thought then" next to "what I think now", and a thread of every entry that mentions them. |
| **Import** | Paste or drop old journals. Dates are parsed from common formats; names that recur become gentle "who is this?" questions the user can answer or dismiss. |
| **Truths** | Beliefs about people or situations. A truth is superseded, never edited, so "believed then / know now" is always recoverable. |
| **You** | Counts, returns after a quiet spell, and one chronological thread of the user's own words. No scores, no mood graph. |
| **Reflection** | Related past entries shown beside the current one, found by a local embedding model (all-MiniLM-L6-v2 via ONNX + sqlite-vec). Pull, never push. An optional, off-by-default layer can ask a short question a human wrote; it never states a conclusion. |
| **Demo data** | An invented demo set (and an optional public-domain diary, 531 entries over 13 years), clearly labelled and removable with one button. |
| **Export** | User-initiated export that swaps names for roles and passes one egress checkpoint. |

Underneath the app sits the **trust engine** the project started as:

- `plugin/`: a Claude Code plugin whose hooks block or warn when an agent is about to
  write personal identifiers (ID numbers, bank details, phone numbers, emails, IPs, and
  more) outside the places they belong. It also ships two skills (`incident-to-eval`,
  `provenance-lint`).
- `mcp/`: an MCP server exposing the same gate as tools (`check`, `redact`, `tag_fact`,
  `lint`). Standard library only.
- `corpus/`: a golden corpus of synthetic cases that every implementation is tested
  against: what must be masked, what must be left alone, known false positives, and
  known misses published as debt rather than hidden.
- `conventions/`: the provenance receipt format, the trust doctrine, and the
  "stage-only autonomy" rule (agents propose, people decide).

## Run it

Requirements: macOS or Linux, Python 3.11+ (3.13 preferred), Node 20+, `make`.

```bash
make dev          # creates .venv, installs deps, starts backend + frontend
                  # then open http://127.0.0.1:5173
```

Optional, one-time steps:

```bash
make model        # fetch the local embedding model (checksummed; the only network step)
make index        # rebuild the reflection index from the ledger (always safe)
make demo-diary   # build the public-domain diary demo set (needs corpus-data, see below)
```

Without `make model` the app still works, using word-overlap matching, and the UI says
so ("shared words only").

To try it quickly: open **Settings → Load demo data**, turn on "Let it ask me a gentle
question", then open **Journal**.

## Test it

```bash
make test         # 7 suites across two Python interpreters
make lint         # ruff
```

The suites cover the redaction gate against the golden corpus, the MCP server against
the same corpus, the capture API and hash chain, frozen engine test vectors, an end-to-end
user journey (capture, import, threads, truths, egress, demo wipe), the reflection
relevance floors, and the diary converter.

Two interpreters on purpose: `plugin/hooks/*` run as Claude Code hooks under the system
`python3` (3.9 on the dev machine), so their suites run there to prove compatibility,
while the app runs in a 3.13 virtualenv. A lint auto-fix once rewrote the hooks to a
3.11-only API and silently broke the gate; the corpus suite caught it, and the split
keeps it caught.

CI (GitHub Actions) runs the offline suites on every push. A nightly job calibrates the
optional LLM classifier tier, and only runs when an API key is configured.

## Design notes

- **Local forever, by architecture.** The journal core never makes a network call and
  binds localhost only, with a per-session token on API calls to block DNS-rebinding and
  cross-site requests. Anything social in the future would be a separate opt-in service
  that receives nothing from the ledger ([ADR 001](docs/adr/001-tiered-architecture.md)).
- **Append-only, hash-chained ledger as the source of truth.** One JSONL stream per
  record type (entries, people, truths, and more), each chained to the previous row.
  SQLite and the vector index are derived views and can be rebuilt at any time. The hash
  rule is frozen in [a spec with test vectors](docs/spec/engine-v1.md) so a future port
  can be checked mechanically.
- **People by role by default.** Identity handling is a written policy
  ([ADR 002](docs/adr/002-identity-policy.md)): alias-first, names allowed locally,
  roles enforced on anything that leaves the device.
- **Precision over recall in reflection.** A wrong pairing implies two unrelated parts
  of someone's life belong together; a missed one costs nothing. The match floor is set
  where nothing false gets through, which means roughly half of genuinely related pairs
  are missed. That trade-off is measured in `tests/fixtures/relevance.json` and written
  up in [ADR 003](docs/adr/003-reflection-surface.md) rather than hidden.
- **Honest test data.** Every fixture is invented. Sensitive-looking tokens in the
  corpus are split with `~~` at rest so the tracked files never contain a matchable
  identifier; the runners strip the splitter before testing.
- **Ethics gate on data.** Calibration uses only licensed research corpora or public
  domain text. The corpus data itself is gitignored (licence hygiene) and re-fetchable
  from pinned records in `corpus-data/ACQUISITION-LOG.md`.

## Known limitations

Found by running 13 years of a real public-domain diary (Barbellion, *Journal of a
Disappointed Man*) through the app:

- The name heuristic used by import is tuned for modern casual writing. On literary prose
  about half of the "who is this?" questions are noise; the demo caps them at 12.
- The month view only shows the current month, and the Journal view stops at 200 entries,
  so older imported entries need paging or a year jump.
- At high writing density almost every entry has a related hint, which weakens the
  signal. Whether that needs a stronger floor at scale is still open.

Import took 0.6 s, the one-time index build 7 s, and a related-entry lookup 13 ms on that
data set.

## Repository map

```
app/backend/     FastAPI app: ledger, store, importer, reflection index, demo data
app/frontend/    React + TypeScript + Vite UI
plugin/          Claude Code plugin: redaction gate hooks + skills
mcp/             trust-gate MCP server
corpus/          golden corpus (synthetic) that binds every implementation
conventions/     provenance receipts, trust doctrine, stage-only autonomy
docs/            ADRs, engine spec, concepts, recipes, operations
research/        grounding notes: the science, market, data and law
tests/           the seven suites, fixtures and frozen vectors
ops/             dev runner, backup, model fetch, diary converter
VISION.md        the product roadmap and first principles
PITCH.md         one-page framing
```

## About this copy

This is a public copy of a private working repository. The history has been scrubbed:
internal working notes (session handoffs, agent operating contracts, account-setup
runbooks, a runtime alert log) were removed, and references to the author's private
personal systems, local file paths and unpublished accounts were replaced with neutral
placeholders. `YOUR-GITHUB-USER` in install commands and docs links stands for wherever
this repository is published. "life-os" in VISION.md refers to the author's private
personal-operations system that this journal grew out of; it is not included here.

The name: *நம்பிக்கை (nambikkai)* is Tamil for trust, faith, hope. It is what a journal
has to earn from a person.

## License

[MIT](LICENSE)
