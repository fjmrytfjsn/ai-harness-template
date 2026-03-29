# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## 🚀 このプロジェクトについて

このプロジェクトは AI Harness Template から作成されており、以下の機能が利用可能です：

- 🤖 **AI エージェントハーネス** - 次世代のハーネスエンジニアリング基盤
- 📈 **リアルタイム Dashboard** - プロジェクト監視・メトリクス表示
- 🛡️ **ミドルウェアスタック** - セキュリティ・ログ・パフォーマンス
- 🔧 **動的スキルシステム** - コードレビュー・ファイル解析
- 🌐 **OpenCode Web統合** - ブラウザベース AI 開発環境

## ⚠️ 初期設定が必要です

**AI プロバイダーの設定**:
このプロジェクトを使用するには、AIプロバイダーの設定が必要です。

📖 **設定手順**: `QUICK_FIX.md` を参照してください

## 🛠️ 開発開始

### 1. AI プロバイダー設定

```bash
# OpenAI を使用する場合（推奨）
echo "OPENAI_API_KEY=sk-your-key" > .env
sed -i 's/default: null/default: "openai"/' .ai-guidance/opencode-integration.yaml
```

### 2. OpenCode Web 起動

- VS Code の「PORTS」タブ → ポート3000
- ブラウザで OpenCode Web にアクセス
- AI 支援付きコーディング開始

### 3. AI Harness 機能

- **🔍 Code Review**: 高度なコード分析
- **📝 Commit Message**: 適切なコミットメッセージ生成
- **📊 File Analysis**: ファイル品質メトリクス

## 📊 AI Harness Dashboard

```bash
# Dashboard 起動
./scripts/dashboard.sh start

# ブラウザで http://localhost:8080 にアクセス
# リアルタイムメトリクス・ログ・システム状態を監視
```

## 📁 プロジェクト構造

```
{{PROJECT_NAME}}/
├── .ai-guidance/          # AI Harness 設定・スキル・ミドルウェア
├── .devcontainer/         # 開発環境設定
├── scripts/               # ユーティリティスクリプト
└── src/                   # プロジェクトソースコード（追加してください）
```

## 🔧 カスタマイズ

### AI Harness 設定

`.ai-guidance/harness.yaml` でプロジェクト固有の設定をカスタマイズできます：

```yaml
project:
  name: "{{PROJECT_NAME}}"
  description: "{{PROJECT_DESCRIPTION}}"

harness:
  middleware_enabled: true
  skills_enabled: true
  auto_review: false # 必要に応じて true に
```

### 新しいスキルの追加

```bash
# スキル作成例
cp .ai-guidance/skills/code_review.py .ai-guidance/skills/my_skill.py
# my_skill.py をカスタマイズ
```

## 🧪 テスト・ビルド・デプロイ

```bash
# TODO: プロジェクト固有のコマンドを追加
npm test      # テスト実行
npm build     # ビルド
npm deploy    # デプロイ
```

## 📚 ドキュメント

- [OpenCode Web 統合ガイド](.ai-guidance/docs/opencode-integration.md)
- [スキル開発ガイド](.ai-guidance/docs/skills-development.md)
- [ミドルウェア設定](.ai-guidance/docs/middleware-config.md)

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下でライセンスされています。

## 🎉 AI Harness Template について

このプロジェクトは [AI Harness Template](https://github.com/fjmrytfjsn/ai-harness-template) から作成されました。

最新機能・アップデート情報は元テンプレートリポジトリを参照してください。

---

**Happy Coding!** 🚀
