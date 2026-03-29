# 🚨 緊急時対応ガイド - プロバイダー未設定 / 401エラー

## 前提: デフォルトではプロバイダー未設定

このテンプレートはデフォルトでプロバイダーが未設定です。OpenCode Web を使用するには、以下のいずれかを設定してください。

## 🎯 即座に実行できる解決策

### 解決策1: OpenAI API を使用（最も簡単・確実）

```bash
# 1. OpenAI API キーを設定
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
EOF

# 2. プロバイダー設定を変更
sed -i 's/default: null/default: "openai"/' .ai-guidance/opencode-integration.yaml

# 3. OpenCode Web を再起動
# VS Code の「PORTS」タブ → ポート3000 → 再読み込み
```

### 解決策2: ローカル LLM を使用（オフライン・無料）

```bash
# 1. Ollama をインストール・起動
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# 2. 軽量なコーディングモデルをダウンロード
ollama pull deepseek-coder:6.7b

# 3. プロバイダー設定変更
sed -i 's/default: null/default: "ollama"/' .ai-guidance/opencode-integration.yaml

# Ollamaプロバイダー詳細を追加
cat >> .ai-guidance/opencode-integration.yaml << 'EOF'

  # Ollama ローカル LLM 設定
  ollama:
    name: "Ollama Local"
    base_url: "http://localhost:11434"
    models: ["deepseek-coder:6.7b"]
    auth: "none"
EOF
```

### 解決策3: Personal Access Token 設定（GitHub 機能最大活用）

```bash
# 1. GitHub で Personal Access Token を作成
# https://github.com/settings/tokens
# 必要スコープ: repo, copilot, read:user

# 2. 環境変数設定
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_personal_access_token_here
EOF

# 3. プロバイダー設定変更
sed -i 's/default: null/default: "github-copilot"/' .ai-guidance/opencode-integration.yaml

# 4. GitHub CLI で認証
gh auth login --with-token < .env

# 5. Copilot API 有効確認
gh api user/copilot/billing
```

## 📊 設定確認

```bash
# OpenCode Web が起動しているか確認
curl -s http://localhost:3000/health || echo "OpenCode Web が起動していません"

# 設定ファイル確認
cat .ai-guidance/opencode-integration.yaml

# 環境変数確認
env | grep -E "(OPENAI|GITHUB|OLLAMA)"

# プロセス確認
ps aux | grep -E "(opencode|ollama)"
```

## 🔄 動作テスト

```bash
# AI Harness スキルのテスト実行
python .ai-guidance/skills/code_review.py --test

# OpenCode Web API テスト
curl -X POST http://localhost:3000/api/complete \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "model": "test"}'
```

## 💡 トラブルシューティング

### ポート3000が使用中の場合

```bash
# プロセス確認・終了
sudo lsof -ti:3000 | xargs kill -9

# 別ポートで起動
npx opencode-ai web --port 3001 &
```

### 依存関係エラーの場合

```bash
# Node.js 依存関係の再インストール
npm install -g opencode-ai@latest

# Python 依存関係の再インストール
pip install -r .ai-guidance/requirements.txt
```

### DevContainer 環境の問題

```bash
# 完全リビルド
# Ctrl+Shift+P → "Dev Containers: Rebuild Container"

# または手動セットアップ
./.devcontainer/start-services.sh
```

## ✅ 正常動作の確認

以下が全て OK なら正常に動作しています：

1. **OpenCode Web アクセス**: http://localhost:3000 でUIが表示される
2. **AI レスポンス**: プロンプト入力でAIからの回答が返る
3. **AI Harness 統合**: カスタムコマンドが利用可能
4. **エラーなし**: ブラウザコンソールにエラーが出ない

---

**詳細ドキュメント**: [OpenCode Integration Guide](.template/docs/OPENCODE_INTEGRATION.md)

**📝 このファイルについて**: このQUICK_FIX.mdはテンプレート固有のガイドファイルです。プロバイダー設定が完了したら削除してかまいません。

```bash
rm QUICK_FIX.md
git add . && git commit -m "cleanup: Remove template guide file"
```
