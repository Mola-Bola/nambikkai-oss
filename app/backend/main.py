# ============================================================================
# Nambikkai web app — local API (M2: skeleton + capture).
#
# Binds 127.0.0.1 only (ADR 001: the journal core makes zero runtime network
# calls and accepts none from off-device). Wraps the existing engine rather
# than rewriting it: the redaction net is plugin/hooks/patterns.py, the same
# rule pack + golden corpus the gate runs.
#
# Privacy net is propose-never-act (stage-only autonomy): when an entry looks
# like it contains a high-confidence identifier (card/ID/passport/phone), the
# API answers needs_choice instead of saving; the user picks blur or keep.
# Their device, their words, their call (ADR 002: journal fields are
# local-free; roles/redaction are enforced at egress, which M2 doesn't have).
# ============================================================================
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patterns import sweep, redact, BLOCKING_KINDS  # noqa: E402
import ledger  # noqa: E402

app = FastAPI(title="Nambikkai", docs_url=None, redoc_url=None)

# Layman words for what the sweep found — kind names never reach a screen.
KIND_WORDS = {
    "nric": "an ID number",
    "passport": "a passport number",
    "phone": "a phone number",
    "account": "a card or account number",
}

GUIDED_FIELDS = ("feeling", "why", "cause", "helps")


class EntryIn(BaseModel):
    kind: Literal["guided", "free"]
    feeling: str = ""
    why: str = ""
    cause: str = ""
    helps: str = ""
    body: str = ""
    privacy_choice: Optional[Literal["keep", "blur"]] = None


def _chain_state():
    ok, count, broken = ledger.verify(ledger.ledger_path())
    return {"ok": ok, "count": count, "broken_at": broken}


@app.get("/api/health")
def health():
    return {"ok": True, "chain": _chain_state()}


@app.get("/api/entries")
def list_entries(limit: int = 100):
    records = ledger.read_all(ledger.ledger_path())
    return {"entries": list(reversed(records))[:limit], "chain": _chain_state()}


@app.post("/api/entries")
def create_entry(e: EntryIn):
    fields = GUIDED_FIELDS if e.kind == "guided" else ("body",)
    texts = {f: getattr(e, f).strip() for f in fields}
    if not any(texts.values()):
        raise HTTPException(400, "Nothing to keep yet. Write a little first.")

    combined = "\n".join(v for v in texts.values() if v)
    found_kinds = {f.kind for f in sweep(combined)} & BLOCKING_KINDS

    if found_kinds and e.privacy_choice is None:
        return {
            "saved": False,
            "needs_choice": True,
            "found": sorted(KIND_WORDS[k] for k in found_kinds),
        }

    blurred = bool(found_kinds and e.privacy_choice == "blur")
    if blurred:
        texts = {f: (redact(v) if v else v) for f, v in texts.items()}

    record = {
        "id": uuid.uuid4().hex,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": e.kind,
        **texts,
        "blurred": blurred,
        # Provenance (conventions/provenance.md): the user wrote it themselves.
        "src": "self",
        "tier": "stated",
        "ttl": "permanent",
    }
    rec = ledger.append(ledger.ledger_path(), record)
    return {"saved": True, "entry": rec, "chain": _chain_state()}
