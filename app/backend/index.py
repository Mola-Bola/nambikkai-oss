# ============================================================================
# Nambikkai relevance index — a DERIVED view over the ledger (ADR 003).
#
# THE LEDGER IS THE SOURCE OF TRUTH. This file writes a sqlite database that
# holds vectors and nothing a user would miss. Delete data/index.sqlite3 and
# `make index` rebuilds it exactly; the .jsonl streams are never read for
# anything but input and are never written here at all.
#
# Three rules follow from that, and they are load-bearing:
#
#   1. Indexing NEVER fails a save. Every call site wraps this module so that a
#      broken index costs you a related-entries link, not your writing. See
#      main.py's _index_quietly.
#   2. The index knows which backend and dimension wrote it. Vectors from the
#      lexical and static backends are different spaces, and comparing across
#      them would produce confident nonsense. A mismatch drops and rebuilds
#      rather than mixing.
#   3. What comes back is entry IDS AND A SCORE, and the caller reads the words
#      from the ledger. Nothing derived is ever shown to a user as content.
#
# Run a rebuild by hand:  .venv/bin/python app/backend/index.py backfill
# ============================================================================
import os
import struct
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
# store.py reaches into the engine's redaction net, so the hooks directory has
# to be importable when this file is run directly as `make index` rather than
# through the app. Without it the rebuild command dies on import.
sys.path.insert(0, os.path.join(_ROOT, "plugin", "hooks"))

import embed  # noqa: E402
import ledger  # noqa: E402
import store  # noqa: E402

DB_FILE = "index.sqlite3"

# How alike two entries must be before the surface will offer one for the
# other. MEASURED, not guessed: tests/fixtures/relevance.json holds the pairs
# these came from, and test_reflection.py re-derives them on every run.
#
# THESE ARE SET FOR PRECISION, AND THE COST IS REAL. Measured over every pair
# in tests/fixtures/relevance.json, not a hand-picked few, because sampling
# flattered them badly the first time.
#
# The honest picture for the model: of four paraphrased pairs that a person
# would call related, two score 0.44 and 0.52 and two score 0.29 and 0.32.
# Unrelated pairs reach 0.33. So the weaker half of the real matches sits
# INSIDE the noise band, and no threshold exists that catches them without
# also letting noise through. There is no clever fix available here; the model
# simply cannot tell those apart.
#
# Given that, 0.40 buys zero false matches on the whole fixture corpus with
# 0.066 of headroom, and pays for it by missing about half of what it could
# have found. That is the right way round for this product. A missed connection
# costs nothing: the user still has their journal. A false one puts two
# unrelated pieces of someone's life side by side and implies they belong
# together, in the one place that promised never to tell them what to think.
# Silence beats a bad guess, so the floor is set where silence wins.
#
# The lexical floor is high for the same reason. Without the model, matching is
# word overlap and nothing more: at 0.30 it fires only on real repetition of
# the user's own phrasing, and on the fixture corpus it fires on nothing at
# all. It misses every paraphrase there (see known_gap), which is exactly why
# the UI says "shared words only" instead of implying comprehension.
#
# One known overmatch survives at any workable floor: the same event described
# with opposite outcomes reads as one topic. That is affordable only because of
# the shape ADR 003 chose. A weak match here puts a few of the user's own lines
# behind a click with no claim attached, and costs a glance. The same weak
# match behind an asserted sentence about their inner life would cost trust,
# which is exactly why this surface never gets to make one.
#
# test_reflection.py recomputes every edge above, so none of these numbers can
# rot quietly.
FLOOR = {
    embed.LEXICAL: 0.30,
    embed.STATIC: 0.40,
}

# Entries with almost no content words match each other on emptiness alone
# ("today was fine" against "an ordinary day"). They are kept in the ledger
# like everything else and simply never offered as a match.
MIN_CONTENT_WORDS = 4


def db_path() -> str:
    return os.path.join(ledger.data_dir(), DB_FILE)


def _pack(vec: list) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _connect():
    import sqlite3

    import sqlite_vec

    os.makedirs(ledger.data_dir(), exist_ok=True)
    con = sqlite3.connect(db_path())
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)
    return con


def _schema(con, backend: str, dim: int) -> None:
    con.execute("CREATE TABLE IF NOT EXISTS index_meta (k TEXT PRIMARY KEY, v TEXT)")
    con.execute(
        "CREATE TABLE IF NOT EXISTS indexed ("
        "  rowid_ INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  entry_id TEXT UNIQUE NOT NULL,"
        "  at TEXT NOT NULL DEFAULT ''"
        ")"
    )
    con.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS entry_vectors USING vec0("
        f"  embedding float[{dim}] distance_metric=cosine"
        f")"
    )
    con.executemany(
        "INSERT OR REPLACE INTO index_meta (k, v) VALUES (?, ?)",
        [("backend", backend), ("dim", str(dim))],
    )
    con.commit()


def _stale(con, backend: str, dim: int) -> bool:
    """Does the database on disk speak a different vector language than we do?"""
    try:
        rows = dict(con.execute("SELECT k, v FROM index_meta").fetchall())
    except Exception:
        return True
    if not rows:
        return False  # brand new; _schema is about to stamp it
    return rows.get("backend") != backend or rows.get("dim") != str(dim)


def _reset(con) -> None:
    con.execute("DROP TABLE IF EXISTS entry_vectors")
    con.execute("DROP TABLE IF EXISTS indexed")
    con.execute("DROP TABLE IF EXISTS index_meta")
    con.commit()


