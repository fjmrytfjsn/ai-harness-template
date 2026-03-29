# AI エージェントハーネス テンプレート

**プロダクション対応AIエージェントハーネス** - 次世代のハーネスエンジニアリング基盤

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Japanese](https://img.shields.io/badge/Language-Japanese-red.svg)](https://github.com/fjmrytfjsn/ai-harness-template)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com/fjmrytfjsn/ai-harness-template)

## 🎯 このテンプレートについて

このテンプレートから、**Agent = Model + Harness** 原則に基づく最新のAIエージェント基盤を即座に構築できます。

従来のコンテキストエンジニアリングから**ハーネスエンジニアリング**へ。プロジェクト固有のAI機能を高速・安全・効率的に実現します。

## ⚡ クイックスタート

### 1. このテンプレートを使用

**GitHub Web UI（推奨）:**
1. [Use this template](https://github.com/fjmrytfjsn/ai-harness-template) ボタンをクリック
2. 新しいリポジトリ名を入力
3. "Create repository from template" をクリック
4. **"Open in Codespaces"** をクリック（自動セットアップ開始）

### 2. 初期設定（1分で完了）

Codespaces起動後、以下が自動実行されます：
- ✅ プロジェクト設定・初期化
- ✅ 依存関係インストール  
- ✅ OpenCode Web 起動
- ⚠️ **AI プロバイダー設定が必要** → `QUICK_FIX.md` 参照

### 3. AIプロバイダー設定

```bash
# OpenAI使用（最も簡単）
echo "OPENAI_API_KEY=sk-your-key" > .env
sed -i 's/default: null/default: "openai"/' .ai-guidance/opencode-integration.yaml
```

### 4. 即座に利用開始

- 📱 VS Code「PORTS」タブ → ポート3000でOpenCode Web
- 🤖 AI支援コーディング開始
- 📊 ポート8080でDashboard監視

## ✨ 主な機能

### 🤖 AI エージェントハーネス
- **動的スキルシステム**: コードレビュー・ファイル解析・コミットメッセージ生成
- **ミドルウェアスタック**: セキュリティ・ログ・パフォーマンス
- **MCP統合**: GitHub/Playwright等の標準化ツール連携

### 📊 リアルタイム監視
- **AI Harness Dashboard**: システム状態・メトリクス・ログ
- **プロジェクト分析**: ファイル構造・依存関係・品質指標
- **パフォーマンス追跡**: レスポンス時間・使用量・エラー率

### 🌐 OpenCode Web 統合
- **ブラウザベース開発**: VS Code不要の AI コーディング
- **マルチプロバイダー対応**: OpenAI/Anthropic/Ollama/GitHub Copilot
- **カスタムコマンド**: プロジェクト固有AI機能の統合

### 🔄 安全な更新システム
- **テンプレート更新**: 新機能の自動取り込み
- **バックアップ・ロールバック**: 安全な実験環境
- **競合解決**: インテリジェントなマージ戦略

## 📋 詳細ドキュメント

テンプレート使用後、詳細ガイドは `.template/` ディレクトリ内で確認できます：

- 📖 [インストールガイド](.template/INSTALLATION.md)
- 🛠️ [使用方法](.template/USAGE.md)
- ❓ [FAQ](.template/FAQ.md)
- 📊 [Dashboard ガイド](.template/docs/DASHBOARD.md)
- 🔧 [OpenCode統合](.template/docs/OPENCODE_INTEGRATION.md)

## 🛡️ セキュリティ・プライバシー

- 🔒 **PII検出**: 個人情報の自動フィルタリング
- 🛡️ **セキュアミドルウェア**: 入力検証・出力サニタイズ
- 📝 **ログ管理**: センシティブ情報の適切な除外
- 🔑 **認証**: 各プロバイダーの安全な認証フロー

## 🌟 企業・チーム利用

- 👥 **マルチユーザー対応**: チーム開発環境
- 📊 **使用量追跡**: コスト管理・分析
- 🔧 **カスタマイズ**: 企業固有要件への対応
- 🚀 **スケーラビリティ**: 大規模プロジェクト対応

## 🤝 コミュニティ・サポート

- 💬 **Issues**: バグ報告・機能要望
- 📢 **Discussions**: 使用方法・ベストプラクティス
- 🔄 **Pull Requests**: 機能改善・修正の貢献
- 📖 **Wiki**: コミュニティドキュメント

## 📄 ライセンス

MIT License - 商用利用・再配布・改変すべて自由

---

🚀 **今すぐ始める**: [Use this template](https://github.com/fjmrytfjsn/ai-harness-template) → Codespaces → 1分でAI開発環境完成！