# tools/sprites/rion_grips.py — ท่า Rion ตามกลุ่มการจับอาวุธ (5 เฟรม: ยืนถือ · ง้าง · ลงมือ · ต่อ · ตามแรง)
# เดิมมีแค่ท่าฟันมีด (rion_anim.attack_west) ซึ่งแขนไม่ขยับ — ที่นี่ลบแขนหน้าเดิมแล้ววาดแขนใหม่ (ไหล่→ศอก→มือ)
# กลุ่ม: twohand (ไม้เบสบอล/หอกยาว · สองมือ) · aim (ที่เย็บ/ปืนตะปู/หน้าไม้ · ยกแขนเล็ง มือหลังประคอง)
#        sling (หนังสติ๊ก · มือหน้ายื่นถือง่าม มือหลังดึงยาง) · punch (ถุงมือ · การ์ด→ง้าง→ต่อยตรง)
# ผล: assets/sprites/rion_lastlight_draft/grips/<group>_<i>.png + ตำแหน่งมือ/มุมอาวุธใน POSES (weapons_held.py อ่าน)
import os, math
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/west.png')
OUT = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/grips')
SKIN, SKIN_D, SHIRT, OUTL = (212, 176, 138), (179, 122, 85), (210, 189, 154), (21, 15, 13)
SH_F, SH_B = (26, 39), (31, 39)    # ไหล่หน้า/หลัง (ท่ายืน หันซ้าย)

# ต่อเฟรม: (เลื่อนตัว dx, ศอกหน้า, มือหน้า, ศอกหลัง|None, มือหลัง|None, มุมอาวุธ)
# มุมจอ: 0 = ชี้ขวา · 90 = ขึ้น · 180 = ชี้ซ้าย (หน้า)
POSES = {
	'twohand': [   # ตั้งไม้ระดับอก → ง้างหลังหัว → เหวี่ยงผ่านหน้า → ต่อ → ตามแรงลงต่ำ
		(0, (24, 44), (23, 45), (29, 44), (24, 44), 100),
		(3, (32, 40), (33, 34), (35, 40), (34, 34), 55),
		(-4, (21, 42), (17, 43), (25, 43), (18, 43), 172),
		(-4, (21, 44), (17, 45), (25, 45), (18, 45), 200),
		(-1, (23, 47), (21, 49), (27, 48), (22, 49), 250)],
	'aim': [       # ถือต่ำ → ยกขึ้น → เหยียดแขนเล็ง มือหลังประคอง → ยิง (สะบัด) → ลดลง
		(0, (24, 45), (22, 47), None, None, 195),
		(0, (22, 42), (19, 42), (27, 43), (21, 43), 182),
		(-2, (20, 41), (15, 41), (25, 42), (18, 42), 180),
		(-1, (21, 40), (17, 40), (26, 41), (19, 41), 172),
		(0, (22, 43), (19, 44), (27, 44), (21, 44), 188)],
	'sling': [     # ถือข้างตัว → ยกง่าม → เหยียดแขนหน้า มือหลังดึงยางถึงแก้ม → ปล่อย → ลด
		(0, (24, 45), (22, 47), None, None, 100),
		(0, (21, 42), (18, 41), (27, 41), (24, 40), 95),
		(-1, (19, 40), (14, 39), (29, 38), (31, 36), 95),
		(-2, (19, 40), (14, 39), (27, 40), (25, 41), 95),
		(0, (21, 43), (18, 44), None, None, 100)],
	'punch': [     # การ์ดหน้าอก → ดึงหมัดไปหลัง → ต่อยตรง → ค้าง → คืนการ์ด
		(0, (24, 44), (22, 41), None, None, 180),
		(2, (30, 44), (30, 41), None, None, 180),
		(-4, (20, 41), (14, 41), None, None, 180),
		(-4, (20, 41), (15, 41), None, None, 180),
		(-1, (24, 44), (21, 41), None, None, 180)],
	# เวทย์ (6 เฟรม): มือหลังถือตำราเปิดที่อก ตลอด · มือหน้าทำท่า
	'cast_fwd': [  # ถือตำรา → ยกมือหน้าขึ้นรวมพลัง → ดึงกลับ → ผลักฝ่ามือไปหน้า → ค้าง → ลดมือ
		(0, (24, 45), (23, 47), (28, 45), (25, 43), 0),
		(0, (24, 41), (23, 37), (28, 45), (25, 43), 0),
		(1, (27, 42), (27, 38), (29, 45), (26, 43), 0),
		(-3, (20, 41), (15, 41), (25, 45), (22, 43), 0),
		(-3, (20, 41), (15, 41), (25, 45), (22, 43), 0),
		(0, (23, 44), (21, 46), (28, 45), (25, 43), 0)],
	'cast_up': [   # ถือตำรา → ยกมือหน้าเฉียงขึ้น → ชูฝ่ามือสูงพ้นหน้า (หัวโต แขนสั้น ชูตรงจะบังหน้า) → ค้าง → ค้าง → ลดมือ
		(0, (24, 45), (23, 47), (28, 45), (25, 43), 0),
		(0, (23, 41), (20, 38), (28, 45), (25, 43), 0),
		(-1, (20, 37), (15, 33), (28, 45), (25, 43), 0),
		(-1, (19, 36), (13, 30), (28, 45), (25, 43), 0),
		(-1, (19, 36), (13, 30), (28, 45), (25, 43), 0),
		(0, (23, 43), (20, 42), (28, 45), (25, 43), 0)],
}

