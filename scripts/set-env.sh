#!/bin/bash

set -e

WORKSPACE_DIR="${containerWorkspaceFolder:-${CONTAINER_WORKSPACE_FOLDER:-$(pwd)}}"
cd "$WORKSPACE_DIR"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        touch .env
    fi
fi

read -r -p "TS_AUTHKEY を入力してください: " TS_AUTHKEY
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
