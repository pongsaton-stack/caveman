# tools/sprites/skill_sheet_cut.py — ตัด "Skill Sprite Sheet 173 ท่า" ทีละช่อง → เอฟเฟกต์ของแต่ละท่า + อนิเมชันกับ Rion ตัวจริง (kwan สั่ง 5 ต.ค. 2026)
#
#   python3 tools/sprites/skill_sheet_cut.py
#
# ชีต: docs/art-bible/compendium/skill_sprite_sheet.jpg (2576x1717 · 6 แผง SL PC CR BD ST DV)
# 1. หาช่อง (ชีตมีจริง 172 ช่อง แม้หัวชีตเขียน 173): แถว = เส้นขอบแนวนอนที่วัดจากชีตนี้ (ROWS) · คอลัมน์ = เส้นขอบแนวตั้งสีสดที่ยาวเกือบเต็มแถว (หาเองต่อแถว · ขอบระหว่างช่องมาเป็นคู่)
#    รหัส = ลำดับตำแหน่งในแผง (SL01…SL30 · DV07…DV29) — ป้ายในชีตเองมีผิด (DV10 เขียน DV19 · BD21 เขียน BD26 · ST25 เขียน ST29) จึงไม่อ่านจากป้าย
# 2. เอฟเฟกต์: ตัดแถบป้ายบนออก → ความทึบ = ความสว่างเหนือสีพื้นช่อง (แสงเรืองเป็นหลัก) → ลบตัวเอกตัวเล็กในชีต
#    (ก้อนสีกลาง ๆ ไม่อิ่มตัว สูงเท่าคน) → ถอดสีพื้นออก (un-premultiply) → พลิกซ้าย-ขวา ให้พุ่งไปทางซ้ายแบบจอสู้ในเกม (Rion อยู่ขวา หันซ้าย)
# 3. อนิเมชัน: Rion ตัวจริงของเกม (rion_lastlight_draft · หน้าตรงต้นแบบ Last Light) แทนตัวเอกในชีต · ท่าตามสาย (POSES)
#    จังหวะ TIMELINE: ยืน → ง้าง → ปล่อย (เอฟเฟกต์เผยจากมือออกไป) → กระทบ (สว่างวาบ) → ค้าง → จาง → คืนท่า
#    หน้า animation test วาดสดจาก index.json ชุดเดียวกัน (ไม่เก็บทุกเฟรมเป็นภาพ — หน้าใหญ่เกิน)
# ออก assets/sprites/skills_sheet_draft/ (.gdignore · ร่าง): <code>_fx.png · <code>_cell.png (ช่องต้นฉบับ) · index.json · ชีตตรวจ docs/art-bible/compendium/skill_anim_preview.png
import json, os, sys
import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

ROOT = sc.ROOT
SRC = os.path.join(ROOT, 'docs/art-bible/compendium/skill_sprite_sheet.jpg')
OUT = os.path.join(ROOT, 'assets/sprites/skills_sheet_draft')
RION = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft')

# (ตระกูล, สายในเกม, รหัสแรก, ช่วง x ของแผง, [(บน, ล่าง) ของแต่ละแถว] วัดจากเส้นขอบแนวนอนในชีตนี้)
PANELS = [
	('SL', 'คม', 1, (19, 844), [(287, 372), (380, 468), (476, 565), (573, 663), (672, 765), (772, 876)]),
	('PC', 'แทง', 1, (863, 1698), [(286, 373), (380, 474), (483, 573), (581, 671), (680, 773), (780, 878)]),
	('CR', 'ทุบ', 1, (1713, 2557), [(287, 374), (381, 475), (483, 577), (585, 680), (689, 781), (789, 882)]),
	('BD', 'มือเปล่า', 1, (19, 844), [(1019, 1105), (1114, 1196), (1205, 1289), (1298, 1381), (1389, 1469), (1476, 1548)]),
	('ST', 'ยิง', 1, (863, 1698), [(1020, 1103), (1110, 1193), (1201, 1283), (1290, 1372), (1379, 1461), (1467, 1547)]),
	('DV', 'กล', 7, (1713, 2557), [(1019, 1107), (1115, 1201), (1210, 1295), (1303, 1385), (1393, 1546)]),
]
# ชีตมีช่อง ST แค่ 29 ช่อง (ช่องที่ 25 ป้ายเขียน ST29 · แถวสุดท้ายมี 4 ช่อง) → ช่องกว้างสุดท้ายใช้ป้ายในชีต ST30 (ท่าปิดสายแบบ SL30/PC30)
CODE_OVERRIDE = {'ST29': 'ST30'}
HEADER = 0.30        # สัดส่วนบนของช่องที่เป็นป้ายรหัส+ชื่อ (ตัดทิ้ง)
FX_MAX = (176, 72)   # เอฟเฟกต์กว้าง/สูงไม่เกินนี้ (พิกเซลเกม · ช่องกว้างพิเศษ SL30/ST30/DV27-29 ย่อลง)

