# Corpus acquisition log — top-5 items 1–4
_2026-07-15, Cowork (Fable) session. Source: `research/2026-07-15-corpus-dossier.md` top-5 list.
Item 5 (NSDE/MIDUS) deliberately skipped — registration paperwork is the owner's.
Ethics gate binding throughout; per-source licence notes in each folder's `LICENCE-NOTES.md`.
Repo git locked (stale index.lock) — **files only, no commits made, no git commands run in this repo.**
No pipelines or shared registers touched; only `corpus-data/` created._

## Network constraints this session (shaped everything)
Sandbox proxy allowlist permitted **github.com (git-over-HTTPS), pypi.org** only of the needed hosts.
Blocked: zenodo.org, huggingface.co, gutenberg.org, unige.ch, dl.fbaipublicfiles.com,
storage.googleapis.com, osf.io, archive.org (also unreachable via web_fetch). No workarounds
attempted beyond official GitHub mirrors. Blocked pieces are logged per item with rerun commands.

## 1 · openESM — PARTIAL (metadata ✅, harmonised data ❌ blocked)
- Acquired: full official metadata catalogue (61 datasets, per-dataset licences/DOIs/links) from
  `openesm-project/openesm-metadata` → `openesm/metadata/`. Python package `openesm` verified
  installable; its Zenodo endpoint (record 17182171) was proxy-blocked.
- To finish at home: `pip install openesm` → `openesm.get_dataset(id)` per selection. Hours.
- Licences: 37× CC BY-NC 4.0, 19× CC-BY 4.0, 3× CC0, 1× GPL-3.0, 1× CC BY-NC-SA 4.0 — check per
  dataset at pull time.

## 2 · ISEAR — ✅ COMPLETE
- `isear/isear.csv` — **7,666 records** (matches ~7,665 expected), header ID/CITY/COUN/SUBJ/SEX/AGE…
- Source: JULIELab/ISEAR mirror (HEAD 93b631c); UNIGE original-provider PDF included.
- Open flag: confirm UNIGE terms (site unreachable this session); mirror states CC BY-NC-SA 3.0.

## 3 · Gutenberg diaries — ✅ COMPLETE (Pepys + 2)
- Pepys Complete (PG #4200, ~103k lines), Barbellion *Journal of a Disappointed Man* (PG #39585),
  Evelyn *Diary* Vol 1 (PG #41218) → `gutenberg-diaries/`. Source: GITenberg (PG's official GitHub
  org) since gutenberg.org was blocked. Public domain; PG headers still in the text files — strip
  before corpus use. Evelyn Vol 2 = PG #42081 if wanted.

## 4 · GoEmotions + EmpatheticDialogues — ✅ usable / mirror-sourced
- GoEmotions: official google-research repo subtree → `goemotions/data/` — standard splits
  54,263 comments (43,410/5,426/5,427) + 27-emotion taxonomy + mappings. Raw 211k `full_dataset`
  CSVs blocked (storage.googleapis.com); fetch commands preserved in `data/full_dataset/README.md`.
  **Conditional-use rules binding** (classifier training only; never exemplars; never regurgitate).
- EmpatheticDialogues: HF and fbaipublicfiles both blocked. Acquired the ~25k conversations
  (**24,856 conv ids, 132,103 utterance rows verified**) via the published EmpatheticIntents
  research mirror → `empathetic-dialogues/empatheticdialogues_unannotated/`.
  **Follow-up: re-fetch canonical tarball at home to verify/replace** (minutes).

## Verification run (2026-07-15)
ISEAR record count ✓ · ED conversation count ✓ · Pepys/Barbellion/Evelyn text files open clean ✓ ·
openESM `datasets.json` parses ✓ · 5/5 LICENCE-NOTES.md present ✓ · `.git/index.lock` untouched ✓.

## Open follow-ups (owner)
1. ~~Run openESM data pull at home (item 1 completion).~~ → **partially closed** (see 2026-07-15b
   below): 7 curated datasets pulled; 54 remain — pull on demand with the documented command.
2. ~~Re-fetch canonical EmpatheticDialogues tarball; verify against mirror.~~ → **closed** (2026-07-15b).
3. Confirm ISEAR terms on the UNIGE page.  _(still open — UNIGE not tested this session)_
4. Optional: GoEmotions raw full_dataset (3 CSVs) if per-rater annotations ever needed.
5. NSDE/MIDUS registration (item 5, skipped by instruction).

---

# 2026-07-15b — follow-up session (Cowork, Opus): two gaps closed
_Same instruction re-issued; prior session's data verified intact first (ISEAR 7,667 rows ✓,
GoEmotions splits 43,410/5,426/5,427 ✓, Pepys/Barbellion/Evelyn open ✓, openESM catalogue parses ✓).
This environment reached the hosts the earlier sandbox blocked (zenodo/HF/gutenberg/osf = 200), so the
two soft spots were completable. Owner chose "close both gaps, small openESM." Files only; no commits;
`.git/index.lock` still present and untouched; no pipelines/registers touched. Scratch venv + git-lfs
used off to the side (in the session scratchpad), not in the repo._

## Item 4b · EmpatheticDialogues — canonical copy acquired ✅
- Pulled official `facebook/empathetic_dialogues` Parquet via git+git-lfs (HF `refs/convert/parquet`,
  commit `d5b57ae`) → `empathetic-dialogues/canonical-hf-parquet/`. Verified **99,646 rows / 23,149
  conv ids** across train/val/test. Mirror retained; count delta explained (serialization, not loss)
  in that folder's `PROVENANCE.md`. Original ParlAI tarball binary-download was permission-denied this
  session; HF Parquet is derived from that same tarball, so the follow-up is closed.

## Item 1 · openESM — 7 curated harmonised datasets acquired ✅ (partial by design)
- `openesm/data/` — 7 of 61, ~15 MB total, chosen for licence + design spread and schema fit:
  Habets (CC0), Gundogdu (CC0), Dejonckheere (CC-BY), Jang (CC-BY), Fried (CC-BY), Wright (CC BY-NC,
  event-contingent), Ringwald (CC BY-NC, event-contingent). Each dir has the harmonised `*_ts.tsv`,
  static file where present, codebook, and `_zenodo_record.json` for provenance. Person counts match
  metadata; timestamps present. Pulled per-record from Zenodo (pip package's catalogue record 17182171
  was 504-ing; bypassed with direct per-record fetch + retries — no scraping). Remaining 54 pull the
  same way on demand (command in `openesm/LICENCE-NOTES.md`).

## Verification (2026-07-15b)
ED Parquet 3/3 splits real Apache Parquet, counts ✓ · openESM 7/7 dirs have real `*_ts.tsv` with
matching person counts ✓ · total `corpus-data/` now ~43 MB · no commits, no repo git commands run.
