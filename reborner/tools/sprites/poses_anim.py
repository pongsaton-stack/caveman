# tools/sprites/poses_anim.py — อิริยาบถของ Rion และหมาคู่หู (ร่าง · ยังไม่เข้าเกม · kwan สั่ง "ครอบคลุมที่สุด")
# ทำจากภาพยืน/เดินเดิมด้วยโค้ด (ตัด/เลื่อน/ยุบแถวพิกเซล + วาดแขนใหม่จาก rion_grips) — ไม่วาดตัวใหม่ ไม่เปลี่ยนพาเลตต์ตัวละคร
# ผืนภาพ: Rion 64x76 (เผื่อหัว 12px ให้กระโดด/อีโมต) · หมา 48x48 (ตัว 34px วางกลางล่าง)
# ผล: assets/sprites/poses_draft/<who>_<pose>_<i>.png + index.json (ลำดับเฟรม · จังหวะ · กลุ่ม · ป้ายไทย)
import json, math, os
from PIL import Image, ImageDraw
import rion_grips as G

ROOT = G.ROOT
R = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/')
D = os.path.join(ROOT, 'assets/sprites/dog_lastlight_draft/')
OUT = os.path.join(ROOT, 'assets/sprites/poses_draft')
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

def rion_poses():
	P = {}
	S, W, N, E = rion('south'), rion('west'), rion('north'), rion('east')
	base = {'south': S, 'west': W, 'north': N, 'east': E}
	walk = {d: [rion('%s_w%d' % (d, i)) for i in range(4)] for d, _ in DIRS}
	# ยืน/หายใจ 4 ทิศ
	for d, th in DIRS:
		P['idle_' + d] = ('ยืน · หายใจ', 'ยืนหายใจ ' + th, [rc(base[d]), rc(breathe(base[d], 40))], [0, 0, 1, 1], 0.4)
	# วิ่ง 4 ทิศ (ก้าวเดิน + ตัวเด้ง + เอนไปทางที่วิ่ง)
	for d, th in DIRS:
		k = {'west': -2, 'east': 2}.get(d, 0)
		fr = [rc(lean(walk[d][i], k, HIP, 8), 0, -1 if i == 2 else 0) for i in (1, 2, 3)]
		P['run_' + d] = ('เคลื่อนที่', 'วิ่ง' + th, fr, [0, 1, 2, 1], 0.09)
	# หมุนตัว · มองซ้ายขวา
	P['spin'] = ('เคลื่อนที่', 'หมุนตัวรอบ', [rc(base[d]) for d, _ in DIRS], [0, 1, 2, 3], 0.12)
	P['look'] = ('ท่าทาง', 'มองซ้าย-ขวา', [rc(S), rc(W), rc(E)], [0, 0, 1, 1, 0, 0, 2, 2], 0.3)
	# กระโดด (หน้า/ซ้าย): ย่อ → ลอย → สูงสุด → ลง → ย่อรับ
	for d, th in (('south', 'หน้า'), ('west', 'ซ้าย')):
		b = base[d]; cr = squash(b, 57, 2)
		P['jump_' + d] = ('เคลื่อนที่', 'กระโดด' + th, [rc(cr, 0, 0, 9), rc(b, 0, -6, 7), rc(b, 0, -10, 5), rc(b, 0, -5, 7), rc(cr, 0, 0, 9), rc(b, 0, 0, 9)],
			[5, 0, 1, 2, 2, 3, 4, 5], 0.1)
	# นั่ง (หน้า): ยุบขา + แยกเท้า · นั่งพักหายใจ
	sit = squash(S, 56, 5); feet = lambda x, y: y >= 59
	sit = put(put(part(sit, lambda x, y: not feet(x, y)), part(sit, lambda x, y: feet(x, y) and x < 32), -2, 0), part(sit, lambda x, y: feet(x, y) and x >= 32), 2, 0)
	P['sit'] = ('ท่าทาง', 'นั่งยอง (หน้า)', [rc(sit), rc(breathe(sit, 45))], [0, 0, 1, 1], 0.45)
	# คุกเข่า (ซ้าย) — ใช้ท่าทรุดของท่าล้มเดิม
	kneel = rion('west_k0')
	P['kneel'] = ('ท่าทาง', 'คุกเข่า (ซ้าย)', [rc(kneel), rc(breathe(kneel, 44))], [0, 0, 1, 1], 0.45)
	# นอนหลับ: นอนหงาย + Zzz ลอย
	lie = rion('west_k1'); sl = []
	for i in range(4):
		f = rc(breathe(lie, 52) if i % 2 else lie); glyph(f, 'z', 44 + i, TOP + 30 - 4 * i, 255 - 40 * i)
		if i >= 2: glyph(f, 'z', 50, TOP + 34 - 4 * (i - 2), 200)
		sl.append(f)
	P['sleep'] = ('ท่าทาง', 'นอนหลับ', sl, [0, 1, 2, 3], 0.4)
	# โบกมือ (ซ้าย)
	wv = [arm_pose(W, ((21, 35), (16, 30))), arm_pose(W, ((21, 35), (19, 28))), arm_pose(W, ((24, 44), (23, 47)))]
	P['wave'] = ('ท่าทาง', 'โบกมือทักทาย', [rc(f) for f in wv], [2, 0, 1, 0, 1, 0, 2], 0.16)
	# เก็บของ: ย่อ → เอื้อมมือลงพื้น → ลุกชูของ + ประกาย
	reach = arm_pose(squash(W, 56, 4), ((20, 50), (15, 56)))
	hold = item(arm_pose(W, ((21, 35), (16, 31))), 16, 30)
	h2 = hold.copy(); glyph(h2, 'spark', 9, 20); glyph(h2, 'spark', 21, 18)
	P['pickup'] = ('ท่าทาง', 'ก้มเก็บของ → ชูขึ้น', [rc(W), rc(squash(W, 56, 4)), rc(reach), rc(hold), rc(h2)], [0, 1, 2, 2, 1, 3, 4, 3, 4], 0.16)
	# ผลักลัง: เอนไปหน้า สองแขนดัน ขาก้าวช้า
	ps = []
	for i, w in enumerate((1, 2, 3, 2)):
		f = arm_pose(lean(walk['west'][w], -3, HIP, 8), ((19, 42), (14, 42)), ((22, 44), (15, 45)))
		c = crate(blank(64, 64 + TOP), 0 - i); ps.append(put(c, f, 0, TOP))
	P['push'] = ('ท่าทาง', 'ผลักลัง', ps, [0, 1, 2, 3], 0.22)
	# พยักหน้า · ส่ายหน้า (หน้า)
	head = lambda x, y: y < 31
	P['nod'] = ('ท่าทาง', 'พยักหน้า', [rc(S), rc(shift_part(S, head, 0, 1)), rc(shift_part(S, head, 0, 2))], [0, 1, 2, 1, 0, 1, 2, 1, 0, 0], 0.1)
	P['shake'] = ('ท่าทาง', 'ส่ายหน้า', [rc(S), rc(shift_part(S, head, -1, 0)), rc(shift_part(S, head, 1, 0))], [0, 1, 0, 2, 0, 1, 0, 2, 0, 0], 0.1)
	# อารมณ์ (หน้า): อีโมตเด้งเหนือหัว
	def emote(name, gl, body=None, hop=False, gx=45):
		b = body or S; fr = []
		for i in range(4):
			f = rc(b, 0, -2 if hop and i == 1 else 0)
			if i: glyph(f, gl, gx, (TOP - 9 if i == 1 else TOP - 7) + (1 if i == 3 else 0))
			fr.append(f)
		return fr
	P['emo_surprise'] = ('อารมณ์', '! ตกใจ', emote('!', '!', hop=True, gx=47), [0, 1, 2, 2, 3, 2, 3], 0.15)
	P['emo_question'] = ('อารมณ์', '? สงสัย', emote('?', '?', shift_part(S, head, 1, 0)), [0, 1, 2, 2, 3, 2, 3], 0.18)
	P['emo_happy'] = ('อารมณ์', '♪ ดีใจ', emote('n', 'note', hop=True), [0, 1, 2, 3, 2, 1, 2, 3], 0.15)
	P['emo_love'] = ('อารมณ์', '♥ ชอบ', emote('h', 'heart'), [0, 1, 2, 3, 2, 3], 0.2)
	P['emo_angry'] = ('อารมณ์', 'โกรธ', emote('a', 'anger', shift_part(S, head, 0, 1), gx=43), [0, 1, 2, 3, 2, 3], 0.12)
	P['emo_sweat'] = ('อารมณ์', 'เหงื่อตก (ลำบากใจ)', emote('s', 'sweat', shift_part(S, head, 0, 1), gx=44), [0, 1, 2, 3, 3, 3], 0.2)
	P['emo_think'] = ('อารมณ์', '... คิด', emote('d', 'dots', gx=42), [0, 1, 2, 3, 2, 3], 0.3)
	P['emo_sleepy'] = ('อารมณ์', 'ง่วง', emote('z', 'z', shift_part(S, head, 0, 2), gx=44), [0, 1, 2, 3, 2, 3], 0.35)
	# ── ในศึก (หันซ้าย) ──
	ready = squash(W, 57, 1)
	P['b_ready'] = ('ในศึก', 'ตั้งท่ารอ (หายใจ)', [rc(ready), rc(breathe(ready, 42))], [0, 0, 1, 1], 0.3)
	guard = squash(arm_pose(W, ((24, 44), (22, 40)), ((28, 44), (24, 41))), 57, 2)
	g2 = guard.copy(); glyph(g2, 'spark', 16, 36)
	P['b_guard'] = ('ในศึก', 'ป้องกัน', [rc(W), rc(guard), rc(g2)], [0, 1, 2, 1, 1, 1], 0.14)
	dodge = lean(W, 5, HIP, 8)
	d1 = rc(W); put(d1, W, 0, TOP, 0); d2 = rc(dodge, 6); put(d2, W, 0, TOP, 0.35); d3 = rc(dodge, 7); d4 = rc(lean(W, 2, HIP, 8), 3)
	P['b_dodge'] = ('ในศึก', 'หลบ (ถอยหลบ + ภาพติดตา)', [d1, d2, d3, d4], [0, 1, 2, 2, 3, 0], 0.1)
	use = [rc(arm_pose(W, ((24, 44), (23, 47)))), rc(item(arm_pose(W, ((22, 40), (18, 37))), 18, 36)), rc(item(arm_pose(W, ((21, 35), (16, 31))), 16, 30))]
	u2 = use[2].copy(); glyph(u2, 'spark', 10, TOP + 20); glyph(u2, 'spark', 22, TOP + 14); glyph(u2, 'spark', 30, TOP + 28)
	P['b_item'] = ('ในศึก', 'ใช้ไอเท็ม', use + [u2], [0, 1, 2, 3, 2, 3, 0], 0.14)
	fist = arm_pose(W, ((22, 33), (19, 27)))
	v1 = rc(fist, 0, -3, 7); glyph(v1, 'spark', 14, TOP + 12); v2 = rc(fist, 0, 0, 9); glyph(v2, 'spark', 12, TOP + 16); glyph(v2, 'spark', 24, TOP + 6)
	P['b_victory'] = ('ในศึก', 'ชนะ (ชูหมัด)', [rc(W, 0, 0, 9), rc(squash(W, 57, 2), 0, 0, 9), v1, v2], [0, 1, 2, 3, 3, 3, 3, 1], 0.14)
	low = squash(lean(W, -2, HIP, 8), 57, 2)
	l1 = rc(low); glyph(l1, 'sweat', 36, TOP + 6); l2 = rc(breathe(low, 44)); glyph(l2, 'sweat', 36, TOP + 7)
	P['b_lowhp'] = ('ในศึก', 'HP ต่ำ (หอบ)', [l1, l2], [0, 1], 0.22)
	rv = [rc(rion('west_k1')), rc(kneel), rc(squash(W, 56, 3)), rc(W)]
	r2 = rv[3].copy(); glyph(r2, 'spark', 14, TOP + 8); glyph(r2, 'spark', 44, TOP + 14)
	P['b_revive'] = ('ในศึก', 'ฟื้นจากล้ม', rv + [r2], [0, 0, 1, 2, 4, 3, 3], 0.18)
	cheer = [rc(W), rc(arm_pose(W, ((22, 33), (19, 27))), 0, -2, 7)]
	P['b_cheer'] = ('ในศึก', 'เชียร์เพื่อน (ชูมือกระโดดเบา)', cheer, [0, 1, 0, 1], 0.16)
	return P

