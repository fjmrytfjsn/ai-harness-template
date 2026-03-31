#!/usr/bin/env bash
# Prepare a stable SSH agent socket path for Dev Container bind mount.
set -euo pipefail

AGENT_ENV_FILE="$HOME/.ssh/agent.env"
AGENT_LINK="$HOME/.ssh/agent.sock"

mkdir -p "$HOME/.ssh"

has_valid_agent() {
  [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "${SSH_AUTH_SOCK}" ]
}

load_saved_agent() {
  if [ -f "$AGENT_ENV_FILE" ]; then
    # shellcheck source=/dev/null
    . "$AGENT_ENV_FILE"
  fi
}

save_agent_env() {
  cat > "$AGENT_ENV_FILE" <<EOF
export SSH_AUTH_SOCK="${SSH_AUTH_SOCK}"
export SSH_AGENT_PID="${SSH_AGENT_PID:-}"
EOF
}

start_agent_if_needed() {
  if has_valid_agent; then
    return
  fi

  load_saved_agent
  if has_valid_agent; then
    return
  fi

  eval "$(ssh-agent -s)" >/dev/null
  save_agent_env
}

start_agent_if_needed

if ! has_valid_agent; then
  echo "[devcontainer:init-ssh-agent] ERROR: SSH agent socket is unavailable." >&2
  exit 1
fi

ln -snf "$SSH_AUTH_SOCK" "$AGENT_LINK"

echo "[devcontainer:init-ssh-agent] Linked $AGENT_LINK -> $SSH_AUTH_SOCK"

if ssh-add -l >/dev/null 2>&1; then
  echo "[devcontainer:init-ssh-agent] SSH keys are loaded."
else
  echo "[devcontainer:init-ssh-agent] No SSH keys loaded. Run: ssh-add ~/.ssh/<your_key>" >&2
fi
