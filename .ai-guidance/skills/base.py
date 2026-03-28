"""
スキル基底クラス

全てのPythonスキルが継承する基底クラス
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import logging
import time
from pathlib import Path


class Skill(ABC):
    """スキル基底クラス

    動的スキルシステムの基盤となる抽象クラス。
    全てのPythonベーススキルがこのクラスを継承する。
    """

    def __init__(self, config: Dict[str, Any] = None):
        """スキル初期化

        Args:
            config: スキル設定辞書
        """
        self.config = config or {}

        # 基本情報
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
        self.parallel_safe = self.config.get('parallel_safe', False)

        # 結果管理
        self.results = []
        self.errors = []
        self.warnings = []
        self.debug_info = []

        # 実行時情報
        self.start_time = None
        self.end_time = None
        self.execution_context = None

        # ログ設定
        self.logger = logging.getLogger(f"skill.{self.name}")

        # ハーネス参照（実行時に設定）
        self.harness = None

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """スキル実行メソッド

        サブクラスで必ず実装する必要があるメイン実行メソッド

        Args:
            *args: 位置引数
            **kwargs: キーワード引数

        Returns:
            実行結果辞書。必ず 'success' キーを含むこと
        """
        pass

    async def setup(self):
        """スキル実行前の準備処理"""
        self.start_time = time.time()

        # 依存関係チェック
        if not await self.validate_dependencies():
            raise SkillDependencyError(f"依存関係が満たされていません: {self.dependencies}")

        # ツール可用性チェック
        if not await self.check_tools_available():
            raise SkillToolError(f"必要なツールが利用できません: {self.required_tools}")

        self.logger.info(f"スキル '{self.name}' の準備が完了")

    async def cleanup(self):
        """スキル実行後のクリーンアップ処理"""
        self.end_time = time.time()

        # 実行時間ログ
        if self.start_time:
            duration = self.end_time - self.start_time
            self.logger.info(f"スキル '{self.name}' 実行完了: {duration:.2f}秒")

        # リソースクリーンアップ
        await self._cleanup_resources()

    async def validate_dependencies(self) -> bool:
        """依存関係の検証"""
        for dep in self.dependencies:
            if not await self._check_dependency(dep):
                self.add_error(f"依存関係が満たされていません: {dep}")
                return False
        return True

    async def check_tools_available(self) -> bool:
        """必要ツールの可用性チェック"""
        if not self.harness:
            return True  # ハーネス未設定時はスキップ

        for tool in self.required_tools:
            if not await self.harness.is_tool_available(tool):
                self.add_error(f"必要なツールが利用できません: {tool}")
                return False
        return True

    async def _check_dependency(self, dependency: str) -> bool:
        """単一依存関係のチェック"""
        try:
            # Python モジュールの場合
            if '.' in dependency:
                __import__(dependency)
                return True

            # コマンドの場合
            if self.harness:
                result = await self.harness.call_tool('bash',
                    command=f"which {dependency}",
                    capture_output=True)
                return result.returncode == 0

            return True

        except Exception as e:
            self.logger.debug(f"依存関係チェック失敗 {dependency}: {e}")
            return False

    async def _cleanup_resources(self):
        """リソースクリーンアップ"""
        # サブクラスでオーバーライド可能
        pass

    # 結果管理メソッド
    def add_result(self, result: Any):
        """成功結果を追加"""
        self.results.append({
            'data': result,
            'timestamp': time.time(),
            'type': 'result'
        })
        self.logger.debug(f"結果追加: {result}")

    def add_error(self, error: str):
        """エラーを追加"""
        self.errors.append({
            'message': error,
            'timestamp': time.time(),
            'type': 'error'
        })
        self.logger.error(error)

    def add_warning(self, warning: str):
        """警告を追加"""
        self.warnings.append({
            'message': warning,
            'timestamp': time.time(),
            'type': 'warning'
        })
        self.logger.warning(warning)

    def add_debug_info(self, info: str):
        """デバッグ情報を追加"""
        self.debug_info.append({
            'message': info,
            'timestamp': time.time(),
            'type': 'debug'
        })
        self.logger.debug(info)

    # ハーネス統合メソッド
    async def call_tool(self, tool_name: str, *args, **kwargs):
        """ハーネス経由でツールを呼び出し"""
        if not self.harness:
            raise SkillError("ハーネスが設定されていません")

        try:
            result = await self.harness.call_tool(tool_name, *args, **kwargs)
            self.add_debug_info(f"ツール呼び出し成功: {tool_name}")
            return result
        except Exception as e:
            self.add_error(f"ツール呼び出し失敗 {tool_name}: {e}")
            raise

    async def load_skill(self, skill_name: str):
        """他のスキルを動的にロード"""
        if not self.harness:
            raise SkillError("ハーネスが設定されていません")

        return await self.harness.load_skill(skill_name)

    async def execute_skill(self, skill_name: str, *args, **kwargs):
        """他のスキルを実行"""
        skill = await self.load_skill(skill_name)
        return await skill.execute(*args, **kwargs)

    # メモリアクセス
    async def save_to_memory(self, key: str, value: Any):
        """メモリに値を保存"""
        if self.harness and hasattr(self.harness, 'memory'):
            await self.harness.memory.save(key, value)

    async def load_from_memory(self, key: str, default: Any = None):
        """メモリから値をロード"""
        if self.harness and hasattr(self.harness, 'memory'):
            return await self.harness.memory.load(key, default)
        return default

    # 実行サマリー
    def get_summary(self) -> Dict[str, Any]:
        """実行サマリーを取得"""
        duration = None
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time

        return {
            'skill_name': self.name,
            'version': self.version,
            'duration_seconds': duration,
            'results_count': len(self.results),
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'success': len(self.errors) == 0,
            'partial_success': len(self.results) > 0 and len(self.errors) > 0
        }

    def get_detailed_report(self) -> Dict[str, Any]:
        """詳細レポートを取得"""
        return {
            **self.get_summary(),
            'results': self.results,
            'errors': self.errors,
            'warnings': self.warnings,
            'debug_info': self.debug_info if self.logger.isEnabledFor(logging.DEBUG) else [],
            'config': self.config
        }


class CompositeSkill(Skill):
    """複合スキル基底クラス

    複数のサブスキルを組み合わせて実行するスキル用
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sub_skills = self.config.get('sub_skills', [])
        self.execution_mode = self.config.get('execution_mode', 'sequential')  # sequential or parallel
        self.fail_fast = self.config.get('fail_fast', True)

    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """複合スキル実行"""
        sub_results = []

        if self.execution_mode == 'parallel':
            sub_results = await self._execute_parallel(*args, **kwargs)
        else:
            sub_results = await self._execute_sequential(*args, **kwargs)

        # 結果を統合
        return self._merge_results(sub_results)

    async def _execute_sequential(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """順次実行"""
        results = []

        for skill_name in self.sub_skills:
            try:
                result = await self.execute_skill(skill_name, *args, **kwargs)
                results.append(result)

                # 失敗時に即座に停止
                if self.fail_fast and not result.get('success', False):
                    self.add_error(f"サブスキル {skill_name} が失敗したため実行を停止")
                    break

            except Exception as e:
                error_result = {'success': False, 'error': str(e), 'skill': skill_name}
                results.append(error_result)

                if self.fail_fast:
                    self.add_error(f"サブスキル {skill_name} でエラーが発生: {e}")
                    break

        return results

    async def _execute_parallel(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """並列実行"""
        tasks = []

        for skill_name in self.sub_skills:
            task = asyncio.create_task(
                self._execute_single_skill(skill_name, *args, **kwargs)
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_single_skill(self, skill_name: str, *args, **kwargs) -> Dict[str, Any]:
        """単一スキルの実行（エラーハンドリング付き）"""
        try:
            return await self.execute_skill(skill_name, *args, **kwargs)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'skill': skill_name
            }

    def _merge_results(self, sub_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """サブスキル結果をマージ"""

        successful_results = [r for r in sub_results if r.get('success', False)]
        failed_results = [r for r in sub_results if not r.get('success', False)]

        # 統合結果
        merged = {
            'success': len(failed_results) == 0,
            'partial_success': len(successful_results) > 0 and len(failed_results) > 0,
            'total_sub_skills': len(sub_results),
            'successful_sub_skills': len(successful_results),
            'failed_sub_skills': len(failed_results),
            'sub_results': sub_results,
            'execution_mode': self.execution_mode
        }

        # 成功した結果をメインの結果に追加
        for result in successful_results:
            if 'results' in result:
                self.results.extend(result['results'])

        # 失敗した結果をエラーに追加
        for result in failed_results:
            if 'error' in result:
                self.add_error(f"サブスキル {result.get('skill', 'unknown')} エラー: {result['error']}")

        return merged


# 例外クラス
class SkillError(Exception):
    """スキル一般エラー"""
    pass


class SkillDependencyError(SkillError):
    """スキル依存関係エラー"""
    pass


class SkillToolError(SkillError):
    """スキルツールエラー"""
    pass


class SkillTimeoutError(SkillError):
    """スキルタイムアウトエラー"""
    pass


class SkillNotFoundError(SkillError):
    """スキル未発見エラー"""
    pass
