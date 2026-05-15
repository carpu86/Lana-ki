#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/home/carpu/LanaApp/lana-ki}"
SYNC_FOLDER="${SYNC_FOLDER_PATH:-/home/carpu/LanaApp/sync}"
LOG_ROOT="${LANA_LOG_ROOT:-/home/carpu/LanaApp/logs}"
API_PORT="${LANA_API_PORT:-8024}"

mkdir -p "$SYNC_FOLDER" "$LOG_ROOT"

echo "$(date -Iseconds) | Starte Lana Orchestrator auf Port $API_PORT" | tee -a "$LOG_ROOT/lana_self_provision.log"
(
  cd "$REPO_ROOT"
  python -m uvicorn backend.main:app --host 0.0.0.0 --port "$API_PORT"
) >> "$LOG_ROOT/lana_uvicorn.log" 2>&1 &

watch_sync() {
  if command -v inotifywait >/dev/null 2>&1; then
    inotifywait -m -e create,modify,delete "$SYNC_FOLDER" | while read -r path action file; do
      echo "$(date -Iseconds) | sync event | $action | ${path}${file}" >> "$LOG_ROOT/lana_sync_watch.log"
    done
  else
    while true; do
      find "$SYNC_FOLDER" -maxdepth 1 -type f -printf '%TY-%Tm-%TdT%TT %p\n' | sort > "$LOG_ROOT/.lana_sync_state"
      sleep 10
    done
  fi
}

watch_sync