# ท่า Rion ต่อสาย: 5 ภาพ = ยืน · ง้าง · ปล่อย · กระทบ · คืนท่า (ไฟล์ใน rion_lastlight_draft · grips/ = ท่าตามการจับ)
POSES = {
	'SL': ['west', 'west_a0', 'west_a1', 'west_a2', 'west_a3'],
	'PC': ['west', 'west_a0', 'west_a1', 'west_a1', 'west_a3'],
	'CR': ['grips/twohand_0', 'grips/twohand_1', 'grips/twohand_2', 'grips/twohand_3', 'grips/twohand_4'],
	'BD': ['grips/punch_0', 'grips/punch_1', 'grips/punch_2', 'grips/punch_3', 'grips/punch_4'],
	'ST': ['grips/aim_0', 'grips/aim_1', 'grips/aim_2', 'grips/aim_3', 'grips/aim_4'],
	'DV': ['grips/cast_fwd_0', 'grips/cast_fwd_1', 'grips/cast_fwd_3', 'grips/cast_fwd_4', 'grips/cast_fwd_5'],
}
# เฟรมละ MS · pose = ช่องใน POSES · reveal = เอฟเฟกต์เผยจากมือออกไปกี่ส่วน · alpha · flash = สว่างเพิ่ม
# VFX ซ้อน (หน้าเทสวาดด้วยโค้ดทับภาพชีต · kwan เลือก 5 ต.ค.) — สายละ 1 ท่าให้ดูก่อนทาทั้ง 172
VFX_SAMPLES = ['SL01', 'PC06', 'CR04', 'BD10', 'ST05', 'DV08']
MS = 70
TIMELINE = [
	{'pose': 0, 'reveal': 0, 'alpha': 0, 'flash': 0},
	{'pose': 1, 'reveal': 0, 'alpha': 0, 'flash': 0},
	{'pose': 1, 'reveal': 0, 'alpha': 0, 'flash': 0},
	{'pose': 2, 'reveal': 0.3, 'alpha': 1, 'flash': 0},
	{'pose': 2, 'reveal': 0.6, 'alpha': 1, 'flash': 0},
	{'pose': 3, 'reveal': 0.9, 'alpha': 1, 'flash': 0},
	{'pose': 3, 'reveal': 1, 'alpha': 1, 'flash': 0.6},
	{'pose': 3, 'reveal': 1, 'alpha': 1, 'flash': 0.25},
	{'pose': 3, 'reveal': 1, 'alpha': 1, 'flash': 0},
	{'pose': 4, 'reveal': 1, 'alpha': 0.66, 'flash': 0},
	{'pose': 4, 'reveal': 1, 'alpha': 0.33, 'flash': 0},
	{'pose': 0, 'reveal': 0, 'alpha': 0, 'flash': 0},
]
STAGE = (256, 96)    # ผืนอนิเมชัน: Rion มุมขวา เอฟเฟกต์ทางซ้าย
RION_AT = (STAGE[0] - 64, STAGE[1] - 64 - 2)
HAND = (RION_AT[0] + 18, RION_AT[1] + 40)   # มือหน้าของท่าปล่อย (หันซ้าย) — เอฟเฟกต์เริ่มตรงนี้ ยื่นไปทางซ้าย

def col_edges(B, x0, x1, y0, y1):
	frac = B[y0 + 4:y1 - 4, x0:x1].mean(0)
	xs = [x0 + i for i, f in enumerate(frac) if f > 0.85]
	g = []
	for x in xs:
		if g and x - g[-1][-1] <= 3: g[-1].append(x)
		else: g.append([x])
	g = [(a[0], a[-1]) for a in g]
	if len(g) > 1 and g[1][0] - g[0][1] < 20: g = g[1:]      # ขอบแผงด้านนอก
	if len(g) > 1 and g[-1][0] - g[-2][1] < 20: g = g[:-1]
	inner = []
	for i in range(1, len(g) - 1):   # ขอบระหว่างช่องมาเป็นคู่ (ขวาของช่องนี้ · ซ้ายของช่องถัดไป)
		if 4 <= g[i + 1][0] - g[i][1] <= 13 and i + 1 < len(g) - 1: inner.append((g[i], g[i + 1]))
	cells, left = [], g[0][1]
	for r, l in inner:
		cells.append((left + 1, r[0])); left = l[1]
	cells.append((left + 1, g[-1][0]))
	return cells

