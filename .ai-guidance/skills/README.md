# 動的スキルシステム

オンデマンドでロードされる高度なAIエージェントスキル。

## スキルアーキテクチャ

ハーネスの動的スキルシステムは、従来のコンテキスト汚染を避け、必要な時のみスキルをロード：

```
リクエスト → スキル検索 → 関連スキル選択 → ロード → 実行 → アンロード
              ↓           ↓              ↓      ↓      ↓
          トリガー解析  信頼度計算    遅延ロード  実行  メモリ解放
          キーワード    コンテキスト   依存関係    結果  次回高速化
          パターン      マッチング    注入       検証   キャッシュ
```

## スキルタイプ

### 1. テンプレートベーススキル (.yaml)

設定駆動型の軽量スキル：

```yaml
# skills/commit_message.yaml
name: "commit_message"
description: "git変更から従来型コミットメッセージを生成"
version: "1.0.0"

triggers:
  - "コミット"
  - "コミットメッセージ"
  - "従来型コミット"

templates:
  conventional:
    format: "{type}({scope}): {description}"
    types:
      feat: "新機能"
      fix: "バグ修正"
```

### 2. Pythonスキル (.py)

高度なロジックを含む実行型スキル：

```python
# skills/code_review.py
class CodeReviewSkill(Skill):
    async def execute(self, files=None):
        # 高度なコード解析
        return self.generate_review_report()
```

### 3. 複合スキル

複数のサブスキルを組み合わせたワークフロー：

```yaml
name: "full_deployment"
type: "composite"
sub_skills:
  - "code_review"
  - "run_tests"
  - "build_application"
  - "deploy_to_staging"
```

## スキル発見メカニズム

### トリガーベース検索

キーワードとパターンでスキルを自動発見：

```python
# スキルマネージャーが自動実行
class SkillManager:
    async def find_relevant_skills(self, user_message: str):
        """ユーザーメッセージから関連スキルを検索"""

        relevant_skills = []

        for skill in self.available_skills:
            confidence = 0.0

            # トリガーキーワードマッチング
            for trigger in skill.triggers:
                if trigger in user_message.lower():
                    confidence += 0.3

            # コンテキストパターンマッチング
            for pattern in skill.context_patterns:
                if re.search(pattern, user_message, re.IGNORECASE):
                    confidence += 0.2

            # 過去の使用履歴
            if self.memory.was_skill_successful(skill.name):
                confidence += 0.1

            if confidence > 0.5:  # 閾値以上で選択
                relevant_skills.append((skill, confidence))

        return sorted(relevant_skills, key=lambda x: x[1], reverse=True)
```

### 意図解析ベース選択

```python
class IntentAnalyzer:
    """ユーザー意図を解析してスキル選択"""

    intent_patterns = {
        'code_analysis': [
            r'レビュー.*コード',
            r'コード.*チェック',
            r'バグ.*探',
            r'品質.*確認'
        ],
        'deployment': [
            r'デプロイ',
            r'本番.*リリース',
            r'アプリ.*公開'
        ],
        'testing': [
            r'テスト.*実行',
            r'テスト.*書',
            r'検証.*実施'
        ]
    }

    async def analyze_intent(self, message: str) -> Dict[str, float]:
        """意図分析結果を返す"""
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, message):
                    score += 1.0
            intent_scores[intent] = score / len(patterns)

        return intent_scores
```

## スキル実装パターン

### 基本スキルクラス

