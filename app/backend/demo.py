# ============================================================================
# Nambikkai demo data (M7).
#
# Every person, pet and place below is FICTIONAL. Nothing here is drawn from a
# real journal — not the owner's, not a corpus entry, not a scraped anything
# (the ethics gate binds: licensed corpora and published material only, and
# nothing regurgitated). These are invented characters written to exercise the
# surfaces: a persona with a revised view, a truth that changed, a name that
# recurs enough to become a loose end.
#
# Every record carries demo=true. The UI says so on screen, it is never loaded
# by default, and one button removes it (store.wipe_demo). No fixture is ever
# rendered as if it were the user's own life.
# ============================================================================
import json
import os
from datetime import UTC, datetime, timedelta

import importer
import store
from patterns import BLOCKING_KINDS, redact, sweep


def _days_ago(n: int, hour: int = 19) -> str:
    when = datetime.now(UTC) - timedelta(days=n)
    return when.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat(
        timespec="seconds"
    )


PEOPLE = [
    {
        "name": "Priya",
        "alias": "mother",
        "kind": "mother · calls on Sundays",
        "thought_then": "Always worried, always calling at the wrong time.",
        "think_now": "Her worry is how she says she misses me.",
        "still_relevant": True,
    },
    {
        "name": "Sam",
        "alias": "partner",
        "kind": "partner · here, every day",
        "thought_then": "",
        "think_now": "",
        "still_relevant": True,
    },
    {
        "name": "Mochi",
        "alias": "the cat",
        "kind": "cat · owns the couch",
        "thought_then": "The reason the couch is ruined.",
        "think_now": "The reason the couch is home.",
        "still_relevant": True,
    },
    {
        "name": "The lake",
        "alias": "the lake",
        "kind": "place · the thinking room",
        "thought_then": "A hobby.",
        "think_now": "Where the thinking actually happens.",
        "still_relevant": True,
    },
]

ENTRIES = [
    {
        "days": 1,
        "kind": "free",
        "body": (
            "The lake again after work. Cold enough to empty the head. Came out grinning. "
            "Whatever the week takes, the water gives back."
        ),
    },
    {
        "days": 3,
        "kind": "guided",
        "feeling": "wound up",
        "why": "It is not the boxes. The new place still does not smell like ours.",
        "cause": "Sam, and the move",
        "helps": "Saying the actual thing instead of the boxes thing.",
    },
    {
        "days": 6,
        "kind": "free",
        "body": (
            "Priya called. She asked about the garden like I have one. "
            "Maybe that is her way of saying put down roots."
        ),
    },
    {
        "days": 9,
        "kind": "guided",
        "feeling": "steady",
        "why": "Slept properly for once and the morning was not a fight.",
        "cause": "Mochi, who slept on the laundry again with no shame at all",
        "helps": "An early night. Boring, and it works.",
    },
    {
        "days": 21,
        "kind": "free",
        "body": (
            "Long stretch of nothing written. Not because it was bad. "
            "Just quiet. Came back to it tonight."
        ),
    },
    {
        "days": 48,
        "kind": "guided",
        "feeling": "homesick",
        "why": "The light in July here is wrong. It is the wrong July.",
        "cause": "the old flat",
        "helps": "Cooking the food from home. It works more than it should.",
    },
]

# A truth that changed its mind: the whole point of the ledger, in one story.
TRUTH_OLD = "He cut me out of that project because he wanted me gone."
TRUTH_NEW = (
    "He was shielding the team from a reorg he could not talk about. "
    "I read silence as malice."
)
TRUTH_SHARE = (
    "I judged you for two years for a thing you were protecting us from. "
    "If we ever sit down again, the coffee is on me."
)
TRUTH_SELF = (
    "I do my best thinking near water. The desk is where I record it, "
    "not where it happens."
)


def load() -> dict:
    """Add the demo set. Idempotent-ish: wipe first if it is already loaded."""
    if store.has_demo():
        store.wipe_demo()

    ids = {}
    for i, person in enumerate(PEOPLE):
        record = store.add_persona(
            {
                "id": store.new_id(),
                "at": _days_ago(60 - i),
                "demo": True,
                "persona_ids": [],
                **person,
            }
        )
        ids[person["name"]] = record["id"]

    for spec in ENTRIES:
        body = {k: v for k, v in spec.items() if k not in ("days",)}
        store.add_entry(
            {
                "id": store.new_id(),
                "at": _days_ago(spec["days"]),
                "demo": True,
                "demo_set": INVENTED,
                "feeling": "",
                "why": "",
                "cause": "",
                "helps": "",
                "body": "",
                "blurred": False,
                "persona_ids": [],
                "src": "self",
                "tier": "stated",
                "ttl": "permanent",
                **body,
            }
        )

    manager = store.add_persona(
        {
            "id": store.new_id(),
            "at": _days_ago(400),
            "demo": True,
            "name": "The manager",
            "alias": "a former manager",
            "kind": "work · two jobs ago",
            "thought_then": "",
            "think_now": "",
            "still_relevant": False,
            "persona_ids": [],
        }
    )

    old = store.add_truth(
        {
            "id": store.new_id(),
            "about": manager["id"],
            "text": TRUTH_OLD,
            "valid_from": _days_ago(700),
            "share_draft": "",
            "supersedes": None,
            "demo": True,
        }
    )
    store.add_truth(
        {
            "id": store.new_id(),
            "about": manager["id"],
            "text": TRUTH_NEW,
            "valid_from": _days_ago(240),
            "share_draft": TRUTH_SHARE,
            "supersedes": old["id"],
            "demo": True,
        }
    )
    store.add_truth(
        {
            "id": store.new_id(),
            "about": "self",
            "text": TRUTH_SELF,
            "valid_from": _days_ago(40),
            "share_draft": "",
            "supersedes": None,
            "demo": True,
        }
    )

    store.add_loose_end(
        {
            "id": store.new_id(),
            "name": "Ravi",
            "mentions": 4,
            "at": _days_ago(2),
            "demo": True,
            "source": "an imported journal",
        }
    )

    return {
        "loaded": True,
        "set": INVENTED,
        "people": len(PEOPLE) + 1,
        "entries": len(ENTRIES),
    }


