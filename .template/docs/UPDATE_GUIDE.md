# Template Update Guide - テンプレートアップデートガイド

## 🎯 Overview - 概要

AI Harness Template から作成したプロジェクトを、安全に最新版に更新する完全ガイドです。

## 🚀 Quick Start - クイックスタート

### 基本的な更新フロー

```bash
# 1. 更新確認
./scripts/update-template.sh check

# 2. 更新実行（自動バックアップ付き）
./scripts/update-template.sh update

# 3. 結果確認
./scripts/update-template.sh status
```

## 📋 事前準備 - Prerequisites

### ✅ 必須チェックリスト

- [ ] 全ての変更をコミット済み
- [ ] 作業ブランチから main/master に移動
- [ ] 重要な設定ファイルのバックアップ
- [ ] インターネット接続が安定

### 🔍 準備コマンド

```bash
# 作業状態確認
git status

# 未コミットがあればコミット
git add .
git commit -m "feat: update前の作業保存"

# メインブランチに移動
git checkout main
```

## 🔄 更新方法 - Update Methods

### Method 1: 自動更新（推奨）

**完全自動でリスクが最小:**

```bash
# アップデート実行
./scripts/update-template.sh update
```

**実行内容:**

1. 📋 Git状態チェック
2. 🔗 テンプレートリモート設定
3. ⬇️ 最新版取得
4. 💾 自動バックアップ作成
5. 🔀 インテリジェントマージ
6. ✅ 更新適用

### Method 2: 段階的更新

**より慎重にステップバイステップ:**

```bash
# 1. 更新チェックのみ
./scripts/update-template.sh check

# 2. 詳細な変更内容確認
git log --oneline --graph template/main

# 3. 手動でバックアップ作成（オプション）
cp .ai-guidance/harness.yaml .ai-guidance/harness.yaml.backup

# 4. 更新実行
./scripts/update-template.sh update
```

### Method 3: 手動マージ

**高度なカスタマイズがある場合:**

```bash
# 1. テンプレートリモート追加
git remote add template https://github.com/fjmrytfjsn/ai-harness-template.git

# 2. 最新版取得
git fetch template main

# 3. マージブランチ作成
git checkout -b template-merge

# 4. 手動マージ
git merge template/main --no-ff

# 5. 競合解決（必要に応じて）
# VS Code等で競合マーカーを編集

# 6. マージ完了
git commit
git checkout main
git merge template-merge --no-ff
```

## 🛡️ 安全機能 - Safety Features

### 自動バックアップ

```bash
# バックアップ内容
.template-backups/
├── backup_20241226_143022/
│   ├── .ai-guidance/harness.yaml
│   ├── README.md
│   ├── .env
│   └── custom_files.txt
└── latest_backup.txt

# バックアップから復元
./scripts/update-template.sh rollback backup_20241226_143022
```

### 競合検出

システムが自動的に競合の可能性をチェック:

- `.ai-guidance/harness.yaml` - プロジェクト設定
- `README.md` - プロジェクト説明
- `.devcontainer/devcontainer.json` - 環境設定
- カスタマイズしたスキルファイル

### 保護されるファイル

以下は更新時に**保護**され、上書きされません:

- プロジェクト固有の設定
- `.env` 環境変数
- `*.custom.*` パターンのファイル
- `*.local.*` パターンのファイル

## 🔧 カスタマイズの保持 - Preserving Customizations

### 設定ファイル

```yaml
# .ai-guidance/harness.yaml
project:
  name: "my-custom-project" # ← 保持される
  description: "カスタム説明" # ← 保持される

harness:
  # 新機能が自動追加される
  new_feature: true # ← 自動追加

  # 既存設定は保持
  middleware: ["custom"] # ← 保持される
```

### カスタムスキル

```python
# .ai-guidance/skills/my_custom_skill.py
# ← このファイルは完全に保持される

# 一方、テンプレートのスキルは更新される:
# .ai-guidance/skills/code_review.py ← 最新版に更新
```

### ドキュメント

```markdown
# README.md

# My Project ← プロジェクト名は保持

## Custom Section ← カスタム章は保持

...

## Template Features ← テンプレート部分は更新

...
```

