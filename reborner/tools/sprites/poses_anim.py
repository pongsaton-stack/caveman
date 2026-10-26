# tools/sprites/poses_anim.py — เครื่องมือพิกเซลสำหรับอิริยาบถ Rion/หมา (ตัด/เลื่อน/ยุบแถว · เอน · อีโมต · ของในมือ)
# ท่าทั้งหมดย้ายไป poses64.py แล้ว (ทุกคลิป 64 เฟรม) · ไฟล์นี้เหลือแค่ตัวช่วยที่ poses64 / npc_sprites ใช้ร่วม
# ผืนภาพ: Rion 64x76 (เผื่อหัว 12px ให้กระโดด/อีโมต) · หมา 48x48 (ตัว 34px วางกลางล่าง)
import os
from PIL import Image, ImageDraw
import rion_grips as G

ROOT = G.ROOT
R = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/')
D = os.path.join(ROOT, 'assets/sprites/dog_lastlight_draft/')
OUTL = G.OUTL
HIP, TOP = 54, 12                 # Rion: แถวเริ่มขา · ที่ว่างเหนือหัว
DHIP, DOX, DOY = 28, 7, 14        # หมา: แถวเริ่มขา · ตำแหน่งวางบนผืน 48x48
DIRS = [('south', 'หน้า'), ('west', 'ซ้าย'), ('north', 'หลัง'), ('east', 'ขวา')]

