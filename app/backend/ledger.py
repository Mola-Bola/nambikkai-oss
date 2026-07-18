# ============================================================================
# Nambikkai ledger — append-only jsonl, hash-chained.
#
# Every record seals to the one before it: hash = sha256(prev_hash + canonical
# json of the record minus its own hash). Yesterday's entry can't be quietly
# rewritten — by the user at 2am, by a bug, or by anything else. verify() walks
# the whole file and reports the first broken link.
#
# STREAMS (M3+): entries, personas and truths each get their own chained file
# (journal.jsonl, personas.jsonl, truths.jsonl, loose-ends.jsonl). Each stream
# has its OWN genesis string, so a record can't be spliced from one stream into
# another and still verify. The hash rule itself is unchanged and still frozen
# by docs/spec/engine-v1.md — "journal" keeps the original genesis so every
# chain written before M3 still verifies untouched.
#
# The files are the source of truth. They live under NAMBIKKAI_DATA (default
# <repo>/data), which is gitignored: user words never enter version control.
# ============================================================================
import hashlib
import json
import os

GENESIS = "nambikkai:journal:v1"
LEDGER_FILE = "journal.jsonl"

JOURNAL = "journal"
PERSONAS = "personas"
TRUTHS = "truths"
LOOSE_ENDS = "loose-ends"


def data_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.environ.get("NAMBIKKAI_DATA", os.path.join(root, "data"))


def genesis_for(stream: str) -> str:
    """Per-stream genesis; 'journal' keeps the frozen v1 value."""
    return GENESIS if stream == JOURNAL else f"nambikkai:{stream}:v1"


def stream_path(stream: str) -> str:
    return os.path.join(data_dir(), f"{stream}.jsonl")


def ledger_path() -> str:
    return os.path.join(data_dir(), LEDGER_FILE)


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _record_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    return _sha(rec["prev"] + _canon(body))


def read_all(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _last_hash(path: str, genesis: str) -> str:
    records = read_all(path)
    return records[-1]["hash"] if records else _sha(genesis)


def append(path: str, record: dict, genesis: str = GENESIS) -> dict:
    rec = dict(record)
    rec["prev"] = _last_hash(path, genesis)
    rec["hash"] = _record_hash(rec)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(_canon(rec) + "\n")
    return rec


def verify(path: str, genesis: str = GENESIS):
    """Walk the chain. Returns (ok, count, first_broken_index_or_None)."""
    records = read_all(path)
    prev = _sha(genesis)
    for i, rec in enumerate(records):
        if rec.get("prev") != prev or rec.get("hash") != _record_hash(rec):
            return False, len(records), i
        prev = rec["hash"]
    return True, len(records), None


# --- stream-level helpers (M3+) ---------------------------------------------


def read_stream(stream: str) -> list:
    return read_all(stream_path(stream))


def append_to(stream: str, record: dict) -> dict:
    return append(stream_path(stream), record, genesis_for(stream))


def verify_stream(stream: str):
    return verify(stream_path(stream), genesis_for(stream))


def all_streams() -> list:
    return [JOURNAL, PERSONAS, TRUTHS, LOOSE_ENDS]


def rewrite_stream(stream: str, records: list) -> None:
    """Rebuild a stream from scratch, re-chaining as it goes.

    Only for operations that legitimately replace history wholesale: wiping demo
    data, and superseding a truth (which closes a record's validity window). It
    never edits in place — the file is rewritten and every record re-sealed.
    """
    path = stream_path(stream)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        prev = _sha(genesis_for(stream))
        for record in records:
            rec = {k: v for k, v in record.items() if k not in ("prev", "hash")}
            rec["prev"] = prev
            rec["hash"] = _record_hash(rec)
            f.write(_canon(rec) + "\n")
            prev = rec["hash"]
