#!/usr/bin/env bash
# tools/blender/start_blender_mcp.sh — เปิด Blender (จอเสมือน) พร้อมตัวเชื่อม MCP ที่พอร์ต 9876 ในเครื่องคลาวด์
#
#   tools/blender/start_blender_mcp.sh          ติดตั้งที่ขาด + เปิด Blender เบื้องหลัง (เรียกซ้ำได้ เปิดอยู่แล้วก็ไม่เปิดซ้ำ)
#   tools/blender/start_blender_mcp.sh --stop   ปิด Blender
#
# ฝั่ง Claude Code ต่อผ่าน .mcp.json (server "blender" = uvx mcp-for-blender) · เครื่องมือ MCP ใช้ได้เมื่อเริ่ม session ใหม่
# Blender 4.0 จาก apt · ปลั๊กอินมาจากแพ็กเกจ mcp-for-blender (MIT) ไม่ได้คัดลอกลง repo · ไม่มีจอ → xvfb-run (ปลั๊กอินไม่รันในโหมด -b)
set -u
VER=2.1.9
PORT=${BLENDER_PORT:-9876}
LOG=${BLENDER_MCP_LOG:-/tmp/blender_mcp.log}
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "--stop" ]; then pkill -x blender && echo "ปิด Blender แล้ว" || echo "ไม่ได้เปิดอยู่"; exit 0; fi
if (exec 3<>/dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then echo "Blender MCP เปิดอยู่แล้วที่พอร์ต $PORT"; exit 0; fi

command -v blender >/dev/null || { echo "ติดตั้ง Blender…"; (sudo -n true 2>/dev/null && SUDO=sudo || SUDO=""; $SUDO apt-get install -y --no-install-recommends blender >/dev/null) || { echo "ติดตั้ง Blender ไม่ได้"; exit 1; }; }
blender --background --python-expr "import requests" >/dev/null 2>&1 || { echo "ติดตั้ง python3-requests ให้ Blender…"; (sudo -n true 2>/dev/null && SUDO=sudo || SUDO=""; $SUDO apt-get install -y --no-install-recommends python3-requests >/dev/null) || { echo "ติดตั้ง python3-requests ไม่ได้"; exit 1; }; }
command -v xvfb-run >/dev/null || { echo "ไม่มี xvfb-run"; exit 1; }
command -v uv >/dev/null || { echo "ไม่มี uv"; exit 1; }
uv tool list 2>/dev/null | grep -q "mcp-for-blender v$VER" || uv tool install -q "mcp-for-blender==$VER" || { echo "ติดตั้ง mcp-for-blender ไม่ได้"; exit 1; }

ADDON=$(find "$(uv tool dir)/mcp-for-blender" -path "*blender_mcp/bundled/addon.py" | head -1)
[ -f "$ADDON" ] || { echo "ไม่เจอ addon.py ในแพ็กเกจ"; exit 1; }

BLENDERMCP_ADDON="$ADDON" BLENDER_PORT=$PORT BLENDERMCP_NO_UPDATE_CHECK=1 DISABLE_TELEMETRY=1 \
	nohup xvfb-run -a blender --python "$HERE/mcp_boot.py" >"$LOG" 2>&1 &
for i in $(seq 1 60); do
	if (exec 3<>/dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then echo "Blender MCP พร้อมที่พอร์ต $PORT (log: $LOG)"; exit 0; fi
	sleep 1
done
echo "Blender ไม่เปิดพอร์ตใน 60 วินาที — ดู $LOG"; tail -20 "$LOG"; exit 1