def cells(a):
	mx = a.max(2); sat = (mx - a.min(2)) / np.maximum(mx, 1)
	B = (mx > 120) & (sat > 0.35)
	for fam, school, first, (x0, x1), rows in PANELS:
		n = first
		for y0, y1 in rows:
			for cx0, cx1 in col_edges(B, x0, x1, y0, y1):
				yield {'code': CODE_OVERRIDE.get(f'{fam}{n:02d}', f'{fam}{n:02d}'), 'family': fam, 'school': school, 'box': [int(cx0), int(y0), int(cx1), int(y1)]}
				n += 1

def effect(cell):
	"""เอฟเฟกต์จากช่อง: แสงเรืองเหนือสีพื้น ไม่เอาป้ายบนและตัวเอกตัวเล็ก · คืน RGBA (ยังไม่พลิก)"""
	h, w = cell.shape[:2]
	body = cell[int(h * HEADER):h - 5, 5:w - 5].astype(float)
	mx = body.max(2); mn = body.min(2); sat = (mx - mn) / np.maximum(mx, 1)
	bg = np.median(body.reshape(-1, 3), axis=0); bgv = bg.max()
	alpha = np.clip((mx - bgv - 25) / 150, 0, 1)
	# ตัวเอกในชีต: ก้อนสีไม่อิ่มตัว (ผิว เสื้อ หมวก เป้ + เส้นขอบเข้ม) รูปร่างคน = สูงเกือบเต็มแถบ แคบ ทึบ
	# (แสงเรืองไม่อิ่มตัวมีแต่เป็นเส้นบาง ๆ ไม่ทึบ · ลูกพลังกลมกว้างเกินคน)
	bh, bw = mx.shape
	hero = (mx > 35) & (mx < 245) & (sat < 0.5)
	hero = ndimage.binary_fill_holes(ndimage.binary_closing(hero, iterations=2))
	core = ndimage.binary_erosion(hero, iterations=2)   # ตัดคอขวดบาง ๆ ที่ต่อตัวเอกเข้ากับเอฟเฟกต์/ตัวเอกอีกตัว
	lab, n = ndimage.label(core)
	cut = np.zeros_like(hero)
	for i, sl in enumerate(ndimage.find_objects(lab), 1):
		hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
		area = (lab[sl] == i).sum()
		if hh >= bh * 0.35 and ww <= bw * 0.3 and area / (hh * ww) > 0.3: cut |= lab == i
	cut = ndimage.binary_dilation(cut, iterations=2) & hero   # คืนขนาดเดิมเฉพาะในส่วนที่เป็นสีตัวเอก
	# ตัวเอกที่ยืนติดเอฟเฟกต์จนแยกก้อนไม่ได้: ในชีตตัวเอกยืนครึ่งซ้ายของช่องเสมอ → แนวคอลัมน์ที่สีตัวคนสูง ≥ 35% ของแถบ
	# กว้าง ≥ 6px ในครึ่งซ้าย = ตัวคน → ลบเฉพาะสีตัวคนในแนวนั้น (แสงที่พาดผ่านยังอยู่)
	cov = hero.mean(0) >= 0.35
	cov[int(bw * 0.55):] = False
	lab1, n1 = ndimage.label(cov)
	for i in range(1, n1 + 1):
		xs = np.where(lab1 == i)[0]
		if len(xs) >= 6: cut[:, xs.min():xs.max() + 1] |= hero[:, xs.min():xs.max() + 1]
	cut = ndimage.binary_dilation(cut, iterations=3)
	alpha[cut] = 0
	a = np.maximum(alpha, 1e-3)[..., None]
	rgb = np.clip(bg + (body - bg) / a, 0, 255)   # ถอดสีพื้นออก → สีจริงของแสง
	out = np.zeros(body.shape[:2] + (4,), np.uint8)
	out[..., :3] = rgb; out[..., 3] = (alpha * 255).round()
	out[out[..., 3] < 12] = 0
	# เศษเล็ก ๆ (ขอบตัวเอกที่เหลือ · จุดรบกวน jpg) ทิ้ง — ไม่งั้นกรอบเอฟเฟกต์กว้างเกินและเลื่อนห่างมือ
	lab, n = ndimage.label(ndimage.binary_dilation(out[..., 3] > 0, iterations=2))
	if n:
		size = ndimage.sum(out[..., 3] > 40, lab, range(1, n + 1))
		small = min(30, size.max() * 0.05)   # เทียบกับก้อนใหญ่สุด — ท่าที่เป็นเส้นบาง ๆ ทั้งท่า (PC30) ไม่หายหมด
		out[np.isin(lab, [i + 1 for i in range(n) if size[i] < small])] = 0
	ys, xs = np.where(out[..., 3] > 0)
	if not len(xs): return None, 0
	return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(cut.sum())

