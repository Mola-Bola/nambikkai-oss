# ============================================================================
# Nambikkai store — the domain operations over the chained streams (M3–M7).
#
# Two rules shape everything here:
#
# 1. APPEND-ONLY, ALWAYS. Nothing is edited in place. Revising a truth appends a
#    new record that SUPERSEDES the old one; the old text keeps its dates and
#    stays readable forever ("believed then / know now"). A truth's valid_to is
#    therefore computed, never stored — it is simply when its successor began.
#    The single exception is wiping demo data, which rewrites streams wholesale
#    and re-seals every remaining record.
#
# 2. THE MACHINE NEVER ASSERTS A FEELING (VISION, first principles). Nothing in
#    here scores, predicts or labels a mood. Import proposes questions; the user
#    answers. Counting is allowed; concluding is not.
# ============================================================================
import json
import os
import re
import uuid
from datetime import UTC, datetime

import ledger
from patterns import redact

DEMO_TAG = "demo"


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def new_id() -> str:
    return uuid.uuid4().hex


# --- preferences ------------------------------------------------------------
# Deliberately NOT in the ledger. The chained streams are a record of a life;
# whether a toggle is on is a setting, and mixing the two would put "changed a
# checkbox" in the same history as "changed my mind about my mother".

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    # ADR 003: the gentle-question layer is off until the user turns it on.
    "questions_on": False,
    # The usage guide shows once, before the first entry, and never nags after.
    "guide_seen": False,
}


def _settings_path() -> str:
    return os.path.join(ledger.data_dir(), SETTINGS_FILE)


def settings() -> dict:
    path = _settings_path()
    if not os.path.exists(path):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path, encoding="utf-8") as f:
            saved = json.load(f)
    except (OSError, ValueError):
        # An unreadable settings file must not brick the app, and the safe
        # reading of a broken preference file is always the default: off.
        return dict(DEFAULT_SETTINGS)
    return {**DEFAULT_SETTINGS, **{k: saved[k] for k in DEFAULT_SETTINGS if k in saved}}


def save_settings(changes: dict) -> dict:
    merged = {**settings(), **{k: v for k, v in changes.items() if k in DEFAULT_SETTINGS}}
    os.makedirs(ledger.data_dir(), exist_ok=True)
    with open(_settings_path(), "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    return merged


# --- entries ----------------------------------------------------------------


def entries(include_demo: bool = True) -> list:
    rows = ledger.read_stream(ledger.JOURNAL)
    if not include_demo:
        rows = [r for r in rows if not r.get(DEMO_TAG)]
    return rows


def add_entry(record: dict) -> dict:
    return ledger.append_to(ledger.JOURNAL, record)


def entry_text(entry: dict) -> str:
    """All of an entry's user-written words, joined. Used for search/threads."""
    fields = ("feeling", "why", "cause", "helps", "body")
    return "\n".join(entry.get(f) or "" for f in fields).strip()


# --- personas ---------------------------------------------------------------


def personas(include_demo: bool = True) -> list:
    rows = ledger.read_stream(ledger.PERSONAS)
    latest: dict[str, dict] = {}
    for row in rows:
        # A persona edit appends a fresh record with the same id; last wins.
        latest[row["id"]] = row
    out = [p for p in latest.values() if not p.get("deleted")]
    if not include_demo:
        out = [p for p in out if not p.get(DEMO_TAG)]
    return sorted(out, key=lambda p: p.get("name", "").lower())


def persona(persona_id: str) -> dict | None:
    for p in personas():
        if p["id"] == persona_id:
            return p
    return None


def add_persona(record: dict) -> dict:
    return ledger.append_to(ledger.PERSONAS, record)


def persona_thread(persona_id: str) -> list:
    """Entries that belong to this persona: tagged explicitly, or naming them.

    Name matching is a plain word-boundary search over the user's own text. It
    finds mentions; it never interprets them.
    """
    p = persona(persona_id)
    if not p:
        return []
    name = (p.get("name") or "").strip()
    pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE) if name else None
    found = []
    for entry in entries():
        tagged = persona_id in (entry.get("persona_ids") or [])
        named = bool(pattern and pattern.search(entry_text(entry)))
        if tagged or named:
            found.append(entry)
    return sorted(found, key=lambda e: e.get("at", ""), reverse=True)


