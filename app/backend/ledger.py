# ============================================================================
# Nambikkai journal ledger — append-only jsonl, hash-chained.
#
# Every record seals to the one before it: hash = sha256(prev_hash + canonical
# json of the record minus its own hash). Yesterday's entry can't be quietly
# rewritten — by the user at 2am, by a bug, or by anything else. verify() walks
# the whole file and reports the first broken link.
#
# The jsonl file is the source of truth (SQLite views come later, M3+). It
# lives under NAMBIKKAI_DATA (default <repo>/data), which is gitignored: user
# words never enter version control.
# ============================================================================
import hashlib
import json
import os

GENESIS = "nambikkai:journal:v1"
LEDGER_FILE = "journal.jsonl"


def data_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.environ.get("NAMBIKKAI_DATA", os.path.join(root, "data"))


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


def _last_hash(path: str) -> str:
    records = read_all(path)
    return records[-1]["hash"] if records else _sha(GENESIS)


def append(path: str, record: dict) -> dict:
    rec = dict(record)
    rec["prev"] = _last_hash(path)
    rec["hash"] = _record_hash(rec)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(_canon(rec) + "\n")
    return rec


def verify(path: str):
    """Walk the chain. Returns (ok, count, first_broken_index_or_None)."""
    records = read_all(path)
    prev = _sha(GENESIS)
    for i, rec in enumerate(records):
        if rec.get("prev") != prev or rec.get("hash") != _record_hash(rec):
            return False, len(records), i
        prev = rec["hash"]
    return True, len(records), None
