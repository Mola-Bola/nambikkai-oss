#!/usr/bin/env python3
# ============================================================================
# Nambikkai frozen-vector suite (FOUNDATIONS item 5, spec docs/spec/engine-v1.md).
#
# This is the contract a future engine port (Rust/TS for mobile) must satisfy.
# It deliberately hard-codes expected hashes: if this suite fails, the hash rule
# changed and every chain already written just became unverifiable. The fix is
# almost never "regenerate the vectors" — it's "put the rule back".
#
# Run: .venv/bin/python tests/test_vectors.py   (exit 0 = pass)
# ============================================================================
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))

import ledger  # noqa: E402
from patterns import BLOCKING_KINDS, redact, sweep  # noqa: E402

VECTORS = os.path.join(HERE, "vectors", "engine-v1.json")
fails = []


def arm(s):
    """Strip the at-rest splitter so the identifier becomes matchable."""
    return s.replace("~~", "")


def chain(data):
    if hashlib.sha256(data["genesis_source"].encode()).hexdigest() != data["genesis_prev"]:
        fails.append("genesis: sha256(genesis_source) does not match the frozen genesis_prev")
    if data["genesis_source"] != ledger.GENESIS:
        froze = data["genesis_source"]
        fails.append(f"genesis: engine uses {ledger.GENESIS!r}, spec froze {froze!r}")

    tmp = tempfile.mkdtemp(prefix="nambikkai-vectors-")
    path = os.path.join(tmp, "vectors.jsonl")
    for vec in data["chain"]:
        got = ledger.append(path, vec["input"])
        vid = vec["input"]["id"]
        if got["prev"] != vec["prev"]:
            fails.append(f"chain {vid}: prev {got['prev'][:16]} != {vec['prev'][:16]}")
        if got["hash"] != vec["hash"]:
            fails.append(f"chain {vid}: hash {got['hash'][:16]} != {vec['hash'][:16]}")

    ok, count, broken = ledger.verify(path)
    if not (ok and count == len(data["chain"])):
        fails.append(f"chain: rebuilt file must verify, got ok={ok} count={count} broken={broken}")


def redaction(data):
    for vec in data["redaction"]:
        text = arm(vec["input"])
        note = vec["note"]
        kinds = {f.kind for f in sweep(text)}
        expected = set(vec["expect_kinds"])
        if kinds != expected:
            fails.append(f"redaction {note!r}: kinds {kinds or 'none'} != {expected or 'none'}")

        is_blocking = bool(kinds & BLOCKING_KINDS)
        if is_blocking != vec["blocking"]:
            fails.append(f"redaction {note!r}: blocking={is_blocking}, expected {vec['blocking']}")

        masked = redact(text)
        if expected:
            # No raw digit-run from the identifier may survive masking.
            for token in text.split():
                digits = "".join(c for c in token if c.isdigit())
                if len(digits) >= 6 and token in masked:
                    fails.append(f"redaction {note!r}: raw token survived masking")
        elif masked != text:
            fails.append(f"redaction {note!r}: clean prose was altered")

        # Masking must be deterministic.
        if redact(text) != masked:
            fails.append(f"redaction {note!r}: not deterministic")


def main():
    with open(VECTORS, encoding="utf-8") as f:
        data = json.load(f)
    chain(data)
    redaction(data)
    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        print("\nA vector mismatch means the ENGINE changed, not the test.")
        print("See docs/spec/engine-v1.md before touching this file.")
        sys.exit(1)
    print("nambikkai vector suite: all green (frozen chain + redaction contract)")


if __name__ == "__main__":
    main()
