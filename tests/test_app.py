#!/usr/bin/env python3
# ============================================================================
# Nambikkai app self-test (M2): ledger chain + capture API.
#
# Part 1 — CHAIN: append/verify round-trip; a tampered middle record must
#   break verification at exactly that index (tamper-evidence is the product
#   promise, so it gets a test, not a comment).
# Part 2 — API: capture happy path (guided + free), empty rejection, and the
#   privacy net's propose-never-act flow — an entry carrying a high-confidence
#   identifier must come back needs_choice, then save blurred or as-written
#   per the user's explicit choice (ADR 002).
#
# At-rest rule applies HERE TOO: synthetic identifiers carry the '~~' splitter
# and are armed at runtime, same as test_guard.py.
#
# Run: .venv/bin/python tests/test_app.py   (exit 0 = pass; needs fastapi)
# ============================================================================
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TMP = tempfile.mkdtemp(prefix="nambikkai-test-")
os.environ["NAMBIKKAI_DATA"] = TMP  # must precede app imports

sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
import ledger  # noqa: E402

SYN_CARD = "4111 1111~~ 1111 1111"  # synthetic Visa test number, split at rest
fails = []


def arm(s):
    return s.replace("~~", "")


def chain():
    path = os.path.join(TMP, "chain-test.jsonl")
    for i in range(3):
        ledger.append(path, {"id": f"e{i}", "body": f"entry {i}"})
    ok, count, broken = ledger.verify(path)
    if not (ok and count == 3 and broken is None):
        fails.append(f"chain: clean 3-entry file should verify, got ok={ok} broken={broken}")

    # Tamper with the middle record's text; the chain must break at index 1.
    with open(path) as f:
        lines = f.readlines()
    rec = json.loads(lines[1])
    rec["body"] = "quietly rewritten at 2am"
    lines[1] = json.dumps(rec) + "\n"
    with open(path, "w") as f:
        f.writelines(lines)
    ok, count, broken = ledger.verify(path)
    if ok or broken != 1:
        fails.append(f"chain: tampered record must break at 1, got ok={ok} broken={broken}")


def api():
    import security
    from fastapi.testclient import TestClient
    from main import app

    # base_url pins a loopback Host header; the guard rejects anything else.
    c = TestClient(app, base_url="http://127.0.0.1")
    c.headers.update({security.TOKEN_HEADER: security.current_token()})

    r = c.post("/api/entries", json={"kind": "guided", "feeling": "homesick but lighter"})
    if not (r.status_code == 200 and r.json()["saved"]):
        fails.append(f"api: guided save failed: {r.status_code} {r.text}")

    r = c.post("/api/entries", json={"kind": "free", "body": "long day. wrote anyway."})
    if not (r.status_code == 200 and r.json()["saved"]):
        fails.append(f"api: free save failed: {r.status_code} {r.text}")

    r = c.post("/api/entries", json={"kind": "guided"})
    if r.status_code != 400:
        fails.append(f"api: empty entry must 400, got {r.status_code}")

    # Privacy net: identifier -> needs_choice, nothing saved yet.
    risky = {"kind": "free", "body": f"paid the deposit with card {arm(SYN_CARD)}"}
    r = c.post("/api/entries", json=risky)
    if not (r.status_code == 200 and r.json().get("needs_choice")):
        fails.append(f"api: identifier must trigger needs_choice, got {r.text}")

    # Choice: blur -> saved with the number masked.
    r = c.post("/api/entries", json={**risky, "privacy_choice": "blur"})
    body = r.json()["entry"]["body"] if r.status_code == 200 and r.json().get("saved") else ""
    if arm(SYN_CARD) in body or "****" not in body:
        fails.append(f"api: blur choice must mask the number, got: {body!r}")

    # Choice: keep -> saved as written (their device, their call).
    r = c.post("/api/entries", json={**risky, "privacy_choice": "keep"})
    if not (r.status_code == 200 and r.json().get("saved")):
        fails.append(f"api: keep choice must save, got {r.text}")

    # The whole session must verify as one unbroken chain.
    r = c.get("/api/entries")
    chain_state = r.json()["chain"]
    if not chain_state["ok"] or chain_state["count"] != 4:
        fails.append(f"api: expected unbroken chain of 4, got {chain_state}")


def guard():
    """The localhost guard: a drive-by page must not reach the journal."""
    import security
    from fastapi.testclient import TestClient
    from main import app

    c = TestClient(app, base_url="http://127.0.0.1")
    good = {security.TOKEN_HEADER: security.current_token()}

    r = c.get("/api/entries")  # no token at all
    if r.status_code != 401:
        fails.append(f"guard: tokenless request must 401, got {r.status_code}")

    r = c.get("/api/entries", headers={security.TOKEN_HEADER: "guessed-token"})
    if r.status_code != 401:
        fails.append(f"guard: wrong token must 401, got {r.status_code}")

    # DNS-rebinding shape: right token, but Host is the attacker's domain.
    r = c.get("/api/entries", headers={**good, "host": "attacker.example"})
    if r.status_code != 403:
        fails.append(f"guard: non-loopback Host must 403, got {r.status_code}")

    r = c.get("/api/entries", headers=good)
    if r.status_code != 200:
        fails.append(f"guard: the app's own request must pass, got {r.status_code}")


def main():
    chain()
    api()
    guard()
    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        sys.exit(1)
    print("nambikkai app self-test: all green (chain + capture API)")


if __name__ == "__main__":
    main()
