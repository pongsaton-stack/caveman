"""ชุดท่า Rion ครบจาก prompt pack → พิกเซล 32-bit (kwan 16 ต.ค. เลือก "1": ครบแล้วย่อพิกเซล/ทำคลิป/ลงหน้าเทสทีเดียวทั้งชุด)
อ่าน rion_pack_draft/<ชีต>/<แถว>_<ช่อง>.png (rion_pack_cut.py) + rion_pack_draft/fix/ (rion_pack_fix.py)
→ assets/sprites/rion_pack_px/<คลิป>_<i>.png + index.json · ร่าง ยังไม่เข้าเกม (.gdignore)

ย่อ: ทุกชีตย่อให้ "ตัวยืน" (REF) สูง PX_H = 72 เท่าตัวในเกม · BOX premultiplied · ทึบ > 0.5 · ขอบ 1 จุดผสม #2a1a14 · สีร่วม 40 สีทั้งชุด ไม่ dither (สูตรเดียวกับ rion_flow_cut.build_pixel)
วาง: ผืนสูง CANVAS_H เท้าแถว FEET · กลางหัว (แถวบน 30% ของตัว) ตรงกลางผืนทุกเฟรม (หัวไม่ส่าย) ·
  เฟรมที่ลอยในชีต (กระโดด ล้ม) คงระยะเหนือพื้นตามกรอบในชีต เทียบกับเฟรมที่ต่ำสุดของแถวเดียวกัน
"""
import json
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "assets/sprites/rion_pack_draft")
OUT = os.path.join(ROOT, "assets/sprites/rion_pack_px")
PX_H, PX_COLORS, PORTRAIT_H = 72, 40, 64
CANVAS_H, FEET = 112, 108

# ตัวยืนตรงของแต่ละชีต (เฟรม, สัดส่วนของความสูงยืน) · ชีตที่ไม่มีท่ายืน ใช้ท่าวิ่งหารสัดส่วนที่วัดจาก 17-3 (วิ่ง 290 / ยืนหน้า 17-3 แถว 6)
REF = {"14-1": ("0_0", 1), "15-6": ("0_0", 1), "15-2": ("0_0", 1), "15-3": ("0_0", 1), "15-4": ("0_0", 1), "15-5": ("0_0", 1),
	"16-1": ("0_0", 1), "16-1b": ("2_0", 1), "16-2": ("0_0", 1), "16-3": ("0_0", 1), "16-4": ("0_0", 1),
	"17-1b": ("0_0", 1), "17-2": ("0_5", 1), "17-3b": ("0_0", None)}
# 16-1b วาดแถววิ่งหลังเล็กกว่าแถวกระโดด (ตัวยืนหน้า 2_0) → แถว 0 ใช้อัตราของตัวเอง: วิ่งหลัง ÷ สัดส่วนวิ่ง/ยืนแบบ 17-3b
ROW_REF = {("16-1b", "0"): "0_0"}
# ไฟล์ fix/ ใช้อัตราย่อของชีตที่เป็นฐาน
FIX_BASE = {"fan": "15-4", "hurt": "17-2", "cheer": "17-2"}

ATK, RUN, IDLE, EMO = 110, 90, 220, 160   # ms ต่อเฟรม (ค่าภาพของหน้าเทส ไม่ใช่ค่าเกม)


def R(sheet, row, cols):
	return [(sheet, f"{row}_{c}") for c in cols]


def F(name, n):
	return [("fix", f"{name}_{i}") for i in range(n)]


G_BATTLE, G_MAGIC, G_FIELD, G_GESTURE, G_MOOD, G_EXTRA = (
	"Rion พิกเซล · ชุดครบ · ท่าศึก", "Rion พิกเซล · ชุดครบ · ร่ายเวทย์", "Rion พิกเซล · ชุดครบ · ยืน/วิ่ง",
	"Rion พิกเซล · ชุดครบ · ท่าทาง", "Rion พิกเซล · ชุดครบ · พัก/อารมณ์", "Rion พิกเซล · ชุดครบ · ศึกเสริม")
