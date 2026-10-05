# tools/sprites/weapons_stack.py — อาวุธ 2D ที่หมุนได้แบบ sprite stack (kwan เลือก 5 ต.ค. 2026 · ข้อ 3)
#
#   python3 tools/sprites/weapons_stack.py
#
# sprite stack = ภาพแบนหลายชั้นซ้อนกัน แต่ละชั้นเลื่อนขึ้น 1px → หมุนทุกชั้นพร้อมกันแล้วดูมีความหนา (ยังเป็นพิกเซล 2D ล้วน ไม่มี 3D)
# ต่อชิ้น: วางไอคอน 32px ราบกับพื้น → ความหนาต่อพิกเซล = ระยะจากขอบรูป (ใบมีดบาง ด้าม/ตัวปืนหนา) ไม่เกิน MAX_LAYERS
#   ชั้นบนสุดของแต่ละพิกเซล = สีเดิม · ชั้นที่อยู่ใต้ลงไป = สีเดิมมืดลง (เห็นเป็นด้านข้างตอนหมุน)
# ออก assets/sprites/weapons_stack_draft/<รหัส>.png = ชั้นเรียงซ้าย→ขวา (ชั้นล่าง → บน) กว้าง 32 × จำนวนชั้น + index.json
# ภาพตรวจ docs/art-bible/weapons/weapon_stack_preview.png (บางชิ้น 8 มุม · วาดด้วย render() ตัวเดียวกับหน้าเทส)
# หน้า animation test วาดสดใน JS ด้วยวิธีเดียวกับ render() (หมุน nearest ที่ความละเอียดจริง แล้วค่อยขยาย)
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

SRC = os.path.join(sc.ROOT, 'assets/sprites/weapons_sheet_draft')
OUT = os.path.join(sc.ROOT, 'assets/sprites/weapons_stack_draft')
N = 32
MAX_LAYERS = 5       # หนาสุด 5px ที่ไอคอน 32px (ราว 1/6 ของความยาว)
THICK_PER_DIST = 0.8 # ความหนาต่อระยะจากขอบ 1px
SIDE_DARK = 0.62     # สีด้านข้าง = สีผิว × ค่านี้ (ชั้นล่างสุด) ไล่สว่างขึ้นถึง ×0.85 ใต้ผิวบน
TILT = 0.62          # มองเฉียงจากบน: แกนลึกหดเหลือเท่านี้ (เท่ากับหน้าเทส)

def layers(icon):
	a = np.asarray(icon.convert('RGBA')).copy()
	m = a[..., 3] > 0
	t = np.clip(np.round(ndimage.distance_transform_edt(m) * THICK_PER_DIST), 1, MAX_LAYERS).astype(int) * m
	L = int(t.max()) or 1
	out = []
	for z in range(L):
		lay = np.zeros_like(a); on = t > z
		lay[on] = a[on]
		side = on & (t - 1 > z)   # มีชั้นอยู่ข้างบน → ด้านข้าง
		k = SIDE_DARK + (0.85 - SIDE_DARK) * z / max(1, L - 1)
		lay[side, :3] = (a[side, :3] * k).astype(np.uint8)
		out.append(Image.fromarray(lay, 'RGBA'))
	return out

def render(lays, angle, size=48):
	"""หมุนทุกชั้นแบบ nearest ที่ความละเอียดจริง แล้วหดแกนลึก (TILT) · ชั้นที่ z สูงเลื่อนขึ้น z px"""
	can = Image.new('RGBA', (size, size), (0, 0, 0, 0))
	for z, lay in enumerate(lays):
		r = lay.rotate(math.degrees(angle), Image.NEAREST, expand=True)
		r = r.resize((r.width, max(1, round(r.height * TILT))), Image.NEAREST)
		can.alpha_composite(r, ((size - r.width) // 2, (size - r.height) // 2 + 6 - z))
	return can

def main():
	idx = json.load(open(os.path.join(SRC, 'index.json'), encoding='utf-8'))['items']
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	items = []; demo = []
	for it in idx:
		lays = layers(Image.open(os.path.join(SRC, it['code'] + '.png')))
		strip = Image.new('RGBA', (N * len(lays), N), (0, 0, 0, 0))
		for z, l in enumerate(lays): strip.paste(l, (z * N, 0))
		strip.save(os.path.join(OUT, it['code'] + '.png'))
		items.append({'code': it['code'], 'family': it['family'], 'tier': it.get('tier'), 'name': it.get('name'), 'layers': len(lays)})
		if it['code'] in ('SL01', 'SL20', 'PC25', 'CR09', 'BD10', 'ST03', 'DV08', 'W301', 'W307'): demo.append(lays)
	json.dump({'_doc': 'sprite stack ของอาวุธจากชีต 210 · ไฟล์ = ชั้นเรียงซ้าย→ขวา (ล่าง→บน) ช่องละ 32px · ร่าง ยังไม่เข้าเกม · tools/sprites/weapons_stack.py',
		'tilt': TILT, 'items': items}, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	angs = [i * math.pi / 4 for i in range(8)]
	pv = Image.new('RGBA', (48 * 8, 48 * len(demo)), (58, 62, 70, 255))
	for r, lays in enumerate(demo):
		for c, a in enumerate(angs): pv.alpha_composite(render(lays, a), (c * 48, r * 48))
	pv.resize((pv.width * 3, pv.height * 3), Image.NEAREST).save(os.path.join(sc.ROOT, 'docs/art-bible/weapons/weapon_stack_preview.png'))
	cnt = {}
	for i in items: cnt[i['layers']] = cnt.get(i['layers'], 0) + 1
	print(len(items), 'ชิ้น · จำนวนชั้น→จำนวนชิ้น', dict(sorted(cnt.items())))

if __name__ == '__main__':
	main()
