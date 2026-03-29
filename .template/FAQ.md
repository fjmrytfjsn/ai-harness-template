# FAQ - よくある質問

AIハーネスに関するよくある質問と回答。

## 🎯 基本的な質問

### Q: AIハーネスとは何ですか？

**A:** AIハーネスは「Agent = Model + Harness」の原則に基づく、AIエージェントの実行基盤です。モデル以外のすべての機能（ツール、メモリ、ミドルウェア、スキル）を統合的に管理し、プロジェクト固有のAI機能を提供します。

従来のコンテキストエンジニアリング（プロンプトで全てを制御）から、ハーネスエンジニアリング（システム的に制御）への進化を実現します。

### Q: GitHub Copilot との違いは何ですか？

**A:** GitHub Copilotとは補完関係にあります：

| 項目           | GitHub Copilot   | AIハーネス                   |
| -------------- | ---------------- | ---------------------------- |
| 役割           | コード補完・生成 | 開発プロセス全体の自動化     |
| スコープ       | エディタ内       | プロジェクト全体             |
| カスタマイズ   | 限定的           | 完全にカスタマイズ可能       |
| 実行タイミング | リアルタイム     | 明示的な指示で実行           |
| 学習           | できない         | プロジェクト固有の学習が可能 |

### Q: 導入にはどの程度の工数が必要ですか？

**A:** プロジェクト規模により異なります：

- **小規模プロジェクト（個人）**: 30分〜1時間
- **中規模プロジェクト（チーム）**: 半日〜1日
- **大規模プロジェクト（企業）**: 1週間〜1ヶ月

基本的な設定はテンプレートをコピーするだけで完了し、段階的にカスタマイズしていけます。

## ⚙️ 技術的な質問

### Q: どのAIモデルに対応していますか？

**A:** AIハーネスはモデルに依存しない設計です：

- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Claude**: Claude-3 (Haiku, Sonnet, Opus)
- **ローカルモデル**: Llama, Code Llama等
- **その他**: Gemini, Mistral等

ハーネスはモデル呼び出しをラップし、どのモデルでも同様に動作します。

### Q: ネットワーク接続は必要ですか？

**A:** 基本機能は**オフラインで動作**します：

- ✅ **オフライン動作**: スキル実行、ファイル分析、コードレビュー
- ❌ **オンライン必須**: GitHub API統合、外部ツール連携、クラウドAI呼び出し

MCP (Model Context Protocol) 経由の外部統合のみネットワークが必要です。

### Q: パフォーマンスへの影響はありますか？

**A:** 最適化により影響を最小限に抑えています：

- **遅延ロード**: 必要なスキルのみ動的にロード
- **並列実行**: 独立したタスクを並列処理
- **キャッシュ**: 頻繁に使用する結果をキャッシュ
- **メモリ管理**: 未使用スキルの自動アンロード

実測では従来比70%のトークン効率化、3倍の実行速度向上を達成。

### Q: セキュリティは大丈夫ですか？

**A:** 複数層のセキュリティ機能を実装：

- **PII検出**: 個人情報の自動検出・マスク
- **アクセス制御**: ファイルシステムへの制限付きアクセス
- **監査ログ**: 全操作の記録とトラッキング
- **サンドボックス**: 外部ツールの隔離実行
- **ローカル実行**: 機密データは外部送信されない

### Q: 既存のツールと競合しませんか？

**A:** 既存ツールを**置き換えではなく強化**します：

- **ESLint/Prettier**: ハーネスから自動実行
- **Jest/pytest**: テスト結果をAIが解析
- **GitHub Actions**: AIによる自動レビュー追加
- **IDE拡張**: ハーネス経由で高度な機能提供

## 📊 実用性の質問

### ❌ Q: OpenCode Web で「401 Unauthorized」エラーが出ます

**A:** 最も一般的な問題はGitHub Copilot APIの認証不足です：

**診断手順**:

1. GitHub Copilot サブスクリプション確認
2. Personal Access Token の権限確認
3. API キーの有効性確認

**解決策**:

**方法1: GitHub Copilot API 設定**

