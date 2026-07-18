#!/usr/bin/env python3
# ============================================================================
# Nambikkai reflection suite (R2-R6) — the doctrine of ADR 003, in assertions.
#
# The reflection loop is the part of this product most able to do harm, because
# the useful thing to do with a year of someone's writing is exactly the
# dangerous thing: notice a pattern and name it. So the tests here are less
# about "does it work" and more about "can it misbehave".
#
#   RELEVANCE   Floors are re-derived from tests/fixtures/relevance.json over
#               EVERY pair, not a chosen few. Published gaps must still be gaps
#               and published overmatches must still be overmatches: a fixture
#               file that quietly stops being true is worse than none.
#   COPY        No reflection surface may emit an asserted feeling. Every phrase
#               the app can show is checked, and the check is on the shipped
#               source, not on a copy of it.
#   OFFLINE     The model must run with the network unavailable. Enforced by
#               breaking sockets, not by trusting a comment.
#   LEDGER      Indexing must not touch the chain, and the index must be fully
#               rebuildable from the ledger.
#
# Runs WITHOUT the model (falls back to lexical and skips the model-only
# assertions), so `make test` passes on a clean checkout. Run `make model`
# first to exercise the whole thing.
#
# Run: .venv/bin/python tests/test_reflection.py   (exit 0 = pass)
# ============================================================================
import itertools
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TMP = tempfile.mkdtemp(prefix="nambikkai-reflection-")
os.environ["NAMBIKKAI_DATA"] = TMP  # must precede app imports

sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))

import embed  # noqa: E402
import index as relevance  # noqa: E402
import ledger  # noqa: E402
import security  # noqa: E402
import store  # noqa: E402

with open(os.path.join(HERE, "fixtures", "relevance.json"), encoding="utf-8") as _f:
    FIXTURES = json.load(_f)
ENTRIES = FIXTURES["entries"]

fails = []
notes = []


def client():
    from fastapi.testclient import TestClient
    from main import app

    c = TestClient(app, base_url="http://127.0.0.1")
    c.headers.update({security.TOKEN_HEADER: security.current_token()})
    return c


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=False))


# --- relevance --------------------------------------------------------------


def scores_for(backend):
    vectors = {k: embed.vector(t, backend) for k, t in ENTRIES.items()}
    return {
        frozenset((a, b)): dot(vectors[a], vectors[b])
        for a, b in itertools.combinations(ENTRIES, 2)
    }


def relevance_floors(backend):
    """The floor must sit above every unrelated pair and below what must surface.

    Both edges are recomputed here so the constants in index.py cannot drift
    away from the fixtures they were derived from.
    """
    scores = scores_for(backend)
    floor = relevance.FLOOR[backend]

    # Anything the fixtures call related is excluded from the noise measurement,
    # including the pairs we knowingly miss: they are not noise, just unreached.
    related = {frozenset((a, b)) for a, b, _ in FIXTURES["related_pairs"]}
    overmatch = {
        frozenset((a, b)) for a, b, bk, _ in FIXTURES["known_overmatch"] if bk == backend
    }
    thin = {
        k
        for k, text in ENTRIES.items()
        if len(embed.content_words(text)) < relevance.MIN_CONTENT_WORDS
    }

    noise = [
        (score, pair)
        for pair, score in scores.items()
        if pair not in related and pair not in overmatch and not (pair & thin)
    ]
    worst, worst_pair = max(noise)
    if worst >= floor:
        fails.append(
            f"relevance[{backend}]: unrelated pair {sorted(worst_pair)} scores {worst:.3f}, "
            f"at or above the floor {floor}. The surface would show a false connection."
        )
    else:
        notes.append(
            f"{backend}: floor {floor} clears worst noise "
            f"{worst:.3f} by {floor - worst:+.3f}"
        )

    for a, b, bk in FIXTURES["must_surface"]:
        if bk != backend:
            continue
        score = scores[frozenset((a, b))]
        if score < floor:
            fails.append(
                f"relevance[{backend}]: {a}~{b} must surface but scores {score:.3f} < {floor}"
            )

    for a, b in FIXTURES["must_stay_silent"]:
        score = scores[frozenset((a, b))]
        if score >= floor:
            fails.append(
                f"relevance[{backend}]: {a}~{b} must stay silent but scores {score:.3f} >= {floor}"
            )


