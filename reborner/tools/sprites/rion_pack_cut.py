"""ตัดชีตชุดคำสั่งเจนท่า Rion (PROMPT_PACK.md · kwan 16 ต.ค. 2026) → เฟรมขนาดชีต (ร่าง · ยังไม่ย่อ ไม่เข้าเกม)
  python3 tools/sprites/rion_pack_cut.py [ชีต ...]   → assets/sprites/rion_pack_draft/<ชีต>/<แถว>_<ช่อง>.png + index.json
                                                     + docs/art-bible/rion_hires/pack_check/<ชีต>.jpg (ภาพตรวจ มีเลขแถว-ช่อง)
  ภาพเฟรมขนาดชีต ~32 MB ไม่ commit (.gitignore) · สร้างใหม่จากชีตด้วยคำสั่งนี้
หาตัว: ลบพื้นเขียว → ก้อนติดกัน (ปิดรู 2) · ก้อนใหญ่ (> BIG จุด) = ตัวละคร 1 ตัว · จัดแถวตามจุดกลาง y ที่ใกล้กลางแถวของตาราง ROWS
  ก้อนเล็ก (แสง ลูกไฟ วงรูน เศษ) ติดกับตัวที่ใกล้ที่สุด (ระยะกรอบ) · ชีตที่สั่ง "ไม่มีสัญลักษณ์" (DROP_SMALL) ทิ้งก้อนเล็กที่ไม่แตะตัว
ภาพหน้า 16-5 = ตารางเท่ากัน (ตัวชิดกันจนแยกก้อนไม่ได้)"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "docs/art-bible/rion_hires")
OUT = os.path.join(ROOT, "assets/sprites/rion_pack_draft")
CHECK = os.path.join(SRC, "pack_check")
sys.path.insert(0, os.path.dirname(__file__))
from rion_px_weapons import key_green   # ลบพื้นเขียวแบบเดียวกับท่าถืออาวุธ

# ชีต → (ไฟล์, จำนวนแถวในภาพ, ทิ้งก้อนเล็ก) · แถวในภาพนับตามที่ Flow วาดจริง (ไม่ใช่ที่สั่ง)
SHEETS = {
	"14-1": ("flow_trial_v14_1.jpg", 8, False),
	"15-6": ("flow_trial_v15_6.jpg", 6, False),
	"16-1": ("flow_trial_v16_1.jpg", 6, False),
	"16-2": ("flow_trial_v16_2.jpg", 6, False),
	"16-3": ("flow_trial_v16_3.jpg", 6, True),
	"16-4": ("flow_trial_v16_4.jpg", 5, True),
	"16-5": ("flow_trial_v16_5.jpg", 4, False),
	"16-1b": ("flow_trial_v16_1b.jpg", 4, False),
	"15-2": ("flow_trial_v15_2.jpg", 6, False),
	"15-3": ("flow_trial_v15_3.jpg", 6, False),
	"15-4": ("flow_trial_v15_4.jpg", 6, False),
	"15-5": ("flow_trial_v15_5.jpg", 6, False),
	"17-1": ("flow_trial_v17_1.jpg", 7, False),
	"17-2": ("flow_trial_v17_2.jpg", 5, False),
	"17-3": ("flow_trial_v17_3.jpg", 8, False),
	"17-3b": ("flow_trial_v17_3b.png", 2, False),
	"17-1b": ("flow_trial_v17_1b.png", 7, False),
	"17-4b": ("flow_trial_v17_4b.jpg", 4, False),
	"18-1": ("flow_trial_v18_1.jpg", 7, False),
	"M-walkA": ("master_walk_a.jpg", 1, False),   # แบบ master (18 ต.ค.) · สั่งเดินซ้ายแต่ Flow วาดหันขวา นาฬิกาแขนใกล้ → พลิกแล้วได้เดินซ้ายที่นาฬิกาถูกข้าง
	"M-walkB": ("master_walk_b.jpg", 1, False),   # แบบ master · เดินขวา นาฬิกาแขนไกล ถูกต้อง   # ท่าสายคม 7 ท่า (techs.csv ตามลำดับ)   # แถว 4 = ช่องที่ 6 ของแถวเชียร์ที่ Flow ปัดลงบรรทัดใหม่
}
# ชีตที่พื้นไม่ใช่เขียวสดสีเดียว (17-1: Flow วาดพื้นเขียวอ่อนต่างกันทีละแถบ) → ลบพื้นด้วยสีขอบซ้าย/ขวาของแต่ละบรรทัด
BAND_KEY = {"17-1"}
# กลางแถว (y ในชีต) วัดด้วยตา สำหรับชีตที่แถวสูงไม่เท่ากัน (16-1b: กระโดดแบ่ง 4 + 2 ตัว) · ชีตอื่นใช้ตารางเท่ากัน
ROW_CY = {"16-1b": [386, 992, 1649, 2222]}
GRID = {"16-5": 2}   # ชีตที่ตัดเป็นตารางเท่ากัน: จำนวนคอลัมน์
# จำนวนตัวต่อแถวที่นับด้วยตาจากภาพ (ไม่ใช่ที่สั่ง) · ก้อนเกิน (ตำราลอย กล่อง) = รวมเข้าตัวใกล้สุด · ก้อนขาด (ตัวชิดกัน) = ผ่าที่คอลัมน์โปร่งสุด
EXPECT = {"14-1": [6] * 8, "15-6": [4] * 6, "16-1": [6] * 6, "16-2": [5, 6, 6, 6, 6, 5], "16-3": [5] * 6, "16-4": [5, 6, 6, 6, 6],
	"16-1b": [6, 4, 4, 2], "15-2": [5] * 6, "15-3": [5] * 6, "15-4": [5] * 6, "15-5": [5] * 6,
	"17-1": [5] * 7, "17-2": [6, 5, 5, 5, 5], "17-3": [6] * 8, "17-3b": [6, 6], "17-1b": [5] * 6 + [6], "17-4b": [5, 6, 5, 1], "18-1": [6] * 7, "M-walkA": [6], "M-walkB": [6]}
BIG = 6000
# เฟรมที่มือว่าง (อาวุธหาย) → ใช้เฟรมอื่นในแถวเดียวกันแทน (kwan 16 ต.ค. เลือก "1" กับ 15-1: ช่องคืนท่ามือว่าง = ช่อง 1 ยืนถืออาวุธ) · (แถว, ช่อง) นับจาก 0
REUSE = {
	"15-2": {(0, 4): (0, 0), (1, 4): (1, 0), (2, 4): (2, 0), (4, 2): (4, 1)},
	"15-3": {(0, 4): (0, 0), (1, 4): (1, 0), (2, 4): (2, 0), (3, 4): (3, 0)},
	"15-4": {(0, 4): (0, 0), (1, 4): (1, 0), (2, 4): (2, 0), (4, 2): (4, 1)},
	"15-5": {(0, 4): (0, 0), (1, 4): (1, 0), (2, 4): (2, 0), (3, 4): (3, 0)},
}
# 15-6 แถว 2 (ดำ: ตำราลอย · พนมมือ · เรืองส้ม) Flow วาดครึ่งตัวถึงเข็มขัด → ต่อขาจากท่ายืนของสายเดียวกัน (แถว 3 ช่อง 1)
#   วางให้หัวตรงกัน (บนสุดของภาพ) · คอลัมน์ตามกลางลำตัวแถวล่างสุดของภาพครึ่งตัว · ทับขึ้นมา OVERLAP แถวให้รอยตัดหาย
LEGS = {"15-6": {"rows": [1], "donor": (2, 0)}}
OVERLAP = 6
HAND_BAND = 40


def key_band(rgb):
	"""พื้น = สีมัธยฐานของขอบซ้าย/ขวาในบรรทัดเดียวกัน · ใกล้สีนั้น = โปร่ง (ขอบนุ่ม 20–50)"""
	edge = np.concatenate([rgb[:, :12], rgb[:, -12:]], 1)
	bg = np.median(edge, 1)[:, None, :]
	d = np.sqrt(((rgb - bg) ** 2).sum(2))
	a = np.clip((d - 20) / 30.0, 0, 1)
	return rgb.copy(), a


def cut(key):
	fn, nrows, drop = SHEETS[key]
	rgb = np.array(Image.open(os.path.join(SRC, fn)).convert("RGB")).astype(float)
	col, a = (key_band if key in BAND_KEY else key_green)(rgb)
	H, Wd = a.shape
	m = a > 0.5
	frames = []
	if key in GRID:
		nc = GRID[key]
		for r in range(nrows):
			for c in range(nc):
				y0, y1, x0, x1 = r * H // nrows, (r + 1) * H // nrows, c * Wd // nc, (c + 1) * Wd // nc
				frames.append((r, c, (y0, y1, x0, x1), m[y0:y1, x0:x1]))
	else:
		lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
		objs = ndimage.find_objects(lab)
		area = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
		big = [i for i in range(n) if area[i] > BIG]
		cy = lambda i: (objs[i][0].start + objs[i][0].stop) / 2
		cx = lambda i: (objs[i][1].start + objs[i][1].stop) / 2
		rcy = ROW_CY.get(key) or [(r + .5) * H / nrows for r in range(nrows)]
		row_of = {i: min(range(nrows), key=lambda r: abs(cy(i) - rcy[r])) for i in big}
		own = {i: [i] for i in big}
		for i in range(n):
			if i in own or area[i] < 12: continue
			def gap(j):   # ระยะระหว่างกรอบ (0 = ซ้อนกัน)
				a0, b0 = objs[i], objs[j]
				dy = max(0, a0[0].start - b0[0].stop, b0[0].start - a0[0].stop)
				dx = max(0, a0[1].start - b0[1].stop, b0[1].start - a0[1].stop)
				return dx + dy
			j = min(big, key=gap)
			if drop and gap(j) > 0: continue
			own[j].append(i)
		want = EXPECT.get(key)
		for r in range(nrows):
			items = []   # (mask เต็มชีต) ของแต่ละตัว
			for i in sorted([i for i in big if row_of[i] == r], key=cx):
				items.append(np.isin(lab, [k + 1 for k in own[i]]) & m)
			if want:
				n_want = want[r]
				while len(items) > n_want:   # ก้อนเกิน → รวมก้อนเล็กสุดเข้าก้อนข้างที่ใกล้สุด
					k = min(range(len(items)), key=lambda q: items[q].sum())
					xc = lambda q: np.where(items[q].any(0))[0].mean()
					j = min([q for q in range(len(items)) if q != k], key=lambda q: abs(xc(q) - xc(k)))
					items[j] = items[j] | items[k]; items.pop(k)
				while len(items) < n_want:   # ตัวชิดกัน → ผ่าก้อนที่กว้างสุดที่คอลัมน์โปร่งสุดใกล้จุดแบ่งเท่า
					wid = [np.ptp(np.where(it.any(0))[0]) for it in items]
					k = int(np.argmax(wid)); it = items[k]
					xs = np.where(it.any(0))[0]; x0, x1 = xs.min(), xs.max() + 1
					parts = max(2, round((x1 - x0) / (Wd / max(want))))
					parts = min(parts, n_want - len(items) + 1)
					dens = it[:, x0:x1].sum(0).astype(float)
					cuts = [x0]
					for q in range(1, parts):
						t = int((x1 - x0) * q / parts); r0 = max(1, t - (x1 - x0) // (parts * 3)); r1 = min(x1 - x0 - 1, t + (x1 - x0) // (parts * 3))
						cuts.append(x0 + r0 + int(np.argmin(dens[r0:r1])))
					cuts.append(x1)
					new = []
					for q in range(parts):
						piece = it.copy(); piece[:, :cuts[q]] = False; piece[:, cuts[q + 1]:] = False
						new.append(piece)
					items[k:k + 1] = new
			for c, sel_full in enumerate(items):
				ys, xs = np.where(sel_full)
				y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
				frames.append((r, c, (y0, y1, x0, x1), sel_full[y0:y1, x0:x1]))
	d = os.path.join(OUT, key); os.makedirs(d, exist_ok=True)
	for f in os.listdir(d):
		if f.endswith(".png"): os.remove(os.path.join(d, f))
	idx = []
	for r, c, (y0, y1, x0, x1), sel in frames:
		img = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
		img[..., :3] = col[y0:y1, x0:x1].clip(0, 255)
		img[..., 3] = (np.where(sel, a[y0:y1, x0:x1], 0) * 255).astype(np.uint8)
		Image.fromarray(img, "RGBA").save(os.path.join(d, "%d_%d.png" % (r, c)))
		idx.append({"row": r, "col": c, "box": [int(x0), int(y0), int(x1), int(y1)]})
	if key in LEGS:
		fx = LEGS[key]; dr_, dc_ = fx["donor"]
		don = np.array(Image.open(os.path.join(d, "%d_%d.png" % (dr_, dc_)))).astype(float)
		dm = don[..., 3] > 128
		for e in idx:
			if e["row"] not in fx["rows"]: continue
			f = os.path.join(d, "%d_%d.png" % (e["row"], e["col"]))
			tg = np.array(Image.open(f)).astype(float)
			h, w = tg.shape[:2]
			cut_y = h - OVERLAP
			tx = np.where(tg[h - 3, :, 3] > 128)[0]; dx_ = np.where(dm[h - 3])[0]
			# กลางลำตัว: แถวล่างของตำราลอยอาจไม่ถึง → ใช้ก้อนที่กว้างสุดของแถวนั้น
			sh = int(round(tx.mean() - dx_.mean())) if len(tx) and len(dx_) else 0
			H2 = max(h, don.shape[0]); x0 = min(0, sh); W2 = max(w, sh + don.shape[1]) - x0
			out = np.zeros((H2, W2, 4))
			part = don[cut_y:].copy()
			# มือที่ห้อยข้างสะโพกของท่ายืน (ผิว + เส้นขอบรอบ) ใน HAND_BAND แถวแรกใต้รอยต่อ → ลบ ไม่งั้นมือโผล่ข้างกางเกงทั้งที่พนมมืออยู่
			r_, g_, b_ = part[..., 0], part[..., 1], part[..., 2]
			skin = (r_ > 200) & (g_ > 150) & (r_ > b_ + 40) & (part[..., 3] > 128)
			skin[HAND_BAND:] = False
			blue = (b_ > r_ + 50) & (b_ > g_ + 20) & (part[..., 3] > 128)   # กางเกง → ผิวที่อยู่นอกความกว้างกางเกง = มือ (ผิวขาใต้กางเกงอยู่ในความกว้าง)
			bx = np.where(blue[:HAND_BAND].any(0))[0]
			if len(bx):
				Xs = np.arange(part.shape[1])[None, :]
				skin &= (Xs < bx.min() - 2) | (Xs > bx.max() + 2)
			kill = ndimage.binary_dilation(skin, iterations=5); kill[HAND_BAND + 5:] = False
			if len(bx): kill[:, bx.min():bx.max() + 1] = False
			part[kill] = 0
			out[cut_y:don.shape[0], sh - x0:sh - x0 + don.shape[1]] = part
			top = out[:h, -x0:-x0 + w]; a_ = tg[..., 3:4] / 255
			out[:h, -x0:-x0 + w] = tg * a_ + top * (1 - a_)
			Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").save(f)
			e["legs_from"] = "%d_%d" % (dr_, dc_)
		print(key, "ต่อขาแถว", [r + 1 for r in fx["rows"]], "จากแถว %d ช่อง %d" % (dr_ + 1, dc_ + 1))
	for (r, c), (sr, sc) in REUSE.get(key, {}).items():
		Image.open(os.path.join(d, "%d_%d.png" % (sr, sc))).save(os.path.join(d, "%d_%d.png" % (r, c)))
		for e in idx:
			if (e["row"], e["col"]) == (r, c): e["reuse"] = "%d_%d" % (sr, sc)
	if key in REUSE: print(key, "ใช้เฟรมแทนช่องมือว่าง", len(REUSE[key]), "ช่อง")
	json.dump({"sheet": key, "file": fn, "frames": idx}, open(os.path.join(d, "index.json"), "w"), indent=1)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	# ภาพตรวจ: ชีตย่อครึ่ง + กรอบ + เลขแถว-ช่อง (นับจาก 1)
	os.makedirs(CHECK, exist_ok=True)
	im = Image.open(os.path.join(SRC, fn)).convert("RGB")
	dr = ImageDraw.Draw(im)
	for e in idx:
		dr.rectangle(e["box"], outline=(255, 0, 255), width=3)
		dr.text((e["box"][0] + 4, e["box"][1] + 4), "%d-%d" % (e["row"] + 1, e["col"] + 1), fill=(255, 255, 0))
	im.resize((im.width // 2, im.height // 2)).save(os.path.join(CHECK, key + ".jpg"), quality=85)
	per_row = [sum(1 for e in idx if e["row"] == r) for r in range(nrows)]
	print(key, "ตัว", len(idx), "ต่อแถว", per_row)
	return per_row


if __name__ == "__main__":
	for k in (sys.argv[1:] or SHEETS): cut(k)
