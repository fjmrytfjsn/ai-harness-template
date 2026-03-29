#!/bin/bash

# AI Harness Dashboard 管理スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DASHBOARD_SCRIPT="$PROJECT_ROOT/.ai-guidance/dashboard.py"
PID_FILE="$PROJECT_ROOT/.ai-guidance/dashboard.pid"
LOG_FILE="$PROJECT_ROOT/.ai-guidance/logs/dashboard.log"

cd "$PROJECT_ROOT"

case "${1:-help}" in
    "start")
        echo "🚀 AI Harness Dashboard を起動中..."
        
        # 既に起動中かチェック
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "⚠️  Dashboard は既に起動中です (PID: $PID)"
                echo "   http://localhost:8000 でアクセス可能です"
                exit 0
            else
                echo "古いPIDファイルを削除しています..."
                rm -f "$PID_FILE"
            fi
        fi
        
        # ログディレクトリ作成
        mkdir -p "$(dirname "$LOG_FILE")"
        
        # Python 依存関係確認
        if ! python -c "import aiohttp, aiohttp_cors" 2>/dev/null; then
            echo "📦 Python 依存関係をインストール中..."
            pip install --user aiohttp aiohttp-cors psutil
        fi
        
        # Dashboard 起動
        nohup python "$DASHBOARD_SCRIPT" --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
        DASHBOARD_PID=$!
        echo $DASHBOARD_PID > "$PID_FILE"
        
        # 起動確認（最大10秒待機）
        echo "⏳ 起動を確認中..."
        for i in {1..10}; do
            if curl -s http://localhost:8000 > /dev/null 2>&1; then
                echo "✅ AI Harness Dashboard 起動完了!"
                echo ""
                echo "🎯 アクセス情報:"
                echo "   URL: http://localhost:8000"
                echo "   PID: $DASHBOARD_PID"
                echo "   ログ: $LOG_FILE"
                echo ""
                echo "📊 機能:"
                echo "   - リアルタイム監視"
                echo "   - スキル使用統計"  
                echo "   - パフォーマンスメトリクス"
                echo "   - アクティビティログ"
                exit 0
            fi
            sleep 1
        done
        
        echo "⚠️  Dashboard の起動に時間がかかっています"
        echo "   ログを確認してください: tail -f $LOG_FILE"
        ;;
        
    "stop")
        echo "🛑 AI Harness Dashboard を停止中..."
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                kill $PID
                sleep 2
                
                if ps -p $PID > /dev/null 2>&1; then
                    echo "⚠️  通常停止に失敗、強制停止します..."
                    kill -9 $PID
                fi
                
                rm -f "$PID_FILE"
                echo "✅ Dashboard 停止完了"
            else
                echo "⚠️  Dashboard は起動していません"
                rm -f "$PID_FILE"
            fi
        else
            echo "⚠️  PIDファイルが見つかりません"
        fi
        ;;
        
    "restart")
        echo "🔄 AI Harness Dashboard を再起動中..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    "status")
        echo "📊 AI Harness Dashboard 状態:"
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "   状態: 起動中 (PID: $PID)"
                echo "   URL: http://localhost:8000"
                
                # 接続テスト
                if curl -s http://localhost:8000 > /dev/null 2>&1; then
                    echo "   接続: OK"
                else
                    echo "   接続: 失敗 - サービスが応答しません"
                fi
                
                # プロセス情報
                echo "   プロセス情報:"
                ps -p $PID -o pid,ppid,etime,pcpu,pmem,cmd 2>/dev/null || echo "     プロセス情報を取得できません"
            else
                echo "   状態: 停止中（PIDファイル残存）"
                rm -f "$PID_FILE"
            fi
        else
            echo "   状態: 停止中"
        fi
        
        # ログサイズ
        if [ -f "$LOG_FILE" ]; then
            LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
            echo "   ログサイズ: $LOG_SIZE ($LOG_FILE)"
        fi
        ;;
        
    "logs")
        echo "📋 AI Harness Dashboard ログ:"
        if [ -f "$LOG_FILE" ]; then
            tail -n ${2:-50} "$LOG_FILE"
        else
            echo "   ログファイルが見つかりません: $LOG_FILE"
        fi
        ;;
        
    "open")
        echo "🌐 AI Harness Dashboard を開いています..."
        
        if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            # OS判定してブラウザ起動
            if command -v xdg-open > /dev/null; then
                xdg-open http://localhost:8000
            elif command -v open > /dev/null; then
                open http://localhost:8000
            else
                echo "   手動でブラウザを開いてください: http://localhost:8000"
            fi
        else
            echo "⚠️  Dashboard が起動していません"
            echo "   まず '$0 start' で起動してください"
        fi
        ;;
        
    "help"|*)
        echo "AI Harness Dashboard 管理スクリプト"
        echo ""
        echo "使用方法:"
        echo "  $0 <コマンド> [オプション]"
        echo ""
        echo "コマンド:"
        echo "  start    Dashboard を起動"
        echo "  stop     Dashboard を停止"
        echo "  restart  Dashboard を再起動"
        echo "  status   Dashboard の状態確認"
        echo "  logs     Dashboard のログ表示 [行数=50]"
        echo "  open     Dashboard をブラウザで開く"
        echo "  help     このヘルプを表示"
        echo ""
        echo "例:"
        echo "  $0 start"
        echo "  $0 logs 100"
        echo "  $0 status"
        ;;
esac