## 📊 更新内容の確認 - Reviewing Updates

### 変更内容の確認

```bash
# アップデート前に変更内容確認
./scripts/update-template.sh check

# 詳細なコミット履歴
git log --oneline --graph template/main

# ファイル別の差分
git diff HEAD template/main -- .ai-guidance/
```

### 主な更新カテゴリ

#### 🆕 新機能追加

- 新しいスキルの追加
- Dashboard の機能拡張
- OpenCode Web の新機能対応

#### 🐛 バグ修正

- 認証エラーの解決
- パフォーマンスの改善
- 互換性の向上

#### 🔒 セキュリティ更新

- 依存関係の更新
- セキュリティホールの修正
- ベストプラクティスの適用

#### 📚 ドキュメント改善

- 使用方法の明確化
- トラブルシューティング追加
- FAQ の更新

## 🚨 トラブルシューティング - Troubleshooting

### 競合が発生した場合

```bash
# 競合ファイルの確認
git status

# VS Code で競合解決
code <競合ファイル>

# 解決後にコミット
git add .
git commit -m "resolve: テンプレート更新の競合を解決"

# 更新完了処理
./scripts/update-template.sh complete
```

### 更新に失敗した場合

```bash
# 1. 現在の状態確認
git status
git branch

# 2. 更新ブランチにいる場合は中断
git checkout main
git branch -D template-update

# 3. バックアップから復元
./scripts/update-template.sh rollback

# 4. 再試行
./scripts/update-template.sh update
```

### よくある問題と解決策

#### "未コミットの変更があります"

```bash
# 作業を保存
git stash push -m "更新前の一時保存"

# 更新実行
./scripts/update-template.sh update

# 作業を復元
git stash pop
```

#### "テンプレートリモートが見つかりません"

```bash
# 手動でリモート追加
git remote add template https://github.com/fjmrytfjsn/ai-harness-template.git

# 再実行
./scripts/update-template.sh update
```

#### "ネットワークエラー"

```bash
# プロキシ設定確認
git config --global http.proxy

# GitHub接続テスト
curl -I https://github.com

# 再試行
./scripts/update-template.sh check
```

## 📈 更新後の検証 - Post-Update Validation

### 動作確認チェックリスト

```bash
# ✅ 基本機能確認
./scripts/dashboard.sh status
./scripts/initialize-project.sh --help

# ✅ OpenCode Web 起動確認
npx opencode-ai web --version

# ✅ AI Harness 設定確認
cat .ai-guidance/harness.yaml

# ✅ 依存関係確認
pip list | grep aiohttp
npm list -g opencode-ai
```

### パフォーマンステスト

```bash
# Dashboard起動時間測定
time ./scripts/dashboard.sh start

# メモリ使用量確認
./scripts/dashboard.sh status

# ログエラー確認
./scripts/dashboard.sh logs | grep -i error
```

## 🔄 定期更新の推奨 - Recommended Update Schedule

### 個人開発プロジェクト

- **月1回**: 機能更新とセキュリティパッチ
- **即座**: 重大なセキュリティ修正

### チーム開発プロジェクト

- **四半期ごと**: 計画的な機能更新
- **月1回**: セキュリティ更新のチェック
- **即座**: 重大なバグ修正

### プロダクション環境

- **半年ごと**: メジャーアップデート
- **月1回**: セキュリティパッチ確認
- **テスト環境で先行検証**: 本番適用前の十分な検証

## 🤝 コミュニティサポート - Community Support

### ヘルプの取得

- 📖 **Documentation**: [docs/](docs/) ディレクトリ
- 🐛 **Issues**: GitHub Issues で問題報告
- 💬 **Discussions**: GitHub Discussions で質問
- 📧 **Direct**: メンテナーへの直接連絡

### 貢献方法

- 🔧 **Bug Reports**: 問題の詳細報告
- 💡 **Feature Requests**: 新機能の提案
- 📝 **Documentation**: ドキュメントの改善
- 🧪 **Testing**: 新バージョンのテスト

---

**更新で困ったときは**: [GitHub Issues](https://github.com/fjmrytfjsn/ai-harness-template/issues) でサポートを受けられます！
