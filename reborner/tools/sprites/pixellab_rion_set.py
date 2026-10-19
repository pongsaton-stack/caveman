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
for s, (st, th) in SCHOOL.items():
	CLIPS.append((f"pls_idle_{s}", f"ยืนในศึก · {th}", st, f"idle_{s}_v", "west", None, 180, True))
	CLIPS.append((f"pls_atk_{s}", f"โจมตีพื้นฐาน {s}0 · {th}", st, f"{s}0_v", "west", None, 90, False))
CLIPS += [("pls_hurt", "โดนตี · ถือมีด", "fight_knife", "hurt_k_v", "west", None, 90, False),
	("pls_ko", "ล้ม · มีดหลุดมือ", "fight_knife", "ko_k_v", "west", None, 110, False),
	("pls_walk_s", "เดินลง (หันหน้า)", None, "walk_v-eb599d32", "south", None, 90, True),
	("pls_walk_n", "เดินขึ้น (หันหลัง)", None, "walk_v", "north", None, 90, True)]


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
	clips, report = [], []
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
		for i, im in enumerate(ims):
			c = Image.new("RGBA", (120, 112)); c.alpha_composite(im, (30 - x0 + max(0, (60 - (max(b[2] for b in bb) - x0)) // 2), 108 - y1))
			n = f"{cid}_{i}"; c.save(os.path.join(OUT, n + ".png")); names.append(n)
		clips.append({"group": G, "id": cid, "label": f"{th} · {len(names)} เฟรม (PixelLab · ลบแสงที่วาดติดมา {removed} จุด)", "frames": names, "ms": ms,
			"loop": loop, "w": 120, "travel": 0, "src": [f"pixellab {st or 'base'} {anim} {d}"]})
		report.append((cid, len(names), removed))
	json.dump({"_doc": "ชุด Rion ในเกมจาก PixelLab · tools/sprites/pixellab_rion_set.py · ร่าง ยังไม่เข้าเกม", "clips": clips},
		open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	for r in report: print(*r)


if __name__ == "__main__":
	main()
