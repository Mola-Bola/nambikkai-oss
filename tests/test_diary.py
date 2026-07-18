#!/usr/bin/env python3
# ============================================================================
# Nambikkai diary suite (D1-D4) — the real-life demo set.
#
# Two different things are guarded here, and only one of them can run
# everywhere:
#
#   THE CONVERTER needs corpus-data/, which is gitignored. When the source is
#   absent these checks SKIP loudly rather than passing quietly, because a
#   green tick on a test that did not run is worse than a red one.
#
#   THE DEMO RULES need nothing but the app. Labelling, wipe, and the promise
#   that a fixture is never rendered as the user's own life are asserted
#   always, with a tiny synthetic diary built here rather than from the corpus.
#
# The sharpest test in this file is boilerplate_never_leaks. The first version
# of the converter ended at "INDEX OF NAMES" and the publisher's SYNOPSIS ended
# up inside the final entry, so a line reading "Returns to work, 278" was
# sitting in a demo journal as though a man had written it about his life.
#
# Run: .venv/bin/python tests/test_diary.py   (exit 0 = pass)
# ============================================================================
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TMP = tempfile.mkdtemp(prefix="nambikkai-diary-")
os.environ["NAMBIKKAI_DATA"] = TMP  # must precede app imports

sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
sys.path.insert(0, os.path.join(ROOT, "plugin", "hooks"))

import ledger  # noqa: E402
import security  # noqa: E402
import store  # noqa: E402

fails = []
notes = []


