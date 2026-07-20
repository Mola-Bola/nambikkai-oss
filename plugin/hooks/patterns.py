# ============================================================================
# Nambikkai detection rules — the shared pattern engine.
#
# One rule set, one golden corpus (corpus/cases.json). Every port of these
# rules — any language, any runtime — must pass the same corpus, or it does
# not ship. That is the whole trick: the corpus, not the code, is canonical.
#
# v0.2 rule pack: SG NRIC/FIN · passport shapes · AU mobile · intl (+cc) and
# US (paren) phones · US SSN · IBAN (country-anchored) · DOB (dd/mm/yyyy and
# ISO) · long account/card numbers · email · IPv4 · geo pairs · brokerage-style
# refs. Still deliberately a starter pack — regional packs land as corpus PRs
# (a rule without cases doesn't merge).
# ============================================================================
import re
from collections.abc import Callable
from typing import NamedTuple

# Three postures, calibrated by the corpus:
# - BLOCKING: high-confidence identifiers — the gate refuses egress outright.
# - WARN: overmatch-prone or routine-in-technical-payloads kinds (plain dates,
#   mixed-alnum refs, emails, IPs, coord pairs) — logged, never halting work.
#   Email is deliberately warn at the gate: it is everywhere in legitimate dev
#   payloads (commit trailers, configs); blocking it would halt routine work.
# - PROMPT: what the journal app's blur/keep question covers — everything
#   blocking, plus email, where asking the person is cheap and right.
BLOCKING_KINDS = {"nric", "passport", "phone", "account", "ssn", "iban"}
WARN_KINDS = {"dob", "brokerage", "email", "ip", "geo"}
PROMPT_KINDS = BLOCKING_KINDS | {"email"}


class Rule(NamedTuple):
    kind: str
    re: "re.Pattern[str]"
    mask: Callable[[str], str]


def _stars(n: int) -> str:
    return "*" * max(0, n)


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


# IBAN country prefixes (registry majors). Anchoring on a real country code is
# what keeps this rule blocking-grade: bare uppercase wire refs don't start
# LLDD with a valid code, so those stay in the brokerage warn tier.
_IBAN_CC = (
    "AD|AE|AL|AT|AZ|BA|BE|BG|BH|BR|CH|CY|CZ|DE|DK|DO|EE|EG|ES|FI|FO|FR|GB|GE|"
    "GI|GL|GR|GT|HR|HU|IE|IL|IQ|IS|IT|JO|KW|KZ|LB|LC|LI|LT|LU|LV|MC|MD|ME|MK|"
    "MT|MR|MU|NL|NO|PK|PL|PS|PT|QA|RO|RS|SA|SC|SE|SI|SK|SM|SV|TL|TN|TR|UA|VA|VG|XK"
)

# Order matters: more specific patterns first so they win a tie (mirrors RULES[]).
RULES = [
    # Email: wins its whole span over anything nested inside it -> d***@example.com
    Rule("email",
         re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
         lambda m: m.split("@", 1)[0][:1] + "***@" + m.split("@", 1)[1]),
    # SG FIN/NRIC: [STFGM] + 7 digits + letter -> SXXXX676B
    Rule("nric", re.compile(r"\b[STFGM]\d{7}[A-Z]\b"),
         lambda m: m[0] + "XXXX" + m[5:8] + m[8]),
    # IBAN, compact or 4-grouped, anchored on a real country code -> DE89****...3000
    Rule("iban",
         re.compile(r"\b(?:" + _IBAN_CC + r")\d{2}"
                    r"(?:[A-Z0-9]{11,30}|(?: [A-Z0-9]{4}){2,7}(?: [A-Z0-9]{1,3})?)\b"),
         lambda m: (lambda c: c[:4] + _stars(len(c) - 8) + c[-4:])(m.replace(" ", ""))),
    # Passport: letter + 7-8 digits, or 1-2 letters + 6-7 digits + optional letter
    Rule("passport", re.compile(r"\b[A-Z]\d{7,8}\b|\b[A-Z]{1,2}\d{6,7}[A-Z]?\b"),
         lambda m: m[:4] + _stars(len(m) - 5) + m[-1:]),
    # US SSN, dashed form only (bare 9 digits would overmatch) -> ***-**-8121
    Rule("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
         lambda m: "***-**-" + m[-4:]),
    # AU mobile: 04xx xxx xxx (optional spaces) -> 0402 6XX XXX
    Rule("phone", re.compile(r"\b04\d{2}\s?\d{3}\s?\d{3}\b"),
         lambda m: (lambda d: f"{d[:4]} {d[4]}XX XXX")(re.sub(r"\s", "", m))),
    # Intl phone: +cc then 8-15 digits, compact or space/dash grouped -> +61*******78
    # (lookbehind keeps arithmetic like y+12345678 out of a BLOCKING kind)
    Rule("phone",
         re.compile(r"(?<![A-Za-z0-9)])\+(?:\d{8,15}\b|\d{1,3}(?:[ -]\d{2,4}){2,4}\b)"),
         lambda m: (lambda d: "+" + d[:2] + _stars(len(d) - 4) + d[-2:])(_digits(m))),
    # US phone, paren-anchored form only ((415) 555-2671) — the bare dashed
    # form collides with part/serial numbers and stays a published gap.
    Rule("phone", re.compile(r"\(\d{3}\)[ -]?\d{3}[- ]?\d{4}\b"),
         lambda m: (lambda d: "(" + d[:3] + ") ***-**" + d[-2:])(_digits(m))),
    # DOB dd/mm/yyyy or dd-mm-yyyy -> MM/YYYY
    Rule("dob", re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"),
         lambda m: "MM/YYYY"),
    # DOB ISO yyyy-mm-dd -> YYYY-MM (any ISO date masks; documented overmatch)
    Rule("dob", re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
         lambda m: "YYYY-MM"),
    # Long account/card number (12-19 digits, optional spaces/dashes) -> ****last4
    Rule("account", re.compile(r"\b(?:\d[ -]?){11,18}\d\b"),
         lambda m: "****" + re.sub(r"[ -]", "", m)[-4:]),
    # IPv4 -> 192.*.*.* (version-quad shapes overmatch; warn tier)
    Rule("ip", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
         lambda m: m.split(".")[0] + ".*.*.*"),
    # Geo pair: decimal lat, long with >=3 decimals (scores/money carry fewer)
    Rule("geo",
         re.compile(r"(?<![\d.])-?\d{1,3}\.\d{3,6},\s?-?\d{1,3}\.\d{3,6}(?![\d.])"),
         lambda m: re.sub(r"\.\d+", ".***", m)),
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
    for start, _priority, end, kind, value, mask in all_m:
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
    for start, end, _kind, value, mask in matches:
        out += text[last:start] + mask(value)
        last = end
    return out + text[last:]


def is_clean(text: str) -> bool:
    return len(sweep(text)) == 0
