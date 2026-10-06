# tools/sprites/rion_rig.py — ริก Rion + อาวุธจากชีต "Weapon Collection" (kwan 6 ต.ค. "เอา RIG มาช่วย" → เลือกข้อ 1 Rion + อาวุธทั้งชีต)
#
#   python3 tools/sprites/rion_rig.py            ตัวอย่าง (SAMPLES)
#   python3 tools/sprites/rion_rig.py --all      ทุกชิ้นในชีต (หลัง kwan อนุมัติตัวอย่าง)
#
# ริก = ใช้ตอนอบภาพ ไม่ใช่หมุนสไปรต์ตอนเล่น (หมุนพิกเซลตอนเล่นแล้วเส้นหยัก) → ผลเป็นเฟรมพิกเซลคมทุกเฟรม
#   กระดูก: ลำตัว (เลื่อน dx · ยุบ dy) → ไหล่ → ศอก → มือ (ตำแหน่งจากคีย์เฟรม แทรกค่าระหว่างคีย์) → อาวุธติดมือ (มุมจากคีย์เฟรม หมุนทางสั้น)
#   ตัว Rion = west.png ลบแขนหน้าเดิม แล้ววาดแขนใหม่ทุกเฟรม (rion_grips.draw_arm)
#   อาวุธ: ไอคอน 32px จาก weapons_sheet_cut.py · แกน + จุดจับหาอัตโนมัติ (แกนหลักของรูป · ด้าม = ปลายล่างซ้าย ในชีตวางเฉียงขึ้นขวาทุกชิ้น)
#     หมุนแบบเดียวกับ weapons_held.py (ขยาย 8 เท่า → หมุน nearest → ย่อด้วยสีส่วนใหญ่ → เส้นขอบใหม่) · ยาว = ความยาวรูป × LEN_K ของสาย
#   สาย: SL ฟันมือเดียว · PC แทงพุ่ง · CR สองมือเหวี่ยง · ST ประทับยิง · BD ถุงมือสวมมือ ต่อยตรง · DV โดรนลอยข้างตัว Rion ชี้สั่ง · W ตามสายที่ใกล้
#   ฟาดเร็ว (มุมเปลี่ยนเกิน SMEAR_DEG ใน 1 เฟรม) = รอยปลายอาวุธ 2 เส้นสีอ่อน (smear แบบภาพวาดมือ)
# ค่าทั้งหมดเป็นค่าภาพ ไม่ใช่ค่าเกม
# ออก assets/sprites/rion_rig_draft/<code>_<i>.png (64x64 · .gdignore · ร่าง) + index.json · ภาพตรวจ docs/art-bible/weapons/rion_rig_preview.png
import json, math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rion_grips as G
import weapons_held as WH
import poses_anim as PA
import rion_anim as RA
import poses64 as P64

