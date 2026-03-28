# ミドルウェア開発ガイド

ハーネスミドルウェアによるエージェント実行パイプラインのカスタマイズ。

## ミドルウェアアーキテクチャ

ハーネスは6つのフックポイントを提供し、エージェント実行の全段階をカスタマイズ可能：

```
リクエスト → before_agent → before_model → wrap_model_call → after_model → after_agent → レスポンス
                 ↓              ↓              ↓              ↓             ↓
              前処理         モデル前処理    モデル呼び出し制御   モデル後処理    後処理
                               ↓              ↓              ↓             ↓
                           コンテキスト    ツール呼び出し     結果処理       学習・保存
                           調整・注入      制御・監視      変換・検証     メモリ更新
```

## ミドルウェアフック

### 1. before_agent
エージェント処理開始前の前処理：
- リクエストの検証・変換
- セキュリティチェック
- コンテキスト準備

### 2. before_model
モデル呼び出し前の処理：
- プロンプトの拡張・最適化
- メモリ情報の注入
- 設定の調整

### 3. wrap_model_call
モデル呼び出し自体の制御：
- レート制限・リトライ制御
- 複数モデル並列実行
- キャッシュ制御

### 4. wrap_tool_call
ツール呼び出しの制御：
- ツール実行の監視
- 結果の検証・変換
- エラーハンドリング

### 5. after_model
モデル応答後の処理：
- 結果の検証・フィルタリング
- フォーマット変換
- 品質チェック

### 6. after_agent
エージェント処理完了後の後処理：
- 結果のログ記録
- メモリ更新・学習
- 通知・統合

## 基本ミドルウェア実装

### ベースクラス

```python
# middleware/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Middleware(ABC):
    """ハーネスミドルウェアベースクラス"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)

    async def before_agent(self, request: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """エージェント処理開始前"""
        return request

    async def before_model(self, prompt: str, context: Any) -> str:
        """モデル呼び出し前"""
        return prompt

    async def wrap_model_call(self, call_func, *args, **kwargs):
        """モデル呼び出し制御"""
        return await call_func(*args, **kwargs)

    async def wrap_tool_call(self, call_func, tool_name: str, *args, **kwargs):
        """ツール呼び出し制御"""
        return await call_func(tool_name, *args, **kwargs)

    async def after_model(self, response: str, context: Any) -> str:
        """モデル応答後処理"""
        return response

    async def after_agent(self, result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """エージェント処理完了後"""
        return result
```

## 実装例

### 1. ログ記録ミドルウェア

```python
# middleware/logging.py
import logging
import json
from datetime import datetime
from .base import Middleware

class LoggingMiddleware(Middleware):
    """包括的なログ記録とメトリクス収集"""

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger('harness')
        self.session_id = None

    async def before_agent(self, request, context):
        """リクエスト開始をログ"""
        self.session_id = request.get('session_id') or context.generate_id()

        self.logger.info(f"[{self.session_id}] エージェント処理開始", extra={
            'session_id': self.session_id,
            'user_message': request.get('message', '')[:100],
            'timestamp': datetime.utcnow().isoformat()
        })

        context.start_time = datetime.utcnow()
        return request

    async def before_model(self, prompt, context):
        """モデル呼び出し前ログ"""
        self.logger.debug(f"[{self.session_id}] モデル呼び出し準備完了", extra={
            'prompt_length': len(prompt),
            'context_tokens': context.get_token_count()
        })
        return prompt

    async def wrap_tool_call(self, call_func, tool_name, *args, **kwargs):
        """ツール使用をログ"""
        start_time = datetime.utcnow()

        try:
            result = await call_func(tool_name, *args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()

            self.logger.info(f"[{self.session_id}] ツール実行成功: {tool_name}", extra={
                'tool_name': tool_name,
                'duration_seconds': duration,
                'success': True
            })

            return result

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()

            self.logger.error(f"[{self.session_id}] ツール実行失敗: {tool_name}", extra={
                'tool_name': tool_name,
                'error': str(e),
                'duration_seconds': duration,
                'success': False
            })
            raise

    async def after_agent(self, result, context):
        """セッション完了をログ"""
        total_duration = (datetime.utcnow() - context.start_time).total_seconds()

        self.logger.info(f"[{self.session_id}] エージェント処理完了", extra={
            'session_id': self.session_id,
            'total_duration_seconds': total_duration,
            'success': result.get('success', False),
            'tools_used': len(context.get_tools_used()),
            'tokens_used': context.get_total_tokens()
        })

        return result
```

### 2. セキュリティミドルウェア

