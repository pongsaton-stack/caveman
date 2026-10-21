"""ชุด Rion ในเกมจาก PixelLab (kwan 19 ต.ค. "เปลี่ยนเป็น PixelLab ทั้งชุด") → ภาพสะอาด + คลิปให้หน้า animation test

ภาพดิบ: assets/sprites/pixellab_draft/states/<State>/<State>/animations/<ท่า>_v/west · เดินขึ้น/ลง zip/Idle/animations/walk_v*/{north,south}
PixelLab วาดเส้นฟาด/แสง/ประกายติดมาทั้งที่ห้าม (19 ต.ค.) → ลบด้วยโค้ด:
  สีที่ห่างจากสีของภาพยืน (rotation ทิศเดียวกัน) > 40 หรือสว่างกว่าจุดสว่างสุดของตัว · แล้วเก็บก้อนใหญ่สุด + ก้อนที่แตะก้อนใหญ่ (อาวุธที่ติดมือ)
เฟรมที่ใช้ไม่ได้ (ท่าหายใจกลายเป็นเหวี่ยง · เดินขึ้นหันกลับมาหน้า) ตัดด้วย KEEP · ผืน 120x112 เท้าแถว 108 แบบ rion_pack_px · หันซ้ายตามภาพดิบ
  python3 tools/sprites/pixellab_rion_set.py → assets/sprites/pixellab_draft/px_set/<คลิป>_<i>.png + index.json (หน้า animation test อ่านเอง · ร่าง ยังไม่เข้าเกม)
"""
import glob
import json
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PL = os.path.join(ROOT, "assets/sprites/pixellab_draft")
OUT = os.path.join(PL, "px_set")
G = "★ Rion PixelLab · ชุดในเกม (ร่าง 19 ต.ค.)"
SCHOOL = {"bl": ("fight_knife", "คม · มีด"), "bt": ("BT_A_stance", "ทุบ · ค้อน"), "pt": ("PT_A_stance", "แทง · ไขควง"),
	"rg": ("RG_A_stance", "ยิง · ธนู"), "dv": ("DV_A_stance", "กล · รีโมต"), "fs": ("FS_A_stance", "มือเปล่า · นวม")}
# (คลิป, ชื่อ, State, โฟลเดอร์ท่า, ทิศ, เฟรมที่ใช้ (None = ทั้งหมด), ms, วน)
CLIPS = []
# เฟรมที่ตัด (ตรวจด้วยตา 19 ต.ค.): run_k เฟรม 6–7 ซีดขาว+ประกายวาดติด · fs0 เฟรม 1–2 เส้นลมขาวพาดทับอก ลบแล้วหัวขาด · pt0 เฟรม 5 วงลมขาวพันรอบตัว
# bl0 รอบ 2 (kwan 19 ต.ค.): รอบแรกสลับมือกลางท่า (ง้างมือขวา ฟันมือซ้าย) → เจนใหม่ระบุมือขวาทุกเฟรม
ATK_ANIM = {"bl": "bl0_v2"}
KEEP = {"pls_atk_fs": [0, 3, 4, 5, 6, 7], "pls_atk_pt": [0, 1, 2, 3, 4, 6, 7]}
for s, (st, th) in SCHOOL.items():
	CLIPS.append((f"pls_idle_{s}", f"ยืนในศึก · {th}", st, f"idle_{s}_v", "west", None, 180, True))
	CLIPS.append((f"pls_atk_{s}", f"โจมตีพื้นฐาน {s}0 · {th}", st, ATK_ANIM.get(s, f"{s}0_v"), "west", KEEP.get(f"pls_atk_{s}"), 90, False))
