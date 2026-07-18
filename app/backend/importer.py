# ============================================================================
# Nambikkai import — reading what you already wrote (M4, the onboarding wedge).
#
# WHAT THIS DOES: splits pasted/dropped text into dated entries, and notices
# names that recur.
#
# WHAT IT DELIBERATELY DOES NOT DO: decide how you felt. No sentiment scoring,
# no mood labelling, no emotional summary — that is the first principle in
# VISION and it binds hardest right here, where a machine is reading a life.
# Recurring names become QUESTIONS in the loose-ends queue ("you mention Ravi
# four times, someone you'd like on your map?"), answerable whenever, never a
# gate, never a quiz.
#
# Import never deletes and never rewrites: your original text becomes entries,
# word for word.
# ============================================================================
import re
from datetime import UTC, datetime

ISO = r"(?P<iso>\d{4}-\d{1,2}-\d{1,2})"
DMY = r"(?P<d>\d{1,2})[/.](?P<m>\d{1,2})[/.](?P<y>\d{4})"
MONTHS = (
    "january|february|march|april|may|june|july|august|september|october|november|december"
)
DAY_MONTH = (
    rf"(?P<dd>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<mon>{MONTHS})[a-z]*\.?,?\s+(?P<yy>\d{{4}})"
)
MONTH_DAY = (
    rf"(?P<mon2>{MONTHS})[a-z]*\.?\s+(?P<dd2>\d{{1,2}})(?:st|nd|rd|th)?,?\s+(?P<yy2>\d{{4}})"
)

DATE_RE = re.compile(rf"{ISO}|{DMY}|{DAY_MONTH}|{MONTH_DAY}", re.IGNORECASE)
MONTH_INDEX = {m: i + 1 for i, m in enumerate(MONTHS.split("|"))}

# Capitalised words that are almost never someone's name.
NOT_NAMES = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "the", "this", "that", "then", "there", "they", "them", "these", "those",
    "today", "tomorrow", "yesterday", "tonight", "morning", "evening", "afternoon",
    "and", "but", "for", "with", "when", "what", "why", "how", "who", "where",
    "she", "her", "him", "his", "our", "you", "your", "yours", "its",
    "was", "were", "have", "had", "been", "did", "does", "not", "all", "just",
    "still", "again", "maybe", "after", "before", "because", "about", "into",
    "one", "two", "three", "first", "last", "next", "every", "some", "something",
    "nothing", "everything", "anyway", "well", "okay", "yeah", "god", "home",
    "work", "back", "even", "only", "like", "made", "make", "went", "got",
    "felt", "feel", "think", "thought", "said", "told", "want", "need",
}

NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")


def _parse_date(match: re.Match) -> str | None:
    g = match.groupdict()
    try:
        if g.get("iso"):
            y, m, d = (int(x) for x in g["iso"].split("-"))
        elif g.get("y"):
            # Day-first: the owner writes AU/UK style. Ambiguous dates stay ambiguous;
            # we pick one convention and say so rather than guessing per-entry.
            d, m, y = int(g["d"]), int(g["m"]), int(g["y"])
        elif g.get("yy"):
            d, m, y = int(g["dd"]), MONTH_INDEX[g["mon"].lower()], int(g["yy"])
        elif g.get("yy2"):
            d, m, y = int(g["dd2"]), MONTH_INDEX[g["mon2"].lower()], int(g["yy2"])
        else:
            return None
        return datetime(y, m, d, 12, 0, 0, tzinfo=UTC).isoformat(timespec="seconds")
    except (ValueError, KeyError):
        return None


def split_entries(text: str) -> list:
    """Break text into dated blocks. A line that opens with a date starts one."""
    lines = text.splitlines()
    blocks: list[dict] = []
    current = {"at": None, "lines": []}

    for line in lines:
        stripped = line.strip().lstrip("#*->=_ ").strip()
        match = DATE_RE.match(stripped)
        # A date opening a short line reads as a header, not prose about a date.
        if match and len(stripped) - len(match.group(0)) < 40:
            if current["lines"] and any(x.strip() for x in current["lines"]):
                blocks.append(current)
            remainder = stripped[match.end():].strip(" ·-–—:,")
            current = {"at": _parse_date(match), "lines": [remainder] if remainder else []}
        else:
            current["lines"].append(line)

    if current["lines"] and any(x.strip() for x in current["lines"]):
        blocks.append(current)

    out = []
    for block in blocks:
        body = "\n".join(block["lines"]).strip()
        if body:
            out.append({"at": block["at"], "body": body})
    return out


def name_candidates(text: str, min_mentions: int = 2) -> list:
    """Names that recur often enough to be worth asking about."""
    counts: dict[str, int] = {}
    for token in NAME_RE.findall(text):
        if token.lower() in NOT_NAMES:
            continue
        counts[token] = counts.get(token, 0) + 1
    found = [
        {"name": name, "mentions": n} for name, n in counts.items() if n >= min_mentions
    ]
    return sorted(found, key=lambda c: c["mentions"], reverse=True)


def digest(text: str) -> dict:
    """Read text; return entries to keep and questions to ask. Nothing else."""
    blocks = split_entries(text)
    undated = sum(1 for b in blocks if not b["at"])
    return {
        "entries": blocks,
        "candidates": name_candidates(text),
        "undated": undated,
    }
