#!/usr/bin/env python3
# ============================================================================
# Nambikkai flag — the Stop-hook chat sentinel (detection only).
#
# HONEST LIMIT: Claude Code has no primitive that rewrites displayed assistant
# text before it reaches the chat window, so the transcript cannot be scrubbed
# inline. This hook does the next best thing — it scans the assistant's just-
# finished turn for raw identifier patterns and LOGS a masked alert (never
# blocks, never loops). It converts a silent chat leak into a caught,
# reviewable one; your periodic review reads the alert log, and every real
# catch becomes a new corpus case (see conventions/doctrine.md, rule 2).
#
# Only high-confidence kinds are flagged (dob/brokerage overmatch on plain
# dates/codes and would cry wolf on ordinary replies). Masked snippets only.
# ============================================================================
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import sweep, redact, BLOCKING_KINDS  # noqa: E402

ALERT_LOG = os.environ.get(
    "NAMBIKKAI_LOG", os.path.join(os.getcwd(), ".nambikkai", "alerts.log")
)


def last_assistant_text(transcript_path):
    """Return the text of the final assistant message in the JSONL transcript."""
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except Exception:
        return ""
    for line in reversed(lines):
        try:
            evt = json.loads(line)
        except Exception:
            continue
        msg = evt.get("message") or {}
        if evt.get("type") == "assistant" or msg.get("role") == "assistant":
            content = msg.get("content", [])
            if isinstance(content, str):
                return content
            parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
            if parts:
                return "\n".join(parts)
    return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    text = last_assistant_text(data.get("transcript_path", ""))
    if not text:
        sys.exit(0)

    kinds = {f.kind for f in sweep(text)} & BLOCKING_KINDS
    if not kinds:
        sys.exit(0)

    sample = redact(text)[:160].replace("\n", " ")
    try:
        os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(ALERT_LOG, "a") as f:
            f.write(f"{stamp}\tCHAT-LEAK\tkinds={','.join(sorted(kinds))}\t{sample}\n")
    except Exception:
        pass
    sys.exit(0)  # never block a stop


if __name__ == "__main__":
    main()
