#!/bin/bash

# AI Harness + OpenCode Web サービス起動スクリプト  
# DevContainer 起動時に毎回実行される

set -e

# ワークスペースディレクトリの確認
WORKSPACE_DIR="${CONTAINERWORKSPACEFOLDER:-$(pwd)}"
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

start_opencode_web() {
    if command -v opencode >/dev/null 2>&1; then
        # npm install -g opencode-ai が提供する実バイナリは `opencode`
        nohup opencode web --port 3000 > .ai-guidance/logs/opencode.log 2>&1 &
    elif command -v opencode-ai >/dev/null 2>&1; then
        # 旧環境互換: もし opencode-ai バイナリが存在する場合はそれを利用
        nohup opencode-ai web --port 3000 > .ai-guidance/logs/opencode.log 2>&1 &
    else
        # グローバルバイナリが未導入の環境では固定バージョンを npx で起動
        nohup npx --yes "opencode-ai@${OPENCODE_VERSION}" web --port 3000 > .ai-guidance/logs/opencode.log 2>&1 &
    fi
}

echo "🚀 AI Harness サービスを起動中..."

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

    EXISTING_OPENCODE_PID="$(get_pid_by_port 3000)"
    if [ -n "$EXISTING_OPENCODE_PID" ]; then
        echo "$EXISTING_OPENCODE_PID" > .ai-guidance/opencode.pid
        echo "✅ OpenCode Web は既に起動済みです (PID: $EXISTING_OPENCODE_PID)"
    else
        # OpenCode Web をバックグラウンドで起動
        start_opencode_web
        OPENCODE_PID=$!
        if wait_for_port 3000 "$OPENCODE_STARTUP_TIMEOUT_SECONDS" 1; then
            ACTIVE_OPENCODE_PID="$(get_pid_by_port 3000)"
            [ -z "$ACTIVE_OPENCODE_PID" ] && ACTIVE_OPENCODE_PID="$OPENCODE_PID"
            echo "$ACTIVE_OPENCODE_PID" > .ai-guidance/opencode.pid
            echo "✅ OpenCode Web 起動完了 (PID: $ACTIVE_OPENCODE_PID)"
        else
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
