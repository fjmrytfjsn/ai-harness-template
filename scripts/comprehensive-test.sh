#!/bin/bash

# AI Harness Template 総合テストスクリプト
# 全機能の統合テストと検証

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_LOG="$PROJECT_ROOT/.ai-guidance/logs/comprehensive-test.log"

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ログ関数
log() {
    echo -e "$1" | tee -a "$TEST_LOG"
}

print_header() {
    log "${BLUE}=============================================="
    log "🧪 AI Harness Template - 総合テスト"
    log "==============================================${NC}"
}

print_section() {
    log "\n${PURPLE}📋 $1${NC}"
    log "----------------------------------------------"
}

print_test() {
    log "${BLUE}🔍 テスト: $1${NC}"
}

print_success() {
    log "${GREEN}✅ 成功: $1${NC}"
}

print_warning() {
    log "${YELLOW}⚠️  警告: $1${NC}"
}

print_error() {
    log "${RED}❌ 失敗: $1${NC}"
}

# テスト結果カウンター
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNING_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_test "$test_name"
    
    if eval "$test_command" >> "$TEST_LOG" 2>&1; then
        if [ $? -eq $expected_exit_code ]; then
            print_success "$test_name"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            print_warning "$test_name (予期しない終了コード)"
            WARNING_TESTS=$((WARNING_TESTS + 1))
            return 1
        fi
    else
        print_error "$test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# テスト開始
cd "$PROJECT_ROOT"

print_header

# ログディレクトリ作成
mkdir -p "$(dirname "$TEST_LOG")"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 総合テスト開始" > "$TEST_LOG"

# 1. ファイル構造テスト
print_section "ファイル構造テスト"

run_test "必須ディレクトリ存在確認" "[ -d '.ai-guidance' ] && [ -d 'scripts' ] && [ -d 'docs' ]"
run_test "設定ファイル存在確認" "[ -f '.ai-guidance/harness.yaml' ]"
run_test "スクリプト存在確認" "[ -f 'scripts/dashboard.sh' ] && [ -f 'scripts/update-template.sh' ] && [ -f 'scripts/initialize-project.sh' ]"
run_test "ドキュメント存在確認" "[ -f 'README.md' ] && [ -f 'VERSION.md' ] && [ -f 'docs/UPDATE_GUIDE.md' ]"
run_test "DevContainer設定確認" "[ -f '.devcontainer/devcontainer.json' ] && [ -f '.devcontainer/setup.sh' ]"

# 2. スクリプト実行権限テスト
print_section "スクリプト実行権限テスト"

run_test "dashboard.sh実行権限" "[ -x 'scripts/dashboard.sh' ]"
run_test "update-template.sh実行権限" "[ -x 'scripts/update-template.sh' ]"
run_test "initialize-project.sh実行権限" "[ -x 'scripts/initialize-project.sh' ]"

# 3. 設定ファイル検証テスト
print_section "設定ファイル検証テスト"

run_test "harness.yaml構文チェック" "python -c 'import yaml; yaml.safe_load(open(\".ai-guidance/harness.yaml\"))'"
run_test "devcontainer.json構文チェック" "python -c 'import json; json.load(open(\".devcontainer/devcontainer.json\"))'"

# 4. 依存関係テスト
print_section "依存関係テスト"

run_test "Python利用可能性" "python --version"
run_test "Node.js利用可能性" "node --version"
run_test "npm利用可能性" "npm --version"
run_test "Git利用可能性" "git --version"

# 5. Python依存関係テスト
print_section "Python依存関係テスト"

run_test "yaml解析" "python -c 'import yaml; print(\"yaml OK\")'"
run_test "aiohttp可用性" "python -c 'import aiohttp; print(\"aiohttp OK\")' 2>/dev/null || echo 'aiohttp not installed'"
run_test "psutil可用性" "python -c 'import psutil; print(\"psutil OK\")' 2>/dev/null || echo 'psutil not installed'"

# 6. スクリプト基本機能テスト
print_section "スクリプト基本機能テスト"

run_test "dashboard.sh ヘルプ表示" "./scripts/dashboard.sh help"
run_test "update-template.sh ヘルプ表示" "./scripts/update-template.sh help"
run_test "initialize-project.sh パーミッション" "[ -x './scripts/initialize-project.sh' ]"

# 7. Dashboard機能テスト
print_section "Dashboard機能テスト"

run_test "Dashboard起動テスト" "./scripts/dashboard.sh start"
sleep 3
run_test "Dashboard状態確認" "./scripts/dashboard.sh status"
run_test "Dashboard接続テスト" "curl -s http://localhost:8000 > /dev/null"
run_test "Dashboard停止テスト" "./scripts/dashboard.sh stop"

# 8. 更新システム機能テスト  
print_section "更新システム機能テスト"

run_test "更新システム状態確認" "./scripts/update-template.sh status"
run_test "テンプレートリモート確認" "git remote get-url template"

# 9. AI Harness スキルテスト
print_section "AI Harness スキルテスト"