# ── หมา ──
def dc(src, dx=0, dy=0, shadow_rx=None):
	c = blank(48, 48)
	if shadow_rx: shadow(c, 24, 46, shadow_rx)
	return put(c, src, DOX + dx, DOY + dy)

def dog_poses():
	P = {}
	S, W, N, E = dog('south'), dog('west'), dog('north'), dog('east')
	base = {'south': S, 'west': W, 'north': N, 'east': E}
	walk = {d: [dog('%s_w%d' % (d, i)) for i in range(4)] for d, _ in DIRS}
	head_w = lambda x, y: x < 19 and y < 27           # หัว+อก (หันซ้าย)
	tail_w = lambda x, y: x >= 26 and y < 22          # หาง (หันซ้าย)
	tail_e = lambda x, y: x <= 7 and y < 22           # หาง (หันขวา)
	for d, th in DIRS:
		P['idle_' + d] = ('ยืน · หายใจ', 'ยืนหายใจ ' + th, [dc(base[d]), dc(breathe(base[d], 18))], [0, 0, 1, 1], 0.4)
	P['wag_west'] = ('ยืน · หายใจ', 'กระดิกหาง (ซ้าย)', [dc(W), dc(shift_part(W, tail_w, 1, -1)), dc(shift_part(W, tail_w, -1, 1))], [0, 1, 0, 2], 0.1)
	P['wag_east'] = ('ยืน · หายใจ', 'กระดิกหาง (ขวา)', [dc(E), dc(shift_part(E, tail_e, -1, -1)), dc(shift_part(E, tail_e, 1, 1))], [0, 1, 0, 2], 0.1)
	P['wag_north'] = ('ยืน · หายใจ', 'กระดิกหาง (หลัง)', [dc(N), dc(shift_part(N, lambda x, y: y < 14, -1, 0)), dc(shift_part(N, lambda x, y: y < 14, 1, 0))], [0, 1, 0, 2], 0.1)
	for d, th in DIRS:
		fr = [dc(walk[d][i], 0, -1 if i == 2 else 0) for i in (1, 2, 3)]
		P['run_' + d] = ('เคลื่อนที่', 'วิ่ง' + th, fr, [0, 1, 2, 1], 0.08)
	P['spin'] = ('เคลื่อนที่', 'หมุนวนดีใจ', [dc(base[d]) for d, _ in DIRS], [0, 1, 2, 3], 0.09)
	cr = squash(W, 29, 1)
	P['hop'] = ('เคลื่อนที่', 'กระโดด (ซ้าย)', [dc(cr, 0, 0, 8), dc(W, 0, -4, 6), dc(W, 0, -7, 4), dc(W, 0, -3, 6), dc(cr, 0, 0, 8), dc(W, 0, 0, 8)], [5, 0, 1, 2, 3, 4, 5], 0.09)
	# นั่ง: ก้นลง 3px (ส่วนหลัง x>=19 ยุบแถว) · หน้าเงยเล็กน้อย
	rear = lambda x, y: x >= 19
	sit = put(part(W, lambda x, y: not rear(x, y)), squash(part(W, rear), 24, 3))
	sit = shift_part(sit, head_w, 0, -1, keep=True)
	P['sit'] = ('ท่าทาง', 'นั่ง (ซ้าย)', [dc(sit), dc(shift_part(sit, tail_w, 0, 2)), dc(shift_part(sit, tail_w, 1, 1))], [0, 0, 1, 2, 1, 2], 0.2)
	# หมอบ/นอน: ยุบขาทั้งตัว · หลับมี Zzz
	lie = squash(W, 27, 4)
	P['lie'] = ('ท่าทาง', 'หมอบ (ซ้าย)', [dc(lie), dc(breathe(lie, 22))], [0, 0, 1, 1], 0.4)
	zz = []
	for i in range(4):
		f = dc(breathe(lie, 22) if i % 2 else lie); glyph(f, 'z', 16 + i, 16 - 3 * i, 255 - 40 * i); zz.append(f)
	P['sleep'] = ('ท่าทาง', 'นอนหลับ', zz, [0, 1, 2, 3], 0.4)
	# เห่า: หัวยื่นเงย + เส้นเสียง
	bk = dc(shift_part(W, head_w, -1, -1, keep=True)); d = ImageDraw.Draw(bk)
	for i, (x, y) in enumerate(((3, 28), (2, 32), (3, 36))): d.line([(x, y), (x - 3, y + (i - 1) * 2)], fill=(250, 250, 250, 255))
	P['bark'] = ('ท่าทาง', 'เห่า', [dc(W), bk], [0, 1, 0, 1, 0, 0], 0.12)
	# ดมพื้น: หัวก้ม 3-4px สลับ
	P['sniff'] = ('ท่าทาง', 'ก้มดมพื้น', [dc(shift_part(W, head_w, 0, 3)), dc(shift_part(W, head_w, -1, 4))], [0, 1, 0, 1, 0, 0, 1], 0.12)
	# ก้มชวนเล่น: ช่วงหน้าต่ำ ก้นโด่ง หางกระดิก
	front = lambda x, y: x < 19
	bow = put(part(W, lambda x, y: not front(x, y)), squash(part(W, front), 25, 3))
	P['playbow'] = ('ท่าทาง', 'ก้มชวนเล่น', [dc(bow), dc(shift_part(bow, tail_w, 1, -1)), dc(shift_part(bow, tail_w, -1, 1))], [0, 1, 2, 1, 2, 0], 0.12)
	# สะบัดตัว (หน้า) + หยดน้ำ
	sh = []
	for i, dx in enumerate((-1, 1, -1, 1)):
		f = dc(S, dx); glyph(f, 'drop', 6 + 2 * i, 18 - i); glyph(f, 'drop', 40 - 2 * i, 20 + i); sh.append(f)
	P['shake'] = ('ท่าทาง', 'สะบัดตัว', sh, [0, 1, 2, 3, 0, 1], 0.07)
	P['look'] = ('ท่าทาง', 'หันซ้าย-ขวา', [dc(S), dc(W), dc(E)], [0, 0, 1, 1, 0, 0, 2, 2], 0.3)
	def emote(gl, hop=False, gx=30):
		fr = []
		for i in range(4):
			f = dc(S, 0, -2 if hop and i == 1 else 0)
			if i: glyph(f, gl, gx, (3 if i == 1 else 5) + (1 if i == 3 else 0))
			fr.append(f)
		return fr
	P['emo_surprise'] = ('อารมณ์', '! ตกใจ', emote('!', True, 32), [0, 1, 2, 2, 3, 2, 3], 0.15)
	P['emo_question'] = ('อารมณ์', '? สงสัย (เอียงหัว)', [dc(S)] + [glyph(dc(shift_part(S, lambda x, y: y < 18, 1, 0)), '?', 30, 4 + (i == 2)) for i in range(3)], [0, 1, 2, 3, 2, 3], 0.18)
	P['emo_happy'] = ('อารมณ์', '♪ ดีใจ', emote('note', True), [0, 1, 2, 3, 2, 1, 2, 3], 0.15)
	P['emo_love'] = ('อารมณ์', '♥ รัก', emote('heart'), [0, 1, 2, 3, 2, 3], 0.2)
	return P


