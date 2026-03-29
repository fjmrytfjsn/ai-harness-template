# エージェントメモリシステム

エージェントセッション間での永続的な知識と学習。

## メモリタイプ

### 作業メモリ

現在のコンテキストウィンドウ - ハーネスが自動管理：

- 会話履歴
- アクティブなツール出力
- 現在のタスク状態
- ロードされたスキルとそのコンテキスト

### セッションメモリ

現在のセッション用の一時的な知識：

- ユーザー設定
- プロジェクト発見事項
- 中間結果
- タスク進捗

### 永続メモリ

セッション間での長期知識：

- **facts.md** - プロジェクトについての検証済み情報
- **patterns.md** - 観察されたパターンとテンプレート
- **decisions.md** - 過去の決定とその理由
- **skills_learned.md** - このプロジェクトで開発されたカスタムスキル

## メモリ管理

### 自動メモリ永続化

ハーネスが重要な情報を自動的に保存：

```python
# memory/middleware が自動的にキャプチャ:
- コード分析中に発見された重要な事実
- ユーザー設定と構成選択
- 成功したパターンとワークフロー
- 行われた決定とその推論
```

### 手動メモリ管理

明示的に情報をメモリに保存可能：

```python
# スキルやミドルウェア内で
await self.memory.save_fact(
    "project_uses_typescript",
    "このプロジェクトは主にTypeScriptとReactを使用"
)

await self.memory.save_pattern(
    "testing_pattern",
    "テストはソースファイルの隣の __tests__ ディレクトリに配置"
)

await self.memory.save_decision(
    "code_style_choice",
    "Prettierを2スペースインデントで使用することに決定",
    reasoning="チームの好みと既存コードベースの一貫性"
)
```

### メモリ検索

メモリは自動的にロードされ、エージェントコンテキストで利用可能：

```python
# スキル内で自動的に利用可能
project_info = self.memory.get_facts()
past_decisions = self.memory.get_decisions()
learned_patterns = self.memory.get_patterns()

# コンテキスト対応検索
relevant_info = self.memory.search("認証パターン")
```

## メモリ構造

```
memory/
├── facts.md              # 検証済みプロジェクト情報
├── patterns.md           # コードパターンとテンプレート
├── decisions.md          # 過去の決定と理由
├── skills_learned.md     # 開発されたカスタムスキル
├── user_preferences.md   # ユーザー設定
└── project_context.md    # 高レベルプロジェクト理解
```

## メモリファイルの例

### facts.md

```markdown
# プロジェクト事実

## アーキテクチャ

- **フレームワーク**: TypeScript付きReact
- **状態管理**: Redux Toolkit
- **スタイリング**: Tailwind CSS
- **テスト**: Jest + React Testing Library

## ファイル構造

- コンポーネントは `src/components/` に
- テストは `__tests__/` ディレクトリに
- ユーティリティは `src/utils/` に
- APIレイヤーは `src/services/` に

## 依存関係

- Node.js 18+
- パッケージマネージャー: npm
- ビルドツール: Vite
```

### patterns.md

```markdown
# 観察されたパターン

## コンポーネントパターン

- フック付き関数コンポーネント
- 同じファイルで定義されたPropsインターフェース
- 名前付きタイプエクスポート付きデフォルトエクスポート

## テストパターン

- コンポーネント毎に1つのテストファイル
- `data-testid` 属性を使用したテストID
- `__mocks__/` での外部依存関係のモック

## インポートパターン

- ローカルファイルには相対インポート
- パスマッピングを使用した `src/` からの絶対インポート
- サードパーティインポートが最初、次にローカルインポート
```

### decisions.md

```markdown
# 過去の決定

## コードスタイル (2024-03-28)

**決定**: Prettierを2スペースインデントと末尾カンマで使用
**理由**: 既存のコードベースとチームの好みに合致
**影響**: 全ファイルでの一貫したフォーマット

## 認証戦略 (2024-03-25)

**決定**: リフレッシュトークンローテーション付きJWTを実装
**理由**: セキュリティとパフォーマンスのバランス
**検討した代替案**: セッションベース認証（スケーリング懸念で却下）
**影響**: 全APIエンドポイントでbearer token認証が必要
```

## スキルとのメモリ統合

スキルは自動的にメモリコンテキストにアクセス：

```python
# skills/code_review.py
class CodeReviewSkill(Skill):
    async def execute(self, files=None):
        # メモリが自動的にロード
        project_patterns = self.memory.get_patterns()
        past_decisions = self.memory.get_decisions()

        # メモリを使用してレビューに情報提供
        for file_path in files:
            # 既知のパターンに対してチェック
            if self.violates_established_patterns(file_path, project_patterns):
                self.add_issue("パターン違反を検出")

            # 過去の決定を参照
            if self.conflicts_with_decisions(file_path, past_decisions):
                self.add_issue("以前のアーキテクチャ決定と競合")
```

## メモリ学習

エージェントは自動的にメモリを学習・更新：

```python
# 成功したタスク完了後
class MemoryLearningMiddleware:
    async def after_agent(self, result, context):
        """成功した相互作用から学習"""

        if result.success:
            # 新しいパターンを抽出
            patterns = self.extract_patterns(context.actions)
            for pattern in patterns:
                await self.memory.save_pattern(pattern)

            # 成功したワークフローを保存
            if context.was_complex_task():
                workflow = self.extract_workflow(context)
                await self.memory.save_skill_template(workflow)

            # プロジェクト理解を更新
            new_facts = self.extract_facts(result.outputs)
            for fact in new_facts:
                await self.memory.save_fact(fact)
```

## 設定

メモリ動作は harness.yaml で設定：

```yaml
# harness.yaml
memory:
  persistence: "filesystem"
  base_path: "./memory/"

  # 自動学習設定
  auto_save_facts: true
  auto_save_patterns: true
  auto_save_decisions: true

  # メモリ制限
  max_facts: 1000
  max_patterns: 500
  max_decisions: 200

  # 保持ポリシー
  retention_days: 90 # 古いメモリの自動クリーンアップ

  # 検索と検索
  enable_semantic_search: false # ベクターデータベースが必要
  similarity_threshold: 0.7
```

## パフォーマンス考慮事項

- **遅延ローディング**: スキル実行中にオンデマンドでメモリをロード
- **キャッシング**: 頻繁にアクセスされるメモリはセッションでキャッシュ
- **圧縮**: 大きなメモリファイルは自動的に圧縮
- **クリーンアップ**: 古い未使用メモリは自動的にアーカイブ

## プライバシーとセキュリティ

- **ローカルストレージ**: 全メモリはプロジェクトディレクトリにローカル保存
- **外部サービスなし**: メモリは外部サービスに送信されない
- **Gitignore**: 機密プロジェクトではmemoryディレクトリを .gitignore に追加
- **暗号化**: 機密プロジェクトメモリ用のオプション暗号化

---

メモリシステムにより、エージェントは時間をかけてプロジェクトの本当の理解を構築し、各相互作用でより効果的でコンテキスト対応になります。
