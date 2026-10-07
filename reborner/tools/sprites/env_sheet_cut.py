# tools/sprites/env_sheet_cut.py — ตัดชิ้นจากชีต "Reborner Environment Tileset" (kwan ส่ง 7 ต.ค. 2026 · พร้อม prompt pack)
#
#   python3 tools/sprites/env_sheet_cut.py [หมวด ...]      (ไม่ใส่ = ทุกหมวดใน PANELS)
#
# ชีต: docs/art-bible/world/environment_tileset_sheet.png (1536x1024 · พื้นกรมท่าเข้ม · กรอบหมวดเรืองฟ้า)
# kwan เลือก 7 ต.ค.: ยึดเกมเดิม (มุมบนลงล่าง ช่อง 24px · Overworld.gd TILE) — ชีตเป็นมุม 3/4 ช่อง 32px จึงใช้ชิ้นเป็นของวางบนแผนที่ ไม่ใช่ไทล์พื้น
# ต่อหมวด: ลบพื้น (เทจากขอบกรอบเฉพาะสีมืดอมน้ำเงิน) → ก้อนติดกัน (ไม่ขยาย — ของวางชิดกันในชีตจะได้ไม่ติดกัน) → ทิ้งก้อนเล็ก
#   → <id>_src.png ขนาดชีต · <id>_0.png ย่อด้วยอัตราเดียวทั้งหมวด (SCALE · ลังในชีต ~32px → ~20px เท่าลังในเกม) สีมากสุดในบล็อก + ลดสีร่วม ≤ COLORS
# ออก assets/sprites/env_sheet_draft/ (.gdignore · ร่าง ไม่เข้าเกม) + index.json + ชีตตรวจ docs/art-bible/world/env_<หมวด>_cut.png
# ไม่มีตัวเลขเกมในไฟล์นี้ — เป็นค่ารูปภาพทั้งหมด
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

ROOT = sc.ROOT
SRC = os.path.join(ROOT, 'docs/art-bible/world/environment_tileset_sheet.png')
OUT = os.path.join(ROOT, 'assets/sprites/env_sheet_draft')
SCALE, COLORS, MIN_AREA = 1.6, 24, 120

# หมวด: (รหัส, ชื่อไทย, กรอบในชีต x0 y0 x1 y1 — ใต้แถบชื่อหมวด ในขอบเรือง)
PANELS = {
	'props': ('PR', 'ของวาง (Props)', (1294, 112, 1532, 436)),
}

def bg_mask(rgb):
	"""พื้นกรมท่า: มืด + น้ำเงิน ≥ แดง · เทจากขอบกรอบเท่านั้น (เส้นขอบตัวของที่มืดแต่อุ่นไม่โดน · ช่องมืดในตัวของที่ปิดล้อมไม่โดน)"""
	r, g, b = (rgb[..., i].astype(int) for i in range(3))
	dark = (r + g + b < 150) & (b >= r + 6)
	lab, _ = ndimage.label(dark)
	edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
	return np.isin(lab, list(edge))

def pieces(rgb):
	op = ~bg_mask(rgb)
	op = ndimage.binary_opening(op, np.ones((2, 2)))   # เส้นขอบเรือง/จุดรบกวน 1px
	lab, n = ndimage.label(op)
	out = []
	for i, sl in enumerate(ndimage.find_objects(lab), 1):
		m = (lab[sl] == i) & op[sl]
		if m.sum() < MIN_AREA: continue
		out.append((sl, m))
	out.sort(key=lambda p: (p[0][0].start // 40, p[0][1].start))   # อ่านทีละแถว ซ้าย→ขวา
	return out

def run(key):
	code, name, box = PANELS[key]
	sheet = np.asarray(Image.open(SRC).convert('RGB'))
	x0, y0, x1, y1 = box
	rgb = sheet[y0:y1, x0:x1]
	ps = pieces(rgb)
	small, srcs, info = [], [], []
	for n, (sl, m) in enumerate(ps, 1):
		sub = rgb[sl]
		src = np.zeros(sub.shape[:2] + (4,), np.uint8); src[..., :3] = sub; src[..., 3] = m * 255
		srcs.append(src)
		small.append(sc.drop_orphans(sc.block_mode(sub, m, SCALE)))
		info.append({'id': f'{code}{n:02d}', 'box': [x0 + sl[1].start, y0 + sl[0].start, x0 + sl[1].stop, y0 + sl[0].stop]})
	pal = sc.auto_palette(small, COLORS)
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, '.gdignore'), 'w').close()
	for it, s, src in zip(info, small, srcs):
		img, _ = sc.lock(s, pal)
		Image.fromarray(img, 'RGBA').save(os.path.join(OUT, it['id'] + '_0.png'))
		Image.fromarray(src, 'RGBA').save(os.path.join(OUT, it['id'] + '_src.png'))
		it['size'] = [img.shape[1], img.shape[0]]
	# ชีตตรวจ: ชิ้นย่อแล้ว ขยาย ×4 เรียงแถว บนพื้นเทาเข้ม
	cell = max(max(i['size']) for i in info) * 4 + 8; cols = 8; rows = -(-len(info) // cols)
	pv = Image.new('RGBA', (cols * cell, rows * cell), (46, 42, 34, 255))
	for k, it in enumerate(info):
		im = Image.open(os.path.join(OUT, it['id'] + '_0.png')); w, h = im.size
		im = im.resize((w * 4, h * 4), Image.NEAREST)
		pv.alpha_composite(im, ((k % cols) * cell + (cell - w * 4) // 2, (k // cols) * cell + cell - 4 - h * 4))
	pv.save(os.path.join(ROOT, f'docs/art-bible/world/env_{key}_cut.png'))
	return {'key': key, 'name': name, 'scale': SCALE, 'colors': len(pal), 'items': info}

def main():
	keys = sys.argv[1:] or list(PANELS)
	idx_path = os.path.join(OUT, 'index.json')
	idx = json.load(open(idx_path, encoding='utf-8')) if os.path.exists(idx_path) else {}
	idx['_doc'] = 'ชิ้นตัดจากชีต Environment Tileset (tools/sprites/env_sheet_cut.py) · ร่าง ยังไม่เข้าเกม'
	idx.setdefault('panels', {})
	for k in keys:
		idx['panels'][k] = run(k)
		print(k, len(idx['panels'][k]['items']), 'ชิ้น ·', idx['panels'][k]['colors'], 'สี')
	json.dump(idx, open(idx_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
	main()
