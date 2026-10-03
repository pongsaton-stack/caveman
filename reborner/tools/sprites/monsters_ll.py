# tools/sprites/monsters_ll.py — มอนสไตล์ Last Light ตามสเปก docs/art-bible/monster_visual_master.json
# แนวที่ kwan สั่ง (3 ต.ค. 2026): "ให้เหมือนต้นแบบที่สุด ขัด bible ได้ คิดนอกกรอบได้"
#   → ตัดจากชีต lastlight_01.png โดยตรง (แบบเดียวกับ Rion/หมา) แล้วเก็บงาน/ลงสี — ไม่วาดจากรูปทรงเรขาคณิตอีก
#   M01 สไลม์เถ้า : ตัดสไลม์ในชีต (48x38 พอดีช่อง S) · 2 แบบ: green = สีต้นแบบ · ash = ลงสีเถ้า คงตา/ปาก/ประกาย
#   M15 หมาป่าคู่ : ชีตไม่มีหมาป่า → ใช้หมาคู่หู (dog_lastlight_draft) ลงสีเทาน้ำตาล วางสองตัว ตัวหลังหูพับ
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

if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/sprites/monsters_ll/')
	os.makedirs(out, exist_ok=True)
	g, kind, m = slime_parts()
	a = slime_ash(g, kind, m)
	for name, im in (('M01_green', g), ('M01_ash', a)):
		place(im, 48).save(os.path.join(out, name + '.png'))
		place(squash(im), 48).save(os.path.join(out, name + '_idle1.png'))
	wolf_pair().save(os.path.join(out, 'M15.png'))
	wolf_pair(1).save(os.path.join(out, 'M15_idle1.png'))
	print('ok ->', out)