# --- truths -----------------------------------------------------------------


def _truth_rows() -> list:
    return ledger.read_stream(ledger.TRUTHS)


def truths(include_demo: bool = True) -> list:
    """Every truth, each carrying its computed validity window.

    valid_to is derived: a truth ends when the truth that supersedes it begins.
    Nothing is mutated to make that happen.
    """
    rows = _truth_rows()
    if not include_demo:
        rows = [r for r in rows if not r.get(DEMO_TAG)]
    successor: dict[str, dict] = {}
    for row in rows:
        if row.get("supersedes"):
            successor[row["supersedes"]] = row

    out = []
    for row in rows:
        nxt = successor.get(row["id"])
        out.append(
            {
                **row,
                "valid_to": nxt["valid_from"] if nxt else None,
                "superseded_by": nxt["id"] if nxt else None,
                "current": nxt is None,
            }
        )
    return out


def add_truth(record: dict) -> dict:
    return ledger.append_to(ledger.TRUTHS, record)


def truths_about(about: str) -> list:
    rows = [t for t in truths() if t.get("about") == about]
    return sorted(rows, key=lambda t: t.get("valid_from", ""))


# --- loose ends (import's gentle questions) ---------------------------------


def loose_ends(open_only: bool = True) -> list:
    """Fold the stream: questions, minus the ones already answered or waved off."""
    rows = ledger.read_stream(ledger.LOOSE_ENDS)
    resolved = {r["resolves"] for r in rows if r.get("resolves")}
    out = [
        r
        for r in rows
        if not r.get("resolves") and (not open_only or r["id"] not in resolved)
    ]
    return sorted(out, key=lambda r: r.get("mentions", 0), reverse=True)


def add_loose_end(record: dict) -> dict:
    return ledger.append_to(ledger.LOOSE_ENDS, record)


def resolve_loose_end(loose_end_id: str, action: str) -> dict:
    return ledger.append_to(
        ledger.LOOSE_ENDS,
        {"id": new_id(), "resolves": loose_end_id, "action": action, "at": _now()},
    )


def loose_end_exists(name: str) -> bool:
    """Once asked and answered, never ask about the same name again."""
    rows = ledger.read_stream(ledger.LOOSE_ENDS)
    return any((r.get("name") or "").lower() == name.lower() for r in rows)


# --- the bigger picture (M6) ------------------------------------------------


def quiet_spell_returns(rows: list, gap_days: int = 7) -> int:
    """How many times the user came back after a quiet stretch.

    Returning is the thing worth counting (research: reward the return, never
    punish the gap). This counts events; it does not judge them.
    """
    dates = sorted({(r.get("at") or "")[:10] for r in rows if r.get("at")})
    returns = 0
    for earlier, later in zip(dates, dates[1:], strict=False):
        try:
            a = datetime.fromisoformat(earlier)
            b = datetime.fromisoformat(later)
        except ValueError:
            continue
        if (b - a).days >= gap_days:
            returns += 1
    return returns


def overview() -> dict:
    entry_rows = entries()
    truth_rows = truths()
    return {
        "entries_kept": len(entry_rows),
        "people_mapped": len(personas()),
        "truths_revisited": len([t for t in truth_rows if t.get("supersedes")]),
        "returns_after_quiet": quiet_spell_returns(entry_rows),
        "days_written": len({(r.get("at") or "")[:10] for r in entry_rows if r.get("at")}),
    }


def timeline() -> list:
    """One chronological thread of what actually happened, in the user's words.

    Deliberately NOT a mood graph. Each row is a fact the user created: they
    wrote, they mapped someone, they formed or revised a truth. No tone is
    inferred and no verdict is offered.
    """
    rows = []
    for e in entries():
        # The feeling word is shown on its own, so keep it out of the headline
        # or a guided entry reads as the same phrase twice.
        rest = "\n".join(
            (e.get(f) or "") for f in ("why", "cause", "helps", "body")
        ).strip()
        line = (rest or entry_text(e)).splitlines()
        rows.append(
            {
                "at": e.get("at", ""),
                "kind": "entry",
                "id": e.get("id", ""),
                "headline": (line[0] if line else "").strip()[:160],
                "feeling": (e.get("feeling") or "").strip(),
                "demo": bool(e.get(DEMO_TAG)),
            }
        )
    for p in personas():
        rows.append(
            {
                "at": p.get("at", ""),
                "kind": "persona",
                "id": p.get("id", ""),
                "headline": p.get("name", ""),
                "feeling": "",
                "demo": bool(p.get(DEMO_TAG)),
            }
        )
    for t in truths():
        rows.append(
            {
                "at": t.get("valid_from", ""),
                "kind": "truth-revised" if t.get("supersedes") else "truth",
                "id": t.get("id", ""),
                "headline": (t.get("text") or "")[:160],
                "feeling": "",
                "demo": bool(t.get(DEMO_TAG)),
            }
        )
    return sorted((r for r in rows if r["at"]), key=lambda r: r["at"], reverse=True)


