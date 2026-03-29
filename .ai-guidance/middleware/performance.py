"""
Performance Middleware for AI Harness
パフォーマンス最適化ミドルウェア
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
import logging

from .base import BaseMiddleware

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseMiddleware):
    """パフォーマンス監視・最適化ミドルウェア"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # パフォーマンス設定
        self.enable_caching = config.get('enable_caching', True)
        self.enable_parallel_execution = config.get('enable_parallel_execution', True)
        self.enable_metrics_collection = config.get('enable_metrics_collection', True)
        self.cache_ttl = config.get('cache_ttl', 300)  # 5分
        self.max_parallel_tasks = config.get('max_parallel_tasks', 5)
        
        # メトリクス収集
        self.metrics = {
            'request_count': 0,
            'total_duration': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_executions': 0,
            'response_times': deque(maxlen=1000),  # 最新1000件
            'error_count': 0
        }
        
        # キャッシュシステム
        self.cache = {}
        self.cache_timestamps = {}
        
        # 並列実行管理
        self.semaphore = asyncio.Semaphore(self.max_parallel_tasks)
        self.active_tasks = set()
        
        logger.info("Performance Middleware initialized")
    
    async def before_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """エージェント実行前の最適化"""
        # リクエスト開始時刻記録
        context['_perf_start_time'] = time.time()
        context['_perf_request_id'] = f"req_{int(time.time() * 1000)}"
        
        # メトリクス更新
        if self.enable_metrics_collection:
            self.metrics['request_count'] += 1
            
        logger.debug(f"Performance tracking started for {context['_perf_request_id']}")
        return context
    
    async def before_model(self, prompt: str, context: Dict[str, Any]) -> str:
        """モデル呼び出し前の最適化"""
        
        # キャッシュチェック
        if self.enable_caching:
            cache_key = self._generate_cache_key(prompt, context)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result is not None:
                context['_cache_hit'] = True
                context['_cached_result'] = cached_result
                self.metrics['cache_hits'] += 1
                logger.debug(f"Cache hit for request {context.get('_perf_request_id')}")
                return prompt
        
        context['_cache_hit'] = False
        self.metrics['cache_misses'] += 1
        
        # プロンプト最適化
        optimized_prompt = self._optimize_prompt(prompt, context)
        
        return optimized_prompt
    
    async def wrap_model_call(self, model_call, prompt: str, context: Dict[str, Any]) -> Any:
        """モデル呼び出しのラップと最適化"""
        
        # キャッシュヒットの場合は cached result を返す
        if context.get('_cache_hit'):
            return context.get('_cached_result')
        
        # 並列実行制御
        if self.enable_parallel_execution:
            async with self.semaphore:
                start_time = time.time()
                
                try:
                    # モデル呼び出し実行
                    result = await model_call(prompt, context)
                    
                    # 実行時間記録
                    duration = time.time() - start_time
                    context['_model_duration'] = duration
                    
                    # キャッシュに保存
                    if self.enable_caching:
                        cache_key = self._generate_cache_key(prompt, context)
                        self._cache_result(cache_key, result)
                    
                    return result
                    
                except Exception as e:
                    self.metrics['error_count'] += 1
                    logger.error(f"Model call failed: {e}")
                    raise
        else:
            # 通常実行
            return await model_call(prompt, context)
    
    async def wrap_tool_call(self, tool_call, tool_name: str, context: Dict[str, Any]) -> Any:
        """ツール呼び出しの並列化と最適化"""
        
        if self.enable_parallel_execution and self._can_parallelize_tool(tool_name):
            # 並列実行対象のツール
            async with self.semaphore:
                start_time = time.time()
                
                try:
                    result = await tool_call(tool_name, context)
                    
                    # ツール実行時間記録
                    duration = time.time() - start_time
                    context.setdefault('_tool_durations', {})[tool_name] = duration
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Tool {tool_name} execution failed: {e}")
                    raise
        else:
            # 通常実行
            return await tool_call(tool_name, context)
    
    async def after_model(self, result: Any, context: Dict[str, Any]) -> Any:
        """モデル応答後の最適化"""
        
        # レスポンス最適化
        optimized_result = self._optimize_response(result, context)
        
        return optimized_result
    
    async def after_agent(self, result: Any, context: Dict[str, Any]) -> Any:
        """エージェント実行後のメトリクス更新"""
        
        if self.enable_metrics_collection:
            # 総実行時間計算
            if '_perf_start_time' in context:
                total_duration = time.time() - context['_perf_start_time']
                self.metrics['total_duration'] += total_duration
                self.metrics['response_times'].append(total_duration)
                
                # 詳細メトリクス
                request_id = context.get('_perf_request_id', 'unknown')
                model_duration = context.get('_model_duration', 0)
                tool_durations = context.get('_tool_durations', {})
                cache_hit = context.get('_cache_hit', False)
                
                logger.info(f"Performance summary for {request_id}: "
                          f"total={total_duration:.3f}s, "
                          f"model={model_duration:.3f}s, "
                          f"tools={sum(tool_durations.values()):.3f}s, "
                          f"cache_hit={cache_hit}")
        
        return result
    
    def _generate_cache_key(self, prompt: str, context: Dict[str, Any]) -> str:
        """キャッシュキー生成"""
        import hashlib
        
        # プロンプトとコンテキストの重要部分をハッシュ化
        cache_data = {
            'prompt': prompt[:1000],  # プロンプトの最初の1000文字
            'model': context.get('model_name', 'default'),
            'temperature': context.get('temperature', 0.7),
        }
        
        cache_str = str(sorted(cache_data.items()))
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """キャッシュから結果取得"""
        if cache_key not in self.cache:
            return None
            
        # TTL チェック
        if cache_key in self.cache_timestamps:
            cache_age = time.time() - self.cache_timestamps[cache_key]
            if cache_age > self.cache_ttl:
                # 期限切れキャッシュを削除
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None
        
        return self.cache[cache_key]
    
    def _cache_result(self, cache_key: str, result: Any):
        """結果をキャッシュに保存"""
        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
        
        # キャッシュサイズ制限
        if len(self.cache) > 1000:
            # 最も古いキャッシュエントリを削除
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
    
    def _optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """プロンプト最適化"""
        # 基本的なプロンプト最適化
        optimized = prompt.strip()
        
        # 冗長な空白を削除
        optimized = ' '.join(optimized.split())
        
        # コンテキスト圧縮のヒント
        if len(optimized) > 4000:
            context['_prompt_compressed'] = True
            # 長すぎるプロンプトの場合は要約を提案
            optimized = f"以下の内容を簡潔にまとめて回答してください:\n\n{optimized[:3500]}..."
        
        return optimized
    
    def _optimize_response(self, result: Any, context: Dict[str, Any]) -> Any:
        """レスポンス最適化"""
        # レスポンスの基本最適化
        if isinstance(result, str):
            # 基本的な文字列最適化
            result = result.strip()
            
            # 冗長な改行を削除
            result = '\n'.join(line.strip() for line in result.split('\n') if line.strip())
        
        return result
    
    def _can_parallelize_tool(self, tool_name: str) -> bool:
        """ツールが並列実行可能かどうか判定"""
        # 並列実行安全なツールのリスト
        parallel_safe_tools = {
            'file_read', 'web_search', 'api_call', 'database_query',
            'code_analysis', 'lint_check', 'test_run'
        }
        
        # 並列実行危険なツール（排他制御が必要）
        exclusive_tools = {
            'file_write', 'git_commit', 'deployment', 'database_write'
        }
        
        if tool_name in parallel_safe_tools:
            return True
        elif tool_name in exclusive_tools:
            return False
        else:
            # デフォルトは安全側で非並列
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクス取得"""
        metrics = self.metrics.copy()
        
        # 追加統計
        if len(self.metrics['response_times']) > 0:
            times = list(self.metrics['response_times'])
            metrics['avg_response_time'] = sum(times) / len(times)
            metrics['min_response_time'] = min(times)
            metrics['max_response_time'] = max(times)
            
            # パーセンタイル計算
            sorted_times = sorted(times)
            n = len(sorted_times)
            metrics['p95_response_time'] = sorted_times[int(n * 0.95)] if n > 0 else 0
            metrics['p99_response_time'] = sorted_times[int(n * 0.99)] if n > 0 else 0
        
        # キャッシュ統計
        if metrics['cache_hits'] + metrics['cache_misses'] > 0:
            total_cache_requests = metrics['cache_hits'] + metrics['cache_misses']
            metrics['cache_hit_rate'] = metrics['cache_hits'] / total_cache_requests
        else:
            metrics['cache_hit_rate'] = 0.0
        
        # エラー率
        if metrics['request_count'] > 0:
            metrics['error_rate'] = metrics['error_count'] / metrics['request_count']
        else:
            metrics['error_rate'] = 0.0
        
        # 現在のキャッシュサイズ
        metrics['cache_size'] = len(self.cache)
        
        return metrics
    
    def clear_cache(self):
        """キャッシュクリア"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Performance cache cleared")
    
    def reset_metrics(self):
        """メトリクスリセット"""
        self.metrics = {
            'request_count': 0,
            'total_duration': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_executions': 0,
            'response_times': deque(maxlen=1000),
            'error_count': 0
        }
        logger.info("Performance metrics reset")


# パフォーマンス最適化のためのユーティリティ関数

async def batch_execute(tasks: List[Any], max_concurrent: int = 5) -> List[Any]:
    """タスクを並列バッチ実行"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*[execute_task(task) for task in tasks])

def measure_performance(func):
    """パフォーマンス測定デコレータ"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper