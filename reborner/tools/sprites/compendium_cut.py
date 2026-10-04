# tools/sprites/compendium_cut.py — ตัดมอน 64 ช่องจาก Monster Compendium (kwan ส่ง 4 ต.ค. 2026)
# ต้นฉบับ docs/art-bible/compendium/monster_compendium.jpg (2576x1717)
# วิธี: ลบพื้นครีม → หาก้อนภาพ → ก้อนเตี้ยสีน้ำเงินเข้ม = ป้ายชื่อ → ก้อนภาพยกให้ป้ายที่อยู่ใต้มัน (ช่องเดียวกัน)
# ผล: assets/sprites/compendium_draft/<region>_<n>_<slug>.png (ตัวหลัก 48px) + _idle1 + _card.png (ทุกตัวในช่อง)
# **ร่าง ยังไม่เข้าเกม** — แสดงในหน้า animation test เท่านั้น
import os, re, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as nd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ll_polish import hue_outline, clamp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'docs/art-bible/compendium/monster_compendium.jpg')
OUT = os.path.join(ROOT, 'assets/sprites/compendium_draft')
# กรอบแต่ละภูมิ (พิกัดในภาพ 2576 กว้าง) + ชื่อตามลำดับ แถวบนซ้าย→ขวา แล้วแถวล่าง (อ่านจากป้ายในชีต)
REGIONS = [
	('overworld', 'หมู่บ้าน-ซากเมือง', (19, 231, 747, 618), ['Slime', 'Small Rat', 'Mutant Rat', 'Scavenger', 'Bandit', 'Dog (NPC)', 'Zombie', 'Runner', 'Civilian', 'Security Bot']),
	('forest', 'ป่าไม้', (766, 231, 1403, 605), ['Fox', 'Rabid Fox', 'Wolf', 'Dire Wolf', 'Boar', 'Alpha Boar', 'Forest Spirit', 'Treant']),
	('water', 'แม่น้ำ-ทะเล', (1423, 231, 1912, 605), ['Fish', 'Piranha', 'Jellyfish', 'Sea Slime', 'Turtle', 'Shark', 'Sea Serpent', 'Crab']),
	('ruins', 'ซากปรักหักพัง', (1932, 231, 2550, 605), ['Skeleton', 'Skeleton Archer', 'Armored Skeleton', 'Wraith', 'Ancient Guardian', 'Stone Golem', 'Relic Machine', 'Ghost']),
	('desert', 'ทะเลทราย', (19, 676, 656, 1075), ['Sand Slime', 'Scorpion', 'Cactus Monster', 'Sand Bandit', 'Worm', 'Sand Golem', 'Mummy', 'Dust Devil']),
	('cave', 'ถ้ำ', (676, 676, 1281, 1075), ['Bat', 'Cave Spider', 'Rock Golem', 'Crystal Golem', 'Lava Slime', 'Lava Elemental', 'Cave Lizard', 'Deep Crawler']),
	('underground', 'ใต้ดิน', (1294, 676, 1880, 1075), ['Mole', 'Tunnel Worm', 'Miner Bot', 'Crystal Beetle', 'Crystal Spider', 'Ancient Dragon', 'Underground King', 'The Core']),
	('special', 'พิเศษ', (1893, 676, 2550, 1075), ['Explosive Slime', 'Berserker', 'Toxic Plant', 'Floating Eye', 'Mirror Knight', 'Infected Creature', 'Time Anomaly', 'Reality Fragment']),
]
CELL = 48; TALL = 42

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

LABEL_BAND = 0.74   # ส่วนล่างของแต่ละแถวการ์ด (สัดส่วนจากบนแถว) = ป้ายชื่อ — ตัดทิ้งก่อนหาก้อนภาพ

def cut_region(img, box, names):
	"""แบ่งกรอบเป็นตาราง 2 แถว × (จำนวนชื่อ/2) คอลัมน์เท่ากัน · ก้อนภาพเข้าช่องตามจุดกึ่งกลาง"""
	c = np.asarray(img.crop(box)).astype(int)
	H, W = c.shape[:2]; ncol = len(names) // 2; rowh = H / 2; colw = W / ncol
	r, g, b = c[..., 0], c[..., 1], c[..., 2]
	fg = nd.binary_opening(~((r > 222) & (g > 208) & (b > 185) & (r - b < 55)), iterations=1)
	for row in range(2):
		fg[int(row * rowh + LABEL_BAND * rowh):int((row + 1) * rowh), :] = False
	lab, n = nd.label(nd.binary_dilation(fg, iterations=3))
	lab = np.where(fg, lab, 0)
	cards = [{'spr': []} for _ in names]
	for i, s in enumerate(nd.find_objects(lab)):
		if s is None: continue
		h = s[0].stop - s[0].start; w = s[1].stop - s[1].start
		if h < 12 or w < 12: continue
		cx = (s[1].start + s[1].stop) / 2; cy = (s[0].start + s[0].stop) / 2
		k = int(cy // rowh) * ncol + min(ncol - 1, int(cx // colw))
		cards[k]['spr'].append((s, i + 1))
	return c, lab, cards

def to_rgba(c, lab, items):
	ys = [s[0].start for s, _ in items]; ye = [s[0].stop for s, _ in items]
	xs = [s[1].start for s, _ in items]; xe = [s[1].stop for s, _ in items]
	y0, y1, x0, x1 = min(ys), max(ye), min(xs), max(xe)
	sub = c[y0:y1, x0:x1]; L = lab[y0:y1, x0:x1]
	r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
	keep = np.isin(L, [i for _, i in items]) & ~((r > 222) & (g > 208) & (b > 185) & (r - b < 55))
	a = np.where(keep, 255, 0)
	return Image.fromarray(np.dstack([sub, a]).astype('uint8'), 'RGBA')

def fit(im, tall=TALL, box=CELL - 2):
	k = min(tall / im.height, box / im.width)
	w, h = max(1, round(im.width * k)), max(1, round(im.height * k))
	r = im.resize((w, h), Image.LANCZOS); px = r.load()
	for y in range(h):
		for x in range(w):
			p = px[x, y]; px[x, y] = p[:3] + ((255,) if p[3] >= 128 else (0,))
	return r

def place(sp, size=CELL):
	cv = Image.new('RGBA', (size, size), (0, 0, 0, 0)); cv.paste(sp, ((size - sp.width) // 2, size - sp.height - 1), sp); return cv

def main():
	img = Image.open(SRC).convert('RGB')
	os.makedirs(OUT, exist_ok=True)
	index = []
	for key, th, box, names in REGIONS:
		c, lab, cards = cut_region(img, box, names)
		for n, (m, name) in enumerate(zip(cards, names)):
			if not m['spr']:
				print('!! ไม่มีภาพ', key, name); continue
			fid = '%s_%02d_%s' % (key, n + 1, slug(name))
			card = to_rgba(c, lab, m['spr'])
			card.save(os.path.join(OUT, fid + '_card.png'))
			main_s = max(m['spr'], key=lambda t: (t[0][0].stop - t[0][0].start) * (t[0][1].stop - t[0][1].start))
			sp = hue_outline(clamp(fit(to_rgba(c, lab, [main_s]))))
			place(sp).save(os.path.join(OUT, fid + '.png'))
			place(sp.resize((sp.width, max(1, sp.height - 1)), Image.NEAREST)).save(os.path.join(OUT, fid + '_idle1.png'))
			index.append({'id': fid, 'region': key, 'region_th': th, 'name': name, 'variants': len(m['spr'])})
	json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, indent=1)
	# ชีตตรวจ: ตัวหลัก 48px ทั้งหมด 8 ต่อแถว
	cols = 10; rows = (len(index) + cols - 1) // cols
	sheet = Image.new('RGBA', (cols * CELL, rows * CELL), (232, 217, 181, 255))
	for i, e in enumerate(index):
		t = Image.open(os.path.join(OUT, e['id'] + '.png')); sheet.paste(t, ((i % cols) * CELL, (i // cols) * CELL), t)
	sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(ROOT, 'docs/art-bible/previews/compendium_draft.png'))
	print('ok', len(index))

if __name__ == '__main__':
	main()
