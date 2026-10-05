#!/usr/bin/env bash
# tools/export_web.sh — สร้างเว็บเกมพร้อมเผยแพร่ในโฟลเดอร์เดียว (แทนขั้นตอนมือใน CLAUDE.md "เล่นผ่านเว็บ")
#   GODOT=<godot> tools/export_web.sh <โฟลเดอร์ผลลัพธ์>
# ทำ: export "Web" → gzip index.wasm เป็น index.wasm.gz.wasm → index.pck เป็น index.pck.wasm (โฮสต์รับแค่ชนิดไฟล์มาตรฐาน · ไฟล์ละ ≤15 MB)
#     → ใช้ tools/web/reborner.html เป็น index.html โดยแก้ fileSizes ให้ตรงไฟล์ใหม่ (แก้เฉพาะสำเนาในผลลัพธ์)
# ต้องมี export template เว็บ: tools/get_godot.sh --web
set -eu
cd "$(dirname "$0")/.."
G="${GODOT:?ตั้ง GODOT=/path/to/godot}"; OUT="${1:?ระบุโฟลเดอร์ผลลัพธ์}"
rm -rf "$OUT"; mkdir -p "$OUT/raw"
"$G" --headless --path . --export-release "Web" "$OUT/raw/index.html" > "$OUT/export.log" 2>&1 || { tail -20 "$OUT/export.log"; exit 1; }
cp "$OUT/raw/index.js" "$OUT/raw/index.png" "$OUT/raw/index.icon.png" "$OUT/raw/index.apple-touch-icon.png" "$OUT/" 2>/dev/null || true
cp "$OUT/raw/index.js" "$OUT/"
gzip -9 -c "$OUT/raw/index.wasm" > "$OUT/index.wasm.gz.wasm"
cp "$OUT/raw/index.pck" "$OUT/index.pck.wasm"
PCK=$(stat -c %s "$OUT/raw/index.pck"); WASM=$(stat -c %s "$OUT/raw/index.wasm")
python3 - "$PCK" "$WASM" "$OUT/index.html" <<'EOF'
import re, sys
pck, wasm, out = sys.argv[1], sys.argv[2], sys.argv[3]
s = open('tools/web/reborner.html', encoding='utf-8').read()
s2 = re.sub(r'"index\.pck":\d+', '"index.pck":' + pck, s)
s2 = re.sub(r'"index\.wasm":\d+', '"index.wasm":' + wasm, s2)
open(out, 'w', encoding='utf-8').write(s2)
print('fileSizes: index.pck=%s index.wasm=%s (ใส่ใน index.html ของผลลัพธ์ · tools/web/reborner.html ไม่ถูกแก้)' % (pck, wasm))
EOF
for f in "$OUT"/*.wasm; do sz=$(stat -c %s "$f"); [ "$sz" -le 15728640 ] || echo "เตือน: $(basename "$f") $sz ไบต์ เกิน 15 MB"; done
rm -rf "$OUT/raw"
ls -la "$OUT"
