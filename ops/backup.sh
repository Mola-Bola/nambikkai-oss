#!/usr/bin/env bash
# ============================================================================
# Nambikkai backup (FOUNDATIONS add-now item 4).
#
# Copies the journal data dir to a timestamped snapshot, VERIFIES the chain in
# the copy, and prunes old snapshots. A backup nobody has verified is a rumour,
# so this refuses to report success on a snapshot whose chain doesn't check out.
#
# Stays local by design (ADR 001): the default destination is a sibling dir on
# this machine. Point NAMBIKKAI_BACKUP_DIR at an encrypted volume if you want
# off-machine copies — that is the owner's call, not this script's.
#
# Usage:  bash ops/backup.sh          (or `make backup`)
# Restore: docs/operations/backup-restore.md
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

DATA="${NAMBIKKAI_DATA:-$ROOT/data}"
DEST="${NAMBIKKAI_BACKUP_DIR:-$HOME/.nambikkai-backups}"
KEEP="${NAMBIKKAI_BACKUP_KEEP:-14}"

if [ ! -d "$DATA" ]; then
  echo "nothing to back up yet: $DATA does not exist"
  exit 0
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SNAP="$DEST/$STAMP"
mkdir -p "$SNAP"
chmod 700 "$DEST" "$SNAP"

# The session token is an ephemeral secret, never a backup artefact.
rsync -a --exclude '.session-token' "$DATA"/ "$SNAP"/

# Prove the copy is intact before calling it a backup.
if ! PYTHONPATH="$ROOT/app/backend" "$ROOT/.venv/bin/python" - "$SNAP" <<'PY'
import os
import sys

import ledger

path = os.path.join(sys.argv[1], ledger.LEDGER_FILE)
if not os.path.exists(path):
    print("  (no journal file in snapshot; nothing to verify)")
    sys.exit(0)
ok, count, broken = ledger.verify(path)
if not ok:
    print(f"  CHAIN BROKEN in snapshot at record {broken}")
    sys.exit(1)
print(f"  verified {count} entries, chain unbroken")
PY
then
  echo "BACKUP FAILED verification: $SNAP" >&2
  exit 1
fi

# Prune: keep the newest $KEEP snapshots.
cd "$DEST"
ls -1d 20*Z 2>/dev/null | sort -r | tail -n +$((KEEP + 1)) | while read -r old; do
  rm -rf "$old"
done

echo "backup ok: $SNAP"
