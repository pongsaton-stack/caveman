# tools/sprites/monsters_ll.py — มอนสไตล์ Last Light ตามสเปก docs/art-bible/monster_visual_master.json
# แนวที่ kwan สั่ง (3 ต.ค. 2026): "ให้เหมือนต้นแบบที่สุด ขัด bible ได้ คิดนอกกรอบได้"
#   → ตัดจากชีต lastlight_01.png โดยตรง (แบบเดียวกับ Rion/หมา) แล้วเก็บงาน/ลงสี — ไม่วาดจากรูปทรงเรขาคณิตอีก
#   M01 สไลม์เถ้า : ตัดสไลม์ในชีต (48x38 พอดีช่อง S) · 2 แบบ: green = สีต้นแบบ · ash = ลงสีเถ้า คงตา/ปาก/ประกาย
#   M15 หมาป่าคู่ : ชีตไม่มีหมาป่า → ใช้หมาคู่หู (dog_lastlight_draft) ลงสีเทาน้ำตาล วางสองตัว ตัวหลังหูพับ
#   M03/M06 + COMP-M03/COMP-M06 (อนุมัติแล้ว): หนอน = สไลม์ย่อลงสีอุ่น + หินมอสจากชีต · ค้างคาว = หัวหมามุมหน้า + ปีกวาดใหม่
# ศัตรูอยู่ซ้ายของจอสู้ → หันขวา · ไม่ใช้เครดิต PixelLab
# รัน: <python+Pillow> tools/sprites/monsters_ll.py [out_dir]
import colorsys, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ll_cut import cut, place
from ll_polish import hue_outline

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOG = os.path.join(ROOT, 'assets/sprites/dog_lastlight_draft/')

def h2c(h):
	return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def hsv(c):
	return colorsys.rgb_to_hsv(*(u / 255 for u in c[:3]))

# ── M01 สไลม์เถ้า ─────────────────────────────────────────────
ASH = [h2c(h) for h in ('3A3835', '56534E', '73706A', '918D84', 'AEAA9F', 'CAC6BA', 'E6E2D6')]
ASH_SPECKS = ((10, 17), (11, 17), (31, 9), (36, 22), (37, 22), (14, 28), (30, 27), (22, 10), (8, 25), (40, 30))

def slime_parts():
	"""ตัดสไลม์จากชีต · แยกตา/ปาก/ประกายก่อนลดสี (ไม่งั้นปากแดงกับประกายตาหาย)"""
	sl = cut((490, 425, 565, 490), tol=60, shadow=False, fringe=1)
	px = sl.load(); W, H = sl.size
	kind = {}
	for y in range(H):
		for x in range(W):
			p = px[x, y]
			if p[3] < 128:
				px[x, y] = (0, 0, 0, 0); continue
			h, s, v = hsv(p)
			if (h < 0.07 or h > 0.92) and s > 0.35 and v > 0.35: kind[x, y] = 'mouth'
			elif v > 0.86 and s < 0.30: kind[x, y] = 'shine'
			elif v < 0.30: kind[x, y] = 'dark'
			else: kind[x, y] = 'body'
	m = {}
	for cls, n in (('body', 7), ('mouth', 2), ('shine', 1), ('dark', 2)):
		pts = [k for k, v in kind.items() if v == cls]
		if not pts:
			continue
		tmp = Image.new('RGB', (len(pts), 1)); tmp.putdata([px[k][:3] for k in pts])
		q = tmp.quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
		m.update(zip(pts, [q.getpixel((i, 0)) for i in range(len(pts))]))
	g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gp = g.load()
	for k, c in m.items():
		gp[k] = c + (255,)
	return hue_outline(g), kind, m

def slime_ash(g, kind, m):
	"""เนื้อตัว → ทางลาดเทาเถ้าตามความสว่าง · เส้นขอบเขียว → เทาเข้ม · จุดด่างเถ้าดำตามสเปก"""
	a = g.copy(); ap = a.load(); W, H = a.size
	body = sorted({m[k] for k in m if kind[k] == 'body'}, key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])
	rank = {c: i for i, c in enumerate(body)}
	for k, v in kind.items():
		if v == 'body' and ap[k][3] and ap[k][:3] == m[k]:
			ap[k] = ASH[min(len(ASH) - 1, rank[m[k]])] + (255,)
	for y in range(H):
		for x in range(W):
			p = ap[x, y]
			if p[3] and kind.get((x, y)) != 'mouth':
				h, s, v = hsv(p)
				if 0.15 < h < 0.6 and s > 0.15:
					L = 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
					ap[x, y] = (ASH[0] if L < 70 else ASH[1] if L < 110 else ASH[2]) + (255,)
	for x, y in ASH_SPECKS:
		if 0 <= x < W and 0 <= y < H and kind.get((x, y)) == 'body' and ap[x, y][3]:
			ap[x, y] = ASH[0] + (255,)
	return a