```python
# skills/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio

class Skill(ABC):
    """スキル基底クラス"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.config.get('name', self.__class__.__name__)
        self.version = self.config.get('version', '1.0.0')
        self.description = self.config.get('description', '')

        # トリガー設定
        self.triggers = self.config.get('triggers', [])
        self.context_patterns = self.config.get('context_patterns', [])

        # 依存関係
        self.dependencies = self.config.get('dependencies', [])
        self.required_tools = self.config.get('required_tools', [])

        # 実行制御
        self.timeout = self.config.get('timeout', 300)  # 5分
        self.retry_count = self.config.get('retry_count', 3)

        # 結果
        self.results = []
        self.errors = []
        self.warnings = []

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """スキル実行メソッド（サブクラスで実装）"""
        pass

    async def validate_dependencies(self) -> bool:
        """依存関係チェック"""
        for dep in self.dependencies:
            if not await self._check_dependency(dep):
                self.errors.append(f"依存関係が満たされていません: {dep}")
                return False
        return True

    async def check_tools_available(self) -> bool:
        """必要ツールの可用性チェック"""
        for tool in self.required_tools:
            if not await self._check_tool_available(tool):
                self.errors.append(f"必要なツールが利用できません: {tool}")
                return False
        return True

    async def setup(self):
        """スキル実行前の準備"""
        await self.validate_dependencies()
        await self.check_tools_available()

    async def cleanup(self):
        """スキル実行後のクリーンアップ"""
        pass

    def add_result(self, result: Any):
        """結果を追加"""
        self.results.append(result)

    def add_error(self, error: str):
        """エラーを追加"""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """警告を追加"""
        self.warnings.append(warning)

    def get_summary(self) -> Dict[str, Any]:
        """実行サマリーを取得"""
        return {
            'skill_name': self.name,
            'version': self.version,
            'results_count': len(self.results),
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'success': len(self.errors) == 0
        }
```

### ツール統合スキル

```python
# skills/file_analyzer.py
class FileAnalyzerSkill(Skill):
    """ファイル分析スキル"""

    def __init__(self, config=None):
        super().__init__(config)
        self.supported_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb']

    async def execute(self, file_paths: List[str] = None, **kwargs) -> Dict[str, Any]:
        """ファイル群を分析"""

        if not file_paths:
            # glob ツールでファイル検索
            file_paths = await self.find_source_files()

        analysis_results = []

        for file_path in file_paths:
            try:
                # view ツールでファイル内容取得
                content = await self.harness.call_tool('view', path=file_path)

                # 分析実行
                analysis = await self.analyze_file(file_path, content)
                analysis_results.append(analysis)

                self.add_result(analysis)

            except Exception as e:
                self.add_error(f"ファイル分析失敗 {file_path}: {e}")

        return {
            'analyzed_files': len(analysis_results),
            'results': analysis_results,
            'summary': self.generate_summary(analysis_results)
        }

    async def find_source_files(self) -> List[str]:
        """ソースファイルを検索"""
        all_files = []

        for ext in self.supported_extensions:
            pattern = f"**/*{ext}"
            files = await self.harness.call_tool('glob', pattern=pattern)
            all_files.extend(files)

        return all_files

    async def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """単一ファイル分析"""

        analysis = {
            'file_path': file_path,
            'lines_count': len(content.splitlines()),
            'size_bytes': len(content.encode('utf-8')),
            'language': self.detect_language(file_path),
            'complexity_score': self.calculate_complexity(content),
            'issues': self.find_issues(content),
            'metrics': self.calculate_metrics(content)
        }

        return analysis

    def detect_language(self, file_path: str) -> str:
        """プログラミング言語検出"""
        ext = Path(file_path).suffix
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rb': 'Ruby'
        }
        return language_map.get(ext, 'Unknown')

    def calculate_complexity(self, content: str) -> int:
        """循環的複雑度の概算"""
        # 簡易実装：制御フロー文をカウント
        complexity_keywords = [
            'if', 'elif', 'else', 'for', 'while', 'try', 'except',
            'switch', 'case', 'catch', 'finally'
        ]

        complexity = 1  # ベースライン
        for keyword in complexity_keywords:
            complexity += content.lower().count(keyword)

        return complexity

    def find_issues(self, content: str) -> List[Dict[str, Any]]:
        """コード課題検出"""
        issues = []

        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            # 長すぎる行
            if len(line) > 100:
                issues.append({
                    'type': 'long_line',
                    'line': i,
                    'message': f'行が長すぎます ({len(line)} 文字)'
                })

            # TODOコメント
            if 'TODO' in line.upper():
                issues.append({
                    'type': 'todo',
                    'line': i,
                    'message': 'TODOコメントが残っています'
                })

            # ハードコードされた値（数字）
            if re.search(r'\b\d{2,}\b', line) and 'import' not in line:
                issues.append({
                    'type': 'magic_number',
                    'line': i,
                    'message': 'マジックナンバーの可能性'
                })

        return issues
```

