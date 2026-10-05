# tools/sprites/weapons_held.py — Rion ถืออาวุธแต่ละชิ้น (ท่ายืน + ฟัน 4 เฟรม) ตามหลักกายภาพ
# ขนาด: ยาวตามของจริงโดยประมาณ (HELD_CM) × PX_PER_CM (Rion สูง ~50 จุด ≈ 140 ซม.) × CHIBI (ขยายของเล็กให้อ่านออก)
# การจับ: มีด/ดินสอ = มือเดียวจับด้าม ปลายชี้หน้า · ไม้เบสบอล = พาดบ่า→เหวี่ยงแนวนอน · หนังสติ๊ก = ง่ามตั้ง ยื่นไปหน้า
#        ที่เย็บ/ปืนตะปู = จับด้ามเหมือนปืน ชี้หน้า · ถุงมือ = สวมที่มือ (ไม่หมุน ทั้งตัวเท่าฝ่ามือ)
# หมุนแบบ "ขยาย 8 เท่า → หมุน nearest → ย่อด้วยสีส่วนใหญ่" แล้วใส่เส้นขอบใหม่ที่ขนาดจริง (พิกเซลเท่ากับตัวละคร)
# ผล: assets/sprites/weapons_held/<id>_<frame>.png (64x64 ซ้อนบน Rion แล้ว) — ร่าง ไม่เข้าเกม
import os, sys, json, math, colorsys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weapons as W

ROOT = W.ROOT
RION = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft')
OUT = os.path.join(ROOT, 'assets/sprites/weapons_held')
PX_PER_CM = 50 / 140.0
CHIBI = 1.3
MIN_PX = 12          # ของเล็กกว่านี้อ่านไม่ออกที่ขนาดตัวละคร — ขยายขั้นต่ำ
BEHIND = {'bat': (1,)}   # เฟรมที่อาวุธอยู่หลังตัว (ไม้พาดบ่า/ง้างไปหลังหัว)
# มือข้างหน้าในแต่ละเฟรม (วัดจากภาพ · ตรวจด้วยจุดเขียวแล้ว)
HAND = {'west': (23, 47), 'west_a0': (30, 41), 'west_a1': (24, 46), 'west_a2': (24, 46), 'west_a3': (25, 50)}
FRAMES = ['west', 'west_a0', 'west_a1', 'west_a2', 'west_a3']
# ความยาวของจริงโดยประมาณ (ซม.) — ใช้กำหนดขนาดภาพเท่านั้น ไม่ใช่ค่าเกม
HELD_CM = {'SL-1': 30, 'SL-2': 45, 'SL-3': 55, 'SL-4': 60, 'SL-5': 38,
	'PC-1': 19, 'PC-2': 24, 'PC-3': 60, 'PC-4': 75, 'PC-5': 85,
	'CR-1': 80, 'CR-2': 82, 'CR-3': 85, 'CR-4': 95, 'CR-5': 86,
	'ST-1': 20, 'ST-2': 24, 'ST-3': 28, 'ST-4': 70, 'ST-5': 24,
	'DV-1': 16, 'DV-2': 24, 'DV-3': 34, 'DV-4': 45, 'DV-5': 18}
# มุมจอ (องศา · 0 = ชี้ขวา · 90 = ชี้ขึ้น · Rion หันซ้าย = หน้า 180) ต่อเฟรม ยืน, ง้าง, ฟัน, ฟันต่อ, ตามแรง
POSE = {
	'blade': [215, 95, 175, 190, 230],     # มือเดียว ปลายต่ำไปหน้า → ง้างขึ้น → แทง/ฟันแนวนอน → ตามลงต่ำ
	'bat':   [100, 75, 165, 195, 245],     # ตั้งไม้รอ (ปลายขึ้น) → ง้างไปหลังหัว → เหวี่ยงแนวนอน → ตามแรงลงต่ำ
	'sling': [100, 95, 92, 92, 100],       # ง่ามตั้งขึ้น ยื่นไปหน้า (ยางดึงไม่ได้วาด)
	'gun':   [200, 170, 180, 182, 190],    # ชี้หน้า ต่ำเล็กน้อย → ยกเล็ง → ยิง (สะบัดนิดเดียว)
}
FAMILY_POSE = {'SL': 'blade', 'PC': 'blade', 'CR': 'bat', 'ST': 'sling', 'DV': 'gun'}
POSE_OVERRIDE = {'ST-4': 'gun'}   # หน้าไม้ร่ม = ประทับยิงแนวนอนเหมือนปืน ไม่ใช่ตั้งง่าม