ROOT = G.ROOT
SHEET = os.path.join(ROOT, 'assets/sprites/weapons_sheet_draft')
OUT = os.path.join(ROOT, 'assets/sprites/rion_rig_draft')
N = 12
SMEAR_DEG = 40
SMEAR_COL = (236, 236, 244, 255)
# คีย์เฟรม: (เวลา 0–1, ตัวเลื่อน dx, ตัวยุบ dy, ศอก, มือ, มุมอาวุธ) · มุมจอ 0 = ชี้ขวา 90 = ขึ้น 180 = หน้า (ซ้าย)
# ท่าละ: ยืน → ง้าง (ค้างนิดให้ผู้เล่นอ่านออก) → ฟาด (เร็ว 1–2 เฟรม) → ตามแรง → คืน
KEYS = {
	'slash': [(0.0, 0, 0, (24, 44), (22, 45), 125), (0.12, 0, 0, (24, 44), (22, 45), 125), (0.38, 2, 1, (31, 41), (34, 38), 12),   # ง้างระดับไหล่ไปหลัง (มือสูงระดับหัวแล้วใบมีดหายหลังหมวก)
		(0.5, -4, 0, (20, 41), (16, 42), 185), (0.62, -4, 0, (21, 45), (18, 48), 240), (1.0, 0, 0, (24, 44), (22, 45), 125)],
	'thrust': [(0.0, 0, 0, (24, 44), (23, 47), 105), (0.12, 0, 0, (24, 44), (23, 47), 105), (0.38, 3, 1, (29, 43), (31, 42), 182),
		(0.5, -5, 0, (19, 41), (13, 41), 180), (0.66, -5, 0, (19, 41), (14, 41), 180), (1.0, 0, 0, (24, 44), (23, 47), 105)],
	'swing2': [(0.0, 0, 0, (23, 46), (21, 48), 250), (0.12, 0, 0, (23, 46), (21, 48), 250), (0.38, 3, 1, (32, 40), (33, 34), 20),   # ยืน = หัวค้อนพักพื้นข้างหน้า (พาดบ่าแล้วหายหลังเป้)
		(0.5, -4, 0, (21, 42), (17, 43), 172), (0.62, -4, 0, (21, 44), (17, 45), 200), (0.78, -1, 0, (23, 47), (21, 49), 250), (1.0, 0, 0, (23, 46), (21, 48), 250)],
	'aim': [(0.0, 0, 0, (24, 45), (22, 47), 195), (0.2, 0, 0, (22, 42), (19, 42), 182), (0.4, -2, 0, (20, 41), (15, 41), 180),
		(0.48, 1, 0, (21, 40), (17, 40), 168), (0.6, -1, 0, (20, 41), (15, 41), 180), (1.0, 0, 0, (24, 45), (22, 47), 195)],
	'punch': [(0.0, 0, 0, (24, 44), (22, 41), 180), (0.12, 0, 0, (24, 44), (22, 41), 180), (0.38, 2, 1, (30, 44), (30, 41), 180),
		(0.5, -4, 0, (20, 41), (14, 41), 180), (0.66, -4, 0, (20, 41), (15, 41), 180), (1.0, 0, 0, (24, 44), (22, 41), 180)],
	'point': [(0.0, 0, 0, (24, 45), (23, 47), 0), (0.25, 0, 0, (24, 41), (23, 37), 0), (0.45, -2, 0, (20, 41), (15, 40), 0),
		(0.7, -2, 0, (20, 41), (15, 40), 0), (1.0, 0, 0, (24, 45), (23, 47), 0)],
}
# สรีระต่อคีย์ (kwan 6 ต.ค. "ร่างกายแข็ง ไม่เป็นธรรมชาติ ปรับสรีระให้เข้ากับทุกแอกชั่น") — เวลาเดียวกับ KEYS ทีละตัว
#   lean เอนช่วงบน (+ = ไปหลัง/ขวา − = โถมไปหน้า) · sq ย่อเข่า (แถว) · st ก้าวขา (+1 = ขาหน้าก้าวไปหน้าเต็ม −1 = ถอยขาหน้า) ·
#   ch อกลง · hd หัวลง (หัวตามทีหลังอก) · hx หัวไปหน้า (−) · pk เป้กระเด้ง (+ ลง) · ทุกท่าหายใจเบา ๆ ตอนยืน + กะพริบตาตอนฟาด
Z = dict(lean=0, sq=0, st=0.25, ch=0, hd=0, hx=0, pk=0)
def B(**k): return dict(Z, **k)
BODY = {
	'slash': [Z, Z, B(lean=3, sq=2, st=-0.5, ch=1, pk=-1), B(lean=-3, sq=2, st=1, hd=1, hx=-1, pk=1), B(lean=-2, sq=1, st=1, hd=1, pk=1), Z],
	'thrust': [Z, Z, B(lean=3, sq=1, st=-0.6, ch=1, pk=-1), B(lean=-4, sq=2, st=1, hx=-1, pk=1), B(lean=-3, sq=2, st=1, hd=1), Z],
	'swing2': [Z, Z, B(lean=4, sq=2, st=-0.5, ch=1, pk=-1), B(lean=-4, sq=3, st=1, hd=1, hx=-1, pk=1), B(lean=-3, sq=3, st=1, hd=1, pk=1), B(lean=-1, sq=1, st=0.6), Z],
	'aim': [Z, B(sq=1, st=0.6), B(lean=1, sq=1, st=0.8, hx=-1), B(lean=3, sq=1, st=0.8, hd=1, pk=1), B(lean=1, sq=1, st=0.8, hx=-1), Z],
	'punch': [B(sq=1, st=0.5), B(sq=1, st=0.5), B(lean=2, sq=2, st=-0.3, ch=1, pk=-1), B(lean=-3, sq=1, st=1, hx=-1, pk=1), B(lean=-2, sq=1, st=1, hd=1), B(sq=1, st=0.5)],
	'point': [Z, B(lean=1, st=0.4, ch=-1), B(lean=-2, sq=1, st=0.9, hx=-1, pk=1), B(lean=-2, sq=1, st=0.9), Z],
}
# มือหลังจับด้ามด้วยในท่าสองมือ (ชดเชยจากมือหน้า) · ประทับปืน มือหลังประคองใต้ลำ
BACK = {'swing2': (5, 0), 'aim': (5, 1)}
BEHIND_ANG = (15, 110)   # อาวุธชี้ขึ้น/ไปหลัง (มุมจอในช่วงนี้) = อยู่หลังตัว (พาดบ่า · ง้าง) · รอบแรกใช้ช่วงเวลา แล้วอาวุธหายหลังหัว
FAM = {'SL': 'slash', 'PC': 'thrust', 'CR': 'swing2', 'ST': 'aim', 'BD': 'punch', 'DV': 'point'}
W_FAM = {'W301': 'SL', 'W302': 'CR', 'W303': 'SL', 'W304': 'CR', 'W305': 'SL', 'W306': 'ST', 'W307': 'CR', 'W308': 'CR', 'W309': 'CR', 'W310': 'ST'}
LEN_K = {'SL': 0.72, 'PC': 0.95, 'CR': 0.8, 'ST': 0.6}   # ความยาวในมือ / ความยาวรูปในไอคอน 32px
SAMPLES = ['SL01', 'SL30', 'PC01', 'PC30', 'CR01', 'CR30', 'ST01', 'ST30', 'BD01', 'BD30', 'DV07', 'DV29', 'W301', 'W309']

