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
DESPILL = {"v6"}   # JPG รอบ 6: ขอบตัวติดสีเขียวผสมเส้นขอบ → ฟ้าอมเขียว (teal) รอบตัว


def despill(rgb, al):
	"""จุดขอบ (ห่างพื้นโปร่ง ≤ 2) ที่เขียว≈น้ำเงิน และเขียวสูงกว่าแดง > 25 = เส้นขอบเข้มที่ปนเขียวพื้น → ทาเป็นสีเส้นขอบ (หมวกน้ำเงิน b >> g ไม่โดน)"""
	rgb = rgb.copy().astype(np.int32); r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
	edge = (al > 0) & ndimage.binary_dilation(al < .5, iterations=2)
	tint = edge & (np.abs(g - b) < 28) & (g - r > 25)
	rgb[tint] = (38, 28, 24)
	return rgb


def even(xs, n):   # เส้นตารางเท่ากัน → ช่อง n ช่องแรก
	return [(xs[i], xs[i + 1]) for i in range(n)]


V1_X = [0, 178, 359, 540, 721, 901, 1082, 1264, 1438]
V3_X8 = [0, 177, 358, 538, 719, 900, 1080, 1261, 1438]
V3_X6 = [0, 238, 478, 719, 959, 1200, 1438]
# แถว: (ท่า, ป้าย, ช่อง [(x0,x1)], ms/เฟรม (ดิบ), วน?, ทิศที่สั่ง, หันขวาในภาพ→พลิก?, เฟรมกระทบ/ปล่อย (None = ไม่มี))
# ชีตไม่มีเส้นตาราง (รอบ 5 · GPT · PNG): ช่อง = None · ry = กลางแถวแต่ละแถว (วัดจากภาพ) → cut_free() แยกตัวละครเอง
V5_ROWS = lambda roll_hit: [
	("walk_front", "เดินหน้า", None, 100, True, "หน้า", False, None),
	("walk_back", "เดินหลัง", None, 100, True, "หลัง", False, None),
	("walk_left", "เดินซ้าย", None, 100, True, "ซ้าย", False, None),
	("kneel", "ล้มคุกเข่า", None, 110, False, "ซ้าย", True, 3),
	("guard", "ตั้งรับ", None, 120, False, "ซ้าย", True, 1),
	("dodge", "หลบ", None, 90, False, "ซ้าย", True, 1),
	("watch", "จับตา", None, 160, True, "ซ้าย", True, None),
	("jump_roll", "กระโดดม้วน → คุกเข่าฟัน", None, 80, False, "ซ้าย", True, roll_hit),
	("victory", "ชนะ เต้นสามช่า", None, 120, True, "หน้า", False, None),
	("walk_right", "เดินขวา (พลิกจากเดินซ้าย)", None, 100, True, "ขวา", False, None)]   # ไม่อยู่ในชีต: fix_free() สร้าง (cut_free ข้ามเพราะไม่มีแถว)
# kwan 15 ต.ค. เลือกชีต A (v5a) เป็นฐานต่อยอด → อยู่แรกสุด = ชุดที่หน้าเทสเปิดก่อน
# รอบ 6 (Google Flow · JPG 1376x768): สั่ง 9 แถว x 8 แต่ได้ตาราง 7 แถว x 14 ช่อง · ท่าละ 7 ช่อง (ครึ่งแถว) · บางท่ามา 2 ชุด
# ช่อง = (x0, x1, แถวในชีต) · เส้นตารางวัดจากภาพ
V6_X = [0, 97, 195, 294, 392, 490, 589, 688, 786, 885, 984, 1082, 1180, 1278, 1375]
V6_Y = [0, 108, 218, 329, 439, 549, 659, 768]
v6 = lambda sr, c0, n=7: [(V6_X[c], V6_X[c + 1], sr) for c in range(c0, c0 + n)]
# รอบ 8-2 (GPT · ต่อจากชีต A · JPG 1438x2576 · ไม่มีเส้นตาราง): ร่าย · คุกเข่า · ตั้งรับ · ม้วนฟันสองมือ · สามช่า · ตัวสูง ~360 (ชีต A ~155)
V8B_ROWS = [
	("cast", "ร่าย: พนมมือ → ผลักปล่อย", None, 110, False, "ซ้าย", True, 5),
	("kneel", "ล้มคุกเข่า (มือแตะพื้น)", None, 110, False, "ซ้าย", True, 3),
	("guard", "ตั้งรับ ไขว้แขน", None, 120, False, "ซ้าย", True, 4),
	("jump_roll", "กระโดดม้วน → ฟันสองมือ", None, 80, False, "ซ้าย", True, 5),
	("victory", "ชนะ เต้นสามช่า", None, 120, True, "หน้า", False, None)]
