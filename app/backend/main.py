# ============================================================================
# Nambikkai web app — local API (M2 capture → M7 demo/export).
#
# Binds 127.0.0.1 only and requires a per-session token (ADR 001 + security.py):
# the journal core makes zero runtime network calls and accepts none from
# off-device.
#
# Wraps the existing engine rather than rewriting it: the redaction net is
# plugin/hooks/patterns.py, the same rule pack and golden corpus the gate runs.
#
# Two doctrines are enforced in code here, not just in copy:
#   · Propose, never act. An entry that looks like it holds an identifier comes
#     back as needs_choice; the user picks blur or keep. Their device, their
#     words, their call (ADR 002: journal fields are local-free).
#   · Names on the device, roles at the door. /api/export is the single egress
#     choke-point, and it is the only place ADR 002's role-swap applies.
# ============================================================================
import os
import sys
from datetime import UTC, datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import demo as demo_data  # noqa: E402
import embed  # noqa: E402
import importer  # noqa: E402
import index as relevance  # noqa: E402
import ledger  # noqa: E402
import security  # noqa: E402
import store  # noqa: E402
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


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


# --- request models ---------------------------------------------------------


class EntryIn(BaseModel):
    kind: Literal["guided", "free"]
    feeling: str = ""
    why: str = ""
    cause: str = ""
    helps: str = ""
    body: str = ""
    persona_ids: list[str] = []
    privacy_choice: Literal["keep", "blur"] | None = None


class PersonaIn(BaseModel):
    name: str
    alias: str = ""
    kind: str = ""
    thought_then: str = ""
    think_now: str = ""
    still_relevant: bool = True


class TruthIn(BaseModel):
    about: str = "self"  # a persona id, or "self"
    text: str
    share_draft: str = ""
    supersedes: str | None = None


class ImportIn(BaseModel):
    text: str


class LooseEndIn(BaseModel):
    action: Literal["added", "dismissed"]


# --- response models --------------------------------------------------------
# These exist so the OpenAPI schema is real: the frontend's types are GENERATED
# from it (make api-types), which kills backend/frontend drift as a class.


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
    persona_ids: list[str] = []
    demo: bool = False
    src: str = "self"
    tier: str = "stated"
    ttl: str = "permanent"


class PersonaOut(BaseModel):
    id: str
    at: str = ""
    name: str
    alias: str = ""
    kind: str = ""
    thought_then: str = ""
    think_now: str = ""
    still_relevant: bool = True
    demo: bool = False
    mentions: int = 0
    last_line: str = ""


class TruthOut(BaseModel):
    id: str
    about: str = "self"
    about_name: str = "Yourself"
    text: str
    share_draft: str = ""
    valid_from: str = ""
    valid_to: str | None = None
    current: bool = True
    supersedes: str | None = None
    demo: bool = False


class LooseEndOut(BaseModel):
    id: str
    name: str
    mentions: int = 0
    at: str = ""
    source: str = ""
    demo: bool = False


class TimelineRow(BaseModel):
    at: str
    kind: str
    id: str
    headline: str = ""
    feeling: str = ""
    demo: bool = False


class OverviewOut(BaseModel):
    entries_kept: int
    people_mapped: int
    truths_revisited: int
    returns_after_quiet: int
    days_written: int


class HealthOut(BaseModel):
    ok: bool
    chain: ChainState
    demo_loaded: bool = False


class EntriesOut(BaseModel):
    entries: list[EntryOut]
    chain: ChainState


class SaveOut(BaseModel):
    saved: bool
    needs_choice: bool = False
    found: list[str] = []
    entry: EntryOut | None = None
    chain: ChainState | None = None


class ThreadOut(BaseModel):
    persona: PersonaOut
    entries: list[EntryOut]
    truths: list[TruthOut]


class YouOut(BaseModel):
    overview: OverviewOut
    timeline: list[TimelineRow]
    written_days: list[str]
    truth_days: list[str]
    year_ago: list[EntryOut]


class ImportOut(BaseModel):
    kept: int
    undated: int
    questions: list[LooseEndOut]


class WipeOut(BaseModel):
    removed: int


class RelatedEntry(BaseModel):
    """A past entry offered beside the one in front of you.

    `entry` is the user's own record, verbatim from the ledger. There is no
    field here for a summary, a theme, a label or a reason, and there must
    never be one: ADR 003 puts the user's words on screen or nothing.
    """

    entry: EntryOut
    score: float


