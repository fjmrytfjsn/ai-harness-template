# 🚀 セットアップガイド

このテンプレートから新しいプロジェクトを作成した後、以下の手順に従って設定してください。

## ⚡ クイックスタート（5分で完了）

### 0. 開発環境の選択

**🚀 GitHub Codespaces（推奨）:**

- ブラウザだけで完結
- OpenCode Web 自動起動
- 設定済み AI Harness 環境

**💻 ローカル Dev Container:**

- VS Code + Docker 環境
- 同等の機能をローカルで実行

**⚙️ 手動セットアップ:**

- 既存環境にインストール

### 1. プロジェクト情報の設定

`.ai-guidance/harness.yaml` を編集：

```yaml
project:
  name: "your-project-name" # ← プロジェクト名
  description: "あなたのプロジェクトの説明" # ← プロジェクト説明
  authors: ["Your Name"] # ← 作成者名
  repository: "https://github.com/username/repo" # ← リポジトリURL
```

### 2. README.md の更新

`README.md` の以下を変更：

- プロジェクトタイトル
- 機能説明
- 使用方法
- 連絡先情報

### 3. AI プロバイダーの設定

プロジェクトで使用するAIサービスを選択：

#### GitHub Copilot

```yaml
ai:
  provider: "github-copilot"
  model: "gpt-4"
```

#### OpenAI

```yaml
ai:
  provider: "openai"
  model: "gpt-4o"
```

#### Anthropic Claude

```yaml
ai:
  provider: "anthropic"
  model: "claude-3.5-sonnet"
```

### 4. スキルのカスタマイズ

`.ai-guidance/skills/` でプロジェクト固有のスキルを追加・編集：

- `code_review.py` - コードレビュー規則
- `commit_message.yaml` - コミットメッセージフォーマット
- カスタムスキルの追加

### 5. セキュリティ設定

`.ai-guidance/middleware/security.py` で：

- PII検出パターン
- アクセス制御ルール
- 組織固有のセキュリティポリシー

## 🛠️ 詳細設定

### DevContainer 統合機能

このテンプレートには **OpenCode Web** 統合DevContainerが含まれており、以下が自動で設定されます：

#### 🚀 自動起動サービス

- **OpenCode Web**: ポート3000で自動起動
- **AI Harness**: 設定済み環境
- **Python + Node.js**: 必要な実行環境

#### 🔧 プリインストール済み

- OpenCode AI CLI
- GitHub Copilot 拡張機能
- Python AI 関連ライブラリ
- YAML/JSON エディタ支援

#### 📱 ポートフォワーディング

- `3000`: OpenCode Web UI
- `8000`: AI Harness Dashboard（オプション）

#### ⚙️ 環境変数

```bash
OPENCODE_AUTO_START=true        # 自動起動有効
AI_HARNESS_ENV=development      # 開発環境モード
PYTHONPATH=.ai-guidance         # Python パス設定
```

### プロジェクト固有設定

```yaml
# .ai-guidance/harness.yaml
project_settings:
  # 開発環境
  development:
    debug_mode: true
    log_level: "DEBUG"

  # 本番環境
  production:
    debug_mode: false
    log_level: "INFO"
    enable_monitoring: true
```

### GitHub 設定

#### Issues & PR テンプレート

- `.github/ISSUE_TEMPLATE/` - カスタマイズ
- `.github/pull_request_template.md` - PR規則

#### Actions 設定

- `.github/workflows/` - CI/CDパイプライン追加

### ドキュメント更新

1. `USAGE.md` - 使用方法ガイド
2. `INSTALLATION.md` - インストール手順
3. `FAQ.md` - よくある質問
4. `CONTRIBUTING.md` - コントリビューションガイド（オプション）

## ✅ 設定完了チェックリスト

- [ ] プロジェクト名・説明を更新
- [ ] AIプロバイダーを設定
- [ ] README.md をカスタマイズ
- [ ] 不要なファイルを削除
- [ ] GitHub設定を確認
- [ ] 初回コミット・プッシュ実行

## 🚀 次のステップ

設定完了後：

1. `gh copilot suggest` または対応AIツールでテスト
2. プロジェクト固有のスキル開発
3. チーム設定・権限管理
4. 本格的な開発開始！

## 📞 サポート

質問や問題があれば：

- [Issues](https://github.com/fjmrytfjsn/ai-harness-template/issues) で報告
- [Discussions](https://github.com/fjmrytfjsn/ai-harness-template/discussions) で相談

**Happy Coding! 🎉**
