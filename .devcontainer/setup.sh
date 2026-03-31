# AI Harness + OpenCode Web セットアップスクリプト
# DevContainer 作成時に一度だけ実行される

set -e

echo "🚀 AI Harness + OpenCode Web 環境をセットアップ中..."
echo "=============================================="

# OpenCode Web の起動に必要なツールを準備
if ! command -v xdg-open >/dev/null 2>&1; then
    echo "📦 xdg-utils をインストール中..."
    sudo apt-get update -y
    sudo apt-get install -y xdg-utils
fi

# Node.js とnpmのバージョン確認
echo "📦 Node.js: $(node --version)"
echo "📦 npm: $(npm --version)"  
echo "📦 Python: $(python --version)"

# OpenCode AI をグローバルインストール
echo "⬇️  OpenCode AI をインストール中..."
OPENCODE_VERSION="${OPENCODE_VERSION:-1.3.9}"
if npm install -g "opencode-ai@${OPENCODE_VERSION}"; then
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

# Git 設定（Codespaces/ローカル両対応）
CURRENT_GIT_NAME="$(git config --get user.name 2>/dev/null || true)"
CURRENT_GIT_EMAIL="$(git config --get user.email 2>/dev/null || true)"

if [ -z "$CURRENT_GIT_NAME" ] || [ -z "$CURRENT_GIT_EMAIL" ]; then
    if [ -n "$GITHUB_USER" ]; then
        FALLBACK_GIT_NAME="$GITHUB_USER"
        FALLBACK_GIT_EMAIL="$GITHUB_USER@users.noreply.github.com"
    else
        FALLBACK_GIT_NAME="Dev Container User"
        FALLBACK_GIT_EMAIL="devcontainer@local"
    fi

    # リポジトリローカル設定でフォールバックし、グローバル汚染を避ける
    git config user.name "$FALLBACK_GIT_NAME" || true
    git config user.email "$FALLBACK_GIT_EMAIL" || true
    echo "📝 Git user を自動設定: $FALLBACK_GIT_NAME <$FALLBACK_GIT_EMAIL>"
fi

# SSH リモート利用時の事前診断（失敗してもセットアップは継続）
ORIGIN_URL="$(git config --get remote.origin.url 2>/dev/null || true)"
if [[ "$ORIGIN_URL" == git@* ]]; then
    echo "🔐 SSH 認証を診断中..."

    if [ -S "${SSH_AUTH_SOCK:-}" ]; then
        echo "✅ SSH agent socket を検出: $SSH_AUTH_SOCK"
    else
        echo "⚠️  SSH agent socket を検出できません"
        echo "💡 Dev Container を再起動し、ホスト側で ssh-agent が有効か確認してください"
    fi

    if ssh-add -l >/dev/null 2>&1; then
        echo "✅ SSH agent に鍵が登録されています"
    else
        echo "⚠️  SSH agent に鍵がありません"
        echo "💡 ホスト側で 'ssh-add ~/.ssh/<your_key>' を実行してください"
    fi

    if ssh -T -o BatchMode=yes -o ConnectTimeout=5 git@github.com >/dev/null 2>&1; then
        echo "✅ GitHub への SSH 到達性を確認しました"
    else
        echo "⚠️  GitHub への SSH 接続を確認できませんでした"
        echo "💡 コンテナ内で 'ssh -T git@github.com' を実行して詳細を確認してください"
    fi
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
    REPOSITORY_PATH="${GITHUB_REPOSITORY:-}"
    if [ -z "$REPOSITORY_PATH" ]; then
        ORIGIN_URL="$(git config --get remote.origin.url 2>/dev/null || true)"
        if [ -n "$ORIGIN_URL" ]; then
            REPOSITORY_PATH="$(echo "$ORIGIN_URL" | sed -E 's#(git@|https://)([^/:]+)[:/]([^/]+)/([^/.]+)(\.git)?#\3/\4#')"
        fi
    fi
    REPO_OWNER="${REPOSITORY_PATH%/*}"
    REPO_NAME="${REPOSITORY_PATH##*/}"
    [ -z "$REPO_OWNER" ] && REPO_OWNER="${GITHUB_USER:-dev}"
    [ -z "$REPO_NAME" ] && REPO_NAME="$(basename "$PWD")"
    export DEFAULT_REPOSITORY_URL="${GITHUB_SERVER_URL:-https://github.com}/$REPO_OWNER/$REPO_NAME"
    
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
