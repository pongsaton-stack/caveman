"""ภาพสไปรต์ Flow (Muse เจน · แนบ rion_ref_x8.png · 1024x1024 พื้นเทาเรียบ) → ผืนเกม 120x112 เท้าแถว 108 (kwan 25 ต.ค.)

Flow วาดบนตารางพิกเซลจริง (~11.75 จุด/พิกเซล ตัวสูง 71 = เท่า Rion เดิม) และวางหัวที่เดิมทุกภาพ →
  วัดขนาด/แนวตารางต่อภาพจากขอบสี → ค่ากลางกลางช่อง 6x6 → ตัดพื้น (ห่างสีพื้น < 30) → ปัดเข้าสีชุด Rion (pls_idle/atk) ถ้าใกล้
  เลื่อนทุกภาพในชุดเท่ากัน (ยึดภาพแรก: เท้าแถว 108 · กลางตัวคอลัมน์ 58) เพื่อให้ตำแหน่งตัวต่อเนื่องข้ามเฟรม
  python3 tools/sprites/flow_to_px.py OUT_DIR a.jpg b.jpg ... → OUT_DIR/<ชื่อ>_120.png + compare.png (ขยาย 4 เท่า)
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

PX = os.path.join(os.path.dirname(__file__), "../../assets/sprites/pixellab_draft/px_set/")


def palette():
	cols = {}
	for p in glob.glob(PX + "pls_idle_bl_*.png") + glob.glob(PX + "pls_atk_bl_*.png") + glob.glob(PX + "pls_idle_bt_*.png"):
		a = np.asarray(Image.open(p).convert("RGBA"))
		for c in a[a[..., 3] > 200][:, :3]:
			cols[tuple(c)] = cols.get(tuple(c), 0) + 1
	return np.array([c for c, n in cols.items() if n >= 3])


def grid(im, axis):
	g = np.abs(np.diff(im, axis=axis)).sum(2).sum(1 - axis)
	n = len(g)
	best = (0, 0, 0)
	for s in np.arange(10, 14, 0.05):
		for o in np.arange(0, s, 0.25):
			pos = np.round(np.arange(o, n, s)).astype(int)
			v = g[pos[pos < n]].mean()
			if v > best[0]:
				best = (v, s, o)
	return best[1], best[2]


def cells(path, pal):
	im = np.asarray(Image.open(path).convert("RGB")).astype(int)
	bg = np.median(im[:20, :20].reshape(-1, 3), 0)
	sx, ox = grid(im, 1)
	sy, oy = grid(im, 0)
	nx, ny = int((im.shape[1] - ox) // sx), int((im.shape[0] - oy) // sy)
	sm = np.zeros((ny, nx, 4), np.uint8)
	for j in range(ny):
		for i in range(nx):
			x0, y0 = int(ox + i * sx + sx / 2 - 3), int(oy + j * sy + sy / 2 - 3)
			c = np.median(im[y0:y0 + 6, x0:x0 + 6].reshape(-1, 3), 0)
			if np.abs(c - bg).sum() < 30:
				continue
			d = ((pal - c) ** 2).sum(1)
			k = d.argmin()
			sm[j, i, :3] = pal[k] if d[k] < 1800 else c.astype(np.uint8)
			sm[j, i, 3] = 255
	return Image.fromarray(sm), (sx, sy)


def main():
	out, srcs = sys.argv[1], sys.argv[2:]
	os.makedirs(out, exist_ok=True)
	pal = palette()
	shift = None
	frames = []
	for p in srcs:
		spr, s = cells(p, pal)
		bb = spr.getbbox()
		if shift is None:
			shift = (58 - (bb[0] + bb[2]) // 2, 109 - bb[3])
		can = Image.new("RGBA", (120, 112))
		can.paste(spr, shift, spr)
		name = os.path.splitext(os.path.basename(p))[0]
		can.save(os.path.join(out, name + "_120.png"))
		print(name, "grid %.2fx%.2f" % s, "size", bb[2] - bb[0], "x", bb[3] - bb[1], "clipped" if can.getbbox() != (bb[0] + shift[0], bb[1] + shift[1], bb[2] + shift[0], bb[3] + shift[1]) else "")
		frames.append(can)
	sc = 4
	sheet = Image.new("RGB", (120 * sc * len(frames), 112 * sc), (70, 70, 80))
	for i, c in enumerate(frames):
		u = c.resize((120 * sc, 112 * sc), Image.NEAREST)
		sheet.paste(u, (i * 120 * sc, 0), u)
	sheet.save(os.path.join(out, "compare.png"))


if __name__ == "__main__":
	main()