def load_converter():
    spec = importlib.util.spec_from_file_location(
        "convert_diary", os.path.join(ROOT, "ops", "convert-diary.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def client():
    from fastapi.testclient import TestClient
    from main import app

    c = TestClient(app, base_url="http://127.0.0.1")
    c.headers.update({security.TOKEN_HEADER: security.current_token()})
    return c


# --- the converter, when the source is on this machine ----------------------

# Barbellion, PG #39585. These are the numbers the converter produced once its
# three parsing bugs were fixed. They are asserted exactly: a change here means
# either the source moved or the parse regressed, and both deserve a red tick.
EXPECTED = {
    "entries": 531,
    "first": "1903-01-03",
    "last": "1917-10-21",
}

# Spot-checks, chosen because each one covers a bug that actually happened.
SPOT_CHECKS = [
    # The very first entry, proving front matter and the H.G. Wells
    # introduction were skipped rather than swallowed.
    ("1903-01-03", "Am writing an essay on the life-history of insects"),
    # A ranged heading, "_ October_ 14 _to_ 20." with a stray space inside the
    # italic markup. Its one-word entry used to merge into the day before.
    ("1917-10-14", "Miserable."),
    # The other ranged heading, "_August_ 21--_August_ 24.".
    ("1914-08-21", "In bed with a fever."),
    # A heading set without a space, "_December_4.".
    ("1908-12-04", "Went to the Veterinary Surgeon"),
    # The last entry, proving FINIS. stopped the walk before the footnotes.
    ("1917-10-21", "Self-disgust."),
]

# Anything that would mean Project Gutenberg furniture, the publisher's back
# matter, or the index reached a demo journal.
BOILERPLATE = (
    "project gutenberg",
    "gutenberg.org",
    "index of names",
    "synopsis",
    "end of this project",
    "start of this project",
    "returns to work, 278",  # a real line from the SYNOPSIS that once leaked
    "produced by marc",
)


def converted_text():
    path = os.path.join(ROOT, "build", "demo-diaries", "barbellion.txt")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def converter_output():
    """Convert from source and check the shape of what comes out."""
    converter = load_converter()
    source = os.path.join(ROOT, converter.DIARIES["barbellion"]["path"])
    if not os.path.exists(source):
        notes.append(
            "converter: SKIPPED, corpus-data/ is absent (gitignored). "
            "Re-fetch per corpus-data/ACQUISITION-LOG.md, then `make demo-diary`."
        )
        return None

    manifest = converter.build("barbellion", check_only=True)
    for key, expected in EXPECTED.items():
        if manifest.get(key) != expected:
            fails.append(
                f"converter: {key} is {manifest.get(key)!r}, expected {expected!r}. "
                f"The source changed or the parse regressed."
            )

    # Deterministic: same input, same bytes.
    again = converter.build("barbellion", check_only=True)
    if again.get("sha256") != manifest.get("sha256"):
        fails.append("converter: two runs over the same source produced different output")

    return manifest


# THE PUBLISHED BOOK IS NOT STRICTLY CHRONOLOGICAL, and that is the source's
# doing rather than the converter's. In 1915 an "August 7" entry sits between
# January 2 and January 30, and January 30 comes before January 19. Both are in
# a stretch of thematic pieces the editor placed out of sequence ("Hearing
# Beethoven", "An Average Day").
#
# So ordering is NOT asserted. The exact known jumps are, which is stricter:
# these two may exist and nothing else may.
KNOWN_OUT_OF_ORDER = [("1915-08-07", "1915-01-30"), ("1915-01-30", "1915-01-19")]


def dates_parse_and_span_a_life(text):
    """Every heading is a real date, and the whole thing covers years."""
    dates = re.findall(r"^(\d{4}-\d{2}-\d{2})$", text, re.M)
    if len(dates) != EXPECTED["entries"]:
        fails.append(
            f"converter: found {len(dates)} date headings, expected {EXPECTED['entries']}"
        )
    from datetime import date

    parsed = []
    for d in dates:
        try:
            parsed.append(date.fromisoformat(d))
        except ValueError:
            fails.append(f"converter: {d!r} is not a real date")

    if parsed and (parsed[-1] - parsed[0]).days < 365 * 10:
        fails.append("converter: the span is under ten years, which is not a long life")

    jumps = [
        (a.isoformat(), b.isoformat())
        for a, b in zip(parsed, parsed[1:], strict=False)
        if b < a
    ]
    if jumps != KNOWN_OUT_OF_ORDER:
        fails.append(
            f"converter: out-of-order entries changed. Expected the two the editor "
            f"put out of sequence {KNOWN_OUT_OF_ORDER}, got {jumps}. Either the "
            f"source moved or the year tracking broke."
        )


def spot_checks(text):
    """Named dates carry the words the author actually wrote under them."""
    blocks = {}
    current = None
    for line in text.splitlines():
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line.strip()):
            current = line.strip()
            blocks[current] = []
        elif current:
            blocks[current].append(line)

    for date_str, expected in SPOT_CHECKS:
        body = "\n".join(blocks.get(date_str, []))
        if not body.strip():
            fails.append(f"converter: {date_str} has no entry at all")
        elif expected.lower() not in body.lower():
            fails.append(
                f"converter: {date_str} should contain {expected!r}, got {body.strip()[:80]!r}"
            )


def boilerplate_never_leaks(text):
    """No Project Gutenberg or publisher furniture inside any entry.

    This is the one that already caught a real leak, so it checks the whole
    converted file rather than a sample.
    """
    low = text.lower()
    for phrase in BOILERPLATE:
        if phrase in low:
            line = next(
                (ln.strip() for ln in text.splitlines() if phrase in ln.lower()), ""
            )
            fails.append(f"BOILERPLATE LEAK: {phrase!r} reached an entry: {line[:90]!r}")

    # Gutenberg's italic markup should be unwrapped, not left as underscores.
    if "_" in text:
        stray = [ln.strip() for ln in text.splitlines() if "_" in ln][:2]
        fails.append(f"converter: italic markup survived into entries: {stray}")


def the_gap_is_published(text):
    """Known limits, asserted so they cannot quietly change.

    Undated fragments: this diary has none, because the author dated every
    entry. If a future source has them, the manifest counts them and this is
    where that count gets a home.
    """
    manifest_path = os.path.join(ROOT, "build", "demo-diaries", "barbellion.json")
    if not os.path.exists(manifest_path):
        return
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    skipped = manifest.get("undated_lines_skipped")
    # One line of front matter sits between PART I and the first year heading
    # ("[The Following are Selected Entries.]" is stripped as editorial, the
    # remaining line is the part subtitle). Known, small, and counted.
    if skipped != 1:
        fails.append(
            f"converter: {skipped} lines were skipped before the first date, expected 1. "
            f"Anything larger means front matter is being silently dropped."
        )

    # The author wrote two entries on some days. Duplicate dates are FINE and
    # must not be de-duplicated: they are two things he wrote, not one.
    dates = re.findall(r"^(\d{4}-\d{2}-\d{2})$", text, re.M)
    if len(dates) == len(set(dates)):
        notes.append("converter: no duplicate dates this run (the diary has had two)")


# --- the demo rules, which hold with or without the corpus ------------------

TINY_DIARY = """\
1911-04-02

The rain kept on all day and I read by the window, which was no hardship.
Mrs Hallett called about the roof again and stayed for tea.

1911-04-09

Walked to the reservoir and back before dark. The water was flat and grey.
Mrs Hallett was right about the roof, which galls me more than the leak.

1912-01-15

A year since I started keeping this and I have not once written what I meant to.
"""


def build_tiny_diary():
    """A three-entry diary on disk, so demo rules are testable without corpus."""
    out_dir = os.path.join(ROOT, "build", "demo-diaries")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "testdiary.txt"), "w", encoding="utf-8") as f:
        f.write(TINY_DIARY)
    with open(os.path.join(out_dir, "testdiary.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "name": "testdiary",
                "title": "A Test Diary",
                "author": "Nobody At All",
                "source": "invented for tests/test_diary.py",
                "entries": 3,
                "first": "1911-04-02",
                "last": "1912-01-15",
                "undated_lines_skipped": 0,
                "sha256": "n/a",
            },
            f,
        )


