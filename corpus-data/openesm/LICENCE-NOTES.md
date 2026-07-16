# openESM — licence notes
_Acquired 2026-07-15 (Cowork session). Dossier item 1._

## What is here
`metadata/` — the full openESM metadata catalogue, cloned from the official
[openesm-project/openesm-metadata](https://github.com/openesm-project/openesm-metadata) repo
(shallow clone, HEAD of 2026-07-15): `datasets.json` + 61 per-dataset metadata JSONs
(licence, Zenodo DOI, links to data/codebook/code, N, sampling scheme, features).

## Harmonised data — a curated 7 now pulled (`data/`), rest still on Zenodo
_2026-07-15 (Cowork, Opus follow-up): zenodo.org reachable this session, so a curated handful of
the harmonised time-series were pulled directly from the per-dataset Zenodo records (the `openesm`
pip package's own catalogue record 17182171 was 504-ing, so it was bypassed; per-record fetch with
retries, no scraping). Selection = spread across licence + design, favouring the rarest schema fit
(event-contingent = trigger/context) plus the fully-open CC0 sets and canonical dynamics datasets._

| dir under `data/` | author | yr | N (≈persons in ts) | design | licence |
|---|---|---|---|---|---|
| `0014_habets` | Habets | 2020 | 20 | dense daily, fully open | **CC0 1.0** |
| `0021_gundogdu` | Gundogdu | 2017 | 54 | 30-day series, fully open (+passive raw) | **CC0 1.0** |
| `0012_dejonckheere` | Dejonckheere | 2019 | 100 | canonical emotion-dynamics | CC-BY 4.0 |
| `0017_jang` | Jang | 2024 | 43 | longest per-person series (402 tp) | CC-BY 4.0 |
| `0001_fried` | Fried | 2021 | 79 | COVID life-event EMA | CC-BY 4.0 |
| `0064_wright` | Wright | 2017 | 245 | **event-contingent** (trigger/context, dyadic) | CC BY-NC 4.0 |
| `0046_ringwald` | Ringwald | 2024 | 526 | **event-contingent** + width (empathy/PA/NA) | CC BY-NC 4.0 |

Each dir holds the harmonised `*_ts.tsv` (timestamped per-person time-series), any `*_static*`
person-level file, the codebook, and `_zenodo_record.json` (record id, DOI, title, file list) for
provenance. Verified: person counts match the metadata; timestamp columns present.

**The other 54 datasets are NOT pulled** — pull any of them the same way:
```python
pip install openesm
import openesm
openesm.list_datasets()              # same catalogue as metadata/ here
openesm.get_dataset("<dataset_id>")  # downloads from Zenodo, licence surfaced
# (if the package's catalogue record 504s, fetch the per-record files directly:
#  GET https://zenodo.org/api/records/<recid-from-zenodo_doi> -> .files[].links.self)
```

### Licence flag on the pulled 7
Two are **CC0** (Habets, Gundogdu — unrestricted). Three are **CC-BY** (attribute only). Two are
**CC BY-NC** (Wright, Ringwald — non-commercial; flag before any commercial deployment). Full licence
text per record in each dir's `_zenodo_record.json`.

## Per-dataset licences (from the catalogue, 61 datasets)
- CC BY-NC 4.0 — 37 datasets
- CC-BY 4.0 — 19
- CC0 1.0 — 3
- GPL-3.0 — 1
- CC BY-NC-SA 4.0 — 1

**Check the individual dataset's `license` field before use** (`metadata/datasets/<id>_*/..._metadata.json`).
The NC-licensed majority constrains commercial use — flag before any commercial deployment of
anything derived from those datasets.

Four datasets have GitHub-hosted originals (0003, 0022, 0045, 0073 — see metadata) and could be
pulled from GitHub now if needed before the Zenodo fetch; originals are NOT in harmonised format.

## Ethics gate
✅ PASS — purpose-built open research data (dossier §A.1). Metadata itself: openly published catalogue.