# ── เทียบจำนวนเฟรม (kwan ถาม "กี่เฟรมถึงสมูท") — เดิน 8 เฟรม · หายใจ 4 เฟรม ทำแบบเดียวกับชุดเดิม (rion_anim) แต่แบ่งช่วงละเอียดขึ้น ──
import rion_anim as RA
def walkN_side(src_dir, n_name, N, facing_left=True, split=30, hip=HIP, foot=63, kmax=4):
	"""ข้าง N เฟรม: ระยะก้าว k = kmax·cos(2πt) · ตัวขึ้นลง = sin(4πt) · ปัดเป็นพิกเซลเต็ม"""
	im = RA.load(n_name, src_dir)
	upper = RA.region(im, lambda x, y: y < hip)
	front = RA.region(im, lambda x, y: y >= hip and (x < split if facing_left else x >= split))
	back = RA.region(im, lambda x, y: y >= hip and (x >= split if facing_left else x < split))
	sg = -1 if facing_left else 1; out = []
	for i in range(N):
		t = i / N; k = round(kmax * math.cos(2 * math.pi * t)); b = round(math.sin(4 * math.pi * t))
		f = RA.blank()
		RA.paste(f, RA.shear(back, -sg * k, hip, foot), 0, -1 if 0.18 < t < 0.32 else 0)
		RA.paste(f, RA.shear(front, sg * k, hip, foot), 0, -1 if 0.68 < t < 0.82 else 0)
		if b > 0: RA.paste(f, RA.region(upper, lambda x, y: y >= hip - 1)); RA.paste(f, upper, 0, 1)
		elif b < 0: RA.bob(f, upper, hip)
		else: RA.paste(f, upper)
		out.append(f)
	return out