# รอบ 8-1 (GPT · ต่อจากชีต A · JPG 1438x2576): ยืนในศึก · ฟันมีด · โดนตี · ล้มนอน · วิ่ง
V8A_ROWS = [
	("idle_battle", "ยืนในศึก", None, 220, True, "ซ้าย", True, None),
	("attack_knife", "ฟันมีด (วิ่งเข้าฟันตามแรง)", None, 80, False, "ซ้าย", True, 4),
	("hurt", "โดนตี", None, 90, False, "ซ้าย", True, 0),
	("death", "ล้มนอน", None, 100, False, "ซ้าย", True, 3),
	("run", "วิ่ง", None, 80, True, "ซ้าย", True, None)]
# ลบส่วนเกินก่อนแยกก้อน (พิกัดชีต x0, y0, x1, y1 · วัดจากภาพ): เฟรมฟัน GPT วาดตัวชูมีดซ้อนอยู่ข้างหลังตัวที่ฟัน → ลบตัวหลัง (ท่าชูมีดมีในเฟรม 4 แล้ว)
# กล่อง (x0, y0, x1, y1) หรือรูปหลายเหลี่ยม [(x, y), ...] · ขอบขวาไล่ตามขอบหมวก/ผมของตัวที่ฟัน (วัดจากภาพขยาย 5 เท่า)
ERASE = {"v8a": [[(753, 480), (1000, 480), (1000, 632), (868, 632), (842, 649), (827, 659), (815, 669), (805, 681),
	(803, 705), (813, 712), (813, 738), (753, 738)]]}
# ก้อนกว้างเกิน 1.8 เท่าของก้อนทั่วไปในแถว = หลายตัวติดกัน → ผ่าที่คอลัมน์ (พิกัดชีต วัดจากภาพ)
# เส้นผ่า = x คงที่ หรือ [(ตั้งแต่ y, x), ...] (เส้นหักตามขอบ)
# ล้มนอน 3 เฟรมท้ายนอนเหลื่อมกัน: ตัวกลางไม่มีขา (ตัวแรกบัง) → ผ่าหลังหมวกตัวแรก (956) และตามขอบแว่นตัวกลาง แล้วตัดตัวกลางทิ้ง (OMIT)
SPLIT = {("v8a", "death"): [[(0, 945), (1795, 949), (1810, 952), (1825, 955), (1890, 953)], [(0, 1160), (1860, 1144)]]}
# ชุดหลัก (kwan 15 ต.ค. "เอาชีต A มาต่อยอด"): ท่าจากชีต A + ท่าจากรอบ 8-2 แทนท่าที่ชีต A พลาด (คุกเข่า ตั้งรับ ม้วนฟัน สามช่า) + ร่ายใหม่
# ไม่ได้ตัดจากชีต — build_main() คัดลอกไฟล์จาก v5a / v8b (ย่อให้เท่าชีต A) · แถว: (ท่า, ป้าย, ชุดต้นทาง, ms, วน, ทิศ, พลิก, กระทบ)
MAIN_FROM = {"cast": "v8b", "kneel": "v8b", "guard": "v8b", "jump_roll": "v8b", "victory": "v8b",
	"idle_battle": "v8a", "attack_knife": "v8a", "hurt": "v8a", "death": "v8a", "run": "v8a"}
_rows = {"v5a": {r[0]: r for r in V5_ROWS(5)}, "v8a": {r[0]: r for r in V8A_ROWS}, "v8b": {r[0]: r for r in V8B_ROWS}}
MAIN_ROWS = [_rows[MAIN_FROM.get(n, "v5a")][n] for n in
	["idle_battle", "walk_front", "walk_back", "walk_left", "walk_right", "run", "attack_knife", "hurt", "death", "cast", "kneel", "guard", "dodge", "watch", "jump_roll", "victory"]]
