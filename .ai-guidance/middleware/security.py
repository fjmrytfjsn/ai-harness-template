"""
セキュリティミドルウェア

PII検出、危険なコマンドの防止、アクセス制御、セキュリティ監査
"""

import re
import hashlib
from typing import List, Dict, Any, Set
from datetime import datetime
from pathlib import Path

from .base import BaseMiddleware


class SecurityMiddleware(BaseMiddleware):
    """セキュリティミドルウェア

    機能:
    - PII（個人識別情報）の検出とマスク
    - 危険なコマンドの実行防止
    - ファイルシステムアクセス制御
    - セキュリティイベントの監査ログ
    - リクエスト頻度制限
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

        # PII検出設定
        self.mask_pii = config.get("mask_pii", True)
        self.pii_replacement = config.get("pii_replacement", "[MASKED]")

        # ファイルアクセス制御
        self.protected_paths = set(
            config.get(
                "protected_paths",
                [
                    "/etc/",
                    "/bin/",
                    "/usr/",
                    "/root/",
                    "/boot/",
                    "C:\\Windows\\",
                    "C:\\Program Files\\",
                    "C:\\Users\\Administrator\\",
                ],
            )
        )

        self.allowed_extensions = set(
            config.get(
                "allowed_extensions",
                [
                    ".txt",
                    ".md",
                    ".py",
                    ".js",
                    ".ts",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".html",
                    ".css",
                    ".sql",
                    ".sh",
                    ".bat",
                    ".xml",
                    ".csv",
                ],
            )
        )

        # セキュリティ監査
        self.audit_log = []
        self.security_events = []

        # レート制限（簡易実装）
        self.request_history = []
        self.max_requests_per_minute = config.get("max_requests_per_minute", 60)

        self._setup_patterns()

    def _setup_patterns(self):
        """セキュリティパターンを設定"""

        # PII検出パターン
        self.pii_patterns = [
            # クレジットカード番号
            (re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"), "クレジットカード番号"),
            # 日本のマイナンバー
            (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "マイナンバー"),
            # アメリカのSSN
            (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
            # 電話番号（日本）
            (re.compile(r"\b(?:0\d{1,4}[- ]?)?\d{1,4}[- ]?\d{4}\b"), "電話番号"),
            # メールアドレス
            (
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
                "メールアドレス",
            ),
            # IPアドレス
            (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "IPアドレス"),
            # パスワード関連（パスワード: XXX の形式）
            (re.compile(r"(?i)(?:password|passwd|pwd)[:\s=]+\S+"), "パスワード"),
            # APIキー・トークン
            (
                re.compile(
                    r"(?i)(?:api[_-]?key|token|secret)[:\s=]+[A-Za-z0-9+/=]{20,}"
                ),
                "APIキー",
            ),
        ]

        # 危険なコマンドパターン
        self.dangerous_commands = [
            # ファイルシステム破壊
            (re.compile(r"rm\s+(-rf?|--recursive)\s+[/\\]"), "ルートディレクトリ削除"),
            (re.compile(r"sudo\s+rm"), "sudo権限での削除"),
            (re.compile(r"format\s+[Cc]:"), "システムドライブフォーマット"),
            # データベース操作
            (re.compile(r"DROP\s+(DATABASE|TABLE)", re.IGNORECASE), "データベース削除"),
            (
                re.compile(r"DELETE\s+FROM.*WHERE\s+1\s*=\s*1", re.IGNORECASE),
                "全データ削除",
            ),
            # ネットワーク攻撃
            (re.compile(r"nmap\s+-"), "ネットワークスキャン"),
            (re.compile(r"wget.*\|\s*sh"), "リモートスクリプト実行"),
            (re.compile(r"curl.*\|\s*(sh|bash)"), "リモートスクリプト実行"),
            # 権限昇格
            (re.compile(r"sudo\s+su"), "権限昇格"),
            (re.compile(r"chmod\s+777"), "ファイル権限全開放"),
            # プロセス操作
            (re.compile(r"kill\s+-9\s+1"), "initプロセス強制終了"),
            (re.compile(r"pkill\s+-f"), "広範囲プロセス終了"),
        ]

        # 機密ファイルパターン
        self.sensitive_files = [
            re.compile(r"\.ssh/"),
            re.compile(r"\.env"),
            re.compile(r"config\.json"),
            re.compile(r"credentials"),
            re.compile(r"\.key$"),
            re.compile(r"\.pem$"),
            re.compile(r"\.p12$"),
        ]

    async def before_agent(
        self, request: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """セキュリティ前処理"""
        result = await super().before_agent(request, context)

        # レート制限チェック
        self._check_rate_limit(context)

        # PII検出とマスク
        message = result.get("message", "")
        if self.mask_pii and message:
            original_message = message
            pii_found = []

            for pattern, pii_type in self.pii_patterns:
                matches = pattern.findall(message)
                if matches:
                    pii_found.append(pii_type)
                    message = pattern.sub(self.pii_replacement, message)

            if pii_found:
                self._log_security_event(
                    "pii_detected",
                    {
                        "pii_types": pii_found,
                        "message_length": len(original_message),
                        "masked_count": len(pii_found),
                    },
                )

                self.log_warning(f"PII検出とマスク実行: {', '.join(pii_found)}")

            result["message"] = message

        return result

    async def wrap_tool_call(self, call_func, tool_name: str, *args, **kwargs):
        """ツール呼び出しセキュリティチェック"""

        # 危険なコマンドチェック（bashツール等）
        if tool_name in ["bash", "shell", "cmd", "powershell"]:
            command = self._extract_command(args, kwargs)
            if command:
                self._check_dangerous_commands(command)

        # ファイル操作セキュリティチェック
        elif tool_name in ["edit", "create", "delete", "move", "copy"]:
            file_path = self._extract_file_path(args, kwargs)
            if file_path:
                self._check_file_access(file_path, tool_name)

        # ネットワークアクセスチェック
        elif tool_name in ["web_fetch", "http_request", "curl"]:
            url = self._extract_url(args, kwargs)
            if url:
                self._check_network_access(url)

        # 実行前ログ
        self._log_security_event(
            "tool_call_attempt",
            {
                "tool_name": tool_name,
                "args_count": len(args),
                "has_kwargs": bool(kwargs),
            },
        )

        try:
            result = await call_func(tool_name, *args, **kwargs)

            # 実行成功ログ
            self._log_security_event("tool_call_success", {"tool_name": tool_name})

            return result

        except SecurityError as e:
            # セキュリティエラーログ
            self._log_security_event(
                "security_violation",
                {
                    "tool_name": tool_name,
                    "violation_type": e.violation_type,
                    "details": str(e),
                },
            )

            self.log_error(f"セキュリティ違反: {e}")
            raise

        except Exception as e:
            # 一般エラーログ
            self._log_security_event(
                "tool_call_error",
                {
                    "tool_name": tool_name,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            raise

    def _check_rate_limit(self, context):
        """レート制限チェック"""
        now = datetime.utcnow()

        # 1分以上古いリクエストを削除
        self.request_history = [
            req_time
            for req_time in self.request_history
            if (now - req_time).total_seconds() < 60
        ]

        # 制限チェック
        if len(self.request_history) >= self.max_requests_per_minute:
            raise SecurityError(
                "レート制限に達しました。1分後に再試行してください。",
                violation_type="rate_limit_exceeded",
            )

        self.request_history.append(now)

    def _check_dangerous_commands(self, command: str):
        """危険なコマンドチェック"""
        for pattern, description in self.dangerous_commands:
            if pattern.search(command):
                raise SecurityError(
                    f"危険なコマンドが検出されました: {description}",
                    violation_type="dangerous_command",
                    details={"command": command, "pattern": description},
                )

    def _check_file_access(self, file_path: str, operation: str):
        """ファイルアクセスチェック"""
        path_obj = Path(file_path).resolve()

        # 保護されたパスチェック
        for protected in self.protected_paths:
            if str(path_obj).startswith(protected):
                raise SecurityError(
                    f"保護されたパスへのアクセス試行: {file_path}",
                    violation_type="protected_path_access",
                    details={"path": file_path, "operation": operation},
                )

        # 機密ファイルチェック
        for pattern in self.sensitive_files:
            if pattern.search(str(path_obj)):
                raise SecurityError(
                    f"機密ファイルへのアクセス試行: {file_path}",
                    violation_type="sensitive_file_access",
                    details={"path": file_path, "operation": operation},
                )

        # ファイル拡張子チェック（書き込み操作の場合）
        if operation in ["create", "edit"] and path_obj.suffix:
            if path_obj.suffix.lower() not in self.allowed_extensions:
                raise SecurityError(
                    f"許可されていないファイル形式: {path_obj.suffix}",
                    violation_type="disallowed_file_type",
                    details={"path": file_path, "extension": path_obj.suffix},
                )

    def _check_network_access(self, url: str):
        """ネットワークアクセスチェック"""

        # 内部IPアドレスへのアクセスチェック
        internal_patterns = [
            re.compile(r"https?://127\."),
            re.compile(r"https?://localhost"),
            re.compile(r"https?://10\."),
            re.compile(r"https?://172\.1[6-9]\."),
            re.compile(r"https?://172\.2[0-9]\."),
            re.compile(r"https?://172\.3[0-1]\."),
            re.compile(r"https?://192\.168\."),
        ]

        for pattern in internal_patterns:
            if pattern.search(url):
                self.log_warning(f"内部ネットワークへのアクセス: {url}")
                # 警告のみ、ブロックはしない
                break

    def _extract_command(self, args, kwargs) -> str:
        """引数からコマンドを抽出"""
        if "command" in kwargs:
            return kwargs["command"]
        if args and isinstance(args[0], str):
            return args[0]
        return ""

    def _extract_file_path(self, args, kwargs) -> str:
        """引数からファイルパスを抽出"""
        if "path" in kwargs:
            return kwargs["path"]
        if "file_path" in kwargs:
            return kwargs["file_path"]
        if args and isinstance(args[0], str):
            return args[0]
        return ""

    def _extract_url(self, args, kwargs) -> str:
        """引数からURLを抽出"""
        if "url" in kwargs:
            return kwargs["url"]
        if args and isinstance(args[0], str) and args[0].startswith("http"):
            return args[0]
        return ""

    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """セキュリティイベントをログ"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "details": details,
        }

        self.security_events.append(event)
        self.audit_log.append(event)

        # 構造化ログとして出力
        self.log_info(
            f"セキュリティイベント: {event_type}", extra={"security_event": event}
        )

    async def after_agent(self, result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """セキュリティ後処理"""
        result = await super().after_agent(result, context)

        # セキュリティサマリーを結果に追加
        security_summary = {
            "events_count": len(self.security_events),
            "violations_count": len(
                [
                    e
                    for e in self.security_events
                    if e["event_type"] == "security_violation"
                ]
            ),
            "pii_detections": len(
                [e for e in self.security_events if e["event_type"] == "pii_detected"]
            ),
        }

        result["security_summary"] = security_summary

        # セキュリティレポートログ
        self.log_info(f"セキュリティサマリー: {security_summary}")

        return result

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """監査ログを取得"""
        return self.audit_log.copy()

    def get_security_events(self) -> List[Dict[str, Any]]:
        """セキュリティイベントを取得"""
        return self.security_events.copy()


class SecurityError(Exception):
    """セキュリティ関連エラー"""

    def __init__(
        self, message: str, violation_type: str = None, details: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.violation_type = violation_type
        self.details = details or {}
