#!/bin/bash

# AI Harness + OpenCode Web セットアップスクリプト
# DevContainer 作成時に一度だけ実行される

set -e

echo "🚀 AI Harness + OpenCode Web 環境をセットアップ中..."
echo "=============================================="

# Node.js とnpmのバージョン確認
echo "📦 Node.js: $(node --version)"
echo "📦 npm: $(npm --version)"
echo "📦 Python: $(python --version)"

# OpenCode AI をグローバルインストール
echo "⬇️  OpenCode AI をインストール中..."
npm install -g opencode-ai@latest

# Python 依存関係をインストール（AI Harness用）
echo "🐍 Python 依存関係をインストール中..."
pip install --user pyyaml jinja2 aiohttp aiofiles

# AI Harness 用のディレクトリ作成
mkdir -p .ai-guidance/cache
mkdir -p .ai-guidance/logs
mkdir -p .ai-guidance/temp

# 権限設定
chmod +x scripts/initialize-project.sh 2>/dev/null || true

# Git 設定（Codespacesで自動設定されない場合の対策）
if [ -n "$GITHUB_USER" ]; then
    git config --global user.name "$GITHUB_USER"
    git config --global user.email "$GITHUB_USER@users.noreply.github.com"
fi

echo "✅ セットアップ完了!"
echo ""
echo "🎯 利用可能なサービス:"
echo "   - OpenCode Web: ポート 3000"
echo "   - AI Harness Dashboard: ポート 8000 (オプション)"
echo ""
echo "📝 次のステップ:"
echo "   1. ./scripts/initialize-project.sh でプロジェクト初期化"
echo "   2. VS Code の 'PORTS' タブから OpenCode Web にアクセス"
echo "   3. AI コーディングを開始!"
echo ""