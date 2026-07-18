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
from datetime import UTC, datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger  # noqa: E402
import security  # noqa: E402
from patterns import BLOCKING_KINDS, redact, sweep  # noqa: E402

# Every route depends on the loopback+token guard (see security.py).
app = FastAPI(
    title="Nambikkai",
    docs_url=None,
    redoc_url=None,
    dependencies=[Depends(security.guard)],
)
security.issue_token(ledger.data_dir())

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
    privacy_choice: Literal["keep", "blur"] | None = None


# Response models exist so the OpenAPI schema is real: the frontend's types are
# GENERATED from it (make api-types), which kills backend/frontend drift as a
# class rather than by review. FOUNDATIONS add-now item 6.
class ChainState(BaseModel):
    ok: bool
    count: int
    broken_at: int | None = None


class EntryOut(BaseModel):
    id: str
    at: str
    kind: Literal["guided", "free"]
    feeling: str = ""
    why: str = ""
    cause: str = ""
    helps: str = ""
    body: str = ""
    blurred: bool = False
    src: str = "self"
    tier: str = "stated"
    ttl: str = "permanent"


class HealthOut(BaseModel):
    ok: bool
    chain: ChainState


class EntriesOut(BaseModel):
    entries: list[EntryOut]
    chain: ChainState


class SaveOut(BaseModel):
    saved: bool
    # Present when the privacy net wants the user's decision before saving.
    needs_choice: bool = False
    found: list[str] = []
    # Present once the entry is actually in the journal.
    entry: EntryOut | None = None
    chain: ChainState | None = None


def _chain_state() -> ChainState:
    ok, count, broken = ledger.verify(ledger.ledger_path())
    return ChainState(ok=ok, count=count, broken_at=broken)


@app.get("/api/health", response_model=HealthOut)
def health():
    return HealthOut(ok=True, chain=_chain_state())


@app.get("/api/entries", response_model=EntriesOut)
def list_entries(limit: int = 100):
    records = ledger.read_all(ledger.ledger_path())
    entries = [EntryOut(**r) for r in list(reversed(records))[:limit]]
    return EntriesOut(entries=entries, chain=_chain_state())


@app.post("/api/entries", response_model=SaveOut)
def create_entry(e: EntryIn):
    fields = GUIDED_FIELDS if e.kind == "guided" else ("body",)
    texts = {f: getattr(e, f).strip() for f in fields}
    if not any(texts.values()):
        raise HTTPException(400, "Nothing to keep yet. Write a little first.")

    combined = "\n".join(v for v in texts.values() if v)
    found_kinds = {f.kind for f in sweep(combined)} & BLOCKING_KINDS

    if found_kinds and e.privacy_choice is None:
        return SaveOut(
            saved=False,
            needs_choice=True,
            found=sorted(KIND_WORDS[k] for k in found_kinds),
        )

    blurred = bool(found_kinds and e.privacy_choice == "blur")
    if blurred:
        texts = {f: (redact(v) if v else v) for f, v in texts.items()}

    record = {
        "id": uuid.uuid4().hex,
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "kind": e.kind,
        **texts,
        "blurred": blurred,
        # Provenance (conventions/provenance.md): the user wrote it themselves.
        "src": "self",
        "tier": "stated",
        "ttl": "permanent",
    }
    rec = ledger.append(ledger.ledger_path(), record)
    return SaveOut(saved=True, entry=EntryOut(**rec), chain=_chain_state())
