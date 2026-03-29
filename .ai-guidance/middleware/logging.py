"""
ログ記録ミドルウェア

包括的なログ記録、メトリクス収集、デバッグ情報の提供
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from .base import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    """包括的ログ記録ミドルウェア

    特徴:
    - 構造化ログ出力（JSON形式）
    - セッション追跡
    - パフォーマンスメトリクス
    - ツール使用統計
    - エラー詳細記録
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

        # ログ設定
        self.log_level = config.get("log_level", "INFO")
        self.log_to_file = config.get("log_to_file", True)
        self.log_file_path = config.get("log_file_path", "./logs/harness.log")
        self.include_prompts = config.get("include_prompts", False)
        self.include_responses = config.get("include_responses", False)

        # セッション情報
        self.session_id = None
        self.tool_calls = []
        self.metrics = {}

        self._setup_logging()

    def _setup_logging(self):
        """ログ設定をセットアップ"""

        # ログフォーマッター
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # ファイルハンドラー（設定されている場合）
        if self.log_to_file:
            log_file = Path(self.log_file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

        self.logger.setLevel(getattr(logging, self.log_level))

    async def before_agent(
        self, request: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """エージェント処理開始ログ"""
        result = await super().before_agent(request, context)

        self.session_id = request.get("session_id") or context.generate_session_id()
        self.metrics["start_time"] = datetime.utcnow()
        self.tool_calls = []

        # 構造化ログ出力
        log_data = {
            "event": "agent_start",
            "session_id": self.session_id,
            "user_message_length": len(request.get("message", "")),
            "timestamp": self.metrics["start_time"].isoformat(),
            "context_info": {
                "user_id": context.get("user_id"),
                "request_id": context.get("request_id"),
            },
        }

        if self.include_prompts:
            log_data["user_message"] = request.get("message", "")

        self.logger.info(
            f"エージェント処理開始 [{self.session_id}]",
            extra={"structured_data": log_data},
        )

        return result

    async def before_model(self, prompt: str, context: Any) -> str:
        """モデル呼び出し前ログ"""
        result = await super().before_model(prompt, context)

        self.start_timer("model_call")

        log_data = {
            "event": "model_call_start",
            "session_id": self.session_id,
            "prompt_length": len(result),
            "estimated_tokens": len(result.split()) * 1.3,  # 概算
            "timestamp": datetime.utcnow().isoformat(),
        }

        if self.include_prompts:
            log_data["prompt"] = result

        self.logger.debug(
            f"モデル呼び出し開始 [{self.session_id}]",
            extra={"structured_data": log_data},
        )

        return result

    async def wrap_tool_call(self, call_func, tool_name: str, *args, **kwargs):
        """ツール呼び出しログ"""

        # ツール呼び出し開始ログ
        tool_start_time = datetime.utcnow()

        tool_call_data = {
            "tool_name": tool_name,
            "start_time": tool_start_time,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys()),
        }

        log_data = {
            "event": "tool_call_start",
            "session_id": self.session_id,
            "tool_name": tool_name,
            "timestamp": tool_start_time.isoformat(),
            "call_number": len(self.tool_calls) + 1,
        }

        self.logger.info(
            f"ツール実行開始: {tool_name} [{self.session_id}]",
            extra={"structured_data": log_data},
        )

        try:
            # ツール実行
            result = await call_func(tool_name, *args, **kwargs)

            # 成功ログ
            tool_end_time = datetime.utcnow()
            duration = (tool_end_time - tool_start_time).total_seconds()

            tool_call_data.update(
                {
                    "end_time": tool_end_time,
                    "duration": duration,
                    "success": True,
                    "result_type": type(result).__name__,
                    "result_length": len(str(result)) if result else 0,
                }
            )

            success_log_data = {
                "event": "tool_call_success",
                "session_id": self.session_id,
                "tool_name": tool_name,
                "duration": duration,
                "timestamp": tool_end_time.isoformat(),
            }

            self.logger.info(
                f"ツール実行成功: {tool_name} ({duration:.2f}s) [{self.session_id}]",
                extra={"structured_data": success_log_data},
            )

            self.tool_calls.append(tool_call_data)
            return result

        except Exception as e:
            # エラーログ
            tool_end_time = datetime.utcnow()
            duration = (tool_end_time - tool_start_time).total_seconds()

            tool_call_data.update(
                {
                    "end_time": tool_end_time,
                    "duration": duration,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            error_log_data = {
                "event": "tool_call_error",
                "session_id": self.session_id,
                "tool_name": tool_name,
                "duration": duration,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": tool_end_time.isoformat(),
            }

            self.logger.error(
                f"ツール実行失敗: {tool_name} ({duration:.2f}s) - {e} [{self.session_id}]",
                extra={"structured_data": error_log_data},
            )

            self.tool_calls.append(tool_call_data)
            raise

    async def after_model(self, response: str, context: Any) -> str:
        """モデル応答後ログ"""
        result = await super().after_model(response, context)

        model_duration = self.end_timer("model_call")

        log_data = {
            "event": "model_call_complete",
            "session_id": self.session_id,
            "response_length": len(result),
            "estimated_tokens": len(result.split()) * 1.3,  # 概算
            "duration": model_duration,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if self.include_responses:
            log_data["response"] = result

        self.logger.info(
            f"モデル応答完了 ({model_duration:.2f}s) [{self.session_id}]",
            extra={"structured_data": log_data},
        )

        return result

    async def after_agent(self, result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """エージェント処理完了ログ"""
        result = await super().after_agent(result, context)

        # セッション統計を計算
        end_time = datetime.utcnow()
        total_duration = (end_time - self.metrics["start_time"]).total_seconds()

        # ツール統計
        successful_tools = [tc for tc in self.tool_calls if tc.get("success")]
        failed_tools = [tc for tc in self.tool_calls if not tc.get("success")]

        tool_stats = {}
        for tool_call in self.tool_calls:
            tool_name = tool_call["tool_name"]
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "success_count": 0,
                }

            tool_stats[tool_name]["count"] += 1
            tool_stats[tool_name]["total_duration"] += tool_call.get("duration", 0)
            if tool_call.get("success"):
                tool_stats[tool_name]["success_count"] += 1

        # 平均実行時間を計算
        for stats in tool_stats.values():
            stats["average_duration"] = stats["total_duration"] / stats["count"]
            stats["success_rate"] = stats["success_count"] / stats["count"]

        # 最終ログ
        session_summary = {
            "event": "agent_complete",
            "session_id": self.session_id,
            "total_duration": total_duration,
            "success": result.get("success", False),
            "tools_used": len(self.tool_calls),
            "successful_tools": len(successful_tools),
            "failed_tools": len(failed_tools),
            "tool_statistics": tool_stats,
            "end_timestamp": end_time.isoformat(),
        }

        self.logger.info(
            f"エージェント処理完了 [{self.session_id}] - "
            f"総時間: {total_duration:.2f}s, ツール使用: {len(self.tool_calls)}回, "
            f"成功率: {len(successful_tools)}/{len(self.tool_calls)}",
            extra={"structured_data": session_summary},
        )

        # 結果にメトリクスを追加
        result["session_metrics"] = {
            "session_id": self.session_id,
            "total_duration": total_duration,
            "tool_calls": len(self.tool_calls),
            "tool_success_rate": (
                len(successful_tools) / len(self.tool_calls) if self.tool_calls else 1.0
            ),
            "tool_statistics": tool_stats,
        }

        return result

    def get_session_logs(self, session_id: str = None) -> Dict[str, Any]:
        """指定セッションのログを取得"""
        target_session = session_id or self.session_id

        return {
            "session_id": target_session,
            "tool_calls": [tc for tc in self.tool_calls],
            "metrics": self.metrics,
        }