def ld(path): return Image.open(path).convert('RGBA')
def rion(n): return ld(R + n + '.png')
def dog(n): return ld(D + n + '.png')
def blank(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def part(im, fn):
	out = blank(*im.size); s = im.load(); d = out.load()
	for y in range(im.size[1]):
		for x in range(im.size[0]):
			if s[x, y][3] and fn(x, y): d[x, y] = s[x, y]
	return out

def put(dst, src, dx=0, dy=0, alpha=None):
	if alpha is not None:
		src = src.copy(); src.putalpha(src.getchannel('A').point(lambda a: int(a * alpha)))
	layer = blank(*dst.size); layer.paste(src, (dx, dy), src); dst.alpha_composite(layer); return dst

def squash(im, cut0, n):
	"""ตัดแถว cut0..cut0+n-1 ทิ้ง แถวเหนือขึ้นไปเลื่อนลง n (ย่อเข่า/นั่ง/หมอบ)"""
	out = blank(*im.size); s = im.load(); d = out.load()
	for y in range(im.size[1]):
		if cut0 <= y < cut0 + n: continue
		ny = y + n if y < cut0 else y
		for x in range(im.size[0]):
			if s[x, y][3] and ny < im.size[1]: d[x, ny] = s[x, y]
	return out

def lean(im, k, y0, top):
	"""เอนช่วงบน: แถวเหนือ y0 เลื่อน dx = k*(y0-y)/(y0-top)"""
	out = blank(*im.size); s = im.load(); d = out.load()
	for y in range(im.size[1]):
		dx = 0 if y >= y0 else round(k * (y0 - y) / (y0 - top))
		for x in range(im.size[0]):
			if s[x, y][3] and 0 <= x + dx < im.size[0]: d[x + dx, y] = s[x, y]
	return out

def shift_part(im, fn, dx, dy, keep=False):
	"""ย้ายเฉพาะพิกเซลที่ fn จริง (หัว/หาง) ทับบนส่วนที่เหลือ · keep = ทิ้งของเดิมไว้ใต้ (กันรอยแยกที่คอเวลาเงยขึ้น)"""
	rest = im.copy() if keep else part(im, lambda x, y: not fn(x, y)); p = part(im, fn)
	return put(rest, p, dx, dy)

def breathe(im, y_cut, k=1):
	"""หายใจ: ช่วงบน (หัว+ไหล่) ลง k px ส่วนล่างอยู่ที่เดิม"""
	return shift_part(im, lambda x, y: y < y_cut, 0, k)

# ── อีโมต (พิกเซลกราฟิก + ขอบเข้ม) ──
GLYPH = {
	'!': (['XX', 'XX', 'XX', 'XX', '  ', 'XX'], (255, 220, 80)),
	'?': ([' XXX ', 'XX  XX'[:5], '   XX', '  XX ', '     ', '  XX '], (250, 250, 250)),
	'note': (['  XXX', '  X X', '  X  ', 'XXX  ', 'XXX  '], (130, 220, 255)),
	'heart': ([' X X ', 'XXXXX', 'XXXXX', ' XXX ', '  X  '], (240, 90, 120)),
	'z': (['XXXX', '  X ', ' X  ', 'XXXX'], (220, 230, 255)),
	'dots': (['X X X'], (250, 250, 250)),
	'anger': (['X  X', ' XX ', ' XX ', 'X  X'], (230, 50, 50)),
	'sweat': ([' X ', ' X ', 'XXX', 'XXX', ' X '], (140, 200, 255)),
	'spark': ([' X ', 'XXX', ' X '], (255, 244, 180)),
	'drop': (['X', 'X'], (140, 200, 255)),
}
def glyph(im, name, x, y, alpha=255):
	rows, col = GLYPH[name]
	on = {(x + i, y + j) for j, r in enumerate(rows) for i, c in enumerate(r) if c == 'X'}
	p = im.load(); W, H = im.size
	for (a, b) in on:
		for ox in (-1, 0, 1):
			for oy in (-1, 0, 1):
				q = (a + ox, b + oy)
				if q not in on and 0 <= q[0] < W and 0 <= q[1] < H and p[q][3] == 0: p[q] = OUTL + (alpha,)
	for q in on:
		if 0 <= q[0] < W and 0 <= q[1] < H: p[q] = col + (alpha,)
	return im

def shadow(im, cx, y, rx):
	d = ImageDraw.Draw(im); d.ellipse([cx - rx, y - 1, cx + rx, y + 1], fill=(0, 0, 0, 70)); return im

# ── Rion ──
def rc(src, dx=0, dy=0, shadow_rx=None):
	"""วางเฟรม 64x64 ลงผืน 64x76 · dy ลบ = ลอยขึ้น"""
	c = blank(64, 64 + TOP)
	if shadow_rx: shadow(c, 32, 62 + TOP, shadow_rx)
	return put(c, src, dx, TOP + dy)

def arm_pose(base, front, back=None, dx=0):
	"""ลบแขนหน้าเดิม (ท่าหันซ้าย) แล้ววาดแขนใหม่: front/back = (ศอก, มือ)"""
	im = G.shift(G.remove_front_arm(base.copy()), dx)
	if back: G.draw_arm(im, (G.SH_B[0] + dx, G.SH_B[1]), back[0], back[1], back=True)
	G.draw_arm(im, (G.SH_F[0] + dx, G.SH_F[1]), front[0], front[1])
	return im

def item(im, x, y):
	"""ขวดยาเล็กในมือ (ของที่เก็บได้)"""
	d = ImageDraw.Draw(im)
	d.rectangle([x - 2, y - 5, x + 2, y + 1], fill=OUTL + (255,)); d.rectangle([x - 1, y - 4, x + 1, y], fill=(110, 200, 140, 255))
	d.point([(x - 1, y - 4)], fill=(230, 255, 230, 255)); d.rectangle([x - 1, y - 7, x + 1, y - 6], fill=(150, 110, 80, 255))
	return im

def crate(im, x):
	d = ImageDraw.Draw(im); y0 = 46 + TOP
	d.rectangle([x, y0, x + 13, 62 + TOP], fill=OUTL + (255,)); d.rectangle([x + 1, y0 + 1, x + 12, 61 + TOP], fill=(150, 104, 62, 255))
	d.line([(x + 1, y0 + 1), (x + 12, 61 + TOP)], fill=(110, 74, 44, 255)); d.line([(x + 1, y0 + 8), (x + 12, y0 + 8)], fill=(110, 74, 44, 255))
	return im

# ── หมา ──
def dc(src, dx=0, dy=0, shadow_rx=None):
	c = blank(48, 48)
	if shadow_rx: shadow(c, 24, 46, shadow_rx)
	return put(c, src, DOX + dx, DOY + dy)

def dedupe(frames):
	"""เฟรมที่ปัดเป็นพิกเซลเต็มแล้วซ้ำกัน → เก็บภาพไม่ซ้ำ + ลำดับ"""
	uniq, order, seen = [], [], {}
	for f in frames:
		k = f.tobytes()
		if k not in seen: seen[k] = len(uniq); uniq.append(f)
		order.append(seen[k])
	return uniq, order