def plain_icon(fam, tier):
	"""ไอคอนแบบไม่มีเส้นขอบ (เส้นขอบใส่ใหม่หลังย่อ)"""
	orig = W.Weapon.image
	def no_outline(self):
		im = Image.new('RGBA', (W.N, W.N), (0, 0, 0, 0)); p = im.load()
		for y in range(W.N):
			for x in range(W.N):
				if self.px[y][x]: p[x, y] = self.px[y][x]
		return im
	W.Weapon.image = no_outline
	try: return W.DRAW[fam](tier)
	finally: W.Weapon.image = orig

def grip_and_dir(fam, icon):
	"""จุดจับ (ในไอคอน) และมุมของอาวุธในไอคอน"""
	if fam in ('SL', 'PC', 'CR'): return (6.0, 26.0), 45.0       # ท้ายด้ามแกนทแยง
	if fam == 'ST': return (7.0, 27.0), 45.0                       # ปลายด้ามหนังสติ๊ก
	bb = icon.getbbox(); return (bb[0] + 5.0, bb[3] - 3.0), 0.0    # ปืน/ที่เย็บ: ด้ามล่างท้าย ตัวชี้ขวา

def mode_downscale(big, k):
	"""ย่อด้วย 'สีที่มากที่สุดในบล็อก' — รักษาสีพาเลตต์ ไม่เบลอ"""
	a = np.asarray(big); H, Wd = a.shape[:2]; h, w = max(1, H // k), max(1, Wd // k)
	out = np.zeros((h, w, 4), np.uint8)
	for y in range(h):
		for x in range(w):
			blk = a[y * k:(y + 1) * k, x * k:(x + 1) * k].reshape(-1, 4)
			op = blk[blk[:, 3] > 0]
			if len(op) * 2 < len(blk) * 0.8: continue
			cols, cnt = np.unique(op, axis=0, return_counts=True); out[y, x] = cols[cnt.argmax()]
	return Image.fromarray(out, 'RGBA').copy()

def outline(im):
	im = im.copy(); p = im.load(); Wd, H = im.size; edge = []
	for y in range(H):
		for x in range(Wd):
			if p[x, y][3]: continue
			nb = [p[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < Wd and 0 <= y + dy < H and p[x + dx, y + dy][3]]
			if nb:
				r, g, b = [sum(c[i] for c in nb) / len(nb) / 255 for i in range(3)]
				h, s, v = colorsys.rgb_to_hsv(r, g, b); h = (h + ((0.72 - h + 0.5) % 1 - 0.5) * 0.25) % 1
				R, G, B = colorsys.hsv_to_rgb(h, min(1, s * 0.9 + 0.25), max(0.08, min(0.24, v * 0.3)))
				edge.append((x, y, (int(R * 255), int(G * 255), int(B * 255), 255)))
	for x, y, c in edge: p[x, y] = c
	return im

def held_sprite(icon, grip, icon_dir, length_px, angle):
	"""คืน (ภาพ, จุดจับในภาพ) — หมุนรอบจุดจับให้ทิศอาวุธ = angle · ยาว length_px"""
	K = 8; bb = icon.getbbox()
	icon_len = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) if icon_dir else (bb[2] - bb[0])
	s = length_px / icon_len
	big = icon.resize((W.N * K, W.N * K), Image.NEAREST)
	pad = W.N * K * 2; canvas = Image.new('RGBA', (pad, pad), (0, 0, 0, 0))
	gx, gy = grip[0] * K, grip[1] * K; canvas.paste(big, (int(pad / 2 - gx), int(pad / 2 - gy)), big)
	flip = 90 < angle < 270 and not icon_dir      # ปืน/ที่เย็บ: หันซ้ายด้วยการพลิก ไม่ใช่หมุนกลับหัว
	if flip:
		canvas = canvas.transpose(Image.FLIP_LEFT_RIGHT); rot = 180 - angle
	else:
		rot = angle - icon_dir
	canvas = canvas.rotate(rot, Image.NEAREST)
	k2 = max(1, round(K / s)); small = mode_downscale(canvas, k2)
	c = small.size[0] / 2.0
	return small, (c, c)

def strip_baked_knife(frame, name):
	"""เฟรมฟันมีดีดเดิมมีมีดกับส่วนโค้งแดงวาดติดมา — ลบออกก่อนซ้อนอาวุธอื่น"""
	im = frame.copy(); p = im.load(); hx, hy = HAND[name]
	for y in range(64):
		for x in range(64):
			r, g, b, a = p[x, y]
			if not a: continue
			# ตัว Rion เริ่มที่ x 16 (ท่ายืน) — ทุกอย่างทางซ้ายกว่านั้นคือมีด/ส่วนโค้งที่วาดติดมา
			red = r > 100 and r > 2 * g and r > 2 * b
			knife = x < hx - 1 and 40 <= y <= 58 and abs(r - g) < 40 and abs(g - b) < 40
			if red or knife or x < 15: p[x, y] = (0, 0, 0, 0)
	return im

def glove_on(frame, icon, name, fist):
	"""ถุงมือ: ย่อทั้งตัวเท่าฝ่ามือ (~8 จุด) สวมทับมือ · ท่าฟัน = กำหมัดชี้หน้า (หมุน 90°)"""
	bb = icon.getbbox(); g = icon.crop(bb)
	if fist: g = g.rotate(90, Image.NEAREST, expand=True)
	k = max(1, round(max(g.size) * 8 / 9)); big = g.resize((g.width * 8, g.height * 8), Image.NEAREST)
	small = outline(mode_downscale(big, k)); hx, hy = HAND[name]
	frame.alpha_composite(small, (int(hx - small.width / 2), int(hy - small.height / 2)))
	return frame

def main():
	spec = json.load(open(W.SPEC, encoding='utf-8')); os.makedirs(OUT, exist_ok=True); n = 0
	for f in spec['families']:
		fam = f['family_id']
		for wpn in f['weapons']:
			icon = plain_icon(fam, wpn['tier'])
			for i, name in enumerate(FRAMES):
				base = Image.open(os.path.join(RION, name + '.png')).convert('RGBA')
				if name != 'west': base = strip_baked_knife(base, name)
				if fam == 'BD':
					out = glove_on(base, icon, name, i in (2, 3))
				else:
					grip, idir = grip_and_dir(fam, icon)
					L = max(MIN_PX, HELD_CM[wpn['id']] * PX_PER_CM * CHIBI)
					pose = POSE_OVERRIDE.get(wpn['id'], FAMILY_POSE[fam])
					spr, (cx, cy) = held_sprite(icon, grip, idir, L, POSE[pose][i])
					spr = outline(spr); hx, hy = HAND[name]; at = (int(round(hx - cx)), int(round(hy - cy)))
					if i in BEHIND.get(pose, ()):
						out = Image.new('RGBA', base.size, (0, 0, 0, 0)); out.alpha_composite(spr, at); out.alpha_composite(base)
					else:
						out = base.copy(); out.alpha_composite(spr, at)
				out.save(os.path.join(OUT, '%s_%d.png' % (wpn['id'], i))); n += 1
	print('ok', n)

if __name__ == '__main__':
	main()
