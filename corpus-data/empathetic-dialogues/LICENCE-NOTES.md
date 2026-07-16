# EmpatheticDialogues — licence notes
_Acquired 2026-07-15 (Cowork session). Dossier item 4b._

## What is here — canonical + mirror (both kept)
- `canonical-hf-parquet/` — **the canonical copy** (added 2026-07-15, Opus follow-up): the official
  `facebook/empathetic_dialogues` train/validation/test Parquet from HuggingFace (git+git-lfs,
  branch `refs/convert/parquet`, commit `d5b57ae`). 99,646 utterance rows / 23,149 conv ids, full
  schema (`conv_id, utterance_idx, context, prompt, speaker_idx, utterance, selfeval, tags`). Dataset
  card + loader + full provenance/reconciliation in that folder's `PROVENANCE.md`.
- `empatheticdialogues_unannotated/` — the earlier EmpatheticIntents mirror (Rashkin et al. 2019,
  Facebook AI) as 32 per-emotion CSVs (~132k utterance rows), from
  [anuradha1992/EmpatheticIntents](https://github.com/anuradha1992/EmpatheticIntents) (SIGDIAL 2020).
  README kept as `MIRROR-README-empatheticintents.md`. **Retained** for its emotion-label file layout.

The row/conv-count difference between the two is serialization granularity, not missing data — see
`canonical-hf-parquet/PROVENANCE.md`. The original ParlAI tarball
(`dl.fbaipublicfiles.com/parlai/…`) was reachable but binary-download was sandbox-denied this
session; the HF Parquet is derived from that same tarball, so the canonical follow-up is closed.

## Licence
CC BY-NC 4.0 (original dataset licence; permits redistribution with attribution, non-commercial).
Attribution: Rashkin, Smith, Li & Boureau (2019), *Towards Empathetic Open-domain Conversation
Models*, ACL.

## Ethics gate
✅ PASS — crowd-worker consented (dossier §B.7). Value is the empathetic-responding *voice*, not
schema fields. NC licence constrains commercial use — same flag as the NC openESM datasets.