CLIPS += [("pls_hurt", "โดนตี · ถือมีด", "fight_knife", "hurt_k_v", "west", None, 90, False),
	("pls_ko", "ล้ม · มีดหลุดมือ", "fight_knife", "ko_k_v", "west", None, 110, False),
	("pls_run_bl", "วิ่งถือมีด", "fight_knife", "run_k_v", "west", [0, 1, 2, 3, 4, 5], 60, True),
	("pls_hop_bl", "กระโดดถอยถือมีด", "fight_knife", "hop_k_v", "west", [0, 1, 2, 3, 4], 60, False),   # hop_k เฟรม 5–7 กลายเป็นพุ่งไปหน้า + ประกาย/เส้นลม → ตัดทิ้ง · ลงพื้นใช้ภาพย่อ (1) ด้วยโค้ด
	("pls_bl1", "เขี้ยวพุ่ง bl1 · มีด", "fight_knife", "bl1_v2", "west", None, 90, False),   # รอบ 2 (kwan 19 ต.ค. "ขอลองเขี้ยวพุ่ง"): รอบแรกเฟรม 5–6 ฟันมือซ้าย + เฟรม 3 มีดหาย → เจนใหม่ระบุแขนไกล/ใกล้ทุกจังหวะ
	("pls_glim_shift", "ท่ากลางประกาย · ง้าง → ย่อ (มีด)", "fight_knife", "glim_shift_v2", "west", None, 90, False),   # รอบแรกเซิร์ฟเวอร์ PixelLab หมดเวลา (ไม่หักเครดิต) · kwan 21 ต.ค. "เจนภาพท่ากลาง": end_frame จาก bl0_v2 เฟรม 4 → bl1_v2 เฟรม 3
	("pls_bl7", "ตัดเอ็น bl7 (กาลี) · มีด", "fight_knife", "bl7_v", "west", [0, 1, 4, 5], 90, False),   # kwan 21 ต.ค.: ใช้ 0 ตั้งการ์ด · 1 ก้าวเข้ามีดวนขึ้น · 4 มีดวนลงหน้า · 5 ปาด (2–3 มีดชิดหน้า · 6 ประกายวาดติด · 7 มีดหาย · 5–7 เดินหน้าไม่ถอย)
	("pls_bl7_back", "ตัดเอ็น · ก้าวถอยแบบกาลี (end_frame)", "fight_knife", "bl7_back_v", "west", None, 90, False),
	("pls_walk_s", "เดินลง (หันหน้า)", None, "walk_v-eb599d32", "south", None, 90, True),
	("pls_walk_n", "เดินขึ้น (หันหลัง)", None, "walk_v", "north", None, 90, True)]


# ใบมีดที่ clean() ลบไปพร้อมเส้นฟาดฟ้า (ใบมีดเรืองขาวฟ้าทับเส้นฟาด) → วาดคืนตามแนวด้ามที่เหลือ · พิกัดในผืน 120x112 หลังจัดวาง
# bl0 รอบ 2 เฟรม 5 (จังหวะฟาด): ด้ามชี้ลงซ้ายจบที่ (32, 75) · สีใบมีด/ขอบจากเฟรม 6 (ใบมีดเดียวกันที่ไม่ถูกลบ)
BLADE = {("pls_atk_bl", 5): ((32, 75), (-1, 1), 7, "pls_atk_bl", 6)}
# ใบมีดที่ clean() ลบไส้ขาวเหลือแต่โครงขาด → ล้างโครงในกรอบ clear แล้วคัดลอกใบมีด (พร้อมขอบ) จากเฟรมอ้างอิงในกรอบ src เลื่อนตาม shift
# bl1 รอบ 2 เฟรม 6 (จังหวะแทง): กำปั้นอยู่ซ้ายของเฟรม 7 พอดี 3 จุด ความสูงเท่ากัน · ใบมีดเฟรม 7 ชี้ซ้ายแนวนอนเหมือนกัน
BLADE_COPY = {("pls_bl1", 6): (7, (-3, 0), (26, 64, 36, 73), (30, 64, 39, 73))}


# ท่าเชื่อมระหว่างสองคลิป: แต่ละคลิปจัดวางแยกกัน (ตามกรอบรวมของคลิป) → ภาพดิบตำแหน่งเดียวกันลงผืนต่างกันได้ (atk_bl กับ bl1 ห่าง 11 จุด)
# → ภาพท่าเชื่อมเลื่อนตำแหน่งทีละเฟรมจากตำแหน่งของคลิปต้นทางไปคลิปปลายทาง ไม่กระตุกตอนต่อ (ต้องอยู่หลังทั้งสองคลิปใน CLIPS)
ALIGN_BLEND = {"pls_glim_shift": ("pls_atk_bl", "pls_bl1")}
# วางแนวนอนตามคลิปอื่น แต่เท้าตามกรอบตัวเอง: bl7_back (end_frame จาก bl7_v) PixelLab วาดต่ำกว่าภาพต้นทาง 2 จุด → วางทั้งคลิปเท่า pls_bl7 แล้วเท้าลอย/จม
ALIGN_X = {"pls_bl7_back": "pls_bl7"}


