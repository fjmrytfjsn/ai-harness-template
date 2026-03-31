#!/bin/bash

set -e

WORKSPACE_DIR="${containerWorkspaceFolder:-${CONTAINER_WORKSPACE_FOLDER:-$(pwd)}}"
cd "$WORKSPACE_DIR"
PARENT_DIR="$(dirname "$WORKSPACE_DIR")"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        touch .env
    fi
fi

if [ -f "$PARENT_DIR/.tailscale_authKey" ]; then
    TS_AUTHKEY="$(head -n 1 "$PARENT_DIR/.tailscale_authKey" | tr -d '\r\n')"
elif [ -f ".tailscale_authKey" ]; then
    TS_AUTHKEY="$(head -n 1 .tailscale_authKey | tr -d '\r\n')"
fi

if [ -z "${TS_AUTHKEY:-}" ]; then
    read -r -p "TS_AUTHKEY を入力してください: " TS_AUTHKEY
fi

if [ -z "$TS_AUTHKEY" ]; then
    echo "TS_AUTHKEY が空のため中止します"
    exit 1
fi

if grep -q '^TS_AUTHKEY=' .env; then
    sed -i "s/^TS_AUTHKEY=.*/TS_AUTHKEY=${TS_AUTHKEY}/" .env
else
    printf '\nTS_AUTHKEY=%s\n' "$TS_AUTHKEY" >> .env
fi

echo "✅ .env に TS_AUTHKEY を設定しました"