def clean_up_tiny_diary():
    for suffix in (".txt", ".json"):
        path = os.path.join(ROOT, "build", "demo-diaries", f"testdiary{suffix}")
        if os.path.exists(path):
            os.remove(path)


def diary_is_labelled_demo(c):
    """Every record from a diary carries the demo flag and names its set."""
    listed = c.get("/api/demo/diaries").json()
    if not any(d["name"] == "testdiary" for d in listed):
        fails.append("demo: a converted diary on disk should be offered")
        return

    result = c.post("/api/demo/diaries/testdiary").json()
    if not result["loaded"] or result["entries"] != 3:
        fails.append(f"demo: loading the test diary failed: {result}")
        return

    rows = [e for e in store.entries() if e.get("src") == "import"]
    unlabelled = [e for e in rows if not e.get("demo")]
    if unlabelled:
        fails.append(
            f"DEMO LEAK: {len(unlabelled)} diary entries are not labelled demo. "
            f"A fixture must never render as the user's own life."
        )
    if any(not e.get("demo_set") for e in rows):
        fails.append("demo: diary entries must name which demo set they came from")

    health = c.get("/api/health").json()
    if not health["demo_loaded"] or "Test Diary" not in health["demo_set"]:
        fails.append(f"demo: health should name the loaded set, got {health['demo_set']!r}")

    if not any(q.get("demo") for q in store.loose_ends()):
        fails.append("demo: questions raised by a demo diary must themselves be demo")


def a_real_entry_survives_the_wipe(c):
    """The user's own writing is untouched by loading and wiping a diary."""
    c.post("/api/entries", json={"kind": "free", "body": "My own words, kept through all this."})
    mine_before = [e for e in store.entries() if not e.get("demo")]

    c.post("/api/demo/diaries/testdiary")
    removed = c.post("/api/demo/wipe").json()["removed"]
    if removed <= 0:
        fails.append("demo: wiping a diary should report what it removed")

    mine_after = [e for e in store.entries() if not e.get("demo")]
    if len(mine_after) != len(mine_before):
        fails.append(
            f"DEMO LEAK: wiping the diary changed the user's own entries "
            f"({len(mine_before)} -> {len(mine_after)})"
        )
    if store.has_demo() or store.demo_set():
        fails.append("demo: wipe must remove every diary record and clear the set name")

    for stream in ledger.all_streams():
        ok, _, _ = ledger.verify_stream(stream)
        if not ok:
            fails.append(f"demo: {stream} must still verify after a diary wipe re-seals it")


def a_missing_diary_is_not_an_error(c):
    """Asking for a diary nobody built says so, rather than exploding."""
    r = c.post("/api/demo/diaries/not-a-real-diary")
    if r.status_code != 404:
        fails.append(f"demo: an unbuilt diary should 404, got {r.status_code}")
    if "make demo-diary" not in r.text:
        fails.append("demo: the 404 should say how to prepare one")


def the_diary_is_never_committed():
    """The source and the converted copy both stay out of git."""
    with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as f:
        ignored = f.read()
    for path in ("corpus-data/**", "/build/"):
        if path not in ignored:
            fails.append(f"git: {path} must be gitignored so diary text never enters git")


def main():
    c = client()

    text = converted_text()
    manifest = converter_output()
    if manifest and text:
        dates_parse_and_span_a_life(text)
        spot_checks(text)
        boilerplate_never_leaks(text)
        the_gap_is_published(text)
    elif manifest and not text:
        notes.append("converter: source present but build/ is empty. Run `make demo-diary`.")

    build_tiny_diary()
    try:
        diary_is_labelled_demo(c)
        a_real_entry_survives_the_wipe(c)
        a_missing_diary_is_not_an_error(c)
    finally:
        clean_up_tiny_diary()

    the_diary_is_never_committed()

    for note in notes:
        print(f"note  {note}")
    if fails:
        for f in fails:
            print(f"FAIL  {f}")
        sys.exit(1)
    print(
        "nambikkai diary suite: all green "
        "(converter · dates · no boilerplate · demo labelling · wipe)"
    )


if __name__ == "__main__":
    main()
