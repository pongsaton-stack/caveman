# tools/sprites/items_icons.py — การ์ดไอเท็ม: ไอคอน 32x32 (ร่าง · ยังไม่เข้าเกม)
# รายชื่อมาจากไฟล์เกมตรง ๆ: data/items.csv (ยา) + ของดรอปของมอน/บอสใน data/monsters.csv (คอลัมน์ drop/drop_rate)
# ตัวเลขทุกตัวบนการ์ดอ่านจาก csv — ไม่มีเลขที่พิมพ์เอง · หน้าที่ของวัตถุดิบยังไม่กำหนด (ชีตสินค้า 19 ชิ้นอยู่ในเวิร์กบุ๊ก ไม่อยู่ใน repo)
# ผล: assets/sprites/items_draft/<id>.png + index.json
import csv, json, math, os
from pixkit import Sprite, ramp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets/sprites/items_draft')
SCHOOL = {'White': (226, 222, 196), 'Black': (64, 56, 74), 'Red': (176, 52, 44), 'อัญเชิญ': (214, 128, 52)}

# ── ลวดลายไอคอน ──
def book(s, col, torn=False):
	s.part((120, 84, 56), lambda d: d.rectangle([7, 6, 25, 27]))                     # สันปก
	s.part(col, lambda d: d.rectangle([9, 5, 25, 26]))
	s.part((236, 226, 196), lambda d: d.rectangle([10, 24, 24, 26]), tex=0, outline=False)   # ขอบกระดาษ
	s.flat((240, 210, 120), lambda d: d.ellipse([14, 11, 20, 17]), alpha=230)          # ตราบนปก
	s.px([(17, 12), (15, 14), (19, 14), (17, 16)], ramp(col)[1])
	if torn: s.flat((0, 0, 0), lambda d: d.polygon([(25, 5), (25, 14), (20, 9), (22, 5)]), alpha=0)

def potion(s, col, heart=False):
	s.part((150, 110, 80), lambda d: d.rectangle([13, 4, 19, 8]))
	s.part((200, 220, 220), lambda d: d.rectangle([12, 8, 20, 11]))
	s.part(col, lambda d: d.ellipse([7, 10, 25, 28]))
	s.flat((255, 255, 255), lambda d: d.rectangle([11, 15, 12, 18]), alpha=200)
	if heart:
		s.flat((255, 236, 236), lambda d: (d.ellipse([12, 15, 16, 19]), d.ellipse([16, 15, 20, 19]), d.polygon([(12, 18), (20, 18), (16, 23)])))

def fang(s, col):
	s.part(col, lambda d: d.polygon([(8, 6), (20, 6), (17, 18), (11, 27), (10, 16)]))
	s.part((150, 70, 50), lambda d: d.rectangle([8, 5, 20, 8]))

def pair_fang(s, col):
	for ox in (0, 9):
		s.part(col, lambda d, o=ox: d.polygon([(6 + o, 7), (14 + o, 7), (12 + o, 18), (9 + o, 26), (8 + o, 16)]))

def hide(s, col):
	s.part(col, lambda d: d.polygon([(6, 8), (12, 5), (20, 6), (27, 9), (25, 17), (27, 25), (18, 27), (9, 26), (5, 20), (7, 14)]), tex=0.35)

def scale(s, col):
	for i, (x, y) in enumerate(((6, 12), (16, 10), (10, 18), (19, 19))):
		s.part(col, lambda d, x=x, y=y: d.pieslice([x, y - 6, x + 11, y + 10], 0, 180))

def bone(s, col, big=False):
	k = 2 if big else 0
	s.part(col, lambda d: (d.line([(9, 23), (23, 9)], fill=255, width=4 + k), d.ellipse([4, 19, 11 + k, 26 + k]), d.ellipse([8, 23, 14 + k, 29]),
		d.ellipse([19, 3, 26, 10 - k]), d.ellipse([22, 7, 29, 14])))