def glow_colors(img, n=3):
	"""สีหลักของแสง 3 สี (สว่างสุดก่อน) — ให้อนุภาค/ประกาย/คลื่นของ VFX ในหน้าเทสใช้สีเดียวกับเอฟเฟกต์"""
	a = np.asarray(img)
	px = a[a[..., 3] > 128][:, :3]
	if len(px) < 8: return ['#ffffff']
	q = Image.fromarray(px[None].astype(np.uint8), 'RGB').quantize(n + 2, Image.Quantize.MEDIANCUT)
	cnt = np.bincount(np.asarray(q).ravel(), minlength=n + 2)
	pal = np.array(q.getpalette()[:3 * (n + 2)]).reshape(-1, 3)
	top = sorted([i for i in np.argsort(cnt)[::-1][:n] if cnt[i]], key=lambda i: -int(pal[i].sum()))
	return ['#%02x%02x%02x' % tuple(int(v) for v in pal[i]) for i in top]

def fit(img):
	s = min(1.0, FX_MAX[0] / img.width, FX_MAX[1] / img.height)
	return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS) if s < 1 else img

def pose_img(fam, i):
	return Image.open(os.path.join(RION, POSES[fam][i] + '.png')).convert('RGBA')

def render(fam, fx, t):
	"""เฟรมเดียว (ภาพตรวจ) — จังหวะ/ตำแหน่งเดียวกับ sheetSkillView() ในหน้าเทส · หน้าเทสวาดสว่างวาบแบบบวกแสง ส่วนนี้ใช้เพิ่มความสว่าง"""
	can = Image.new('RGBA', STAGE, (0, 0, 0, 0))
	if t['alpha'] > 0 and t['reveal'] > 0:
		e = fx.copy()
		if t['flash']: e = ImageEnhance.Brightness(e).enhance(1 + t['flash'])
		cw = max(1, round(e.width * t['reveal']))
		e = e.crop((e.width - cw, 0, e.width, e.height))   # เผยจากมือ (ขวา) ออกไปทางซ้าย
		al = np.asarray(e).copy(); al[..., 3] = (al[..., 3] * t['alpha']).astype(np.uint8); e = Image.fromarray(al, 'RGBA')
		can.alpha_composite(e, (max(0, HAND[0] - cw), max(0, HAND[1] - fx.height // 2)))
	can.alpha_composite(pose_img(fam, t['pose']), RION_AT)
	return can

def main():
	a = np.asarray(Image.open(SRC).convert('RGB')).astype(int)
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	items = []; previews = []
	for c in cells(a):
		x0, y0, x1, y1 = c['box']; cell = a[y0:y1, x0:x1]
		Image.fromarray(cell.astype(np.uint8)).save(os.path.join(OUT, c['code'] + '_cell.png'))
		fx, cut = effect(cell)
		if fx is None: print('ไม่มีเอฟเฟกต์', c['code']); continue
		fxi = fit(Image.fromarray(fx, 'RGBA').transpose(Image.FLIP_LEFT_RIGHT))
		fxi.save(os.path.join(OUT, c['code'] + '_fx.png'))
		c.update(fx_size=list(fxi.size), hero_px_removed=cut, colors=glow_colors(fxi))
		items.append(c)
		if c['code'] in ('SL01', 'SL20', 'PC06', 'CR04', 'BD10', 'ST05', 'DV08', 'SL30'): previews.append((c['family'], fxi))
	cnt = {}
	for c in items: cnt[c['family']] = cnt.get(c['family'], 0) + 1
	json.dump({'_doc': 'ตัดจาก docs/art-bible/compendium/skill_sprite_sheet.jpg ด้วย tools/sprites/skill_sheet_cut.py · ร่าง ยังไม่เข้าเกม · '
		'รหัส = ลำดับตำแหน่งในแผง (ป้ายในชีตบางช่องผิด) · หน้าเทสวาดตาม timeline/poses/stage ชุดนี้',
		'vfx_samples': VFX_SAMPLES, 'ms': MS, 'timeline': TIMELINE, 'poses': POSES, 'stage': STAGE, 'rion_at': RION_AT, 'hand': HAND, 'items': items},
		open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	keys = [3, 5, 6, 8, 10]
	pv = Image.new('RGBA', (STAGE[0] * len(keys), STAGE[1] * len(previews)), (58, 62, 70, 255))
	for r, (fam, fx) in enumerate(previews):
		for c, k in enumerate(keys): pv.alpha_composite(render(fam, fx, TIMELINE[k]), (c * STAGE[0], r * STAGE[1]))
	pv.resize((pv.width * 2, pv.height * 2), Image.NEAREST).save(os.path.join(ROOT, 'docs/art-bible/compendium/skill_anim_preview.png'))
	print(len(items), 'ท่า ·', cnt)

if __name__ == '__main__':
	main()
