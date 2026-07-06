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
# Part 3 — CLASSIFIER TIER: offline, proves the opt-in classifier fails OPEN
#   (enabled + no API key → the call still goes through). With a live
#   ANTHROPIC_API_KEY in the env, additionally runs the calibration: every
#   known_gap case tagged classifier:"expected" must come back flagged, and
#   no raw span may survive masking. Offline runs skip calibration and say so.
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


def classifier_tier():
    tmplog = os.path.join(HERE, ".test-alerts.log")

    # (a) fail-open, always: classifier ON but no key — a regex-clean write
    # (a known_gap payload) must still be ALLOWED, never wedged.
    with open(CASES) as f:
        gaps = [c for c in json.load(f)["known_gap"] if c.get("classifier") == "expected"]
    gap_payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/x.md", "content": arm(gaps[0]["input"])},
    }
    rc, _ = run_gate(gap_payload, {
        "NAMBIKKAI_LOG": tmplog, "NAMBIKKAI_CLASSIFIER": "1", "ANTHROPIC_API_KEY": "",
    })
    if rc != 0:
        fails.append(f"classifier: enabled+keyless must fail OPEN (rc 0), got rc {rc}")

    # (b) block-mode contract, offline + deterministic: stub classify() in
    # process and drive classifier_pass directly. Block mode refuses, warn
    # tier doesn't, the override downgrades — no API involved.
    import io
    import classifier as clf
    import guard
    orig_classify, orig_log, orig_override = clf.classify, guard.ALERT_LOG, guard.OVERRIDE
    orig_stderr = sys.stderr
    try:
        guard.ALERT_LOG = tmplog
        clf.classify = lambda text: [{"kind": "name", "text": "Zork Blen"}]
        sys.stderr = io.StringIO()  # swallow the announce lines

        os.environ["NAMBIKKAI_CLASSIFIER"] = "block"
        guard.OVERRIDE = False
        if guard.classifier_pass("Write", "payment from Zork Blen received") is not True:
            fails.append("classifier block-mode: finding must demand refusal (True)")
        if "Zork Blen" in sys.stderr.getvalue():
            fails.append("classifier block-mode: raw span echoed in the block message")

        guard.OVERRIDE = True
        if guard.classifier_pass("Write", "payment from Zork Blen received") is not False:
            fails.append("classifier block-mode: NAMBIKKAI_ALLOW_RAW must downgrade to allow")

        os.environ["NAMBIKKAI_CLASSIFIER"] = "warn"
        guard.OVERRIDE = False
        if guard.classifier_pass("Write", "payment from Zork Blen received") is not False:
            fails.append("classifier warn tier: finding must allow (False)")

        clf.classify = lambda text: None  # API failure
        os.environ["NAMBIKKAI_CLASSIFIER"] = "block"
        if guard.classifier_pass("Write", "anything at all here") is not False:
            fails.append("classifier block-mode: API failure must fail OPEN even in block mode")
    finally:
        clf.classify, guard.ALERT_LOG, guard.OVERRIDE = orig_classify, orig_log, orig_override
        sys.stderr = orig_stderr
        os.environ.pop("NAMBIKKAI_CLASSIFIER", None)

    # (c) live calibration, only with a key: every expected case must flag.
    if os.environ.get("ANTHROPIC_API_KEY", "").strip():
        import classifier
        os.environ["NAMBIKKAI_CLASSIFIER"] = "1"
        for c in gaps:
            armed = arm(c["input"])
            found = classifier.classify(armed)
            if found is None:
                fails.append(f"classifier live {c['id']}: API call failed")
            elif not found:
                fails.append(f"classifier live {c['id']}: expected a flag, got none")
            else:
                masked = classifier.mask_findings(armed, found)
                for f_ in found:
                    if len(f_["text"]) > 3 and f_["text"] in masked:
                        fails.append(f"classifier live {c['id']}: raw span survived masking")
        print(f"classifier calibration: {len(gaps)} expected cases run live")
    else:
        print("classifier calibration: SKIPPED (no ANTHROPIC_API_KEY) — fail-open asserted only")

    if os.path.exists(tmplog):
        os.remove(tmplog)


corpus()
gate()
classifier_tier()

if fails:
    print(f"FAIL ({len(fails)})")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("nambikkai self-test: all green (corpus + gate)")
