# ============================================================================
# Nambikkai embeddings — how a piece of writing becomes a vector, on device.
#
# ADR 003 fixes the policy this file implements:
#
#   · Embedding is a LOCAL computation or it does not happen. No entry text is
#     ever sent anywhere to be matched.
#   · The model is never fetched at runtime. It arrives through `make model`,
#     an explicit one-time step whose downloads are checksummed before use.
#     Nothing here downloads anything, ever. If the model is absent, this
#     module says so and falls back; it does not go and get it.
#
# TWO BACKENDS, ONE INTERFACE:
#
#   lexical-v1   Pure standard library. Hashed word and word-pair features,
#                L2-normalised. Always available, no download, deterministic
#                across machines and Python versions. It matches SHARED WORDS,
#                which is a real and honest kind of related, but it cannot see
#                that "couldn't sleep again" and "staring at the ceiling" are
#                the same night. That limit is published, not hidden: see
#                tests/fixtures/relevance.json (known_gap).
#
#   minilm-v1    all-MiniLM-L6-v2 (Apache-2.0) run locally through ONNX
#                Runtime. No torch, no server, no network at inference. About
#                3ms per entry on a laptop CPU, which is nothing next to how
#                often someone writes in a journal.
#
# WHY A CONTEXTUAL MODEL AND NOT A STATIC ONE. The first build of this used
# model2vec static embeddings (potion-base-8M, then -32M), which are far
# smaller and faster. They were measured against tests/fixtures/relevance.json
# and they did not work: entries that share nothing but a first-person
# ruminative tone scored HIGHER than two accounts of the same sleepless night.
# potion-base-8M separated matches from non-matches by -0.052 (that is, the
# classes overlapped and no threshold could split them), potion-retrieval-32M
# by +0.012, MiniLM by +0.135. Centering and removing principal components did
# not rescue the static models. The numbers are reproducible from the fixtures;
# the cost of being wrong here is showing someone a false connection in their
# own life, so the bigger model wins.
#
# Vectors from the two backends live in DIFFERENT SPACES and must never be
# compared. index.py records which backend wrote it and rebuilds on a mismatch.
# ============================================================================
import hashlib
import math
import os
import re

LEXICAL = "lexical-v1"
STATIC = "minilm-v1"

LEXICAL_DIM = 256
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_DIM = 384
MAX_TOKENS = 256  # the model's window; longer entries are matched on their opening

# Words too common to say anything about what an entry is ABOUT. Dropping them
# is the cheapest defence against the overmatch failure mode, where two entries
# look related because everybody writes "today" and "really".
_STOPWORD_TEXT = """
    a about after again all also am an and any are as at be because been before
    being but by can cant could did didnt do does doing dont down each even for
    from get got had has have having he her here hers him his how i id if ill im
    in into is isnt it its ive just like me more most much my no nor not now of
    off on once only or other our out over own re should so some such than that
    thats the their them then there these they this those through to too until
    up us very was wasnt we were what when where which while who why will with
    would you your youre
"""

STOPWORDS = frozenset(_STOPWORD_TEXT.split())

_TOKEN = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> list:
    """Words worth matching on: lowercased, stripped of stopwords and stubs."""
    words = []
    for raw in _TOKEN.findall((text or "").lower()):
        word = raw.strip("'")
        if len(word) > 1 and word not in STOPWORDS:
            words.append(word)
    return words


def content_words(text: str) -> list:
    """The words that carry what an entry is about. Used to spot entries too
    thin to match on, which otherwise pair up on emptiness alone."""
    return _tokens(text)


def _normalise(vec: list) -> list:
    length = math.sqrt(sum(v * v for v in vec))
    if length == 0.0:
        return vec
    return [v / length for v in vec]


def lexical_vector(text: str) -> list:
    """Hashed bag of words and word-pairs, L2-normalised.

    Word-pairs are included so "left work" and "work left" are not identical,
    and the signed hashing trick keeps collisions from all pushing one way.
    Term frequency is dampened (1 + log tf) so one word repeated ten times in a
    long vent does not drown out the rest of the entry.
    """
    words = _tokens(text)
    grams = words + [f"{a} {b}" for a, b in zip(words, words[1:], strict=False)]

    counts: dict[str, int] = {}
    for gram in grams:
        counts[gram] = counts.get(gram, 0) + 1

    vec = [0.0] * LEXICAL_DIM
    for gram, tf in counts.items():
        digest = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
        h = int.from_bytes(digest, "big")
        slot = h % LEXICAL_DIM
        sign = 1.0 if (h >> 63) & 1 else -1.0
        vec[slot] += sign * (1.0 + math.log(tf))

    return _normalise(vec)


# --- the static model -------------------------------------------------------


def model_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.environ.get("NAMBIKKAI_MODEL", os.path.join(root, "models", MODEL_NAME))


MODEL_FILES = ("model.onnx", "tokenizer.json", "config.json")


def model_present() -> bool:
    """Has `make model` been run? A file check only. This never fetches."""
    where = model_dir()
    return all(os.path.isfile(os.path.join(where, f)) for f in MODEL_FILES)


_session = None
_tokenizer = None


def _load_model():
    """Load the local model once, from disk. Never downloads, by construction:
    both loaders below are handed a filesystem path and nothing else."""
    global _session, _tokenizer
    if _session is None:
        if not model_present():
            raise RuntimeError(f"No local model at {model_dir()}. Run: make model")
        import onnxruntime as ort
        from tokenizers import Tokenizer

        _tokenizer = Tokenizer.from_file(os.path.join(model_dir(), "tokenizer.json"))
        _tokenizer.enable_truncation(MAX_TOKENS)
        _tokenizer.enable_padding()
        _session = ort.InferenceSession(
            os.path.join(model_dir(), "model.onnx"),
            providers=["CPUExecutionProvider"],
        )
    return _session, _tokenizer


def static_vector(text: str) -> list:
    """Mean-pooled sentence embedding, masked so padding contributes nothing."""
    import numpy as np

    session, tokenizer = _load_model()
    encoded = tokenizer.encode(text or "")
    ids = np.array([encoded.ids], dtype=np.int64)
    mask = np.array([encoded.attention_mask], dtype=np.int64)

    feed = {"input_ids": ids, "attention_mask": mask}
    if any(i.name == "token_type_ids" for i in session.get_inputs()):
        feed["token_type_ids"] = np.zeros_like(ids)

    tokens = session.run(None, feed)[0]  # (1, seq, hidden)
    weights = mask[..., None].astype(np.float32)
    pooled = (tokens * weights).sum(1) / np.clip(weights.sum(1), 1e-9, None)
    return _normalise([float(v) for v in pooled[0]])


def static_dim() -> int:
    return MODEL_DIM


# --- picking a backend ------------------------------------------------------


def active_backend() -> str:
    """Static when the model is on disk, lexical otherwise.

    NAMBIKKAI_EMBED forces one, which is how the test battery proves BOTH
    backends behave, on a machine that may only have downloaded one of them.
    """
    forced = os.environ.get("NAMBIKKAI_EMBED", "").strip()
    if forced in (LEXICAL, STATIC):
        return forced
    return STATIC if model_present() else LEXICAL


def dimension(backend: str | None = None) -> int:
    backend = backend or active_backend()
    return static_dim() if backend == STATIC else LEXICAL_DIM


def vector(text: str, backend: str | None = None) -> list:
    backend = backend or active_backend()
    return static_vector(text) if backend == STATIC else lexical_vector(text)
