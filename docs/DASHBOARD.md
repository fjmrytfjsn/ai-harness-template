# AI Harness Dashboard ガイド

## 🎯 概要

AI Harness Dashboard は、AI エージェント環境をリアルタイムで監視・管理するWebベースの管理ツールです。

## 🚀 起動方法

### 自動起動（推奨）
DevContainer/Codespaces 環境では自動的に起動されます。

### 手動起動
```bash
# Dashboard起動
./scripts/dashboard.sh start

# 状態確認
./scripts/dashboard.sh status

# ブラウザでアクセス
./scripts/dashboard.sh open
```

## 📊 機能一覧

### システム状態監視
- **稼働時間**: ハーネスの連続稼働時間
- **リクエスト数**: 処理されたAI リクエストの総数
- **エラー率**: 失敗したリクエストの割合
- **メモリ使用量**: プロセスのメモリ消費量

### ハーネス情報
- **利用可能スキル数**: `.ai-guidance/skills/` 配下のスキル数
- **アクティブミドルウェア数**: 有効なミドルウェアコンポーネント数
- **コンテキストサイズ**: 最大トークン数設定
- **MCP統合数**: 連携している外部サービス数

### パフォーマンスメトリクス
- **平均レスポンス時間**: AIモデル呼び出しの応答速度
- **CPU使用率**: プロセッサー負荷
- **スループット**: 単位時間当たりの処理数

### アクティビティログ
- **リアルタイムログ**: 全操作の時系列記録
- **エラー追跡**: 発生した問題の詳細
- **スキル使用履歴**: どのスキルがいつ使用されたか

## 🌐 アクセス方法

### Codespaces環境
1. VS Code の **PORTS** タブを開く
2. **ポート 8000** の行を見つける
3. **"Open in Browser"** をクリック

### ローカル環境
ブラウザで `http://localhost:8000` にアクセス

## 🔧 管理コマンド

```bash
# 起動
./scripts/dashboard.sh start

# 停止
./scripts/dashboard.sh stop

# 再起動
./scripts/dashboard.sh restart

# 状態確認
./scripts/dashboard.sh status

# ログ表示（最新50行）
./scripts/dashboard.sh logs

# ログ表示（最新100行）
./scripts/dashboard.sh logs 100

# ブラウザで開く
./scripts/dashboard.sh open
```

## 📈 活用方法

### 開発時の監視
- **スキル使用頻度**: よく使うスキルを把握
- **パフォーマンス**: 重いタスクの特定
- **エラー分析**: 問題のあるコードやプロンプトの特定

### プロダクション運用
- **稼働状況監視**: 24/7でのシステム安定性確認
- **リソース管理**: メモリ・CPU使用量の最適化
- **トラブルシューティング**: 問題の迅速な発見と対応

### チーム開発
- **使用統計共有**: チーム内でのAI活用状況把握
- **ベストプラクティス**: 効果的なスキルやワークフローの共有

## 🛠️ カスタマイズ

### 設定変更
Dashboard の設定は `.ai-guidance/harness.yaml` で管理：

```yaml
dashboard:
  enabled: true
  port: 8000
  update_interval: 5  # 秒
  retention_days: 30  # ログ保持期間
```

### メトリクス拡張
独自のメトリクスを追加したい場合：

```python
# .ai-guidance/dashboard.py を編集
def get_custom_metrics(self):
    return {
        'custom_metric': self.calculate_custom_value(),
        'business_kpi': self.get_business_kpi()
    }
```

## 🔍 トラブルシューティング

### Dashboard が起動しない
```bash
# 依存関係確認
pip install aiohttp aiohttp-cors psutil

# ポート確認
netstat -tlnp | grep 8000

# ログ確認
./scripts/dashboard.sh logs
```

### データが表示されない
```bash
# 設定ファイル確認
cat .ai-guidance/harness.yaml

# 権限確認
ls -la .ai-guidance/
```

### パフォーマンス問題
```bash
# メモリ使用量確認
./scripts/dashboard.sh status

# プロセス状況確認  
ps aux | grep dashboard
```

## 🔒 セキュリティ

- Dashboard は**ローカルネットワーク**でのみアクセス可能
- 本番環境では**リバースプロキシ**での認証を推奨
- 機密データは**ログに記録されません**

## 🚀 パフォーマンス最適化

- **WebSocket**: リアルタイム更新で効率的な通信
- **メモリ管理**: 不要なデータの自動クリーンアップ  
- **非同期処理**: ブロッキングを避けたスムーズな動作