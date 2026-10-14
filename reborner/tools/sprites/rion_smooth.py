# tools/sprites/rion_smooth.py — Rion เดินหน้าแบบเนียน (kwan 14 ต.ค. 2026 "ทำมาให้เลย เป็น rion ขยับเหมือนพระ")
#
# ที่มาของความเนียนในคลิปพระ (วัดหลังย่อเหลือขนาด Rion): ตัวเลื่อนแค่เศษพิกเซล — หัวยุบขึ้นลง 2 จุด 2 ครั้งต่อรอบ ·
#   อกส่ายสวนเท้า ±0.7 · เท้าเลื่อน ±1 · หัวแทบนิ่ง · แต่ภาพเปลี่ยนทุกเฟรมเพราะขยับต่อเนื่องที่ภาพใหญ่แล้วค่อยย่อ
# วิธีเดียวกัน: ขยายชิ้นส่วน Rion (rion_parts_draft/south_*) 8 เท่า → ขยับต่อเนื่อง (ยุบตัว · บิดอก · แกว่งแขน · ยกเข่า · หัว/เป้ตามช้า)
#   → ย่อกลับ 64 ด้วยสีที่มากสุดในบล็อก 8x8 (ได้แต่สีเดิมของ Rion ไม่มีสีใหม่) · ผืน 64x76 แบบ poses64 (เผื่อหัว 12)
# ค่าทั้งหมดเป็นค่าภาพ ไม่ใช่ค่าเกม · ร่าง ยังไม่เข้าเกม
#
#   python3 tools/sprites/rion_smooth.py      ส่งออก assets/sprites/rion_smooth_draft/walk_south_<i>.png + ภาพตรวจ
import math, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARTS = os.path.join(ROOT, 'assets/sprites/rion_parts_draft')
OUT = os.path.join(ROOT, 'assets/sprites/rion_smooth_draft')
S = 8                       # ขยายตอนขยับ
TOP = 12                    # เผื่อเหนือหัว (เท่า poses64)
CYCLE_SEC = 0.96            # รอบเดินเท่าคลิปพระ (23 ภาพ ~ 24 ภาพ/วินาที)
FRAMES = 24
HIP, SHOULDER, FOOT = 54, 36, 63
SH_L, SH_R = (23.5, 37.0), (38.5, 36.0)   # ไหล่ (ภาพ 64) จากกรอบ arm_l / arm_r ใน parts.json

# ขนาดการขยับ (หน่วย = พิกเซลของภาพ 64) วัดจากคลิปพระที่ย่อแล้ว
BOB = 1.6       # ตัวยกตอนขาผ่านกลาง (2 ครั้ง/รอบ)
TWIST = 0.7     # อกส่ายสวนเท้า
FEET = 0.9      # เท้าเลื่อนข้าง
HEAD_SWAY = 0.25
KNEE = 2.0      # ขาที่ยกขึ้นสั้นลง
ARM_DEG = 9.0   # แกว่งแขน
LAG = 0.07      # หัว/เป้ตามช้ากว่าตัว (สัดส่วนรอบ)

_cache = {}
def part(name):
	if name not in _cache:
		im = Image.open(os.path.join(PARTS, 'south_%s.png' % name)).convert('RGBA')
		_cache[name] = im.resize((64 * S, 64 * S), Image.NEAREST)
	return _cache[name]

def bob(t): return -BOB * (0.5 - 0.5 * math.cos(4 * math.pi * t))   # ต่ำสุดตอนเท้าแตะ (t 0, 0.5) · สูงสุดตอนขาผ่าน

def affine(im, dx=0.0, dy=0.0, deg=0.0, pivot=(32, 32), sy=1.0, sy_top=None):
	"""เลื่อน/หมุนรอบ pivot/ยุบแนวตั้งรอบ sy_top · หน่วยภาพ 64 · ทำที่ภาพใหญ่ (nearest)"""
	if abs(deg) > 1e-3: im = im.rotate(deg, Image.NEAREST, center=(pivot[0] * S, pivot[1] * S))
	if sy != 1.0:
		y0 = sy_top * S; a = 1.0 / sy                      # y_src = y0 + (y - y0) / sy
		im = im.transform(im.size, Image.AFFINE, (1, 0, 0, 0, a, y0 - y0 * a), Image.NEAREST)
	if dx or dy: im = im.transform(im.size, Image.AFFINE, (1, 0, -dx * S, 0, 1, -dy * S), Image.NEAREST)
	return im

def leg(im, top, bot, dx):
	"""ยืด/หดขาให้ช่วง HIP..FOOT+1 ของภาพเดิมไปอยู่ top..bot (ภาพ 64) + เลื่อนข้าง dx"""
	a = (FOOT + 1 - HIP) / (bot - top)                     # y_src = HIP + (y - top) * a
	return im.transform(im.size, Image.AFFINE, (1, 0, -dx * S, 0, a, (HIP - top * a) * S), Image.NEAREST)

