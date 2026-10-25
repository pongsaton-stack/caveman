#!/usr/bin/env bash
# tests/lab/build_web.sh — หน้าเว็บของห้องทดลองฉากต่อสู้ Godot (เมนูเลือกท่า 5 · มอน 5 · ฉาก 3 · เสียง · เพลง)
#   GODOT=<godot> tests/lab/build_web.sh <โฟลเดอร์ผลลัพธ์> [res://tests/lab/<ท่า>.tscn]
# ต้องมี export template เว็บ (tools/get_godot.sh --web)
# ทำโปรเจกต์ชั่วคราวใน <out>/proj ที่มีเฉพาะของที่ฉากใช้ (ไม่มี addons/autoload ของเกม) · ภาพร่างคัดลอกไปที่ทางเดิม
#   แต่ไม่มี .gdignore → Godot import ได้ (lab_stage.gd โหลดผ่าน load() เมื่อมีไฟล์ import) · ผลลัพธ์แบบเดียวกับ tools/export_web.sh
set -eu
cd "$(dirname "$0")/../.."
G="${GODOT:?ตั้ง GODOT=/path/to/godot}"; OUT="${1:?ระบุโฟลเดอร์ผลลัพธ์}"; SCENE="${2:-res://tests/lab/jg_bl9.tscn}"
P="$OUT/proj"
rm -rf "$OUT"; mkdir -p "$P/assets/sprites/pixellab_draft/px_set" "$P/assets/sprites/monsters_px_draft" "$P/data" "$P/core" "$P/tests/lab" "$P/docs/art-bible/pixellab_test" "$OUT/raw"
python3 - "$P" "$SCENE" <<'EOF'
import re, sys
p, scene = sys.argv[1], sys.argv[2]
s = open('project.godot', encoding='utf-8').read()
for sec in ('autoload', 'dialogic', 'editor_plugins'):   # ส่วนของเกมที่ห้องทดลองไม่ใช้
	s = re.sub(r'\n\[%s\]\n.*?(?=\n\[|\Z)' % sec, '\n', s, flags=re.S)
s = re.sub(r'run/main_scene=".*?"', 'run/main_scene="%s"' % scene, s)
s = re.sub(r'config/name=".*?"', 'config/name="REBORNER lab"', s)
open(p + '/project.godot', 'w', encoding='utf-8').write(s)
e = open('export_presets.cfg', encoding='utf-8').read()
e = re.sub(r'exclude_filter=".*?"', 'exclude_filter=""', e, count=1)
open(p + '/export_presets.cfg', 'w', encoding='utf-8').write(e)
EOF
cp -r assets/fonts "$P/assets/"
cp data/monsters.csv data/monster_body.csv "$P/data/"
cp data/monsters.csv.import data/monster_body.csv.import "$P/data/" 2>/dev/null || true
cp core/CsvDb.gd "$P/core/"
cp tests/lab/*.gd tests/lab/*.tscn "$P/tests/lab/"
cp assets/sprites/pixellab_draft/px_set/pls_*.png "$P/assets/sprites/pixellab_draft/px_set/"
mkdir -p "$P/assets/sprites/flow_draft/bt"; cp assets/sprites/flow_draft/bt/flw_*.png "$P/assets/sprites/flow_draft/bt/"
for f in M01 M03 M06 M15 B1; do cp assets/sprites/monsters_px_draft/${f}_*.png "$P/assets/sprites/monsters_px_draft/"; done
cp docs/art-bible/pixellab_test/bg_frost_volcano.jpg docs/art-bible/pixellab_test/bg_ash_village.jpg docs/art-bible/pixellab_test/bg_flooded_ruins.jpg "$P/docs/art-bible/pixellab_test/"
mkdir -p "$P/docs/art-bible/audio"; cp docs/art-bible/audio/battle_bgm_preview.mp3 "$P/docs/art-bible/audio/"
"$G" --headless --path "$P" --import > "$OUT/import.log" 2>&1 || true
"$G" --headless --path "$P" --export-release "Web" "$OUT/raw/index.html" > "$OUT/export.log" 2>&1 || { tail -20 "$OUT/export.log"; exit 1; }
cp "$OUT/raw/"index*.js "$OUT/"
cp "$OUT/raw/index.png" "$OUT/raw/index.icon.png" "$OUT/raw/index.apple-touch-icon.png" "$OUT/" 2>/dev/null || true
gzip -9 -c "$OUT/raw/index.wasm" > "$OUT/index.wasm.gz.wasm"
cp "$OUT/raw/index.pck" "$OUT/index.pck.wasm"
PCK=$(stat -c %s "$OUT/raw/index.pck"); WASM=$(stat -c %s "$OUT/raw/index.wasm")
python3 - "$PCK" "$WASM" "$OUT/index.html" <<'EOF'
import re, sys
pck, wasm, out = sys.argv[1], sys.argv[2], sys.argv[3]
s = open('tools/web/reborner.html', encoding='utf-8').read()   # หน้าเว็บเกม: ดัก fetch แปลงชื่อไฟล์ .wasm กลับ
s = re.sub(r'\s*<div id="dpad".*?</div>\s*<div id="pads-right".*?</div>', '\n', s, flags=re.S)   # ห้องทดลองใช้เมาส์/แตะ ไม่ต้องมีปุ่มเดิน
s = re.sub(r'<title>.*?</title>', '<title>ห้องทดลองฉากต่อสู้ Godot</title>', s, flags=re.S)
s = re.sub(r'"index\.pck":\d+', '"index.pck":' + pck, s)
s = re.sub(r'"index\.wasm":\d+', '"index.wasm":' + wasm, s)
open(out, 'w', encoding='utf-8').write(s)
print('fileSizes: index.pck=%s index.wasm=%s' % (pck, wasm))
EOF
for f in "$OUT"/*.wasm; do sz=$(stat -c %s "$f"); [ "$sz" -le 15728640 ] || echo "เตือน: $(basename "$f") $sz ไบต์ เกิน 15 MB"; done
rm -rf "$OUT/raw"
ls -la "$OUT"