SETS = [
	("main", "★ ชุดหลัก · ชีต A + รอบ 8-2", "flow_trial_v5a.png", None, MAIN_ROWS),
	("v5a", "รอบ 5 ชีต A · GPT (PNG ไม่มีเส้นตาราง)", "flow_trial_v5a.png", [88, 253, 422, 595, 742, 870, 1003, 1101, 1223], V5_ROWS(5)),
	("v8a", "รอบ 8-1 · GPT ต่อจากชีต A (ขนาดเดิม)", "flow_trial_v8a.jpg", [221, 730, 1272, 1755, 2377], V8A_ROWS),
	("v8b", "รอบ 8-2 · GPT ต่อจากชีต A (ขนาดเดิม)", "flow_trial_v8b.jpg", [232, 730, 1274, 1843, 2399], V8B_ROWS),
	("v6", "รอบ 6 · Flow (JPG · 7x14)", "flow_trial_v6.jpg", V6_Y, [
		("walk_front", "เดินหน้า", v6(0, 0, 14), 100, True, "หน้า", False, None),
		("walk_back", "เดินหลัง", v6(1, 0, 14), 100, True, "หลัง", False, None),
		("walk_left", "เดินซ้าย (Flow วาดหันขวา → พลิก)", v6(2, 0), 100, True, "ซ้าย", True, None),
		("kneel", "ล้มคุกเข่า ชุด 1", v6(2, 7), 110, False, "ซ้าย", True, 2),
		("kneel_b", "ล้มคุกเข่า ชุด 2", v6(3, 0), 110, False, "ซ้าย", True, 3),
		("guard", "ตั้งรับ", v6(3, 7), 120, False, "ซ้าย", True, 2),
		("dodge", "หลบ ชุด 1", v6(4, 0), 90, False, "ซ้าย", True, 2),
		("dodge_b", "หลบ ชุด 2", v6(4, 7), 90, False, "ซ้าย", True, 2),
		("jump_roll", "กระโดดม้วน → คุกเข่าฟัน", v6(5, 0), 80, False, "ซ้าย", True, 5),
		("kneel_knife", "ยืน → คุกเข่าถือมีด (ไม่ได้สั่ง)", v6(5, 7), 110, False, "ซ้าย", True, None),
		("watch", "จับตา", v6(6, 0), 160, True, "หน้า", False, None),
		("victory", "ชนะ เต้นสามช่า", v6(6, 7), 120, True, "หน้า", False, None),
		("walk_right", "เดินขวา (เดินซ้าย + ลบนาฬิกา)", None, 100, True, "ขวา", False, None)]),
	("v5b", "รอบ 5 ชีต B · GPT (PNG ไม่มีเส้นตาราง)", "flow_trial_v5b.png", [92, 261, 422, 586, 733, 827, 927, 1024, 1117], V5_ROWS(5)),
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


def cut_free(sid, fn, cen, rows):
	"""ชีตไม่มีเส้นตาราง: ก้อนตัวละคร (ติดกันเมื่อขยาย 2 จุด) → ใส่แถวที่กลางแถวใกล้กลางก้อนที่สุด ·
	ก้อนสูงเกิน 1.4 เท่าของความสูงทั่วไป (สองแถวชนกัน) → ผ่าที่กึ่งกลางระหว่างแถวก่อน · ก้อนเล็ก (< 30% ของก้อนกลางในแถว) รวมเข้าตัวที่ใกล้สุด ·
	ช่องต่อแถว: กว้าง = ตัวกว้างสุด + 16 · สูง = ยอดสุดถึงล่างสุดของทั้งแถว (คงตำแหน่งแนวตั้ง จังหวะกระโดด/หลบไม่หาย) · กลางตัวตรงกลางช่อง · ลบพิกเซลของตัวอื่น"""
	a = np.array(Image.open(os.path.join(ROOT, "docs/art-bible/rion_hires", fn)).convert("RGB")).astype(np.int32)
	rgb, al = R.key(a)
	for e in ERASE.get(sid, []):
		if len(e) == 4 and not isinstance(e[0], tuple): x0, y0, x1, y1 = e; al[y0:y1, x0:x1] = 0; continue
		from PIL import ImageDraw
		pm = Image.new("L", (al.shape[1], al.shape[0]), 0); ImageDraw.Draw(pm).polygon(e, fill=255); al[np.array(pm) > 0] = 0
	m = al > .5; H = m.shape[0]
	mids = [(cen[i] + cen[i + 1]) // 2 for i in range(len(cen) - 1)]; cuts = [0] + mids + [H]
	lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=2))
	parts = []
	for i, sl in enumerate(ndimage.find_objects(lab)):
		pm = (lab == i + 1) & m
		if pm.sum() < 150: continue
		parts.append(pm)
	typ = np.median([np.ptp(np.nonzero(pm)[0]) for pm in parts])
	byrow = [[] for _ in cen]
	for pm in parts:
		ys = np.nonzero(pm)[0]
		pieces = [pm]
		if np.ptp(ys) > 1.4 * typ:   # สองแถวชนกัน → ผ่าตามเส้นกึ่งกลางแถว
			pieces = []
			for y0, y1 in zip(cuts, cuts[1:]):
				q = pm.copy(); q[:y0] = False; q[y1:] = False
				if q.sum() >= 150: pieces.append(q)
		for q in pieces:
			cy = np.nonzero(q)[0].mean(); r = int(np.argmin([abs(cy - c) for c in cen])); byrow[r].append(q)
	d = os.path.join(OUT, sid); os.makedirs(d, exist_ok=True); counts = {}
	fx = (a[..., 2] > a[..., 0] + 60) & (a[..., 1] > 150)   # แสงเอฟเฟกต์ฟ้าสว่าง (ลูกพลัง รอยมีด) — หมวกน้ำเงินเขียวต่ำ ไม่โดน
	def cx(pm):   # กลางตัว = ไม่นับแสงเอฟเฟกต์ (เดิมเฟรมปล่อยลูกพลังจัดกลางรวมแสง ตัวเลื่อน ~20 จุด)
		body = pm & ~fx
		return np.nonzero(body if body.sum() > .5 * pm.sum() else pm)[1].mean()
	for (name, *_r), ps in zip(rows[:len(cen)], byrow):
		flip = _r[5]
		n_split = SPLIT.get((sid, name))
		if n_split:
			wmed = np.median([np.ptp(np.nonzero(q)[1]) for q in ps]); out = []
			for q in ps:
				xs = np.nonzero(q)[1]; x0, x1 = xs.min(), xs.max()
				if x1 - x0 < 1.8 * wmed: out.append(q); continue
				Y, X = np.indices(q.shape)
				def bx(c):   # เส้นผ่าเป็นค่า x ต่อแถว
					if not isinstance(c, list): return np.full(q.shape[0], c)
					v = np.zeros(q.shape[0], int)
					for y_from, x in c: v[y_from:] = x
					return v
				cuts = [np.full(q.shape[0], x0)] + [bx(c) for c in n_split] + [np.full(q.shape[0], x1 + 1)]
				for c0, c1 in zip(cuts, cuts[1:]):
					piece = q & (X >= c0[:, None]) & (X < c1[:, None])
					# เศษของตัวข้างเคียงที่ติดขอบผ่า: กร่อน 2 → เก็บก้อนใหญ่สุด → คืนขอบเฉพาะที่ติดก้อนนั้น
					core = ndimage.binary_erosion(piece, iterations=2); lb, kk = ndimage.label(core)
					if kk > 1:
						big = lb == 1 + int(np.argmax(ndimage.sum(core, lb, range(1, kk + 1))))
						piece &= ndimage.binary_dilation(big, iterations=3)
					if piece.sum() >= 150: out.append(piece)
			ps = out
		med = np.median([q.sum() for q in ps]); main = [q.copy() for q in ps if q.sum() >= .3 * med]
		for q in ps:
			if q.sum() < .3 * med:
				j = min(range(len(main)), key=lambda t: abs(cx(main[t]) - cx(q))); main[j] |= q
		frames = sorted(main, key=cx)
		ys = np.concatenate([np.nonzero(f)[0] for f in frames]); y0, y1 = ys.min() - 4, ys.max() + 5
		W = int(max(np.ptp(np.nonzero(f)[1]) for f in frames)) + 17
		for c, f in enumerate(frames):
			fm = ndimage.binary_dilation(f, iterations=2) & (al > 0)
			c0 = int(round(cx(f) - W / 2)); out = np.zeros((y1 - y0, W, 4), np.uint8)
			for x in range(W):
				sx = c0 + x
				if 0 <= sx < a.shape[1]:
					out[:, x, :3] = rgb[y0:y1, sx]; out[:, x, 3] = np.where(fm[y0:y1, sx], al[y0:y1, sx] * 255, 0)
			im = Image.fromarray(out, "RGBA")
			(im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im).save(os.path.join(d, "%s_%d.png" % (name, c)))
		for c in range(len(frames), 40):   # ลบไฟล์เก่าที่เกินจำนวนเฟรมรอบนี้
			p_ = os.path.join(d, "%s_%d.png" % (name, c))
			if os.path.exists(p_): os.remove(p_)
		counts[name] = len(frames)
	return counts