def shear_rows(im, fn):
	"""เลื่อนแต่ละแถวตาม fn(y ภาพ 64) → dx (เศษพิกเซลได้)"""
	a = np.asarray(im).copy(); out = np.zeros_like(a)
	for y in range(a.shape[0]):
		k = int(round(fn(y / S) * S)); out[y] = np.roll(a[y], k, axis=0)
		if k > 0: out[y, :k] = 0
		elif k < 0: out[y, k:] = 0
	return Image.fromarray(out)

def downsample(big):
	"""ย่อ 8x8 → 1 ด้วยสีที่มากสุดในบล็อก (ทึบเมื่อทึบ ≥ ครึ่ง) · ได้แต่สีที่มีอยู่แล้ว"""
	a = np.asarray(big); H, W = a.shape[0] // S, a.shape[1] // S
	blk = a.reshape(H, S, W, S, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, S * S, 4)
	out = np.zeros((H, W, 4), np.uint8)
	for y in range(H):
		for x in range(W):
			px = blk[y, x]; op = px[px[:, 3] > 127]
			if len(op) * 2 < S * S: continue
			key = op[:, 0].astype(np.int64) << 16 | op[:, 1].astype(np.int64) << 8 | op[:, 2]
			v, c = np.unique(key, return_counts=True); k = v[c.argmax()]
			out[y, x] = ((k >> 16) & 255, (k >> 8) & 255, k & 255, 255)
	return Image.fromarray(out)

def frame(t):
	"""t = 0..1 ของรอบเดิน · เท้าซ้ายของภาพยกสูงสุดที่ t 0.25 · ขวาที่ 0.75"""
	ph = 2 * math.pi * t
	b, bl = bob(t), bob(t - LAG)                                   # ตัว · ส่วนที่ตามช้า (หัว/เป้)
	tw = -TWIST * math.cos(ph)                                     # อก (สวนเท้า)
	ft = FEET * math.cos(ph)
	lift_l, lift_r = KNEE * max(0.0, math.sin(ph)), KNEE * max(0.0, -math.sin(ph))
	canvas = Image.new('RGBA', (64 * S, 64 * S))
	def body_shift(y):                                             # เฉือน: สะโพก 0 → ไหล่เต็ม → หัวตามนิดเดียว
		if y >= HIP: return 0.0
		k = min(1.0, (HIP - y) / (HIP - SHOULDER)); return tw * k
	# เป้ (หลังตัว) ตามช้า + ส่ายตามอก
	canvas.alpha_composite(affine(part('pack'), dx=tw * 0.8, dy=bl * 1.15))
	# ขา: ขาที่ยกสั้นลงจากสะโพก + เท้าเลื่อนข้างสวนอก
	for side, lift in (('leg_l', lift_l), ('leg_r', lift_r)):
		canvas.alpha_composite(leg(part(side), HIP + b, FOOT + 1 - lift, ft))   # บนติดสะโพกที่ขยับตามตัว · เท้าติดพื้น (ยก = สั้นลง)
	# ตัว (เฉือนตามความสูง) + ยุบ
	canvas.alpha_composite(affine(shear_rows(part('torso'), body_shift), dy=b))
	# แขน: แกว่งสวนขา (แขนซ้ายของภาพไปหน้าเมื่อขาขวายก) หมุนรอบไหล่ที่ขยับตามตัว
	for side, sh, sgn in (('arm_l', SH_L, 1), ('arm_r', SH_R, -1)):
		deg = sgn * ARM_DEG * math.sin(ph)
		canvas.alpha_composite(affine(part(side), dx=body_shift(sh[1]), dy=b, deg=deg, pivot=sh))
	# หัว: ตามตัวช้านิด · ส่ายน้อยกว่าอก (หัวนิ่งแบบคลิป)
	canvas.alpha_composite(affine(part('head'), dx=tw * HEAD_SWAY, dy=bl))
	small = downsample(canvas)
	out = Image.new('RGBA', (64, 64 + TOP)); out.alpha_composite(small, (0, TOP)); return out

def frames(n=FRAMES): return [frame(i / n) for i in range(n)]

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'w').close()
	fr = frames()
	for i, f in enumerate(fr): f.save(os.path.join(OUT, 'walk_south_%02d.png' % i))
	sheet = Image.new('RGBA', (64 * 12, 76 * 2), (38, 34, 30, 255))
	for i, f in enumerate(fr): sheet.alpha_composite(f, ((i % 12) * 64, (i // 12) * 76))
	sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(OUT, '_sheet.png'))
	u = len({f.tobytes() for f in fr}); print('frames', len(fr), 'unique', u, '→', OUT)