def walkN_front(src_dir, n_name, N, split, hip=HIP, cut0=57, foot_end=61):
	"""หน้า/หลัง N เฟรม: งอเข่า = round(2·|sin 2πt|) ซ้ายครึ่งรอบแรก ขวาครึ่งหลัง"""
	im = RA.load(n_name, src_dir)
	upper = RA.region(im, lambda x, y: y < hip)
	L = RA.region(im, lambda x, y: y >= hip and x < split); Rr = RA.region(im, lambda x, y: y >= hip and x >= split)
	out = []
	for i in range(N):
		sv = math.sin(2 * math.pi * i / N); dpt = round(2 * abs(sv))
		f = RA.blank(); RA.paste(f, upper)
		RA.paste(f, RA.bend(L, cut0, cut0 + dpt, foot_end) if sv > 0 and dpt else L)
		RA.paste(f, RA.bend(Rr, cut0, cut0 + dpt, foot_end) if sv < 0 and dpt else Rr)
		out.append(f)
	return out

def idleN(im, head_cut, chest_cut, N):
	"""หายใจ N เฟรม: อกลง 0-1px ตามโคไซน์ · หัวตามช้ากว่า 1/8 รอบ ลงได้ถึง 2px"""
	out = []
	for i in range(N):
		t = i / N; chest = round(0.5 - 0.5 * math.cos(2 * math.pi * t)); head = max(chest, round(1 - math.cos(2 * math.pi * (t - 0.125))))
		f = shift_part(im, lambda x, y: y < chest_cut, 0, chest) if chest else im
		if head > chest: f = shift_part(f, lambda x, y: y < head_cut + chest, 0, head - chest)
		out.append(f)
	return out

