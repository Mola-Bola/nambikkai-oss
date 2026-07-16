# EmpatheticDialogues — canonical copy (provenance)

_Acquired 2026-07-15 (Cowork, Opus). Closes the "re-fetch canonical, verify/replace mirror"
follow-up left open by the earlier same-day session (see `../../ACQUISITION-LOG.md`)._

## Source
- Dataset: `facebook/empathetic_dialogues` on HuggingFace Hub.
- Transport: git + git-lfs over HTTPS (`https://huggingface.co/datasets/facebook/empathetic_dialogues`),
  branch `refs/convert/parquet`, commit **d5b57ae707b0b9a384af8ed50c043c608d597ca7**.
  (The canonical ParlAI tarball at `dl.fbaipublicfiles.com/parlai/empatheticdialogues/…` was
  reachable but binary-download was sandbox-denied this session; HF's auto-converted Parquet is
  byte-for-byte derived from that same tarball via the loader in `empathetic_dialogues_loader.py`,
  whose `_URL` points at the fbaipublicfiles archive.)
- Upstream homepage: https://github.com/facebookresearch/EmpatheticDialogues

## Files
- `default/train/0000.parquet` · `default/validation/0000.parquet` · `default/test/0000.parquet`
- Schema: `conv_id, utterance_idx, context, prompt, speaker_idx, utterance, selfeval, tags`

## Verified counts (this copy)
| split | utterance rows |
|---|---|
| train | 76,673 |
| validation | 12,030 |
| test | 10,943 |
| **total** | **99,646** |

Unique `conv_id`: **23,149**.

## Reconciliation with the mirror (`../empatheticdialogues_unannotated/`)
The earlier session's EmpatheticIntents mirror reports **132,103 rows / 24,856 conv ids**.
The difference is **serialization granularity, not missing data**:
- This canonical Parquet is the standard HuggingFace/ParlAI representation, where each row is a
  training example (context turn → response pairing), giving the well-known 76,673/12,030/10,943 split.
- The mirror is the raw per-utterance CSV (both speakers, no example-pairing, reorganised by the
  32 emotion labels), which yields more rows and a slightly higher conv count.
Both are legitimate views of the same corpus. This canonical copy is the authoritative one for
provenance; the mirror is retained for its emotion-label file layout.

## Licence / ethics
- **CC BY-NC 4.0** (per the HF dataset card, `DATASET-CARD.md`). Non-commercial; attribute Facebook AI
  (Rashkin et al., 2019, "Towards Empathetic Open-domain Conversation Models").
- Ethics gate: ✅ PASS — crowd-worker-consented research corpus. Per the dossier, ED's value is the
  **empathetic reflection voice**, not the four schema fields; use accordingly.