### 外部API統合スキル

```python
# skills/github_integration.py
import aiohttp
from datetime import datetime, timedelta

class GitHubIntegrationSkill(Skill):
    """GitHub API統合スキル"""

    def __init__(self, config=None):
        super().__init__(config)
        self.github_token = config.get('github_token')
        self.base_url = 'https://api.github.com'

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """GitHub操作実行"""

        if action == 'create_pr':
            return await self.create_pull_request(**kwargs)
        elif action == 'get_issues':
            return await self.get_repository_issues(**kwargs)
        elif action == 'analyze_commits':
            return await self.analyze_recent_commits(**kwargs)
        else:
            raise ValueError(f"未対応のアクション: {action}")

    async def create_pull_request(self, repo: str, title: str,
                                 body: str, head: str, base: str = 'main') -> Dict[str, Any]:
        """プルリクエスト作成"""

        url = f"{self.base_url}/repos/{repo}/pulls"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        payload = {
            'title': title,
            'body': body,
            'head': head,
            'base': base
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    pr_data = await response.json()
                    self.add_result(f"PR作成成功: #{pr_data['number']}")
                    return {
                        'success': True,
                        'pr_number': pr_data['number'],
                        'pr_url': pr_data['html_url']
                    }
                else:
                    error_data = await response.json()
                    self.add_error(f"PR作成失敗: {error_data.get('message', 'Unknown error')}")
                    return {'success': False, 'error': error_data}

    async def get_repository_issues(self, repo: str, state: str = 'open',
                                   labels: List[str] = None) -> Dict[str, Any]:
        """リポジトリのissue取得"""

        url = f"{self.base_url}/repos/{repo}/issues"
        params = {'state': state}

        if labels:
            params['labels'] = ','.join(labels)

        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    issues = await response.json()

                    # 分析結果
                    analysis = {
                        'total_issues': len(issues),
                        'by_label': self._group_issues_by_label(issues),
                        'by_author': self._group_issues_by_author(issues),
                        'average_age_days': self._calculate_average_age(issues)
                    }

                    self.add_result(f"{len(issues)}件のissueを取得")
                    return {
                        'success': True,
                        'issues': issues,
                        'analysis': analysis
                    }
                else:
                    error = await response.text()
                    self.add_error(f"Issue取得失敗: {error}")
                    return {'success': False, 'error': error}

    def _group_issues_by_label(self, issues: List[Dict]) -> Dict[str, int]:
        """ラベル別issue数を集計"""
        label_counts = {}
        for issue in issues:
            for label in issue.get('labels', []):
                label_name = label['name']
                label_counts[label_name] = label_counts.get(label_name, 0) + 1
        return label_counts

    def _group_issues_by_author(self, issues: List[Dict]) -> Dict[str, int]:
        """作成者別issue数を集計"""
        author_counts = {}
        for issue in issues:
            author = issue['user']['login']
            author_counts[author] = author_counts.get(author, 0) + 1
        return author_counts

    def _calculate_average_age(self, issues: List[Dict]) -> float:
        """平均経過日数を計算"""
        if not issues:
            return 0.0

        total_age = 0
        for issue in issues:
            created_at = datetime.fromisoformat(
                issue['created_at'].replace('Z', '+00:00')
            )
            age = (datetime.now(created_at.tzinfo) - created_at).days
            total_age += age

        return total_age / len(issues)
```

## スキルライフサイクル管理

### 動的ロード・アンロード

