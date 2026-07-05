#!/usr/bin/env python3
# ============================================================================
# Nambikkai self-test: corpus drift-guard + gate behaviour.
#
# Part 1 — CORPUS: runs the golden corpus (corpus/cases.json) against the
#   pattern engine. must_mask → caught; must_stay → clean; known_overmatch →
#   caught (asserted, so the docs stay honest); known_gap → missed (documented
#   debt — if a gap case starts passing, the corpus must be updated, not
#   silently celebrated). Any port of the rules binds to this same file.
# Part 2 — GATE: drives plugin/hooks/guard.py as a subprocess to prove
#   block / warn / override behaviour on realistic tool payloads.
#
# At-rest rule applies HERE TOO: no matchable identifier may appear literally
# in this file — synthetic tokens carry the '~~' splitter and are armed at
# runtime. (Nambikkai's own gate blocks this file's creation otherwise. Ask us
# how we know.)
#
# Run: python3 tests/test_guard.py   (exit 0 = pass)
# ============================================================================
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, "plugin", "hooks")
sys.path.insert(0, HOOKS)
from patterns import sweep, is_clean  # noqa: E402

CASES = os.path.join(ROOT, "corpus", "cases.json")
GUARD = os.path.join(HOOKS, "guard.py")
SYN_NRIC = "S12~~34567D"  # synthetic, split at rest; arm() makes it matchable
fails = []


def arm(s):
    """Strip the '~~' at-rest splitter so the identifier becomes matchable."""
    return s.replace("~~", "")


def corpus():
    with open(CASES) as f:
        data = json.load(f)

    for c in data["must_mask"]:
        found = {f.kind for f in sweep(arm(c["input"]))}
        if c["kind"] not in found:
            fails.append(f"must_mask {c['id']}: expected {c['kind']}, caught {found or 'nothing'}")

    for c in data["must_stay"]:
        if not is_clean(c["input"]):
            hits = {f.kind for f in sweep(c["input"])}
            fails.append(f"must_stay {c['id']}: false positive {hits} on clean text")

    for c in data["known_overmatch"]:
        if is_clean(arm(c["input"])):
            fails.append(f"known_overmatch {c['id']}: no longer overmatches — move it to must_stay")

    for c in data["known_gap"]:
        if not is_clean(arm(c["input"])):
            fails.append(f"known_gap {c['id']}: now caught — promote it to must_mask")


def run_gate(payload, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    p = subprocess.run(
        [sys.executable, GUARD],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return p.returncode, p.stderr


def gate():
    tmplog = os.path.join(HERE, ".test-alerts.log")
    env = {"NAMBIKKAI_LOG": tmplog}
    blocked_payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/x.md", "content": "FIN is " + arm(SYN_NRIC) + " on file"},
    }
    clean_payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/x.md", "content": "nothing sensitive here"},
    }

    rc, err = run_gate(blocked_payload, env)
    if rc != 2:
        fails.append(f"gate: expected BLOCK (rc 2) on raw NRIC write, got rc {rc}")
    if arm(SYN_NRIC) in err:
        fails.append("gate: raw value echoed in stderr — masking broken")

    rc, _ = run_gate(clean_payload, env)
    if rc != 0:
        fails.append(f"gate: clean write should pass, got rc {rc}")

    rc, err = run_gate(blocked_payload, {**env, "NAMBIKKAI_ALLOW_RAW": "1"})
    if rc != 0:
        fails.append(f"gate: override should allow (rc 0), got rc {rc}")
    if "OVERRIDDEN" not in err:
        fails.append("gate: override should announce itself on stderr")

    if os.path.exists(tmplog):
        os.remove(tmplog)


corpus()
gate()

if fails:
    print(f"FAIL ({len(fails)})")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("nambikkai self-test: all green (corpus + gate)")