def open_index(backend: str | None = None):
    """A connection with the right schema for the active backend, rebuilt if not."""
    backend = backend or embed.active_backend()
    dim = embed.dimension(backend)
    con = _connect()
    if _stale(con, backend, dim):
        _reset(con)
    _schema(con, backend, dim)
    return con, backend


# --- writing ----------------------------------------------------------------


def has_content(text: str) -> bool:
    return len(embed.content_words(text)) >= MIN_CONTENT_WORDS


def _write(con, backend: str, entry: dict) -> bool:
    text = store.entry_text(entry)
    if not has_content(text):
        return False
    entry_id = entry.get("id") or ""
    if not entry_id:
        return False

    vec = embed.vector(text, backend)
    cur = con.execute("SELECT rowid_ FROM indexed WHERE entry_id = ?", (entry_id,))
    row = cur.fetchone()
    if row:
        # Entries are append-only, so this is a re-index, not an edit. Replace
        # the vector in place so the row id (and any ordering) is stable.
        con.execute("DELETE FROM entry_vectors WHERE rowid = ?", (row[0],))
        rowid = row[0]
    else:
        con.execute(
            "INSERT INTO indexed (entry_id, at) VALUES (?, ?)",
            (entry_id, entry.get("at") or ""),
        )
        rowid = con.execute("SELECT last_insert_rowid()").fetchone()[0]

    con.execute(
        "INSERT INTO entry_vectors (rowid, embedding) VALUES (?, ?)", (rowid, _pack(vec))
    )
    return True


def add(entry: dict) -> bool:
    """Index one freshly written entry. Callers treat failure as a non-event."""
    con, backend = open_index()
    try:
        wrote = _write(con, backend, entry)
        con.commit()
        return wrote
    finally:
        con.close()


def backfill(rebuild: bool = False) -> dict:
    """Bring the index level with the ledger.

    rebuild=True throws the database away first, which is the honest fix for
    anything that ever looks wrong: the ledger can always regenerate this.
    """
    if rebuild and os.path.exists(db_path()):
        os.remove(db_path())

    con, backend = open_index()
    try:
        known = {r[0] for r in con.execute("SELECT entry_id FROM indexed")}
        added = 0
        for entry in store.entries():
            if entry.get("id") in known:
                continue
            if _write(con, backend, entry):
                added += 1
        con.commit()
        total = con.execute("SELECT COUNT(*) FROM indexed").fetchone()[0]
    finally:
        con.close()
    return {"backend": backend, "added": added, "indexed": total}


def forget(entry_ids) -> int:
    """Drop entries from the index, for when their records leave the ledger."""
    ids = list(entry_ids)
    if not ids:
        return 0
    con, _ = open_index()
    try:
        gone = 0
        for entry_id in ids:
            row = con.execute(
                "SELECT rowid_ FROM indexed WHERE entry_id = ?", (entry_id,)
            ).fetchone()
            if not row:
                continue
            con.execute("DELETE FROM entry_vectors WHERE rowid = ?", (row[0],))
            con.execute("DELETE FROM indexed WHERE rowid_ = ?", (row[0],))
            gone += 1
        con.commit()
        return gone
    finally:
        con.close()


# --- reading ----------------------------------------------------------------


def related_to_text(text: str, exclude: str = "", limit: int = 3, floor=None) -> list:
    """The closest past entries to a piece of writing.

    Returns [{"id", "score"}], strongest first, already filtered by the
    relevance floor. Never returns text: the caller reads the user's words from
    the ledger, so nothing derived can be mistaken for something they wrote.
    """
    if not has_content(text):
        return []

    con, backend = open_index()
    try:
        if con.execute("SELECT COUNT(*) FROM indexed").fetchone()[0] == 0:
            return []
        cut = FLOOR[backend] if floor is None else floor
        vec = embed.vector(text, backend)
        # Ask for extra: the excluded entry and sub-floor matches are dropped
        # after the search, not before it.
        rows = con.execute(
            "SELECT v.rowid, v.distance, i.entry_id "
            "FROM entry_vectors v JOIN indexed i ON i.rowid_ = v.rowid "
            "WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance",
            (_pack(vec), limit + 5),
        ).fetchall()
    finally:
        con.close()

    out = []
    for _, distance, entry_id in rows:
        if entry_id == exclude:
            continue
        score = 1.0 - float(distance)  # cosine distance back to similarity
        if score < cut:
            continue
        out.append({"id": entry_id, "score": round(score, 4)})
        if len(out) >= limit:
            break
    return out


def related_to_entry(entry_id: str, limit: int = 3, floor=None) -> list:
    entry = next((e for e in store.entries() if e.get("id") == entry_id), None)
    if not entry:
        return []
    return related_to_text(
        store.entry_text(entry), exclude=entry_id, limit=limit, floor=floor
    )


def status() -> dict:
    backend = embed.active_backend()
    con, _ = open_index()
    try:
        indexed = con.execute("SELECT COUNT(*) FROM indexed").fetchone()[0]
    finally:
        con.close()
    return {
        "backend": backend,
        "dimension": embed.dimension(backend),
        "indexed": indexed,
        "model_present": embed.model_present(),
        "floor": FLOOR[backend],
    }


if __name__ == "__main__":
    rebuild = "--rebuild" in sys.argv
    result = backfill(rebuild=rebuild)
    print(
        f"index: backend {result['backend']} · "
        f"{result['added']} newly indexed · {result['indexed']} entries total"
    )
