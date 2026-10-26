#!/usr/bin/env python3
"""tools/sprites/rion_ref.py — ภาพต้นฉบับ Rion เป็นภาพหลัก (kwan 14 ต.ค. 2026 เลือก "1": ใช้ภาพต้นฉบับ · ทิศ/ท่าอื่นเจนตาม SHOTLIST)

  python3 tools/sprites/rion_ref.py cut
      ตัดพื้นเขียวออกจากต้นฉบับ ไม่แตะตัวละคร (ไม่ทาสี ไม่ล็อกสี ไม่ขยับ)
      → docs/art-bible/rion_hires/rion_front_alpha.png (ขนาดเดิม 1145x1374)
      → assets/sprites/rion_hires_draft/stand_south.png (ผืน 512 ตัวสูง 464 เท้าแถว 504 · ผืนเดียวกับ walk_south_*)

  python3 tools/sprites/rion_ref.py check <ภาพ.png> [...]
      ตรวจภาพที่เจนตามกฎกลางใน SHOTLIST เทียบกับต้นฉบับ: ขนาดผืน · พื้นเขียว #00B140 · ความสูงตัว/แถวเท้า/กลางตัว ·
      สีแปลกปลอม (สีที่ไม่มีในต้นฉบับ = ของเกิน/ชุดเปลี่ยน) · หมวกมีแถบครีม/ขาว · เงาบนพื้น
      ตรวจหน้าตา (ตา ผม ทรงหน้า) อัตโนมัติไม่ได้ — ต้องดูด้วยตา · ผล PASS = ผ่านทุกข้อที่วัดได้ ไม่ใช่ "เหมือน 100%"
"""
import os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs/art-bible/rion_hires/rion_front_src.png")
ALPHA_OUT = os.path.join(ROOT, "docs/art-bible/rion_hires/rion_front_alpha.png")
STAND_OUT = os.path.join(ROOT, "assets/sprites/rion_hires_draft/stand_south.png")
GREEN = np.array([0, 177, 64])
CANVAS, BODY_H, FOOT_ROW = 512, 464, 504      # ผืนเดียวกับ rion_hires_draft/walk_south_*


def key(a):
	"""ความทึบจากความเขียว (สูตรเดียวกับ rion_hd.work_image_hires): d ≤ 40 ทึบ · ≥ 90 โปร่ง · ล้างเขียวที่ขอบ 3 จุด"""
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	d = g - np.maximum(r, b)
	al = np.clip((90 - d) / 50.0, 0, 1)
	band = al < 1
	for _ in range(3):
		n = band.copy(); n[1:] |= band[:-1]; n[:-1] |= band[1:]; n[:, 1:] |= band[:, :-1]; n[:, :-1] |= band[:, 1:]; band = n
	a = a.copy(); a[..., 1] = np.where(band & (d > 0), np.maximum(r, b), g)
	return a, al


def body_box(al):
	ys, xs = np.nonzero(al > 0.5)
	return xs.min(), ys.min(), xs.max(), ys.max()


def cut():
	a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.int32)
	a, al = key(a)
	rgba = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA")
	rgba.save(ALPHA_OUT)
	x0, y0, x1, y1 = body_box(al)
	k = BODY_H / (y1 - y0 + 1)
	sm = rgba.resize((round(rgba.width * k), round(rgba.height * k)), Image.LANCZOS)
	cv = Image.new("RGBA", (CANVAS, CANVAS))
	cv.alpha_composite(sm, (round(CANVAS / 2 - (x0 + x1) / 2 * k), round(FOOT_ROW - y1 * k)))
	cv.save(STAND_OUT)
	print("ตัดพื้นแล้ว · ตัว x%d–%d y%d–%d (สูง %d) → %s · %s" % (x0, x1, y0, y1, y1 - y0 + 1, os.path.relpath(ALPHA_OUT, ROOT), os.path.relpath(STAND_OUT, ROOT)))