def published_gaps(backend):
    """A gap that has closed is good news the fixtures must be told about."""
    scores = scores_for(backend)
    for a, b, bk, _why in FIXTURES["known_gap"]:
        if bk != backend:
            continue
        if scores[frozenset((a, b))] >= relevance.FLOOR[backend]:
            fails.append(
                f"relevance[{backend}]: {a}~{b} is published as a known gap but now surfaces. "
                f"That is an improvement, and relevance.json must stop calling it a gap."
            )


def published_overmatches(backend):
    """Likewise an overmatch that stopped firing. Either way the file is stale."""
    scores = scores_for(backend)
    thin = {
        k
        for k, text in ENTRIES.items()
        if len(embed.content_words(text)) < relevance.MIN_CONTENT_WORDS
    }
    for a, b, bk, _why in FIXTURES["known_overmatch"]:
        if bk != backend:
            continue
        if {a, b} & thin:
            continue  # gated before scoring; asserted for real in thin_entries()
        if scores[frozenset((a, b))] < relevance.FLOOR[backend]:
            fails.append(
                f"relevance[{backend}]: {a}~{b} is published as a known overmatch but no "
                f"longer fires. relevance.json is out of date."
            )


def thin_entries(c):
    """Entries with almost nothing in them must never be offered as a match."""
    thin = [
        k
        for k, t in ENTRIES.items()
        if len(embed.content_words(t)) < relevance.MIN_CONTENT_WORDS
    ]
    if not thin:
        fails.append("fixtures: expected at least one entry too thin to match on")
        return
    for key in thin:
        hits = relevance.related_to_text(ENTRIES[key])
        if hits:
            fails.append(
                f"thin entries: {key!r} has almost no content but returned {len(hits)} match(es). "
                f"Entries like this pair up on emptiness alone."
            )


# --- copy -------------------------------------------------------------------

# Sentences the app may never put in a user's mouth. The reflection surfaces
# are allowed to ASK; they are never allowed to conclude.
#
# "How are you feeling?" is the whole product, so the patterns below are
# written to catch the declarative forms and leave the interrogative alone:
# "you feel" is banned, "you feeling" is not.
ASSERTIONS = (
    r"you feel\b(?!ing)",
    r"you felt\b",
    r"you seem",
    r"you are feeling",
    r"you were feeling",
    r"you always\b",
    r"you never\b",
    r"your mood\b",
    r"this made you\b",
    r"sounds like you\b",
    r"you tend to\b",
    r"you struggle",
    r"we noticed\b",
    r"we think you\b",
    r"you have been feeling",
)

# Reviewed sentences that contain a banned phrase precisely because they are
# promising the opposite. Each one is here by a human decision, and matching is
# exact so a rewrite has to come back through this list.
REVIEWED_EXCEPTIONS = (
    "Nambikkai never tells you what you feel. It asks.",
)

# Clinical vocabulary. A journal, never therapy (CLAUDE.md, standing doctrine).
CLINICAL = (
    "depress",
    "anxiety disorder",
    "diagnos",
    "symptom",
    "therapy",
    "therapist",
    "treatment",
    "disorder",
    "mental illness",
    "trauma response",
)

REFLECTION_SOURCES = (
    "app/frontend/src/views/Reflection.tsx",
    "app/frontend/src/views/Today.tsx",
    "app/frontend/src/views/Journal.tsx",
    "app/frontend/src/views/Settings.tsx",
    "app/frontend/src/views/Guide.tsx",
    "app/backend/main.py",
)


def user_visible(source: str) -> str:
    """Strip comments, so the check reads what ships rather than what we told
    ourselves about it. Engineering prose is allowed to say 'you feel' while
    explaining why no screen may."""
    source = re.sub(r"/\*.*?\*/", " ", source, flags=re.S)
    kept = []
    for line in source.splitlines():
        line = re.sub(r"//.*$", "", line)
        line = re.sub(r"^\s*#.*$", "", line)
        kept.append(line)
    text = "\n".join(kept)
    for allowed in REVIEWED_EXCEPTIONS:
        text = text.replace(allowed, " ")
    return text


def copy_never_asserts():
    """No shipped reflection copy may tell someone what they feel."""
    checked = 0
    for rel in REFLECTION_SOURCES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        checked += 1
        with open(path, encoding="utf-8") as f:
            text = user_visible(f.read())
        low = text.lower()
        for pattern in ASSERTIONS:
            hit = re.search(pattern, low)
            if hit:
                fails.append(f"copy: {rel} asserts a feeling: {hit.group(0)!r}")
        for word in CLINICAL:
            if word in low:
                fails.append(f"copy: {rel} contains clinical language: {word!r}")
        # VISION: no em-dashes in anything a user reads.
        if "—" in text:
            fails.append(f"copy: {rel} contains an em-dash, which reads as machine-written")
    if checked == 0:
        fails.append("copy: no reflection sources found to check, so this proves nothing")