def cut():
	for sid, _, fn, ry, rows in SETS:
		if sid == "main": continue   # ไม่ได้ตัดจากชีต (build_main)
		if rows[0][2] is None:
			print(sid, cut_free(sid, fn, ry, rows)); continue
		a = np.array(Image.open(os.path.join(ROOT, "docs/art-bible/rion_hires", fn)).convert("RGB")).astype(np.int32)
		d = os.path.join(OUT, sid); os.makedirs(d, exist_ok=True)
		for r, (name, _l, cells, _ms, _lp, _w, flip, _h) in enumerate(rows):
			for c, cell in enumerate(cells or []):   # cells None = สร้างทีหลัง (เดินขวา)
				cx0, cx1 = cell[:2]; sr = cell[2] if len(cell) > 2 else r   # ช่องระบุแถวในชีตเองได้ (รอบ 6)
				x0, x1, y0, y1 = cx0 + 4, cx1 - 3, ry[sr] + 3, ry[sr + 1] - 3
				rgb, al = R.key(a[y0:y1, x0:x1])
				lab, k = ndimage.label(al > .5); sz = ndimage.sum(al > .5, lab, range(1, k + 1))
				for i, s in enumerate(sz):
					if s < 40: al[lab == i + 1] = 0
				al[:3] = 0; al[-3:] = 0; al[:, :3] = 0; al[:, -3:] = 0
				if sid in DESPILL: rgb = despill(rgb, al)
				im = Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), "RGBA")
				(im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im).save(os.path.join(d, "%s_%d.png" % (name, c)))


