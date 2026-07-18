#!/usr/bin/env python3
# ============================================================================
# Nambikkai diary converter — a public-domain diary into something M4 can read.
#
# WHY THIS EXISTS. The synthetic demo set (app/backend/demo.py) is six entries
# over seven weeks. It proves the surfaces render; it proves nothing about a
# life. This converts a real diary spanning years into the import format the
# app already accepts, so the app can be watched handling real length: hundreds
# of entries, a loose-ends queue at real scale, a timeline that actually spans,
# and a matcher with enough material to find something.
#
# WHAT IT DOES NOT DO. It does not interpret. No sentiment, no themes, no
# summaries, no invented personas or truths for a real person who cannot
# consent to them. It splits on the dates the author wrote and stops.
#
# LICENCE AND GIT. Source is public domain (Project Gutenberg), and the PG
# header, footer and trademark boilerplate are stripped so nothing carries
# PG trademark entanglement. corpus-data/ is gitignored and so is build/:
# the diary text never enters version control at either end. This reads at
# build time only, exactly like `make model`.
#
# DETERMINISTIC AND RE-RUNNABLE: same input, same bytes out, every time.
#
# Run: make demo-diary       (or: python3 ops/convert-diary.py [--check])
# ============================================================================
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- what we know about the source ------------------------------------------
# Kept as data rather than buried in code so a second diary is a dict, not a
# rewrite. Pepys and Evelyn sit in the same folder if this proves worth it.

DIARIES = {
    "barbellion": {
        "title": "The Journal of a Disappointed Man",
        "author": "W. N. P. Barbellion",
        "source": "Project Gutenberg #39585 (public domain)",
        "path": os.path.join(
            "corpus-data",
            "gutenberg-diaries",
            "barbellion-journal-of-a-disappointed-man",
            "39585-0.txt",
        ),
        # The diary proper runs from the first PART heading to the author's own
        # "FINIS." The title page carries a bare "1919" that would otherwise
        # read as a year heading, which is why this starts at PART and not at
        # the first date.
        #
        # The end anchor was INDEX OF NAMES first, and that was wrong: between
        # the last entry and the index sit the publisher's footnotes and a
        # SYNOPSIS whose contents-listing lines ("Returns to work, 278") were
        # landing inside the final entry. Uppercase FINIS. appears exactly once
        # in the file and is the true end of the diary. The lowercase _Finis_
        # that closes Parts I and II must NOT stop the walk, which is why this
        # is case-sensitive.
        "starts_at": re.compile(r"^PART\s+[IVX]+"),
        "ends_at": re.compile(r"^FINIS\.?$"),
        "year_min": 1903,
        "year_max": 1919,
    },
}

YEAR_LINE = re.compile(r"^(1[6-9]\d\d)$")
_MONTH_NAMES = (
    "January February March April May June July August September October November December"
)
MONTHS = _MONTH_NAMES.split()
MONTH_INDEX = {m.lower(): i + 1 for i, m in enumerate(MONTHS)}

# The author's own headings: "_January_ 3." in Gutenberg's italic convention.
#
# Matched against the line with underscores REMOVED, because the typesetting is
# not consistent and two headings in this diary are malformed:
#
#   _October_ 14.            the ordinary case
#   _ October_ 14 _to_ 20.   a stray space inside the markup, "to" italicised
#   _August_ 21--_August_ 24.
#
# Matching the markup instead of the words missed both of the ranged ones, and
# their entries ("Miserable." among them) silently merged into the day before.
# A range takes its FIRST date, which is the only one the author committed to.
# The space between month and day is \s* and not \s+ on purpose: four headings
# in this diary are set without one ("_December_4."), and requiring the space
# dropped all four.
ENTRY_HEADING = re.compile(
    r"^(" + "|".join(MONTHS) + r")\s*(\d{1,2})"
    r"(?:\s*(?:--|-|–|—|to)\s*(?:(?:" + "|".join(MONTHS) + r")\s*)?\d{1,2})?"
    r"\s*\.?\s*$",
    re.IGNORECASE,
)

UNDERSCORES = re.compile(r"_")

# Structural furniture that is not diary text: part titles, and whole-line
# editorial interjections in brackets, which are the publisher speaking and
# not the diarist.
PART_HEADING = re.compile(r"^PART\s+[IVX]+")
EDITORIAL = re.compile(r"^_?\[.*\]_?$")

# Gutenberg marks italics with underscores. They read as noise in a journal, so
# they are unwrapped -- on the JOINED body, not per line, because the source
# wraps at 72 columns and a species name like "_Strix flammea_" straddles two
# lines. Doing this per line left 74 of them stranded.
#
# Still conservative: a pair spanning a blank line, or a very long span, is
# almost certainly two unrelated underscores rather than emphasis, so it is
# left exactly as written.
ITALICS = re.compile(r"_([^_]+?)_", re.S)