def squash(im):
	"""idle เฟรม 2: ยุบตัวลง 1px (ตัดแถวบนช่วงหัว) — เท้าอยู่ที่เดิม"""
	W, H = im.size; out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
	cut_row = H // 3
	out.alpha_composite(im.crop((0, cut_row + 1, W, H)), (0, cut_row + 1))
	out.alpha_composite(im.crop((0, 0, W, cut_row)), (0, 1))
	return out

# ── M15 หมาป่าคู่ ────────────────────────────────────────────
WOLF = {'2F1B10': '2A2826', '150F0D': '1C1A19', '21160F': '242220', '412C1E': '383A37', '3E2214': '4A4540',
	'4D2A17': '4A4540', '523624': '4A4540', '714022': '5A4E44', '825335': '6C5947', 'B25F3C': '7A6A58',
	'DA7B42': '8A7460', 'E39253': 'A2927B', 'E1B684': 'C4B69C', '8A7460': 'A89C88', 'D2BD9A': 'D2BD9A'}

def wolf(src, fold=False, dim=1.0):
	im = Image.open(DOG + src + '.png').convert('RGBA'); p = im.load()
	for y in range(34):
		for x in range(34):
			if p[x, y][3]:
				c = h2c(WOLF['%02X%02X%02X' % p[x, y][:3]])
				p[x, y] = tuple(int(u * dim) for u in c) + (255,)
	if fold:   # หูขวาพับ: ตัดปลายหู 2 แถว ปิดขอบบน แล้วปลายหูห้อยลงด้านนอก
		out = tuple(int(u * dim) for u in h2c('1C1A19')) + (255,)
		fur = tuple(int(u * dim) for u in h2c('7A6A58')) + (255,)
		for y in (9, 10):
			for x in range(23, 30): p[x, y] = (0, 0, 0, 0)
		for x in range(24, 29): p[x, 11] = out
		for x, y in ((29, 11), (30, 12), (30, 13)): p[x, y] = out
		for x, y in ((29, 12), (29, 13)): p[x, y] = fur
	return im

def wolf_pair(hop=0):
	cv = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
	cv.alpha_composite(wolf('east', fold=True, dim=0.86), (-1, 3 - hop))   # ตัวหลัง: เข้มกว่า = อยู่ลึก
	cv.alpha_composite(wolf('east'), (14, 14 - hop))                       # ตัวหน้า
	return cv

# ── M06 ค้างคาวเงา ───────────────────────────────────────────
# ชีตไม่มีค้างคาว → หัวกลมหูแหลมจากหมามุมหน้า (dog south แถว 2-22) ลงสีเทาเข้ม ตาอำพัน เขี้ยวเล็ก + ปีกหนังวาดใหม่
BAT = {'412C1E': '1C1A19', '2F1B10': '1C1A19', '150F0D': '141312', '21160F': '1C1A19', '714022': '2E2C2A',
	'B25F3C': '3A3735', 'DA7B42': '4A4642', 'E39253': '5C5751', 'E1B684': '5C5751', 'D2BD9A': '5C5751',
	'8A7460': '6E6860', '825335': '4A4642', '523624': '2A2826', '3E2214': '2A2826', '4D2A17': '2A2826'}
WING = [h2c(h) for h in ('3E342C', '5A4A3E', '6F5D4D')]   # เงา · กลาง · สว่าง (น้ำตาลเทา ตามสเปก)
EYE = (h2c('B37A55'), h2c('D6966A'))                      # อำพัน + ประกาย