class RelatedOut(BaseModel):
    related: list[RelatedEntry] = []
    # "shared words only" tells the UI to say matching is basic until the local
    # model is installed. It is never dressed up as anything cleverer.
    matching: Literal["meaning", "shared words only"] = "shared words only"


class ReflectionSettings(BaseModel):
    """Everything the reflection loop is allowed to do, and its default answer.

    questions_on is FALSE by default and only the user may change it (ADR 003).
    """

    questions_on: bool = False
    matching: Literal["meaning", "shared words only"] = "shared words only"
    model_present: bool = False
    indexed: int = 0


# --- helpers ----------------------------------------------------------------


def _index_quietly(entry: dict) -> None:
    """Index a new entry, and never let that failure reach the user.

    The index is a derived view (ADR 003). Losing it costs a related-entries
    link until the next `make index`; it must never cost someone their writing,
    so nothing this raises is allowed to escape a successful save.
    """
    try:
        relevance.add(entry)
    except Exception as exc:  # noqa: BLE001 - deliberately swallowing everything
        print(f"index: skipped an entry ({exc})", file=sys.stderr)


def _resync_index() -> None:
    """Rebuild the index after something rewrote the ledger wholesale.

    Loading or wiping demo data adds and removes entries in bulk, so an
    incremental pass would leave the index pointing at records that no longer
    exist. A full rebuild from the ledger is the cheap, always-correct answer,
    and it is exactly what the index is designed to survive.
    """
    try:
        relevance.backfill(rebuild=True)
    except Exception as exc:  # noqa: BLE001 - a derived view must never break a request
        print(f"index: rebuild skipped ({exc})", file=sys.stderr)


def _chain_state() -> ChainState:
    ok, count, broken = ledger.verify_stream(ledger.JOURNAL)
    return ChainState(ok=ok, count=count, broken_at=broken)


def _entry_out(row: dict) -> EntryOut:
    return EntryOut(**{k: v for k, v in row.items() if k in EntryOut.model_fields})


def _persona_out(row: dict, with_thread: bool = False) -> PersonaOut:
    data = {k: v for k, v in row.items() if k in PersonaOut.model_fields}
    out = PersonaOut(**data)
    if with_thread:
        thread = store.persona_thread(row["id"])
        out.mentions = len(thread)
        if thread:
            first = store.entry_text(thread[0]).splitlines()
            out.last_line = (first[0] if first else "").strip()[:140]
    return out


def _persona_names() -> dict:
    return {p["id"]: p.get("name", "someone") for p in store.personas()}


def _truth_out(row: dict, names: dict | None = None) -> TruthOut:
    names = names if names is not None else _persona_names()
    data = {k: v for k, v in row.items() if k in TruthOut.model_fields}
    about = row.get("about", "self")
    return TruthOut(
        **data,
        about_name="Yourself" if about == "self" else names.get(about, "someone"),
    )


# --- capture (M2) -----------------------------------------------------------


@app.get("/api/health", response_model=HealthOut)
def health():
    return HealthOut(ok=True, chain=_chain_state(), demo_loaded=store.has_demo())


@app.get("/api/entries", response_model=EntriesOut)
def list_entries(limit: int = 200):
    rows = list(reversed(store.entries()))[:limit]
    return EntriesOut(entries=[_entry_out(r) for r in rows], chain=_chain_state())


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

    blank = {"feeling": "", "why": "", "cause": "", "helps": "", "body": ""}
    record = {
        "id": store.new_id(),
        "at": _now(),
        "kind": e.kind,
        **blank,
        **texts,
        "blurred": blurred,
        "persona_ids": e.persona_ids,
        # Provenance (conventions/provenance.md): the user wrote it themselves.
        "src": "self",
        "tier": "stated",
        "ttl": "permanent",
    }
    rec = store.add_entry(record)
    _index_quietly(rec)
    return SaveOut(saved=True, entry=_entry_out(rec), chain=_chain_state())


# --- people & things (M3) ---------------------------------------------------


@app.get("/api/personas", response_model=list[PersonaOut])
def list_personas():
    return [_persona_out(p, with_thread=True) for p in store.personas()]


@app.post("/api/personas", response_model=PersonaOut)
def create_persona(p: PersonaIn):
    if not p.name.strip():
        raise HTTPException(400, "Give them a name or a nickname first.")
    record = store.add_persona(
        {"id": store.new_id(), "at": _now(), "demo": False, **p.model_dump()}
    )
    return _persona_out(record)


