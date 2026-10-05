# tools/sprites/spells_anim.py — ท่าร่ายเวทย์ของ Rion + เอฟเฟกต์รายคาถา (ร่าง · ยังไม่เข้าเกม)
# อ่าน docs/art-bible/spells/spells_full.json · ท่าแขนจาก rion_grips.POSES (cast_fwd = ผลักฝ่ามือ · cast_up = ชูมือ)
# มือหลังถือตำราเปิดที่อกตลอด (GDD 7.2 ร่ายจากตำรา) · ผืนภาพ 96x64 Rion อยู่ขวา (x+32) หันซ้าย เป้าอยู่ซ้าย
# 8 เฟรม: 0 ยืนถือตำรา · 1-2 รวมพลัง (ตำราเรือง ประกายรอบมือ) · 3-6 ปล่อยเวทย์ · 7 ลดมือ เศษเวทย์จาง
# ผล: assets/sprites/spells_draft/<id>_<0-7>.png
import json, math, os, random
from PIL import Image, ImageDraw
import rion_grips as G

ROOT = G.ROOT
OUT = os.path.join(ROOT, 'assets/sprites/spells_draft')
W, H, OX = 96, 64, 32
GRIP_OF = [0, 1, 2, 3, 4, 4, 4, 5]          # เฟรมคลิป → เฟรมท่าแขน
TGT = (14, 40)                              # กลางตัวเป้า
COVER, COVER_D, PAGE, PAGE_D = (122, 52, 44), (84, 34, 30), (236, 226, 196), (196, 180, 146)
OUTL = G.OUTL

def rgba(c, a=255): return tuple(c[:3]) + (a,)

def book(im, hand, glow=None):
	"""ตำราเปิด 10x6 ถือหน้าอก (ปกแดงเลือดหมู สันกลาง) · glow = สีหน้ากระดาษตอนรวมพลัง"""
	d = ImageDraw.Draw(im); x, y = hand[0] - 6, hand[1] - 3
	d.rectangle([x - 1, y - 1, x + 10, y + 6], fill=rgba(OUTL))
	d.rectangle([x, y + 4, x + 9, y + 5], fill=rgba(COVER)); d.point([(x, y + 5), (x + 9, y + 5)], fill=rgba(COVER_D))
	pg = glow or PAGE
	d.rectangle([x, y, x + 3, y + 3], fill=rgba(pg)); d.rectangle([x + 6, y, x + 9, y + 3], fill=rgba(pg))
	d.rectangle([x + 4, y, x + 5, y + 4], fill=rgba(COVER_D))
	ink = (255, 255, 255) if glow else PAGE_D
	d.line([(x + 1, y + 1), (x + 2, y + 1)], fill=rgba(ink)); d.line([(x + 7, y + 1), (x + 8, y + 1)], fill=rgba(ink))
	d.point([(x + 1, y + 2), (x + 7, y + 2)], fill=rgba(ink))

def rion(grip, gi, glow=None):
	"""ประกอบ Rion: ตัว → แขนหลัง → ตำรา → แขนหน้า (แขนหน้าทับตำราได้)"""
	dx, ef, hf, eb, hb, _ = G.POSES[grip][gi]
	im = G.shift(G.remove_front_arm(Image.open(G.SRC).convert('RGBA')), dx)
	G.draw_arm(im, (G.SH_B[0] + dx, G.SH_B[1]), eb, hb, back=True)
	book(im, hb, glow)
	G.draw_arm(im, (G.SH_F[0] + dx, G.SH_F[1]), ef, hf)
	can = Image.new('RGBA', (W, H)); can.alpha_composite(im, (OX, 0))
	return can, (hf[0] + OX, hf[1])