def dedupe(frames):
	"""32 เฟรมที่ปัดเป็นพิกเซลเต็มซ้ำกันเยอะ → เก็บภาพไม่ซ้ำ + ลำดับ"""
	uniq, order, seen = [], [], {}
	for f in frames:
		k = f.tobytes()
		if k not in seen: seen[k] = len(uniq); uniq.append(f)
		order.append(seen[k])
	return uniq, order

COMPARE_N = (32, 64)   # kwan สั่ง 5 ต.ค.: เลิกเทียบ 4/8 เฟรม → เทียบ 32 กับ 64

def compare_poses():
	"""เทียบจำนวนเฟรม: แต่ละท่าทำ 32 และ 64 เฟรมจากสูตรเดียวกัน เล่นพร้อมกัน รอบเท่ากัน"""
	P = {}
	for d, th, fl, sp in (('west', 'ซ้าย', True, 30), ('east', 'ขวา', False, 34)):
		P['walkN_' + d] = ('เทียบจำนวนเฟรม', 'Rion เดิน' + th, 'walk', {n: [rc(f) for f in walkN_side(R, d, n, fl, sp)] for n in COMPARE_N})
	for d, th, sp in (('south', 'หน้า', 32), ('north', 'หลัง', 31)):
		P['walkN_' + d] = ('เทียบจำนวนเฟรม', 'Rion เดิน' + th, 'walk', {n: [rc(f) for f in walkN_front(R, d, n, sp)] for n in COMPARE_N})
	for d in ('south', 'west'):
		b = rion(d); P['idleN_' + d] = ('เทียบจำนวนเฟรม', 'Rion หายใจ ' + dict(DIRS)[d], 'idle', {n: [rc(f) for f in idleN(b, 31, 46, n)] for n in COMPARE_N})
	return P