WATCH_BAND = (155, 166)   # แถวข้อมือในเฟรมเดินรอบ 3 (นาฬิกาอยู่แถว 159–161 ทุกเฟรม · วัด 15 ต.ค.)


def find_watch(a, band=None):
	"""นาฬิกา = ก้อนสีฟ้า 10–120 จุดในแถบข้อมือ ติดผิว ≥ 3 จุด (กางเกงสีฟ้าเหมือนกัน จึงจำกัดแถว)
	band None = แถวคงที่ของรอบ 3 · ชุดอื่นส่ง band ตามสัดส่วนตัว"""
	r, g, b, al = [a[..., k] for k in range(4)]
	band = band or WATCH_BAND
	skin = (al > 200) & (r > 200) & (g > 150) & (b > 110) & (r - b > 40)
	blue = (al > 200) & (b > r + 10) & (b >= g - 8)
	rows = np.zeros_like(blue); rows[band[0]:band[1]] = True; blue &= rows
	near = ndimage.binary_dilation(skin, iterations=3)
	lab, k = ndimage.label(blue)
	hits = [lab == i for i in range(1, k + 1) if 10 <= (lab == i).sum() <= 120 and ((lab == i) & near).sum() >= 3]
	if band is WATCH_BAND: return hits   # ชุดรอบ 5 (band ส่งมา) ใช้แกนฟ้าอ่อนเท่านั้น — ก้อนฟ้าเดิมจับเนคไทได้
	# รอบ 5: หน้าปัดฟ้าอ่อนเกือบขาว (เช่น b1f0f4) + สายเข้มติดเนคไท → ก้อนฟ้าเดิมรวมกับเนคไทจนใหญ่เกิน
	# หาแกนฟ้าอ่อนแทน แล้วขยาย 2 จุดเก็บขอบ/สายเข้มรอบหน้าปัด (ไม่เอาผิว)
	light = (al > 200) & (b > r + 20) & (g > 130) & (b > 160); light &= rows
	lab, k = ndimage.label(ndimage.binary_dilation(light, iterations=1))   # หน้าปัดแตกเป็นจุดห่าง 1 → รวมก้อน
	out = []
	for i in range(1, k + 1):
		m = (lab == i) & light; ys, xs = np.nonzero(m)
		if not (3 <= m.sum() <= 80 and (lab == i).sum() >= 6): continue
		# ข้อมือ = มีผิว (ท่อนแขน) อยู่เหนือแกนภายใน 6 แถว · เข่ามีกางเกงอยู่เหนือ ไม่ผ่าน
		x0 = max(xs.min() - 6, 0); ab = skin[max(ys.min() - 6, 0):ys.min(), x0:xs.max() + 7]
		cols = np.nonzero(ab.any(0))[0] + x0
		if ab.sum() < 4 or cols.max() - cols.min() > 14: continue                 # ท่อนแขนแคบ ไม่ใช่ต้นขา
		if not (cols.min() - 3 <= xs.mean() <= cols.max() + 3): continue          # แกนอยู่ใต้แขน
		out.append(m)
	return sorted(out, key=lambda m: np.nonzero(m)[0].mean())[:1]                     # นาฬิกามีเรือนเดียว · ข้อมืออยู่สูงกว่าเข่า → เอาก้อนบนสุด