FAM = [("SL", "คม"), ("CR", "ทุบ"), ("PC", "แทง"), ("ST", "ยิง"), ("DV", "กล"), ("BD", "มือเปล่า")]
# ถืออาวุธระดับ 2–5: แถวในชีต 15-x ตามลำดับ FAM · แถวที่ Flow วาดผิดแทนด้วย 17-1b / fix (ผลตรวจรอบ 3 ใน PROMPT_PACK.md)
WEAPON = {
	2: {"PC": R("17-1b", 0, range(5))},
	3: {"ST": R("17-1b", 1, range(5)), "BD": R("17-1b", 2, range(5))},
	4: {"SL": F("fan", 5), "ST": R("17-1b", 4, range(5)), "DV": R("17-1b", 5, range(5)), "BD": R("17-1b", 6, [0, 1, 2, 4, 5])},
	5: {},
}

# (กลุ่ม, id, ชื่อ, เฟรม, ms, วน, พลิก)
CLIPS = [
	(G_BATTLE, "idle", "ยืนศึกถือมีด", R("14-1", 0, range(6)), IDLE, True, False),
	(G_BATTLE, "attack", "ฟันมีด (วิ่งเข้า → ฟาด)", R("14-1", 1, range(6)), ATK, False, False),
	(G_BATTLE, "hurt", "โดนตี (มีดแปะด้วยโค้ดช่อง 2–5)", F("hurt", 6), ATK, False, False),
	(G_BATTLE, "down", "ล้ม (17-2 · มีดหลุดมือตอนล้ม)", R("17-2", 1, range(5)), ATK, False, False),
	(G_BATTLE, "run", "วิ่งถือมีด (ตัดช่อง 5 มือว่าง)", R("14-1", 4, [0, 1, 2, 3, 5]), RUN, True, False),
	(G_BATTLE, "cast", "ร่าย พนมมือ → ผลักฝ่ามือ", R("14-1", 5, range(6)), ATK, False, False),
	(G_BATTLE, "kneel", "คุกเข่า", R("14-1", 6, range(6)), ATK, False, False),
	(G_BATTLE, "guard", "ตั้งรับ", R("14-1", 7, range(6)), ATK, False, False),
	(G_MAGIC, "white", "เวทย์ขาว", R("15-6", 0, range(4)), ATK, False, False),
	(G_MAGIC, "black", "เวทย์ดำ (แถวบนต่อขาด้วยโค้ด)", R("15-6", 1, range(4)) + R("15-6", 2, range(4)), ATK, False, False),
	(G_MAGIC, "red", "เวทย์แดง", R("15-6", 3, range(4)), ATK, False, False),
	(G_MAGIC, "summon", "อัญเชิญ", R("15-6", 4, range(4)) + R("15-6", 5, range(4)), ATK, False, False),
	(G_FIELD, "idle_front", "ยืนหายใจ · หน้า", R("16-1", 0, range(6)), IDLE, True, False),
	(G_FIELD, "idle_back", "ยืนหายใจ · หลัง", R("16-1", 1, range(6)), IDLE, True, False),
	(G_FIELD, "run_front", "วิ่ง · หน้า", R("16-1", 2, range(6)), RUN, True, False),
	(G_FIELD, "run_back", "วิ่ง · หลัง (16-1b)", R("16-1b", 0, range(6)), RUN, True, False),
	(G_FIELD, "run_right", "วิ่ง · ขวา (17-3b)", R("17-3b", 0, range(6)), RUN, True, False),
	(G_FIELD, "jump", "กระโดด (16-1b)", R("16-1b", 2, range(4)) + R("16-1b", 3, range(2)), RUN, False, False),
	(G_GESTURE, "wave", "โบกมือ", R("16-2", 0, range(5)), EMO, False, False),
	(G_GESTURE, "nod", "พยักหน้า", R("16-2", 1, range(6)), EMO, False, False),
	(G_GESTURE, "shake", "ส่ายหน้า", R("16-2", 2, range(6)), EMO, False, False),
	(G_GESTURE, "look", "มองหา", R("16-2", 3, range(6)), EMO, False, False),
	(G_GESTURE, "pickup", "เก็บของ", R("16-2", 4, range(6)), EMO, False, False),
	(G_GESTURE, "push", "ผลักลัง (17-3b)", R("17-3b", 1, range(6)), EMO, True, False),
	(G_MOOD, "sit", "นั่ง", R("16-3", 0, range(5)), EMO, False, False),
	(G_MOOD, "sleep", "หลับ (พลิกให้หันขวา)", R("16-3", 1, range(5)), IDLE, False, True),
	(G_MOOD, "surprised", "ตกใจ", R("16-3", 2, range(5)), EMO, False, False),
	(G_MOOD, "confused", "งง", R("16-3", 3, range(5)), EMO, False, False),
	(G_MOOD, "happy", "ดีใจ", R("16-3", 4, range(5)), EMO, False, False),
	(G_MOOD, "angry", "โกรธ", R("16-3", 5, range(5)), EMO, False, False),
	(G_EXTRA, "item", "ใช้ไอเท็ม (ช่อง 2–4 มีดหาย · ยังไม่แก้)", R("16-4", 0, range(5)), EMO, False, False),
	(G_EXTRA, "lowhp", "HP ต่ำ", R("16-4", 1, range(6)), IDLE, True, False),
	(G_EXTRA, "revive", "ฟื้น", R("16-4", 2, range(6)), EMO, False, False),
	(G_EXTRA, "cheer", "เชียร์ (มีดแปะด้วยโค้ดช่อง 2 4 5)", F("cheer", 5), EMO, False, False),
	(G_EXTRA, "insight", "ประกาย (คิดท่าออก)", R("16-4", 4, range(6)), EMO, False, False),
]
for lv in (2, 3, 4, 5):
	for ri, (fam, th) in enumerate(FAM):
		frames = WEAPON[lv].get(fam) or R(f"15-{lv}", ri, range(5))
		CLIPS.append((f"Rion พิกเซล · ชุดครบ · ถืออาวุธ ระดับ {lv}", f"w{lv}_{fam}", f"สาย{th} ระดับ {lv} ({'15-4 + ใบพัดแปะด้วยโค้ด' if frames[0][0] == 'fix' else frames[0][0]})", frames, ATK, False, False))


