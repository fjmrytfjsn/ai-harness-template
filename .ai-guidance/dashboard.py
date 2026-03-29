#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Harness Dashboard
リアルタイムモニタリング・管理ダッシュボード
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import logging
from aiohttp import web, WSMsgType
import aiohttp_cors
from typing import Dict, List, Any, Optional

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIHarnessDashboard:
    """AI Harness ダッシュボード"""

    def __init__(self, config_path: str = ".ai-guidance/harness.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.websockets = set()
        self.metrics = {
            "total_requests": 0,
            "skill_usage": {},
            "middleware_performance": {},
            "error_rate": 0.0,
            "uptime_start": datetime.now(),
            "recent_activities": [],
        }

    def load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
        return {}

    def get_project_info(self) -> Dict[str, Any]:
        """プロジェクト情報取得"""
        project = self.config.get("project", {})
        return {
            "name": project.get("name", "AI Harness プロジェクト"),
            "version": project.get("version", "1.0.0"),
            "description": project.get("description", ""),
            "authors": project.get("authors", []),
            "repository": project.get("repository", ""),
        }

    def get_harness_status(self) -> Dict[str, Any]:
        """ハーネス状態取得"""
        harness = self.config.get("harness", {})
        skills = self.scan_skills()
        middleware = self.scan_middleware()

        return {
            "enabled_skills": len(skills["available"]),
            "active_middleware": len(middleware["available"]),
            "context_size": harness.get("context", {}).get("max_tokens", 0),
            "mcp_integrations": len(harness.get("mcp", {}).get("providers", {})),
            "skills": skills,
            "middleware": middleware,
        }

    def scan_skills(self) -> Dict[str, List[str]]:
        """スキルスキャン"""
        skills_dir = Path(".ai-guidance/skills")
        available = []

        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.py"):
                if skill_file.name != "__init__.py":
                    available.append(skill_file.stem)

        return {
            "available": available,
            "total_count": len(available),
            "most_used": self.get_top_skills(),
        }

    def scan_middleware(self) -> Dict[str, List[str]]:
        """ミドルウェアスキャン"""
        middleware_dir = Path(".ai-guidance/middleware")
        available = []

        if middleware_dir.exists():
            for middleware_file in middleware_dir.glob("*.py"):
                if middleware_file.name != "__init__.py":
                    available.append(middleware_file.stem)

        return {"available": available, "total_count": len(available)}

    def get_top_skills(self, limit: int = 5) -> List[Dict[str, Any]]:
        """よく使用されるスキル取得"""
        skills_usage = self.metrics["skill_usage"]
        sorted_skills = sorted(skills_usage.items(), key=lambda x: x[1], reverse=True)

        return [
            {"name": name, "usage_count": count}
            for name, count in sorted_skills[:limit]
        ]

    def get_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクス取得"""
        uptime = datetime.now() - self.metrics["uptime_start"]

        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": self.format_duration(uptime),
            "total_requests": self.metrics["total_requests"],
            "error_rate": self.metrics["error_rate"],
            "avg_response_time": self.calculate_avg_response_time(),
            "memory_usage": self.get_memory_usage(),
            "recent_activities": self.metrics["recent_activities"][-10:],  # 最新10件
        }

    def format_duration(self, duration: timedelta) -> str:
        """期間のフォーマット"""
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}日 {hours}時間 {minutes}分"
        elif hours > 0:
            return f"{hours}時間 {minutes}分 {seconds}秒"
        else:
            return f"{minutes}分 {seconds}秒"

    def calculate_avg_response_time(self) -> float:
        """平均レスポンス時間計算"""
        # 実際の実装では middleware からのデータを使用
        return 1.2  # デモ用

    def get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量取得"""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2),
            }
        except ImportError:
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}

    def log_activity(self, activity: str, details: str = ""):
        """アクティビティログ"""
        activity_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "details": details,
        }
        self.metrics["recent_activities"].append(activity_entry)

        # 最新100件のみ保持
        if len(self.metrics["recent_activities"]) > 100:
            self.metrics["recent_activities"] = self.metrics["recent_activities"][-100:]

    async def websocket_handler(self, request):
        """WebSocket ハンドラー"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websockets.add(ws)
        logger.info("新しい WebSocket 接続")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "get_status":
                        await self.send_status_update(ws)
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket エラー: {ws.exception()}")
        finally:
            self.websockets.discard(ws)
            logger.info("WebSocket 接続終了")

        return ws

    async def send_status_update(self, ws=None):
        """状態更新送信"""
        status_data = {
            "type": "status_update",
            "timestamp": datetime.now().isoformat(),
            "project": self.get_project_info(),
            "harness": self.get_harness_status(),
            "metrics": self.get_system_metrics(),
        }

        message = json.dumps(status_data, ensure_ascii=False, default=str)

        if ws:
            await ws.send_str(message)
        else:
            # 全接続に送信
            for websocket in self.websockets.copy():
                try:
                    await websocket.send_str(message)
                except Exception as e:
                    logger.error(f"WebSocket 送信エラー: {e}")
                    self.websockets.discard(websocket)

    async def periodic_status_broadcast(self):
        """定期的な状態配信"""
        while True:
            await asyncio.sleep(5)  # 5秒ごと
            if self.websockets:
                await self.send_status_update()

    def get_dashboard_html(self) -> str:
        """ダッシュボード HTML 生成"""
        project_info = self.get_project_info()

        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Harness Dashboard - {project_info['name']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #4a5568; margin-bottom: 10px; }}
        .header .subtitle {{ color: #718096; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h3 {{ color: #4a5568; margin-bottom: 15px; display: flex; align-items: center; }}
        .card .icon {{ margin-right: 8px; }}
        .metric {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .metric-value {{ font-weight: bold; color: #2d3748; }}
        .status-indicator {{ 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            margin-right: 8px;
        }}
        .status-active {{ background-color: #48bb78; }}
        .status-inactive {{ background-color: #f56565; }}
        .progress-bar {{ 
            background: #e2e8f0; 
            height: 8px; 
            border-radius: 4px; 
            overflow: hidden;
            margin-top: 5px;
        }}
        .progress-fill {{ 
            height: 100%; 
            background: linear-gradient(90deg, #4299e1, #3182ce); 
            transition: width 0.3s;
        }}
        .activity-log {{ max-height: 300px; overflow-y: auto; }}
        .activity-item {{ 
            padding: 8px 0; 
            border-bottom: 1px solid #e2e8f0; 
            font-size: 14px;
        }}
        .activity-time {{ color: #718096; font-size: 12px; }}
        .footer {{ 
            text-align: center; 
            margin-top: 30px; 
            color: rgba(255,255,255,0.8); 
        }}
        .loading {{ text-align: center; color: #718096; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Harness Dashboard</h1>
            <div class="subtitle">{project_info['name']} - リアルタイム監視</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3><span class="icon">📊</span>システム状態</h3>
                <div id="system-status" class="loading">データを読み込み中...</div>
            </div>
            
            <div class="card">
                <h3><span class="icon">⚡</span>ハーネス情報</h3>
                <div id="harness-status" class="loading">データを読み込み中...</div>
            </div>
            
            <div class="card">
                <h3><span class="icon">🎯</span>スキル使用統計</h3>
                <div id="skills-status" class="loading">データを読み込み中...</div>
            </div>
            
            <div class="card">
                <h3><span class="icon">📈</span>パフォーマンス</h3>
                <div id="performance-metrics" class="loading">データを読み込み中...</div>
            </div>
            
            <div class="card" style="grid-column: 1 / -1;">
                <h3><span class="icon">📋</span>最新アクティビティ</h3>
                <div id="activity-log" class="activity-log loading">データを読み込み中...</div>
            </div>
        </div>
        
        <div class="footer">
            <p>AI Harness Dashboard - 最終更新: <span id="last-update">-</span></p>
        </div>
    </div>

    <script>
        class DashboardClient {{
            constructor() {{
                this.ws = null;
                this.connect();
            }}
            
            connect() {{
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${{protocol}}//${{window.location.host}}/ws`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {{
                    console.log('WebSocket 接続成功');
                    this.requestStatus();
                }};
                
                this.ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'status_update') {{
                        this.updateDisplay(data);
                    }}
                }};
                
                this.ws.onclose = () => {{
                    console.log('WebSocket 接続終了 - 5秒後に再接続');
                    setTimeout(() => this.connect(), 5000);
                }};
                
                this.ws.onerror = (error) => {{
                    console.error('WebSocket エラー:', error);
                }};
            }}
            
            requestStatus() {{
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {{
                    this.ws.send(JSON.stringify({{ type: 'get_status' }}));
                }}
            }}
            
            updateDisplay(data) {{
                document.getElementById('last-update').textContent = new Date().toLocaleString('ja-JP');
                
                // システム状態
                const systemHtml = `
                    <div class="metric">
                        <span>稼働時間</span>
                        <span class="metric-value">${{data.metrics.uptime_formatted}}</span>
                    </div>
                    <div class="metric">
                        <span>総リクエスト数</span>
                        <span class="metric-value">${{data.metrics.total_requests.toLocaleString()}}</span>
                    </div>
                    <div class="metric">
                        <span>エラー率</span>
                        <span class="metric-value">${{data.metrics.error_rate.toFixed(2)}}%</span>
                    </div>
                    <div class="metric">
                        <span>メモリ使用量</span>
                        <span class="metric-value">${{data.metrics.memory_usage.rss_mb}} MB</span>
                    </div>
                `;
                document.getElementById('system-status').innerHTML = systemHtml;
                
                // ハーネス状態
                const harnessHtml = `
                    <div class="metric">
                        <span>利用可能スキル</span>
                        <span class="metric-value">${{data.harness.enabled_skills}}</span>
                    </div>
                    <div class="metric">
                        <span>アクティブミドルウェア</span>
                        <span class="metric-value">${{data.harness.active_middleware}}</span>
                    </div>
                    <div class="metric">
                        <span>コンテキストサイズ</span>
                        <span class="metric-value">${{data.harness.context_size.toLocaleString()}} tokens</span>
                    </div>
                    <div class="metric">
                        <span>MCP統合数</span>
                        <span class="metric-value">${{data.harness.mcp_integrations}}</span>
                    </div>
                `;
                document.getElementById('harness-status').innerHTML = harnessHtml;
                
                // スキル統計
                const skillsHtml = data.harness.skills.available.map(skill => 
                    `<div class="metric">
                        <span><span class="status-indicator status-active"></span>${{skill}}</span>
                        <span class="metric-value">利用可能</span>
                    </div>`
                ).join('');
                document.getElementById('skills-status').innerHTML = skillsHtml || '<div class="metric">スキルが見つかりません</div>';
                
                // パフォーマンス
                const perfHtml = `
                    <div class="metric">
                        <span>平均レスポンス時間</span>
                        <span class="metric-value">${{data.metrics.avg_response_time.toFixed(2)}}ms</span>
                    </div>
                    <div class="metric">
                        <span>CPU使用率</span>
                        <span class="metric-value">${{data.metrics.memory_usage.percent.toFixed(1)}}%</span>
                    </div>
                `;
                document.getElementById('performance-metrics').innerHTML = perfHtml;
                
                // アクティビティログ
                const activityHtml = data.metrics.recent_activities.map(activity => 
                    `<div class="activity-item">
                        <div>${{activity.activity}} ${{activity.details}}</div>
                        <div class="activity-time">${{new Date(activity.timestamp).toLocaleString('ja-JP')}}</div>
                    </div>`
                ).join('');
                document.getElementById('activity-log').innerHTML = activityHtml || '<div class="activity-item">アクティビティがありません</div>';
            }}
        }}
        
        // ダッシュボード開始
        new DashboardClient();
        
        // 定期的な状態更新要求
        setInterval(() => {{
            if (window.dashboardClient && window.dashboardClient.ws) {{
                window.dashboardClient.requestStatus();
            }}
        }}, 10000); // 10秒ごと
    </script>
</body>
</html>
        """

    async def index_handler(self, request):
        """メインページハンドラー"""
        return web.Response(text=self.get_dashboard_html(), content_type="text/html")

    def create_app(self):
        """Webアプリケーション作成"""
        app = web.Application()

        # CORS設定
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )
            },
        )

        # ルート設定
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/ws", self.websocket_handler)

        # CORS適用
        for route in list(app.router.routes()):
            cors.add(route)

        return app

    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """ダッシュボード開始"""
        self.log_activity("Dashboard Starting", f"ポート {port} で起動中")

        app = self.create_app()

        # バックグラウンドタスク開始
        asyncio.create_task(self.periodic_status_broadcast())

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        self.log_activity("Dashboard Started", f"http://{host}:{port} で利用可能")
        logger.info(f"🎯 AI Harness Dashboard 起動完了: http://{host}:{port}")

        return runner


async def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Harness Dashboard")
    parser.add_argument(
        "--host", default="0.0.0.0", help="ホスト (デフォルト: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="ポート (デフォルト: 8000)"
    )
    parser.add_argument(
        "--config", default=".ai-guidance/harness.yaml", help="設定ファイルパス"
    )

    args = parser.parse_args()

    dashboard = AIHarnessDashboard(config_path=args.config)
    runner = await dashboard.start(host=args.host, port=args.port)

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("ダッシュボードを停止中...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
