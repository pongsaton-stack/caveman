"""ไม้เบสบอลระดับต่างๆ (weapons.csv ชุด 60 ชิ้น: CR-1/2/4/6/9/10 คือไม้) บนภาพ Rion PixelLab สายทุบ — เปลี่ยนด้วยโค้ด ไม่เสียเครดิต (kwan 26 ต.ค. "เพิ่มปุ่มให้เลือกอาวุธในแลป")

หาไม้: สีเทาสีเดียวกับเสื้อ/ถุงเท้า → แยกด้วยรูปทรง: ปลายไม้ = จุดเทาไกลกลางตัวสุด → ไล่จุดเทาติดกันภายใน 36 จุด → ลากเส้นตรง (PCA)
  → ไม้ = จุดเทาห่างเส้น ≤ 1.8 จุด และอยู่บนช่วงความยาวไม้ (ตัดเงาเสื้อที่ไม่อยู่บนแนวไม้)
ระดับ: CR-1 ไม้ร้าว (สีไม้ + รอยร้าว) · CR-2 อลูมิเนียม (ภาพเดิม) · CR-4 หัวเฟือง (เหล็กเข้ม + เฟืองที่ปลาย) · CR-6 ไม้ตะปู (สีไม้ + ตะปู)
  CR-9 เหล็กกล้า (เงินขัดเงา + วงแหวนรูน) · CR-10 สายฟ้า (ฟ้าขาว + สายฟ้าซิกแซก + ขอบเรือง) · กระทะ/ค้อน/หนังสือ (CR-3/5/7/8) ไม่ใช่ไม้ → รอภาพจาก PixelLab
  python3 tools/sprites/bat_tiers.py → assets/sprites/pixellab_draft/weapon_skin/wsk_<ภาพ>__CR-k.png (lab_stage tx() อ่าน prefix wsk_) + check.png
  รันใหม่ทุกครั้งหลัง pixellab_rion_set.py (ภาพต้นทาง px_set/pls_bat*)
"""
import glob
import os
from collections import deque

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "assets/sprites/pixellab_draft/px_set")
OUT = os.path.join(ROOT, "assets/sprites/pixellab_draft/weapon_skin")
TIERS = ["CR-1", "CR-4", "CR-6", "CR-9", "CR-10"]   # CR-2 = ภาพเดิม · ต้องตรงกับ BAT_SKINS ใน tests/lab/lab_stage.gd
RAMP = {"CR-1": [(58, 36, 20), (122, 80, 42), (170, 116, 62), (214, 166, 104)],
	"CR-4": [(40, 42, 48), (74, 78, 88), (104, 110, 122), (150, 156, 168)],
	"CR-6": [(58, 36, 20), (122, 80, 42), (170, 116, 62), (214, 166, 104)],
	"CR-9": [(70, 76, 90), (140, 150, 168), (200, 208, 222), (248, 250, 255)],
	"CR-10": [(30, 60, 140), (70, 130, 230), (150, 200, 255), (240, 250, 255)]}


def bat_mask(a):
	rgb = a[..., :3].astype(float) / 255
	mx, mn = rgb.max(-1), rgb.min(-1)
	sat = (mx - mn) / np.maximum(mx, 1e-3)
	gray = (a[..., 3] > 128) & (sat < 0.16) & (mx > 0.38) & (mx < 0.96)
	body = (a[..., 3] > 128) & ~gray
	if gray.sum() < 6:
		return None
	by, bx = np.argwhere(body).mean(0)
	lab, n = ndimage.label(gray, np.ones((3, 3)))   # ก้อนเทาที่ยาวที่สุด = ไม้ (ถุงเท้า/เงาเสื้อเป็นก้อนสั้น)
	best, span = 0, 0.0
	for i in range(1, n + 1):
		ys, xs = np.nonzero(lab == i)
		sp = float(np.hypot(ys.max() - ys.min(), xs.max() - xs.min()))
		if sp > span:
			best, span = i, sp
	gy, gx = np.nonzero(lab == best)
	k = ((gx - bx) ** 2 + (gy - by) ** 2).argmax()
	tip = (gy[k], gx[k])
	seen = {tip}
	q = deque([tip])
	while q:   # ไล่จุดเทาติดกันจากปลายไม้ ไม่เกิน 36 จุด
		y, x = q.popleft()
		for dy in (-1, 0, 1):
			for dx in (-1, 0, 1):
				n = (y + dy, x + dx)
				if n not in seen and 0 <= n[0] < a.shape[0] and 0 <= n[1] < a.shape[1] and gray[n] and (n[0] - tip[0]) ** 2 + (n[1] - tip[1]) ** 2 <= 36 ** 2:
					seen.add(n)
					q.append(n)
	pts = np.array(sorted(seen), float)
	if len(pts) < 6:
		return None
	c = pts.mean(0)
	u = np.linalg.svd(pts - c)[2][0]   # แนวไม้
	if np.dot(np.array(tip, float) - c, u) < 0:
		u = -u   # u ชี้ไปทางปลายไม้
	proj = (pts - np.array(tip, float)) @ u
	length = -proj.min()
	m = np.zeros(gray.shape, bool)
	for y, x in zip(*np.nonzero(gray)):
		d = np.array([y, x], float) - np.array(tip, float)
		t = -(d @ u)
		if -1 <= t <= length + 1 and abs(d[0] * u[1] - d[1] * u[0]) <= 1.8:
			m[y, x] = True
	return m, np.array(tip, float), u, length


