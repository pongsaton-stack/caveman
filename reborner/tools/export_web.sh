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
# โปรเจกต์ชั่วคราว (kwan 30 ต.ค. "เอาทุกอย่างที่ทำลงเกม"): รวมฉากท่าห้องทดลอง tests/lab + ภาพร่างที่เกมใช้
#   (px_set · weapon_skin · monsters_px_draft · ฉากหลัง) โดยไม่มี .gdignore → Godot import แล้วแพ็กเข้า pck ได้
P="$OUT/proj"
mkdir -p "$P"
tar -cf - --exclude ./.git --exclude ./.godot --exclude ./docs --exclude ./_bmad --exclude ./.claude --exclude ./tools \
	--exclude ./tests/check --exclude ./tests/measure --exclude ./tests/shots --exclude ./tests/unit --exclude ./tests/out \
	--exclude ./assets/sprites/pixellab_draft --exclude ./assets/sprites/monsters_px_draft . | tar -xf - -C "$P"
mkdir -p "$P/assets/sprites/pixellab_draft" "$P/assets/sprites/monsters_px_draft" "$P/docs/art-bible/pixellab_test" "$P/docs/art-bible/world_concepts"
cp -r assets/sprites/pixellab_draft/px_set assets/sprites/pixellab_draft/weapon_skin "$P/assets/sprites/pixellab_draft/"
cp assets/sprites/monsters_px_draft/*.png "$P/assets/sprites/monsters_px_draft/"
cp docs/art-bible/pixellab_test/bg_*.jpg "$P/docs/art-bible/pixellab_test/"
cp docs/art-bible/world_concepts/r4_battle.jpg docs/art-bible/world_concepts/r5_battle.jpg "$P/docs/art-bible/world_concepts/"
python3 - "$P/export_presets.cfg" <<'PYEOF'
import re, sys
p = sys.argv[1]
e = open(p, encoding='utf-8').read()
e = re.sub(r'exclude_filter=".*?"', 'exclude_filter="addons/gdUnit4/*"', e, count=1)
open(p, 'w', encoding='utf-8').write(e)
PYEOF
"$G" --headless --path "$P" --import > "$OUT/import.log" 2>&1 || true
"$G" --headless --path "$P" --export-release "Web" "$(cd "$OUT/raw" && pwd)/index.html" > "$OUT/export.log" 2>&1 || { tail -20 "$OUT/export.log"; exit 1; }
cp "$OUT/raw/index.js" "$OUT/raw/index.png" "$OUT/raw/index.icon.png" "$OUT/raw/index.apple-touch-icon.png" "$OUT/" 2>/dev/null || true
cp "$OUT/raw/"index*.js "$OUT/"   # index.js + index.audio*.worklet.js (ไม่มี worklet = เสียงไม่โหลด)
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
rm -rf "$OUT/raw" "$P"
ls -la "$OUT"
