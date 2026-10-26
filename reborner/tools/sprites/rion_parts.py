# tools/sprites/rion_parts.py — แยกชิ้นส่วน Rion 4 ทิศ: หัว · ตัว · แขนซ้าย/ขวา · ขาซ้าย/ขวา · เป้ (kwan 6 ต.ค. "แยกแขน ขา ตัว หัว ให้ภาพทิศอื่น เพื่อให้แกว่งได้ครบทุกทิศ")
#
#   python3 tools/sprites/rion_parts.py      ส่งออกชั้นชิ้นส่วน + ภาพตรวจ
#
# ขอบเขตวัดจากแผนที่สีทีละพิกเซลของภาพ 64x64 (ผิว/เสื้อ/ผ้าน้ำเงิน/เส้นขอบ) — ซ้าย/ขวา = ของภาพ ไม่ใช่ของตัวละคร
#   หัว = แถวเหนือคอ · ขา = แถวตั้งแต่ HIP (54) แบ่งซ้ายขวาที่ร่องขา · แขน/เป้ = กรอบที่วัดไว้ · ที่เหลือ = ตัว
#   หันซ้าย (west) แขนหน้าใช้แขนวาดใหม่ (rion_grips.draw_arm + ik) อยู่แล้ว ที่นี่ใส่แผนที่ไว้ส่งออกเท่านั้น
# แกว่งแขน (swing_arms): เฉือนแขน = แถวใกล้ไหล่ขยับน้อย แถวมือขยับเต็ม · หน้า/หลัง = แขนสองข้างขึ้น-ลงสลับกัน มือแบะออกนิด ·
#   หันขวา = แขนใกล้แกว่งหน้า-หลังสวนขา · ช่องที่แขนขยับออก (ทับตัวอยู่เดิม) เติมด้วยสีตัวที่ใกล้สุดในแถวเดียวกัน · นอกตัว = โปร่ง
# ออก assets/sprites/rion_parts_draft/<ทิศ>_<ชิ้น>.png (64x64 ต่อชั้น · .gdignore · ร่าง) + parts.json · ภาพตรวจ docs/art-bible/rion_parts_preview.png
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft')
OUT = os.path.join(ROOT, 'assets/sprites/rion_parts_draft')
HIP = 54
# ต่อทิศ: แถวสุดท้ายของหัว · ร่องขา (x แบ่งซ้าย/ขวา) · กรอบชิ้น (x0, x1, y0, y1 รวมขอบ) · ไหล่/มือ (y) ของแขนที่แกว่งได้
SPEC = {
	'south': {'neck': 32, 'split': 31, 'pack': (15, 20, 33, 50), 'arm_l': (21, 24, 36, 49), 'arm_r': (36, 41, 35, 48), 'swing': ('arm_l', 'arm_r')},
	'north': {'neck': 31, 'split': 31, 'pack': (25, 36, 33, 49), 'arm_l': (20, 24, 35, 48), 'arm_r': (37, 42, 34, 48), 'swing': ('arm_l', 'arm_r')},
	'east':  {'neck': 31, 'split': 33, 'pack': (15, 21, 33, 49), 'arm_l': (22, 29, 35, 49), 'arm_r': None, 'swing': ('arm_l',)},
	'west':  {'neck': 30, 'split': 30, 'pack': (35, 47, 31, 51), 'arm_l': (18, 31, 39, 51), 'arm_r': None, 'swing': ()},
}
PARTS = ['head', 'torso', 'arm_l', 'arm_r', 'leg_l', 'leg_r', 'pack']
COLORS = {'head': (230, 90, 80), 'torso': (90, 170, 230), 'arm_l': (250, 200, 60), 'arm_r': (250, 140, 40), 'leg_l': (120, 220, 120), 'leg_r': (60, 160, 90), 'pack': (180, 110, 220)}

def load(d): return np.asarray(Image.open(os.path.join(SRC, d + '.png')).convert('RGBA')).copy()

def rect_mask(box, op):
	m = np.zeros_like(op)
	if box: x0, x1, y0, y1 = box; m[y0:y1 + 1, x0:x1 + 1] = True
	return m & op

