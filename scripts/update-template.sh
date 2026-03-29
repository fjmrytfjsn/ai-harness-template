#!/bin/bash

# AI Harness Template アップデート管理スクリプト
# テンプレートの最新版を安全に取り込む

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_REMOTE="https://github.com/fjmrytfjsn/ai-harness-template.git"
TEMPLATE_BRANCH="main"
UPDATE_BRANCH="template-update"
BACKUP_DIR=".template-backups"

cd "$PROJECT_ROOT"

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=============================================="
    echo -e "🔄 AI Harness Template Update Manager"
    echo -e "==============================================${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_git_status() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        print_error "このディレクトリはGitリポジトリではありません"
        exit 1
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "未コミットの変更があります"
        echo ""
        git status --short
        echo ""
        read -p "続行しますか？ (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "アップデートをキャンセルしました"
            exit 0
        fi
    fi
}

setup_template_remote() {
    print_info "テンプレートリモートを設定中..."
    
    if ! git remote get-url template > /dev/null 2>&1; then
        git remote add template "$TEMPLATE_REMOTE"
        print_success "テンプレートリモートを追加: $TEMPLATE_REMOTE"
    else
        git remote set-url template "$TEMPLATE_REMOTE"
        print_success "テンプレートリモートを更新: $TEMPLATE_REMOTE"
    fi
}

fetch_template_updates() {
    print_info "テンプレートの最新版を取得中..."
    git fetch template "$TEMPLATE_BRANCH"
    print_success "最新版の取得完了"
}

check_updates_available() {
    local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "")
    local template_commit=$(git rev-parse template/$TEMPLATE_BRANCH 2>/dev/null || echo "")
    
    if [ -z "$template_commit" ]; then
        print_error "テンプレートの取得に失敗しました"
        return 1
    fi
    
    # テンプレートからの最新の共通祖先を確認
    local merge_base=$(git merge-base HEAD template/$TEMPLATE_BRANCH 2>/dev/null || echo "")
    
    if [ "$merge_base" = "$template_commit" ]; then
        print_success "テンプレートは最新版です"
        return 1
    fi
    
    print_info "利用可能なアップデートがあります"
    
    # 変更内容を表示
    echo ""
    print_info "テンプレートでの変更内容:"
    git log --oneline --decorate --graph $merge_base..template/$TEMPLATE_BRANCH 2>/dev/null || true
    echo ""
    
    return 0
}

create_backup() {
    print_info "現在の設定をバックアップ中..."
    
    mkdir -p "$BACKUP_DIR"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_name="backup_${timestamp}"
    
    # 重要なファイルをバックアップ
    local backup_files=(
        ".ai-guidance/harness.yaml"
        "README.md"
        ".env"
        "package.json"
        "pyproject.toml"
    )
    
    mkdir -p "$BACKUP_DIR/$backup_name"
    
    for file in "${backup_files[@]}"; do
        if [ -f "$file" ]; then
            mkdir -p "$BACKUP_DIR/$backup_name/$(dirname "$file")"
            cp "$file" "$BACKUP_DIR/$backup_name/$file"
            print_success "バックアップ: $file"
        fi
    done
    
    # カスタムファイルリストも作成
    find . -name "*.custom.*" -o -name "*.local.*" > "$BACKUP_DIR/$backup_name/custom_files.txt" 2>/dev/null || true
    
    echo "$backup_name" > "$BACKUP_DIR/latest_backup.txt"
    print_success "バックアップ完了: $BACKUP_DIR/$backup_name"
}

detect_conflicts() {
    print_info "競合の可能性をチェック中..."
    
    # カスタマイズされやすいファイル
    local sensitive_files=(
        ".ai-guidance/harness.yaml"
        "README.md" 
        "scripts/initialize-project.sh"
        ".devcontainer/devcontainer.json"
    )
    
    local conflicts=()
    
    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            # ファイルがテンプレートから変更されているかチェック
            if ! git diff --quiet HEAD template/$TEMPLATE_BRANCH -- "$file" 2>/dev/null; then
                conflicts+=("$file")
            fi
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        print_warning "以下のファイルで競合が発生する可能性があります:"
        for file in "${conflicts[@]}"; do
            echo "  - $file"
        done
        echo ""
        return 0
    else
        print_success "競合は検出されませんでした"
        return 1
    fi
}

