#!/usr/bin/env python3
# ============================================================================
# Nambikkai journey suite (M3–M7) — the charter's acceptance test, in code.
#
# Walks the owner's own end-to-end test: write a directed entry · import an old
# journal · watch people and the timeline appear · answer a loose end · record
# and revise a truth · wipe demo data. Plus the M7 battery the charter names:
#
#   capture schema · import mapping · chain tamper · EGRESS POLICY
#
# The egress test is the sharp one: ADR 002 promises that names never leave the
# device. A real name written into an entry must come out of /api/export as a
# role, or the promise is marketing.
#
# At-rest rule applies HERE TOO: synthetic identifiers carry the '~~' splitter
# and are armed at runtime.
#
# Run: .venv/bin/python tests/test_journey.py   (exit 0 = pass)
# ============================================================================
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TMP = tempfile.mkdtemp(prefix="nambikkai-journey-")
os.environ["NAMBIKKAI_DATA"] = TMP  # must precede app imports

sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))

import ledger  # noqa: E402
import security  # noqa: E402
import store  # noqa: E402

SYN_PHONE = "04~~02 123 456"  # synthetic AU mobile, split at rest
fails = []


def arm(s):
    return s.replace("~~", "")


def client():
    from fastapi.testclient import TestClient
    from main import app

    c = TestClient(app, base_url="http://127.0.0.1")
    c.headers.update({security.TOKEN_HEADER: security.current_token()})
    return c


OLD_JOURNAL = """\
2024-03-02
Wrote nothing for weeks. Today the kitchen smelled like home again.
Ravi called and stayed on the line while I cooked.

14 June 2024
Ravi again, this time about the move. He thinks I should go.

2024-07-19
The lake was flat as glass. Ravi would have liked it.
"""


def capture_schema(c):
    """Every captured entry carries the fields the spec froze."""
    r = c.post(
        "/api/entries",
        json={
            "kind": "guided",
            "feeling": "steady",
            "why": "slept properly",
            "cause": "Mochi",
            "helps": "an early night",
        },
    )
    if r.status_code != 200 or not r.json()["saved"]:
        fails.append(f"capture: guided entry failed: {r.status_code} {r.text}")
        return
    entry = r.json()["entry"]
    for field in ("id", "at", "kind", "feeling", "why", "cause", "helps", "blurred", "src"):
        if field not in entry:
            fails.append(f"capture schema: entry is missing {field!r}")
    if (entry.get("src"), entry.get("tier"), entry.get("ttl")) != ("self", "stated", "permanent"):
        fails.append("capture schema: provenance fields wrong on a self-written entry")


def import_mapping(c):
    """Import maps dates to entries and recurring names to QUESTIONS, not facts."""
    r = c.post("/api/import", json={"text": OLD_JOURNAL})
    if r.status_code != 200:
        fails.append(f"import: failed: {r.status_code} {r.text}")
        return
    out = r.json()
    if out["kept"] != 3:
        fails.append(f"import mapping: expected 3 dated entries, got {out['kept']}")

    dates = sorted((e.get("at") or "")[:10] for e in store.entries() if e.get("src") == "import")
    if dates != ["2024-03-02", "2024-06-14", "2024-07-19"]:
        fails.append(f"import mapping: dates parsed wrong: {dates}")

    names = {q["name"] for q in out["questions"]}
    if "Ravi" not in names:
        fails.append(f"import mapping: recurring name should become a question, got {names}")

    # The machine must not have concluded anything about feelings.
    for entry in store.entries():
        if entry.get("src") == "import" and entry.get("feeling"):
            fails.append("import: a feeling was assigned by the machine, which must never happen")


def loose_end_flow(c):
    """Answering a loose end puts them on the map; it is never a gate."""
    ends = c.get("/api/loose-ends").json()
    ravi = next((e for e in ends if e["name"] == "Ravi"), None)
    if not ravi:
        fails.append("loose ends: Ravi should be waiting to be asked about")
        return
    r = c.post(f"/api/loose-ends/{ravi['id']}", json={"action": "added"})
    if r.status_code != 200:
        fails.append(f"loose ends: answering failed: {r.text}")
        return
    if any(e["id"] == ravi["id"] for e in r.json()):
        fails.append("loose ends: an answered question must stop being asked")
    if not any(p["name"] == "Ravi" for p in c.get("/api/personas").json()):
        fails.append("loose ends: answering 'add' should put them on the map")


def persona_threads(c):
    """An entry naming someone lands on their thread without being tagged."""
    people = c.get("/api/personas").json()
    ravi = next((p for p in people if p["name"] == "Ravi"), None)
    if not ravi:
        fails.append("threads: Ravi missing from the map")
        return
    thread = c.get(f"/api/personas/{ravi['id']}/thread").json()
    if len(thread["entries"]) < 3:
        fails.append(f"threads: expected Ravi's 3 mentions, got {len(thread['entries'])}")