def erase_watch_free(a, band):
	"""ชุดรอบ 5 (ตัวเล็ก): ไม่คัดลอกกรอบ (ลากเนคไท/กางเกงมาด้วย) → ทาเฉพาะช่วงแขน
	ขอบแขน = ผิวแถวเหนือและใต้นาฬิกา (ใกล้แกนฟ้า ±7) แทรกค่าทีละแถว · ในช่วง = สีผิวที่ใกล้สุดนอกแถบนาฬิกา · ขอบ = เส้นเข้ม"""
	a = a.copy(); cores = find_watch(a, band); r, g, b, al = [a[..., k] for k in range(4)]
	skin = (al > 200) & (r > 200) & (g > 150) & (b > 110) & (r - b > 40)
	done = 0
	for m in cores:
		ys, xs = np.nonzero(m); y0, y1 = ys.min() - 2, ys.max() + 2; cx = int(xs.mean())
		def span(y):
			for dy in range(0, 6):
				row = np.nonzero(skin[y, cx - 7:cx + 8])[0]
				if 3 <= len(row) and row.max() - row.min() <= 12: return cx - 7 + row.min(), cx - 7 + row.max()
				y += 1 if y > y1 else -1
			return None
		up, dn = span(y0 - 1), span(y1 + 1)
		if up is None and dn is None: continue
		up = up or dn; dn = dn or up
		src = skin.copy(); src[y0:y1 + 1] = False
		_, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
		dark = a[y0 - 1, max(up[0] - 1, 0), :4].copy() if al[y0 - 1, max(up[0] - 1, 0)] > 128 else np.array([40, 26, 20, 255])
		for y in range(y0, y1 + 1):
			t = (y - y0) / max(1, y1 - y0); L = int(round(up[0] + (dn[0] - up[0]) * t)); R = int(round(up[1] + (dn[1] - up[1]) * t))
			for x in range(L, R + 1): a[y, x] = a[iy[y, x], ix[y, x]]
			for x in (L - 1, R + 1):
				if 0 <= x < a.shape[1] and al[y, x] > 128 and not skin[y, x]: a[y, x] = dark
		done += 1
	return a, done


def erase_watch(a, band=None):
	"""ลบนาฬิกาทั้งกรอบ (รวมหน้าปัดสีเทาและเส้นขอบบน-ล่าง): กรอบ = ก้อนสีฟ้า ∪ แขนทั้งเส้น ขยายบน-ล่าง 3 แถว
	เติมด้วยแขนจากเหนือกรอบ เลื่อนตามความเอียงของแขน (วัดจากกลางผิวแขนที่ 2 และ 8 แถวเหนือกรอบ) · เติมเฉพาะจุดที่เป็นตัว (ไม่ทาพื้นโปร่ง)"""
	a = a.copy(); hits = find_watch(a, band); r, g, b, al = [a[..., k] for k in range(4)]
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


def nframes(d, n, cells):   # ชีตมีตาราง = จำนวนช่อง · ชีตไม่มีตาราง = จำนวนไฟล์ที่ cut_free เขียน
	if cells: return len(cells)
	i = 0
	while os.path.exists(os.path.join(d, "%s_%d.png" % (n, i))): i += 1
	return i


def fix_free(sid):
	"""ชุดรอบ 5: เดินขวา = พลิกเดินซ้าย + ลบนาฬิกา · แถบข้อมือ = 58–80% ของความสูงตัว (ตัวเล็กกว่ารอบ 3 แถวคงที่ใช้ไม่ได้)"""
	d = os.path.join(OUT, sid); p = lambda n, i: os.path.join(d, "%s_%d.png" % (n, i)); i = 0; found = []
	while os.path.exists(p("walk_left", i)):
		a = np.array(Image.open(p("walk_left", i))).astype(np.int32); ys = np.nonzero(a[..., 3] > 128)[0]; t, b = ys.min(), ys.max()
		a, n = erase_watch_free(a, (int(t + (b - t) * .58), int(t + (b - t) * .80) + 1)); found.append(n)
		Image.fromarray(a.astype(np.uint8), "RGBA").transpose(Image.FLIP_LEFT_RIGHT).save(p("walk_right", i)); i += 1
	print(sid, "เดินขวา (พลิกเดินซ้าย) ลบนาฬิกาต่อเฟรม", found)
	if sid != "v6": norm_rows(sid)   # รอบ 6 ช่องตารางเท่ากัน หัวขนาดเท่ากันทุกแถว (ท่าในศึกวาดมุม 3/4 → ความกว้างหมวกแคบกว่า วัดแล้วขยายผิด)