def ease(p): return p * p * (3 - 2 * p)

def lerp_ang(a, b, t):
	d = (b - a + 540) % 360 - 180; return a + d * t

def pose_at(group, t):
	"""คืน (dx, dy, ศอก, มือ, มุม, สรีระ) ที่เวลา t · ช่วงสั้น (ฟาด ≤ 0.15) = เร็วคงที่ · ช่วงยาว = นุ่มหัวท้าย"""
	ks, bs = KEYS[group], BODY[group]
	for k in range(len(ks) - 1):
		(t0, *a), (t1, *b) = ks[k], ks[k + 1]
		if t0 <= t <= t1:
			u = ease((t - t0) / max(1e-6, t1 - t0)) if t1 - t0 > 0.15 else (t - t0) / max(1e-6, t1 - t0)
			lp = lambda x, y: x + (y - x) * u
			body = {n: lp(bs[k][n], bs[k + 1][n]) for n in Z}
			return (lp(a[0], b[0]), lp(a[1], b[1]), (lp(a[2][0], b[2][0]), lp(a[2][1], b[2][1])), (lp(a[3][0], b[3][0]), lp(a[3][1], b[3][1])), lerp_ang(a[4], b[4], u), body)
	return pose_at(group, ks[-1][0])

ri = lambda v: int(round(v))
HIP, SQ_AT, LEAN_TOP = PA.HIP, 57, 8

def stance(im, st, kmax=4):
	"""ขาหน้า/หลังเฉือนตามก้าว (เหมือน poses64.legs_side แต่ไม่ยกเท้า ไม่เด้งตัว) · หันซ้าย ขาหน้า = x < 30"""
	RA.SIZE[0] = 64; k = ri(kmax * st)
	if not k: return im
	upper = RA.region(im, lambda x, y: y < HIP); front = RA.region(im, lambda x, y: y >= HIP and x < 30); back = RA.region(im, lambda x, y: y >= HIP and x >= 30)
	f = RA.blank(); RA.paste(f, RA.shear(back, k, HIP, 63)); RA.paste(f, RA.shear(front, -k, HIP, 63)); RA.paste(f, upper); return f

def body_pose(im, b):
	"""ลำตัวตามสรีระ: ก้าวขา → ย่อเข่า → เอน → อก → หัว → เป้ (ลำดับเดียวกับ poses64.rion_frame)"""
	im = stance(im, b['st'])
	if ri(b['sq']): im = PA.squash(im, SQ_AT, ri(b['sq']))
	if ri(b['lean']): im = PA.lean(im, b['lean'], HIP, LEAN_TOP)
	ch, hd = ri(b['ch']), ri(b['hd'])
	if ch: im = PA.shift_part(im, lambda x, y: y < 46, 0, ch)
	if hd or ri(b['hx']): im = PA.shift_part(im, lambda x, y: y < 31 + ch, ri(b['hx']), hd, keep=True)
	if ri(b['pk']): im = PA.shift_part(im, P64.PACK, 0, ri(b['pk']), keep=True)
	return im

def body_pt(pt, b):
	"""จุดบนลำตัว (ไหล่/ศอก/มือ) หลังผ่าน body_pose — ให้แขนกับอาวุธวาดตามตัวที่เอน/ย่อแล้ว"""
	x, y = pt; n = ri(b['sq'])
	if n and y < SQ_AT: y += n
	if ri(b['lean']) and y < HIP: x += ri(b['lean'] * (HIP - y) / (HIP - LEAN_TOP))
	if ri(b['ch']) and y < 46: y += ri(b['ch'])
	return (x, y)

