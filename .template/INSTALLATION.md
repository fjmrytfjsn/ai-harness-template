# インストール & セットアップガイド

AIハーネスをプロジェクトに導入するための詳細手順。

## 🎯 対象読者

- AIエージェント（GitHub Copilot CLI等）を使用する開発者
- チームでAI支援開発を標準化したい方
- プロジェクト固有のAI設定を管理したい方

## 📋 前提条件

### 必須要件

- **Git**: バージョン管理
- **AIエージェントツール**: GitHub Copilot CLI、Cursor、またはハーネス対応ツール

### 推奨環境

- **Node.js 18+** (JavaScript/TypeScriptプロジェクト)
- **Python 3.8+** (Pythonプロジェクト)
- **VS Code** + Copilot拡張機能

## 🚀 インストール方法

### 方法1: GitHubテンプレートから（推奨）

```bash
# 新規プロジェクトの場合
gh repo create my-project --template your-org/ai-guidance-template
cd my-project

# 既存プロジェクトに追加
cd your-existing-project
gh repo clone your-org/ai-guidance-template temp-template
cp -r temp-template/.ai-guidance ./
rm -rf temp-template
```

### 方法2: 直接ダウンロード

```bash
# このリポジトリをクローン
git clone https://github.com/your-org/ai-guidance.git

# 必要ファイルをコピー
cp -r ai-guidance/.ai-guidance ./your-project/
cd your-project
```

### 方法3: サブモジュールとして追加

```bash
# サブモジュールとして追加
git submodule add https://github.com/your-org/ai-guidance.git .ai-guidance-source

# シンボリックリンク作成
ln -s .ai-guidance-source/.ai-guidance .ai-guidance
```

## ⚙️ 基本設定

### 1. プロジェクト情報設定

```bash
# .ai-guidance/harness.yaml を編集
vim .ai-guidance/harness.yaml
```

```yaml
# 最低限の設定項目
project:
  name: "your-project-name" # プロジェクト名
  description: "プロジェクトの説明" # 簡潔な説明
  languages: ["Python", "JavaScript"] # 主要使用言語


# 他の設定はデフォルトでOK
```

### 2. 環境変数設定（オプション）

```bash
# .env ファイル作成（プロジェクトルート）
cat > .env << 'EOF'
# GitHub統合（オプション）
GITHUB_TOKEN=ghp_your_token_here

# Slack通知（オプション）
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# ハーネス設定
AI_HARNESS_LOG_LEVEL=INFO
AI_HARNESS_ENV=development
EOF

# .env を .gitignore に追加
echo ".env" >> .gitignore
```

### 3. 動作確認

```bash
# AIエージェント（GitHub Copilot CLI等）で動作確認
# 任意のAIツールから以下のようなプロンプトを試す
```

動作確認プロンプト例：

```
「このプロジェクトの設定を確認して」
→ harness.yaml が正常に読み込まれるかチェック

「ファイル構造を分析して」
→ file_analyzer スキルが動作するかチェック

「READMEのコードをレビューして」
→ code_review スキルが動作するかチェック
```

## 🔧 プロジェクト別カスタマイズ

### Python プロジェクト

```yaml
# .ai-guidance/harness.yaml
project:
  languages: ["Python"]

skills:
  overrides:
    code_review:
      python_specific:
        check_pep8: true
        max_function_length: 50
        check_type_hints: true

    file_analyzer:
      python_config:
        use_ast_analysis: true
        check_imports: true
        detect_unused_imports: true
```

### JavaScript/TypeScript プロジェクト

```yaml
# .ai-guidance/harness.yaml
project:
  languages: ["TypeScript", "JavaScript"]

skills:
  overrides:
    code_review:
      javascript_specific:
        check_eslint_rules: true
        check_typescript_types: true
        detect_console_logs: true

    file_analyzer:
      javascript_config:
        analyze_packages: true
        check_dependencies: true
```

### React プロジェクト

```yaml
# .ai-guidance/harness.yaml
project:
  languages: ["TypeScript", "React"]
  framework: "React"

skills:
  overrides:
    code_review:
      react_specific:
        check_hooks_rules: true
        check_component_patterns: true
        validate_props: true

# React用カスタムスキル有効化
enabled_skills:
  - "code_review"
  - "commit_message"
  - "file_analyzer"
  - "react_component_analyzer" # カスタムスキル
```

## 🛠️ チーム設定

### 共通設定の管理

```bash
# チーム共通の設定を別ファイルで管理
mkdir .ai-guidance/team-configs

# 共通設定
cat > .ai-guidance/team-configs/common.yaml << 'EOF'
# チーム共通のコーディング規約
code_standards:
  max_line_length: 120
  indentation: 2
  require_comments: true

security_rules:
  mask_pii: true
  check_secrets: true

quality_gates:
  max_complexity: 10
  min_test_coverage: 80
EOF
```

### 役割別設定

```yaml
# .ai-guidance/team-configs/roles.yaml
roles:
  frontend_developer:
    enabled_skills:
      - "code_review"
      - "ui_analyzer"
      - "accessibility_check"

  backend_developer:
    enabled_skills:
      - "code_review"
      - "security_analyzer"
      - "performance_check"

  devops_engineer:
    enabled_skills:
      - "deployment"
      - "infrastructure_check"
      - "security_scan"
```

## 📊 監視・ログ設定

### 開発環境

```yaml
# .ai-guidance/harness.yaml (development)
environment: "development"

debug:
  enabled: true
  verbose_logging: true

middleware:
  - name: "logging"
    config:
      log_level: "DEBUG"
      log_to_file: true
      log_file_path: ".ai-guidance/logs/debug.log"
      include_prompts: true # 開発時のみ
```