create_update_branch() {
    print_info "アップデート用ブランチを作成中..."
    
    # 既存のアップデートブランチがあれば削除
    if git branch | grep -q "$UPDATE_BRANCH"; then
        git branch -D "$UPDATE_BRANCH" 2>/dev/null || true
    fi
    
    git checkout -b "$UPDATE_BRANCH"
    print_success "ブランチ '$UPDATE_BRANCH' を作成"
}

merge_template_updates() {
    print_info "テンプレートの変更をマージ中..."
    
    # テンプレート固有のファイルを除外するマージ戦略
    local exclude_files=(
        "README.md"
        ".git*"
        "TEMPLATE_CLEANUP.md"
        "QUICK_FIX.md"
    )
    
    # カスタマージを実行
    if git merge template/$TEMPLATE_BRANCH --no-commit --no-ff; then
        print_success "自動マージ完了"
        
        # 除外ファイルの処理
        for file in "${exclude_files[@]}"; do
            if [ -f "$file" ]; then
                git checkout HEAD -- "$file" 2>/dev/null || true
            fi
        done
        
        git add .
        git commit -m "feat: テンプレートアップデートをマージ

🔄 AI Harness Template からの更新を統合

📋 更新内容:
$(git log --oneline $(git merge-base HEAD template/$TEMPLATE_BRANCH)..template/$TEMPLATE_BRANCH | head -5)

🛡️ 保護されたファイル:
- プロジェクト固有設定は保持
- カスタマイズ内容は維持
- 競合の自動解決

Co-authored-by: Template Update <template-update@ai-harness.com>"

        print_success "マージコミット作成完了"
        return 0
    else
        print_warning "手動での競合解決が必要です"
        return 1
    fi
}

show_manual_merge_help() {
    print_info "手動マージのヘルプ:"
    echo ""
    echo "1. 競合ファイルを確認:"
    echo "   git status"
    echo ""
    echo "2. 競合を解決:"
    echo "   - VS Code等で競合マーカーを編集"
    echo "   - 必要な変更を統合"
    echo ""
    echo "3. 解決後にコミット:"
    echo "   git add ."
    echo "   git commit"
    echo ""
    echo "4. このスクリプトで完了処理:"
    echo "   $0 complete"
}

apply_updates() {
    print_info "アップデートを適用中..."
    
    local current_branch=$(git branch --show-current)
    
    if [ "$current_branch" != "$UPDATE_BRANCH" ]; then
        print_error "アップデートブランチにいません: $current_branch"
        exit 1
    fi
    
    # 元のブランチに戻ってマージ
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || {
        print_error "メインブランチに戻れませんでした"
        exit 1
    }
    
    git merge "$UPDATE_BRANCH" --no-ff
    git branch -d "$UPDATE_BRANCH"
    
    print_success "アップデート適用完了"
}