def recolor(a, m, ramp):
	lum = a[..., :3].astype(float).mean(-1)
	ys, xs = np.nonzero(m)
	lo, hi = lum[m].min(), lum[m].max()
	for y, x in zip(ys, xs):
		i = int(round((lum[y, x] - lo) / max(1.0, hi - lo) * (len(ramp) - 1)))
		a[y, x, :3] = ramp[i]


def put(a, y, x, col):
	y, x = int(round(y)), int(round(x))
	if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
		a[y, x] = list(col) + [255]


def skin(a, tier):
	r = bat_mask(a)
	if r is None:
		return a
	m, tip, u, length = r
	a = a.copy()
	nrm = np.array([-u[1], u[0]])
	at = lambda t, s=0.0: tip - u * t + nrm * s   # จุดบนไม้ห่างปลาย t ห่างแกน s
	if tier in RAMP:
		recolor(a, m, RAMP[tier])
	if tier == "CR-1":   # รอยร้าวซิกแซกกลางไม้
		for i, s in enumerate([-1, 0, 1, 0, -1]):
			p = at(length * 0.45 + i, s * 0.8)
			if m[int(round(p[0])), int(round(p[1]))]:
				put(a, *p, (40, 22, 12))
	if tier == "CR-6":   # ตะปูโผล่สองข้างช่วงหัวไม้
		for i, t in enumerate(np.arange(2, length * 0.5, 3.5)):
			side = 1 if i % 2 == 0 else -1
			put(a, *at(t, side * 2.4), (54, 54, 64))   # ตะปู: หัวเข้มติดไม้ + ปลายสว่างโผล่ออก
			put(a, *at(t, side * 3.4), (226, 228, 236))
	if tier == "CR-4":   # เฟืองที่ปลายไม้
		c = at(2.5)
		for ang in np.linspace(0, 2 * np.pi, 8, endpoint=False):
			for rr in (4.0, 5.0):
				put(a, c[0] + np.sin(ang) * rr, c[1] + np.cos(ang) * rr, (38, 40, 46))
		for dy in range(-3, 4):
			for dx in range(-3, 4):
				if dy * dy + dx * dx <= 9:
					put(a, c[0] + dy, c[1] + dx, (58, 62, 70) if dy * dy + dx * dx > 2 else (150, 156, 168))
	if tier == "CR-9":   # วงแหวนรูนสีฟ้ารอบช่วงหัวไม้
		for t in (length * 0.18, length * 0.36):
			for s in (-1.6, -0.6, 0.6, 1.6):
				p = at(t, s)
				if m[int(round(p[0])), int(round(p[1]))]:
					put(a, *p, (110, 220, 255))
	if tier == "CR-10":   # สายฟ้าซิกแซกตามไม้ + ขอบเรืองเหลือง
		for i, t in enumerate(np.arange(1, length * 0.8, 1.5)):
			p = at(t, (0.9, 0, -0.9, 0)[i % 4])
			if m[int(round(p[0])), int(round(p[1]))]:
				put(a, *p, (255, 244, 120))
		ring = np.zeros_like(m)
		for dy in (-1, 0, 1):
			for dx in (-1, 0, 1):
				ring |= np.roll(np.roll(m, dy, 0), dx, 1)
		for y, x in zip(*np.nonzero(ring & (a[..., 3] < 128))):
			a[y, x] = [255, 236, 90, 200]
	return a


def main():
	os.makedirs(OUT, exist_ok=True)
	srcs = sorted(glob.glob(os.path.join(SRC, "pls_bat*.png")))
	rows = []
	for p in srcs:
		a = np.array(Image.open(p).convert("RGBA"))
		name = os.path.splitext(os.path.basename(p))[0]
		row = [a]
		for t in TIERS:
			b = skin(a, t)
			Image.fromarray(b, "RGBA").save(os.path.join(OUT, f"wsk_{name}__{t}.png"))
			row.append(b)
		rows.append(row)
	pick = [i for i, p in enumerate(srcs) if any(k in p for k in ("breath_0", "run_3", "bat2_1", "bat2_0", "imp_0", "hop_5"))]
	sc = 3
	sheet = Image.new("RGB", ((len(TIERS) + 1) * 100 * sc, len(pick) * 87 * sc), (70, 70, 80))
	for j, i in enumerate(pick):
		for k, b in enumerate(rows[i]):
			im = Image.fromarray(b, "RGBA").crop((10, 25, 110, 112)).resize((100 * sc, 87 * sc), Image.NEAREST)
			sheet.paste(im, (k * 100 * sc, j * 87 * sc), im)
	sheet.save(os.path.join(OUT, "check.png"))
	print(len(srcs), "ภาพ x", len(TIERS), "ระดับ →", OUT)


if __name__ == "__main__":
	main()
