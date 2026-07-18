#!/usr/bin/env python3
# ============================================================================
# Nambikkai trust-gate MCP server (v0.2) — the same perimeter, for any client.
#
# A dependency-free stdio MCP server exposing the Nambikkai engine to anything
# that speaks MCP — not just Claude Code. It does NOT fork the rules: it
# imports plugin/hooks/patterns.py directly, and tests/test_mcp.py drives this
# server against the same corpus/cases.json the hooks bind to. A port that
# doesn't pass the golden file doesn't ship.
#
# Four tools:
#   check(text)     → findings as kinds + MASKED spans (never raw), clean flag
#   redact(text)    → the text with every finding partial-masked in place
#   tag_fact(...)   → a provenance receipt appended per conventions/provenance.md
#                     — and it gates its OWN input: a fact carrying a raw
#                     blocking identifier is refused, not stamped
#   lint(text)      → mechanical receipt lint: untagged fact-shaped lines,
#                     stale TTLs, malformed receipts (the provenance-lint
#                     skill remains the judgment layer; this is the fast net)
#
# Run:  python3 mcp/server.py   (stdio; register it in any MCP client config)
# ============================================================================
import json
import os
import re
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))
from patterns import BLOCKING_KINDS, RULES, redact, sweep  # noqa: E402

SERVER_INFO = {"name": "nambikkai-trust-gate", "version": "0.2.0"}
VALID_TIERS = {"firm", "stated", "inferred", "hunch"}
TTL_RE = re.compile(r"^(evergreen|permanent|expired|\d+mo|\d+d|review:\d{4}-\d{2}|—)$")
RECEIPT_RE = re.compile(r"\[src:\s*([^|\]]*)\|([^|\]]*)\|([^|\]]*)\|([^|\]]*)\]")

# ---------------------------------------------------------------- tools ----

def _mask_value(kind, value):
    """Mask a single finding's value with its own rule's mask fn."""
    for rule in RULES:
        if rule.kind == kind:
            try:
                return rule.mask(value)
            except Exception:
                break
    return "*" * len(value)


def tool_check(args):
    text = args.get("text", "")
    findings = sweep(text)
    return {
        "clean": not findings,
        "findings": [
            # kinds + masked spans only — check() can never become the leak
            {"kind": f.kind, "masked": _mask_value(f.kind, f.value), "index": f.index}
            for f in findings
        ],
        "blocking": sorted({f.kind for f in findings} & BLOCKING_KINDS),
    }


def tool_redact(args):
    return {"text": redact(args.get("text", ""))}


def tool_tag_fact(args):
    fact = args.get("fact", "").rstrip()
    src = args.get("src", "").strip()
    when = args.get("date", "").strip() or date.today().strftime("%Y-%m")
    tier = args.get("tier", "").strip()
    ttl = args.get("ttl", "").strip() or "—"

    if not fact or not src:
        return {"error": "fact and src are required"}
    if tier not in VALID_TIERS:
        return {"error": f"tier must be one of {sorted(VALID_TIERS)}"}
    if not TTL_RE.match(ttl):
        return {"error": "ttl must be evergreen | permanent | expired | <N>mo | <N>d | review:YYYY-MM | —"}
    if not re.match(r"^\d{4}-\d{2}(-\d{2})?$", when):
        return {"error": "date must be YYYY-MM (or YYYY-MM-DD when the day matters)"}

    # The receipt rule 5, enforced here too: a fact line carries no raw
    # identifier. Refuse to stamp one — same perimeter, different door.
    hot = {f.kind for f in sweep(fact)} & BLOCKING_KINDS
    if hot:
        return {
            "error": f"fact contains a raw {'/'.join(sorted(hot))} value — "
                     "replace it with a pointer to your secrets store, then tag"
        }
    return {"tagged": f"{fact}  [src: {src} | {when} | {tier} | {ttl}]"}