```python
# middleware/security.py
import re
from typing import List
from .base import Middleware

class SecurityMiddleware(Middleware):
    """セキュリティチェックとPII検出"""

    def __init__(self, config):
        super().__init__(config)

        # PII検出パターン
        self.pii_patterns = [
            (re.compile(r'\b\d{4}-\d{4}-\d{4}-\d{4}\b'), 'クレジットカード番号'),
            (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), 'SSN'),
            (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), 'メールアドレス'),
            (re.compile(r'\b\d{3}-\d{3}-\d{4}\b'), '電話番号'),
        ]

        # 危険なコマンドパターン
        self.dangerous_commands = [
            re.compile(r'rm\s+-rf\s+/'),
            re.compile(r'sudo\s+rm'),
            re.compile(r'format\s+c:'),
            re.compile(r'DROP\s+DATABASE', re.IGNORECASE)
        ]

    async def before_agent(self, request, context):
        """リクエストセキュリティチェック"""
        message = request.get('message', '')

        # PII検出
        pii_found = []
        for pattern, pii_type in self.pii_patterns:
            if pattern.search(message):
                pii_found.append(pii_type)

        if pii_found:
            context.add_security_warning(f"PII検出: {', '.join(pii_found)}")
            # PII部分をマスク
            for pattern, _ in self.pii_patterns:
                message = pattern.sub('[MASKED]', message)

        request['message'] = message
        return request

    async def wrap_tool_call(self, call_func, tool_name, *args, **kwargs):
        """ツール呼び出しセキュリティチェック"""

        # bashやshellツールの危険コマンドチェック
        if tool_name in ['bash', 'shell', 'cmd']:
            command = kwargs.get('command', '') or (args[0] if args else '')

            for pattern in self.dangerous_commands:
                if pattern.search(command):
                    raise SecurityError(f"危険なコマンドが検出されました: {command}")

        # ファイル操作の制限チェック
        if tool_name in ['edit', 'create', 'delete']:
            file_path = kwargs.get('path', '') or (args[0] if args else '')

            # システムファイル保護
            protected_paths = ['/etc/', '/bin/', '/usr/', 'C:\\Windows\\']
            if any(file_path.startswith(path) for path in protected_paths):
                raise SecurityError(f"保護されたパスへのアクセス試行: {file_path}")

        return await call_func(tool_name, *args, **kwargs)

class SecurityError(Exception):
    pass
```

### 3. パフォーマンス最適化ミドルウェア

```python
# middleware/performance.py
import asyncio
import time
from collections import defaultdict
from .base import Middleware

class PerformanceMiddleware(Middleware):
    """パフォーマンス最適化とキャッシュ制御"""

    def __init__(self, config):
        super().__init__(config)
        self.cache = {}
        self.tool_usage = defaultdict(int)
        self.parallel_limit = config.get('parallel_limit', 5)

    async def wrap_model_call(self, call_func, *args, **kwargs):
        """モデル呼び出し最適化"""

        # プロンプトキャッシュチェック
        prompt = kwargs.get('prompt') or args[0] if args else ''
        cache_key = hash(prompt)

        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]

            # 5分以内のキャッシュを使用
            if time.time() - cached_time < 300:
                return cached_result

        # モデル呼び出し実行
        start_time = time.time()
        result = await call_func(*args, **kwargs)
        duration = time.time() - start_time

        # 結果をキャッシュ（長い処理のみ）
        if duration > 2.0:
            self.cache[cache_key] = (time.time(), result)

        return result

    async def wrap_tool_call(self, call_func, tool_name, *args, **kwargs):
        """ツール並列実行制御"""
        self.tool_usage[tool_name] += 1

        # 並列制限制御
        if hasattr(self, '_semaphore'):
            async with self._semaphore:
                return await call_func(tool_name, *args, **kwargs)
        else:
            return await call_func(tool_name, *args, **kwargs)

    async def before_agent(self, request, context):
        """並列実行用セマフォ初期化"""
        self._semaphore = asyncio.Semaphore(self.parallel_limit)
        return request

    async def after_agent(self, result, context):
        """パフォーマンス統計をログ"""
        context.add_performance_stats({
            'cache_hits': len(self.cache),
            'tool_usage': dict(self.tool_usage),
            'parallel_limit': self.parallel_limit
        })

        return result
```

### 4. メモリ学習ミドルウェア