def key_of(sheet, f):
	r = f.split("_")[0]
	return sheet + "/" + r if (sheet, r) in ROW_REF else sheet


def load(sheet, f):
	return np.array(Image.open(os.path.join(SRC, sheet, f + ".png")).convert("RGBA")).astype(float)


def height(a):
	ys = np.nonzero(a[..., 3].max(1) > 128)[0]
	return ys.max() - ys.min() + 1


def run_frac():   # วิ่ง/ยืน วัดจาก 17-3 (มีทั้งวิ่งขวาแถว 1 และยืนหน้าแถว 6 ในชีตเดียว)
	return height(load("17-3", "0_0")) / height(load("17-3", "5_0"))


def scale_of(sheet):
	if "/" in sheet:   # sheet/row จาก ROW_REF
		s, r = sheet.split("/")
		return PX_H * run_frac() / height(load(s, ROW_REF[(s, r)]))
	sheet = FIX_BASE.get(sheet, sheet)
	if sheet == "17-3b":   # ไม่มีท่ายืน
		return PX_H * run_frac() / height(load("17-3b", "0_0"))
	f, _ = REF[sheet]
	return PX_H / height(load(sheet, f))


def boxes(sheet):
	p = os.path.join(SRC, sheet, "index.json")
	if not os.path.isfile(p):
		return {}
	return {f"{e['row']}_{e['col']}": e["box"] for e in json.load(open(p))["frames"]}


def shrink(a, k):
	al = a[..., 3:] / 255
	pre = a.copy()
	pre[..., :3] *= al
	w, h = max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))
	sm = np.array(Image.fromarray(pre.astype(np.uint8), "RGBA").resize((w, h), Image.BOX)).astype(float)
	A = sm[..., 3] / 255
	rgb = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	m = A > .5
	e = m & ~ndimage.binary_erosion(m)
	rgb[e] = rgb[e] * .35 + np.array([42, 26, 20]) * .65
	return rgb.astype(np.uint8), m


