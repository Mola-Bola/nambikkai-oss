#!/usr/bin/env bash
# ============================================================================
# The ONE place Nambikkai is allowed to reach the network for a model, and it
# only ever runs because a human typed `make model` (ADR 003).
#
# Downloads to a temp dir, checks every sha256 against ops/model-manifest.txt,
# and only then moves the files into models/. A file that does not match its
# checksum is deleted, not installed: better no model at all than one we cannot
# vouch for. Re-running when the model is already present verifies and exits.
#
# Nothing in the app calls this. app/backend/embed.py checks whether the files
# exist and falls back if they do not; it never fetches.
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/ops/model-manifest.txt"

REPO=$(awk '$1=="repo"{print $2}' "$MANIFEST")
REVISION=$(awk '$1=="revision"{print $2}' "$MANIFEST")
NAME="${REPO##*/}"
DEST="$ROOT/models/$NAME"

if command -v shasum >/dev/null 2>&1; then
  sha256() { shasum -a 256 "$1" | awk '{print $1}'; }
else
  sha256() { sha256sum "$1" | awk '{print $1}'; }
fi

# Every file the manifest pins, as "expected_sha local_name remote_path".
# The two names differ where a repo publishes a file in a subdirectory.
wanted=$(awk '$1=="sha256"{print $2, $3, $4}' "$MANIFEST")

verify_all() {
  while read -r expected file _; do
    [ -f "$DEST/$file" ] || return 1
    [ "$(sha256 "$DEST/$file")" = "$expected" ] || return 1
  done <<< "$wanted"
  return 0
}

if verify_all; then
  echo "model: $NAME already installed and verified ($DEST)"
  exit 0
fi

echo "model: fetching $REPO at $REVISION"
echo "       this is the only network step in the project, and it runs once."

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

while read -r expected file remote; do
  url="https://huggingface.co/$REPO/resolve/$REVISION/${remote:-$file}"
  echo "  -> $file"
  curl -sSL --fail --max-time 600 -o "$TMP/$file" "$url"
  got=$(sha256 "$TMP/$file")
  if [ "$got" != "$expected" ]; then
    echo "CHECKSUM MISMATCH for $file" >&2
    echo "  expected $expected" >&2
    echo "  got      $got" >&2
    echo "Nothing was installed. Check ops/model-manifest.txt against the source." >&2
    exit 1
  fi
done <<< "$wanted"

mkdir -p "$DEST"
while read -r _ file _; do
  mv "$TMP/$file" "$DEST/$file"
done <<< "$wanted"

echo "model: $NAME installed and verified at $DEST"
echo "       now run 'make index' to rebuild the relevance index with it."