def copy_blade(f, ref, shift, clear, srcbox):
	a = np.array(Image.open(f).convert("RGBA")); r = np.array(Image.open(ref).convert("RGBA"))
	a[clear[1]:clear[3], clear[0]:clear[2]] = 0
	for y in range(srcbox[1], srcbox[3]):
		for x in range(srcbox[0], srcbox[2]):
			if r[y, x, 3] >= 128: a[y + shift[1], x + shift[0]] = r[y, x]
	Image.fromarray(a).save(f)


def draw_blade(c, end, step, n, ref_cid, ref_i):
	"""ใบมีดแนวเฉียง 2 จุด ขอบเข้ม ต่อจากปลายด้าม end ไปทาง step n จุด · ปลายแหลม 1 จุด"""
	ref = np.array(Image.open(os.path.join(OUT, f"{ref_cid}_{ref_i}.png")).convert("RGBA")).astype(int)
	sat = ref[..., :3].max(-1) - ref[..., :3].min(-1); lum = ref[..., :3].mean(-1)
	blade = (ref[..., 3] > 127) & (sat < 40) & (lum > 120)
	light = tuple(np.median(ref[blade][:, :4], axis=0).astype(int))
	edge = tuple(np.median(ref[ndimage.binary_dilation(blade) & ~blade & (ref[..., 3] > 127)][:, :4], axis=0).astype(int))
	a = np.array(c); core = set()
	for k in range(1, n + 1):
		x, y = end[0] + step[0] * k, end[1] + step[1] * k
		core.add((x, y))
		if k < n: core.add((x - step[0], y))   # สองจุดต่อแถว ปลายเหลือจุดเดียว
	for x, y in core: a[y, x] = light
	for x, y in core:
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				u, v = x + dx, y + dy
				if (u, v) not in core and a[v, u, 3] < 128: a[v, u] = edge
	c.paste(Image.fromarray(a.astype(np.uint8), "RGBA"))


def src(st, anim, d):
	base = os.path.join(PL, "states", st, st) if st else os.path.join(PL, "zip", "Idle")
	return sorted(glob.glob(os.path.join(base, "animations", anim, d, "*.png"))), os.path.join(base, "rotations", d + ".png")


def clean(im, ref):
	a, r = np.array(im), np.array(ref)
	pal = np.unique(r[r[..., 3] > 127][:, :3], axis=0).astype(int)
	lum = lambda x: x[..., :3].astype(int) @ np.array([299, 587, 114]) // 1000
	hi = np.percentile(lum(r)[r[..., 3] > 127], 99) + 12
	px = a[..., :3].reshape(-1, 1, 3).astype(int)
	d = np.min(((px - pal[None]) ** 2).sum(-1), axis=1).reshape(a.shape[:2])
	body = a[..., 3] > 127
	far = body & ((d > 40 ** 2) | ((lum(a) > hi) & (d > 15 ** 2)))
	keep = body & ~far
	# เส้นฟาด/วงหมัด/ประกายสีขาวเทา สีตรงกับเสื้อขาว ลบด้วยสีไม่ได้ → ก้อนสีซีดที่รอบก้อนเป็นพื้นโปร่งเกินครึ่ง = เอฟเฟกต์ (เสื้อ/ใบมีดจริงมีเส้นขอบเข้มล้อม)
	rgb = a[..., :3].astype(int)
	pale = keep & (rgb.max(-1) - rgb.min(-1) < 40) & (lum(a) > 110)
	plab, pn = ndimage.label(pale)
	for i in range(1, pn + 1):
		comp = plab == i
		ring = ndimage.binary_dilation(comp) & ~comp
		if ring.sum() and (ring & ~keep).sum() / ring.sum() > 0.5:
			keep &= ~comp; far |= comp
	# ขอบน้ำเงินของเส้นฟาดสีฟ้า (สีตรงกับหมวก) → พิกเซลน้ำเงินที่ห่างเส้นฟาดสีฟ้าที่ลบไปแล้วไม่เกิน 2 จุด
	blue = keep & (rgb[..., 2] > rgb[..., 0] + 50) & (rgb[..., 2] > rgb[..., 1] + 20)
	cyan = far & (rgb[..., 1] > 150) & (rgb[..., 2] > 200) & (rgb[..., 0] < 170)   # เฉพาะเส้นฟาดสีฟ้า (แว่นทองที่ถูกลบในเดินขึ้นไม่นับ · ไม่งั้นกินขอบหมวก)
	edge = blue & ndimage.binary_dilation(cyan, iterations=2)
	keep &= ~edge; far |= edge
	lab, n = ndimage.label(keep)
	if n > 1:
		sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
		big = lab == 1 + int(np.argmax(sz))
		near = ndimage.binary_dilation(big, iterations=2)
		ids = {int(i) for i in np.unique(lab[near]) if i}
		keep = np.isin(lab, list(ids))
	out = a.copy(); out[~keep] = 0
	return Image.fromarray(out, "RGBA"), int(far.sum())


