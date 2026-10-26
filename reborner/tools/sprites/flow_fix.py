"""แก้ชีต Flow ก่อนตัด (ไม่แตะไฟล์ต้นฉบับ) — ลบของเกินในช่องแล้วเติมสีตามพื้นที่
  ใช้โดย rion_px_weapons.py: fixed(sheet_key, rgb) → rgb ที่แก้แล้ว
รอบ 15-1 (flow_trial_v15_1b.jpg · kwan 16 ต.ค. เลือก "1 แก้ด้วยโค้ด"): แถวมีด ช่อง 1 ถือมีด 2 เล่ม → ลบใบมีด+ด้ามของมือหลัง (ตัดผ่านกางเกง)
  พื้นที่ลบ = จุดในรูปหลายเหลี่ยมที่ไม่ใช่ พื้นเขียว/ผิว/น้ำเงินกางเกง · ซ้ายเส้นขอบกางเกง (edge) = พื้นเขียว · ขวา = สีกางเกง (ค่ากลางจากกล่อง sample)
  แล้ววาดเส้นขอบเข้มใหม่ทุกจุดที่ไม่ใช่พื้นและอยู่ติดพื้นเขียว ≤ 2 จุด + รอยต่อกางเกงที่เติมกับกำปั้น/เป้ (เฉพาะรอบพื้นที่ลบ)"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

BG = (6, 190, 30)
OUTLINE = (42, 30, 28)
FIX = {"v15_1": [{
	"poly": [(68, 282), (90, 286), (152, 311), (154, 321), (140, 324), (108, 322), (84, 318), (74, 308), (68, 296)],
	"edge": ((72, 284), (76, 313)),   # ขอบซ้ายกางเกง (บน → ล่าง) · ชิดกำปั้น ไม่เหลือช่องพื้นระหว่างมือกับกางเกง
	"sample": (108, 150, 296, 312),   # กล่องสีกางเกง x0 x1 y0 y1
}]}


def _poly(shape, pts):
	pm = Image.new("L", (shape[1], shape[0]), 0); ImageDraw.Draw(pm).polygon(pts, fill=255)
	return np.array(pm) > 0


def _masks(a):
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	bg = (g > 140) & (g > r + 60) & (g > b + 60)
	skin = (r > 190) & (g > 140) & (r > b + 30)
	blue = (b > r + 50) & (b > g + 20) & (b > 110)
	return bg, skin, blue


def fixed(key, rgb):
	a = rgb.astype(float).copy()
	for f in FIX.get(key, []):
		pm = _poly(a.shape, f["poly"])
		bg, skin, blue = _masks(a)
		hole = ndimage.binary_dilation(pm & ~bg & ~skin & ~blue, iterations=1) & pm & ~skin
		x0, x1, y0, y1 = f["sample"]
		sb = a[y0:y1, x0:x1][blue[y0:y1, x0:x1]]
		shorts = np.median(sb, axis=0)
		(ex0, ey0), (ex1, ey1) = f["edge"]
		Y, X = np.indices(bg.shape)
		line_x = ex0 + (ex1 - ex0) * (Y - ey0) / float(ey1 - ey0)
		# แถวที่มีกำปั้น: ขอบกางเกงเริ่มชิดขอบขวาของผิว (ไม่เหลือช่องพื้นเขียวแคบ ๆ)
		for y in np.unique(Y[hole]):
			xs = np.nonzero(skin[y, ex0 - 24:ex0 + 12])[0]
			if xs.size: line_x[y] = np.minimum(line_x[y], ex0 - 24 + xs.max() + 1)
		out = hole & (X < line_x)
		a[hole & ~out] = shorts
		a[out] = BG
		bg2 = _masks(a)[0]
		near = ndimage.binary_dilation(bg2, iterations=2) & ~bg2
		zone = ndimage.binary_dilation(hole, iterations=3)
		a[near & zone] = OUTLINE
		# รอยต่อกางเกงที่เติมกับของอื่นที่ไม่ใช่กางเกง (กำปั้น เป้) = เส้นขอบ 1 จุดฝั่งกางเกง
		fill = hole & ~out
		other = ~fill & ~_masks(a)[2] & ~bg2
		a[fill & ndimage.binary_dilation(other, iterations=1)] = OUTLINE
	return a