```python
# harness/skill_manager.py
class SkillManager:
    """スキルの動的管理"""

    def __init__(self):
        self.loaded_skills = {}
        self.skill_cache = {}
        self.usage_stats = {}

    async def load_skill(self, skill_name: str) -> Skill:
        """スキルを動的にロード"""

        if skill_name in self.loaded_skills:
            return self.loaded_skills[skill_name]

        # スキル定義ファイル検索
        skill_config = await self._find_skill_config(skill_name)
        if not skill_config:
            raise SkillNotFoundError(f"スキル '{skill_name}' が見つかりません")

        # スキルインスタンス作成
        skill_instance = await self._create_skill_instance(skill_config)

        # 依存関係チェック
        await skill_instance.setup()

        # キャッシュに保存
        self.loaded_skills[skill_name] = skill_instance

        return skill_instance

    async def unload_skill(self, skill_name: str):
        """スキルをアンロード"""

        if skill_name in self.loaded_skills:
            skill = self.loaded_skills[skill_name]
            await skill.cleanup()
            del self.loaded_skills[skill_name]

    async def execute_skill(self, skill_name: str, *args, **kwargs) -> Dict[str, Any]:
        """スキルを実行"""

        # 使用統計更新
        self.usage_stats[skill_name] = self.usage_stats.get(skill_name, 0) + 1

        # スキルロード
        skill = await self.load_skill(skill_name)

        try:
            # 実行
            result = await skill.execute(*args, **kwargs)

            # 成功時は一時的にキャッシュ保持
            self._update_cache_priority(skill_name, success=True)

            return result

        except Exception as e:
            # エラー時はすぐにアンロード
            await self.unload_skill(skill_name)
            raise

        finally:
            # メモリ圧迫時は低優先度スキルをアンロード
            await self._manage_memory_pressure()

    async def _manage_memory_pressure(self):
        """メモリ圧迫時のスキル管理"""

        if len(self.loaded_skills) > 10:  # 閾値
            # 最も使用頻度の低いスキルをアンロード
            least_used = min(self.usage_stats.items(), key=lambda x: x[1])
            await self.unload_skill(least_used[0])
```

### スキル依存関係解決

```python
class DependencyResolver:
    """スキル依存関係の解決"""

    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
        self.dependency_graph = {}

    async def resolve_dependencies(self, skill_name: str) -> List[str]:
        """依存関係を解決して実行順序を決定"""

        visited = set()
        resolution_order = []

        await self._resolve_recursive(skill_name, visited, resolution_order)

        return resolution_order

    async def _resolve_recursive(self, skill_name: str, visited: set, order: List[str]):
        """再帰的依存関係解決"""

        if skill_name in visited:
            return

        visited.add(skill_name)

        # スキル設定取得
        skill_config = await self.skill_manager._find_skill_config(skill_name)
        dependencies = skill_config.get('dependencies', [])

        # 依存スキルを先に解決
        for dep_skill in dependencies:
            await self._resolve_recursive(dep_skill, visited, order)

        # 自分自身を追加
        order.append(skill_name)
```

## スキル設定例

### harness.yaml でのスキル設定

```yaml
# harness.yaml
skills:
  # 基本設定
  discovery:
    auto_discovery: true
    search_paths:
      - ".ai-guidance/skills/"
      - "~/.ai-guidance/global-skills/"

  # ロード制御
  loading:
    lazy_loading: true
    max_loaded: 10
    timeout_seconds: 300

  # 実行制御
  execution:
    parallel_execution: true
    max_parallel: 3
    retry_failed: true

  # 特定スキル設定
  overrides:
    code_review:
      timeout_seconds: 600
      confidence_threshold: 0.7

    github_integration:
      github_token: "${GITHUB_TOKEN}"
      rate_limit: 100

# 個別スキル有効化/無効化
enabled_skills:
  - "code_review"
  - "commit_message"
  - "file_analyzer"
  - "github_integration"

disabled_skills:
  - "legacy_skill"
```

## スキル作成テンプレート

### 基本スキルテンプレート

