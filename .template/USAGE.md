# AI ハーネス 使用ガイド

AI エージェントハーネスの詳細な使用方法とベストプラクティス。

## 🚀 クイックスタート

### 1. プロジェクトへの導入

```bash
# プロジェクトルートに .ai-guidance をコピー
cp -r /path/to/ai-guidance-template/.ai-guidance ./

# または、GitHub テンプレートからクローン
git clone https://github.com/your-org/ai-guidance-template.git
cp -r ai-guidance-template/.ai-guidance ./your-project/
```

### 2. 基本設定

```yaml
# .ai-guidance/harness.yaml
project:
  name: "my-awesome-project"
  description: "プロジェクトの説明"

# 基本的な設定はそのまま使用可能
# 必要に応じてカスタマイズ
```

### 3. 動作確認

GitHubのCopilot CLI やその他のAIエージェントツールから：

```
「このプロジェクトのコードをレビューして」
→ code_review スキルが自動的に実行される

「コミットメッセージを生成して」
→ commit_message スキルが実行される

「ファイル構造を分析して」
→ file_analyzer スキルが実行される
```

## 📋 基本的な使用パターン

### コードレビュー

```bash
# 変更されたファイルを自動レビュー
git add .
# AIエージェントに「変更をレビューして」
```

自動実行される処理：
1. `git diff --staged` で変更を取得
2. セキュリティ、パフォーマンス、品質を分析
3. 日本語で改善提案を出力

### コミットメッセージ生成

```bash
git add .
# AIエージェントに「コミットメッセージを作成」
```

実行される処理：
1. 変更内容を分析
2. 従来型コミット形式でメッセージ生成
3. 適切なタイプ（feat/fix/docs等）を自動判定

### プロジェクト分析

```bash
# AIエージェントに「プロジェクト全体を分析して」
```

実行される処理：
1. ソースファイルを自動検索
2. 言語別統計、複雑度分析
3. 品質課題の検出とレポート生成

## ⚙️ 設定のカスタマイズ

### プロジェクト固有設定

```yaml
# .ai-guidance/harness.yaml
project:
  name: "your-project-name"
  languages: ["Python", "TypeScript"]  # 主要言語

# スキル設定をカスタマイズ
skills:
  overrides:
    code_review:
      max_line_length: 120      # プロジェクト標準に合わせて調整
      check_security: true      # セキュリティチェック有効化

    file_analyzer:
      max_complexity: 15        # 複雑度の閾値調整
      exclude_patterns:         # 除外パターン追加
        - "*/generated/*"
        - "*/migrations/*"
```

### ミドルウェア設定

```yaml
# ログレベル調整
middleware:
  - name: "logging"
    config:
      log_level: "DEBUG"        # 開発時は DEBUG
      log_to_file: true
      include_prompts: false    # プロンプトをログに含めない

  - name: "security"
    config:
      mask_pii: true           # PII自動マスク
      max_requests_per_minute: 30  # レート制限調整
```

### MCP統合設定

```yaml
# GitHub統合
mcp_servers:
  github:
    enabled: true
    config:
      token: "${GITHUB_TOKEN}"   # 環境変数から取得
      rate_limit: 5000

  # Playwright（ウェブ自動化）
  playwright:
    enabled: false              # 必要時のみ有効化
```

## 🔧 カスタムスキル作成

### 簡単なYAMLスキル

```yaml
# .ai-guidance/skills/my_custom.yaml
name: "my_custom"
description: "カスタムタスクの実行"
triggers:
  - "カスタム実行"
  - "特別処理"

templates:
  report_template: |
    ## {title}

    実行結果: {result}
    実行時間: {duration}
```

### 高度なPythonスキル

