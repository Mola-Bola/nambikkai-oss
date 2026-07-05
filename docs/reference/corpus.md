# Corpus schema

`corpus/cases.json` — the single source of truth every implementation binds to.

```json
{
  "_readme": "…",
  "must_mask":       [ { "id": "R-01", "kind": "nric", "input": "…S12~~34567D…", "note": "…" } ],
  "must_stay":       [ { "id": "S-01", "input": "…", "note": "…" } ],
  "known_overmatch": [ { "id": "O-01", "kind": "dob", "input": "…", "note": "…" } ],
  "known_gap":       [ { "id": "G-01", "input": "…", "note": "…" } ]
}
```

## Fields

- **`id`** — group prefix + sequence: `R-` (mask) · `S-` (stay) · `O-` (overmatch) ·
  `G-` (gap). Never reuse an id; never renumber.
- **`kind`** — the rule expected to fire (`must_mask`/`known_overmatch` only).
- **`input`** — the test string. Synthetic values ONLY. Any sensitive-shaped token
  carries the `~~` at-rest splitter; runners strip it via `arm()` before testing.
- **`note`** — one line: which incident class this case guards.

## Assertions per group

| Group | Runner asserts | If the assertion flips |
|---|---|---|
| `must_mask` | detected, correct kind | rules regressed — fix the rules |
| `must_stay` | zero findings | new false positive — fix the rules |
| `known_overmatch` | still detected | it stopped over-matching — **move the case to `must_stay`** and update the docs |
| `known_gap` | still missed | the rules grew — **promote the case to `must_mask`** |

The last two rows are the trick: documented limitations are *asserted*, so docs and
reality cannot drift apart silently.

## Invariants

1. All values synthetic — never a real identifier, even split.
2. The corpus file passes the gate it feeds (the `~~` convention guarantees it).
3. A rule change without corpus cases doesn't merge; a case without a `note` doesn't
   merge.