def wing(s, col):
	s.part(col, lambda d: d.polygon([(4, 10), (14, 6), (28, 8), (24, 13), (27, 17), (22, 19), (24, 24), (12, 22), (6, 16)]), tex=0.1)
	s.px([(10 + i, 12 + i // 3) for i in range(14)], ramp(col)[1])

def feather(s, col):
	s.part(col, lambda d: d.polygon([(22, 3), (27, 8), (18, 20), (9, 27), (8, 24), (14, 14)]))
	s.px([(23 - i, 6 + i) for i in range(16)], ramp(col)[0])

def stone(s, col):
	s.part(col, lambda d: d.polygon([(6, 14), (12, 7), (22, 8), (27, 16), (23, 26), (10, 26)]), tex=0.3)

def key(s, col):
	s.part(col, lambda d: (d.ellipse([4, 4, 15, 15]), d.rectangle([12, 13, 16, 28]), d.rectangle([16, 20, 21, 23]), d.rectangle([16, 25, 20, 28])))
	s.flat((0, 0, 0), lambda d: d.ellipse([8, 8, 11, 11]), alpha=0)

def wood(s, col, core=False):
	s.part(col, lambda d: d.rectangle([6, 9, 26, 22]), tex=0.3)
	s.part(col, lambda d: d.ellipse([20, 8, 28, 23]), tex=0)
	if core: s.flat((240, 200, 110), lambda d: d.ellipse([22, 13, 26, 18]))

def gear(s, col):
	pts = []
	for i in range(16):
		a = i * math.pi / 8; r = 12 if i % 2 == 0 else 9
		pts.append((16 + r * math.cos(a), 16 + r * math.sin(a)))
	s.part(col, lambda d: d.polygon(pts))
	s.flat((0, 0, 0), lambda d: d.ellipse([13, 13, 19, 19]), alpha=0)

def armor(s, col):
	s.part(col, lambda d: d.polygon([(6, 6), (26, 6), (26, 18), (16, 27), (6, 18)]), tex=0.3)
	s.px([(16, y) for y in range(8, 24)], ramp(col)[1])

def axe(s, col):
	s.part((110, 80, 56), lambda d: d.line([(8, 27), (22, 6)], fill=255, width=3))
	s.part(col, lambda d: d.polygon([(16, 5), (27, 6), (28, 17), (23, 15), (18, 11)]))

def sword(s, col):
	s.part(col, lambda d: d.polygon([(25, 3), (28, 6), (12, 22), (9, 19)]))
	s.part((90, 70, 60), lambda d: (d.line([(7, 18), (13, 24)], fill=255, width=2), d.line([(9, 22), (5, 27)], fill=255, width=3)))

def bow(s, col):
	s.part(col, lambda d: d.arc([2, 3, 26, 29], 300, 60, fill=255, width=3))
	s.px([(19, 6 + i) for i in range(21)], (220, 210, 190))

def eye(s, col):
	s.part((200, 230, 240), lambda d: d.ellipse([5, 5, 27, 27]), tex=0.05)
	s.part(col, lambda d: d.ellipse([11, 11, 21, 21]), tex=0)
	s.flat((10, 10, 20), lambda d: d.ellipse([14, 14, 18, 18])); s.px([(10, 10), (11, 9)], (255, 255, 255))

def tear(s, col):
	s.part(col, lambda d: (d.polygon([(16, 3), (9, 17), (23, 17)]), d.ellipse([8, 11, 24, 27])), tex=0.05)
	s.flat((255, 255, 255), lambda d: d.rectangle([12, 15, 13, 19]), alpha=220)

def mask(s, col):
	s.part(col, lambda d: d.ellipse([6, 3, 26, 29]), tex=0.05)
	s.flat((0, 0, 0), lambda d: (d.ellipse([10, 11, 14, 16]), d.ellipse([18, 11, 22, 16]), d.rectangle([14, 21, 18, 22])), alpha=0)

def web(s, col):
	pts = [(16 + 13 * math.cos(i * math.pi / 4), 16 + 13 * math.sin(i * math.pi / 4)) for i in range(8)]
	s.part(col, lambda d: [d.line([(16, 16), p], fill=255, width=1) for p in pts] + [d.polygon([(16 + r * math.cos(i * math.pi / 4), 16 + r * math.sin(i * math.pi / 4)) for i in range(8)], fill=None, outline=255) for r in (5, 9, 13)], light=False, tex=0)

def blob(s, col):
	s.part(col, lambda d: (d.ellipse([5, 12, 27, 28]), d.ellipse([11, 6, 21, 18])), tex=0.1)
	s.flat((255, 255, 255), lambda d: d.rectangle([12, 10, 13, 12]), alpha=200)

def spores(s, col):
	for x, y, r in ((9, 10, 5), (20, 8, 4), (17, 19, 6), (8, 22, 3), (25, 21, 3)):
		s.part(col, lambda d, x=x, y=y, r=r: d.ellipse([x - r, y - r, x + r, y + r]), tex=0.2)

def ash(s, col, glow=False, page=False):
	s.part(col, lambda d: d.pieslice([4, 12, 28, 36], 180, 360), tex=0.4)
	if glow:
		for x, y in ((11, 18), (17, 16), (21, 20), (14, 21)): s.px([(x, y), (x + 1, y)], (255, 180, 60))
	if page: s.part((220, 210, 180), lambda d: d.polygon([(12, 8), (21, 6), (22, 15), (13, 16)]), tex=0.1)

def bag(s, col):
	s.part(col, lambda d: (d.ellipse([5, 10, 27, 29]), d.polygon([(11, 6), (21, 6), (19, 12), (13, 12)])), tex=0.25)
	s.part((200, 170, 70), lambda d: d.rectangle([11, 11, 21, 13]), tex=0)
	s.flat((250, 220, 110), lambda d: d.ellipse([13, 17, 19, 23]))

def ledger(s, col):
	book(s, col); s.px([(12 + i, 20) for i in range(10)] + [(12 + i, 22) for i in range(8)], (180, 170, 150))

def claw(s, col):
	for o in (0, 6, 12):
		s.part(col, lambda d, o=o: d.polygon([(6 + o, 26), (9 + o, 26), (12 + o, 8), (10 + o, 5), (8 + o, 12)]))

def crystal(s, col):
	s.part(col, lambda d: d.polygon([(16, 3), (24, 12), (20, 28), (12, 28), (8, 12)]), tex=0.05)
	s.part(col, lambda d: d.polygon([(25, 10), (29, 16), (26, 24), (22, 20)]), tex=0.05)
	s.flat((255, 255, 255), lambda d: d.line([(14, 8), (12, 18)], fill=255), alpha=180)

def flake(s, col):   # หนังหมี/ขน → หนัง · เกล็ดเรืองใช้ scale
	hide(s, col)

# คำในชื่อ → (ลาย, สี) · ลำดับมีผล (น้ำตา ก่อน ตา)
MOTIF = [
	('ยาเติมชีวิต', lambda s: potion(s, (200, 50, 60), heart=True), 'ยา'), ('ยาสมุนไพร', lambda s: potion(s, (90, 170, 90)), 'ยา'),
	('ขี้เถ้าตำรา', lambda s: ash(s, (110, 104, 98), page=True), 'วัตถุดิบ'), ('ตำราฉีก', lambda s: book(s, (120, 110, 96), torn=True), 'วัตถุดิบ'),
	('บัญชีวิญญาณ', lambda s: ledger(s, (60, 40, 70)), 'ของสำคัญ'), ('ตำรา', None, 'ตำรา'),
	('กุญแจ', lambda s: key(s, (140, 140, 128)), 'ของสำคัญ'), ('ถุงเงิน', lambda s: bag(s, (150, 110, 70)), 'เงิน'),
	('เขี้ยวคู่', lambda s: pair_fang(s, (236, 228, 200)), 'วัตถุดิบ'), ('เขี้ยวประจุ', lambda s: fang(s, (250, 230, 110)), 'วัตถุดิบ'),
	('เขี้ยว', lambda s: fang(s, (236, 228, 200)), 'วัตถุดิบ'), ('ฟัน', lambda s: fang(s, (220, 226, 230)), 'วัตถุดิบ'),
	('หนังจ่าฝูง', lambda s: hide(s, (110, 100, 96)), 'วัตถุดิบ'), ('หนังหมี', lambda s: hide(s, (226, 230, 236)), 'วัตถุดิบ'), ('หนัง', lambda s: hide(s, (150, 104, 72)), 'วัตถุดิบ'),
	('เกล็ดเรือง', lambda s: scale(s, (110, 220, 210)), 'วัตถุดิบ'), ('เกล็ดอ่อน', lambda s: scale(s, (230, 150, 140)), 'วัตถุดิบ'), ('เกล็ดหนา', lambda s: scale(s, (70, 110, 70)), 'วัตถุดิบ'),
	('กระดูกมังกร', lambda s: bone(s, (226, 214, 180), big=True), 'วัตถุดิบ'), ('กระดูกยักษ์', lambda s: bone(s, (214, 220, 230), big=True), 'วัตถุดิบ'), ('กระดูก', lambda s: bone(s, (214, 204, 170)), 'วัตถุดิบ'),
	('ปีกราชินี', lambda s: wing(s, (120, 60, 140)), 'วัตถุดิบ'), ('ปีก', lambda s: wing(s, (80, 70, 90)), 'วัตถุดิบ'), ('ขนดำ', lambda s: feather(s, (60, 60, 76)), 'วัตถุดิบ'),
	('หินดิบ', lambda s: stone(s, (130, 124, 116)), 'วัตถุดิบ'), ('แก่นไม้', lambda s: wood(s, (130, 90, 56), core=True), 'วัตถุดิบ'), ('ไม้', lambda s: wood(s, (170, 124, 80)), 'วัตถุดิบ'),
	('เฟือง', lambda s: gear(s, (220, 180, 70)), 'วัตถุดิบ'), ('เกราะสนิม', lambda s: armor(s, (160, 90, 56)), 'วัตถุดิบ'), ('เกราะ', lambda s: armor(s, (110, 118, 124)), 'วัตถุดิบ'),
	('ขวาน', lambda s: axe(s, (150, 156, 160)), 'วัตถุดิบ'), ('ดาบเงา', lambda s: sword(s, (70, 60, 100)), 'วัตถุดิบ'), ('ธนู', lambda s: bow(s, (60, 50, 50)), 'วัตถุดิบ'),
	('น้ำตา', lambda s: tear(s, (150, 210, 240)), 'วัตถุดิบ'), ('ตาแก้ว', lambda s: eye(s, (90, 60, 160)), 'วัตถุดิบ'), ('หน้ากาก', lambda s: mask(s, (226, 222, 212)), 'วัตถุดิบ'),
	('ใย', lambda s: web(s, (236, 236, 236)), 'วัตถุดิบ'), ('เมือก', lambda s: blob(s, (140, 136, 128)), 'วัตถุดิบ'), ('สปอร์', lambda s: spores(s, (170, 100, 160)), 'วัตถุดิบ'),
	('เถ้าเรือง', lambda s: ash(s, (90, 80, 74), glow=True), 'วัตถุดิบ'), ('เหล็กก้าม', lambda s: claw(s, (120, 126, 134)), 'วัตถุดิบ'), ('เงาตกผลึก', lambda s: crystal(s, (90, 80, 140)), 'วัตถุดิบ'),
]

def tome_color(name):
	for k, c in SCHOOL.items():
		if k in name: return c
	return (120, 110, 96)

def rows():
	out = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/items.csv'), encoding='utf-8')):
		out.append({'id': r['item_id'], 'name': r['name'], 'kind': r['kind'], 'value': r['value'], 'price': r['price'], 'stock': r['stock'], 'note': r['note'], 'from': 'data/items.csv'})
	seen = {}
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8')):
		name = r['drop'].replace(' (100%)', '').strip()
		if not name or name == '-': continue
		e = seen.get(name)
		src = {'monster_id': r['monster_id'], 'monster': r['name_th'], 'region': r['region'], 'rate': r['drop_rate']}
		if e: e['sources'].append(src); continue
		seen[name] = {'id': 'D-' + r['monster_id'], 'name': name, 'sources': [src], 'from': 'data/monsters.csv (drop)'}
		out.append(seen[name])
	return out

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'w').close()
	items = rows()
	for it in items:
		s = Sprite(32, 32, it['id'])
		for word, fn, cat in MOTIF:
			if word in it['name']:
				it['cat'] = cat
				(fn or (lambda s: book(s, tome_color(it['name']))))(s); break
		else:
			raise SystemExit('ไม่มีลายสำหรับ ' + it['name'])
		s.shadow(16, 29, 10, 1); s.im.save(os.path.join(OUT, it['id'] + '.png'))
	json.dump({'_doc': 'ไอเท็มร่าง — รายชื่อ/ตัวเลขจาก data/items.csv + drop ใน data/monsters.csv (tools/sprites/items_icons.py)', 'items': items},
		open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print('ok', len(items), {c: sum(1 for i in items if i['cat'] == c) for c in {i['cat'] for i in items}})
