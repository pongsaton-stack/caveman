# tools/sprites/rion_hd.py — Rion เดินหน้าแบบเนียนจากภาพใหญ่ (kwan 14 ต.ค. 2026 ส่งภาพ Rion หันหน้า 1145x1374 พื้นเขียว)
#
# ที่มา: ภาพ 64px ขยายแล้วขยับ → พิกเซลแตก (ไม่มีรายละเอียดระหว่างพิกเซล) · ภาพใหญ่มีรายละเอียดจริง ย่อแล้วขอบ/ลายเปลี่ยนนุ่มกว่า
# ขั้นตอน: ตัดพื้นเขียว → ทาหน้าหมวกสีครีมเป็นน้ำเงิน (kwan เลือก "ผมทาสีน้ำเงินเอง") → ย่อให้ตัวสูง 58×8 จุด → ล็อกสีพาเลตต์ Rion ในเกม (18 สี)
#   → แยกชิ้น หัว/ตัว/แขนซ้าย/แขนขวา/ขาซ้าย/ขาขวา ด้วยพิกัดที่วัดจากภาพ (ตาราง 50px) → ส่งให้ rion_smooth ขยับ (ชุดเดียวกับ Version 84) → ย่อ 8x8 → เส้นขอบรอบตัว
# ต้นฉบับ docs/art-bible/rion_hires/rion_front_src.png (ภาพที่ kwan เจน) · ร่าง ยังไม่เข้าเกม
# Version 86: kwan เจนภาพ 1 ใหม่ หมวกน้ำเงินทั้งใบ แขนกางห่างตัว → ใช้แทน (ภาพเดิม = rion_front_src_v1.png) · วัดพิกัดใหม่ · ทาหมวกยังอยู่แต่แทบไม่เจอครีม
#
#   python3 tools/sprites/rion_hd.py      → assets/sprites/rion_smooth_draft/hd_walk_south_<i>.png + hd_parts_check.png
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rion_smooth as RS

ROOT = RS.ROOT
SRC = os.path.join(ROOT, 'docs/art-bible/rion_hires/rion_front_src.png')
REF = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/south.png')
OUT = RS.OUT
S, H64 = RS.S, 58                      # ตัวสูง 58 จุดเท่า Rion ในเกม (south.png แถว 5–62)
FOOT_ABS, CX_ABS, H_ABS = 1316, 570, 1210   # วัดจากภาพต้นฉบับ: เท้าล่างสุด · กลางตัว · ความสูงตัว
F = H64 * S / H_ABS                    # จุดภาพต้นฉบับ → จุดภาพทำงาน (×8)
# พิกัดในภาพต้นฉบับ (วัดด้วยตาราง 50px)
NECK_Y, HIP_Y, LEG_SPLIT_X, SHOULDER_Y = 625, 1052, 570, 770
NECK_OVERLAP = 40                     # ตัดคอที่คาง (ไม่มีปกเสื้อบังแบบภาพเดิม) → ตัวต่อขึ้นไปหลังหัว 40 จุด
# แขน = รูปหลายเหลี่ยมรอบแขนท่อนล่างใต้แขนเสื้อถึงกำปั้น (วัดจากตาราง) · sh = จุดหมุนที่ไหล่/ปลายแขนเสื้อ
ARM_L = dict(poly=[(372, 790), (440, 828), (425, 880), (412, 910), (410, 1000), (320, 1000), (322, 930), (345, 870), (358, 815)], sh=(405, 810))
ARM_R = dict(poly=[(700, 828), (762, 790), (785, 840), (808, 880), (820, 1000), (725, 1000), (722, 930), (705, 880)], sh=(735, 810))

def to64(x, y): return 32 + (x - CX_ABS) * F / S, 63 - (FOOT_ABS - y) * F / S
def to_work(x, y): a, b = to64(x, y); return a * S, b * S

