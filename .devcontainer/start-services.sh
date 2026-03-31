#!/bin/bash

# AI Harness + OpenCode Web サービス起動スクリプト  
# DevContainer 起動時に毎回実行される

set -e

LOCK_FILE="/tmp/ai-harness-start-services.lock"
exec 9>"$LOCK_FILE"
if ! flock -w 120 9; then
    echo "❌ start-services.sh の排他ロック取得に失敗しました"
    echo "   既存の起動処理が長時間実行中の可能性があります"
    exit 1
fi

# ワークスペースディレクトリの確認
# Dev Containers の環境変数名は containerWorkspaceFolder（小文字始まり）
WORKSPACE_DIR="${containerWorkspaceFolder:-${CONTAINER_WORKSPACE_FOLDER:-$(pwd)}}"
cd "$WORKSPACE_DIR"

# 実行時に必要なディレクトリを保証
mkdir -p .ai-guidance/logs
mkdir -p .ai-guidance/cache
mkdir -p .ai-guidance/temp

# デフォルトURL（Codespaces時は上書き）
OPENCODE_URL="http://localhost:3000"
DASHBOARD_URL="http://localhost:8000"
OPENCODE_VERSION="${OPENCODE_VERSION:-1.3.9}"
OPENCODE_STARTUP_TIMEOUT_SECONDS="${OPENCODE_STARTUP_TIMEOUT_SECONDS:-60}"
OPENCODE_START_RETRIES="${OPENCODE_START_RETRIES:-3}"
OPENCODE_MONITOR_ENABLED="${OPENCODE_MONITOR_ENABLED:-true}"
OPENCODE_MONITOR_INTERVAL_SECONDS="${OPENCODE_MONITOR_INTERVAL_SECONDS:-5}"
OPENCODE_MONITOR_LOG=".ai-guidance/logs/opencode-monitor.log"
TS_STATE_DIR="${TS_STATE_DIR:-.ai-guidance/tailscale}"
TS_SOCKET="${TS_SOCKET:-/tmp/tailscaled.sock}"
TS_HOSTNAME="${TS_HOSTNAME:-ai-harness-devcontainer}"
TS_LOG=".ai-guidance/logs/tailscaled.log"

get_pid_by_port() {
    local port="$1"
    ss -ltnp 2>/dev/null | grep -E ":${port}[[:space:]]" | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | head -n 1
}

wait_for_port() {
    local port="$1"
    local retries="${2:-10}"
    local delay="${3:-1}"
    local i
    for i in $(seq 1 "$retries"); do
        if ss -ltn 2>/dev/null | grep -qE ":${port}[[:space:]]"; then
            return 0
        fi
        sleep "$delay"
    done
    return 1
}

