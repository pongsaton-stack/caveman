#!/usr/bin/env python3
"""tools/sprites/rion_flow_cut.py — ตัดชีต Google Flow ทดลอง (kwan 15 ต.ค. 2026 · คำสั่งใน FLOW_PIXEL_TRIAL.md) เป็นเฟรม + หน้าเทส

  python3 tools/sprites/rion_flow_cut.py [--page OUT.html]
ชีตอยู่ใน docs/art-bible/rion_hires/flow_trial_<ชุด>.jpg · ตำแหน่งช่อง = เส้นตารางเขียวเข้มที่วัดจากภาพทีละแถว (แต่ละชุด/แถวแบ่งไม่เท่ากัน)
ต่อช่อง: ตัดในเส้นตาราง → ลบเขียว (rion_ref.key) → ทิ้งเศษ < 40 จุด → พลิกซ้าย-ขวาถ้าแถวนั้นหันขวา (ในศึก Rion หันซ้าย) →
  assets/sprites/rion_flow_draft/<ชุด>/<ท่า>_<i>.png (ขนาดช่องเดิม ไม่ย่อ · .gdignore)
"""
import argparse, base64, io, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rion_ref as R
ROOT = R.ROOT
OUT = os.path.join(ROOT, "assets/sprites/rion_flow_draft")


def even(xs, n):   # เส้นตารางเท่ากัน → ช่อง n ช่องแรก
	return [(xs[i], xs[i + 1]) for i in range(n)]


V1_X = [0, 178, 359, 540, 721, 901, 1082, 1264, 1438]
V3_X8 = [0, 177, 358, 538, 719, 900, 1080, 1261, 1438]
V3_X6 = [0, 238, 478, 719, 959, 1200, 1438]
# แถว: (ท่า, ป้าย, ช่อง [(x0,x1)], ms/เฟรม (ดิบ), วน?, ทิศที่สั่ง, หันขวาในภาพ→พลิก?, เฟรมกระทบ/ปล่อย (None = ไม่มี))
SETS = [
	("v3", "รอบ 3 · 15 ต.ค. (11 แถว · สั่งหันซ้าย)", "flow_trial_v3.jpg",
	 [1, 237, 473, 709, 944, 1179, 1413, 1647, 1879, 2111, 2343, 2573], [
		("idle_battle", "ยืนในศึก", even(V3_X8, 4), 220, True, "ซ้าย", True, None),
		("walk_front", "เดินหน้า", even(V3_X8, 8), 100, True, "หน้า", False, None),
		("walk_back", "เดินหลัง", even(V3_X8, 8), 100, True, "หลัง", False, None),
		("walk_left", "เดินซ้าย", even(V3_X8, 8), 100, True, "ซ้าย", False, None),
		("walk_right", "เดินขวา (พลิกจากเดินซ้าย)", even(V3_X8, 8), 100, True, "ขวา", False, None),
		("attack_knife", "ฟันมีด", even(V3_X8, 8), 80, False, "ซ้าย", True, 5),
		("hurt", "โดนตี", even(V3_X6, 5), 90, False, "ซ้าย", True, 0),
		("kneel", "ล้มคุกเข่า", even(V3_X6, 5), 110, False, "ซ้าย", True, 2),
		("death", "ล้มนอน", even(V3_X6, 6), 100, False, "ซ้าย", True, 3),
		("cast", "พนมมือ → คลื่นพลัง", [(0, 187), (187, 389), (389, 608), (608, 959), (959, 1250), (1250, 1438)], 110, False, "ซ้าย", True, 3),
		("run", "วิ่ง", even(V3_X6, 6), 80, True, "ซ้าย", True, None)]),
	("v1", "รอบ 2 · 15 ต.ค. (JPG แรก · สั่งหันซ้าย)", "flow_trial_v1.jpg",
	 [3, 232, 463, 693, 926, 1159, 1392, 1627, 1862, 2098, 2337, 2572], [
		("idle_battle", "ยืนในศึก", even(V1_X, 4), 220, True, "ซ้าย", True, None),
		("walk_front", "เดินหน้า", even(V1_X, 8), 100, True, "หน้า", False, None),
		("walk_back", "เดินหลัง", even(V1_X, 8), 100, True, "หลัง", False, None),
		("walk_left", "เดินซ้าย", even(V1_X, 8), 100, True, "ซ้าย", False, None),
		("walk_right", "เดินขวา", even(V1_X, 8), 100, True, "ขวา", False, None),
		("attack_knife", "ฟันมีด", even(V1_X, 8), 80, False, "ซ้าย", True, 4),
		("hurt", "โดนตี", even(V1_X, 6), 90, False, "ซ้าย", True, 0),
		("kneel", "ล้มคุกเข่า", even(V1_X, 6), 110, False, "ซ้าย", True, 3),
		("death", "ล้มนอน", even(V1_X, 8), 100, False, "ซ้าย", False, 3),
		("cast", "พนมมือ → คลื่นพลัง", even(V1_X, 8), 110, False, "ซ้าย", True, 3),
		("run", "วิ่ง", even(V1_X, 6), 80, True, "ซ้าย", True, None)]),
]


