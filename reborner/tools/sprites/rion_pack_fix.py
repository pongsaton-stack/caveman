"""แก้ของในมือที่ Flow วาดไม่ได้ด้วยโค้ด (kwan 16 ต.ค. เลือก "1" หลัง 17-4b)
  fan  : 15-4 แถว 1 ถือมีดครบ 5 ช่อง → ลบใบมีด แล้วแปะใบพัดลม+มอเตอร์ที่ตัดจาก 17-1b ช่อง 4-2 ตามแกนเดิมของมีด
  knife: 17-2 โดนตี/เชียร์ ช่องที่มือว่าง → แปะมีด (ใบ+ด้าม) ที่ตัดจากเฟรมที่มีมีดในแถวเดียวกัน ที่จุดมือ (วัดด้วยตา · KNIFE_AT)
อ่าน/เขียน assets/sprites/rion_pack_draft/<ชีต>/ · ผลไป rion_pack_draft/fix/<ชื่อ>_<i>.png + ภาพตรวจ pack_check/fix.jpg
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
D = os.path.join(ROOT, "assets/sprites/rion_pack_draft")
OUT = os.path.join(D, "fix")
CHECK = os.path.join(ROOT, "docs/art-bible/rion_hires/pack_check/fix.jpg")

# ใบพัดลมใน 17-1b ช่อง 4-2 (แถว 3 ช่อง 1 นับจาก 0): จุดจับ (ปลายด้ามในถุงมือ) → ปลายใบ · วัดจากภาพขยาย
FAN_SRC = ("17-1b", "3_1")
FAN_GRIP = np.array([134.0, 86.0])
FAN_TIP = np.array([184.0, 3.0])
FAN_FROM = 6       # เริ่มตัดเหนือจุดจับ (พ้นถุงมือ) หน่วยพิกเซลตามแกน
FAN_HALF = 14      # ครึ่งความกว้างใบ+มอเตอร์
FAN_SCALE = 1.5    # ใบพัดยาวกว่ามีด (สั่งไว้ "ยาวเท่าแขน")
PAD = 140          # ขยายผืนก่อนแปะ (ใบพัดยาวกว่ามีด หลุดขอบภาพเดิม) แล้วค่อยครอปตามตัว
# ช่องที่หาใบมีดอัตโนมัติไม่ได้ (ใบมีดติดรอยฟัน): โคน/ปลาย วัดด้วยตาจากภาพขยาย · ลบเฉพาะแถบกว้าง 8 รอบแกน ไม่ลบรอยฟันขาวล้วน
BLADE_AT = {3: ((187, 246), (241, 192))}

# มีดใน 17-2 ช่อง 1-6 (แถว 0 ช่อง 5): กลางกำปั้น · โคนใบ (การ์ด) · ปลายใบ — วัดจากภาพขยาย ×3
KNIFE_SRC = ("17-2", "0_5")
KNIFE_FIST = np.array([192.0, 276.0])
KNIFE_GRIP = np.array([196.0, 262.0])
KNIFE_TIP = np.array([232.0, 180.0])
# ช่องมือว่าง → กลางกำปั้นมือที่ถือมีด (มือขวาของภาพ ข้างเดียวกับเฟรมที่มีมีด) · โดนตี 2–5 · เชียร์ 2 4 5 (ชูกำปั้นข้างที่ถือมีด จึงชูมีดด้วย)
KNIFE_AT = {"0_1": (201, 267), "0_2": (205, 269), "0_3": (187, 298), "0_4": (163, 324),
	"4_1": (218, 163), "4_3": (217, 209), "4_4": (213, 255)}
# 18-1 ท่าสายคม: ช่องที่ Flow ลืมมีด → มีดจากช่อง 1-1 (แถว 0 ช่อง 0) แปะที่กำปั้นมือหน้า · 5-4 (หันหลัง) ถือสองเล่ม → ลบเล่มซ้าย (กรอบเหนือมือ)
K18_SRC = ("18-1", "0_0")
K18_FIST, K18_GRIP, K18_TIP = np.array([145.0, 217.0]), np.array([150.0, 202.0]), np.array([190.0, 142.0])
K18_AT = {"0_1": (156, 210), "1_1": (178, 168), "5_4": (152, 167), "6_1": (171, 177), "6_4": (149, 212)}
K18_ERASE = {"4_3": (0, 30, 44, 106)}   # x0 y0 x1 y1 ในภาพ (ใบมีดเล่มซ้าย เหนือกำปั้น)
HURT = ["0_0", "0_1", "0_2", "0_3", "0_4", "0_5"]
CHEER = ["4_0", "4_1", "4_2", "4_3", "4_4"]


def load(k, f):
	return np.array(Image.open(os.path.join(D, k, f + ".png")).convert("RGBA")).astype(float)


def axis_mask(img, grip, tip, t0, half):
	h, w = img.shape[:2]
	yy, xx = np.mgrid[0:h, 0:w]
	d = (tip - grip) / np.linalg.norm(tip - grip)
	vx, vy = xx - grip[0], yy - grip[1]
	t = vx * d[0] + vy * d[1]
	p = np.abs(vx * d[1] - vy * d[0])
	return (t >= t0) & (t <= np.linalg.norm(tip - grip) + 3) & (p <= half)


def fan_piece():
	img = load(*FAN_SRC)
	m = axis_mask(img, FAN_GRIP, FAN_TIP, FAN_FROM, FAN_HALF) & (img[..., 3] > 0)
	piece = img.copy()
	piece[~m, 3] = 0
	return piece


def blade_of(img):
	"""ใบมีด = ก้อนสีเทา/ขาวอิ่มตัวต่ำ ยาวแคบ ไม่ใช่เสื้อ (กลม) ไม่ใช่รอยฟัน (ใหญ่ขาวล้วน)"""
	rgb, a = img[..., :3], img[..., 3]
	mx, mn = rgb.max(2), rgb.min(2)
	grey = (a > 128) & (mx > 120) & ((mx - mn) < 40)
	lab, n = ndimage.label(grey)
	best = None
	for i in range(1, n + 1):
		ys, xs = np.nonzero(lab == i)
		if len(ys) < 120 or len(ys) > 4000:
			continue
		pts = np.stack([xs, ys], 1).astype(float)
		c = pts.mean(0)
		ev, evec = np.linalg.eigh(np.cov((pts - c).T))
		if ev[1] < 9 * ev[0]:     # ไม่ยาวพอ
			continue
		if rgb[ys, xs].mean() > 245:  # ขาวล้วน = รอยฟัน
			continue
		if best is None or len(ys) > best[0]:
			best = (len(ys), lab == i, pts, c, evec[:, 1])
	return best


def brown(img):
	r, g, b = img[..., 0], img[..., 1], img[..., 2]
	return (img[..., 3] > 128) & (r > 90) & (r > g + 20) & (g > b + 5)


def paste_rotated(dst, piece, src_grip, src_tip, dst_grip, dst_dir, length):
	"""หมุน/ย่อ piece ให้แกน src_grip→src_tip ไปอยู่ที่ dst_grip ทิศ dst_dir ยาว length แล้ววางทับ dst"""
	sv = src_tip - src_grip
	s = length / np.linalg.norm(sv)
	ang = np.arctan2(dst_dir[1], dst_dir[0]) - np.arctan2(sv[1], sv[0])
	ca, sa = np.cos(ang), np.sin(ang)
	h, w = dst.shape[:2]
	yy, xx = np.mgrid[0:h, 0:w].astype(float)
	# ผกผัน: จุดปลายทาง → จุดต้นทาง
	dx, dy = (xx - dst_grip[0]) / s, (yy - dst_grip[1]) / s
	sx = ca * dx + sa * dy + src_grip[0]
	sy = -sa * dx + ca * dy + src_grip[1]
	pim = Image.fromarray(piece.astype(np.uint8), "RGBA")
	big = np.array(pim.resize((pim.width * 4, pim.height * 4), Image.LANCZOS)).astype(float)
	ix, iy = np.round(sx * 4).astype(int), np.round(sy * 4).astype(int)
	ok = (ix >= 0) & (iy >= 0) & (ix < big.shape[1]) & (iy < big.shape[0])
	src = np.zeros_like(dst)
	src[ok] = big[iy[ok], ix[ok]]
	al = src[..., 3:4] / 255.0
	out = dst.copy()
	out[..., :3] = src[..., :3] * al + dst[..., :3] * (1 - al)
	out[..., 3] = np.maximum(dst[..., 3], src[..., 3])
	return out


def fix_fan():
	piece = fan_piece()
	res = []
	for c in range(5):
		img = np.pad(load("15-4", f"0_{c}"), ((PAD, PAD), (PAD, PAD), (0, 0)))
		if c in BLADE_AT:
			grip, tip = (np.array(p, float) + PAD for p in BLADE_AT[c])
			white = (img[..., :3].min(2) > 245)
			kill = axis_mask(img, grip, tip, 2, 8) & ~white & ~brown(img)
			pts = np.argwhere(kill)
		else:
			b = blade_of(img)
			assert b, f"15-4 0_{c}: หาใบมีดไม่เจอ"
			_, bm, pts, cen, ax = b
			t = (pts - cen) @ ax
			e1, e2 = cen + ax * t.min(), cen + ax * t.max()
			br = brown(img)
			near = lambda e: br[max(0, int(e[1]) - 18):int(e[1]) + 18, max(0, int(e[0]) - 18):int(e[0]) + 18].sum()
			grip, tip = (e1, e2) if near(e1) > near(e2) else (e2, e1)
			# ลบใบ + เส้นขอบรอบใบ (เฉพาะพ้นโคนใบไป 2 จุด ไม่กินมือ)
			kill = ndimage.binary_dilation(bm, iterations=4) & axis_mask(img, grip, tip, 2, 99) & ~brown(img)
		L = np.linalg.norm(tip - grip)
		d = (tip - grip) / L
		img[kill, 3] = 0
		img = paste_rotated(img, piece, FAN_GRIP + (FAN_TIP - FAN_GRIP) / np.linalg.norm(FAN_TIP - FAN_GRIP) * FAN_FROM,
			FAN_TIP, grip, d, L * FAN_SCALE)
		ys, xs = np.nonzero(img[..., 3] > 0)
		res.append(img[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
		print(f"fan {c}: ใบมีด {len(pts)} จุด ยาว {L:.0f} โคน {grip.round()} ทิศ {d.round(2)}")
	return res


def fix_knife(order):
	src = load(*KNIFE_SRC)
	piece = src.copy()
	piece[~(axis_mask(src, KNIFE_GRIP, KNIFE_TIP, -4, 11) & (src[..., 3] > 0)), 3] = 0
	L = np.linalg.norm(KNIFE_TIP - KNIFE_GRIP)
	d = (KNIFE_TIP - KNIFE_GRIP) / L
	res = []
	for f in order:
		img = load("17-2", f)
		if f in KNIFE_AT:
			img = np.pad(img, ((PAD, PAD), (PAD, PAD), (0, 0)))
			grip = np.array(KNIFE_AT[f], float) + (KNIFE_GRIP - KNIFE_FIST) + PAD
			img = paste_rotated(img, piece, KNIFE_GRIP, KNIFE_TIP, grip, d, L)
			ys, xs = np.nonzero(img[..., 3] > 0)
			img = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
		res.append(img)
	return res


def fix_18_1():
	src = load(*K18_SRC)
	piece = src.copy()
	piece[~(axis_mask(src, K18_GRIP, K18_TIP, -4, 11) & (src[..., 3] > 0)), 3] = 0
	L = np.linalg.norm(K18_TIP - K18_GRIP)
	d = (K18_TIP - K18_GRIP) / L
	out = {}
	for f, fist in K18_AT.items():
		img = np.pad(load("18-1", f), ((PAD, PAD), (PAD, PAD), (0, 0)))
		img = paste_rotated(img, piece, K18_GRIP, K18_TIP, np.array(fist, float) + (K18_GRIP - K18_FIST) + PAD, d, L)
		ys, xs = np.nonzero(img[..., 3] > 0)
		out[f] = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
	for f, (x0, y0, x1, y1) in K18_ERASE.items():
		img = load("18-1", f)
		img[y0:y1, x0:x1, 3] = 0
		out[f] = img
	return out


def save(name, frames):
	os.makedirs(OUT, exist_ok=True)
	for i, f in enumerate(frames):
		Image.fromarray(np.clip(f, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"{name}_{i}.png"))


def sheet(rows):
	H = 300
	tiles = [[Image.fromarray(np.clip(f, 0, 255).astype(np.uint8), "RGBA") for f in r] for r in rows]
	W = max(sum(int(t.width * H / t.height) + 10 for t in r) for r in tiles)
	out = Image.new("RGB", (W, len(rows) * (H + 10)), (60, 110, 60))
	for ri, r in enumerate(tiles):
		x = 0
		for t in r:
			t = t.resize((int(t.width * H / t.height), H), Image.LANCZOS)
			out.paste(t, (x, ri * (H + 10)), t)
			x += t.width + 10
	out.save(CHECK, quality=85)


if __name__ == "__main__":
	fan = fix_fan()
	save("fan", fan)
	hurt, cheer = fix_knife(HURT), fix_knife(CHEER)
	save("hurt", hurt)
	save("cheer", cheer)
	k18 = fix_18_1()
	os.makedirs(OUT, exist_ok=True)
	for f, im in k18.items():
		Image.fromarray(np.clip(im, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"18-1_{f}.png"))
	sheet([fan, hurt, cheer, list(k18.values())])
