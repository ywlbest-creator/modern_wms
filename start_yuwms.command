#!/bin/zsh
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${YU_WMS_PORT:-${PORT:-8765}}"
URL="http://127.0.0.1:${PORT}/"
LOG_FILE="$BASE_DIR/yuwms.log"

echo "YuWMS / YuTMS 一键启动"
echo "程序目录：$BASE_DIR"
echo "访问地址：$URL"
echo

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "检测到服务已在 $PORT 端口运行，直接打开浏览器。"
  open "$URL" >/dev/null 2>&1 || true
  exit 0
fi

cd "$BASE_DIR"
export PORT
python3 app.py >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!

sleep 1

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "启动成功，进程号：$SERVER_PID"
  open "$URL" >/dev/null 2>&1 || true
  echo "默认账号：admin / admin123"
  echo "日志文件：$LOG_FILE"
else
  echo "启动失败，请查看日志：$LOG_FILE"
  exit 1
fi