def axis(icon):
	"""แกนหลักของรูป (PCA ของพิกเซลทึบ) → (จุดจับ, ทิศในไอคอน องศา, ความยาวรูป) · ด้าม = ปลายล่างซ้าย เข้ามา 3 จุด"""
	a = np.asarray(icon)[..., 3] > 0; ys, xs = np.nonzero(a)
	pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0); u, s, vt = np.linalg.svd(pts - c, full_matrices=False); d = vt[0]
	if d[0] < 0: d = -d                                   # ชี้ขวา
	proj = (pts - c) @ d; lo, hi = proj.min(), proj.max()
	grip = c + d * (lo + 3)
	ang = math.degrees(math.atan2(-d[1], d[0]))          # มุมจอ (y ลง)
	return (float(grip[0]), float(grip[1])), ang, float(hi - lo)

def weapon_sprite(icon, grip, idir, length, angle):
	"""หมุนรอบจุดจับให้ปลายชี้ angle · ยาว length · คืน (ภาพ, จุดจับในภาพ)"""
	K = 8; s = length / max(1.0, axis(icon)[2])
	big = icon.resize((32 * K, 32 * K), Image.NEAREST); pad = 32 * K * 2
	can = Image.new('RGBA', (pad, pad), (0, 0, 0, 0)); can.paste(big, (int(pad / 2 - grip[0] * K), int(pad / 2 - grip[1] * K)), big)
	if 90 < angle % 360 < 270:   # ชี้ไปซ้าย: พลิกแทนการหมุนกลับหัว (ลายบนใบมีด/ปืนไม่กลับหัว)
		can = can.transpose(Image.FLIP_LEFT_RIGHT); rot = angle - 180 + idir   # พลิกแล้วทิศรูป = 180 − idir
	else: rot = angle - idir
	can = can.rotate(rot, Image.NEAREST)
	small = WH.mode_downscale(can, max(1, round(K / s)))
	return WH.outline(small), (small.size[0] / 2.0, small.size[1] / 2.0)

def glove(frame, icon, hand, fist, size=13):
	"""ถุงมือ/สนับมือ: ย่อทั้งชิ้นให้ด้านยาว = size (รอบแรก ~9 จุดตาม weapons_held แล้วมองแทบไม่เห็น) สวมทับมือ · ต่อยอยู่ = หมุนให้ชี้หน้า"""
	g = icon.crop(icon.getbbox())
	if fist: g = g.rotate(45, Image.NEAREST, expand=True)
	big = g.resize((g.width * 8, g.height * 8), Image.NEAREST); k = max(1, round(max(g.size) * 8 / size))
	small = WH.outline(WH.mode_downscale(big, k)); frame.alpha_composite(small, (int(hand[0] - small.width / 2), int(hand[1] - small.height / 2)))

def tip(hand, angle, L): a = math.radians(angle); return (hand[0] + math.cos(a) * L, hand[1] - math.sin(a) * L)

def smear(im, hand, a0, a1, L):
	"""รอยปลายอาวุธระหว่างมุมเก่า → ใหม่ ที่รัศมี 0.95L และ 0.7L (เว้นช่วงใกล้มุมใหม่ ไม่ทับตัวอาวุธ)"""
	p = im.load(); d = (a1 - a0 + 540) % 360 - 180; n = max(4, int(abs(d) / 4))
	for r in (0.95, 0.7):
		for i in range(n):
			t = i / n
			if t > 0.85: break
			x, y = tip(hand, a0 + d * t, L * r); x, y = int(round(x)), int(round(y))
			if 0 <= x < 64 and 0 <= y < 64 and not p[x, y][3]: p[x, y] = SMEAR_COL

