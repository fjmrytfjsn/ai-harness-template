#!/bin/bash

# テンプレート初期化スクリプト
# 新しいプロジェクト作成後に実行してください

set -e

echo "🚀 AI Harness Template 初期化スクリプト"
echo "======================================"

# 自動初期化モードかどうかの判定
if [ "$AUTO_INIT_MODE" = "true" ]; then
    echo "🤖 自動初期化モードで実行します..."
    
    PROJECT_NAME="${DEFAULT_PROJECT_NAME:-ai-harness-project}"
    PROJECT_DESCRIPTION="${DEFAULT_DESCRIPTION:-AI Harness プロジェクト}"
    AUTHOR_NAME="${DEFAULT_AUTHOR_NAME:-Developer}"
    REPOSITORY_URL="${DEFAULT_REPOSITORY_URL:-}"
    
    echo "📋 自動設定値:"
    echo "   プロジェクト名: $PROJECT_NAME"
    echo "   説明: $PROJECT_DESCRIPTION"
    echo "   作成者: $AUTHOR_NAME"
    echo "   リポジトリURL: $REPOSITORY_URL"
    echo ""
    
else
    # 対話モード：ユーザー入力を求める
    read -p "プロジェクト名を入力してください: " PROJECT_NAME
    read -p "プロジェクトの説明を入力してください: " PROJECT_DESCRIPTION  
    read -p "作成者名を入力してください: " AUTHOR_NAME
    read -p "リポジトリURL (オプション): " REPOSITORY_URL
    echo ""
fi

echo "📝 設定を更新中..."

# harness.yaml の更新
if [ -f ".ai-guidance/harness.yaml" ]; then
    sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" .ai-guidance/harness.yaml
    sed -i "s/{{PROJECT_DESCRIPTION}}/$PROJECT_DESCRIPTION/g" .ai-guidance/harness.yaml
    sed -i "s/{{AUTHOR_NAME}}/$AUTHOR_NAME/g" .ai-guidance/harness.yaml
    
    if [ -n "$REPOSITORY_URL" ]; then
        sed -i "s|{{REPOSITORY_URL}}|$REPOSITORY_URL|g" .ai-guidance/harness.yaml
    else
        # リポジトリURLが空の場合はプレースホルダーを削除
        sed -i "/{{REPOSITORY_URL}}/d" .ai-guidance/harness.yaml
    fi
fi

# README.md のプロジェクト名を更新
if [ -f "README.md" ]; then
    sed -i "1s/.*/# $PROJECT_NAME/" README.md
    sed -i "s/AI エージェントハーネス テンプレート/$PROJECT_NAME/g" README.md
fi

# package.json があれば更新
if [ -f "package.json" ]; then
    sed -i "s/\"ai-harness-template\"/\"$PROJECT_NAME\"/g" package.json
    sed -i "s/\"プロダクション対応のAIエージェントハーネス\"/\"$PROJECT_DESCRIPTION\"/g" package.json
fi

# pyproject.toml があれば更新
if [ -f "pyproject.toml" ]; then
    sed -i "s/name = \"ai-harness-template\"/name = \"$PROJECT_NAME\"/g" pyproject.toml
    sed -i "s/description = \"プロダクション対応のAIエージェントハーネス\"/description = \"$PROJECT_DESCRIPTION\"/g" pyproject.toml
fi

# テンプレート固有のファイルをクリーンアップ
if [ "$AUTO_INIT_MODE" = "true" ]; then
    echo "🧹 テンプレートファイルをクリーンアップ中..."
    
    # テンプレート説明ファイル削除
    rm -f TEMPLATE_CLEANUP.md 2>/dev/null || true
    rm -f QUICK_FIX.md 2>/dev/null || true
    
    # Gitコミット履歴の初期化（オプション）
    if [ -d ".git" ] && [ "$RESET_GIT_HISTORY" = "true" ]; then
        echo "📝 Git履歴をリセット中..."
        rm -rf .git
        git init
        git add .
        git commit -m "feat: プロジェクト初期化

AI Harness テンプレートから $PROJECT_NAME を作成

📋 プロジェクト情報:
- 名前: $PROJECT_NAME  
- 説明: $PROJECT_DESCRIPTION
- 作成者: $AUTHOR_NAME

🚀 利用可能機能:
- OpenCode Web 統合
- AI Harness スキルシステム
- 動的ミドルウェア
- GitHub MCP 統合"
    fi
fi

echo "✅ 初期化が完了しました!"
echo ""

if [ "$AUTO_INIT_MODE" = "true" ]; then
    echo "🎯 環境準備完了:"
    echo "   ✅ プロジェクト設定済み"
    echo "   ✅ AI Harness 利用可能"
    echo "   ⚠️  AI プロバイダー未設定"
    echo ""
    echo "📱 利用開始前の設定:"
    echo "   1. QUICK_FIX.md で AI プロバイダーを設定"
    echo "   2. VS Code の 'PORTS' タブからポート3000にアクセス"
    echo "   3. OpenCode Web でAIコーディング開始"
    echo "   4. カスタムスキルが自動利用可能"
else
    echo "🔧 次のステップ:"
    echo "1. QUICK_FIX.md で AI プロバイダーを設定（必須）"
    echo "2. README.md の詳細をカスタマイズ"  
    echo "3. 不要なファイルを削除"
    echo "4. git add . && git commit -m \"feat: プロジェクト初期化\""
    echo ""
    echo "📚 詳細は SETUP.md を参照してください"
fi

echo ""
echo "Happy Coding! 🎉"