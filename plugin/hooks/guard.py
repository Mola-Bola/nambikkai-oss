#!/usr/bin/env python3
# ============================================================================
# Nambikkai gate — the PreToolUse perimeter (write/egress side).
#
# Runs the detection rules over a tool call's payload BEFORE it executes.
# - BLOCKS (exit 2) when a high-confidence identifier (NRIC/passport/phone/
#   account) would be written to a file, passed to a shell, or sent to an MCP
#   connector. Enforcement lives at the harness boundary — the app never has
#   to remember to call a library.
# - WARNS (logs, allows) on overmatch-prone kinds (dob/brokerage) so routine
#   dates and codes don't halt work (see corpus known_overmatch).
#
# Override: set NAMBIKKAI_ALLOW_RAW=1 to downgrade a block to a logged warning
# (explicit, auditable — e.g. deliberately writing a real value into your
# local secrets store).
#
# Honest limits: regex can't see free-text names or bare money amounts
# (corpus known_gap G-01..G-04). Those need a classifier pass — documented
# debt, not a hidden hole. Never echoes a raw value — stderr and the log
# carry masked snippets only.
# ============================================================================
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import sweep, redact, BLOCKING_KINDS, WARN_KINDS  # noqa: E402

ALERT_LOG = os.environ.get(
    "NAMBIKKAI_LOG", os.path.join(os.getcwd(), ".nambikkai", "alerts.log")
)
OVERRIDE = os.environ.get("NAMBIKKAI_ALLOW_RAW", "").lower() in {"1", "true", "yes"}


def collect_strings(obj):
    """Recursively pull every string value out of a tool_input structure."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from collect_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from collect_strings(v)


def log_alert(event, tool, kinds, masked_sample):
    try:
        os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(ALERT_LOG, "a") as f:
            # kinds + masked sample only — never the raw value (at-rest rule).
            f.write(f"{stamp}\t{event}\ttool={tool}\tkinds={','.join(sorted(kinds))}\t{masked_sample}\n")
    except Exception:
        pass  # a logging failure must never crash the tool call


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable input → don't block the session

    tool = data.get("tool_name", "?")
    tool_input = data.get("tool_input", {})
    text = "\n".join(collect_strings(tool_input))
    if not text:
        sys.exit(0)

    findings = sweep(text)
    if not findings:
        sys.exit(0)

    kinds = {f.kind for f in findings}
    blocking = kinds & BLOCKING_KINDS
    warning = kinds & WARN_KINDS
    masked = redact(text)
    # a short masked window around the first finding, for the log/message
    sample = masked[:160].replace("\n", " ")

    if blocking and not OVERRIDE:
        log_alert("BLOCK", tool, blocking, sample)
        msg = (
            f"⛔ Nambikkai gate BLOCKED this {tool} call: a raw "
            f"{'/'.join(sorted(blocking))} value would be written/sent. "
            f"Use a pointer to your secrets store instead, or re-run with "
            f"NAMBIKKAI_ALLOW_RAW=1 to override (logged). Masked view: {sample}"
        )
        print(msg, file=sys.stderr)
        sys.exit(2)  # exit 2 → the harness blocks the call and surfaces stderr

    # warn-only kinds, or an overridden block → log and allow
    event = "OVERRIDE" if (blocking and OVERRIDE) else "WARN"
    log_alert(event, tool, kinds, sample)
    if blocking and OVERRIDE:
        print(
            f"⚠️ Nambikkai gate OVERRIDDEN (NAMBIKKAI_ALLOW_RAW): "
            f"{'/'.join(sorted(blocking))} allowed into {tool}.",
            file=sys.stderr,
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