def cut():
	for sid, _, fn, ry, rows in SETS:
		a = np.array(Image.open(os.path.join(ROOT, "docs/art-bible/rion_hires", fn)).convert("RGB")).astype(np.int32)
		d = os.path.join(OUT, sid); os.makedirs(d, exist_ok=True)
		for r, (name, _l, cells, _ms, _lp, _w, flip, _h) in enumerate(rows):
			for c, (cx0, cx1) in enumerate(cells):
				x0, x1, y0, y1 = cx0 + 4, cx1 - 3, ry[r] + 3, ry[r + 1] - 3
				rgb, al = R.key(a[y0:y1, x0:x1])
				lab, k = ndimage.label(al > .5); sz = ndimage.sum(al > .5, lab, range(1, k + 1))
				for i, s in enumerate(sz):
					if s < 40: al[lab == i + 1] = 0
				al[:3] = 0; al[-3:] = 0; al[:, :3] = 0; al[:, -3:] = 0
				im = Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), "RGBA")
				(im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im).save(os.path.join(d, "%s_%d.png" % (name, c)))


WATCH_BAND = (155, 166)   # แถวข้อมือในเฟรมเดินรอบ 3 (นาฬิกาอยู่แถว 159–161 ทุกเฟรม · วัด 15 ต.ค.)


def find_watch(a):
	"""นาฬิกา = ก้อนสีฟ้า 10–120 จุดในแถบข้อมือ ติดผิว ≥ 3 จุด (กางเกงสีฟ้าเหมือนกัน จึงจำกัดแถว)"""
	r, g, b, al = [a[..., k] for k in range(4)]
	skin = (al > 200) & (r > 200) & (g > 150) & (b > 110) & (r - b > 40)
	blue = (al > 200) & (b > r + 10) & (b >= g - 8)
	rows = np.zeros_like(blue); rows[WATCH_BAND[0]:WATCH_BAND[1]] = True; blue &= rows
	near = ndimage.binary_dilation(skin, iterations=3)
	lab, k = ndimage.label(blue)
	return [lab == i for i in range(1, k + 1) if 10 <= (lab == i).sum() <= 120 and ((lab == i) & near).sum() >= 3]


def erase_watch(a):
	"""ลบนาฬิกาทั้งกรอบ (รวมหน้าปัดสีเทาและเส้นขอบบน-ล่าง): กรอบ = ก้อนสีฟ้า ∪ แขนทั้งเส้น ขยายบน-ล่าง 3 แถว
	เติมด้วยแขนจากเหนือกรอบ เลื่อนตามความเอียงของแขน (วัดจากกลางผิวแขนที่ 2 และ 8 แถวเหนือกรอบ) · เติมเฉพาะจุดที่เป็นตัว (ไม่ทาพื้นโปร่ง)"""
	a = a.copy(); hits = find_watch(a); r, g, b, al = [a[..., k] for k in range(4)]
	skin = (al > 200) & (r > 200) & (g > 150) & (b > 110) & (r - b > 40)
	for m in hits:
		ys, xs = np.nonzero(m); y0, y1 = ys.min() - 3, ys.max() + 3
		# กรอบกว้าง = แขนทั้งเส้น (ผิวที่ 3 แถวเหนือนาฬิกา ±8 จากก้อนฟ้า + เส้นขอบ 2) ∪ ก้อนฟ้า · หน้าปัดสีเทาอยู่ฝั่งตรงข้ามก้อนฟ้า
		sk = np.nonzero(skin[y0, xs.min() - 8:xs.max() + 9])[0] + xs.min() - 8
		x0 = min(xs.min() - 2, (sk.min() if len(sk) else xs.min()) - 2); x1 = max(xs.max() + 2, (sk.max() if len(sk) else xs.max()) + 2)
		def arm_cx(y):
			s_ = np.nonzero(skin[y, x0 - 6:x1 + 7])[0]
			return x0 - 6 + s_.mean() if len(s_) else None
		c2, c8 = arm_cx(y0 - 2), arm_cx(y0 - 8)
		slope = (c2 - c8) / 6 if c2 is not None and c8 is not None else 0
		src = a.copy()
		for y in range(y0, y1 + 1):
			sy = y0 - 2; sh = int(round(slope * (y - sy)))
			for x in range(x0, x1 + 1):
				sx = x - sh
				if al[y, x] > 128 and 0 <= sx < a.shape[1] and src[sy, sx, 3] > 128: a[y, x] = src[sy, sx]
	return a, len(hits)