# ── พู่กันพิกเซล ──
def dot(d, p, c, a=255): d.point([(int(p[0]), int(p[1]))], fill=rgba(c, a))
def disc(d, p, r, c, a=255): d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=rgba(c, a))
def ring(d, p, rx, ry, c, a=255, w=1): d.ellipse([p[0] - rx, p[1] - ry, p[0] + rx, p[1] + ry], outline=rgba(c, a), width=w)
def glowball(d, p, r, core, edge):
	disc(d, p, r + 1, edge, 110); disc(d, p, r, edge); disc(d, p, max(0, r - 1), core)
def sparkle(d, p, c, s=1):
	dot(d, p, (255, 255, 255))
	for i in range(1, s + 1):
		for q in ((i, 0), (-i, 0), (0, i), (0, -i)): dot(d, (p[0] + q[0], p[1] + q[1]), c, 255 - 70 * i)

def charge(d, hand, t, col, rnd):
	"""ประกายวนรอบมือหน้า t=1,2"""
	n = 3 if t == 1 else 5; r = 6 if t == 1 else 4
	for i in range(n):
		a = i * 2 * math.pi / n + t * 0.9
		sparkle(d, (hand[0] + r * math.cos(a), hand[1] + r * math.sin(a)), col, 1)
	disc(d, hand, t, col, 120)

