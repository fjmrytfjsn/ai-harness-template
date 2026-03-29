#!/bin/bash

# AI Harness + OpenCode Web サービス起動スクリプト  
# DevContainer 起動時に毎回実行される

set -e

# ワークスペースディレクトリの確認
WORKSPACE_DIR="${CONTAINERWORKSPACEFOLDER:-$(pwd)}"
cd "$WORKSPACE_DIR"

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
    
    # OpenCode Web をバックグラウンドで起動
    nohup npx opencode-ai@latest web --port 3000 > .ai-guidance/logs/opencode.log 2>&1 &
    OPENCODE_PID=$!
    echo $OPENCODE_PID > .ai-guidance/opencode.pid
    
    echo "✅ OpenCode Web 起動完了 (PID: $OPENCODE_PID)"
    
else
    echo "ℹ️  OpenCode Web 自動起動が無効です"
    echo "   手動起動: npx opencode-ai web --port 3000"
fi

# AI Harness Dashboard の起動
echo "⬇️  AI Harness Dashboard を起動中..."

# Python 依存関係確認
python -c "import aiohttp, aiohttp_cors" 2>/dev/null || pip install --user aiohttp aiohttp-cors

# Dashboard をバックグラウンドで起動
nohup python .ai-guidance/dashboard.py --host 0.0.0.0 --port 8000 > .ai-guidance/logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > .ai-guidance/dashboard.pid

echo "✅ AI Harness Dashboard 起動完了 (PID: $DASHBOARD_PID)"

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