```python
# middleware/memory.py
import json
from typing import Dict, Any
from .base import Middleware

class MemoryMiddleware(Middleware):
    """自動メモリ学習と知識蓄積"""

    def __init__(self, config):
        super().__init__(config)
        self.facts_learned = []
        self.patterns_observed = []

    async def before_model(self, prompt, context):
        """メモリコンテキストを注入"""

        # 関連メモリを検索して注入
        relevant_memories = context.memory.search_relevant(prompt)

        if relevant_memories:
            memory_context = "\n## 関連する過去の知識:\n"
            for memory in relevant_memories:
                memory_context += f"- {memory}\n"

            prompt = memory_context + "\n" + prompt

        return prompt

    async def after_model(self, response, context):
        """応答から新しい事実を学習"""

        # 新しい事実の抽出パターン
        fact_indicators = [
            "判明しました",
            "確認できました",
            "使用されています",
            "設定されています"
        ]

        lines = response.split('\n')
        for line in lines:
            if any(indicator in line for indicator in fact_indicators):
                self.facts_learned.append(line.strip())

        return response

    async def wrap_tool_call(self, call_func, tool_name, *args, **kwargs):
        """ツール使用パターンを観察"""

        # ツール使用前の状態記録
        pre_state = {
            'tool': tool_name,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }

        try:
            result = await call_func(tool_name, *args, **kwargs)

            # 成功パターンを記録
            success_pattern = {
                'tool': tool_name,
                'success': True,
                'context': context.get_current_task(),
                'result_type': type(result).__name__
            }
            self.patterns_observed.append(success_pattern)

            return result

        except Exception as e:
            # 失敗パターンも学習
            failure_pattern = {
                'tool': tool_name,
                'success': False,
                'error': str(e),
                'context': context.get_current_task()
            }
            self.patterns_observed.append(failure_pattern)
            raise

    async def after_agent(self, result, context):
        """学習した内容をメモリに保存"""

        # 新しい事実をメモリに保存
        for fact in self.facts_learned:
            await context.memory.save_fact(fact)

        # 観察されたパターンを保存
        successful_patterns = [p for p in self.patterns_observed if p['success']]
        for pattern in successful_patterns:
            await context.memory.save_pattern(pattern)

        # 統計をコンテキストに追加
        result['learning_stats'] = {
            'facts_learned': len(self.facts_learned),
            'patterns_observed': len(self.patterns_observed),
            'success_rate': len(successful_patterns) / len(self.patterns_observed) if self.patterns_observed else 0
        }

        return result
```

## ミドルウェア設定

### harness.yaml での設定

```yaml
# harness.yaml
middleware:
  # 実行順序が重要（先に定義されたものが先に実行）
  - name: "security"
    class: "middleware.security.SecurityMiddleware"
    config:
      enabled: true
      mask_pii: true

  - name: "performance"
    class: "middleware.performance.PerformanceMiddleware"
    config:
      parallel_limit: 5
      enable_cache: true

  - name: "logging"
    class: "middleware.logging.LoggingMiddleware"
    config:
      log_level: "INFO"
      include_prompts: false

  - name: "memory"
    class: "middleware.memory.MemoryMiddleware"
    config:
      auto_learn: true
      similarity_threshold: 0.8
```

## カスタムミドルウェア開発

### 1. 要件定義
- どのフックポイントが必要？
- 何を監視/制御したい？
- パフォーマンスへの影響は？

### 2. 実装
```python
# middleware/my_custom.py
from .base import Middleware

class MyCustomMiddleware(Middleware):
    async def before_agent(self, request, context):
        # カスタムロジック
        return request
```

### 3. 設定追加
```yaml
middleware:
  - name: "my_custom"
    class: "middleware.my_custom.MyCustomMiddleware"
    config:
      custom_setting: "value"
```

### 4. テスト
```python
# tests/test_middleware.py
import pytest
from middleware.my_custom import MyCustomMiddleware

async def test_my_middleware():
    middleware = MyCustomMiddleware({'custom_setting': 'test'})

    request = {'message': 'test message'}
    result = await middleware.before_agent(request, None)

    assert result['message'] == 'test message'
```

## ベストプラクティス

### パフォーマンス
- 重い処理は避ける（特にwrap_model_call）
- 非同期処理を適切に使用
- キャッシュを活用

### セキュリティ
- 入力検証を徹底
- 機密情報のログ出力を防ぐ
- エラー詳細の適切なマスク

### 保守性
- 設定可能な動作にする
- 適切なログ出力
- 単体テストの作成

### 協調性
- 他のミドルウェアとの競合を避ける
- グローバル状態の変更は慎重に
- エラーハンドリングで処理を停止させない

---

ミドルウェアシステムにより、エージェントハーネスを完全にカスタマイズし、企業要件に合わせたAIエージェント基盤を構築できます。