# ── เอฟเฟกต์ปล่อยเวทย์ k = 0..3 (เฟรม 3-6) · k = 4 = เศษจาง (เฟรม 7) ──
def hexagon(d, c, r, col, a):
	pts = [(c[0] + r * math.cos(math.radians(60 * i + 30)), c[1] + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
	d.polygon(pts, fill=rgba(col, a // 3), outline=rgba(col, a))

def fx_WH_1(d, k, hand, rnd):   # กำแพงหกเหลี่ยมหน้าทีม (ฝั่งเรา = รอบ Rion · กั้นด้านหน้า)
	cells = [(26, 18), (26, 30), (26, 42), (26, 54), (20, 24), (20, 36), (20, 48)]
	show = [1, 4, 7, 7, 7][k]
	for i, c in enumerate(cells[:show]):
		a = 255 if k < 4 else 90
		hexagon(d, c, 5, (190, 236, 255) if (i + k) % 3 else (255, 244, 180), a)
	if k == 3:
		for _ in range(4): sparkle(d, rnd.choice(cells), (255, 244, 180), 1)

def fx_WH_2(d, k, hand, rnd):   # วงแหวนทองหมุนรอบตัว แล้วซึมเข้าอก
	c = (OX + 26, 40)
	r = [16, 12, 8, 3, 0][k]
	if r: ring(d, c, r, max(2, r // 2), (255, 214, 90), 255, 1); ring(d, c, r + 1, max(2, r // 2) + 1, (255, 244, 180), 120)
	for i in range(3):
		a = k * 1.3 + i * 2.1
		if r: sparkle(d, (c[0] + r * math.cos(a), c[1] + r / 2 * math.sin(a)), (255, 214, 90))
	if k >= 3: disc(d, c, 3 if k == 3 else 1, (255, 236, 150), 200 if k == 3 else 90)

def fx_WH_3(d, k, hand, rnd):   # ฟองสบู่แสงลอยขึ้นรอบตัวแล้วแตก
	base = [(OX + 16, 56), (OX + 24, 52), (OX + 32, 58), (OX + 20, 46), (OX + 30, 48)]
	for i, (x, y) in enumerate(base):
		yy = y - 8 * k - 3 * i
		if yy < 4: continue
		if k == 3 and i % 2: sparkle(d, (x, yy), (200, 240, 255), 2); continue
		if k == 4: dot(d, (x, yy), (220, 245, 255), 100); continue
		ring(d, (x, yy), 2 + i % 2, 2 + i % 2, (200, 240, 255), 220); dot(d, (x - 1, yy - 1), (255, 255, 255))

def heart(d, c, s, col):
	x, y = c
	disc(d, (x - s, y - s // 2), s, col); disc(d, (x + s, y - s // 2), s, col)
	d.polygon([(x - 2 * s, y - s // 2), (x + 2 * s, y - s // 2), (x, y + 2 * s)], fill=rgba(col))

def fx_WH_4(d, k, hand, rnd):   # หัวใจเย็บปะลอยลงหาเพื่อนร่วมทีม (ยืนหน้า Rion)
	tgt = (OX + 6, 34)
	if k < 3:
		y = [8, 18, 28][k]; heart(d, (tgt[0], y), 3, (21, 15, 13)); heart(d, (tgt[0], y), 2, (226, 92, 110))
		d.line([(tgt[0] - 2, y - 2), (tgt[0] + 2, y + 2)], fill=rgba((250, 230, 210)))   # รอยเย็บ
	elif k == 3:
		for i in range(6):
			a = i * math.pi / 3; sparkle(d, (tgt[0] + 7 * math.cos(a), tgt[1] + 7 * math.sin(a)), (255, 150, 170), 1)
	else:
		for i in range(3): dot(d, (tgt[0] - 4 + 4 * i, tgt[1] - 6 - i), (255, 170, 185), 140)

FIRE = [(255, 250, 200), (255, 214, 90), (255, 140, 40), (214, 64, 30)]
def fx_BK_1(d, k, hand, rnd):   # เปลวไฟพ่นตรงจากฝ่ามือ
	ln = [12, 26, 34, 30, 0][k]
	for i in range(ln):
		x = hand[0] - 2 - i; w = 1 + i // 6
		for yy in range(-w, w + 1):
			if rnd.random() < 0.85:
				lvl = min(3, (abs(yy) * 2 + i // 8 + rnd.randint(0, 1)))
				dot(d, (x, hand[1] + yy), FIRE[lvl])
	if k == 4:
		for i in range(5): dot(d, (TGT[0] + rnd.randint(-6, 6), TGT[1] - rnd.randint(0, 14)), (110, 100, 96), 160)

ICE = [(255, 255, 255), (190, 240, 255), (110, 200, 240), (60, 130, 200)]
def flake(d, p, c):
	for q in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): dot(d, (p[0] + q[0], p[1] + q[1]), c if q != (0, 0) else ICE[0])

def fx_BK_2(d, k, hand, rnd):   # ลมเย็นกวาดทั้งแถว (สามเส้นแนวนอน) + เกล็ดน้ำแข็ง
	if k == 4:
		for _ in range(6): dot(d, (rnd.randint(2, 30), rnd.randint(22, 58)), ICE[1], 150)
		return
	reach = [hand[0] - 14, hand[0] - 30, 0, 0][k]
	for row, y in enumerate((26, 40, 54)):
		for x in range(max(0, reach), hand[0] - 2):
			if (x + row * 3 + k * 5) % 7 < 4: dot(d, (x, y + int(1.5 * math.sin(x / 3 + k))), ICE[2], 200)
		for _ in range(3): flake(d, (rnd.randint(max(1, reach), hand[0] - 4), y + rnd.randint(-3, 3)), ICE[1])

def fx_BK_3(d, k, hand, rnd):   # ลำแสงกรวยขาวเหลือง
	if k == 4: sparkle(d, (TGT[0], TGT[1] - 4), (255, 244, 180), 2); return
	ln = [14, 40, 44, 44][k]; spread = [3, 9, 12, 10][k]
	tip = (hand[0] - ln, hand[1])
	d.polygon([(hand[0] - 2, hand[1] - 1), tip[0:1] + (hand[1] - spread,), (tip[0], hand[1] + spread), (hand[0] - 2, hand[1] + 1)], fill=rgba((255, 244, 180), 110))
	d.polygon([(hand[0] - 2, hand[1]), (tip[0], hand[1] - spread // 2), (tip[0], hand[1] + spread // 2)], fill=rgba((255, 255, 230), 200))
	sparkle(d, hand, (255, 244, 180), 2)

DARK = [(30, 14, 44), (78, 40, 110), (140, 90, 190), (200, 160, 240)]
def fx_BK_4(d, k, hand, rnd):   # ควันเงาม่วงพุ่งเป็นเส้นตรง (ทะลุแนว)
	if k == 4:
		for i in range(4): dot(d, (6 + 8 * i, hand[1] - 3 + (i % 2) * 6), DARK[2], 120)
		return
	reach = [hand[0] - 16, 0, 0, 0][k]
	for x in range(reach, hand[0] - 1):
		y = hand[1] + round(2 * math.sin(x / 4 + k * 1.7))
		dot(d, (x, y), DARK[1]); dot(d, (x, y + 1), DARK[0])
		if (x + k) % 5 == 0: dot(d, (x, y - 2 + rnd.randint(0, 1)), DARK[2], 200)
	if k >= 2:
		for _ in range(5): disc(d, (rnd.randint(2, hand[0] - 6), hand[1] + rnd.randint(-4, 4)), 1, DARK[3 if k == 2 else 2], 160)

def fx_BK_5(d, k, hand, rnd):   # ลูกไฟลอยไปแล้วระเบิดวงกว้าง (ศัตรูทุกตัว)
	if k < 2:
		p = (hand[0] - [6, 22][k], hand[1] - [2, 4][k]); glowball(d, p, 3, FIRE[0], FIRE[2])
		dot(d, (p[0] + 5, p[1] + 1), FIRE[3], 160); dot(d, (p[0] + 7, p[1] + 2), FIRE[3], 100)
	elif k == 2:
		c = (16, 38); disc(d, c, 15, FIRE[3], 160); disc(d, c, 12, FIRE[2]); disc(d, c, 8, FIRE[1]); disc(d, c, 4, FIRE[0])
	elif k == 3:
		c = (16, 38); ring(d, c, 17, 15, (110, 100, 96), 200, 2); disc(d, c, 9, FIRE[2], 200); disc(d, c, 5, FIRE[1], 220)
		for _ in range(6): dot(d, (c[0] + rnd.randint(-16, 16), c[1] + rnd.randint(-14, 14)), FIRE[1])
	else:
		for _ in range(8): dot(d, (16 + rnd.randint(-14, 14), 38 + rnd.randint(-16, 8)), (110, 100, 96), 150)

def fx_BK_6(d, k, hand, rnd):   # เข็มน้ำแข็งยาวสามเล่มพุ่งเรียงกัน
	if k == 4:
		for i in range(3): flake(d, (TGT[0] + 3 - 3 * i, TGT[1] - 4 + 4 * i), ICE[1])
		return
	for i in range(3):
		x = hand[0] - 4 - (k * 12 - i * 7)
		if x > hand[0] - 3: continue
		y = hand[1] - 3 + 3 * i; x = max(x, TGT[0] + 2)
		d.line([(x, y), (x + 9, y)], fill=rgba(ICE[2])); d.line([(x, y - 1), (x + 6, y - 1)], fill=rgba(ICE[1]))
		dot(d, (x - 1, y), ICE[0])
	if k == 3: sparkle(d, (TGT[0], TGT[1]), ICE[1], 2)

RED, RED_D = (226, 48, 48), (150, 24, 30)
def mark_circle(d, c, r, frac, col):
	if frac >= 1: ring(d, c, r, r, col, 255, 1); ring(d, (c[0] + 1, c[1]), r, r, col, 160, 1)
	else: d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], -90, -90 + 360 * frac, fill=rgba(col), width=2)
	d.point([(c[0] + r, c[1] - r + 2)], fill=rgba(RED))   # หางปากกา

def fx_RD_1(d, k, hand, rnd):   # หน้าปัดนาฬิกาหมุนเร็ว เหนือพวกเดียวกัน (ยืนหน้า Rion)
	c = (OX + 4, 22)
	if k == 4: ring(d, c, 6, 6, (240, 230, 200), 80); return
	disc(d, c, 7, OUTL); disc(d, c, 6, (240, 230, 200)); ring(d, c, 6, 6, RED_D)
	for i in range(2):   # เข็มยาว/สั้น หมุนเร็ว
		a = math.radians(-90 + k * 135 * (3 if i else 1)); r = 5 if i else 3
		d.line([c, (c[0] + r * math.cos(a), c[1] + r * math.sin(a))], fill=rgba(OUTL))
	for j in range(3): dot(d, (c[0] - 10 - 2 * j, c[1] - 3 + 3 * j), RED, 200)   # เส้นความเร็ว
	if k == 3: sparkle(d, (c[0] + 9, c[1] - 6), (255, 214, 90), 1)

def fx_RD_2(d, k, hand, rnd):   # แถบเทปกาวพันรอบเป้า
	if k == 4:
		for i in range(3): d.line([(TGT[0] - 7, TGT[1] - 8 + 7 * i), (TGT[0] + 7, TGT[1] - 6 + 7 * i)], fill=rgba((196, 178, 130), 140), width=2)
		return
	if k == 0:
		d.line([(hand[0] - 2, hand[1]), (TGT[0] + 10, TGT[1] - 6)], fill=rgba((214, 196, 150)), width=2); return
	for i in range(min(3, k + 1)):
		y = TGT[1] - 8 + 7 * i
		d.line([(TGT[0] - 8, y), (TGT[0] + 8, y + 2)], fill=rgba((214, 196, 150)), width=3)
		d.line([(TGT[0] - 8, y - 1), (TGT[0] + 8, y + 1)], fill=rgba((240, 226, 186)))

def blade_icon(d, c):
	d.line([(c[0] - 3, c[1] + 3), (c[0] + 3, c[1] - 3)], fill=rgba(RED), width=2); d.line([(c[0] - 4, c[1] + 1), (c[0] - 1, c[1] + 4)], fill=rgba(RED_D))
def hammer_icon(d, c):
	d.rectangle([c[0] - 3, c[1] - 3, c[0] + 3, c[1] - 1], fill=rgba(RED)); d.line([(c[0], c[1] - 1), (c[0], c[1] + 4)], fill=rgba(RED_D), width=2)

def pen_mark(icon):
	def fx(d, k, hand, rnd):    # วงกลมปากกาแดงขีดรอบเป้า แล้วประทับเครื่องหมายจุดอ่อน
		if k == 4: mark_circle(d, TGT, 12, 1, RED_D); icon(d, (TGT[0] + 12, TGT[1] - 12)); return
		mark_circle(d, TGT, 12, [0.35, 0.7, 1, 1][k], RED)
		if k >= 2: icon(d, (TGT[0] + 12, TGT[1] - 12))
		if k == 3: sparkle(d, (TGT[0] + 12, TGT[1] - 12), RED, 2)
	return fx

def fx_RD_5(d, k, hand, rnd):   # ยางลบชมพูถูไปมา เศษยางกระจาย
	if k == 4:
		for _ in range(5): dot(d, (TGT[0] + rnd.randint(-10, 10), TGT[1] + rnd.randint(6, 18)), (230, 150, 170), 180)
		return
	x = TGT[0] + [-6, 4, -4, 5][k]; y = TGT[1] - 6
	d.rectangle([x - 5, y - 3, x + 5, y + 3], fill=rgba(OUTL)); d.rectangle([x - 4, y - 2, x + 4, y + 2], fill=rgba((244, 160, 180)))
	d.rectangle([x + 1, y - 2, x + 4, y + 2], fill=rgba((90, 120, 200)))
	for _ in range(2 + k): dot(d, (x + rnd.randint(-8, 8), y + rnd.randint(4, 10)), (230, 150, 170))

def fx_SM_1(d, k, hand, rnd):   # วงชอล์กบนพื้นเรืองส้ม ร่างเงาเตาหินโผล่ขึ้นพ่นถ่าน
	c = (16, 58)
	ring(d, c, 15, 4, (236, 232, 220), 255 if k < 4 else 90)
	if k >= 1 and k < 4: ring(d, c, 13, 3, FIRE[2], 220); ring(d, c, 15, 4, FIRE[1], 140)
	for i in range(6):   # สัญลักษณ์ชอล์กบนวง
		a = i * math.pi / 3 + k * 0.3; dot(d, (c[0] + 15 * math.cos(a), c[1] + 4 * math.sin(a)), (255, 255, 255), 255 if k < 4 else 90)
	if k in (1, 2, 3):
		h = [10, 22, 26][k - 1]; top = c[1] - h
		d.rectangle([c[0] - 8, top, c[0] + 8, c[1] - 1], fill=rgba((38, 30, 30), 230))   # ตัวเตา (เงา)
		d.rectangle([c[0] - 9, top - 2, c[0] + 9, top + 1], fill=rgba((54, 44, 42), 230))   # ฝาเตา
		if h >= 22:
			d.rectangle([c[0] - 4, top + 8, c[0] + 4, top + 13], fill=rgba(FIRE[2])); d.rectangle([c[0] - 2, top + 9, c[0] + 2, top + 12], fill=rgba(FIRE[0]))   # ปากเตา
			dot(d, (c[0] - 4, top + 4), FIRE[1]); dot(d, (c[0] + 4, top + 4), FIRE[1])   # ตา
		if k == 3:
			for _ in range(10): dot(d, (c[0] + rnd.randint(-20, 30), top + rnd.randint(-10, 14)), rnd.choice(FIRE[:3]))
	if k == 4:
		for _ in range(6): dot(d, (c[0] + rnd.randint(-14, 14), c[1] - rnd.randint(4, 30)), FIRE[2], 140)

FX = {'WH-1': fx_WH_1, 'WH-2': fx_WH_2, 'WH-3': fx_WH_3, 'WH-4': fx_WH_4,
	'BK-1': fx_BK_1, 'BK-2': fx_BK_2, 'BK-3': fx_BK_3, 'BK-4': fx_BK_4, 'BK-5': fx_BK_5, 'BK-6': fx_BK_6,
	'RD-1': fx_RD_1, 'RD-2': fx_RD_2, 'RD-3': pen_mark(blade_icon), 'RD-4': pen_mark(hammer_icon), 'RD-5': fx_RD_5,
	'SM-1': fx_SM_1}
ELEM_COL = {'ไฟ': FIRE[1], 'น้ำแข็ง': ICE[1], 'แสง': (255, 244, 180), 'มืด': DARK[3]}
SCHOOL_COL = {'WH': (255, 244, 180), 'BK': (200, 200, 255), 'RD': (255, 120, 110), 'SM': FIRE[1]}

def frames(sp, school, pose):
	col = ELEM_COL.get(sp['element'], SCHOOL_COL[school]); rnd = random.Random(sp['id']); out = []
	for t, gi in enumerate(GRIP_OF):
		im, hand = rion(pose, gi, col if 1 <= t <= 4 else None)
		fx = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(fx)
		if t in (1, 2): charge(d, hand, t, col, rnd)
		elif t >= 3: FX[sp['id']](d, t - 3, hand, rnd)
		im.alpha_composite(fx); out.append(im)
	return out

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, '.gdignore'), 'w').close()
	data = json.load(open(os.path.join(ROOT, 'docs/art-bible/spells/spells_full.json'), encoding='utf-8')); n = 0
	for s in data['schools']:
		for sp in s['spells']:
			for i, im in enumerate(frames(sp, s['school_id'], s['pose'])): im.save(os.path.join(OUT, '%s_%d.png' % (sp['id'], i)))
			n += 1
	print('ok', n)