```python
# .ai-guidance/skills/deployment.py
from .base import Skill

class DeploymentSkill(Skill):
    def __init__(self, config=None):
        super().__init__({
            'name': 'deployment',
            'triggers': ['デプロイ', 'リリース', '公開'],
            'required_tools': ['bash'],
            **config or {}
        })

    async def execute(self, environment='staging', **kwargs):
        """デプロイメント実行"""

        try:
            # 1. テスト実行
            await self.call_tool('bash', command='npm test')

            # 2. ビルド
            await self.call_tool('bash', command='npm run build')

            # 3. デプロイ
            deploy_cmd = f'npm run deploy:{environment}'
            result = await self.call_tool('bash', command=deploy_cmd)

            self.add_result(f"{environment}環境へのデプロイが完了")

            return {
                'success': True,
                'environment': environment,
                'deploy_result': result
            }

        except Exception as e:
            self.add_error(f"デプロイ失敗: {e}")
            return {'success': False, 'error': str(e)}
```

### カスタムミドルウェア

```python
# .ai-guidance/middleware/notification.py
from .base import BaseMiddleware
import aiohttp

class NotificationMiddleware(BaseMiddleware):
    """Slack通知ミドルウェア"""

    def __init__(self, config):
        super().__init__(config)
        self.webhook_url = config.get('slack_webhook_url')

    async def after_agent(self, result, context):
        """エージェント完了後にSlack通知"""

        if result.get('success') and self.webhook_url:
            message = {
                'text': f"AIエージェント処理完了: {result.get('summary', 'タスク完了')}"
            }

            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=message)

        return result
```

## 📊 監視とデバッグ

### ログの確認

```bash
# ハーネスログ確認
tail -f .ai-guidance/logs/harness.log

# 構造化ログをJSONとして解析
cat .ai-guidance/logs/harness.log | jq '.structured_data'
```

### パフォーマンス分析

ログから自動的に収集されるメトリクス：
- スキル実行時間
- ツール使用統計
- エラー発生率
- メモリ使用量（概算）

### デバッグモード

```yaml
# harness.yaml - デバッグ設定
debug:
  enabled: true
  verbose_logging: true
  save_intermediate_results: true

middleware:
  - name: "logging"
    config:
      log_level: "DEBUG"
      include_prompts: true      # デバッグ時のみ有効化
      include_responses: true
```

## 🔐 セキュリティ設定

### PII保護

```yaml
middleware:
  - name: "security"
    config:
      mask_pii: true
      pii_replacement: "[REDACTED]"

      # カスタムPIIパターン追加
      custom_pii_patterns:
        - pattern: "\\b\\d{4}-\\d{4}-\\d{4}\\b"
          description: "社員番号"
```

### ファイルアクセス制御

```yaml
middleware:
  - name: "security"
    config:
      protected_paths:
        - "/etc/"
        - "/home/user/.ssh/"
        - "config/secrets/"       # プロジェクト固有

      allowed_extensions:
        - ".py"
        - ".js"
        - ".md"
        - ".yaml"
```

### 監査ログ

```python
# セキュリティイベント確認
security_middleware = harness.get_middleware('security')
audit_log = security_middleware.get_audit_log()

for event in audit_log:
    if event['event_type'] == 'security_violation':
        print(f"違反検出: {event['details']}")
```

## 🚀 プロダクション配備

### 本番環境設定

```yaml
# .ai-guidance/harness.yaml (production)
environment: "production"

middleware:
  - name: "logging"
    config:
      log_level: "INFO"          # INFO以上のみ
      log_to_file: true
      include_prompts: false     # 本番では無効化

  - name: "security"
    config:
      mask_pii: true
      max_requests_per_minute: 100

skills:
  loading:
    max_loaded: 5               # メモリ使用量制限
    timeout_seconds: 180        # タイムアウト短縮

# 本番用スキルのみ有効化
enabled_skills:
  - "code_review"
  - "commit_message"

disabled_skills:
  - "debug_analyzer"           # デバッグ用スキルを無効化
```

### 環境変数設定

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# AI_HARNESS_ENV=production  # 本番環境フラグ
AI_HARNESS_LOG_LEVEL=INFO
AI_HARNESS_MAX_PARALLEL=3
```

### CI/CD統合

```yaml
# .github/workflows/ai-harness.yml
name: AI Harness Integration