def ref_stats():
	a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.int32)
	_, al = key(a)
	px = a[al > 0.99].astype(np.float64)
	rng = np.random.default_rng(1)
	cent = px[rng.choice(len(px), 16, replace=False)]
	for _ in range(25):   # k-means 16 สี = พาเลตต์ต้นฉบับ
		lab = ((px[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
		cent = np.array([px[lab == i].mean(0) if (lab == i).any() else cent[i] for i in range(len(cent))])
	return a, al, cent


def check(path, ref):
	ra, ral, cent = ref
	rx0, ry0, rx1, ry1 = body_box(ral)
	im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(np.int32)
	rows = []
	def row(ok, name, got, want):
		rows.append(("ผ่าน" if ok else "ไม่ผ่าน", name, got, want))
	row(im.size == (1145, 1374), "ขนาดผืน", "%dx%d" % im.size, "1145x1374")
	edge = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
	med = np.median(edge, 0); dg = float(np.abs(med - GREEN).max())
	row(dg <= 12, "สีพื้น (ค่ากลางขอบภาพ)", "#%02x%02x%02x" % tuple(int(v) for v in med), "#00b140 (ต่างไม่เกิน 12)")
	_, al = key(a)
	if (al > 0.5).sum() < 1000:
		row(False, "หาตัวละคร", "ไม่เจอ", "-"); return rows
	x0, y0, x1, y1 = body_box(al)
	h, rh = y1 - y0 + 1, ry1 - ry0 + 1
	row(abs(h - rh) / rh <= 0.05, "ความสูงตัว", "%d" % h, "%d ±5%%" % rh)
	row(abs(y1 - ry1) <= 15, "แถวเท้า (ล่างสุด)", "%d" % y1, "%d ±15" % ry1)
	row(abs((x0 + x1) / 2 - (rx0 + rx1) / 2) <= 60, "กลางตัว x", "%.0f" % ((x0 + x1) / 2), "%.0f ±60" % ((rx0 + rx1) / 2))
	row(y0 > 2 and y1 < im.height - 3 and x0 > 2 and x1 < im.width - 3, "ตัวไม่ชนขอบภาพ (เท้าครบ)", "x%d–%d y%d–%d" % (x0, x1, y0, y1), "ห่างขอบ")
	px = a[al > 0.99].astype(np.float64)
	dist = np.sqrt(((px[:, None] - cent[None]) ** 2).sum(-1)).min(1)
	far = dist > 60; alien = float(far.mean())
	got = "%.1f%%" % (alien * 100)
	if far.any():   # สีแปลกปลอมที่เจอบ่อยสุด (ปัด 32) ช่วยบอกว่าอะไรเกินมา
		q = (px[far] // 32 * 32 + 16).astype(int); u, c = np.unique(q, axis=0, return_counts=True)
		got += " เด่น #%02x%02x%02x" % tuple(u[c.argmax()])
	row(alien <= 0.01, "สีแปลกปลอม (ไม่มีในต้นฉบับ)", got, "≤ 1% (ต้นฉบับเอง 0.3%)")
	top = a[y0:y0 + int(h * 0.22)]; tal = al[y0:y0 + int(h * 0.22)] > 0.99
	r, g, b = top[..., 0], top[..., 1], top[..., 2]
	cream = tal & (r > 190) & (g > 175) & (b > 120) & (r - b > 10) & (r - b < 110)
	cr = float(cream.sum()) / max(1, tal.sum())
	row(cr <= 0.02, "แถบครีม/ขาวบนหมวก (22% บนของตัว)", "%.1f%%" % (cr * 100), "≤ 2%")
	below = a[min(y1 + 1, a.shape[0] - 1):min(y1 + 25, a.shape[0])]
	if len(below):
		dark = float((np.abs(below - GREEN).max(-1) > 30).mean())
		row(dark <= 0.01, "เงา/ของใต้เท้า (24 แถว)", "%.1f%%" % (dark * 100), "≤ 1%")
	return rows


if __name__ == "__main__":
	if len(sys.argv) < 2 or sys.argv[1] not in ("cut", "check"):
		print(__doc__); sys.exit(2)
	if sys.argv[1] == "cut":
		cut(); sys.exit(0)
	ref = ref_stats(); bad = 0
	for p in sys.argv[2:]:
		rows = check(p, ref); fails = [r for r in rows if r[0] != "ผ่าน"]; bad += bool(fails)
		print("\n== %s → %s" % (os.path.basename(p), "PASS (ข้อที่วัดได้) · ยังต้องดูหน้าตาด้วยตา" if not fails else "ไม่ผ่าน %d ข้อ" % len(fails)))
		for r in rows:
			print("  %-7s %-34s %-22s ต้องการ %s" % r)
	sys.exit(1 if bad else 0)