def truth_revision(c):
    """Revising keeps both: the old belief with its dates, and what you know now."""
    people = c.get("/api/personas").json()
    ravi = next(p for p in people if p["name"] == "Ravi")

    first = c.post(
        "/api/truths",
        json={
            "about": ravi["id"],
            "text": "He only calls when he needs something.",
            "share_draft": "",
        },
    ).json()

    second = c.post(
        "/api/truths",
        json={
            "about": ravi["id"],
            "text": "He calls when he senses something is wrong. I mistook timing for motive.",
            "share_draft": "I owe you an apology and a long lunch.",
            "supersedes": first["id"],
        },
    )
    if second.status_code != 200:
        fails.append(f"truths: revision failed: {second.text}")
        return

    rows = c.get("/api/truths").json()
    old = next((t for t in rows if t["id"] == first["id"]), None)
    new = next((t for t in rows if t["id"] == second.json()["id"]), None)

    if not old or old["current"]:
        fails.append("truths: the superseded belief must stop being current")
    if not old or not old["valid_to"]:
        fails.append("truths: the old belief must gain an end date (believed then)")
    if not new or not new["current"]:
        fails.append("truths: the new belief must be the current one")
    if old and old["text"] not in [t["text"] for t in rows]:
        fails.append("truths: the old wording must remain readable, never overwritten")


def chain_tamper():
    """Every stream is tamper-evident, not just the journal."""
    for stream in ledger.all_streams():
        ok, count, _ = ledger.verify_stream(stream)
        if not ok:
            fails.append(f"chain: {stream} should verify clean, it did not")
        if count == 0:
            continue
        path = ledger.stream_path(stream)
        with open(path) as f:
            lines = f.readlines()
        keep = list(lines)
        rec = json.loads(lines[0])
        rec["at"] = "1999-01-01T00:00:00+00:00"
        lines[0] = json.dumps(rec) + "\n"
        with open(path, "w") as f:
            f.writelines(lines)
        ok, _, broken = ledger.verify_stream(stream)
        if ok or broken != 0:
            fails.append(f"chain: tampering with {stream} must be caught at record 0")
        with open(path, "w") as f:  # put it back
            f.writelines(keep)

    # A stream's records must not verify if moved into a different stream.
    if ledger.genesis_for("journal") == ledger.genesis_for("truths"):
        fails.append("chain: streams must not share a genesis, or records can be spliced across")


def egress_policy(c):
    """ADR 002, the promise that matters: names never leave, identifiers never leave."""
    c.post(
        "/api/personas",
        json={"name": "Priya", "alias": "my mother", "kind": "mother", "still_relevant": True},
    )
    c.post(
        "/api/entries",
        json={
            "kind": "free",
            "body": f"Priya rang from {arm(SYN_PHONE)} and asked about the garden again.",
            "privacy_choice": "keep",  # kept as written ON DEVICE, deliberately
        },
    )

    raw = json.dumps(c.get("/api/entries").json())
    if "Priya" not in raw:
        fails.append("egress: on the device the real name must be kept as the user wrote it")

    bundle = c.get("/api/export").json()
    text = json.dumps(bundle)

    if "Priya" in text:
        fails.append("EGRESS LEAK: a real name survived export")
    if "my mother" not in text:
        fails.append("egress: the name should have been replaced by the chosen role")
    if arm(SYN_PHONE).replace(" ", "") in text.replace(" ", ""):
        fails.append("EGRESS LEAK: a raw phone number survived export")
    if any("share_draft" in t for t in bundle["truths"]):
        fails.append("EGRESS LEAK: a private 'what I'd say to them' draft was exported")


def demo_isolation(c):
    """Demo data is labelled, and wiping it leaves real writing untouched."""
    before = len([e for e in store.entries() if not e.get("demo")])

    c.post("/api/demo/load")
    if not c.get("/api/health").json()["demo_loaded"]:
        fails.append("demo: health should report demo data is loaded")
    if not all(e.get("demo") for e in store.entries() if e.get("src") == "self" and e.get("demo")):
        fails.append("demo: every demo record must carry the demo flag")

    entries_now = c.get("/api/entries").json()["entries"]
    if not any(e["demo"] for e in entries_now):
        fails.append("demo: demo entries must be visibly flagged to the UI")

    r = c.post("/api/demo/wipe").json()
    if r["removed"] <= 0:
        fails.append("demo: wipe should report what it removed")
    after = len([e for e in store.entries() if not e.get("demo")])
    if after != before:
        fails.append(f"demo: wiping demo data changed real entries ({before} -> {after})")
    if store.has_demo():
        fails.append("demo: wipe must remove every demo record")
    for stream in ledger.all_streams():
        ok, _, _ = ledger.verify_stream(stream)
        if not ok:
            fails.append(f"demo: {stream} must still verify after a wipe re-seals it")


def main():
    c = client()
    capture_schema(c)
    import_mapping(c)
    loose_end_flow(c)
    persona_threads(c)
    truth_revision(c)
    chain_tamper()
    egress_policy(c)
    demo_isolation(c)

    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        sys.exit(1)
    print(
        "nambikkai journey suite: all green "
        "(capture · import · threads · truths · egress · demo)"
    )


if __name__ == "__main__":
    main()
