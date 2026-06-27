#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
TARGET_WWW="$HA_CONFIG_DIR/www/todo-system"
TARGET_PYSCRIPTS="$HA_CONFIG_DIR/pyscripts"

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required. Example: rsync -av --delete $FRONTEND_DIR/dist/ $TARGET_WWW/" >&2
  exit 1
fi

cd "$FRONTEND_DIR"
npm run build
mkdir -p "$TARGET_WWW" "$TARGET_PYSCRIPTS"
rsync -av --delete "$FRONTEND_DIR/dist/" "$TARGET_WWW/"
rsync -av "$ROOT_DIR/ha/pyscripts/" "$TARGET_PYSCRIPTS/"

echo "Deployment complete."
echo "Example: rsync -av --delete $FRONTEND_DIR/dist/ user@ha:/config/www/todo-system/"
echo "Example: rsync -av $ROOT_DIR/ha/pyscripts/ user@ha:/config/pyscripts/"