def dog_compare():
	P = {}
	for d, th, fl in (('west', 'ซ้าย', True), ('east', 'ขวา', False)):
		P['walkN_' + d] = ('เทียบจำนวนเฟรม', 'หมาเดิน' + th, 'walk', {n: [dc(f) for f in walkN_side(D, d, n, fl, 17, DHIP, 32, 2)] for n in COMPARE_N})
	b = dog('west'); P['idleN_west'] = ('เทียบจำนวนเฟรม', 'หมาหายใจ ซ้าย', 'idle', {n: [dc(f) for f in idleN(b, 18, 24, n)] for n in COMPARE_N})
	return P

def save_compare(who, P, index):
	"""เก็บเฉพาะภาพไม่ซ้ำของแต่ละชุด: <id>_s<n>_<i>.png + ลำดับเล่น"""
	for pid, (group, label, timing, sets) in P.items():
		row = {'id': '%s_%s' % (who, pid), 'who': who, 'group': group, 'label': label + ' ' + ' / '.join(map(str, sets)) + ' เฟรม', 'timing': timing, 'sets': []}
		for n, frames in sets.items():
			uniq, order = dedupe(frames)
			for i, im in enumerate(uniq): im.save(os.path.join(OUT, '%s_%s_s%d_%d.png' % (who, pid, n, i)))
			row['sets'].append({'n': n, 'unique': len(uniq), 'order': order})
		row['n'] = max(sets); row['order'] = row['sets'][-1]['order']
		index.append(row)

def save(who, P, index):
	for pid, val in P.items():
		group, label, frames, order, sec = val[:5]
		for i, im in enumerate(frames): im.save(os.path.join(OUT, '%s_%s_%d.png' % (who, pid, i)))
		row = {'id': '%s_%s' % (who, pid), 'who': who, 'group': group, 'label': label, 'n': len(frames), 'order': order}
		row['sec'] = sec
		index.append(row)

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, '.gdignore'), 'w').close()
	for f in os.listdir(OUT):
		if f.endswith('.png'): os.remove(os.path.join(OUT, f))
	index = []
	save('rion', rion_poses(), index); save_compare('rion', compare_poses(), index); save('dog', dog_poses(), index); save_compare('dog', dog_compare(), index)
	json.dump({'_doc': 'อิริยาบถร่าง (tools/sprites/poses_anim.py) · sec = วินาทีต่อเฟรม (ร่าง ปรับได้) · order = ลำดับเฟรมที่เล่น', 'poses': index},
		open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print('ok', len(index), 'poses', sum(p['n'] for p in index), 'frames')