def remove_front_arm(im):
	"""ผิวช่วงลำตัว (แขนหน้าเดิม) → สีเสื้อ เพื่อไม่ให้มีแขนซ้ำเมื่อวาดแขนใหม่"""
	p = im.load()
	for y in range(39, 51):
		for x in range(18, 31):
			c = p[x, y]
			if c[3] and c[:3] in (SKIN, SKIN_D): p[x, y] = SHIRT + (255,)
	return im

def shift(im, dx):
	out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(im, (dx, 0)); return out

def thick_line(pix, a, b, col, w=2):
	(x0, y0), (x1, y1) = a, b; n = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) * 2))
	pts = set()
	for i in range(n + 1):
		t = i / n; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
		for ox in range(w):
			for oy in range(w): pts.add((int(round(x - 0.5 + ox)), int(round(y - 0.5 + oy))))
	return pts

def draw_arm(im, shoulder, elbow, hand, back=False):
	p = im.load(); upper = thick_line(p, shoulder, elbow, None); lower = thick_line(p, elbow, hand, None)
	fist = {(hand[0] + dx, hand[1] + dy) for dx in (-1, 0) for dy in (-1, 0)}
	body = upper | lower | fist
	sk = SKIN_D if back else SKIN
	for x, y in body:   # เส้นขอบรอบแขนก่อน
		for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			q = (x + ox, y + oy)
			if q not in body and 0 <= q[0] < 64 and 0 <= q[1] < 64: p[q] = OUTL + (255,)
	sleeve = {q for q in upper if math.hypot(q[0] - shoulder[0], q[1] - shoulder[1]) <= 3}
	for q in body:
		if 0 <= q[0] < 64 and 0 <= q[1] < 64:
			p[q] = (SHIRT if q in sleeve else SKIN_D if q in fist and q[1] == hand[1] else sk) + (255,)
	return im

def frames(group):
	base = remove_front_arm(Image.open(SRC).convert('RGBA')); out = []
	for dx, ef, hf, eb, hb, ang in POSES[group]:
		im = shift(base, dx)
		if hb: draw_arm(im, (SH_B[0] + dx, SH_B[1]), eb, hb, back=True)
		draw_arm(im, (SH_F[0] + dx, SH_F[1]), ef, hf)
		out.append(im)
	return out

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	for g in POSES:
		for i, im in enumerate(frames(g)): im.save(os.path.join(OUT, '%s_%d.png' % (g, i)))
	print('ok', len(POSES))