```python
# skills/my_skill_template.py
"""
新しいスキルのテンプレート

このテンプレートをコピーしてカスタムスキルを作成
"""

from .base import Skill
from typing import Dict, Any, List
import asyncio

class MySkillTemplate(Skill):
    """スキルの説明をここに記述"""

    def __init__(self, config=None):
        # デフォルト設定
        default_config = {
            'name': 'my_skill_template',
            'version': '1.0.0',
            'description': 'カスタムスキルのテンプレート',
            'triggers': [
                'my_trigger',
                'custom_action'
            ],
            'dependencies': [],
            'required_tools': ['bash'],  # 必要なツール
            'timeout': 180
        }

        # 設定をマージ
        if config:
            default_config.update(config)

        super().__init__(default_config)

        # カスタム設定
        self.custom_setting = self.config.get('custom_setting', 'default_value')

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """メインの実行ロジック"""

        try:
            # 1. 入力検証
            self._validate_inputs(*args, **kwargs)

            # 2. 準備処理
            await self._prepare()

            # 3. メイン処理
            results = await self._main_process(*args, **kwargs)

            # 4. 結果処理
            processed_results = await self._process_results(results)

            # 5. 成功ログ
            self.add_result("処理が正常に完了しました")

            return {
                'success': True,
                'results': processed_results,
                'summary': self._generate_summary(processed_results)
            }

        except Exception as e:
            # エラーハンドリング
            self.add_error(f"実行エラー: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'partial_results': getattr(self, '_partial_results', [])
            }

    def _validate_inputs(self, *args, **kwargs):
        """入力検証"""
        # カスタム検証ロジック
        pass

    async def _prepare(self):
        """準備処理"""
        # 必要なリソースの準備
        pass

    async def _main_process(self, *args, **kwargs):
        """メイン処理"""
        # 実際の処理ロジック
        results = []

        # 例: ツール呼び出し
        # output = await self.harness.call_tool('bash', command='ls -la')
        # results.append(output)

        return results

    async def _process_results(self, raw_results):
        """結果処理"""
        # 結果の変換・整形
        return raw_results

    def _generate_summary(self, results):
        """サマリー生成"""
        return {
            'processed_items': len(results),
            'status': 'completed'
        }
```

### YAMLスキルテンプレート

```yaml
# skills/my_yaml_skill.yaml
name: "my_yaml_skill"
description: "YAML設定ベースのスキル例"
version: "1.0.0"
type: "template"

# トリガー条件
triggers:
  - "yaml_action"
  - "template_skill"

context_patterns:
  - "yaml.*設定"
  - "テンプレート.*実行"

# 依存関係
dependencies:
  - "bash"

required_tools:
  - "edit"
  - "view"

# 設定
configuration:
  timeout_seconds: 120
  retry_count: 2
  output_format: "markdown"

# テンプレート定義
templates:
  main_template: |
    ## {title} の実行結果

    **実行日時**: {timestamp}
    **実行者**: {user}

    ### 処理内容
    {content}

    ### 結果
    {results}

# 実行ステップ
execution_steps:
  - name: "準備"
    action: "setup"
    params:
      check_dependencies: true

  - name: "メイン処理"
    action: "process"
    params:
      input_validation: true
      parallel_execution: false

  - name: "結果出力"
    action: "output"
    params:
      format: "{output_format}"

# 結果検証ルール
validation_rules:
  - field: "success"
    required: true
    type: "boolean"

  - field: "results"
    required: true
    type: "array"
    min_length: 1

# 例
examples:
  - input: "yaml_action を実行"
    expected_output: "YAML設定ベースの処理を実行しました"

  - input: "template_skill でレポート生成"
    expected_output: "テンプレートを使用してレポートを生成しました"
```

## ベストプラクティス

### パフォーマンス

- 遅延ロード：必要時のみスキルをロード
- キャッシュ活用：頻繁に使用するスキルはメモリ保持
- 並列実行：独立したスキルは並列で実行

### エラーハンドリング

- 部分的成功の対応
- 適切なエラーメッセージ
- ログとデバッグ情報の提供

### 保守性

- 明確な責任分離
- 設定の外部化
- バージョン管理対応

### セキュリティ

- 入力検証の徹底
- 権限チェック
- 機密情報の適切な処理

---

動的スキルシステムにより、AIエージェントは必要な機能のみを効率的にロードし、コンテキストを汚染することなく高度な処理を実現できます。