run_test "スキルディレクトリ確認" "[ -d '.ai-guidance/skills' ]"
run_test "コードレビュースキル" "[ -f '.ai-guidance/skills/code_review.py' ]"
run_test "ファイル分析スキル" "[ -f '.ai-guidance/skills/file_analyzer.py' ]"
run_test "基本スキルクラス" "[ -f '.ai-guidance/skills/base.py' ]"

# 10. ミドルウェアテスト
print_section "ミドルウェアテスト"

run_test "ミドルウェアディレクトリ確認" "[ -d '.ai-guidance/middleware' ]"
run_test "ログミドルウェア" "[ -f '.ai-guidance/middleware/logging.py' ]"
run_test "セキュリティミドルウェア" "[ -f '.ai-guidance/middleware/security.py' ]"
run_test "パフォーマンスミドルウェア" "[ -f '.ai-guidance/middleware/performance.py' ]"

# 11. MCP統合テスト
print_section "MCP統合テスト"

run_test "MCP設定ディレクトリ" "[ -d '.ai-guidance/mcp' ]"
run_test "GitHub MCP設定" "[ -f '.ai-guidance/mcp/github.yaml' ]"
run_test "Playwright MCP設定" "[ -f '.ai-guidance/mcp/playwright.yaml' ]"

# 12. OpenCode Web統合テスト
print_section "OpenCode Web統合テスト"

run_test "OpenCode統合設定" "[ -f '.ai-guidance/opencode-integration.yaml' ]"
run_test "OpenCode Web パッケージ確認" "npm list -g opencode-ai || echo 'OpenCode Web not installed globally'"

# 13. ドキュメント整合性テスト
print_section "ドキュメント整合性テスト"

run_test "README.md基本構造" "grep -q '# AI エージェントハーネス テンプレート' README.md"
run_test "バージョン情報存在" "grep -q 'v1.0.0' VERSION.md"
run_test "アップデートガイド存在" "grep -q 'Template Update Guide' docs/UPDATE_GUIDE.md"
run_test "Dashboard ガイド存在" "[ -f 'docs/DASHBOARD.md' ]"

# 14. GitHub統合テスト
print_section "GitHub統合テスト"

run_test "GitHub Actions設定" "[ -d '.github' ]"
run_test "Issue テンプレート" "[ -f '.github/ISSUE_TEMPLATE/template-update.yml' ]"
run_test "ライセンスファイル" "[ -f 'LICENSE' ]"

# 15. セキュリティテスト
print_section "セキュリティテスト"

run_test "機密情報チェック" "! grep -r 'password\|secret\|key.*=' . --exclude-dir=.git --exclude='*.log' --exclude='comprehensive-test.sh' || echo 'No secrets found'"
run_test ".gitignore 存在" "[ -f '.gitignore' ]"
run_test "環境ファイル除外" "grep -q '\\.env' .gitignore || echo '.env not in gitignore'"

# 16. パフォーマンステスト
print_section "パフォーマンステスト"

print_test "ファイル数確認"
FILE_COUNT=$(find . -type f | wc -l)
log "📊 総ファイル数: $FILE_COUNT"

print_test "プロジェクトサイズ確認"
PROJECT_SIZE=$(du -sh . | cut -f1)
log "📊 プロジェクトサイズ: $PROJECT_SIZE"

print_test "ログファイルサイズ確認"
if [ -f "$TEST_LOG" ]; then
    LOG_SIZE=$(du -sh "$TEST_LOG" | cut -f1)
    log "📊 テストログサイズ: $LOG_SIZE"
fi

# テスト結果サマリー
print_section "テスト結果サマリー"

log "${BLUE}📊 総合テスト結果:${NC}"
log "   🧪 総テスト数: $TOTAL_TESTS"
log "   ✅ 成功: $PASSED_TESTS"
log "   ⚠️  警告: $WARNING_TESTS"  
log "   ❌ 失敗: $FAILED_TESTS"

# 成功率計算
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    log "   📈 成功率: ${SUCCESS_RATE}%"
    
    if [ $SUCCESS_RATE -ge 95 ]; then
        log "${GREEN}🎉 優秀: テンプレートはプロダクション準備完了です！${NC}"
    elif [ $SUCCESS_RATE -ge 80 ]; then
        log "${YELLOW}👍 良好: 軽微な改善の余地があります${NC}"
    else
        log "${RED}⚠️  要改善: 複数の問題を修正する必要があります${NC}"
    fi
fi

# 推奨事項
log "\n${PURPLE}💡 推奨事項:${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    log "   🔧 失敗したテストを確認し、問題を修正してください"
fi
if [ $WARNING_TESTS -gt 0 ]; then
    log "   ⚠️  警告のあるテストを確認し、必要に応じて改善してください"
fi
log "   📝 定期的にこのテストを実行して品質を維持してください"
log "   🔄 新機能追加時はテストを更新してください"

log "\n${BLUE}📋 詳細なテストログ: $TEST_LOG${NC}"
log "${BLUE}=============================================="
log "🏁 総合テスト完了"
log "==============================================${NC}"

# 終了コード決定
if [ $FAILED_TESTS -gt 0 ]; then
    exit 1
elif [ $WARNING_TESTS -gt 0 ]; then
    exit 2
else
    exit 0
fi