def load_src():
	a = np.asarray(Image.open(SRC).convert('RGB')).astype(np.int32)
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	alpha = (g - np.maximum(r, b)) < 40                                  # พื้นเขียว = โปร่ง
	# หน้าหมวกสีครีม → น้ำเงิน (ครีม = สว่าง อุ่น ไม่อิ่มตัว · เว้นแว่น (ทอง b ต่ำ) และหน้า/ผม (ต่ำกว่าแถวหมวก))
	yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
	cream = alpha & (yy < 400) & (r > 190) & (g > 180) & (b > 140) & (r - b < 95) & (r - b > 5)
	lum = (r + g + b) / 3.0
	blue_hi, blue_lo = np.array([92, 140, 215]), np.array([52, 96, 178])   # ไล่จากสีน้ำเงินของหมวกเดิมในภาพ
	k = np.clip((lum - 170) / 80.0, 0, 1)[..., None]
	a = np.where(cream[..., None], (blue_lo + (blue_hi - blue_lo) * k).astype(np.int32), a)
	return a, alpha, int(cream.sum())

def palette():
	p = np.asarray(Image.open(REF).convert('RGBA')).reshape(-1, 4)
	return np.array(sorted({tuple(c[:3]) for c in p if c[3] > 0}), np.float64)

def work_image(a, alpha, pal):
	"""ย่อเป็นผืนทำงาน 512x512 (ตัว 464 จุด เท้าที่แถว 63×8) แล้วล็อกสี"""
	rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
	src = Image.fromarray(rgba, 'RGBA')
	w, h = round(src.width * F), round(src.height * F)
	small = np.asarray(src.resize((w, h), Image.LANCZOS)).astype(np.float64)
	ox, oy = to_work(0, 0)
	canvas = np.zeros((64 * S, 64 * S, 4), np.uint8)
	op = small[..., 3] > 127
	idx = ((small[..., :3][..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
	col = pal[idx].astype(np.uint8)
	out = np.zeros_like(small, dtype=np.uint8); out[..., :3] = col; out[..., 3] = op * 255
	x0, y0 = int(round(ox)), int(round(oy))
	cy0, cx0 = max(0, y0), max(0, x0); sy0, sx0 = cy0 - y0, cx0 - x0
	hh, ww = min(64 * S - cy0, h - sy0), min(64 * S - cx0, w - sx0)
	canvas[cy0:cy0 + hh, cx0:cx0 + ww] = out[sy0:sy0 + hh, sx0:sx0 + ww]
	return canvas

def masks(canvas):
	"""แยกชิ้นในผืนทำงาน · แขน = ผิว/นาฬิกาในกรอบแขน + ขอบเข้มที่ติดผิว (ขยาย 2 จุด)"""
	Hh, Ww = canvas.shape[:2]; yy, xx = np.mgrid[0:Hh, 0:Ww]
	op = canvas[..., 3] > 0; c = canvas[..., :3].astype(np.int32)
	def wy(y): return to_work(0, y)[1]
	def wx(x): return to_work(x, 0)[0]
	head = op & (yy < wy(NECK_Y))
	legs = op & (yy >= wy(HIP_Y))
	leg_l, leg_r = legs & (xx < wx(LEG_SPLIT_X)), legs & (xx >= wx(LEG_SPLIT_X))
	from PIL import ImageDraw
	def arm(A):
		m = Image.new('L', (Ww, Hh)); ImageDraw.Draw(m).polygon([to_work(x, y) for x, y in A['poly']], fill=255)
		return op & (np.asarray(m) > 0) & ~head & ~legs
	arm_l, arm_r = arm(ARM_L), arm(ARM_R)
	torso = op & ~head & ~legs & ~arm_l & ~arm_r
	torso |= op & (yy >= wy(NECK_Y - NECK_OVERLAP)) & (yy < wy(NECK_Y))   # คางซ้อนหลังหัว: หัวตามช้าแล้วไม่เห็นช่องที่คอ
	return dict(head=head, leg_l=leg_l, leg_r=leg_r, arm_l=arm_l, arm_r=arm_r, torso=torso)

def fill_holes(canvas, torso, arm, side):
	"""ใต้แขน (ตอนแขนแกว่งออก) เติมสีตัวที่ใกล้สุดในแถวเดียวกัน ฝั่งลำตัว · ไม่มีตัวในระยะ = โปร่ง"""
	out = np.zeros_like(canvas); out[torso] = canvas[torso]
	ys, xs = np.nonzero(arm)
	step = 1 if side == 'l' else -1
	for y, x in zip(ys, xs):
		for d in range(1, 48):
			xx = x + step * d
			if 0 <= xx < canvas.shape[1] and torso[y, xx]: out[y, x] = canvas[y, xx]; break
	return out

def outline(im, color):
	"""ขอบเข้มรอบตัว: พิกเซลทึบที่ติดพื้นโปร่ง (4 ทิศ) → สีเข้มสุดของพาเลตต์"""
	a = np.asarray(im).copy(); op = a[..., 3] > 0
	edge = op.copy(); e = np.zeros_like(op)
	e[1:] |= ~op[:-1]; e[:-1] |= ~op[1:]; e[:, 1:] |= ~op[:, :-1]; e[:, :-1] |= ~op[:, 1:]
	edge &= e; a[edge, :3] = color
	return Image.fromarray(a)

def build():
	a, alpha, n_cream = load_src(); pal = palette()
	canvas = work_image(a, alpha, pal)
	M = masks(canvas)
	layer = lambda m: Image.fromarray(np.where(m[..., None], canvas, 0).astype(np.uint8), 'RGBA')
	torso = M['torso'] | M['arm_l'] | M['arm_r']
	t = fill_holes(canvas, M['torso'], M['arm_l'], 'l'); t2 = fill_holes(canvas, M['torso'], M['arm_r'], 'r')
	t[M['arm_r']] = t2[M['arm_r']]
	parts = {'head': layer(M['head']), 'torso': Image.fromarray(t, 'RGBA'), 'arm_l': layer(M['arm_l']), 'arm_r': layer(M['arm_r']),
		'leg_l': layer(M['leg_l']), 'leg_r': layer(M['leg_r']), 'pack': Image.new('RGBA', (64 * S, 64 * S))}
	# ตั้งค่า rion_smooth ให้ตรงสัดส่วนภาพใหม่
	RS._cache.clear(); RS._cache.update(parts)
	RS.HIP = to64(0, HIP_Y)[1]; RS.SHOULDER = to64(0, SHOULDER_Y)[1]; RS.FOOT = 63
	RS.SH_L = to64(*ARM_L['sh']); RS.SH_R = to64(*ARM_R['sh'])
	dark = tuple(int(v) for v in pal[np.argmin(pal.sum(1))])
	frames = []
	for i in range(RS.FRAMES):
		f = RS.frame(i / RS.FRAMES); body = f.crop((0, RS.TOP, 64, RS.TOP + 64))
		g = Image.new('RGBA', f.size); g.alpha_composite(outline(body, dark), (0, RS.TOP)); frames.append(g)
	return frames, parts, canvas, n_cream

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	frames, parts, canvas, n_cream = build()
	for i, f in enumerate(frames): f.save(os.path.join(OUT, 'hd_walk_south_%02d.png' % i))
	# ภาพตรวจ: ผืนทำงาน + ชิ้นแต่ละสี
	chk = Image.new('RGBA', (64 * S * 2, 64 * S), (38, 34, 30, 255)); chk.alpha_composite(Image.fromarray(canvas, 'RGBA'), (0, 0))
	tint = {'head': (255, 80, 80), 'torso': (80, 200, 80), 'arm_l': (80, 120, 255), 'arm_r': (255, 200, 40), 'leg_l': (200, 80, 255), 'leg_r': (40, 220, 220)}
	for k, col in tint.items():
		m = np.asarray(parts[k])[..., 3] > 0; t = np.zeros((64 * S, 64 * S, 4), np.uint8); t[m] = col + (255,)
		chk.alpha_composite(Image.fromarray(t, 'RGBA'), (64 * S, 0))
	chk.save(os.path.join(OUT, 'hd_parts_check.png'))
	print('cream px recolored', n_cream, '· frames', len(frames), 'unique', len({f.tobytes() for f in frames}))