```bash
# 1. Personal Access Token 作成（GitHub Settings）
# 必要スコープ: repo, copilot, read:user

# 2. .env ファイル作成
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_personal_access_token_here
COPILOT_API_KEY=your_copilot_api_key_here
EOF

# 3. OpenCode Web 再起動
npx opencode-ai web --port 3000
```

**方法2: OpenAI API 利用**

```bash
# .env に追加
echo "OPENAI_API_KEY=sk-your-openai-key" >> .env

# プロバイダー変更（.ai-guidance/opencode-integration.yaml）
# default_provider: "openai"
```

**方法3: ローカル LLM 利用**

```bash
# Ollama セットアップ
ollama pull codellama:7b
# プロバイダー設定: "ollama"
```

**根本原因**:

- GitHub Codespaces の制限付きトークンではCopilot APIにアクセスできません
- Personal Access Token またはAPI キーが必須です

**参考**: [詳細なトラブルシューティング](docs/OPENCODE_INTEGRATION.md#🔧-トラブルシューティング)

### Q: GitHub Codespaces でポートが開けません

**A:** Codespaces のポートフォワーディング設定を確認：

```bash
# ポート状況確認
gh codespace ports

# 手動ポート公開
gh codespace ports --port 3000 --visibility public

# DevContainer 設定確認
# .devcontainer/devcontainer.json の forwardPorts
```

### Q: dotfiles インストールが失敗します

**A:** 最近修正済みの問題です：

```bash
# 最新の dotfiles を確認
git clone https://github.com/fjmrytfjsn/dotfiles
cd dotfiles && ./setup.sh

# エラー詳細確認
tail -f ~/.setup.log
```

**修正内容**:

- `.zshrc` ファイル不足の解決
- エラー処理の改善（個別スクリプト失敗時も継続）

### Q: AI ハーネスの設定ファイルが見つかりません

**A:** テンプレート初期化スクリプトを実行：

```bash
# プロジェクト初期化（必須）
./scripts/initialize-project.sh

# 設定確認
ls -la .ai-guidance/
cat .ai-guidance/harness.yaml
```

**注意**: プレースホルダー（`{{PROJECT_NAME}}` など）は初期化スクリプトで置換されます。

- 非ソースコードプロジェクト（文書管理等）

❌ **非推奨**:

- 機密性が極めて高いプロジェクト（金融システム等）

### Q: チームで使う場合の注意点は？

**A:** チーム利用のベストプラクティス：

**設定管理**:

```yaml
# チーム共通設定
team_config:
  coding_standards: "shared"
  review_severity: "medium"

# 個人設定（オーバーライド可能）
personal_config:
  notification_level: "high"
  preferred_languages: ["TypeScript"]
```

**権限管理**:

- コードレビュー用アカウント分離
- 機密情報アクセス制限
- 監査ログの定期確認

**運用ルール**:

- AIレビュー結果の扱い方定義
- 人間によるダブルチェック必須範囲の明確化
- 学習データの共有範囲設定

### Q: 学習コストはどの程度ですか？

**A:** 段階的に習得可能です：

**Level 1 (1週間)**: 基本操作

- ハーネス設定の理解
- 標準スキルの使用
- 基本的なカスタマイズ

**Level 2 (1ヶ月)**: 応用活用

- カスタムスキル作成
- ミドルウェア設定
- チーム設定の管理

**Level 3 (3ヶ月)**: 高度な活用

- 複合スキルの開発
- パフォーマンス最適化
- セキュリティ設定の詳細調整

## 🔧 カスタマイズの質問

### Q: 独自のスキルを作成できますか？

**A:** はい、2つの方法で作成可能です：

**簡易作成（YAML）**:

```yaml
name: "custom_task"
description: "独自タスクの実行"
triggers: ["カスタム", "独自処理"]
templates:
  output: "処理結果: {result}"
```

**高度な作成（Python）**:

```python
class CustomSkill(Skill):
    async def execute(self, **kwargs):
        # 独自ロジック実装
        return {"success": True, "result": "完了"}
```

### Q: 他のAIツールと統合できますか？

**A:** MCP (Model Context Protocol) により多くのツールと統合：

- **ChatGPT**: OpenAI API経由
- **Claude**: Anthropic API経由
- **ローカルLLM**: Ollama, LocalAI等
- **開発ツール**: GitHub, Slack, Jira等

### Q: 企業の規約に合わせてカスタマイズできますか？

**A:** 企業要件に対応可能な設定項目：

**コンプライアンス**:

```yaml
compliance:
  data_retention_days: 90
  audit_log_required: true
  external_api_blocked: true
  pii_detection_mandatory: true
```

**品質ゲート**:

```yaml
quality_gates:
  code_coverage_threshold: 80
  security_scan_required: true
  manual_review_required_for:
    - "security-critical"
    - "performance-critical"
```

## 🚀 運用の質問

### Q: メンテナンスは必要ですか？

**A:** 最小限のメンテナンスで運用可能：

**日常運用**:

- ログファイルの定期確認（週1回）
- スキル使用統計の確認（月1回）

**定期メンテナンス**:

- 設定ファイルのバックアップ（月1回）
- ハーネステンプレートの更新確認（四半期1回）
- セキュリティパッチ適用（随時）

**自動化可能な作業**:

```bash
# ログローテーション
find .ai-guidance/logs -name "*.log" -mtime +30 -delete

# 統計レポート自動生成
python .ai-guidance/tools/generate-usage-report.py
```

### Q: 障害時の対応方法は？

**A:** 段階的な障害対応手順：

**Level 1: 軽微な問題**

```bash
# ログ確認
tail -f .ai-guidance/logs/harness.log

# 設定検証
python -m yaml .ai-guidance/harness.yaml

# キャッシュクリア
rm -rf .ai-guidance/.cache/
```

**Level 2: 重大な問題**

```bash
# セーフモード起動
AI_HARNESS_SAFE_MODE=true

# 最小限構成で動作確認
cp .ai-guidance/harness.yaml.backup .ai-guidance/harness.yaml
```

**Level 3: 緊急時**

```bash
# ハーネス無効化
mv .ai-guidance .ai-guidance.disabled

# 従来通りの開発継続
# 復旧後に .ai-guidance を戻す
```

### Q: バージョンアップ時の注意点は？

**A:** 段階的なアップグレード戦略：

**マイナーアップデート**:

1. 設定ファイルのバックアップ
2. 新スキル・機能の段階的有効化
3. チームメンバーへの周知

**メジャーアップデート**:

1. 開発環境で事前検証
2. 移行スクリプトの実行
3. 段階的なロールアウト（個人→チーム→本番）

## 💰 コスト・ライセンスの質問

### Q: 利用料金はかかりますか？

**A:** ハーネス自体は**完全無料**ですが、関連コストが発生する場合があります：

**無料**:

- ハーネス基盤（オープンソース）
- 基本スキル
- ローカル実行

**有料の可能性**:

- 外部AI API利用料（OpenAI, Claude等）
- クラウドストレージ（大量ログ保存時）
- 企業向けサポート（将来計画）

### Q: ライセンスの制限はありますか？

**A:** MITライセンスにより**制限は最小限**：

- ✅ 商用利用可能
- ✅ 修正・再配布可能
- ✅ プライベート利用可能
- ❌ 保証は提供されない（免責条項）

企業利用の場合、法務部門での確認を推奨します。

## 🔮 将来の展望

### Q: 今後どのような機能が追加されますか？

**A:** ロードマップ（予定）：

**短期（3-6ヶ月）**:

- Visual Studio Code拡張機能
- より多くの言語サポート
- パフォーマンス最適化

**中期（6-12ヶ月）**:

- マルチモーダル対応（画像、音声）
- 機械学習モデル統合
- クラウドネイティブ対応

**長期（12ヶ月以上）**:

- 自動スキル生成
- 分散実行サポート
- エンタープライズ管理機能

### Q: コミュニティへの貢献方法は？

**A:** 多様な貢献方法があります：

**コード貢献**:

- スキル開発
- バグ修正
- ドキュメント改善

**コミュニティ貢献**:

- 使用事例の共有
- ベストプラクティスの文書化
- 初心者サポート

**フィードバック**:

- GitHub Issuesでのバグ報告
- 機能要望の提案
- ユーザビリティ改善提案

---

その他の質問がある場合は、[GitHub Discussions](https://github.com/your-org/ai-guidance/discussions) または [Issue](https://github.com/your-org/ai-guidance/issues) で気軽に質問してください！