# ชีตรอบ 5 วาดแต่ละแถวคนละขนาด (v5b มองไกลสูงแค่ 56% ของท่าเดิน) → ตัวหดตอนสลับท่า
# ปรับทั้งแถวด้วยอัตราเดียว = ค่าเฉลี่ยเรขาคณิตของ (ความสูงเฟรมยืนตรง ÷ ท่าเดิน) กับ (ความกว้างหมวก ÷ ท่าเดิน) · ท่าหันข้างเทียบเดินซ้าย · ท่าหันหน้าเทียบเดินหน้า
NORM_REF = {"kneel": ("walk_left", 0), "guard": ("walk_left", "max"), "dodge": ("walk_left", -1), "watch": ("walk_left", "max"),
	"jump_roll": ("walk_left", -1), "victory": ("walk_front", "max")}


def _hcap(a):
	r, g, b, al = [a[..., k] for k in range(4)]; ys = np.nonzero((al > 128).any(1))[0]; t, bt = ys.min(), ys.max()
	cap = (al > 200) & (b > r + 60) & (b > 110); cap[int(t + (bt - t) * .4):] = False; xs = np.nonzero(cap.any(0))[0]
	return bt - t, (xs.max() - xs.min()) if len(xs) else 0


def norm_rows(sid):
	d = os.path.join(OUT, sid); p = lambda n, i: os.path.join(d, "%s_%d.png" % (n, i))
	def frames(n):
		out = []; i = 0
		while os.path.exists(p(n, i)): out.append(np.array(Image.open(p(n, i)))); i += 1
		return out
	log = []
	for n, (ref, pick) in NORM_REF.items():
		fs = frames(n); rf = [_hcap(a) for a in frames(ref)]
		if not fs: continue
		hc = [_hcap(a) for a in fs]
		h = max(x[0] for x in hc) if pick == "max" else hc[pick][0]
		hr = h / np.median([x[0] for x in rf]); cr = np.median([x[1] for x in hc]) / np.median([x[1] for x in rf])
		k = 1 / np.sqrt(hr * cr)
		if k < 1.08: log.append("%s ×1" % n); continue
		ims = [Image.fromarray(a).resize((round(a.shape[1] * k), round(a.shape[0] * k)), Image.LANCZOS) for a in fs]
		# ตัดให้เหลือกรอบรวมของทั้งแถว + ขอบ 4 (เท้าอยู่ล่างผืนเหมือนเดิม) ไม่ให้ผืนสูงเกินหน้าเทส
		bb = [im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox() for im in ims]
		x0 = min(b[0] for b in bb); x1 = max(b[2] for b in bb); y0 = min(b[1] for b in bb); y1 = max(b[3] for b in bb)
		cx = (x0 + x1) / 2; w = x1 - x0 + 8
		for i, im in enumerate(ims):
			im.crop((int(cx - w / 2), y0 - 4, int(cx - w / 2) + w, y1 + 4)).save(p(n, i))
		log.append("%s ×%.2f" % (n, k))
	print(sid, "ปรับขนาดแถว:", " · ".join(log))