on:
  pull_request:
    branches: [main]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: AI Code Review
        run: |
          # GitHub Copilot CLI でレビュー実行
          gh copilot suggest "このPRの変更をレビューして"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🎯 ベストプラクティス

### パフォーマンス最適化

```yaml
# 高パフォーマンス設定
skills:
  loading:
    lazy_loading: true          # 遅延ロード有効
    max_loaded: 10             # 適切なキャッシュサイズ

  execution:
    parallel_execution: true    # 並列実行有効
    max_parallel: 5            # CPUコア数に応じて調整
```

### メモリ管理

```python
# スキル内でのメモリ効率化
class EfficientSkill(Skill):
    async def execute(self, large_dataset):
        # ストリーミング処理
        for chunk in self.process_in_chunks(large_dataset):
            result = await self.process_chunk(chunk)
            yield result  # 逐次返却

    def process_in_chunks(self, data, chunk_size=1000):
        """大量データをチャンク単位で処理"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
```

### エラーハンドリング

```python
# 堅牢なエラーハンドリング
class RobustSkill(Skill):
    async def execute(self, **kwargs):
        try:
            result = await self._main_process(**kwargs)
            return {'success': True, 'result': result}

        except ToolNotFoundError as e:
            self.add_error(f"必要ツール未発見: {e}")
            return {'success': False, 'error': 'tool_missing'}

        except TimeoutError as e:
            self.add_error(f"処理タイムアウト: {e}")
            return {'success': False, 'error': 'timeout'}

        except Exception as e:
            self.add_error(f"予期しないエラー: {e}")
            # 部分結果があれば返す
            return {
                'success': False,
                'error': 'unexpected',
                'partial_results': getattr(self, 'partial_results', [])
            }
```

## 🔍 トラブルシューティング

### よくある問題

#### スキルが実行されない

```yaml
# デバッグ設定で原因調査
debug:
  enabled: true
  skill_discovery: true        # スキル発見過程をログ出力

# ログ確認
# "スキル検索" または "skill_discovery" でログ検索
```

#### パフォーマンスが遅い

```bash
# プロファイル情報確認
grep "duration" .ai-guidance/logs/harness.log

# ボトルネックスキル特定
grep "slow_execution" .ai-guidance/logs/harness.log
```

#### メモリ不足

```yaml
# メモリ使用量制限
skills:
  loading:
    max_loaded: 3              # 同時ロード数削減
    memory_limit_mb: 512       # メモリ制限設定
```

### ログ分析

```bash
# エラー分析
grep "ERROR" .ai-guidance/logs/harness.log | tail -10

# セキュリティイベント確認
grep "security_event" .ai-guidance/logs/harness.log

# パフォーマンス分析
awk '/duration/ {sum+=$NF; count++} END {print "平均実行時間:", sum/count}' logs/harness.log
```

## 📚 さらなる学習

### 高度な機能

1. **カスタムMCP統合**: 独自外部ツールの統合
2. **機械学習統合**: 推論結果をスキルで活用
3. **マルチモーダル対応**: 画像・音声データの処理
4. **分散実行**: 複数ノードでの並列処理

### コミュニティリソース

- **GitHubテンプレート**: [ai-guidance-template](https://github.com/your-org/ai-guidance-template)
- **サンプルプロジェクト**: [ai-guidance-examples](https://github.com/your-org/ai-guidance-examples)
- **ベストプラクティス**: [ドキュメント](https://docs.example.com/ai-guidance)

---

このガイドを参考に、プロジェクトに最適なAIエージェントハーネスを構築し、開発生産性を大幅に向上させましょう！

## 🆘 サポート

問題や質問がある場合：
1. まずログファイルを確認
2. デバッグモードで詳細情報収集
3. GitHub Issuesで報告
4. コミュニティフォーラムで質問
