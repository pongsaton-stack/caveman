#!/usr/bin/env python3
"""tools/sprites/rion_flow_cut.py — ตัดชีต Google Flow ทดลอง (kwan 15 ต.ค. 2026 · คำสั่งรวมใน FLOW_PIXEL_TRIAL.md) เป็นเฟรม + หน้าเทส

  python3 tools/sprites/rion_flow_cut.py [--page OUT.html]
ชีต docs/art-bible/rion_hires/flow_trial_v1.jpg (1438x2576 · JPG) · ตาราง 8 คอลัมน์ x 11 แถว (เส้นตารางเขียวเข้ม วัดจากภาพ: CX/RY)
ต่อช่อง: ตัดใน เส้นตาราง → ลบเขียว (rion_ref.key) → ทิ้งเศษ < 40 จุด → assets/sprites/rion_flow_draft/<ท่า>_<i>.png (ขนาดช่องเดิม ไม่ย่อ · .gdignore)
"""
import argparse, base64, io, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rion_ref as R
ROOT = R.ROOT
SHEET = os.path.join(ROOT, "docs/art-bible/rion_hires/flow_trial_v1.jpg")
OUT = os.path.join(ROOT, "assets/sprites/rion_flow_draft")
CX = [0, 178, 359, 540, 721, 901, 1082, 1264, 1438]
RY = [3, 232, 463, 693, 926, 1159, 1392, 1627, 1862, 2098, 2337, 2572]
# (ชื่อ, ป้าย, จำนวนเฟรม, ms/เฟรม, วน?, ทิศที่สั่ง) — จังหวะเป็นค่าภาพในหน้าเทส ไม่ใช่ค่าเกม
ROWS = [("idle_battle", "ยืนในศึก", 4, 220, True, "ซ้าย"), ("walk_front", "เดินหน้า", 8, 100, True, "หน้า"),
	("walk_back", "เดินหลัง", 8, 100, True, "หลัง"), ("walk_left", "เดินซ้าย", 8, 100, True, "ซ้าย"),
	("walk_right", "เดินขวา", 8, 100, True, "ขวา"), ("attack_knife", "ฟันมีด", 8, 80, False, "ซ้าย"),
	("hurt", "โดนตี", 6, 90, False, "ซ้าย"), ("kneel", "ล้มคุกเข่า", 6, 110, False, "ซ้าย"),
	("death", "ล้มนอน", 8, 100, False, "ซ้าย"), ("cast", "พนมมือ → คลื่นพลัง", 8, 110, False, "ซ้าย"),
	("run", "วิ่ง", 6, 80, True, "ซ้าย")]


def cut():
	a = np.array(Image.open(SHEET).convert("RGB")).astype(np.int32); os.makedirs(OUT, exist_ok=True)
	for r, (name, _, n, *_x) in enumerate(ROWS):
		for c in range(n):
			x0, x1, y0, y1 = CX[c] + 3, CX[c + 1] - 2, RY[r] + 2, RY[r + 1] - 2
			rgb, al = R.key(a[y0:y1, x0:x1])
			lab, k = ndimage.label(al > .5); sz = ndimage.sum(al > .5, lab, range(1, k + 1))
			for i, s in enumerate(sz):
				if s < 40: al[lab == i + 1] = 0
			al[:3] = 0; al[-3:] = 0; al[:, :3] = 0; al[:, -3:] = 0
			Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), "RGBA").save(os.path.join(OUT, "%s_%d.png" % (name, c)))


def page(path):
	def uri(p):
		b = io.BytesIO(); Image.open(p).save(b, "WEBP", quality=90); return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
	rows = [{"id": n, "label": lab, "ms": ms, "loop": lp, "want": want, "frames": [uri(os.path.join(OUT, "%s_%d.png" % (n, i))) for i in range(k)]}
		for n, lab, k, ms, lp, want in ROWS]
	tpl = open(os.path.join(ROOT, "tools/web/rion_flow_test.tpl.html"), encoding="utf-8").read()
	open(path, "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps({"rows": rows, "sheet": uri(SHEET)})))
	print("หน้าเทส →", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
	ap = argparse.ArgumentParser(); ap.add_argument("--page"); a = ap.parse_args()
	cut()
	if a.page: page(a.page)
