"""
ハーネスミドルウェアベースクラス

全てのミドルウェアが継承する基底クラス
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time


class Middleware(ABC):
    """ハーネスミドルウェアベースクラス

    6つのフックポイントでエージェント実行パイプラインをカスタマイズ:
    1. before_agent - エージェント処理開始前
    2. before_model - モデル呼び出し前
    3. wrap_model_call - モデル呼び出し制御
    4. wrap_tool_call - ツール呼び出し制御
    5. after_model - モデル応答後
    6. after_agent - エージェント処理完了後
    """

    def __init__(self, config: Dict[str, Any] = None):
        """ミドルウェア初期化

        Args:
            config: ミドルウェア設定辞書
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    async def before_agent(
        self, request: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """エージェント処理開始前のフック

        リクエストの検証、変換、準備処理を実行

        Args:
            request: ユーザーリクエスト
            context: 実行コンテキスト

        Returns:
            処理済みリクエスト
        """
        return request

    async def before_model(self, prompt: str, context: Any) -> str:
        """モデル呼び出し前のフック

        プロンプトの拡張、最適化、コンテキスト注入を実行

        Args:
            prompt: モデルに送信するプロンプト
            context: 実行コンテキスト

        Returns:
            処理済みプロンプト
        """
        return prompt

    async def wrap_model_call(self, call_func, *args, **kwargs):
        """モデル呼び出しのラッパー

        レート制限、キャッシュ、リトライなどを制御

        Args:
            call_func: モデル呼び出し関数
            *args: 関数引数
            **kwargs: 関数キーワード引数

        Returns:
            モデル応答
        """
        return await call_func(*args, **kwargs)

    async def wrap_tool_call(self, call_func, tool_name: str, *args, **kwargs):
        """ツール呼び出しのラッパー

        ツール実行の監視、検証、エラーハンドリングを制御

        Args:
            call_func: ツール呼び出し関数
            tool_name: 実行するツール名
            *args: 関数引数
            **kwargs: 関数キーワード引数

        Returns:
            ツール実行結果
        """
        return await call_func(tool_name, *args, **kwargs)

    async def after_model(self, response: str, context: Any) -> str:
        """モデル応答後のフック

        応答の検証、フィルタリング、変換を実行

        Args:
            response: モデル応答
            context: 実行コンテキスト

        Returns:
            処理済み応答
        """
        return response

    async def after_agent(self, result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """エージェント処理完了後のフック

        結果の記録、学習、通知を実行

        Args:
            result: エージェント実行結果
            context: 実行コンテキスト

        Returns:
            処理済み結果
        """
        return result


class TimingMixin:
    """実行時間計測ミックスイン"""

    def start_timer(self, name: str):
        """タイマー開始"""
        if not hasattr(self, "_timers"):
            self._timers = {}
        self._timers[name] = time.time()

    def end_timer(self, name: str) -> float:
        """タイマー終了して経過時間を返す"""
        if not hasattr(self, "_timers") or name not in self._timers:
            return 0.0

        elapsed = time.time() - self._timers[name]
        del self._timers[name]
        return elapsed


class LoggingMixin:
    """ログ記録ミックスイン"""

    def log_info(self, message: str, **kwargs):
        """情報ログ出力"""
        self.logger.info(message, extra=kwargs)

    def log_debug(self, message: str, **kwargs):
        """デバッグログ出力"""
        self.logger.debug(message, extra=kwargs)

    def log_error(self, message: str, error: Exception = None, **kwargs):
        """エラーログ出力"""
        if error:
            kwargs["error"] = str(error)
            kwargs["error_type"] = type(error).__name__
        self.logger.error(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs):
        """警告ログ出力"""
        self.logger.warning(message, extra=kwargs)


class SecurityMixin:
    """セキュリティチェックミックスイン"""

    def validate_input(self, data: Any) -> bool:
        """入力データ検証"""
        # 基本的な検証ロジック
        if isinstance(data, str) and len(data) > 10000:
            return False
        return True

    def sanitize_output(self, data: str) -> str:
        """出力データのサニタイズ"""
        # 機密情報のマスク処理など
        return data

    def check_permissions(self, action: str, resource: str) -> bool:
        """権限チェック"""
        # アクセス権限の確認
        return True


class BaseMiddleware(Middleware, TimingMixin, LoggingMixin, SecurityMixin):
    """機能豊富な基底ミドルウェアクラス

    TimingMixin, LoggingMixin, SecurityMixin を統合した
    実用的な基底クラス
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.session_id = None

    async def before_agent(
        self, request: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """基本前処理"""
        self.session_id = request.get("session_id", "unknown")
        self.start_timer("total_processing")

        # 入力検証
        if not self.validate_input(request.get("message", "")):
            raise ValueError("無効な入力データ")

        self.log_info("エージェント処理開始", session_id=self.session_id)
        return request

    async def after_agent(self, result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """基本後処理"""
        total_time = self.end_timer("total_processing")

        self.log_info(
            "エージェント処理完了",
            session_id=self.session_id,
            duration=total_time,
            success=result.get("success", False),
        )

        return result