def head_cx(m):
	ys, xs = np.nonzero(m)
	top = ys.min() + 0.3 * (ys.max() - ys.min())
	return xs[ys <= top].mean()


def build():
	shutil.rmtree(OUT, ignore_errors=True)
	os.makedirs(OUT)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	ks = {}
	items, clips = [], []
	for group, cid, label, frames, ms, loop, flip in CLIPS:
		shr = []
		for sheet, f in frames:
			key = f.rsplit("_", 1)[0] if sheet == "fix" else sheet
			if (sheet, f.split("_")[0]) in ROW_REF:
				key = sheet + "/" + f.split("_")[0]
			if key not in ks:
				ks[key] = scale_of(key)
			a = load(sheet, f)
			if flip:
				a = a[:, ::-1]
			rgb, m = shrink(a, ks[key])
			# ลอยเหนือพื้น: ระยะจากขอบล่างกรอบ ถึงขอบล่างต่ำสุดของเฟรมแถวเดียวกันในคลิป
			bx = boxes(sheet).get(f)
			shr.append([rgb, m, sheet, f, bx])
		lows = {}
		for _, _, sheet, f, bx in shr:
			if bx:
				r = (sheet, f.split("_")[0])
				lows[r] = max(lows.get(r, 0), bx[3])
		W = max(s[1].shape[1] for s in shr) + 24
		names = []
		for i, (rgb, m, sheet, f, bx) in enumerate(shr):
			lift = 0
			if bx:
				lift = round((lows[(sheet, f.split("_")[0])] - bx[3]) * ks[key_of(sheet, f)])
			ys = np.nonzero(m.any(1))[0]
			oy = FEET - (ys.max() + 1) - lift
			ox = round(W / 2 - head_cx(m))
			n = f"{cid}_{i}"
			items.append((n, rgb, m, ox, oy, W))
			names.append(n)
		clips.append({"group": group, "id": cid, "label": label, "frames": names, "ms": ms, "loop": loop, "w": W,
			"src": ["%s/%s" % x for x in frames]})
	# ภาพหน้า 16-5 (ครึ่งตัว) สูง PORTRAIT_H
	por = []
	for i in range(8):
		f = f"{i // 2}_{i % 2}"
		a = load("16-5", f)
		rgb, m = shrink(a, PORTRAIT_H / height(a))
		items.append((f"face_{i}", rgb, m, 0, 0, None))
		por.append(f"face_{i}")
	clips.append({"group": "Rion พิกเซล · ชุดครบ · ภาพหน้า", "id": "faces", "label": "ภาพหน้า 8 อารมณ์ (16-5)", "frames": por, "ms": 600, "loop": True, "w": None,
		"src": ["16-5"]})
	pal = Image.fromarray(np.concatenate([r[m] for _, r, m, *_ in items])[None]).quantize(PX_COLORS, method=Image.MEDIANCUT)
	for n, rgb, m, ox, oy, W in items:
		q = np.array(Image.fromarray(rgb).quantize(palette=pal, dither=Image.NONE).convert("RGB"))
		o = np.zeros(rgb.shape[:2] + (4,), np.uint8)
		o[..., :3] = q
		o[..., 3] = m * 255
		im = Image.fromarray(o, "RGBA")
		if W:
			c = Image.new("RGBA", (W, CANVAS_H))
			c.alpha_composite(im, (max(0, ox), max(0, oy)))
			im = c
		im.save(os.path.join(OUT, n + ".png"))
	json.dump({"_doc": "Rion ชุดท่าครบจาก prompt pack (Flow 14-1…17-4b) → พิกเซล · tools/sprites/rion_pack_px.py · ร่าง ยังไม่เข้าเกม",
		"px_h": PX_H, "colors": PX_COLORS, "canvas_h": CANVAS_H, "feet": FEET, "scale": {k: round(v, 4) for k, v in ks.items()}, "clips": clips},
		open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
	print(f"คลิป {len(clips)} · เฟรม {len(items)} · สี {PX_COLORS} · อัตราย่อ", {k: round(v, 3) for k, v in ks.items()})


if __name__ == "__main__":
	build()
