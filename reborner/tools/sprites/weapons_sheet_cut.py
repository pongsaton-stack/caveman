# tools/sprites/weapons_sheet_cut.py — ตัดอาวุธทีละชิ้นจากชีต "Reborner Weapon Collection 210" (kwan ส่ง 5 ต.ค. 2026)
#
#   python3 tools/sprites/weapons_sheet_cut.py
#
# ชีต: docs/art-bible/weapons/weapon_collection_210.png (1536x1024 · พื้นตารางหมากรุกปลอม · มีป้ายรหัสใต้ทุกช่อง)
# ตำแหน่งช่อง = ตำแหน่งป้ายรหัสที่วัดจากชีตนี้ (ตัวอักษรสีกรมท่า · กลางป้าย x · ขอบบนป้าย y) — รูปอยู่เหนือป้ายในช่องเดียวกัน
# ต่อช่อง: ลบพื้น (เทจากขอบช่องเฉพาะสีอ่อนไม่อิ่มตัว → ส่วนสว่างในใบมีดที่มีเส้นขอบล้อมไม่โดน) → ก้อนใหญ่สุด + เศษที่อยู่ติดกัน
#   → <code>_src.png ขนาดชีต · <code>.png ย่อให้ด้านยาว ≤ FIT ในผืน 32x32 (ขนาดเดียวกับ weapons_draft) ด้วยสีมากสุดในบล็อก + ลดสี ≤ 16 สี
# ออก assets/sprites/weapons_sheet_draft/ (.gdignore · ร่าง ไม่เข้าเกม) + index.json + ชีตตรวจ docs/art-bible/weapons/weapon_collection_cut.png
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

ROOT = sc.ROOT
SRC = os.path.join(ROOT, 'docs/art-bible/weapons/weapon_collection_210.png')
OUT = os.path.join(ROOT, 'assets/sprites/weapons_sheet_draft')
CANVAS, FIT = 32, 30

# (ตระกูล, สาย, รหัสแรก, กลางป้าย x ต่อคอลัมน์, ขอบบนป้ายต่อแถว, ความสูงที่รูปใช้เหนือป้าย, ครึ่งความกว้างช่อง)
# สายตามป้ายในชีต: SL ฟัน · PC แทง · CR ทุบ · BD ร่างกาย · ST ยิง · DV สายกล → สายในเกม คม/แทง/ทุบ/มือเปล่า/ยิง/กล
PANELS = [
	('SL', 'คม', 1, [76, 133, 189, 245, 300, 356], [243, 317, 393, 471, 555], 64, 27),
	('PC', 'แทง', 1, [462, 517, 571, 627, 680, 735], [243, 317, 394, 473, 555], 64, 27),
	('CR', 'ทุบ', 1, [842, 896, 948, 1000, 1051, 1102], [244, 320, 398, 474, 556], 64, 26),
	('BD', 'มือเปล่า', 1, [1214, 1269, 1323, 1378, 1432, 1487], [245, 320, 398, 477, 556], 64, 27),
	('ST', 'ยิง', 1, [74, 130, 187, 243, 298, 353], [687, 754, 819, 881, 940], 56, 27),
	('DV', 'กล', 7, [439, 506, 571, 634, 696, 757], [699, 775, 854], 66, 31),
	('DV', 'กล', 25, [439, 506, 573, 644, 717], [933], 66, 31),   # แถวสุดท้าย 5 ช่อง ระยะห่างไม่เท่าแถวบน
]
# อาวุธเดิม 10 ชิ้น: ป้าย W301… อยู่ใต้รูป ชื่อไทยใต้ป้ายอีกบรรทัด
LEGACY_X, LEGACY_Y = [855, 932, 1007, 1081, 1152], [730, 856]
LEGACY_NAMES = ['กระทะ', 'ไม้กวาด', 'ขวดแก้ว', 'ค้อน', 'คีม', 'ปืนฉีดน้ำ', 'ร่ม', 'ถังแก๊ส', 'จอบ', 'โทรโข่ง']   # อ่านจากป้ายในชีต
TIERS = 5

