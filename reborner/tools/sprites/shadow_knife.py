"""มีดเงา bl6 (kwan 28 ต.ค. "เงาสองคม ทำเป็นเสกมีดเงาออกมาอีกอัน")
ภาพ PixelLab ของท่าสองมีด (มีดครัวมือขวา + มีดสั้นมือซ้าย) → ย้อมมีดมือซ้ายเป็นมีดเงา (ใบม่วงเข้ม ขอบม่วงสว่าง ด้ามดำ)
ในชุด px_set (ผืน 120x112) · สร้างภาพ <ชื่อ>n = เอามีดเงาออก (ตอนมีดเงาสลายเป็นควัน)
เรียกอัตโนมัติท้าย pixellab_rion_set.py (ต้องรันกับภาพที่เพิ่งสร้าง · ห้ามรันซ้ำบนภาพที่ย้อมแล้ว) · พิมพ์ SDK สำหรับ tests/lab/sd_bl6.gd

ระบุมีดเงาต่อภาพ: ("box", x0, y0, x1, y1) = ใบมีดทุกจุดในกรอบ · ("seg", A, B) = ใบมีดที่ใกล้เส้น A (ด้าม → ปลาย) มากกว่าเส้น B ของมีดจริง (มีดไขว้กัน)
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PX = os.path.join(ROOT, "assets/sprites/pixellab_draft/px_set")

# พิกัดบนผืน px_set 120x112 (วัดจากภาพขยาย 28 ต.ค.)
SDK = {
	"pls_sd_summon_2": ("box", 84, 74, 104, 96),   # มีดสั้นต่ำหลังสะโพก
	"pls_sd_summon_3": ("box", 84, 76, 104, 98),
	"pls_sd_cut_0": ("box", 84, 80, 104, 97),
	"pls_sd_cut_1": ("box", 73, 64, 95, 87),       # มีดสั้นคุมอก (ชี้ขึ้นหลังไหล่)
	"pls_sd_cut_2": ("box", 67, 64, 88, 87),
	"pls_sd_x_0": ("seg", ((41, 76), (50, 90)), ((54, 80), (45, 91))),   # มีดจากกำปั้นแขนเหยียดหน้า · มีดจริงมาจากมือที่เอว
	"pls_sd_x_1": ("seg", ((44, 76), (55, 89)), ((55, 78), (45, 90))),
	"pls_sd_x_2": ("seg", ((45, 75), (56, 85)), ((54, 80), (45, 90))),
}
BLADE_L = np.array([108, 86, 200])    # ใบมีดเงา (ส่วนสว่างของใบเดิม)
BLADE_H = np.array([170, 150, 255])   # ไฮไลต์บนสุดของใบ
EDGE = np.array([18, 10, 42])         # เส้นขอบ/ด้าม


def seg_dist(p, a, b):
	a, b = np.array(a, float), np.array(b, float)
	ab = b - a
	t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
	return np.linalg.norm(p - (a + t[..., None] * ab), axis=-1)


def mask_of(a, spec):
	rgb = a[..., :3].astype(int)
	alpha = a[..., 3] > 127
	lum = rgb @ np.array([299, 587, 114]) // 1000
	sat = rgb.max(-1) - rgb.min(-1)
	blade = alpha & (sat < 50) & (lum > 95)
	h, w = alpha.shape
	yy, xx = np.mgrid[0:h, 0:w]
	pts = np.stack([xx, yy], -1).astype(float)
	if spec[0] == "box":
		_, x0, y0, x1, y1 = spec
		zone = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
		core = blade & zone
	else:
		_, A, B = spec
		da, db = seg_dist(pts, *A), seg_dist(pts, *B)
		zone = (da < 4.5) & (da <= db)
		core = blade & zone
	# ขอบเข้มรอบใบ + ด้าม (สีน้ำตาลติดใบ) ในโซนเดียวกัน
	ring = ndimage.binary_dilation(core, iterations=1) & alpha & ~core & (lum < 110)
	brown = alpha & (rgb[..., 0] > rgb[..., 2] + 25) & (lum < 120) & (lum > 30)
	handle = ndimage.binary_dilation(core, iterations=4) & brown & zone
	return core, ring | handle, lum


def main():
	out = {}
	for name, spec in SDK.items():
		f = os.path.join(PX, name + ".png")
		a = np.array(Image.open(f).convert("RGBA"))
		core, dark, lum = mask_of(a, spec)
		if core.sum() < 4:
			print("ไม่เจอใบมีดเงา", name, int(core.sum())); continue
		b = a.copy()
		hi = core & (lum > np.percentile(lum[core], 70))
		b[core, :3] = BLADE_L
		b[hi, :3] = BLADE_H
		b[dark, :3] = EDGE
		Image.fromarray(b).save(f)
		n = a.copy()   # ไม่มีมีดเงา (สลายแล้ว)
		n[core | dark] = 0
		Image.fromarray(n).save(os.path.join(PX, name + "n.png"))
		ys, xs = np.nonzero(core)
		out[name] = [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]
		print(name, "ใบ", int(core.sum()), "ขอบ/ด้าม", int(dark.sum()), "กลาง", out[name])
	print("const SDK := {" + ", ".join(f'"{k}": Vector2({v[0]}, {v[1]})' for k, v in out.items()) + "}")
	json.dump(out, open(os.path.join(PX, "shadow_knife.json"), "w"), indent=1)


if __name__ == "__main__":
	main()