def the_copy_check_actually_works():
    """A guard that finds nothing is indistinguishable from no guard at all."""
    planted = 'const bad = "It sounds like you were feeling overwhelmed by that.";'
    text = user_visible(planted).lower()
    if not any(re.search(p, text) for p in ASSERTIONS):
        fails.append("copy: the assertion check failed to catch a planted asserted feeling")
    if user_visible('// you feel awful\n').strip():
        fails.append("copy: comment stripping is not working, so the check reads the wrong text")


def questions_are_a_fixed_set():
    """The gentle layer may only say sentences a human wrote and reviewed."""
    path = os.path.join(ROOT, "app", "frontend", "src", "views", "Reflection.tsx")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "QUESTIONS" not in text:
        fails.append("questions: the phrase set must be a named constant, not built inline")
    for opener in ("does this", "is this", "do you", "would you", "how does"):
        if opener in text.lower():
            return
    fails.append("questions: no question-form prompt found in the reflection surface")


# --- the promises -----------------------------------------------------------


def model_runs_offline():
    """Prove it, do not assert it: break the network and embed anyway."""
    if not embed.model_present():
        notes.append("offline: skipped, no model installed (run `make model` to cover this)")
        return

    import socket

    real_socket = socket.socket
    real_create = socket.create_connection

    def refuse(*args, **kwargs):
        raise AssertionError("the reflection loop tried to open a network connection")

    socket.socket = refuse
    socket.create_connection = refuse
    try:
        # Force a cold load so tokenizer and session construction are covered too.
        embed._session = None
        embed._tokenizer = None
        vector = embed.static_vector("a quiet evening, nothing much to report, but I wrote")
        if len(vector) != embed.MODEL_DIM:
            fails.append(f"offline: expected a {embed.MODEL_DIM}-dim vector, got {len(vector)}")
    except AssertionError as exc:
        fails.append(f"OFFLINE BREACH: {exc}")
    except Exception as exc:  # noqa: BLE001
        fails.append(f"offline: embedding failed with the network down: {exc}")
    finally:
        socket.socket = real_socket
        socket.create_connection = real_create


def no_fetching_in_app_code():
    """The app must contain no way to download a model, only a way to check."""
    for rel in ("app/backend/embed.py", "app/backend/index.py", "app/backend/main.py"):
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            text = f.read()
        for banned in ("huggingface.co", "hf_hub_download", "snapshot_download", "urlopen"):
            # The word may appear in a comment explaining the rule; a call may not.
            for line in text.splitlines():
                stripped = line.strip()
                if banned in stripped and not stripped.startswith("#"):
                    fails.append(f"offline: {rel} looks like it can fetch a model: {stripped!r}")


def index_leaves_the_ledger_alone(c):
    """Writing entries indexes them and the chain stays sealed."""
    before = ledger.verify_stream(ledger.JOURNAL)
    for text in list(ENTRIES.values())[:6]:
        c.post("/api/entries", json={"kind": "free", "body": text})
    ok, count, broken = ledger.verify_stream(ledger.JOURNAL)
    if not ok:
        fails.append(f"ledger: indexing broke the chain at record {broken}")
    if count <= before[1]:
        fails.append("ledger: entries were not actually written")

    state = relevance.status()
    if state["indexed"] == 0:
        fails.append("index: entries were written but nothing was indexed")


def index_is_rebuildable():
    """Delete the index; the ledger must be able to reproduce it exactly."""
    before = relevance.status()["indexed"]
    os.remove(relevance.db_path())
    result = relevance.backfill()
    if result["indexed"] != before:
        fails.append(
            f"index: rebuild produced {result['indexed']} entries, expected {before}. "
            f"The index must be fully derivable from the ledger."
        )


