#!/bin/bash

# AI Harness + OpenCode Web サービス起動スクリプト  
# DevContainer 起動時に毎回実行される

set -e

# ワークスペースディレクトリの確認
WORKSPACE_DIR="${CONTAINERWORKSPACEFOLDER:-$(pwd)}"
cd "$WORKSPACE_DIR"

# OpenCode Web の起動
if [ "$OPENCODE_AUTO_START" = "true" ]; then
    echo "🚀 OpenCode Web を起動中..."
    
    # Codespaces環境での URL 構築
    if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
        ACCESS_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    else
        ACCESS_URL="http://localhost:3000"
    fi
    
    echo ""
    echo "=============================================="
    echo "🤖 AI Harness + OpenCode Web 起動完了!"
    echo ""
    echo "📱 OpenCode Web アクセス:"
    echo "   $ACCESS_URL"
    echo ""
    echo "⚙️  AI Harness 設定:"
    echo "   📁 .ai-guidance/harness.yaml"
    echo ""
    echo "🎯 クイックスタート:"
    echo "   1. VS Code 'PORTS' タブ → ポート 3000"
    echo "   2. OpenCode Web で AI プロバイダー設定"
    echo "   3. 'このプロジェクトのコードをレビューして' と入力"
    echo ""
    echo "📚 ドキュメント: SETUP.md"
    echo "=============================================="
    echo ""
    
    # OpenCode Web をバックグラウンドで起動
    nohup npx opencode-ai@latest web --port 3000 > .ai-guidance/logs/opencode.log 2>&1 &
    
    # プロセスID を保存
    echo $! > .ai-guidance/opencode.pid
    
    echo "✅ OpenCode Web がバックグラウンドで起動しました"
    echo "📋 ログ: .ai-guidance/logs/opencode.log"
    
else
    echo "ℹ️  OpenCode Web 自動起動が無効です"
    echo "   手動起動: npx opencode-ai web --port 3000"
fi

# AI Harness 設定の確認
if [ -f ".ai-guidance/harness.yaml" ]; then
    echo "✅ AI Harness 設定ファイル確認済み"
else
    echo "⚠️  AI Harness 設定ファイルが見つかりません"
    echo "   ./scripts/initialize-project.sh を実行してください"
fi

echo ""