def _parse_month(s):
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _stale(when_s, ttl_s, today):
    """True if a receipt's TTL has lapsed. evergreen/permanent/expired never do."""
    ttl_s = ttl_s.strip()
    if ttl_s in {"evergreen", "permanent", "expired", "—"}:
        return False
    m = re.match(r"^review:(\d{4})-(\d{2})$", ttl_s)
    if m:
        return today >= date(int(m[1]), int(m[2]), 1).replace(
            month=int(m[2]) % 12 + 1, year=int(m[1]) + (int(m[2]) // 12)
        )  # stale once the review month has fully passed
    when = _parse_month(when_s)
    if not when:
        return False  # malformed date is its own finding, not a staleness call
    m = re.match(r"^(\d+)(mo|d)$", ttl_s)
    if m:
        n, unit = int(m[1]), m[2]
        days = n * 30 if unit == "mo" else n
        return (today - when).days > days
    return False


def _fact_shaped(line):
    """Heuristic for 'states a durable fact': substantive prose line, not
    structure. The skill layer judges; this is the mechanical net."""
    s = line.strip()
    return (
        len(s) >= 20
        and not s.startswith(("#", "```", "<!--", "|", ">", "_", "[", "!"))
        and not line.startswith("    ")
        and re.search(r"[a-zA-Z]{3}", s) is not None
    )


def tool_lint(args):
    text = args.get("text", "")
    today = date.today()
    untagged, stale, malformed = [], [], []
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = RECEIPT_RE.search(line)
        if m:
            src_f, when_f, tier_f, ttl_f = (g.strip() for g in m.groups())
            if not src_f or tier_f not in VALID_TIERS or not TTL_RE.match(ttl_f or "—"):
                malformed.append(n)
            elif _stale(when_f, ttl_f, today):
                stale.append(n)
        elif "[src:" in line:
            malformed.append(n)  # a receipt that doesn't parse is worse than none
        elif _fact_shaped(line):
            untagged.append(n)
    return {
        "counts": {"untagged": len(untagged), "stale": len(stale), "malformed": len(malformed)},
        "untagged_lines": untagged[:20],
        "stale_lines": stale[:20],
        "malformed_lines": malformed[:20],
        "note": "untagged is a heuristic net — line numbers only, content never echoed; "
                "the provenance-lint skill is the judgment layer",
    }


TOOLS = {
    "check": (tool_check, "Sweep text for identifier-shaped values. Returns kinds + masked spans (never raw) and whether any are blocking kinds.", {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "text to sweep"}},
        "required": ["text"],
    }),
    "redact": (tool_redact, "Return the text with every detected identifier partial-masked in place.", {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "text to redact"}},
        "required": ["text"],
    }),
    "tag_fact": (tool_tag_fact, "Append a Nambikkai provenance receipt [src | date | tier | ttl] to a fact line. Refuses facts carrying raw blocking identifiers — use a pointer.", {
        "type": "object",
        "properties": {
            "fact": {"type": "string", "description": "the fact line to tag"},
            "src": {"type": "string", "description": "source: filename, 'self', 'assistant', or a short label"},
            "date": {"type": "string", "description": "YYYY-MM (default: current month)"},
            "tier": {"type": "string", "enum": sorted(VALID_TIERS)},
            "ttl": {"type": "string", "description": "evergreen | permanent | <N>mo | <N>d | review:YYYY-MM | —"},
        },
        "required": ["fact", "src", "tier"],
    }),
    "lint": (tool_lint, "Mechanical receipt lint over markdown text: untagged fact-shaped lines, lapsed TTLs, malformed receipts. Line numbers only — content is never echoed.", {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "markdown text to lint"}},
        "required": ["text"],
    }),
}

# ------------------------------------------------------------ protocol ----

def reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except Exception:
            continue  # not ours to crash on
        method, id_ = msg.get("method"), msg.get("id")

        if method == "initialize":
            reply(id_, {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            })
        elif method == "notifications/initialized":
            pass
        elif method == "ping":
            reply(id_, {})
        elif method == "tools/list":
            reply(id_, {"tools": [
                {"name": name, "description": desc, "inputSchema": schema}
                for name, (_, desc, schema) in TOOLS.items()
            ]})
        elif method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name")
            if name not in TOOLS:
                reply(id_, error={"code": -32602, "message": f"unknown tool: {name}"})
                continue
            fn = TOOLS[name][0]
            try:
                out = fn(params.get("arguments", {}))
            except Exception as e:
                out = {"error": f"tool failed: {type(e).__name__}"}  # no payload echo
            reply(id_, {
                "content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False)}],
                "isError": "error" in out,
            })
        elif id_ is not None:
            reply(id_, error={"code": -32601, "message": f"method not found: {method}"})


if __name__ == "__main__":
    main()
