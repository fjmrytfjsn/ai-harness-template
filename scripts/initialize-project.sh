#!/bin/bash

# テンプレート初期化スクリプト
# 新しいプロジェクト作成後に実行してください

set -e

echo "🚀 AI Harness Template 初期化スクリプト"
echo "======================================"

# プロジェクト情報の入力を求める
read -p "プロジェクト名を入力してください: " PROJECT_NAME
read -p "プロジェクトの説明を入力してください: " PROJECT_DESCRIPTION  
read -p "作成者名を入力してください: " AUTHOR_NAME
read -p "リポジトリURL (オプション): " REPOSITORY_URL

echo ""
echo "📝 設定を更新中..."

# harness.yaml の更新
sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" .ai-guidance/harness.yaml
sed -i "s/{{PROJECT_DESCRIPTION}}/$PROJECT_DESCRIPTION/g" .ai-guidance/harness.yaml
sed -i "s/{{AUTHOR_NAME}}/$AUTHOR_NAME/g" .ai-guidance/harness.yaml
sed -i "s|{{REPOSITORY_URL}}|$REPOSITORY_URL|g" .ai-guidance/harness.yaml

# README.md のプロジェクト名を更新
sed -i "1s/.*/# $PROJECT_NAME/" README.md
sed -i "s/AI エージェントハーネス テンプレート/$PROJECT_NAME/g" README.md

# package.json があれば更新
if [ -f "package.json" ]; then
    sed -i "s/\"ai-harness-template\"/\"$PROJECT_NAME\"/g" package.json
    sed -i "s/\"プロダクション対応のAIエージェントハーネス\"/\"$PROJECT_DESCRIPTION\"/g" package.json
fi

echo "✅ 基本設定が完了しました"
echo ""
echo "🔧 次のステップ:"
echo "1. AIプロバイダーを .ai-guidance/harness.yaml で設定"
echo "2. README.md の詳細をカスタマイズ"
echo "3. 不要なファイルを削除"
echo "4. git add . && git commit -m \"feat: プロジェクト初期化\""
echo ""
echo "📚 詳細は SETUP.md を参照してください"
echo ""
echo "Happy Coding! 🎉"