def _unwrap(match: re.Match) -> str:
    inner = match.group(1)
    if "\n\n" in inner or len(inner) > 200:
        return match.group(0)
    return inner


def clean_line(line: str) -> str:
    return line.rstrip()


def convert(spec: dict, text: str) -> dict:
    """Split a diary into dated entries. Returns entries plus what was skipped."""
    lines = text.splitlines()

    started = False
    year = None
    entries: list[dict] = []
    current: dict | None = None
    # Anything the converter could not place: counted, never silently dropped.
    undated_lines = 0

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not started:
            if spec["starts_at"].match(stripped):
                started = True
            continue
        if spec["ends_at"].match(stripped):
            break

        year_match = YEAR_LINE.match(stripped)
        if year_match and spec["year_min"] <= int(year_match.group(1)) <= spec["year_max"]:
            year = int(year_match.group(1))
            continue

        if PART_HEADING.match(stripped) or EDITORIAL.match(stripped):
            continue

        # A heading candidate is short and, once the italic markup is gone,
        # reads as a date and nothing else. The length guard keeps prose that
        # happens to open with a month and a number from being promoted.
        bare = UNDERSCORES.sub("", stripped).strip()
        heading = ENTRY_HEADING.match(bare) if len(bare) <= 40 else None
        if heading and year is not None:
            month = MONTH_INDEX[heading.group(1).lower()]
            day = int(heading.group(2))
            try:
                # Guard against a mis-set day, e.g. "February 30". A heading we
                # cannot turn into a real date is not silently dropped: it is
                # left to fall through as body text of the previous entry.
                from datetime import date

                date(year, month, day)
            except ValueError:
                if current:
                    current["lines"].append(clean_line(line))
                else:
                    undated_lines += 1
                continue

            if current:
                entries.append(current)
            current = {"date": f"{year:04d}-{month:02d}-{day:02d}", "lines": []}
            continue

        if current is None:
            # Prose before the first dated heading, which is front matter the
            # anchors did not catch. Counted so the goldens can assert on it.
            if stripped:
                undated_lines += 1
            continue

        current["lines"].append(clean_line(line))

    if current:
        entries.append(current)

    kept = []
    for entry in entries:
        body = "\n".join(entry["lines"]).strip()
        # Collapse runs of blank lines inside an entry; keep paragraphs.
        body = re.sub(r"\n{3,}", "\n\n", body)
        body = ITALICS.sub(_unwrap, body)
        if body:
            kept.append({"date": entry["date"], "body": body})

    return {"entries": kept, "undated_lines": undated_lines}


def render(spec: dict, entries: list) -> str:
    """The import file: an ISO date on its own line, then the entry.

    ISO because app/backend/importer.py already parses it and because it is the
    one date format with no day-first/month-first ambiguity to get wrong.
    """
    out = []
    for entry in entries:
        out.append(entry["date"])
        out.append("")
        out.append(entry["body"])
        out.append("")
    return "\n".join(out).strip() + "\n"


def build(name: str, check_only: bool = False) -> dict:
    spec = DIARIES[name]
    source = os.path.join(ROOT, spec["path"])
    if not os.path.exists(source):
        print(
            f"convert-diary: no source at {spec['path']}\n"
            f"  corpus-data/ is gitignored on purpose. Re-fetch per "
            f"corpus-data/ACQUISITION-LOG.md.",
            file=sys.stderr,
        )
        return {}

    with open(source, encoding="utf-8") as f:
        text = f.read()

    result = convert(spec, text)
    entries = result["entries"]
    if not entries:
        print(f"convert-diary: {name} produced no entries, refusing to write", file=sys.stderr)
        return {}

    rendered = render(spec, entries)

    manifest = {
        "name": name,
        "title": spec["title"],
        "author": spec["author"],
        "source": spec["source"],
        "entries": len(entries),
        "first": entries[0]["date"],
        "last": entries[-1]["date"],
        "undated_lines_skipped": result["undated_lines"],
        "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
    }

    if not check_only:
        out_dir = os.path.join(ROOT, "build", "demo-diaries")
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write(rendered)
        with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Convert a public-domain diary for import.")
    parser.add_argument("name", nargs="?", default="barbellion", choices=sorted(DIARIES))
    parser.add_argument(
        "--check", action="store_true", help="convert and report without writing"
    )
    args = parser.parse_args()

    manifest = build(args.name, check_only=args.check)
    if not manifest:
        sys.exit(1)

    print(
        f"{manifest['name']}: {manifest['entries']} entries "
        f"{manifest['first']} to {manifest['last']} "
        f"({manifest['undated_lines_skipped']} lines skipped before the first date)"
    )
    if not args.check:
        print("  wrote build/demo-diaries/ (gitignored, like the source)")


if __name__ == "__main__":
    main()