def render(code, icon):
	fam = W_FAM.get(code, code[:2]); group = FAM[fam]; base = G.remove_front_arm(Image.open(G.SRC).convert('RGBA'))
	frames = []; prev = None
	grip, idir, ilen = axis(icon) if fam not in ('BD', 'DV') else ((0, 0), 0, 0)
	L = max(12.0, ilen * LEN_K.get(fam, 0.8))
	for i in range(N):
		t = i / N; dx, dy, elbow, hand, ang, bd = pose_at(group, t)
		bd['ch'] += 0.6 * math.sin(t * math.tau) if t < 0.15 or t > 0.85 else 0   # หายใจตอนยืน
		dxi, dyi = int(round(dx)), int(round(dy))
		raw = base.copy()
		if 0.46 <= t < 0.54: P64.blink(raw)   # กะพริบ/หรี่ตาตอนออกแรง
		body = G.shift(body_pose(raw, bd), dxi)
		if dyi: body = body.transform(body.size, Image.AFFINE, (1, 0, 0, 0, 1, -dyi), Image.NEAREST)
		mv = lambda q: (lambda r: (ri(r[0]) + dxi, ri(r[1]) + dyi))(body_pt(q, bd))
		sh, el, hd = mv(G.SH_F), mv(elbow), mv(hand)
		el = P64.ik(sh, hd) if fam not in ('BD', 'DV') else el; el = (ri(el[0]), ri(el[1]))   # ศอกหาเองจากไหล่-มือ (แขนยาวคงที่ ไม่ยืดหด)
		out = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
		if fam == 'DV':   # โดรนลอยหลังไหล่ → พุ่งไปหน้าตอน Rion ชี้ → กลับ
			k = math.sin(min(1, max(0, (t - 0.2) / 0.5)) * math.pi)
			dr = icon.crop(icon.getbbox())
			dr = dr.resize((max(1, dr.width * 3 // 4), max(1, dr.height * 3 // 4)), Image.NEAREST)   # ลอยหลังไหล่ ไม่ทับหมวก
			x = int(round(56 - k * 46)) - dr.width // 2; y = int(round(12 + math.sin(t * math.tau * 2) * 1.5 + k * 14)) - dr.height // 2
			out.alpha_composite(body); P64.draw_arm_soft(out, sh, el, hd); out.alpha_composite(WH.outline(dr), (x, y))
		elif fam == 'BD':
			out.alpha_composite(body); P64.draw_arm_soft(out, sh, el, hd); glove(out, icon, hd, 0.42 <= t <= 0.7)
		else:
			spr, (cx, cy) = weapon_sprite(icon, grip, idir, L, ang); at = (int(round(hd[0] - cx)), int(round(hd[1] - cy)))
			behind = BEHIND_ANG[0] < ang % 360 < BEHIND_ANG[1] or math.cos(math.radians(ang)) > 0.05   # ชี้ไปหลัง (ขวา) ทุกมุม = หลังตัว (ค้อนช้อนผ่านล่างไปหลังเคยลอยทับกลางตัว)
			if behind: out.alpha_composite(spr, at)
			out.alpha_composite(body)
			if group in BACK:
				bx, by = BACK[group]; sb = mv(G.SH_B); hb = (hd[0] + bx, hd[1] + by); eb = P64.ik(sb, hb); G.draw_arm(out, sb, (ri(eb[0]), ri(eb[1])), hb, back=True)
			if not behind: out.alpha_composite(spr, at)
			P64.draw_arm_soft(out, sh, el, hd)
			if prev is not None and abs((ang - prev + 540) % 360 - 180) > SMEAR_DEG: smear(out, hd, prev, ang, L)
			prev = ang
		frames.append(out)
	return frames

def main():
	idx = {x['code']: x for x in json.load(open(os.path.join(SHEET, 'index.json'), encoding='utf-8'))['items']}
	codes = list(idx) if '--all' in sys.argv else [c for c in SAMPLES if c in idx]
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	items = []; rows = []
	for code in codes:
		icon = Image.open(os.path.join(SHEET, code + '.png')).convert('RGBA')
		fr = render(code, icon)
		for i, im in enumerate(fr): im.save(os.path.join(OUT, f'{code}_{i}.png'))
		fam = W_FAM.get(code, code[:2])
		items.append({'code': code, 'family': idx[code]['family'], 'pose': FAM[fam], 'name': idx[code].get('name'), 'frames': N}); rows.append(fr)
	json.dump({'_doc': 'Rion + อาวุธจากชีต อบด้วยริก (tools/sprites/rion_rig.py) · ร่าง ยังไม่เข้าเกม · เฟรม 0 ยืน · ง้าง ~4 · ฟาด ~6 · คืน 11',
		'n': N, 'items': items}, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	pv = Image.new('RGBA', (64 * N, 64 * len(rows)), (58, 62, 70, 255))
	for r, fr in enumerate(rows):
		for i, im in enumerate(fr): pv.alpha_composite(im, (64 * i, 64 * r))
	pv.resize((pv.width * 2, pv.height * 2), Image.NEAREST).save(os.path.join(ROOT, 'docs/art-bible/weapons/rion_rig_preview.png'))
	print(len(items), 'ชิ้น ×', N, 'เฟรม')

if __name__ == '__main__':
	main()