restore_backup() {
    local backup_name="$1"
    
    if [ -z "$backup_name" ] && [ -f "$BACKUP_DIR/latest_backup.txt" ]; then
        backup_name=$(cat "$BACKUP_DIR/latest_backup.txt")
    fi
    
    if [ -z "$backup_name" ] || [ ! -d "$BACKUP_DIR/$backup_name" ]; then
        print_error "バックアップが見つかりません: $backup_name"
        exit 1
    fi
    
    print_info "バックアップを復元中: $backup_name"
    
    # バックアップからファイルを復元
    find "$BACKUP_DIR/$backup_name" -type f | while read backup_file; do
        relative_path=${backup_file#$BACKUP_DIR/$backup_name/}
        if [ "$relative_path" != "custom_files.txt" ]; then
            mkdir -p "$(dirname "$relative_path")"
            cp "$backup_file" "$relative_path"
            print_success "復元: $relative_path"
        fi
    done
}

show_status() {
    print_info "テンプレートアップデート状況:"
    echo ""
    
    if git remote get-url template > /dev/null 2>&1; then
        print_success "テンプレートリモート: $(git remote get-url template)"
        
        # 最後の取得日時
        local last_fetch=$(stat -c %y .git/FETCH_HEAD 2>/dev/null | cut -d' ' -f1 || echo "未取得")
        echo "最後の更新チェック: $last_fetch"
        
        # 現在の状態
        if git rev-parse template/$TEMPLATE_BRANCH > /dev/null 2>&1; then
            local commits_behind=$(git rev-list --count HEAD..template/$TEMPLATE_BRANCH 2>/dev/null || echo "0")
            if [ "$commits_behind" -gt 0 ]; then
                print_warning "$commits_behind 個のアップデートが利用可能です"
            else
                print_success "最新版です"
            fi
        fi
    else
        print_warning "テンプレートリモートが設定されていません"
    fi
    
    # バックアップ状況
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A "$BACKUP_DIR")" ]; then
        echo ""
        print_info "利用可能なバックアップ:"
        ls -lt "$BACKUP_DIR" | grep "^d" | head -5 | while read line; do
            backup_name=$(echo "$line" | awk '{print $NF}')
            backup_date=$(echo "$line" | awk '{print $6, $7, $8}')
            echo "  - $backup_name ($backup_date)"
        done
    fi
}

case "${1:-help}" in
    "check")
        print_header
        setup_template_remote
        fetch_template_updates
        check_updates_available
        ;;
        
    "update")
        print_header
        check_git_status
        setup_template_remote
        fetch_template_updates
        
        if check_updates_available; then
            create_backup
            create_update_branch
            
            if detect_conflicts; then
                print_warning "競合が検出されました。慎重に進めます。"
                read -p "続行しますか？ (y/N): " -n 1 -r
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    git checkout main 2>/dev/null || git checkout master
                    git branch -D "$UPDATE_BRANCH" 2>/dev/null || true
                    print_info "アップデートをキャンセルしました"
                    exit 0
                fi
            fi
            
            if merge_template_updates; then
                apply_updates
                print_success "🎉 テンプレートアップデート完了!"
            else
                show_manual_merge_help
                print_warning "手動での競合解決が必要です"
            fi
        fi
        ;;
        
    "complete")
        print_header
        if [ "$(git branch --show-current)" = "$UPDATE_BRANCH" ]; then
            apply_updates
            print_success "🎉 アップデート完了!"
        else
            print_error "アップデートブランチにいません"
        fi
        ;;
        
    "rollback")
        print_header
        backup_name="${2:-}"
        restore_backup "$backup_name"
        print_success "ロールバック完了"
        ;;
        
    "status")
        print_header
        show_status
        ;;
        
    "clean")
        print_header
        if [ -d "$BACKUP_DIR" ]; then
            print_warning "古いバックアップを削除しますか？"
            echo "削除対象: $BACKUP_DIR"
            read -p "続行しますか？ (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$BACKUP_DIR"
                print_success "バックアップディレクトリを削除しました"
            fi
        else
            print_info "削除するバックアップはありません"
        fi
        ;;
        
    "help"|*)
        echo "AI Harness Template Update Manager"
        echo ""
        echo "使用方法:"
        echo "  $0 <コマンド> [オプション]"
        echo ""
        echo "コマンド:"
        echo "  check     利用可能なアップデートをチェック"
        echo "  update    テンプレートをアップデート（自動バックアップ付き）"
        echo "  complete  手動マージ後の完了処理"
        echo "  rollback  バックアップから復元 [backup_name]"
        echo "  status    現在のアップデート状況表示"
        echo "  clean     古いバックアップを削除"
        echo "  help      このヘルプを表示"
        echo ""
        echo "例:"
        echo "  $0 check                    # アップデート確認"
        echo "  $0 update                   # アップデート実行"
        echo "  $0 rollback backup_20240101 # 指定バックアップから復元"
        echo ""
        echo "安全な使用方法:"
        echo "1. 作業内容をコミット"
        echo "2. '$0 check' でアップデート確認"
        echo "3. '$0 update' でアップデート実行"
        echo "4. 問題があれば '$0 rollback' で復元"
        ;;
esac