def the_rebuild_command_runs():
    """`make index` must actually start.

    It did not, once: index.py imports store, store imports the engine's
    redaction net, and running the file directly rather than through the app
    left that off sys.path. The suite exercised backfill() as a function and
    never noticed. So the command is run here as a command.
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "app", "backend", "index.py")],
        capture_output=True,
        text=True,
        env={**os.environ, "NAMBIKKAI_DATA": TMP},
    )
    if result.returncode != 0:
        fails.append(
            f"make index: the rebuild command failed to run: "
            f"{(result.stderr or result.stdout).strip().splitlines()[-1:]}"
        )


def a_wrong_backend_rebuilds_not_mixes():
    """Vectors from two backends must never end up in one table."""
    relevance.backfill(rebuild=True)
    original = os.environ.get("NAMBIKKAI_EMBED")
    other = embed.LEXICAL if embed.active_backend() == embed.STATIC else embed.STATIC
    if other == embed.STATIC and not embed.model_present():
        return  # cannot switch to a model that is not installed
    os.environ["NAMBIKKAI_EMBED"] = other
    try:
        con, backend = relevance.open_index()
        try:
            rows = dict(con.execute("SELECT k, v FROM index_meta").fetchall())
            stored = con.execute("SELECT COUNT(*) FROM indexed").fetchone()[0]
        finally:
            con.close()
        if backend != other or rows.get("backend") != other:
            fails.append(f"index: switching backend to {other} did not restamp the index")
        if stored != 0:
            fails.append(
                f"index: switching backend left {stored} vectors from the old space in place"
            )
    finally:
        if original is None:
            os.environ.pop("NAMBIKKAI_EMBED", None)
        else:
            os.environ["NAMBIKKAI_EMBED"] = original
        relevance.backfill(rebuild=True)


def related_returns_only_the_users_words(c):
    """The API may hand back records and a score. Never a generated sentence."""
    entries = c.get("/api/entries").json()["entries"]
    if not entries:
        fails.append("related: no entries to check against")
        return
    payload = c.get(f"/api/reflection/related/{entries[0]['id']}").json()
    allowed_top = {"related", "matching"}
    if set(payload) - allowed_top:
        fails.append(f"related: unexpected fields in the response: {set(payload) - allowed_top}")
    for item in payload["related"]:
        if set(item) != {"entry", "score"}:
            fails.append(f"related: an item carries more than the record and a score: {set(item)}")
        body = store.entry_text(item["entry"])
        if body and body not in "\n".join(store.entry_text(e) for e in store.entries()):
            fails.append("related: returned text that is not verbatim from the ledger")


def questions_are_off_by_default(c):
    settings = c.get("/api/reflection/settings").json()
    if settings["questions_on"]:
        fails.append("SETTINGS: the gentle-question layer must be off until the user turns it on")
    c.put("/api/reflection/settings", json={"questions_on": True})
    if not c.get("/api/reflection/settings").json()["questions_on"]:
        fails.append("settings: turning questions on did not stick")
    c.put("/api/reflection/settings", json={"questions_on": False})
    if c.get("/api/reflection/settings").json()["questions_on"]:
        fails.append("settings: turning questions back off did not stick")


def a_question_is_not_a_record(c):
    """Nothing the engine asks may become a stored appraisal by itself."""
    c.put("/api/reflection/settings", json={"questions_on": True})
    before = len(store.truths()) + len(store.entries())
    entries = c.get("/api/entries").json()["entries"]
    if entries:
        c.get(f"/api/reflection/related/{entries[0]['id']}")
    after = len(store.truths()) + len(store.entries())
    if after != before:
        fails.append(
            f"records: looking at reflection wrote {after - before} record(s). "
            f"Only a user's own answer may enter the ledger."
        )
    c.put("/api/reflection/settings", json={"questions_on": False})


def main():
    c = client()

    backends = [embed.LEXICAL] + ([embed.STATIC] if embed.model_present() else [])
    if embed.STATIC not in backends:
        notes.append("relevance: model not installed, only the lexical backend was measured")

    for backend in backends:
        relevance_floors(backend)
        published_gaps(backend)
        published_overmatches(backend)

    index_leaves_the_ledger_alone(c)
    thin_entries(c)
    index_is_rebuildable()
    the_rebuild_command_runs()
    a_wrong_backend_rebuilds_not_mixes()
    related_returns_only_the_users_words(c)
    questions_are_off_by_default(c)
    a_question_is_not_a_record(c)

    copy_never_asserts()
    the_copy_check_actually_works()
    questions_are_a_fixed_set()
    model_runs_offline()
    no_fetching_in_app_code()

    for note in notes:
        print(f"note  {note}")
    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        sys.exit(1)
    print(
        "nambikkai reflection suite: all green "
        "(relevance floors · published gaps · copy · offline · ledger untouched)"
    )


if __name__ == "__main__":
    main()
