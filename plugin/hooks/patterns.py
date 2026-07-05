# ============================================================================
# Nambikkai detection rules — the shared pattern engine.
#
# One rule set, one golden corpus (corpus/cases.json). Every port of these
# rules — any language, any runtime — must pass the same corpus, or it does
# not ship. That is the whole trick: the corpus, not the code, is canonical.
#
# v0.1 rule pack: SG NRIC/FIN · passport shapes · AU mobile · DOB · long
# account/card numbers · brokerage-style refs. Deliberately a starter pack —
# regional packs land as corpus PRs (a rule without cases doesn't merge).
# ============================================================================
import re
from typing import Callable, NamedTuple

# Overmatch-prone kinds (see evals/redaction known_overmatch O-01..O-04): plain
# dates and any 6+ mixed-alnum token trip these. The gate WARNS on them (logs,
# does not block) so routine dates/codes don't halt work; it BLOCKS on the
# high-confidence identifier kinds.
BLOCKING_KINDS = {"nric", "passport", "phone", "account"}
WARN_KINDS = {"dob", "brokerage"}


class Rule(NamedTuple):
    kind: str
    re: "re.Pattern[str]"
    mask: Callable[[str], str]


def _stars(n: int) -> str:
    return "*" * max(0, n)


# Order matters: more specific patterns first so they win a tie (mirrors RULES[]).
RULES = [
    # SG FIN/NRIC: [STFGM] + 7 digits + letter -> SXXXX676B
    Rule("nric", re.compile(r"\b[STFGM]\d{7}[A-Z]\b"),
         lambda m: m[0] + "XXXX" + m[5:8] + m[8]),
    # Passport: letter + 7-8 digits, or 1-2 letters + 6-7 digits + optional letter
    Rule("passport", re.compile(r"\b[A-Z]\d{7,8}\b|\b[A-Z]{1,2}\d{6,7}[A-Z]?\b"),
         lambda m: m[:4] + _stars(len(m) - 5) + m[-1:]),
    # AU mobile: 04xx xxx xxx (optional spaces) -> 0402 6XX XXX
    Rule("phone", re.compile(r"\b04\d{2}\s?\d{3}\s?\d{3}\b"),
         lambda m: (lambda d: f"{d[:4]} {d[4]}XX XXX")(re.sub(r"\s", "", m))),
    # DOB dd/mm/yyyy or dd-mm-yyyy -> MM/YYYY
    Rule("dob", re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"),
         lambda m: "MM/YYYY"),
    # Long account/card number (12-19 digits, optional spaces/dashes) -> ****last4
    Rule("account", re.compile(r"\b(?:\d[ -]?){11,18}\d\b"),
         lambda m: "****" + re.sub(r"[ -]", "", m)[-4:]),
    # Brokerage/bank ref: 6+ alnum token with both letters and digits;
    # leading negative-lookahead skips an already-masked NRIC (SXXXX676B shape).
    Rule("brokerage",
         re.compile(r"\b(?![STFGM]XXXX\d{3}[A-Z]\b)(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z0-9]{6,}\b"),
         lambda m: m[:4] + _stars(len(m) - 6) + m[-2:]),
]


class Finding(NamedTuple):
    kind: str
    value: str
    index: int


def _resolve_matches(text: str):
    """Collect every rule match against the ORIGINAL text, then resolve overlaps
    (earliest start wins; ties break by rule priority). Mirrors resolveMatches()."""
    all_m = []
    for priority, rule in enumerate(RULES):
        for m in rule.re.finditer(text):
            all_m.append((m.start(), priority, m.end(), rule.kind, m.group(0), rule.mask))
    all_m.sort(key=lambda t: (t[0], t[1]))
    kept = []
    cursor = -1
    for start, priority, end, kind, value, mask in all_m:
        if start >= cursor:
            kept.append((start, end, kind, value, mask))
            cursor = end
    return kept


def sweep(text: str):
    """Detect (do not modify) sensitive values. Mirrors sweep()."""
    return [Finding(kind, value, start) for start, end, kind, value, mask in _resolve_matches(text)]


def redact(text: str) -> str:
    """Partial-mask sensitive values in place (mask mode). Mirrors redact()."""
    matches = _resolve_matches(text)
    if not matches:
        return text
    out, last = "", 0
    for start, end, kind, value, mask in matches:
        out += text[last:start] + mask(value)
        last = end
    return out + text[last:]


def is_clean(text: str) -> bool:
    return len(sweep(text)) == 0