# ============================================================================
# The real-diary demo set (D1-D3).
#
# A public-domain diary, converted by `make demo-diary`, loaded so the app can
# be watched handling a real life at real length rather than six invented
# entries over seven weeks.
#
# IT IS STILL DEMO DATA and obeys every rule the invented set obeys: every
# record carries demo=true, it is never loaded by default, one button removes
# it, and it is never rendered as if it were the user's own life. The only
# difference is that a real person wrote it, over thirteen years, and died at
# the end of it.
#
# WHAT IS NOT DONE HERE: no personas, no truths, no feelings are invented for
# him. A truth is an appraisal a living person forms and revises; putting words
# in the mouth of a man who cannot correct them would break the same doctrine
# that stops the machine telling a user what they feel. Personas arrive the
# honest way, by the reader answering loose ends.
# ============================================================================

INVENTED = "an invented life"

DIARY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "build",
    "demo-diaries",
)

# The loose-ends queue is CAPPED for this set, and the cap is a demo-loader
# decision rather than a change to import. Barbellion's prose yields 798
# recurring capitalised words, and the most frequent are London, Yet, War,
# Journal, Doctor, Yes, Sir and Death: importer.NOT_NAMES is tuned for modern
# casual journaling and does not survive literary prose. Asking 798 questions
# one popup at a time would make the demo hostile, so it asks a few.
#
# The underlying problem is NOT fixed here on purpose. It is a real finding
# about the name heuristic at scale, it is listed under known limitations in the README,
# and the fix is still an open design question.
DIARY_QUESTION_CAP = 12


def diaries() -> list:
    """Which converted diaries are on disk. Empty until `make demo-diary`."""
    if not os.path.isdir(DIARY_DIR):
        return []
    out = []
    for name in sorted(os.listdir(DIARY_DIR)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(DIARY_DIR, name), encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, ValueError):
            continue
        if os.path.exists(os.path.join(DIARY_DIR, f"{manifest.get('name')}.txt")):
            out.append(manifest)
    return out


def load_diary(name: str) -> dict:
    """Import a converted diary as demo data, through the ordinary import path."""
    manifest = next((d for d in diaries() if d["name"] == name), None)
    if not manifest:
        return {"loaded": False, "reason": "not built"}

    with open(os.path.join(DIARY_DIR, f"{name}.txt"), encoding="utf-8") as f:
        text = f.read()

    if store.has_demo():
        store.wipe_demo()

    label = f"{manifest['title']} ({manifest['first'][:4]} to {manifest['last'][:4]})"
    result = importer.digest(text)

    for block in result["entries"]:
        body = block["body"]
        # The privacy net applies to these words exactly as it does to a user's.
        found = {f.kind for f in sweep(body)} & BLOCKING_KINDS
        store.add_entry(
            {
                "id": store.new_id(),
                "at": block["at"],
                "kind": "free",
                "feeling": "",
                "why": "",
                "cause": "",
                "helps": "",
                "body": redact(body) if found else body,
                "blurred": bool(found),
                "persona_ids": [],
                "demo": True,
                "demo_set": label,
                "src": "import",
                "tier": "stated",
                "ttl": "permanent",
            }
        )

    asked = 0
    for candidate in result["candidates"][:DIARY_QUESTION_CAP]:
        store.add_loose_end(
            {
                "id": store.new_id(),
                "name": candidate["name"],
                "mentions": candidate["mentions"],
                "at": _days_ago(0),
                # No leading "the": the popup already says "in {source}", and
                # this title starts with one ("in the The Journal of a...").
                "source": f"{manifest['title']} demo",
                "demo": True,
                "demo_set": label,
            }
        )
        asked += 1

    return {
        "loaded": True,
        "set": label,
        "entries": len(result["entries"]),
        "questions": asked,
        "candidates_found": len(result["candidates"]),
        "first": manifest["first"],
        "last": manifest["last"],
    }
