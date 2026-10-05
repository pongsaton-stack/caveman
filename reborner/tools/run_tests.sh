#!/usr/bin/env bash
# tools/run_tests.sh — ตรวจ REBORNER ทั้งชุดด้วยคำสั่งเดียว (ใช้ทั้งบนเครื่อง และ CI)
#
#   GODOT=/path/to/godot tools/run_tests.sh            เทสต์ + seed (ค่าเริ่ม)
#   GODOT=... tools/run_tests.sh --sim                  + รัน Sim เก็บผลไว้ tests/out/sim.txt
#   GODOT=... tools/run_tests.sh --shots                + ถ่ายภาพจอจริงทุกสคริปต์ใน tests/shots → tests/out/
#
# tests/unit/ = gdUnit4 (ผ่านเมื่อ exit 0) · เทสต์ใน tests/check/ ผ่านเมื่อ: ออกด้วย 0 · ไม่มี SCRIPT ERROR · ไม่มีบรรทัด "FAIL <...>" · ถ้ามี "FAILS n" ต้อง n = 0
# เทสต์ที่ต้องมีจอ (เปิดฉากจริง/ถ่ายภาพ) ใช้ xvfb-run ถ้ามี ไม่มีก็ข้ามแล้วบอก
# seed: ลายนิ้วมือศึกที่ seed คงที่ ต้องเท่า tests/seed.md5 — เปลี่ยน core/ หรือ data/ แล้วเลขเปลี่ยน = ต้องอธิบายได้และอัปเดตไฟล์นี้พร้อมเหตุผล
# เซฟของเทสต์แยกไฟล์ (REBORNER_SAVE) ไม่แตะเซฟจริงของผู้เล่น
set -u
cd "$(dirname "$0")/.."
G="${GODOT:-godot}"
command -v "$G" >/dev/null 2>&1 || [ -x "$G" ] || { echo "ไม่เจอ Godot — ตั้ง GODOT=/path/to/Godot_v4.7.1"; exit 2; }
export REBORNER_SAVE="user://test_save.json"
OUT=tests/out; mkdir -p "$OUT"
SIM=0; SHOTS=0
for a in "$@"; do case $a in --sim) SIM=1;; --shots) SHOTS=1;; *) echo "ไม่รู้จัก $a"; exit 2;; esac; done
SCREEN_TESTS=" demoend labschools labtest "
XVFB=""; command -v xvfb-run >/dev/null 2>&1 && XVFB="xvfb-run -a"

[ -d .godot ] || { echo "== import ครั้งแรก"; "$G" --headless --path . --import >/dev/null 2>&1; }

run() {   # run <script> <log> <ต้องมีจอ 0/1>
	if [ "$3" = 1 ]; then timeout 300 $XVFB "$G" --path . --rendering-driver opengl3 -s "$1" >"$2" 2>&1
	else timeout 300 "$G" --headless --path . -s "$1" >"$2" 2>&1; fi
}

pass=0; fail=0; skip=0; failed=""
for f in tests/check/*.gd; do
	n=$(basename "$f" .gd); log="$OUT/$n.log"; screen=0
	[[ $SCREEN_TESTS == *" $n "* ]] && screen=1
	if [ $screen = 1 ] && [ -z "$XVFB" ]; then echo "SKIP $n (ต้องมี xvfb-run)"; skip=$((skip+1)); continue; fi
	run "$f" "$log" $screen; rc=$?
	why=""
	[ $rc -ne 0 ] && why="exit $rc"
	grep -q "SCRIPT ERROR" "$log" && why="$why SCRIPT ERROR"
	grep -qE "^FAIL " "$log" && why="$why $(grep -m1 -E '^FAIL ' "$log")"
	fl=$(grep -oE "^FAILS [0-9]+" "$log" | tail -1 | awk '{print $2}')
	[ -n "$fl" ] && [ "$fl" != 0 ] && why="$why FAILS $fl"
	if [ -z "$why" ]; then echo "ok   $n"; pass=$((pass+1)); else echo "FAIL $n —$why (ดู $log)"; fail=$((fail+1)); failed="$failed $n"; fi
done

# gdUnit4 (tests/unit/test_*.gd · extends GdUnitTestSuite) — ผ่านเมื่อ exit 0 · รายงาน HTML/XML ใน tests/out/gdunit
if [ -d addons/gdUnit4 ] && ls tests/unit/test_*.gd >/dev/null 2>&1; then
	timeout 600 "$G" --headless --path . -s res://addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode \
		-a res://tests/unit -c -rd res://tests/out/gdunit >"$OUT/gdunit.log" 2>&1; rc=$?
	sum=$(grep -o "Overall Summary:.*" "$OUT/gdunit.log" | sed 's/\x1b\[[0-9;]*m//g' | head -1)
	if [ $rc = 0 ]; then echo "ok   gdunit · ${sum#Overall Summary: }"; pass=$((pass+1))
	else echo "FAIL gdunit — exit $rc · ${sum#Overall Summary: } (ดู $OUT/gdunit.log)"; fail=$((fail+1)); failed="$failed gdunit"; fi
fi

seed=$(timeout 300 "$G" --headless --path . -s tests/seedcheck.gd 2>/dev/null | grep '|' | md5sum | cut -d' ' -f1)
want=$(cut -d' ' -f1 tests/seed.md5)
if [ "$seed" = "$want" ]; then echo "ok   seed $seed"; pass=$((pass+1)); else echo "FAIL seed $seed (ต้องได้ $want)"; fail=$((fail+1)); failed="$failed seed"; fi

if [ $SIM = 1 ]; then
	timeout 900 "$G" --headless --path . res://scenes/sim.tscn >"$OUT/sim.txt" 2>&1
	echo "sim  → $OUT/sim.txt ($(grep -c . "$OUT/sim.txt") บรรทัด · $(sed -n 2p "$OUT/sim.txt"))"
fi
if [ $SHOTS = 1 ]; then
	if [ -z "$XVFB" ]; then echo "SKIP shots (ต้องมี xvfb-run)"
	else for f in tests/shots/*.gd; do n=$(basename "$f" .gd); run "$f" "$OUT/$n.log" 1; echo "shot $n → exit $? · $(ls $OUT/${n}_*.png 2>/dev/null | wc -l) ภาพ"; done; fi
fi

echo "== ผ่าน $pass · ไม่ผ่าน $fail · ข้าม $skip${failed:+ · ไม่ผ่าน:$failed}"
[ $fail = 0 ]
