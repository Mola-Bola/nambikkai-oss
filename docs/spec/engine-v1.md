# Engine spec v1 — ledger chain & redaction

_FOUNDATIONS add-now item 5. Binding: any port of this engine (Rust/TS for mobile
packaging, per FOUNDATIONS) must reproduce **exactly** these outputs. The frozen
vectors in `tests/vectors/engine-v1.json` are the contract; `make test` asserts
the Python implementation against them on every run._

**Change discipline:** the hash rule is a promise to every entry already written.
Changing anything in §2 invalidates every existing chain. If it must change, it
becomes engine-v2 with a documented migration — never an edit to v1.

## 1 · Storage model

- Append-only files, one JSON object per line, UTF-8.
- The files are the source of truth. Any SQLite views are derived and rebuildable.
- Records are never edited or deleted in place. Correction is a new record.

**Streams (added M3; the hash rule in §2 is unchanged).** Each kind of record
gets its own chained file:

| Stream | File | Genesis string |
|---|---|---|
| entries | `journal.jsonl` | `nambikkai:journal:v1` |
| people & things | `personas.jsonl` | `nambikkai:personas:v1` |
| truths | `truths.jsonl` | `nambikkai:truths:v1` |
| loose ends | `loose-ends.jsonl` | `nambikkai:loose-ends:v1` |

Genesis is per-stream so a record cannot be lifted out of one file, dropped into
another and still verify. `journal` keeps the original genesis, so every chain
written before M3 verifies untouched — the frozen vectors still pass unchanged.

**Superseding, not editing.** A truth is never rewritten. Revising appends a new
record carrying `supersedes: <old id>`; the old record keeps its text and its
`valid_from` forever. A record's `valid_to` is therefore **computed** (it is the
successor's `valid_from`), never stored. Same for personas: an edit appends a
fresh record with the same `id`, and the reader takes the last one.

**Wholesale rewrite** (`rewrite_stream`) exists for exactly one job: removing
demo records. It rebuilds the file and re-seals every remaining record, so the
chain stays valid rather than being left with a hole.

## 2 · The hash chain

Each record carries `prev` and `hash`.

**Canonical JSON** — the exact byte sequence that gets hashed:

- keys sorted lexicographically (`sort_keys=True`)
- no whitespace: separators are `,` and `:`
- non-ASCII preserved, not escaped (`ensure_ascii=False`)

**Genesis.** The first record's `prev` is `sha256("nambikkai:journal:v1")`:

```
prev[0] = 9e3f0a4a5c2b8e6d... (see vectors file for the full value)
```

**Record hash.**

```
hash = sha256( prev || canonical_json(record_without_hash_field) )
```

`record_without_hash_field` is the record with `hash` removed but **`prev`
retained** — `prev` is part of the hashed body as well as the concatenated
prefix. (This is redundant by design; it makes a truncated-field attack fail two
ways instead of one.)

**Chain rule.** `record[n].prev == record[n-1].hash`, and `record[0].prev` is the
genesis value.

**Verification** walks records in file order and returns
`(ok, count, first_broken_index)`. The first index where either the `prev` link or
the recomputed `hash` disagrees is the break point. Everything before it is still
trustworthy; everything from it onward is not.

**Truncation is not tamper.** Removing records from the *end* leaves a valid
chain, because records only link backwards. Detecting truncation needs an external
witness (a backup's record count) — see docs/operations/backup-restore.md.

## 3 · Journal record shape

Written by the capture API (M2). Unknown fields must be preserved verbatim by any
reader, so later milestones can add fields without breaking old chains.

| Field | Meaning |
|---|---|
| `id` | uuid4 hex, unique per entry |
| `at` | UTC ISO-8601, seconds precision |
| `kind` | `guided` \| `free` |
| `feeling` `why` `cause` `helps` | guided fields (absent on free entries) |
| `body` | free-write text (absent on guided entries) |
| `blurred` | true if the user chose to mask identifiers before saving |
| `persona_ids` | people/things the user tagged on this entry |
| `demo` | true only for the synthetic demo set (M7); absent or false for real writing |
| `src` `tier` `ttl` | provenance per conventions/provenance.md (`self`/`stated`/`permanent`) |
| `prev` `hash` | chain fields, §2 |

`src` is `self` for entries the user typed and `import` for entries read out of
a file they brought in.

## 4 · Redaction rule pack

The detection rules live in `plugin/hooks/patterns.py` and are canonically tested
by `corpus/cases.json` — that corpus, not this document, is the authority on
*what* is detected. This spec fixes only the *contract*:

- `sweep(text)` detects without modifying; returns `(kind, value, index)` findings.
- `redact(text)` partial-masks in place; output length may differ from input.
- **Overlap resolution:** all rules match against the original text; earliest
  start wins; ties break by rule order in `RULES` (earlier = higher priority).
- `BLOCKING_KINDS = {nric, passport, phone, account, ssn, iban}` (high
  confidence — the gate refuses egress outright). `WARN_KINDS = {dob, brokerage,
  email, ip, geo}` (overmatch-prone or routine in technical payloads — logged,
  never blocking; email lives here because blocking it would halt ordinary dev
  work such as commit trailers). `PROMPT_KINDS = BLOCKING_KINDS ∪ {email}`
  drives the app's save-time blur/keep question, where asking is cheap; imports
  and the demo loader auto-blur on `BLOCKING_KINDS` only.
- Masks are deterministic: the same input always yields the same masked output.

## 5 · What a port must pass

1. Every vector in `tests/vectors/engine-v1.json` (chain + redaction).
2. The full golden corpus, `corpus/cases.json`, including `known_overmatch` and
   `known_gap` expectations.
