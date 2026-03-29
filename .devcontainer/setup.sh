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
if npm install -g opencode-ai@latest; then
    echo "✅ OpenCode AI インストール完了"
else
    echo "⚠️  OpenCode AI インストール失敗（継続します）"
fi

# Python 依存関係をインストール（AI Harness用）
echo "🐍 Python 依存関係をインストール中..."
if pip install --user pyyaml jinja2 aiohttp aiofiles; then
    echo "✅ Python 依存関係インストール完了"
else
    echo "⚠️  Python 依存関係インストール失敗（継続します）"
fi

# AI Harness 用のディレクトリ作成
mkdir -p .ai-guidance/cache
mkdir -p .ai-guidance/logs
mkdir -p .ai-guidance/temp

# 権限設定
chmod +x scripts/initialize-project.sh 2>/dev/null || true

# Git 設定（Codespacesで自動設定されない場合の対策）
if [ -n "$GITHUB_USER" ]; then
    git config --global user.name "$GITHUB_USER" || true
    git config --global user.email "$GITHUB_USER@users.noreply.github.com" || true
fi

echo ""
echo "🔧 プロジェクト自動初期化を実行中..."
echo "=============================================="

# プロジェクト初期化スクリプトを自動実行
if [ -f "./scripts/initialize-project.sh" ]; then
    echo "自動初期化モードで実行します..."
    
    # デフォルト値での自動設定（安全なフォールバック付き）
    export AUTO_INIT_MODE="true"
    export DEFAULT_PROJECT_NAME="${GITHUB_REPOSITORY##*/}"
    [ -z "$DEFAULT_PROJECT_NAME" ] && export DEFAULT_PROJECT_NAME="$(basename $PWD)"
    export DEFAULT_AUTHOR_NAME="${GITHUB_USER:-Developer}"
    export DEFAULT_DESCRIPTION="AI Harness プロジェクト - 次世代AIエージェント基盤"
    export DEFAULT_REPOSITORY_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-${GITHUB_USER}/$(basename $PWD)}"
    
    # 初期化実行（エラー時は警告のみ）
    if bash ./scripts/initialize-project.sh; then
        echo "✅ プロジェクト初期化完了!"
    else
        echo "⚠️  プロジェクト初期化で一部エラーが発生しましたが、基本機能は利用可能です"
        echo "   手動で './scripts/initialize-project.sh' を実行して設定を完了してください"
    fi
else
    echo "⚠️  initialize-project.sh が見つかりません（スキップします）"
fi

echo ""
echo "✅ 全セットアップ完了!"
echo ""
echo "🎯 利用可能なサービス:"
echo "   - OpenCode Web: ポート 3000"
echo "   - AI Harness Dashboard: ポート 8000 (オプション)"
echo ""
echo "📝 すぐに始められます:"
echo "   1. VS Code の 'PORTS' タブから OpenCode Web にアクセス"
echo "   2. AI Harness スキルが利用可能な状態です"
echo "   3. 認証エラー発生時は QUICK_FIX.md を参照"
echo "   4. AI コーディングを開始!"
echo ""