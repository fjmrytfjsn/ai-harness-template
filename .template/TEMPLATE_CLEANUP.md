# このファイルをテンプレート作成後に削除してください

テンプレートから新しいプロジェクトを作成した後は、以下のファイルが不要になります：

## 🗑️ 削除対象ファイル

```bash
# テンプレート関連ファイル（プロジェクトでは不要）
rm -f TEMPLATE_CLEANUP.md
rm -f docs/EXAMPLES.md         # 必要に応じて保持
rm -f scripts/initialize-project.sh  # 初期化完了後は不要

# GitHub テンプレート設定（プロジェクトでは不要）
rm -f .github/template.yml
```

## ✅ 保持すべきファイル

```
.ai-guidance/           # ハーネス設定 - 必須
├── harness.yaml        # メイン設定
├── skills/             # スキル定義
├── middleware/         # ミドルウェア
└── mcp/                # 外部ツール連携

docs/                   # ドキュメント
├── README.md           # プロジェクト説明
├── SETUP.md            # セットアップガイド
├── USAGE.md            # 使用方法
├── INSTALLATION.md     # インストール手順
└── FAQ.md              # よくある質問

.github/                # GitHub設定
├── ISSUE_TEMPLATE/     # Issue テンプレート
├── pull_request_template.md  # PR テンプレート
└── README.md           # GitHub設定説明

LICENSE                 # ライセンス
```

## 🔧 初期化後のタスク

1. **プロジェクト設定の更新**
   - `.ai-guidance/harness.yaml` のプロジェクト情報
   - `README.md` のタイトルと説明

2. **不要ファイルの削除**

   ```bash
   rm TEMPLATE_CLEANUP.md
   ```

3. **Git コミット**

   ```bash
   git add .
   git commit -m "feat: テンプレートからプロジェクト初期化"
   ```

4. **AI プロバイダー設定**
   - GitHub Copilot / OpenAI / Anthropic 等の選択
   - API キーの設定

5. **プロジェクト固有のカスタマイズ**
   - スキルの追加・修正
   - ミドルウェア設定
   - セキュリティポリシー

## 📚 参考資料

初期化後は以下を参照：

- `SETUP.md` - 詳細なセットアップ手順
- `docs/EXAMPLES.md` - 設定例集
- `USAGE.md` - 使用方法ガイド

Happy Coding! 🎉