@app.put("/api/personas/{persona_id}", response_model=PersonaOut)
def update_persona(persona_id: str, p: PersonaIn):
    existing = store.persona(persona_id)
    if not existing:
        raise HTTPException(404, "That one isn't on your map.")
    record = store.add_persona(
        {
            "id": persona_id,
            "at": _now(),
            "demo": existing.get("demo", False),
            **p.model_dump(),
        }
    )
    return _persona_out(record, with_thread=True)


@app.get("/api/personas/{persona_id}/thread", response_model=ThreadOut)
def read_thread(persona_id: str):
    p = store.persona(persona_id)
    if not p:
        raise HTTPException(404, "That one isn't on your map.")
    names = _persona_names()
    return ThreadOut(
        persona=_persona_out(p, with_thread=True),
        entries=[_entry_out(e) for e in store.persona_thread(persona_id)],
        truths=[_truth_out(t, names) for t in store.truths_about(persona_id)],
    )


# --- truths (M5) ------------------------------------------------------------


@app.get("/api/truths", response_model=list[TruthOut])
def list_truths():
    names = _persona_names()
    rows = sorted(store.truths(), key=lambda t: t.get("valid_from", ""), reverse=True)
    return [_truth_out(t, names) for t in rows]


@app.post("/api/truths", response_model=TruthOut)
def create_truth(t: TruthIn):
    if not t.text.strip():
        raise HTTPException(400, "Write the belief first, however rough.")
    if t.supersedes and not any(x["id"] == t.supersedes for x in store.truths()):
        raise HTTPException(404, "That earlier belief isn't in your ledger.")
    record = store.add_truth(
        {
            "id": store.new_id(),
            "about": t.about,
            "text": t.text.strip(),
            "share_draft": t.share_draft.strip(),
            "valid_from": _now(),
            "supersedes": t.supersedes,
            "demo": False,
        }
    )
    # Re-read so the computed validity window comes back with it.
    fresh = next(x for x in store.truths() if x["id"] == record["id"])
    return _truth_out(fresh)


# --- loose ends (M4) --------------------------------------------------------


@app.get("/api/loose-ends", response_model=list[LooseEndOut])
def list_loose_ends():
    return [LooseEndOut(**{k: v for k, v in r.items() if k in LooseEndOut.model_fields})
            for r in store.loose_ends()]


@app.post("/api/loose-ends/{loose_end_id}", response_model=list[LooseEndOut])
def answer_loose_end(loose_end_id: str, body: LooseEndIn):
    match = next((r for r in store.loose_ends() if r["id"] == loose_end_id), None)
    if not match:
        raise HTTPException(404, "That question has already been answered.")
    if body.action == "added":
        store.add_persona(
            {
                "id": store.new_id(),
                "at": _now(),
                "demo": match.get("demo", False),
                "name": match["name"],
                "alias": "",
                "kind": "from something you wrote",
                "thought_then": "",
                "think_now": "",
                "still_relevant": True,
            }
        )
    store.resolve_loose_end(loose_end_id, body.action)
    return list_loose_ends()


# --- bring in (M4) ----------------------------------------------------------


@app.post("/api/import", response_model=ImportOut)
def import_text(payload: ImportIn):
    if not payload.text.strip():
        raise HTTPException(400, "Nothing to bring in yet. Paste or drop something first.")

    result = importer.digest(payload.text)
    if not result["entries"]:
        raise HTTPException(400, "Couldn't find any writing in that.")

    for block in result["entries"]:
        body = block["body"]
        # The privacy net still applies to imported words, but importing must
        # never stall on a question: identifiers are masked, and the entry says so.
        found = {f.kind for f in sweep(body)} & BLOCKING_KINDS
        imported = store.add_entry(
            {
                "id": store.new_id(),
                "at": block["at"] or _now(),
                "kind": "free",
                "feeling": "",
                "why": "",
                "cause": "",
                "helps": "",
                "body": redact(body) if found else body,
                "blurred": bool(found),
                "persona_ids": [],
                "demo": False,
                "src": "import",
                "tier": "stated",
                "ttl": "permanent",
            }
        )
        # Imported years are exactly what the juxtaposition surface is for.
        _index_quietly(imported)

    known = {p.get("name", "").lower() for p in store.personas()}
    for candidate in result["candidates"]:
        name = candidate["name"]
        if name.lower() in known or store.loose_end_exists(name):
            continue
        store.add_loose_end(
            {
                "id": store.new_id(),
                "name": name,
                "mentions": candidate["mentions"],
                "at": _now(),
                "source": "something you brought in",
                "demo": False,
            }
        )

    return ImportOut(
        kept=len(result["entries"]),
        undated=result["undated"],
        questions=list_loose_ends(),
    )