def cells():
	for fam, school, first, xs, ys, span, half in PANELS:
		n = first
		for row, y in enumerate(ys):
			for x in xs:
				tier = (n - 1) // 6 + 1
				yield {'code': f'{fam}{n:02d}', 'family': fam, 'school': school, 'tier': tier, 'box': (x - half, y - span, x + half, y - 1)}
				n += 1
	n = 301
	for y in LEGACY_Y:
		for x in LEGACY_X:
			yield {'code': f'W{n}', 'family': 'W', 'school': None, 'tier': None, 'name': LEGACY_NAMES[n - 301], 'box': (x - 37, y - 78, x + 37, y - 1)}
			n += 1

def background(rgb):
	"""พื้นช่อง = สีอ่อนไม่อิ่มตัว (ตารางหมากรุก · ขอบช่องสีจาง) ที่ต่อถึงขอบช่อง"""
	mx, mn = rgb.max(2), rgb.min(2)
	light = (mx >= 175) & (mx - mn <= 60)
	lab, _ = ndimage.label(light)
	edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
	return np.isin(lab, list(edge))

def subject(op):
	"""ก้อนใหญ่สุด + ก้อนที่ห่างไม่เกิน 3px (ประกาย/ปลายที่ขาดจากตัว) และไม่แตะขอบช่อง"""
	lab, n = ndimage.label(op)
	if not n: return op
	size = ndimage.sum(op, lab, range(1, n + 1)); big = int(size.argmax()) + 1
	near = ndimage.binary_dilation(lab == big, iterations=3)
	edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}   # เส้นขอบช่อง/ของช่องข้าง ๆ แตะขอบเสมอ
	keep = {big} | {i for i in range(1, n + 1) if size[i - 1] >= 4 and i not in edge and (near & (lab == i)).any()}
	return np.isin(lab, list(keep))

def main():
	a = np.asarray(Image.open(SRC).convert('RGB')).astype(int)
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	index = []; thumbs = []
	for c in cells():
		x0, y0, x1, y1 = c.pop('box'); rgb = a[y0:y1, x0:x1]
		op = subject(~background(rgb))
		ys, xs = np.where(op)
		if not len(xs): print('ว่าง', c['code']); continue
		by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
		src = np.zeros((by1 - by0, bx1 - bx0, 4), np.uint8)
		src[..., :3] = rgb[by0:by1, bx0:bx1]; src[..., 3] = op[by0:by1, bx0:bx1] * 255
		Image.fromarray(src, 'RGBA').save(os.path.join(OUT, c['code'] + '_src.png'))
		s = max(src.shape[0], src.shape[1]) / FIT
		small = sc.block_mode(src[..., :3], src[..., 3] > 0, max(1.0, s), fill=0.4)
		small = sc.drop_orphans(small)
		if (small[..., 3] > 0).any():
			small, _ = sc.lock(small, sc.auto_palette([small], 16))
		can = np.zeros((CANVAS, CANVAS, 4), np.uint8)
		h, w = small.shape[:2]; oy, ox = (CANVAS - h) // 2, (CANVAS - w) // 2
		can[oy:oy + h, ox:ox + w] = small
		Image.fromarray(can, 'RGBA').save(os.path.join(OUT, c['code'] + '.png'))
		c.update(src_box=[int(x0 + bx0), int(y0 + by0), int(x0 + bx1), int(y0 + by1)], scale=round(s, 2),
			colors=int(len(np.unique(can[can[..., 3] > 0][:, :3], axis=0))))
		index.append(c); thumbs.append((c['code'], can))
	json.dump({'_doc': 'ตัดจาก docs/art-bible/weapons/weapon_collection_210.png ด้วย tools/sprites/weapons_sheet_cut.py · ร่าง ยังไม่เข้าเกม · '
		'school = สายในเกมที่ตรงกับตระกูลในชีต (W = อาวุธเดิม ไม่มีสายในชีต) · tier = แถวในชีต',
		'items': index}, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	# ชีตตรวจ: 12 ต่อแถว ขยาย 3 เท่า
	cols = 12; rows = (len(thumbs) + cols - 1) // cols; cell = CANVAS + 4
	sheet = Image.new('RGBA', (cols * cell, rows * cell), (58, 62, 70, 255))
	for i, (_, t) in enumerate(thumbs): sheet.alpha_composite(Image.fromarray(t, 'RGBA'), ((i % cols) * cell + 2, (i // cols) * cell + 2))
	sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(ROOT, 'docs/art-bible/weapons/weapon_collection_cut.png'))
	fams = {}
	for c in index: fams[c['family']] = fams.get(c['family'], 0) + 1
	print(len(index), 'ชิ้น ·', fams)

if __name__ == '__main__':
	main()