def masks(d, a=None):
	"""แผนที่ชิ้นส่วน (bool 64x64 ต่อชิ้น · ไม่ทับกัน) ลำดับความสำคัญ: หัว → ขา → แขน → เป้ → ตัว"""
	a = load(d) if a is None else a; op = a[..., 3] > 0; sp = SPEC[d]
	ys, xs = np.mgrid[0:64, 0:64]; m = {}
	m['head'] = op & (ys <= sp['neck'])
	m['leg_l'] = op & (ys >= HIP) & (xs <= sp['split']); m['leg_r'] = op & (ys >= HIP) & (xs > sp['split'])
	used = m['head'] | m['leg_l'] | m['leg_r']
	for k in ('arm_l', 'arm_r', 'pack'):
		m[k] = rect_mask(sp[k], op) & ~used; used |= m[k]
	m['torso'] = op & ~used
	return m

def swing_arms(img, d, s, lift=1.0):
	"""แกว่งแขน s ∈ [-1, 1] (เฟสเดิน: s = cos) · img = PIL RGBA 64x64 ของทิศนั้น (ยังไม่ผ่านขา/ย่อ) · คืนภาพใหม่"""
	sp = SPEC.get(d)
	if not sp or not sp['swing'] or abs(s) < 0.05: return img
	a = np.asarray(img.convert('RGBA')).copy(); m = masks(d, a); out = a.copy()
	body = m['torso'] | m['pack']
	for k, arm in enumerate(sp['swing']):
		am = m[arm]
		if not am.any(): continue
		x0, x1, y0, y1 = sp[arm]; side = -1 if arm == 'arm_l' else 1
		if d == 'east': dxh, dyh, dyall = -s * 2.4, -abs(s) * 1.0 * lift, 0          # หันขวา: แกว่งหน้า-หลัง (ขาหน้าไปหน้า = แขนไปหลัง)
		else:
			v = s if k == 0 else -s                                                  # หน้า/หลัง: สองแขนสลับ
			dxh, dyh, dyall = side * abs(v) * 1.2, 0.0, -v * 1.2 * lift            # แขนที่แกว่งไปหน้า/หลังยกขึ้น มือแบะออก
		out[am] = 0
		# ช่องที่แขนเคยอยู่: ในช่วงกว้างของตัวแถวนั้น = สีตัวที่ใกล้สุด · นอกตัว = โปร่ง
		for y in range(y0, y1 + 1):
			bx = np.nonzero(body[y])[0]
			if not len(bx): continue
			for x in np.nonzero(am[y])[0]:
				if bx.min() <= x <= bx.max():
					j = bx[np.abs(bx - x).argmin()]; out[y, x] = a[y, j]
		src = np.where(am)
		for y, x in zip(*src):
			f = (y - y0) / max(1, y1 - y0)                                           # 0 ที่ไหล่ → 1 ที่มือ
			nx, ny = int(round(x + dxh * f)), int(round(y + dyall + dyh * f))
			if 0 <= nx < 64 and 0 <= ny < 64: out[ny, nx] = a[y, x]
	return Image.fromarray(out, 'RGBA')

def main():
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	info = {'_doc': 'ชิ้นส่วน Rion 4 ทิศ (tools/sprites/rion_parts.py) · แต่ละไฟล์ 64x64 วางซ้อนตำแหน่งเดิม · ร่าง ยังไม่เข้าเกม', 'hip': HIP, 'dirs': {}}
	k = 4; pv = Image.new('RGBA', (64 * k * 4, 64 * k * 2), (40, 42, 48, 255))
	for i, d in enumerate(['south', 'west', 'north', 'east']):
		a = load(d); m = masks(d, a); info['dirs'][d] = {'neck': SPEC[d]['neck'], 'split': SPEC[d]['split'], 'parts': {}}
		over = np.zeros((64, 64, 4), np.uint8)
		for p in PARTS:
			lay = np.zeros_like(a); lay[m[p]] = a[m[p]]
			Image.fromarray(lay, 'RGBA').save(os.path.join(OUT, f'{d}_{p}.png'))
			ys, xs = np.nonzero(m[p]); info['dirs'][d]['parts'][p] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None
			over[m[p], :3] = COLORS[p]; over[m[p], 3] = 255
		pv.alpha_composite(Image.fromarray(a, 'RGBA').resize((64 * k, 64 * k), Image.NEAREST), (i * 64 * k, 0))
		pv.alpha_composite(Image.fromarray(over, 'RGBA').resize((64 * k, 64 * k), Image.NEAREST), (i * 64 * k, 64 * k))
	json.dump(info, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	pv.save(os.path.join(ROOT, 'docs/art-bible/rion_parts_preview.png'))
	print('ok', len(info['dirs']), 'ทิศ ×', len(PARTS), 'ชิ้น')

if __name__ == '__main__':
	main()
