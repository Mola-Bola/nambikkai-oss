#!/usr/bin/env python3
# ============================================================================
# Nambikkai MCP server test — the same corpus binds the new surface.
#
# Drives mcp/server.py as a real stdio subprocess: MCP handshake, tools/list,
# then every corpus case through check/redact. The promise under test is the
# README's core one: any port/surface must pass corpus/cases.json or it does
# not ship. Plus the tool-level contracts: check never echoes a raw value,
# tag_fact refuses raw identifiers and stamps valid receipts, lint counts
# untagged/stale/malformed honestly.
#
# At-rest rule applies here too: synthetic tokens carry '~~', armed at runtime.
# Run: python3 tests/test_mcp.py   (exit 0 = pass)
# ============================================================================
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SERVER = os.path.join(ROOT, "mcp", "server.py")
CASES = os.path.join(ROOT, "corpus", "cases.json")
SYN_NRIC = "S12~~34567D"
fails = []


def arm(s):
    return s.replace("~~", "")


class Client:
    """Minimal line-delimited JSON-RPC client over the server's stdio."""

    def __init__(self):
        self.p = subprocess.Popen(
            [sys.executable, SERVER],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
        )
        self._id = 0

    def rpc(self, method, params=None):
        self._id += 1
        self.p.stdin.write(json.dumps(
            {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        ) + "\n")
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())

    def call(self, tool, args):
        resp = self.rpc("tools/call", {"name": tool, "arguments": args})
        out = json.loads(resp["result"]["content"][0]["text"])
        return out, resp["result"].get("isError", False)

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=5)


def run():
    with open(CASES) as f:
        data = json.load(f)
    c = Client()

    # handshake + surface
    init = c.rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}})
    if init["result"]["serverInfo"]["name"] != "nambikkai-trust-gate":
        fails.append("handshake: wrong serverInfo")
    tools = {t["name"] for t in c.rpc("tools/list")["result"]["tools"]}
    if tools != {"check", "redact", "tag_fact", "lint"}:
        fails.append(f"tools/list: expected 4 tools, got {sorted(tools)}")

    # THE corpus, through the server
    for case in data["must_mask"]:
        armed = arm(case["input"])
        out, _ = c.call("check", {"text": armed})
        kinds = {f["kind"] for f in out["findings"]}
        if case["kind"] not in kinds:
            fails.append(
                f"mcp must_mask {case['id']}: expected {case['kind']}, got {kinds or 'nothing'}"
            )
        raw = json.dumps(out)
        # the armed token must never travel back over the wire; every rule
        # kind carries digits, so the identifier is the longest digit-bearing
        # token (plain words like "passport" are legit in responses)
        tok = max((t for t in armed.split() if any(ch.isdigit() for ch in t)),
                  key=len, default="")
        if len(tok) >= 8 and tok in raw:
            fails.append(f"mcp must_mask {case['id']}: raw token echoed in check() response")
        red, _ = c.call("redact", {"text": armed})
        if len(tok) >= 8 and tok in red["text"]:
            fails.append(f"mcp must_mask {case['id']}: raw token survived redact()")

    for case in data["must_stay"]:
        out, _ = c.call("check", {"text": case["input"]})
        if not out["clean"]:
            hits = [f["kind"] for f in out["findings"]]
            fails.append(f"mcp must_stay {case['id']}: false positive {hits}")

    for case in data["known_overmatch"]:
        out, _ = c.call("check", {"text": arm(case["input"])})
        if out["clean"]:
            fails.append(f"mcp known_overmatch {case['id']}: no longer overmatches — corpus drift")

    for case in data["known_gap"]:
        out, _ = c.call("check", {"text": arm(case["input"])})
        if not out["clean"]:
            fails.append(f"mcp known_gap {case['id']}: now caught — promote in the corpus")

    # tag_fact: stamps clean facts, refuses hot ones
    out, err = c.call("tag_fact", {
        "fact": "Lease renews in September; agreement in the vault.",
        "src": "self", "tier": "stated", "ttl": "review:2027-01",
    })
    if err or "[src: self |" not in out.get("tagged", ""):
        fails.append(f"tag_fact: valid fact not stamped: {out}")
    out, err = c.call("tag_fact", {
        "fact": "FIN on record is " + arm(SYN_NRIC), "src": "self", "tier": "firm",
    })
    if not err or "pointer" not in out.get("error", ""):
        fails.append("tag_fact: raw NRIC fact must be refused with a pointer hint")
    if arm(SYN_NRIC) in json.dumps(out):
        fails.append("tag_fact: raw value echoed in the refusal")
    out, err = c.call("tag_fact", {"fact": "Some fact here today.", "src": "self", "tier": "vibes"})
    if not err:
        fails.append("tag_fact: invalid tier must be refused")

    # lint: untagged + stale + malformed each land in the right bucket
    doc = "\n".join([
        "# heading stays exempt",
        "The boiler was serviced last spring and passed inspection.",   # untagged
        "Lease renews in September.  [src: self | 2026-03 | firm | review:2026-04]",  # stale
        "Pension fund is XYZ; docs in vault.  [src: pack.pdf | 2026-01 | firm | evergreen]",  # fine
        "Broken receipt line here somehow.  [src: oops | nope]",        # malformed
    ])
    out, _ = c.call("lint", {"text": doc})
    if out["counts"] != {"untagged": 1, "stale": 1, "malformed": 1}:
        fails.append(f"lint: expected 1/1/1, got {out['counts']}")

    c.close()


run()
if fails:
    print(f"FAIL ({len(fails)})")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("nambikkai mcp self-test: all green (server vs corpus + tool contracts)")
