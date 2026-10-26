#!/usr/bin/env bash
# tools/get_godot.sh — โหลด Godot 4.7.1 (ตัวเดียวกับที่โปรเจกต์ใช้) สำหรับเครื่องที่ยังไม่มี: เซสชันคลาวด์ใหม่ / CI
#   tools/get_godot.sh [โฟลเดอร์]          → <โฟลเดอร์>/Godot_v4.7.1-stable_linux.x86_64 (ค่าเริ่ม ~/.cache/godot)
#   tools/get_godot.sh [โฟลเดอร์] --web    → + export template เว็บ (web_nothreads_release.zip) ลง ~/.local/share/godot/export_templates/4.7.1.stable/
#                                            ไฟล์ template ทั้งชุด 1.28 GB — โหลดเฉพาะเมื่อจะ export เว็บ
# พิมพ์ path ของ Godot บรรทัดสุดท้าย → GODOT=$(tools/get_godot.sh | tail -1)
set -eu
VER=4.7.1
DIR="${1:-$HOME/.cache/godot}"; [ "${1:-}" = "--web" ] && DIR="$HOME/.cache/godot"
WEB=0; for a in "$@"; do [ "$a" = "--web" ] && WEB=1; done
BIN="$DIR/Godot_v${VER}-stable_linux.x86_64"
URL="https://github.com/godotengine/godot/releases/download/${VER}-stable"
mkdir -p "$DIR"
if [ ! -x "$BIN" ]; then
	echo "โหลด Godot $VER …" >&2
	curl -fsSL "$URL/Godot_v${VER}-stable_linux.x86_64.zip" -o "$DIR/godot.zip"
	unzip -oq "$DIR/godot.zip" -d "$DIR" && rm "$DIR/godot.zip" && chmod +x "$BIN"
fi
if [ $WEB = 1 ]; then
	T="$HOME/.local/share/godot/export_templates/${VER}.stable"
	if [ ! -f "$T/web_nothreads_release.zip" ]; then
		echo "โหลด export template (1.28 GB) …" >&2
		mkdir -p "$T"
		curl -fsSL "$URL/Godot_v${VER}-stable_export_templates.tpz" -o "$DIR/tpl.tpz"
		unzip -oq -j "$DIR/tpl.tpz" "templates/web_nothreads_release.zip" "templates/version.txt" -d "$T" && rm "$DIR/tpl.tpz"
	fi
fi
"$BIN" --version >&2
echo "$BIN"