def main():
	shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
	clips, report, place = [], [], {}
	for cid, th, st, anim, d, use, ms, loop in CLIPS:
		files, rot = src(st, anim, d)
		if not files:
			print("ไม่มีภาพ", cid); continue
		ref = Image.open(rot).convert("RGBA")
		ims = [Image.open(f).convert("RGBA") for f in files]
		if use: ims = [ims[i] for i in use]
		cl = [clean(im if im.size == ref.size else im, ref if im.size == ref.size else ref.resize(im.size)) for im in ims]
		ims = [c[0] for c in cl]; removed = sum(c[1] for c in cl)
		bb = [im.getchannel("A").getbbox() for im in ims]
		x0, y1 = min(b[0] for b in bb), max(b[3] for b in bb)
		names = []
		place[cid] = (30 - x0 + max(0, (60 - (max(b[2] for b in bb) - x0)) // 2), 108 - y1)
		for i, im in enumerate(ims):
			at = place[cid]
			if cid in ALIGN_X:
				at = (place[ALIGN_X[cid]][0], at[1])
			if cid in ALIGN_BLEND:
				(ax, ay), (bx, by), u = place[ALIGN_BLEND[cid][0]], place[ALIGN_BLEND[cid][1]], i / max(1, len(ims) - 1)
				at = (round(ax + (bx - ax) * u), round(ay + (by - ay) * u))
			c = Image.new("RGBA", (120, 112)); c.alpha_composite(im, at)
			n = f"{cid}_{i}"; c.save(os.path.join(OUT, n + ".png")); names.append(n)
		for (bc, bi), spec in BLADE.items():   # หลังบันทึกครบทั้งคลิป (ใช้สีจากเฟรมอื่นของคลิปเดียวกัน)
			if bc == cid and bi < len(names):
				f = os.path.join(OUT, f"{cid}_{bi}.png"); c = Image.open(f).convert("RGBA"); draw_blade(c, *spec); c.save(f)
		for (bc, bi), (ri, sh, clr, sb) in BLADE_COPY.items():
			if bc == cid and max(bi, ri) < len(names): copy_blade(os.path.join(OUT, f"{cid}_{bi}.png"), os.path.join(OUT, f"{cid}_{ri}.png"), sh, clr, sb)
		clips.append({"group": G, "id": cid, "label": f"{th} · {len(names)} เฟรม (PixelLab · ลบแสงที่วาดติดมา {removed} จุด)", "frames": names, "ms": ms,
			"loop": loop, "w": 120, "travel": 0, "src": [f"pixellab {st or 'base'} {anim} {d}"]})
		report.append((cid, len(names), removed))
	json.dump({"_doc": "ชุด Rion ในเกมจาก PixelLab · tools/sprites/pixellab_rion_set.py · ร่าง ยังไม่เข้าเกม", "clips": clips},
		open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	for r in report: print(*r)
	import weapon_swap; weapon_swap.main()   # คลิปเปลี่ยนอาวุธด้วยโค้ด (ใช้ภาพ pls_atk_bl ที่เพิ่งสร้าง)


if __name__ == "__main__":
	main()