# --- you (M6) ---------------------------------------------------------------


@app.get("/api/you", response_model=YouOut)
def you():
    return YouOut(
        overview=OverviewOut(**store.overview()),
        timeline=[TimelineRow(**r) for r in store.timeline()],
        written_days=store.written_days(),
        truth_days=store.truth_days(),
        year_ago=[_entry_out(e) for e in store.a_year_ago()],
    )


# --- reflection (R2-R4, ADR 003) --------------------------------------------
# The whole loop is here, and it is deliberately thin. It finds ids and hands
# back the user's own records. There is no code path in this section that
# writes a sentence about anyone's inner life, because there is no such thing
# to write: the surface shows their words or it shows nothing.


def _matching_kind() -> str:
    """What the UI is allowed to claim about how matching works right now.

    Without the local model this is honest word overlap, and the screen says so
    rather than implying an understanding the app does not have.
    """
    return "meaning" if embed.active_backend() == embed.STATIC else "shared words only"


@app.get("/api/reflection/settings", response_model=ReflectionSettings)
def reflection_settings():
    saved = store.settings()
    state = relevance.status()
    return ReflectionSettings(
        questions_on=saved["questions_on"],
        matching=_matching_kind(),
        model_present=state["model_present"],
        indexed=state["indexed"],
    )


class ReflectionSettingsIn(BaseModel):
    questions_on: bool


@app.put("/api/reflection/settings", response_model=ReflectionSettings)
def set_reflection_settings(body: ReflectionSettingsIn):
    store.save_settings({"questions_on": body.questions_on})
    return reflection_settings()


class RelatedTextIn(BaseModel):
    text: str


@app.post("/api/reflection/related", response_model=RelatedOut)
def related_to_draft(body: RelatedTextIn):
    """Past entries close to something still being written.

    The draft is embedded and thrown away. Nothing is stored, nothing is
    written to any stream, and the draft never becomes a record by being looked
    at: only pressing Keep does that.
    """
    try:
        hits = relevance.related_to_text(body.text)
    except Exception as exc:  # noqa: BLE001
        print(f"index: draft lookup failed ({exc})", file=sys.stderr)
        hits = []

    by_id = {e["id"]: e for e in store.entries()}
    out = [
        RelatedEntry(entry=_entry_out(by_id[h["id"]]), score=h["score"])
        for h in hits
        if h["id"] in by_id
    ]
    return RelatedOut(related=out, matching=_matching_kind())


@app.get("/api/reflection/related/{entry_id}", response_model=RelatedOut)
def related_entries(entry_id: str, limit: int = 3):
    """Past entries close to this one. Pull-based: nothing calls this uninvited."""
    by_id = {e["id"]: e for e in store.entries()}
    if entry_id not in by_id:
        raise HTTPException(404, "That entry isn't in your journal.")

    try:
        hits = relevance.related_to_entry(entry_id, limit=limit)
    except Exception as exc:  # noqa: BLE001 - no match is a fine answer; an error is not
        print(f"index: lookup failed ({exc})", file=sys.stderr)
        hits = []

    out = []
    for hit in hits:
        row = by_id.get(hit["id"])
        if row:  # an id the ledger no longer has is simply dropped
            out.append(RelatedEntry(entry=_entry_out(row), score=hit["score"]))
    return RelatedOut(related=out, matching=_matching_kind())


# --- egress + demo (M7) -----------------------------------------------------


@app.get("/api/export")
def export_everything(include_demo: bool = False):
    """The one door out. ADR 002's role-swap is applied here and nowhere else."""
    return store.export_bundle(include_demo=include_demo)


@app.post("/api/demo/load")
def load_demo():
    result = demo_data.load()
    _resync_index()
    return result


@app.post("/api/demo/wipe", response_model=WipeOut)
def wipe_demo():
    result = store.wipe_demo()
    _resync_index()
    return WipeOut(**result)