### 本番環境

```yaml
# .ai-guidance/harness.yaml (production)
environment: "production"

debug:
  enabled: false

middleware:
  - name: "logging"
    config:
      log_level: "INFO"
      log_to_file: true
      log_file_path: "/var/log/ai-harness/production.log"
      include_prompts: false # セキュリティのため無効化

  - name: "security"
    config:
      strict_mode: true
      audit_all_actions: true
```

## 🔐 セキュリティ設定

### 基本的なセキュリティ

```yaml
# .ai-guidance/harness.yaml
middleware:
  - name: "security"
    config:
      # PII保護
      mask_pii: true

      # ファイルアクセス制限
      protected_paths:
        - "/etc/"
        - ".env*"
        - "secrets/"
        - "keys/"

      # 危険コマンドブロック
      block_dangerous_commands: true

      # レート制限
      max_requests_per_minute: 60
```

### 企業環境向け設定

```yaml
# .ai-guidance/harness.yaml (enterprise)
middleware:
  - name: "security"
    config:
      # 監査ログ
      audit_log_enabled: true
      audit_log_path: "/var/log/ai-harness/audit.log"

      # 外部通信制限
      allowed_domains:
        - "api.github.com"
        - "your-company-api.com"

      # 機密データ検出
      sensitive_data_patterns:
        - pattern: "\\bAPI_KEY_\\w+"
          replacement: "[API_KEY_MASKED]"
        - pattern: "password\\s*=\\s*['\"][^'\"]+['\"]"
          replacement: 'password="[MASKED]"'
```

## 🧪 テスト・検証

### 設定テスト

```bash
# 設定ファイルの構文チェック
python -c "
import yaml
with open('.ai-guidance/harness.yaml') as f:
    config = yaml.safe_load(f)
    print('✅ 設定ファイルの構文OK')
"

# スキルロードテスト
python -c "
import sys, os
sys.path.append('.ai-guidance/skills')
try:
    from base import Skill
    from code_review import CodeReviewSkill
    print('✅ スキル読み込みOK')
except Exception as e:
    print(f'❌ スキル読み込みエラー: {e}')
"
```

### 動作テストスクリプト

```bash
#!/bin/bash
# test-setup.sh

echo "🧪 AI ハーネス設定テスト開始"

# 1. 必須ファイル存在確認
echo "📁 ファイル存在確認..."
required_files=(
    ".ai-guidance/harness.yaml"
    ".ai-guidance/skills/code_review.py"
    ".ai-guidance/skills/commit_message.yaml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file が見つかりません"
        exit 1
    fi
done

# 2. 設定ファイル検証
echo "⚙️ 設定ファイル検証..."
python -c "
import yaml
try:
    with open('.ai-guidance/harness.yaml') as f:
        config = yaml.safe_load(f)
    print('✅ YAML設定ファイル正常')
except Exception as e:
    print(f'❌ 設定ファイルエラー: {e}')
    exit(1)
"

# 3. 権限確認
echo "🔐 ファイル権限確認..."
if [[ -r ".ai-guidance/harness.yaml" ]]; then
    echo "✅ 設定ファイル読み込み権限OK"
else
    echo "❌ 設定ファイルの読み込み権限不足"
fi

echo "🎉 設定テスト完了！"
```

## 🔄 アップデート

### マイナーアップデート

```bash
# テンプレートの最新版を取得
git remote add ai-guidance-upstream https://github.com/your-org/ai-guidance.git
git fetch ai-guidance-upstream

# 差分確認
git diff HEAD ai-guidance-upstream/main -- .ai-guidance/

# 必要な変更のみマージ
git checkout ai-guidance-upstream/main -- .ai-guidance/skills/new_skill.py
```

### メジャーアップデート

```bash
# 現在の設定をバックアップ
cp -r .ai-guidance .ai-guidance.backup.$(date +%Y%m%d)

# 新バージョンのテンプレート取得
git clone https://github.com/your-org/ai-guidance.git ai-guidance-new

# 設定を移行（手動で確認しながら）
diff -u .ai-guidance/harness.yaml ai-guidance-new/.ai-guidance/harness.yaml

# カスタム設定を新しい形式に移行
# migration スクリプトがある場合
python ai-guidance-new/tools/migrate-config.py .ai-guidance/harness.yaml
```

## 🆘 トラブルシューティング

### よくある問題

#### 「スキルが見つからない」エラー

```bash
# スキルディレクトリの確認
ls -la .ai-guidance/skills/

# 権限確認
ls -la .ai-guidance/skills/*.py

# Python パス確認
python -c "
import sys
import os
sys.path.insert(0, '.ai-guidance/skills')
print('Python path:', sys.path)
try:
    import base
    print('✅ base module imported')
except ImportError as e:
    print('❌ Import error:', e)
"
```

#### 設定が反映されない

```bash
# 設定ファイル構文チェック
python -m yaml .ai-guidance/harness.yaml

# 設定読み込みログ確認
grep -i "config" .ai-guidance/logs/harness.log | tail -5

# キャッシュクリア（該当する場合）
rm -rf .ai-guidance/.cache/
```

#### パフォーマンス問題

```bash
# ログサイズ確認
du -h .ai-guidance/logs/

# 古いログの削除
find .ai-guidance/logs/ -name "*.log" -mtime +7 -delete

# 設定でログレベルを調整
sed -i 's/DEBUG/INFO/g' .ai-guidance/harness.yaml
```

---

このガイドに従って設定することで、プロジェクトに最適なAIハーネス環境を構築できます。

問題が発生した場合は、ログファイルを確認し、必要に応じてGitHubのissueで報告してください。
