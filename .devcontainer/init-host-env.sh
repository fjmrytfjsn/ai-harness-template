#!/usr/bin/env bash
# Initialize .env from host-only secrets once at container creation.
set -euo pipefail

WORKSPACE_DIR="${1:-}"
if [ -z "$WORKSPACE_DIR" ]; then
  echo "[devcontainer:init-host-env] ERROR: workspace path not provided." >&2
  exit 1
fi

HOST_PARENT_DIR="$(dirname "$WORKSPACE_DIR")"
HOST_TAILSCALE_FILE="$HOST_PARENT_DIR/.tailscale_authKey"
ENV_FILE="$WORKSPACE_DIR/.env"

if [ ! -f "$HOST_TAILSCALE_FILE" ]; then
  echo "[devcontainer:init-host-env] No .tailscale_authKey found at $HOST_TAILSCALE_FILE (skipping)."
  exit 0
fi

TS_AUTHKEY="$(head -n 1 "$HOST_TAILSCALE_FILE" | tr -d '\r\n')"
if [ -z "$TS_AUTHKEY" ]; then
  echo "[devcontainer:init-host-env] .tailscale_authKey is empty (skipping)." >&2
  exit 0
fi

if [ ! -f "$ENV_FILE" ]; then
  touch "$ENV_FILE"
fi

if grep -q '^TS_AUTHKEY=' "$ENV_FILE"; then
  sed -i "s/^TS_AUTHKEY=.*/TS_AUTHKEY=${TS_AUTHKEY}/" "$ENV_FILE"
else
  printf '\nTS_AUTHKEY=%s\n' "$TS_AUTHKEY" >> "$ENV_FILE"
fi

echo "[devcontainer:init-host-env] .env updated with TS_AUTHKEY from host file."