def build_main():
	"""ชุดหลัก = คัดลอก v5a + แถวจาก v8b ย่อด้วยอัตราเดียวต่อทิศ (ข้าง/หน้า) = เฉลี่ยเรขาคณิตของ (สูง ÷ ชีต A) กับ (กว้างหมวก ÷ ชีต A)
	เทียบเฟรมยืนตรงแรกของแถว (ร่าย/คุกเข่า/ตั้งรับ = หันข้าง เทียบเดินซ้าย · สามช่า = หันหน้า เทียบเดินหน้า)"""
	import shutil
	d = os.path.join(OUT, "main"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
	ld = lambda sid, n, i: np.array(Image.open(os.path.join(OUT, sid, "%s_%d.png" % (n, i))))
	cnt = lambda sid, n: nframes(os.path.join(OUT, sid), n, None)
	def k_for(src, ref, rows):
		rf = [_hcap(ld("v5a", ref, i)) for i in range(cnt("v5a", ref))]; nh = [_hcap(ld(src, n, 0)) for n in rows]
		hr = np.median([x[0] for x in nh]) / np.median([x[0] for x in rf]); cr = np.median([x[1] for x in nh]) / np.median([x[1] for x in rf])
		return 1 / np.sqrt(hr * cr)
	ks = {"v8b": k_for("v8b", "walk_left", ["cast", "kneel", "guard"]), "v8b_front": k_for("v8b", "walk_front", ["victory"]),
		"v8a": k_for("v8a", "walk_left", ["death", "attack_knife"])}   # รอบ 8-1 เฟรมยืนตรง = ล้มเฟรม 1 · ฟันเฟรม 1
	for n, *_ in MAIN_ROWS:
		src = MAIN_FROM.get(n, "v5a"); k = 1 if src == "v5a" else ks[src + ("_front" if n == "victory" else "")]
		for i in range(cnt(src, n)):
			im = Image.open(os.path.join(OUT, src, "%s_%d.png" % (n, i)))
			if k != 1: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
			im.save(os.path.join(d, "%s_%d.png" % (n, i)))
	print("ชุดหลัก: ย่อ", " · ".join("%s ×%.3f" % kv for kv in ks.items()))


def page(path):
	def uri(p):
		b = io.BytesIO(); Image.open(p).save(b, "WEBP", quality=90); return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
	# ข้ามเฟรม 1 ในโหมด 70 เฟรม: ท่าเดินทุกชุด (เฟรม 1 ต่างจากเฟรม 2 39–49% · v1 ยืนด้วย 36%) · วัดแล้ว 15 ต.ค.
	skip0 = lambda sid, n: (n.startswith("walk") and sid != "v6") or (sid == "v1" and n == "idle_battle")   # รอบ 6 เดินไม่มีเฟรม 1 โดด (ต่าง 23–54% ทุกคู่)
	# ช่องที่ไม่มีตัว Rion (มีแต่คลื่น) ไม่ใส่ในคลิป (ไฟล์ยังเก็บไว้) · v3 cast ช่อง 5
	# คุกเข่ารอบ 3: เฟรม 4–5 สองมือแตะพื้น (คลานสี่ขา ผิดสเปก) → จบที่เฟรม 3 (คุกเข่าข้างเดียว มือวางเข่า) แล้วค้าง
	OMIT = {("v3", "cast"): {4}, ("v3", "kneel"): {3, 4},
		# รอบ 5: เฟรมท้ายคุกเข่าเป็นคลานสี่ขา → A จบเฟรม 4 (เข่าลง มือใกล้พื้น) · B จบเฟรม 4 (คุกเข่าข้างเดียว มือวางเข่า)
		("v5a", "kneel"): {4}, ("v5b", "kneel"): {4, 5},
		# รอบ 6: คุกเข่าทั้งสองชุดจบคลานสี่ขาอีก → ชุด 1 จบเฟรม 3 (ย่อ เข่าลง มือแตะพื้น) · ชุด 2 จบเฟรม 4 (คุกเข่าข้างเดียว)
		("v6", "kneel"): {3, 4, 5, 6}, ("v6", "kneel_b"): {4, 5, 6},
		# รอบ 8-1: ฟันเฟรม 6 (ตามแรง) หมวกสองใบซ้อนกัน แยกไม่สะอาด · โดนตีเฟรม 1 ถือมีดสองเล่ม
		("v8a", "attack_knife"): {5}, ("v8a", "hurt"): {0}, ("v8a", "death"): {4}}
	omit = lambda sid, n: OMIT.get((sid, n)) or (OMIT.get((MAIN_FROM.get(n, "v5a"), n), ()) if sid == "main" else ())
	sets = []
	for sid, label, fn, _ry, rows in SETS:
		d = os.path.join(OUT, sid)
		sets.append({"id": sid, "label": label, "sheet": uri(os.path.join(ROOT, "docs/art-bible/rion_hires", fn)),
			"rows": [{"id": n, "label": lab, "ms": ms, "loop": lp, "want": want, "flipped": fl, "hit": hit, "skip0": skip0(sid, n),
				"frames": [uri(os.path.join(d, "%s_%d.png" % (n, i))) for i in range(nframes(d, n, cells)) if i not in omit(sid, n)]}
				for n, lab, cells, ms, lp, want, fl, hit in rows]})
	tpl = open(os.path.join(ROOT, "tools/web/rion_flow_test.tpl.html"), encoding="utf-8").read()
	import datetime
	built = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%d/%m/%Y %H:%M") + " (เวลาไทย)"   # ป้ายบนหน้า ให้รู้ว่าเห็นรุ่นล่าสุด
	open(path, "w", encoding="utf-8").write(tpl.replace("__BUILT__", built).replace("__DATA__", json.dumps({"sets": sets})))
	print("หน้าเทส →", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
	ap = argparse.ArgumentParser(); ap.add_argument("--page"); a = ap.parse_args()
	cut(); fix_v3(); fix_free("v5a"); fix_free("v5b"); fix_free("v6"); build_main()
	if a.page: page(a.page)