def fix_v3():
	"""แก้ชุดรอบ 3 ด้วยโค้ด (kwan 15 ต.ค. "รู้ว่าผิดทำไมไม่แก้ก่อนส่ง"): เดินซ้ายเฟรม 4 หันขวา → พลิก ·
	เดินขวา (Flow วาดหันซ้าย) → พลิกจากเดินซ้ายที่แก้แล้ว + ลบนาฬิกา (หันขวา ข้อมือซ้ายเป็นแขนไกล)"""
	d = os.path.join(OUT, "v3"); p = lambda n, i: os.path.join(d, "%s_%d.png" % (n, i))
	im = Image.open(p("walk_left", 3)); im.transpose(Image.FLIP_LEFT_RIGHT).save(p("walk_left", 3))
	for i in range(8):
		a = np.array(Image.open(p("walk_left", i))).astype(np.int32)
		a, n = erase_watch(a)
		Image.fromarray(a.astype(np.uint8), "RGBA").transpose(Image.FLIP_LEFT_RIGHT).save(p("walk_right", i))
		print("เดินขวา %d ← เดินซ้าย %d พลิก · ลบนาฬิกา %d ก้อน" % (i, i, n))


def page(path):
	def uri(p):
		b = io.BytesIO(); Image.open(p).save(b, "WEBP", quality=90); return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
	# ข้ามเฟรม 1 ในโหมด 70 เฟรม: ท่าเดินทุกชุด (เฟรม 1 ต่างจากเฟรม 2 39–49% · v1 ยืนด้วย 36%) · วัดแล้ว 15 ต.ค.
	skip0 = lambda sid, n: n.startswith("walk") or (sid == "v1" and n == "idle_battle")
	# ช่องที่ไม่มีตัว Rion (มีแต่คลื่น) ไม่ใส่ในคลิป (ไฟล์ยังเก็บไว้) · v3 cast ช่อง 5
	# คุกเข่ารอบ 3: เฟรม 4–5 สองมือแตะพื้น (คลานสี่ขา ผิดสเปก) → จบที่เฟรม 3 (คุกเข่าข้างเดียว มือวางเข่า) แล้วค้าง
	OMIT = {("v3", "cast"): {4}, ("v3", "kneel"): {3, 4}}
	sets = []
	for sid, label, fn, _ry, rows in SETS:
		d = os.path.join(OUT, sid)
		sets.append({"id": sid, "label": label, "sheet": uri(os.path.join(ROOT, "docs/art-bible/rion_hires", fn)),
			"rows": [{"id": n, "label": lab, "ms": ms, "loop": lp, "want": want, "flipped": fl, "hit": hit, "skip0": skip0(sid, n),
				"frames": [uri(os.path.join(d, "%s_%d.png" % (n, i))) for i in range(len(cells)) if i not in OMIT.get((sid, n), ())]}
				for n, lab, cells, ms, lp, want, fl, hit in rows]})
	tpl = open(os.path.join(ROOT, "tools/web/rion_flow_test.tpl.html"), encoding="utf-8").read()
	import datetime
	built = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%d/%m/%Y %H:%M") + " (เวลาไทย)"   # ป้ายบนหน้า ให้รู้ว่าเห็นรุ่นล่าสุด
	open(path, "w", encoding="utf-8").write(tpl.replace("__BUILT__", built).replace("__DATA__", json.dumps({"sets": sets})))
	print("หน้าเทส →", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
	ap = argparse.ArgumentParser(); ap.add_argument("--page"); a = ap.parse_args()
	cut(); fix_v3()
	if a.page: page(a.page)