def _poly_fill(px, pts, col, W=48):
	ys = [y for _, y in pts]
	for y in range(min(ys), max(ys) + 1):
		xs = []
		for i in range(len(pts)):
			(x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
			if (y0 <= y < y1) or (y1 <= y < y0):
				xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
		xs.sort()
		for j in range(0, len(xs) - 1, 2):
			for x in range(int(round(xs[j])), int(round(xs[j + 1])) + 1):
				if 0 <= x < W and 0 <= y < W:
					px[x, y] = col

def _line(px, a, b, col):
	(x0, y0), (x1, y1) = a, b
	n = max(abs(x1 - x0), abs(y1 - y0), 1)
	for i in range(n + 1):
		px[round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)] = col

def bat(flap=0, friend=False):
	"""ค้างคาวตัวกลม ปีกกางสมมาตร · flap = idle เฟรม 2 (ปีกยกขึ้น 3px ตัวลอยขึ้น 1px)"""
	head = Image.open(DOG + 'south.png').convert('RGBA').crop((5, 2, 31, 23))
	hp = head.load()
	for y in range(head.height):
		for x in range(head.width):
			if hp[x, y][3]:
				hp[x, y] = h2c(BAT['%02X%02X%02X' % hp[x, y][:3]]) + (255,)
	# หัวกลม: ตัดเป็นวงรี (ครอปตรง ๆ ติดลำตัวหมา → ทรงสี่เหลี่ยม) · หูเหนือแถว 7 เก็บไว้
	for y in range(head.height):
		for x in range(head.width):
			nx, ny = (x + 0.5 - 13) / 11.5, (y + 0.5 - 12.5) / 8.5
			if hp[x, y][3] and y >= 7 and nx * nx + ny * ny > 1:
				hp[x, y] = (0, 0, 0, 0)
	# ปากกระบอกเล็กสีอ่อน + จมูก (หน้าเทาเรียบทั้งหน้า — ลายขาวของหมาทำให้ดูเป็นแรคคูน)
	for y in range(16, 21):
		for x in range(9, 18):
			nx, ny = (x + 0.5 - 13.5) / 4.5, (y + 0.5 - 18.5) / 2.6
			if nx * nx + ny * ny <= 1 and hp[x, y][3]:
				hp[x, y] = h2c('8E877C') + (255,)
	for x in (12, 13, 14):
		hp[x, 17] = h2c('1C1A19') + (255,)
	# ตาวาว: วงอำพัน 3x3 รูม่านตาเข้ม ประกายมุมซ้ายบน
	for ex in (7, 16):
		for dx in (0, 1, 2):
			for dy in (11, 12, 13):
				hp[ex + dx, dy] = EYE[0] + (255,)
		hp[ex + 1, 12] = h2c('21160F') + (255,)
		hp[ex, 11] = h2c('E6E2D6') + (255,)
	# เขี้ยวคู่ใต้จมูก
	for fx in (12, 14):
		hp[fx, 20] = h2c('E6E2D6') + (255,)
	cv = Image.new('RGBA', (48, 48), (0, 0, 0, 0)); cp = cv.load()
	dy = -flap
	lift = 3 * flap
	for side in (-1, 1):
		def P(x, y, k=0):   # x วัดจากกลางตัว · k = ยกตามแรงกระพือ (ปลายปีกยกมากสุด)
			return (24 + side * x, y + dy - k)
		sh, top, tip = P(7, 24), P(10, 14, lift), P(23, 10, lift)
		scallop = [P(22, 22, lift // 2), P(18, 19, lift // 2), P(15, 26), P(11, 23), P(8, 29)]
		pts = [sh, top, tip] + scallop
		_poly_fill(cp, pts, WING[1] + (255,))
		_poly_fill(cp, [sh, top, P(14, 15, lift), P(11, 23)], WING[2] + (255,))    # แผ่นปีกใกล้ตัวรับแสง
		for f in (scallop[0], scallop[2], scallop[4]):                            # ก้านนิ้ว
			_line(cp, top, f, WING[0] + (255,))
		_line(cp, top, tip, WING[0] + (255,))
	if friend:   # COMP-M06: ปลอกคอหนังใต้คาง + จี้ทีล
		for y, c in ((17, '9A6038'), (18, '6F4B33')):
			for x in range(5, 22):
				if hp[x, y][3]:
					hp[x, y] = h2c(c) + (255,)
		for x, y, c in ((12, 19, 0), (13, 19, 0), (14, 19, 1), (12, 20, 1), (13, 20, 0), (14, 20, 1), (13, 18, 0)):
			hp[x, y] = TEAL[c] + (255,)
		hp[12, 19] = h2c('3C8A92') + (255,)
	cv.alpha_composite(head, (11, 9 + dy))
	for fx in (21, 26):                                                         # เท้าเล็กห้อย
		cp[fx, 31 + dy] = h2c('2A2826') + (255,); cp[fx, 32 + dy] = h2c('1C1A19') + (255,)
	return hue_outline(cv)

# ── M03 หนอนหิน ──────────────────────────────────────────────
# ชีตไม่มีหนอน → ปล้องตัว = สไลม์ในชีตย่อส่วน ลงสีผิวอุ่น (หัวมีหน้า ปล้องอื่นลบหน้า) · เปลือก = ก้อนหินมีมอสจาก Nature & Props
SKIN = [h2c(h) for h in ('523624', '9A6038', 'B37A55', 'D6966A', 'D4B08A', 'E8D2AE')]
STONE = [h2c(h) for h in ('21160F', '523624', '6C5947', '8A7460', 'A2927B')]
ROCK_BOX = (1215, 530, 1262, 580)

def _shrink(im, w):
	h = round(im.height * w / im.width)
	r = im.resize((w, h), Image.LANCZOS); p = r.load()
	for y in range(h):
		for x in range(w):
			p[x, y] = p[x, y][:3] + (255,) if p[x, y][3] > 110 else (0, 0, 0, 0)
	return r

def _warm(im, kind, face=True):
	"""สไลม์เขียว → ผิวน้ำตาลอ่อน · face=False ลบตา/ปาก/ประกาย (ปล้องลำตัว)"""
	im = im.copy(); p = im.load()
	for y in range(im.height):
		for x in range(im.width):
			c = p[x, y]
			if not c[3]:
				continue
			h, s, v = hsv(c)
			if 0.12 < h < 0.6 and s > 0.12:
				L = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
				p[x, y] = SKIN[min(len(SKIN) - 1, int(L / 256 * len(SKIN) * 1.1))] + (255,)
			elif not face and kind.get((x, y)) in ('dark', 'mouth', 'shine'):
				p[x, y] = SKIN[3] + (255,)
	return im

def _stone(im):
	"""หินเทาอมฟ้า → หินโทนอุ่นตามสเปก · มอสเขียวเก็บไว้"""
	im = im.copy(); p = im.load()
	for y in range(im.height):
		for x in range(im.width):
			c = p[x, y]
			if not c[3]:
				continue
			h, s, v = hsv(c)
			if 0.18 < h < 0.45 and s > 0.3:
				continue
			L = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
			p[x, y] = STONE[min(4, int(L / 256 * 5 * 1.15))] + (255,)
	return im

TEAL = (h2c('146E77'), h2c('13545C'))   # สเปก COMP: ผ้าพันคอ/ปลอกคอสีทีล = เครื่องหมายเพื่อนร่วมทาง
LEAF = (h2c('6F8F3A'), h2c('4F6B2A'))

def stone_worm(wiggle=0, friend=False):
	"""หนอนอ้วนหันขวา: หาง(กรวด) → ปล้อง 2 → หัวมีหน้า · หิน 3 แผ่นบนหลัง · wiggle = idle เฟรม 2 (หัวเงยขึ้น 1px)"""
	g, kind, _ = slime_parts()
	rock = cut(ROCK_BOX, tol=60, shadow=True, fringe=1)
	head = _shrink(_warm(g, kind), 28)
	mid = _shrink(_warm(g, kind, False), 21)
	tail = _shrink(_warm(g, kind, False), 15)
	cv = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
	cv.alpha_composite(tail, (2, 45 - tail.height))
	cv.alpha_composite(mid, (9, 46 - mid.height))
	for w, x, y in ((10, 2, 27), (13, 9, 21), (14, 17, 17)):   # แผ่นหินเรียงจากหางมาหาคอ ยกสูงให้เห็นปล้องข้างล่าง
		cv.alpha_composite(_stone(_shrink(rock, w)), (x, y))
	hy = 46 - head.height - wiggle
	cv.alpha_composite(head, (19, hy))
	cv.alpha_composite(_stone(_shrink(rock, 7)), (0, 39))      # ก้อนหินปลายหาง
	if friend:   # COMP-M03: ผ้าพันคอทีลโค้งตามขอบหัวด้านคอ + ชายผ้าปลิวไปหลัง · ใบไม้บนหัว
		p = cv.load()
		hp_ = head.load()
		for y in range(hy + 5, 46):
			row = [x for x in range(head.width) if 0 <= y - hy < head.height and hp_[x, y - hy][3]]
			if not row:
				continue
			x0 = 19 + row[0]
			for k, c in ((0, TEAL[1]), (1, TEAL[0]), (2, TEAL[0])):
				p[x0 + k, y] = c + (255,)
			if y == hy + 5:
				p[x0 + 1, y] = h2c('3C8A92') + (255,)     # ประกายผ้า
		for x, y in ((16, 37), (17, 37), (15, 38), (16, 38), (17, 38), (14, 39), (15, 39), (13, 40)):   # ชายผ้า
			p[x, y] = TEAL[0] + (255,)
		lx, ly = 32, hy - 1
		for dx, dy, c in ((1, -4, 0), (2, -4, 0), (0, -3, 0), (1, -3, 0), (2, -3, 1), (3, -3, 0), (1, -2, 1), (2, -2, 0), (1, -1, 1), (1, 0, 1)):
			p[lx + dx, ly + dy] = LEAF[c] + (255,)
	return hue_outline(cv)

# ── B1 ราชาหนอนเถ้า (L 96x96 บอส) ─────────────────────────────
# ตระกูลเดียวกับหนอนหิน: ปล้อง = สไลม์ในชีต ลงสีเถ้าถ่าน · เกราะ = หินก้อนใหญ่จากชีต ลงสีถ่าน · มงกุฎหนาม/เขี้ยว/ตานับสิบ วาดเพิ่ม
ASH_FLESH = [h2c(h) for h in ('150F0D', '2A2420', '3E3530', '4D2A17', '6F4B33', '8A7460')]
CHAR = [h2c(h) for h in ('150F0D', '262321', '383A37', '55524D', '76726A')]
EMBER = (h2c('E06A3C'), h2c('F2C08A'), h2c('7A1E14'))
ROCK_BIG_BOX = (1160, 520, 1220, 580)

def _recolor(im, ramp, keep_moss=False, gain=1.1):
	im = im.copy(); p = im.load()
	for y in range(im.height):
		for x in range(im.width):
			c = p[x, y]
			if not c[3]:
				continue
			if keep_moss:
				h, s_, v = hsv(c)
				if 0.18 < h < 0.45 and s_ > 0.3:
					continue
			L = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
			p[x, y] = ramp[min(len(ramp) - 1, int(L / 256 * len(ramp) * gain))] + (255,)
	return im

def worm_king(wave=0):
	"""ราชาหนอนเถ้าหันขวา ยกหัว · wave = idle เฟรม 2 (ปล้องกลางยกขึ้น 1px เป็นคลื่น)"""
	g, kind, _ = slime_parts()
	body = g.copy(); bp = body.load()
	from collections import Counter
	main = Counter(bp[k][:3] for k, v in kind.items() if v == 'body').most_common(1)[0][0]
	for k, v in kind.items():                      # ลบหน้าสไลม์ทั้งบริเวณ (ราชามีตานับสิบแทน)
		if v in ('dark', 'mouth', 'shine'):
			for dx in (-1, 0, 1):
				for dy in (-1, 0, 1):
					q = (k[0] + dx, k[1] + dy)
					if 0 <= q[0] < body.width and 0 <= q[1] < body.height and bp[q][3] and kind.get(q) != 'body' or q == k:
						bp[q] = main + (255,)
	flesh = _recolor(body, ASH_FLESH)
	rock = cut(ROCK_BIG_BOX, tol=60, shadow=True, fringe=1)
	cv = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
	segs = ((26, 2, 93, 0), (32, 14, 92, 1), (38, 28, 90, 0), (42, 42, 84, 1))   # (กว้าง, x, ขอบล่าง, ยกตอนคลื่น)
	for w, x, bottom, up in segs:
		sg = _shrink(flesh, w)
		cv.alpha_composite(sg, (x, bottom - sg.height - up * wave))
	for (w, x, y, up) in ((16, 5, 66, 0), (20, 16, 60, 1), (24, 30, 52, 0), (26, 44, 44, 1)):   # เกราะถ่านบนหลังแต่ละปล้อง
		cv.alpha_composite(_recolor(_shrink(rock, w), CHAR), (x, y - up * wave))
	head = flesh.copy()
	hx, hy = 46, 22
	cv.alpha_composite(head, (hx, hy))
	p = cv.load()
	def put(x, y, c):
		if 0 <= x < 96 and 0 <= y < 96:
			p[x, y] = c + (255,)
	# มงกุฎหนามเถ้า 5 ซี่บนหัว
	for i, (tx, th) in enumerate(((56, 9), (62, 13), (69, 15), (76, 12), (82, 8))):
		base = hy + 6 + abs(i - 2)
		for k in range(th):
			half = max(0, (th - k) // 4)
			for dx in range(-half, half + 1):
				put(tx + dx, base - k, CHAR[1] if dx < 0 else CHAR[3] if k > th - 3 else CHAR[2])
	# ตานับสิบ เรียงสองโค้งข้างหัว (เรืองแดง)
	for ex, ey in ((58, 35), (63, 32), (68, 31), (73, 32), (78, 35), (61, 41), (66, 39), (71, 39), (76, 41), (81, 43)):
		for dx in (-1, 0, 1, 2):          # เบ้าเข้มรอบตา
			for dy in (-1, 0, 1, 2):
				put(ex + dx, ey + dy, CHAR[0])
		put(ex, ey, EMBER[1]); put(ex + 1, ey, EMBER[0]); put(ex, ey + 1, EMBER[0]); put(ex + 1, ey + 1, EMBER[2])
	# เขี้ยวคู่ใหญ่โค้งลง + น้ำลายข้น
	for fx in (78, 87):                  # เขี้ยวคู่ใหญ่ โคนหนา 4px เรียวลง โค้งเข้า
		for k in range(14):
			w = 4 if k < 4 else 3 if k < 8 else 2 if k < 11 else 1
			x = fx + (k // 5)
			for dx in range(w):
				put(x + dx, 49 + k, h2c('E6E2D6') if dx < w - 1 else h2c('A2927B'))
		for k in range(3):
			put(fx + 3, 64 + k, h2c('A7B5A0'))   # น้ำลายข้นหยด
	return hue_outline(cv)

if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/sprites/monsters_ll/')
	os.makedirs(out, exist_ok=True)
	g, kind, m = slime_parts()   # kwan เลือกสีเขียวตามต้นแบบ (3 ต.ค.) · slime_ash() เก็บไว้เผื่อเทียบ
	place(g, 48).save(os.path.join(out, 'M01.png'))
	place(squash(g), 48).save(os.path.join(out, 'M01_idle1.png'))
	wolf_pair().save(os.path.join(out, 'M15.png'))
	wolf_pair(1).save(os.path.join(out, 'M15_idle1.png'))
	# M03/M06 kwan อนุมัติ 3 ต.ค. · COMP-* = เวอร์ชันเพื่อนร่วมทาง (จอสู้หา COMP-<id> ก่อน) — ร่าง ยังไม่อนุมัติ → โฟลเดอร์ draft
	stone_worm().save(os.path.join(out, 'M03.png'))
	stone_worm(1).save(os.path.join(out, 'M03_idle1.png'))
	bat().save(os.path.join(out, 'M06.png'))
	bat(1).save(os.path.join(out, 'M06_idle1.png'))
	stone_worm(friend=True).save(os.path.join(out, 'COMP-M03.png'))     # COMP อนุมัติ 3 ต.ค.
	stone_worm(1, friend=True).save(os.path.join(out, 'COMP-M03_idle1.png'))
	bat(friend=True).save(os.path.join(out, 'COMP-M06.png'))
	bat(1, friend=True).save(os.path.join(out, 'COMP-M06_idle1.png'))
	# ร่างที่ยังไม่อนุมัติ → monsters_ll_draft/ (เกมโหลด monsters_ll/ อัตโนมัติ — ร่างห้ามเข้าเกมก่อนอนุมัติ)
	draft = out.rstrip('/') + '_draft/'
	os.makedirs(draft, exist_ok=True)
	worm_king().save(os.path.join(draft, 'B1.png'))
	worm_king(1).save(os.path.join(draft, 'B1_idle1.png'))
	print('ok ->', out)