is_pid_alive() {
    local pid="$1"
    [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1
}

get_opencode_pid() {
    # まず 3000 を実際に LISTEN している PID を優先
    local pid=""
    pid="$(get_pid_by_port 3000)"
    if [ -n "$pid" ]; then
        echo "$pid"
        return 0
    fi

    # フォールバック: プロセスコマンドから推定
    pid="$(ps -eo pid=,args= | grep -E '\.opencode web --port 3000' | grep -v grep | awk '{print $1}' | head -n 1)"
    if [ -n "$pid" ]; then
        echo "$pid"
        return 0
    fi

    ps -eo pid=,args= | grep -E '(/| )opencode web --port 3000' | grep -v grep | awk '{print $1}' | head -n 1
}

start_opencode_web() {
    local host_arg="--hostname 0.0.0.0"
    if command -v opencode >/dev/null 2>&1; then
        # npm install -g opencode-ai が提供する実バイナリは `opencode`
        nohup setsid opencode web --port 3000 $host_arg > .ai-guidance/logs/opencode.log 2>&1 &
    elif command -v opencode-ai >/dev/null 2>&1; then
        # 旧環境互換: もし opencode-ai バイナリが存在する場合はそれを利用
        nohup setsid opencode-ai web --port 3000 $host_arg > .ai-guidance/logs/opencode.log 2>&1 &
    else
        # グローバルバイナリが未導入の環境では固定バージョンを npx で起動
        nohup setsid npx --yes "opencode-ai@${OPENCODE_VERSION}" web --port 3000 $host_arg > .ai-guidance/logs/opencode.log 2>&1 &
    fi
}

echo "🚀 AI Harness サービスを起動中..."

# Tailscale の起動（AuthKey があれば自動で参加）
if command -v tailscaled >/dev/null 2>&1; then
    mkdir -p "$TS_STATE_DIR"

    TS_TUN_FLAG=""
    if [ ! -c /dev/net/tun ]; then
        TS_TUN_FLAG="--tun=userspace-networking"
    fi

    if ! pgrep -x tailscaled >/dev/null 2>&1; then
        sudo -n nohup setsid tailscaled --state="$TS_STATE_DIR/tailscaled.state" --socket="$TS_SOCKET" $TS_TUN_FLAG > "$TS_LOG" 2>&1 & || true
        sleep 1
    fi

    if [ -n "${TS_AUTHKEY:-}" ]; then
        sudo -n tailscale --socket="$TS_SOCKET" up --authkey "$TS_AUTHKEY" --hostname "$TS_HOSTNAME" --accept-dns=false || true
    else
        echo "ℹ️  TS_AUTHKEY が未設定のため Tailscale 参加をスキップします"
        echo "   参加するには: export TS_AUTHKEY=tskey-... を設定して再起動してください"
    fi
fi

# OpenCode Web の起動
if [ "$OPENCODE_AUTO_START" = "true" ]; then
    echo "⬇️  OpenCode Web を起動中..."
    
    # Codespaces環境での URL 構築
    if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
        OPENCODE_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
        DASHBOARD_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    else
        OPENCODE_URL="http://localhost:3000"
        DASHBOARD_URL="http://localhost:8000"
    fi

    EXISTING_OPENCODE_PID="$(get_opencode_pid)"
    if [ -n "$EXISTING_OPENCODE_PID" ] && is_pid_alive "$EXISTING_OPENCODE_PID"; then
        echo "$EXISTING_OPENCODE_PID" > .ai-guidance/opencode.pid
        echo "✅ OpenCode Web は既に起動済みです (PID: $EXISTING_OPENCODE_PID)"
    else
        rm -f .ai-guidance/opencode.pid
        START_ATTEMPT=1
        STARTED=false

        while [ "$START_ATTEMPT" -le "$OPENCODE_START_RETRIES" ]; do
            echo "   OpenCode 起動試行 ${START_ATTEMPT}/${OPENCODE_START_RETRIES}..."

            # OpenCode Web をバックグラウンドで起動
            start_opencode_web
            OPENCODE_PID=$!

            if wait_for_port 3000 "$OPENCODE_STARTUP_TIMEOUT_SECONDS" 1; then
                ACTIVE_OPENCODE_PID="$(get_opencode_pid)"
                [ -z "$ACTIVE_OPENCODE_PID" ] && ACTIVE_OPENCODE_PID="$OPENCODE_PID"

                # 瞬間的にポートが開いただけのケースを避けるため、短時間の安定性を確認
                sleep 2
                if is_pid_alive "$ACTIVE_OPENCODE_PID" && ss -ltn 2>/dev/null | grep -qE ":3000[[:space:]]"; then
                    echo "$ACTIVE_OPENCODE_PID" > .ai-guidance/opencode.pid
                    echo "✅ OpenCode Web 起動完了 (PID: $ACTIVE_OPENCODE_PID)"
                    STARTED=true
                    break
                fi
            fi

            echo "⚠️  OpenCode Web 起動確認に失敗 (試行 ${START_ATTEMPT})"
            STALE_PID="$(get_opencode_pid)"
            if [ -n "$STALE_PID" ] && is_pid_alive "$STALE_PID"; then
                kill "$STALE_PID" 2>/dev/null || true
            fi
            sleep 1
            START_ATTEMPT=$((START_ATTEMPT + 1))
        done

        if [ "$STARTED" != "true" ]; then
            rm -f .ai-guidance/opencode.pid
            echo "❌ OpenCode Web の起動に失敗しました"
            echo "   使用バージョン: opencode-ai@$OPENCODE_VERSION"
            echo "   ログ: .ai-guidance/logs/opencode.log"
            exit 1
        fi
    fi
    
else
    echo "ℹ️  OpenCode Web 自動起動が無効です"
    echo "   手動起動: opencode web --port 3000"
fi

# AI Harness Dashboard の起動
echo "⬇️  AI Harness Dashboard を起動中..."

# Python 依存関係確認
python -c "import aiohttp, aiohttp_cors" 2>/dev/null || pip install --user aiohttp aiohttp-cors

# Dashboard が既に起動済みなら再起動しない
EXISTING_DASHBOARD_PID="$(get_pid_by_port 8000)"
if [ -n "$EXISTING_DASHBOARD_PID" ]; then
    echo "$EXISTING_DASHBOARD_PID" > .ai-guidance/dashboard.pid
    echo "✅ AI Harness Dashboard は既に起動済みです (PID: $EXISTING_DASHBOARD_PID)"
else
    # Dashboard をバックグラウンドで起動
    nohup python .ai-guidance/dashboard.py --host 0.0.0.0 --port 8000 > .ai-guidance/logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    if wait_for_port 8000 15 1; then
        ACTIVE_DASHBOARD_PID="$(get_pid_by_port 8000)"
        [ -z "$ACTIVE_DASHBOARD_PID" ] && ACTIVE_DASHBOARD_PID="$DASHBOARD_PID"
        echo "$ACTIVE_DASHBOARD_PID" > .ai-guidance/dashboard.pid
        echo "✅ AI Harness Dashboard 起動完了 (PID: $ACTIVE_DASHBOARD_PID)"
    else
        echo "❌ AI Harness Dashboard の起動に失敗しました"
        echo "   ログ: .ai-guidance/logs/dashboard.log"
        exit 1
    fi
fi

# バックグラウンドプロセスがロックを継承しないようにする
exec 9>&-

# OpenCode Web の簡易監視（ポートが落ちたら再起動）
# postAttach のシェル終了後も生き残るように nohup で起動する
if [ "$OPENCODE_AUTO_START" = "true" ] && [ "$OPENCODE_MONITOR_ENABLED" = "true" ]; then
    nohup setsid bash -c '
        OPENCODE_VERSION="'"$OPENCODE_VERSION"'"
        OPENCODE_MONITOR_INTERVAL_SECONDS="'"$OPENCODE_MONITOR_INTERVAL_SECONDS"'"
        OPENCODE_MONITOR_LOG="'"$OPENCODE_MONITOR_LOG"'"
        while true; do
            if ! ss -ltn 2>/dev/null | grep -qE ":3000[[:space:]]"; then
                echo "[$(date -Is)] OpenCode が停止しているため再起動します" >> "$OPENCODE_MONITOR_LOG"
                if command -v opencode >/dev/null 2>&1; then
                    nohup setsid opencode web --port 3000 --hostname 0.0.0.0 >> "$OPENCODE_MONITOR_LOG" 2>&1 &
                elif command -v opencode-ai >/dev/null 2>&1; then
                    nohup setsid opencode-ai web --port 3000 --hostname 0.0.0.0 >> "$OPENCODE_MONITOR_LOG" 2>&1 &
                else
                    nohup setsid npx --yes "opencode-ai@${OPENCODE_VERSION}" web --port 3000 --hostname 0.0.0.0 >> "$OPENCODE_MONITOR_LOG" 2>&1 &
                fi
            fi
            sleep "$OPENCODE_MONITOR_INTERVAL_SECONDS"
        done
    ' >/dev/null 2>&1 &
fi

# AI Harness 設定の確認
if [ -f ".ai-guidance/harness.yaml" ]; then
    echo "✅ AI Harness 設定ファイル確認済み"
else
    echo "⚠️  AI Harness 設定ファイルが見つかりません"
    echo "   ./scripts/initialize-project.sh を実行してください"
fi

# 起動完了メッセージ
echo ""
echo "=============================================="
echo "🤖 AI Harness 環境 起動完了!"
echo ""
echo "📱 利用可能なサービス:"
echo "   🎨 OpenCode Web:     $OPENCODE_URL"
echo "   📊 Harness Dashboard: $DASHBOARD_URL"
echo ""
echo "⚙️  設定ファイル:"
echo "   📁 .ai-guidance/harness.yaml"
echo ""
echo "🎯 クイックスタート:"
echo "   1. VS Code 'PORTS' タブから各サービスにアクセス"
echo "   2. OpenCode Web: AIプロバイダー設定後、コーディング開始"
echo "   3. Dashboard: リアルタイム監視とメトリクス確認"
echo ""
echo "📚 ドキュメント: SETUP.md | QUICK_FIX.md"
echo "=============================================="
echo ""