def written_days() -> list:
    """Dates that have at least one entry. Quiet days are quiet, not missing."""
    return sorted({(r.get("at") or "")[:10] for r in entries() if r.get("at")})


def truth_days() -> list:
    return sorted({(t.get("valid_from") or "")[:10] for t in truths() if t.get("supersedes")})


def a_year_ago(window_days: int = 7) -> list:
    """Entries from roughly this week, a year back."""
    now = datetime.now(UTC)
    out = []
    for e in entries():
        try:
            when = datetime.fromisoformat(e["at"])
        except (KeyError, ValueError):
            continue
        age = (now - when).days
        if 365 - window_days <= age <= 365 + window_days:
            out.append(e)
    return sorted(out, key=lambda e: e.get("at", ""), reverse=True)


# --- egress (ADR 002) -------------------------------------------------------


def _role_for(p: dict, index: int) -> str:
    alias = (p.get("alias") or "").strip()
    return alias or f"person {index + 1}"


def export_bundle(include_demo: bool = False) -> dict:
    """Everything the user has written, prepared to LEAVE the device.

    ADR 002 is enforced here and only here: on the device names are the user's
    business, but anything crossing the line is role-swapped first and swept by
    the redaction net. This is the single egress choke-point.
    """
    people = personas(include_demo=include_demo)
    swaps = []
    for i, p in enumerate(people):
        name = (p.get("name") or "").strip()
        if name:
            swaps.append((re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE), _role_for(p, i)))

    def clean(text: str) -> str:
        out = text or ""
        for pattern, role in swaps:
            out = pattern.sub(role, out)
        return redact(out)

    out_entries = []
    for e in entries(include_demo=include_demo):
        out_entries.append(
            {
                "at": e.get("at", ""),
                "kind": e.get("kind", ""),
                **{f: clean(e.get(f, "")) for f in ("feeling", "why", "cause", "helps", "body")},
            }
        )

    out_people = []
    for i, p in enumerate(people):
        out_people.append(
            {
                "role": _role_for(p, i),
                "kind": clean(p.get("kind", "")),
                "thought_then": clean(p.get("thought_then", "")),
                "think_now": clean(p.get("think_now", "")),
                "still_relevant": p.get("still_relevant", True),
            }
        )

    by_id = {p["id"]: _role_for(p, i) for i, p in enumerate(people)}
    out_truths = []
    for t in truths(include_demo=include_demo):
        about = t.get("about", "self")
        out_truths.append(
            {
                "about": "yourself" if about == "self" else by_id.get(about, "someone"),
                "text": clean(t.get("text", "")),
                "valid_from": t.get("valid_from", ""),
                "valid_to": t.get("valid_to"),
                "current": t.get("current", True),
                # The private draft is NEVER exported, whatever else goes.
            }
        )

    return {
        "exported_at": _now(),
        "note": "Names have been replaced with roles. Identifiers have been masked.",
        "entries": out_entries,
        "people": out_people,
        "truths": out_truths,
    }


# --- demo data (M7) ---------------------------------------------------------


def wipe_demo() -> dict:
    """Remove every demo record and re-seal each stream. Real words untouched."""
    removed = 0
    for stream in ledger.all_streams():
        rows = ledger.read_stream(stream)
        keep = [r for r in rows if not r.get(DEMO_TAG)]
        removed += len(rows) - len(keep)
        if len(keep) != len(rows):
            ledger.rewrite_stream(stream, keep)
    return {"removed": removed}


def has_demo() -> bool:
    return any(
        any(r.get(DEMO_TAG) for r in ledger.read_stream(stream))
        for stream in ledger.all_streams()
    )
