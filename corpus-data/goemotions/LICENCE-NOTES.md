# GoEmotions — licence notes + conditional-use rules
_Acquired 2026-07-15 (Cowork session). Dossier item 4a._

## What is here
`data/` from the official [google-research/google-research](https://github.com/google-research/google-research)
monorepo (`goemotions/` subtree, sparse shallow clone, 2026-07-15): the standard simplified splits
`train.tsv` (43,410) / `dev.tsv` (5,426) / `test.tsv` (5,427) = 54,263 labelled Reddit comments,
plus `emotions.txt` (27+neutral), Ekman/sentiment mappings, and the repo README + model card.

## What is NOT here
`data/full_dataset/` raw files (goemotions_1–3.csv, 211k rows with per-rater annotations) are on
storage.googleapis.com, unreachable from this sandbox. Fetch commands are in
`data/full_dataset/README.md`. The simplified splits are sufficient for classifier training.

## Licence
Apache 2.0 (google-research repo licence). Text content originates from Reddit users.

## Ethics gate — ⚠ CONDITIONAL PASS (binding, dossier §B.6)
- Use for **granular-label classifier training only**.
- **Never** use comments as "journal" exemplars.
- **Never** regurgitate/quote the underlying Reddit text in product output.
