# tools/sprites/poses64.py — ทุกคลิปในแท็บ "ท่าขยับ" แบบ 64 เฟรม (kwan สั่ง 5 ต.ค. 2026 · ร่าง · ไม่แตะสไปรต์ในเกม)
# แต่ละท่าเขียนเป็น "ค่าต่อเนื่องตามเวลา" (ระยะก้าว · ตัวขึ้นลง · เอน · ย่อ · หัว · ศอก/มือ · มุมมีด · หมุนตัว · อีโมต)
# แล้วสุ่มที่ t = i/64 ทั้ง 64 จุด ปัดเป็นพิกเซลเต็ม → เฟรมที่ปัดแล้วเหมือนกันเก็บไฟล์เดียว (index.json บอกลำดับ + จำนวนภาพไม่ซ้ำ)
# ท่าเดิมทั้งหมดมาจาก poses_anim.py / rion_anim.py — ที่นี่แค่ทำให้ต่อเนื่อง
# ผล: assets/sprites/poses64_draft/<id>_<u>.png + index.json
import json, math, os
from PIL import Image, ImageDraw
import rion_grips as G
import rion_anim as RA
import poses_anim as PA
import rion_parts as RP

ROOT = G.ROOT
OUT = os.path.join(ROOT, 'assets/sprites/poses64_draft')
N = 64
HIP, TOP, DHIP = PA.HIP, PA.TOP, PA.DHIP
TAU = 2 * math.pi

def kf(t, keys):
	"""ค่าตามคีย์เฟรม [(t, v), ...] แบบเส้นตรง · v เป็นตัวเลขหรือ tuple"""
	if t <= keys[0][0]: return keys[0][1]
	for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
		if t <= t1:
			u = 0 if t1 == t0 else (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u)      # นุ่มหัวท้าย
			return tuple(a + (b - a) * u for a, b in zip(v0, v1)) if isinstance(v0, tuple) else v0 + (v1 - v0) * u
	return keys[-1][1]
sin = lambda t, n=1: math.sin(TAU * n * t)
cos = lambda t, n=1: math.cos(TAU * n * t)
ri = lambda v: int(round(v))

# ── ขา (เดิน/วิ่ง) ตามเฟส ──
def legs_side(im, phase, facing_left, split, hip, foot, kmax, size):
	RA.SIZE[0] = size
	upper = RA.region(im, lambda x, y: y < hip)
	front = RA.region(im, lambda x, y: y >= hip and (x < split if facing_left else x >= split))
	back = RA.region(im, lambda x, y: y >= hip and (x >= split if facing_left else x < split))
	sg = -1 if facing_left else 1; t = phase % 1
	k = ri(kmax * cos(t)); b = ri(sin(t, 2))
	f = RA.blank()
	RA.paste(f, RA.shear(back, -sg * k, hip, foot), 0, -1 if 0.18 < t < 0.32 else 0)
	RA.paste(f, RA.shear(front, sg * k, hip, foot), 0, -1 if 0.68 < t < 0.82 else 0)
	if b > 0: RA.paste(f, RA.region(upper, lambda x, y: y >= hip - 1)); RA.paste(f, upper, 0, 1)
	elif b < 0: RA.bob(f, upper, hip)
	else: RA.paste(f, upper)
	return f

def legs_front(im, phase, split, hip, cut0, foot_end, size):
	RA.SIZE[0] = size
	upper = RA.region(im, lambda x, y: y < hip)
	L = RA.region(im, lambda x, y: y >= hip and x < split); Rr = RA.region(im, lambda x, y: y >= hip and x >= split)
	sv = sin(phase % 1); d = ri(2 * abs(sv))
	f = RA.blank(); RA.paste(f, upper)
	RA.paste(f, RA.bend(L, cut0, cut0 + d, foot_end) if sv > 0 and d else L)
	RA.paste(f, RA.bend(Rr, cut0, cut0 + d, foot_end) if sv < 0 and d else Rr)
	return f

def turn(im, s):
	"""หันตัว: บีบแนวนอนรอบแกนกลาง s = 0..1"""
	w = im.size[0]; nw = max(2, ri(w * s))
	if nw == w: return im
	sq = im.resize((nw, im.size[1]), Image.NEAREST); out = Image.new('RGBA', im.size); out.alpha_composite(sq, ((w - nw) // 2, 0)); return out

def rot_ground(im, ang, pivot, ground):
	"""หมุนรอบ pivot แล้ววางให้ขอบล่างแตะพื้น (ใช้ตอนล้ม/ลุก)"""
	if abs(ang) < 0.5: return im
	r = im.rotate(-ang, resample=Image.NEAREST, center=pivot); bb = r.getbbox()
	out = Image.new('RGBA', im.size); out.alpha_composite(r, (0, 0)) if not bb else out.paste(r, (0, ground - bb[3]), r); return out

# ── ตัวเรนเดอร์ Rion: params → ภาพ 64x76 ──
def _rot_pt(pt, deg, c):
	a = math.radians(deg); x, y = pt[0] - c[0], pt[1] - c[1]
	return (c[0] + x * math.cos(a) + y * math.sin(a), c[1] - x * math.sin(a) + y * math.cos(a))
BOW_PIVOT = (31, HIP)
def bow(im, deg):
	"""โค้งตัว: หมุนช่วงบน (เหนือ HIP) รอบสะโพก · + = ก้มไปหน้า (หันซ้าย) · ขาอยู่ที่เดิม"""
	upper = PA.part(im, lambda x, y: y < HIP); lower = PA.part(im, lambda x, y: y >= HIP)
	return PA.put(lower, upper.rotate(deg, Image.NEAREST, center=BOW_PIVOT))
def body_pt(pt, p):
	"""จุดบนลำตัว (ไหล่ · มือที่ท่ากำหนด) หลังขยับตัวแบบเดียวกับ rion_frame: ย่อ → เอน → โค้ง → อก"""
	x, y = pt; n = ri(p.get('squash', 0))
	if n and y < p.get('sq_at', 57): y += n
	if ri(p.get('lean', 0)) and y < HIP: x += ri(p['lean'] * (HIP - y) / (HIP - 8))
	if abs(p.get('bow', 0)) >= 1 and y < HIP: x, y = _rot_pt((x, y), p['bow'], BOW_PIVOT)
	if ri(p.get('chest', 0)) and y < 46: y += ri(p['chest'])
	return (x, y)

FLOP_DIRS = ['south', 'west', 'north', 'east']
def rion_frame(p):
	d = p.get('dir', 'west'); img = PA.rion(p.get('img', d))
	if p.get('blink') and d == 'west' and not p.get('img'): blink(img)
	if p.get('arm_hand') and not (p.get('arm') or p.get('barm')) and d == 'west' and not p.get('img'):   # แขนแกว่ง (ชั้นสมจริง) · ศอกจาก ik
		img = G.remove_front_arm(img); hx, hy = reach(G.SH_F, p['arm_hand']); e = ik(G.SH_F, (hx, hy)); draw_arm_soft(img, G.SH_F, (ri(e[0]), ri(e[1])), (ri(hx), ri(hy)))
	if p.get('arm_swing') is not None and d in ('south', 'north', 'east') and not p.get('img'):   # แกว่งแขนทิศอื่น (rion_parts: แยกชิ้นแขนแล้วเฉือน)
		img = RP.swing_arms(img, d, p['arm_swing'], p.get('arm_lift', 1.0))
	arms = (p.get('arm') or p.get('barm')) and d == 'west' and not p.get('img')
	if arms: img = G.remove_front_arm(img)   # แขนที่ท่ากำหนดเอง: วาดหลังขยับตัวเสร็จ (ด้านล่าง) ไหล่จึงอยู่ตามตัวที่ย่อ/เอน/โค้งแล้ว
	if p.get('walk') is not None:
		img = legs_side(img, p['walk'], d == 'west', 30 if d == 'west' else 34, HIP, 63, p.get('kmax', 4), 64) if d in ('west', 'east') \
			else legs_front(img, p['walk'], 32 if d == 'south' else 31, HIP, 57, 61, 64)
	if p.get('feet'): f = ri(p['feet']); img = PA.put(PA.put(PA.part(img, lambda x, y: y < 59), PA.part(img, lambda x, y: y >= 59 and x < 32), -f, 0), PA.part(img, lambda x, y: y >= 59 and x >= 32), f, 0)
	if ri(p.get('squash', 0)): img = PA.squash(img, p.get('sq_at', 57), ri(p['squash']))
	if ri(p.get('lean', 0)): img = PA.lean(img, p['lean'], HIP, 8)
	if abs(p.get('bow', 0)) >= 1: img = bow(img, p['bow'])
	ch, hd = ri(p.get('chest', 0)), ri(p.get('head', 0))
	if ch: img = PA.shift_part(img, lambda x, y: y < 46, 0, ch)
	if hd > ch: img = PA.shift_part(img, lambda x, y: y < 31 + ch, 0, hd - ch)
	if ri(p.get('hx', 0)) or ri(p.get('hy', 0)): img = PA.shift_part(img, lambda x, y: y < 31, ri(p.get('hx', 0)), ri(p.get('hy', 0)))
	if arms:   # ไหล่/มือผ่านการขยับตัวชุดเดียวกัน → มือดึงเข้าไม่เกินความยาวแขน (REACH) → ศอกจาก ik
		if p.get('barm'):
			b = p['barm']; sb = body_pt(G.SH_B, p); hb = reach(sb, body_pt((b[2], b[3]), p)); eb = ik(sb, hb)
			G.draw_arm(img, (ri(sb[0]), ri(sb[1])), (ri(eb[0]), ri(eb[1])), (ri(hb[0]), ri(hb[1])), back=True, w_upper=3)
		a = p.get('arm') or (24, 44, 23, 47); sf = body_pt(G.SH_F, p); hf = reach(sf, body_pt((a[2], a[3]), p)); ef = ik(sf, hf)
		draw_arm_soft(img, (ri(sf[0]), ri(sf[1])), (ri(ef[0]), ri(ef[1])), (ri(hf[0]), ri(hf[1])))
		if p.get('item'): PA.item(img, ri(hf[0]), ri(hf[1]) - 1)
	if ri(p.get('lag_hx', 0)) or ri(p.get('lag_hy', 0)): img = PA.shift_part(img, lambda x, y: y < 31 + ch, ri(p.get('lag_hx', 0)), ri(p.get('lag_hy', 0)), keep=True)   # หัวตามแรงเฉื่อย
	if ri(p.get('pack', 0)) and d in ('west', 'east') and not p.get('img'):
		img = PA.shift_part(img, PACK if d == 'west' else (lambda x, y: PACK(63 - x, y)), 0, ri(p['pack']), keep=True)   # เป้ตามแรงเฉื่อย
	if p.get('turn', 1) < 1: img = turn(img, p['turn'])
	if abs(p.get('rot', 0)) >= 0.5: img = rot_ground(img, p['rot'], (32, 36), 62)   # หมุนรอบกลางตัว (แบบเดียวกับท่าล้มเดิม west_k1) ไม่ล้นขอบ
	c = PA.blank(64, 64 + TOP)
	if p.get('shadow'): PA.shadow(c, 32, 62 + TOP, ri(p['shadow']))
	if p.get('crate') is not None: PA.crate(c, ri(p['crate']))
	if p.get('ghost'): PA.put(c, PA.rion(d), 0, TOP, p['ghost'])
	PA.put(c, img, ri(p.get('dx', 0)), TOP + ri(p.get('dy', 0)))
	for g in p.get('glyphs', []):
		if g[3] > 8: PA.glyph(c, g[0], ri(g[1]), ri(g[2]), ri(g[3]))
	if p.get('fx'): p['fx'](c)
	return c

# ── ตัวเรนเดอร์หมา: params → ภาพ 48x48 ──
HEAD_W = lambda x, y: x < 19 and y < 27
TAIL = {'west': lambda x, y: x >= 26 and y < 22, 'east': lambda x, y: x <= 7 and y < 22, 'north': lambda x, y: y < 14}
def dog_frame(p):
	d = p.get('dir', 'west'); img = PA.dog(d)
	if p.get('walk') is not None:
		img = legs_side(img, p['walk'], d == 'west', 17, DHIP, 32, 2, 34) if d in ('west', 'east') \
			else legs_front(img, p['walk'], 16 if d == 'south' else 18, 24, 27, 32, 34)
	if ri(p.get('rear', 0)):      # นั่ง: ส่วนหลังยุบ
		n = ri(p['rear']); img = PA.put(PA.part(img, lambda x, y: x < 19), PA.squash(PA.part(img, lambda x, y: x >= 19), 24, n))
	if ri(p.get('front', 0)):     # ก้มชวนเล่น: ส่วนหน้ายุบ
		n = ri(p['front']); img = PA.put(PA.part(img, lambda x, y: x >= 19), PA.squash(PA.part(img, lambda x, y: x < 19), 25, n))
	if ri(p.get('squash', 0)): img = PA.squash(img, p.get('sq_at', 27), ri(p['squash']))
	if ri(p.get('chest', 0)): img = PA.shift_part(img, lambda x, y: y < (18 if d != 'west' else 24), 0, ri(p['chest']))
	if ri(p.get('head', 0)) > ri(p.get('chest', 0)) and d == 'west': img = PA.shift_part(img, lambda x, y: y < 18 + ri(p.get('chest', 0)), 0, ri(p['head']) - ri(p.get('chest', 0)))
	if ri(p.get('hx', 0)) or ri(p.get('hy', 0)):
		fn = HEAD_W if d == 'west' else (lambda x, y: y < 18)
		img = PA.shift_part(img, fn, ri(p.get('hx', 0)), ri(p.get('hy', 0)), keep=p.get('hy', 0) < 0)
	if (ri(p.get('tx', 0)) or ri(p.get('ty', 0))) and d in TAIL: img = PA.shift_part(img, TAIL[d], ri(p.get('tx', 0)), ri(p.get('ty', 0)))
	if p.get('turn', 1) < 1: img = turn(img, p['turn'])
	c = PA.blank(48, 48)
	if p.get('shadow'): PA.shadow(c, 24, 46, ri(p['shadow']))
	PA.put(c, img, PA.DOX + ri(p.get('dx', 0)), PA.DOY + ri(p.get('dy', 0)))
	for g in p.get('glyphs', []):
		if g[3] > 8: PA.glyph(c, g[0], ri(g[1]), ri(g[2]), ri(g[3]))
	if p.get('fx'): p['fx'](c)
	return c

# ── ตัวช่วยท่า ──
def breath(t, amp=1.0):
	"""อกลง 0-1 ตามโคไซน์ · หัวตามช้ากว่า 1/8 รอบ ลงได้ถึง 2"""
	return {'chest': amp * (0.5 - 0.5 * cos(t)), 'head': max(amp * (0.5 - 0.5 * cos(t)), amp * (1 - cos(t - 0.125)))}

def emote(name, gx, gy):
	"""อีโมตเด้งขึ้น: โผล่ → พุ่ง → ลอยค้างโยกเบา ๆ"""
	def g(t):
		if t < 0.12: return []
		a = kf(t, [(0.12, 0), (0.2, 255), (0.9, 255), (1.0, 0)])
		y = gy + kf(t, [(0.12, 3), (0.22, -2), (0.32, 0)]) + (0.6 * sin(t, 3) if t > 0.32 else 0)
		return [(name, gx, y, a)]
	return g

def spin_dirs(t, dirs):
	"""หมุนตามลำดับทิศ: แต่ละช่วงบีบตัวลงครึ่งช่วงแล้วสลับทิศ"""
	n = len(dirs); seg = t * n; i = int(seg) % n; u = seg - int(seg)
	return {'dir': dirs[(i + (1 if u > 0.5 else 0)) % n], 'turn': max(0.55, abs(cos(u / 2)) if u < 0.5 else abs(cos((1 - u) / 2)))} if False else \
		{'dir': dirs[i] if u < 0.5 else dirs[(i + 1) % n], 'turn': 1 - 0.45 * math.sin(math.pi * u) if 0.25 < u < 0.75 else 1}

def look_dirs(t, seq):
	"""มองซ้ายขวา: seq = [(ทิศ, ช่วงเวลา)] หันแบบบีบตัวช่วงสั้นตอนเปลี่ยนทิศ"""
	acc = 0
	for i, (d, dur) in enumerate(seq):
		if t < acc + dur:
			u = (t - acc) / dur
			if u > 0.85: return {'dir': seq[(i + 1) % len(seq)][0], 'turn': 0.6 + 0.4 * (u - 0.85) / 0.15}
			if u > 0.7: return {'dir': d, 'turn': 1 - 0.4 * (u - 0.7) / 0.15}
			return {'dir': d}
		acc += dur
	return {'dir': seq[0][0]}

KNIFE = [(-0.0, (31, 40, -70, 9)), (0.25, (21, 48, -165, 10)), (0.5, (21, 49, -190, 10)), (0.75, (24, 49, -220, 8)), (1.0, (31, 40, -70, 9))]
def attack_fx(t, dx):
	def fx(c):
		hx, hy, ang, L = kf(t, KNIFE); im = PA.blank(64, 64)
		RA.knife(im, ri(hx), ri(hy), ang, ri(L))
		if 0.12 < t < 0.95:
			a1 = kf(t, [(0.12, 120), (0.25, 235), (0.5, 250), (0.75, 215), (0.95, 200)])
			a0 = kf(t, [(0.12, 120), (0.5, 105), (0.75, 150), (0.95, 195)])
			th = ri(kf(t, [(0.12, 1), (0.25, 3), (0.5, 4), (0.75, 2), (0.95, 1)]))
			lv = RA.SLASH[1:3] if t < 0.38 else RA.SLASH if t < 0.62 else RA.SLASH[:1]
			RA.arc(im, 20, 44, ri(kf(t, [(0.12, 16), (0.5, 17)])), a0, a1, th, lv)
		PA.put(c, im, 0, TOP)
	return fx

def spark_fx(t, keys, pts):
	def fx(c):
		r = ri(kf(t, keys))
		if r >= 1:
			im = PA.blank(64, 64)
			for x, y, k in pts: RA.spark(im, x, y, max(1, ri(r * k)))
			PA.put(c, im, 0, TOP)
	return fx

def sparkles(t, pts, t0=0.0, t1=1.0):
	if not (t0 <= t <= t1): return []
	return [('spark', x, y + TOP - ri(4 * (t - t0) / (t1 - t0)), 255 if (i + int(t * 24)) % 3 else 120) for i, (x, y) in enumerate(pts)]

def zzz(t, x, y):
	out = []
	for k in range(2):
		u = (t + k * 0.5) % 1
		out.append(('z', x + 4 * u + 3 * k, y - 10 * u, 255 * (1 - u)))
	return out

# ── รายการท่า: id → (ผู้แสดง, กลุ่ม, ป้าย, รอบ(วินาที หรือ ชื่อค่าคงที่), ฟังก์ชัน t→params, ค้างท้าย) ──
P = {}
def pose(pid, who, group, label, cycle, fn, hold=False, clip_id=None): P[pid] = (who, group, label, cycle, fn, hold, clip_id)
DIRS = PA.DIRS
for d, th in DIRS:   # เดินบนแผนที่ (ในเกม 4 เฟรม) · รอบ = 2 ช่อง
	pose('rion_walk_' + d, 'rion', 'Rion บนแผนที่', 'เดิน' + th, 'walk', lambda t, d=d: {'dir': d, 'walk': t}, clip_id='rion_walk_' + d)
pose('rion_stand', 'rion', 'Rion ในศึก', 'ยืน (หายใจ)', 'idle', lambda t: dict(breath(t)), clip_id='rion_stand')
pose('rion_attack', 'rion', 'Rion ในศึก', 'ฟัน', 'attack', lambda t: {'dx': kf(t, [(0, 0), (0.12, 3), (0.25, -4), (0.5, -4), (0.75, -1), (1, 0)]),
	'lean': kf(t, [(0, 0), (0.12, 2), (0.25, -2), (0.5, -1), (1, 0)]), 'fx': attack_fx(t, 0)}, clip_id='rion_attack')
pose('rion_hurt', 'rion', 'Rion ในศึก', 'โดนตี', 'hurt', lambda t: {'lean': kf(t, [(0, 0), (0.08, 7), (0.5, 3), (1, 0)]), 'dx': kf(t, [(0, 0), (0.08, 4), (0.5, 2), (1, 0)]),
	'fx': spark_fx(t, [(0, 0), (0.06, 6), (0.4, 0)], [(20, 36, 1), (15, 27, 0.5)])}, clip_id='rion_hurt')
pose('rion_ko', 'rion', 'Rion ในศึก', 'ล้ม', 'ko', lambda t: {'lean': kf(t, [(0, 3), (0.15, 6), (0.35, -3)]), 'squash': kf(t, [(0.1, 0), (0.35, 5)]), 'sq_at': 56,
	'rot': kf(t, [(0.4, 0), (0.75, 90), (0.82, 84), (0.9, 90)])}, hold=True, clip_id='rion_ko')
for d, th in DIRS:
	pose('rion_idle_' + d, 'rion', 'ยืน · หายใจ', 'ยืนหายใจ ' + th, 1.6, lambda t, d=d: dict(breath(t), dir=d))
	pose('rion_run_' + d, 'rion', 'เคลื่อนที่', 'วิ่ง' + th, 0.36, lambda t, d=d: {'dir': d, 'walk': t, 'kmax': 5, 'lean': {'west': -2, 'east': 2}.get(d, 0)})
pose('rion_spin', 'rion', 'เคลื่อนที่', 'หมุนตัวรอบ', 0.48, lambda t: spin_dirs(t, FLOP_DIRS))
for d, th in (('south', 'หน้า'), ('west', 'ซ้าย')):
	pose('rion_jump_' + d, 'rion', 'เคลื่อนที่', 'กระโดด' + th, 0.8, lambda t, d=d: {'dir': d, 'squash': kf(t, [(0, 0), (0.12, 2), (0.2, 0), (0.75, 0), (0.82, 2), (0.95, 0)]),
		'dy': kf(t, [(0.2, 0), (0.45, -10), (0.55, -10), (0.78, 0)]), 'shadow': 9 - 4 * max(0, -kf(t, [(0.2, 0), (0.45, -10), (0.55, -10), (0.78, 0)])) / 10})
pose('rion_look', 'rion', 'ท่าทาง', 'มองซ้าย-ขวา', 2.4, lambda t: look_dirs(t, [('south', 0.25), ('west', 0.25), ('south', 0.25), ('east', 0.25)]))
pose('rion_sit', 'rion', 'ท่าทาง', 'นั่งยอง (หน้า)', 1.8, lambda t: dict(breath(t), dir='south', squash=5, sq_at=56, feet=2))
pose('rion_kneel', 'rion', 'ท่าทาง', 'คุกเข่า (ซ้าย)', 1.8, lambda t: dict(breath(t), img='west_k0'))
pose('rion_sleep', 'rion', 'ท่าทาง', 'นอนหลับ', 2.4, lambda t: {'img': 'west_k1', 'chest': 0, 'glyphs': zzz(t, 44, TOP + 30)})
pose('rion_wave', 'rion', 'ท่าทาง', 'โบกมือทักทาย', 1.1, lambda t: {'arm': (21, 35, 17.5 + 2.5 * sin(t, 2), 29 - abs(sin(t, 2)))} if 0.12 < t < 0.9 else
	{'arm': kf(t, [(0, (24, 44, 23, 47)), (0.12, (21, 35, 17.5, 29)), (0.9, (21, 35, 17.5, 29)), (1, (24, 44, 23, 47))])})
pose('rion_pickup', 'rion', 'ท่าทาง', 'ก้มเก็บของ → ชูขึ้น', 1.44, lambda t: {'squash': kf(t, [(0, 0), (0.15, 4), (0.42, 4), (0.55, 0)]), 'sq_at': 56,
	'bow': kf(t, [(0, 0), (0.18, 26), (0.42, 26), (0.56, 0)]),   # ย่อเข่า + โค้งตัวก้มลงไปหาของ (เดิมยืดแขนลงพื้น ยาวเกินแขนจริง 2 เท่า)
	'arm': kf(t, [(0, (24, 44, 23, 47)), (0.15, (21, 47, 18, 52)), (0.3, (19, 50, 14, 58)), (0.42, (19, 50, 14, 58)), (0.6, (21, 35, 16, 31)), (1, (21, 35, 16, 31))]),
	'item': t > 0.33, 'glyphs': sparkles(t, [(9, 20), (21, 18)], 0.6, 1.0)})
pose('rion_push', 'rion', 'ท่าทาง', 'ผลักลัง', 0.88, lambda t: {'walk': t, 'kmax': 3, 'lean': -3, 'arm': (19, 45, 15, 48), 'barm': (22, 46, 16, 49), 'crate': 4 - 4 * t})   # ลังชิดมือ (แขนยาวเท่าจริงแล้ว เอื้อมไม่ถึงที่เดิม)
pose('rion_nod', 'rion', 'ท่าทาง', 'พยักหน้า', 1.0, lambda t: {'dir': 'south', 'hy': 2 * max(0, sin(t * 1.25, 2)) if t < 0.8 else 0})
pose('rion_shake', 'rion', 'ท่าทาง', 'ส่ายหน้า', 1.0, lambda t: {'dir': 'south', 'hx': 1.4 * sin(t * 1.25, 2) if t < 0.8 else 0})
EMO = [('surprise', '! ตกใจ', '!', 47, 1.05, {'dy': lambda t: kf(t, [(0.12, 0), (0.2, -3), (0.3, 0)])}),
	('question', '? สงสัย', '?', 45, 1.26, {'hx': lambda t: kf(t, [(0.1, 0), (0.25, 1)])}),
	('happy', '♪ ดีใจ', 'note', 45, 1.2, {'dy': lambda t: -2 * abs(sin(t, 2)) if t > 0.12 else 0}),
	('love', '♥ ชอบ', 'heart', 45, 1.2, {'hy': lambda t: 0.5 + 0.5 * sin(t, 2)}),
	('angry', 'โกรธ', 'anger', 43, 0.72, {'hy': lambda t: 1, 'dx': lambda t: 0.6 * sin(t, 6)}),
	('sweat', 'เหงื่อตก (ลำบากใจ)', 'sweat', 44, 1.2, {'hy': lambda t: kf(t, [(0.1, 0), (0.3, 1)])}),
	('think', '... คิด', 'dots', 42, 1.8, {'hx': lambda t: kf(t, [(0.1, 0), (0.3, 1)])}),
	('sleepy', 'ง่วง', 'z', 44, 2.1, {'hy': lambda t: 1 + max(0, sin(t, 1))})]
for key, label, gl, gx, cyc, extra in EMO:
	pose('rion_emo_' + key, 'rion', 'อารมณ์', label, cyc, lambda t, gl=gl, gx=gx, extra=extra: dict({k: f(t) for k, f in extra.items()}, dir='south', glyphs=emote(gl, gx, TOP - 8)(t)))
pose('rion_b_ready', 'rion', 'ในศึก', 'ตั้งท่ารอ (หายใจ)', 1.2, lambda t: dict(breath(t), squash=1))
pose('rion_b_guard', 'rion', 'ในศึก', 'ป้องกัน', 0.84, lambda t: {'arm': kf(t, [(0, (24, 44, 23, 47)), (0.2, (24, 44, 22, 40)), (1, (24, 44, 22, 40))]),
	'barm': kf(t, [(0, (28, 45, 25, 43)), (0.2, (28, 44, 24, 41)), (1, (28, 44, 24, 41))]), 'squash': kf(t, [(0, 0), (0.2, 2)]),
	'glyphs': [('spark', 16, 36 + TOP, 255)] if 0.25 < t < 0.5 else []})
pose('rion_b_dodge', 'rion', 'ในศึก', 'หลบ (ถอยหลบ + ภาพติดตา)', 0.6, lambda t: {'lean': kf(t, [(0, 0), (0.18, 5), (0.5, 5), (0.7, 2), (1, 0)]), 'dx': kf(t, [(0, 0), (0.18, 6), (0.5, 7), (0.7, 3), (1, 0)]),
	'ghost': kf(t, [(0, 0), (0.12, 0.4), (0.45, 0)])})
pose('rion_b_item', 'rion', 'ในศึก', 'ใช้ไอเท็ม', 0.98, lambda t: {'arm': kf(t, [(0, (24, 44, 23, 47)), (0.2, (22, 40, 18, 37)), (0.4, (21, 35, 16, 31)), (0.8, (21, 35, 16, 31)), (1, (24, 44, 23, 47))]),
	'item': 0.1 < t < 0.92, 'glyphs': sparkles(t, [(10, 20), (22, 14), (30, 28)], 0.42, 0.85)})
pose('rion_b_victory', 'rion', 'ในศึก', 'ชนะ (ชูหมัด)', 1.12, lambda t: {'squash': kf(t, [(0, 0), (0.12, 2), (0.22, 0), (0.88, 0), (0.95, 2), (1, 0)]),
	'dy': kf(t, [(0.18, 0), (0.32, -3), (0.45, 0)]), 'shadow': 8, 'arm': kf(t, [(0, (24, 44, 23, 47)), (0.2, (22, 33, 19, 27)), (0.9, (22, 33, 19, 27)), (1, (24, 44, 23, 47))]),
	'glyphs': sparkles(t, [(12, 16), (24, 6), (14, 12)], 0.3, 0.9)})
pose('rion_b_lowhp', 'rion', 'ในศึก', 'HP ต่ำ (หอบ)', 0.44, lambda t: dict(breath(t), lean=-2, squash=2, glyphs=[('sweat', 36, TOP + 6 + ri(1.5 * (t % 1)), 255)]))
pose('rion_b_revive', 'rion', 'ในศึก', 'ฟื้นจากล้ม', 1.26, lambda t: {'rot': kf(t, [(0, 90), (0.1, 90), (0.45, 0)]), 'squash': kf(t, [(0.45, 5), (0.7, 0)]), 'sq_at': 56,
	'lean': kf(t, [(0.45, -3), (0.7, 0)]), 'glyphs': sparkles(t, [(14, 8), (44, 14)], 0.7, 1.0)}, hold=True)
pose('rion_b_cheer', 'rion', 'ในศึก', 'เชียร์เพื่อน (ชูมือกระโดดเบา)', 0.64, lambda t: {'arm': kf(t, [(0, (24, 44, 23, 47)), (0.25, (22, 33, 19, 27)), (0.5, (24, 44, 23, 47)), (0.75, (22, 33, 19, 27)), (1, (24, 44, 23, 47))]),
	'dy': -2 * abs(sin(t, 2)), 'shadow': 7})
# หมา
for d, th in DIRS:
	pose('dog_walk_' + d, 'dog', 'หมาคู่หู', 'เดิน' + th, 'walk', lambda t, d=d: {'dir': d, 'walk': t}, clip_id='dog_walk_' + d)
	pose('dog_idle_' + d, 'dog', 'ยืน · หายใจ', 'ยืนหายใจ ' + th, 1.6, lambda t, d=d: dict(breath(t), dir=d))
	pose('dog_run_' + d, 'dog', 'เคลื่อนที่', 'วิ่ง' + th, 0.32, lambda t, d=d: {'dir': d, 'walk': t})
for d, th in (('west', 'ซ้าย'), ('east', 'ขวา'), ('north', 'หลัง')):
	sg = -1 if d == 'east' else 1
	pose('dog_wag_' + d, 'dog', 'ยืน · หายใจ', 'กระดิกหาง (%s)' % th, 0.4, lambda t, d=d, sg=sg: {'dir': d, 'tx': sg * 1.4 * sin(t), 'ty': -1.2 * sin(t) if d != 'north' else 0})
pose('dog_spin', 'dog', 'เคลื่อนที่', 'หมุนวนดีใจ', 0.36, lambda t: spin_dirs(t, FLOP_DIRS))
pose('dog_hop', 'dog', 'เคลื่อนที่', 'กระโดด (ซ้าย)', 0.63, lambda t: {'squash': kf(t, [(0, 0), (0.1, 1), (0.18, 0), (0.75, 0), (0.85, 1), (0.95, 0)]), 'sq_at': 29,
	'dy': kf(t, [(0.18, 0), (0.42, -7), (0.52, -7), (0.78, 0)]), 'shadow': 8 - 4 * max(0, -kf(t, [(0.18, 0), (0.42, -7), (0.52, -7), (0.78, 0)])) / 7})
pose('dog_sit', 'dog', 'ท่าทาง', 'นั่ง (ซ้าย)', 1.2, lambda t: {'rear': kf(t, [(0, 0), (0.2, 3)]), 'hy': kf(t, [(0, 0), (0.2, -1)]), 'tx': sin(t, 2) if t > 0.25 else 0, 'ty': 1.5 if t > 0.2 else 0})
pose('dog_lie', 'dog', 'ท่าทาง', 'หมอบ (ซ้าย)', 1.6, lambda t: dict(breath(t), squash=4))
pose('dog_sleep', 'dog', 'ท่าทาง', 'นอนหลับ', 2.4, lambda t: dict(breath(t), squash=4, glyphs=zzz(t, 16, 16)))
def bark_fx(t):
	def fx(c):
		if 0.15 < t < 0.4 or 0.55 < t < 0.8:
			d = ImageDraw.Draw(c)
			for i, (x, y) in enumerate(((3, 28), (2, 32), (3, 36))): d.line([(x, y), (x - 3, y + (i - 1) * 2)], fill=(250, 250, 250, 255))
	return fx
pose('dog_bark', 'dog', 'ท่าทาง', 'เห่า', 0.72, lambda t: {'hx': -max(0, sin(t, 2)), 'hy': -max(0, sin(t, 2)), 'fx': bark_fx(t)})
pose('dog_sniff', 'dog', 'ท่าทาง', 'ก้มดมพื้น', 0.84, lambda t: {'hy': 3 + 0.6 * sin(t, 3), 'hx': -0.6 * sin(t, 3)})
pose('dog_playbow', 'dog', 'ท่าทาง', 'ก้มชวนเล่น', 0.72, lambda t: {'front': kf(t, [(0, 0), (0.2, 3), (0.85, 3), (1, 0)]), 'tx': 1.4 * sin(t, 3), 'ty': -sin(t, 3)})
def drops_fx(t):
	def fx(c):
		for k in range(2):
			u = (t * 2 + k * 0.5) % 1
			PA.glyph(c, 'drop', ri(6 + 6 * u), ri(18 - 4 * u + 10 * u * u), ri(255 * (1 - u))); PA.glyph(c, 'drop', ri(40 - 6 * u), ri(20 - 4 * u + 10 * u * u), ri(255 * (1 - u)))
	return fx
pose('dog_shake', 'dog', 'ท่าทาง', 'สะบัดตัว', 0.42, lambda t: {'dir': 'south', 'dx': 1.4 * sin(t, 3), 'fx': drops_fx(t)})
pose('dog_look', 'dog', 'ท่าทาง', 'หันซ้าย-ขวา', 2.4, lambda t: look_dirs(t, [('south', 0.25), ('west', 0.25), ('south', 0.25), ('east', 0.25)]))
for key, label, gl, gx, cyc, extra in (('surprise', '! ตกใจ', '!', 32, 1.05, {'dy': lambda t: kf(t, [(0.12, 0), (0.2, -2), (0.3, 0)])}),
		('question', '? สงสัย (เอียงหัว)', '?', 30, 1.08, {'hx': lambda t: kf(t, [(0.1, 0), (0.25, 1)])}),
		('happy', '♪ ดีใจ', 'note', 30, 1.2, {'dy': lambda t: -2 * abs(sin(t, 2)) if t > 0.12 else 0}),
		('love', '♥ รัก', 'heart', 30, 1.2, {'tx': lambda t: 0})):
	pose('dog_emo_' + key, 'dog', 'อารมณ์', label, cyc, lambda t, gl=gl, gx=gx, extra=extra: dict({k: f(t) for k, f in extra.items()}, dir='south', glyphs=emote(gl, gx, 4)(t)))

# ── ตัวอย่างระดับ 2 (kwan เลือก 5 ต.ค.): ใส่สิ่งที่ภาพเดิมขาด ไม่วาดตัวใหม่ ──
# แขนแกว่งสวนขา (แขนหน้าวาดใหม่ด้วย IK ไหล่→ศอก→มือ) · เป้ตามแรงช้ากว่าตัว · กะพริบตา · มีดมีภาพเบลอตามแนวฟัน · ท่าฟันมีจังหวะง้าง→ฟาด→ค้าง→ตาม→คืน
DRAW, COMPARE = {}, {}
EYE = [(23, y) for y in range(23, 27)] + [(24, 25), (24, 26)]             # ตา Rion หันซ้าย (วัดจากพิกเซล)
SKIN_C, LID_C = (212, 176, 138, 255), (21, 15, 13, 255)
PACK = lambda x, y: 35 <= x <= 47 and 31 <= y <= 51                          # เป้ด้านหลัง (หันซ้าย)

REACH = 8.5   # ไหล่ → มือ ไกลสุด = ความยาวแขนในภาพต้นฉบับ (west: ไหล่ 26,39 → มือ 23,47) · เกินนี้แขนเส้นบางยื่นยาวเหมือนแขนผี (kwan 6 ต.ค. "มือเหมือนแม่นาก แก้ด่วน")
def reach(sh, hand, lim=REACH):
	"""ดึงมือเข้าหาไหล่ถ้าเกินความยาวแขน (ทุกที่ที่วาดแขนใหม่ต้องผ่านตรงนี้)"""
	dx, dy = hand[0] - sh[0], hand[1] - sh[1]; d = math.hypot(dx, dy)
	return hand if d <= lim else (sh[0] + dx * lim / d, sh[1] + dy * lim / d)

def ik(sh, hand, l1=4.6, l2=4.6):
	"""ศอกจากไหล่+มือ (แขนสองท่อน) · ศอกงอไปทางหลัง/ล่าง"""
	hand = reach(sh, hand); dx, dy = hand[0] - sh[0], hand[1] - sh[1]; d = max(0.01, math.hypot(dx, dy))
	if d >= l1 + l2: return (sh[0] + dx * l1 / d, sh[1] + dy * l1 / d)
	a = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(0.0, l1 * l1 - a * a))
	px, py = sh[0] + dx * a / d, sh[1] + dy * a / d; nx, ny = -dy / d, dx / d
	e1, e2 = (px + nx * h, py + ny * h), (px - nx * h, py - ny * h)
	return e1 if (e1[0] + e1[1]) > (e2[0] + e2[1]) else e2

def draw_arm_soft(im, sh, elbow, hand):
	"""แขนหน้าแบบ rion_grips.draw_arm แต่เส้นขอบที่ทับตัวใช้เงาของสีข้างใต้ (ขอบดำทับเสื้อดูเป็นรู)"""
	under = im.copy(); G.draw_arm(im, sh, elbow, hand, w_upper=3)   # ต้นแขนหนา 3 เท่าแขนเดิม (2 จุดแล้วแขนดูผอมยาว)
	u, p = under.load(), im.load(); o = G.OUTL
	for y in range(64):
		for x in range(64):
			if p[x, y][:3] == o and u[x, y][3] and u[x, y][:3] != o:
				c = u[x, y]; p[x, y] = (int(c[0] * 0.62), int(c[1] * 0.58), int(c[2] * 0.58), 255)
	return im

def blink(im):
	p = im.load()
	for x, y in EYE: p[x, y] = SKIN_C
	for x in (22, 23, 24): p[x, 26] = LID_C
	return im

def rion_v2(p):
	img = PA.rion(p.get('img', 'west'))
	if p.get('blink'): blink(img)
	img = G.remove_front_arm(img)
	hx, hy = reach(G.SH_F, p['hand']); e = ik(G.SH_F, (hx, hy))
	draw_arm_soft(img, G.SH_F, (ri(e[0]), ri(e[1])), (ri(hx), ri(hy)))
	if p.get('knife'):
		ang, L = p['knife']
		for k, (a2, al) in enumerate(p.get('smear', [])):                       # ภาพเบลอตามแนวฟัน (เก่าสุดจางสุด)
			ghost = PA.blank(64, 64); RA.knife(ghost, ri(hx), ri(hy), a2, ri(L)); img = PA.put(img, ghost, 0, 0, al)
		RA.knife(img, ri(hx), ri(hy), ang, ri(L))
	if p.get('walk') is not None: img = legs_side(img, p['walk'], True, 30, HIP, 63, 4, 64)
	if ri(p.get('squash', 0)): img = PA.squash(img, 57, ri(p['squash']))
	ch, hd = ri(p.get('chest', 0)), ri(p.get('head', 0))
	if ch: img = PA.shift_part(img, lambda x, y: y < 46, 0, ch)
	if hd > ch: img = PA.shift_part(img, lambda x, y: y < 31 + ch, 0, hd - ch)
	if ri(p.get('pack', 0)): img = PA.shift_part(img, PACK, 0, ri(p['pack']), keep=True)
	if ri(p.get('lean', 0)): img = PA.lean(img, p['lean'], HIP, 8)
	c = PA.blank(64, 64 + TOP)
	if p.get('shadow'): PA.shadow(c, 32, 62 + TOP, ri(p['shadow']))
	PA.put(c, img, ri(p.get('dx', 0)), TOP)
	if p.get('fx'): p['fx'](c)
	return c

def walk_v2(t):
	sw = cos(t)                                                               # ขาหน้าก้าวไปหน้า = แขนหน้าแกว่งไปหลัง
	body = sin(t, 2); lag = sin(t - 0.12, 2)
	return {'walk': t, 'hand': (23 + 3.5 * sw, 47 - 1.3 * abs(sw)), 'pack': max(-1, min(1, lag - body)), 'blink': 0.70 <= t < 0.74}

def idle_v2(t):
	b = breath(t); lag = 0.5 - 0.5 * cos(t - 0.1)
	return dict(b, hand=(23 + 0.6 * sin(t), 47), pack=round(lag) - round(b['chest']), blink=0.55 <= t < 0.6 or 0.63 <= t < 0.67)

ATK_HAND = [(0, (23, 47, 200, 9)), (0.16, (32, 40, -25, 9)), (0.22, (33, 40, -28, 9)), (0.32, (17, 45, -170, 10)),
	(0.44, (16, 46, -185, 10)), (0.7, (19, 49, -220, 8)), (1.0, (23, 47, 200 - 360, 9))]
def attack_v2(t):
	hx, hy, ang, L = kf(t, ATK_HAND)
	smear = []
	if 0.22 < t < 0.4:                                                        # ช่วงฟาดเร็ว: ทิ้งภาพมีดย้อนหลัง 3 ชั้น
		for k, dt in enumerate((0.03, 0.06, 0.09)):
			smear.append((kf(max(0, t - dt), ATK_HAND)[2], 0.55 - 0.15 * k))
	return {'hand': (hx, hy), 'knife': (ang, L), 'smear': smear,
		'dx': kf(t, [(0, 0), (0.16, 3), (0.22, 3), (0.32, -5), (0.44, -5), (0.7, -2), (1, 0)]),
		'lean': kf(t, [(0, 0), (0.16, 3), (0.22, 3), (0.32, -3), (0.44, -2), (0.7, -1), (1, 0)]),
		'squash': kf(t, [(0, 0), (0.14, 2), (0.22, 2), (0.3, 0), (0.44, 1), (0.6, 0)]),
		'pack': kf(t, [(0, 0), (0.18, -1), (0.32, 1), (0.5, 0)]), 'blink': 0.3 <= t < 0.34,
		'fx': attack_fx(min(0.95, max(0.0, (t - 0.1) / 0.9)), 0) if 0.25 < t < 0.95 else None}

for pid, label, cyc, fn, old in (('rion_walk_west_v2', 'เดินซ้าย · ระดับ 2', 'walk', walk_v2, 'rion_walk_west'),
		('rion_attack_v2', 'ฟัน · ระดับ 2', 'attack', attack_v2, 'rion_attack'),
		('rion_idle_west_v2', 'ยืนหายใจซ้าย · ระดับ 2', 1.6, idle_v2, 'rion_idle_west')):
	pose(pid, 'rion', 'ตัวอย่างระดับ 2', label, cyc, fn); DRAW[pid] = rion_v2; COMPARE[pid] = old

# ── ชั้นความสมจริง (kwan 6 ต.ค. "apply กับท่าขยับทั้งหมด ทำให้สมจริงมากที่สุด") — ใส่ทับทุกท่าอัตโนมัติ จากการเคลื่อนที่ของท่านั้นเอง ──
# 1) แรงเฉื่อย: หัว / เป้ / หางหมา เป็นสปริงหน่วงต่อลำตัว — ตัวขยับ ส่วนเหล่านี้ค้างที่เดิมก่อน แล้วถูกดึงตาม เลยไปนิด แล้วเด้งกลับ (follow-through)
#    ตำแหน่งลำตัวคิดจาก dx · dy · ย่อ · อก · เอน ของท่า · ท่าวน = จำลอง 2 รอบเอารอบหลัง · ท่าค้างท้าย = เริ่มนิ่ง · เปลี่ยนทิศ/หมุน/ล้ม = รีเซ็ต
# 2) หายใจ: ท่าที่ไม่ได้กำหนดอกเอง (ไม่นอน ไม่หมุน) · ประมาณ 1 ครั้งต่อ BREATH_SEC · ถ่ายน้ำหนัก (เอนช้า ๆ) ตอนยืน
# 3) กะพริบตา: ท่าหันซ้ายที่ยาวพอ · 4) แขนแกว่งสวนขา: เดิน/วิ่งที่ไม่ได้กำหนดแขนเอง — หันซ้าย = ศอกจาก ik แบบริก · ทิศอื่น = แยกชิ้นแขน (rion_parts.swing_arms)
# ค่าทั้งหมดเป็นค่าภาพ ไม่ใช่ค่าเกม
SPRING_K, SPRING_C, LAG_MAX, BREATH_SEC = 0.32, 0.42, 2.0, 1.6
CYCLE_SEC = {'walk': 0.6, 'idle': 1.6, 'attack': 0.4, 'hurt': 0.2, 'ko': 0.3}   # รอบโดยประมาณของท่าที่ใช้ค่าคงที่เกม (ใช้นับลมหายใจ/กะพริบเท่านั้น)
IDLE_IDS = ('idle', 'stand', 'ready', 'lowhp', 'kneel')
def _body(p, y_at):
	"""ตำแหน่งลำตัวที่ระดับ y (หัว ~20 · เป้ ~40) หลังท่า: เลื่อน + เอน (เฉือนช่วงบน) + ย่อ + อก"""
	x = p.get('dx', 0) + p.get('lean', 0) * max(0, HIP - y_at) / (HIP - 8)
	y = p.get('dy', 0) + p.get('squash', 0) + p.get('chest', 0)
	return x, y
def _spring(targets, cyclic, resets):
	"""offset ต่อเฟรม ของส่วนที่ตามด้วยสปริงหน่วง · targets = ตำแหน่งลำตัวต่อเฟรม"""
	n = len(targets); o, v = 0.0, 0.0; out = [0.0] * n
	for loop in range(2 if cyclic else 1):
		for i in range(n):
			if i in resets: o, v = 0.0, 0.0
			d = targets[i] - targets[i - 1] if (i or (cyclic and loop)) else 0.0
			o -= d; v += -SPRING_K * o - SPRING_C * v; o = max(-LAG_MAX, min(LAG_MAX, o + v)); out[i] = o
	return out
def realism(pid, who, cycle, hold, ps):
	n = len(ps); cyc = not hold; sec = CYCLE_SEC.get(cycle, 1.0) if isinstance(cycle, str) else cycle
	resets = {i for i in range(n) if ps[i].get('dir', 'west') != ps[i - 1].get('dir', 'west') or abs(ps[i].get('rot', 0)) >= 0.5 or ps[i].get('turn', 1) < 1}
	head = (_spring([_body(p, 20)[0] for p in ps], cyc, resets), _spring([_body(p, 20)[1] for p in ps], cyc, resets))
	low = (_spring([_body(p, 40)[0] for p in ps], cyc, resets), _spring([_body(p, 40)[1] for p in ps], cyc, resets))
	breaths = max(1, round(sec / BREATH_SEC)); idle = any(k in pid for k in IDLE_IDS)
	out = []
	for i, p in enumerate(ps):
		q = dict(p); t = i / n
		if who == 'rion':
			q['lag_hx'] = q.get('lag_hx', 0) + head[0][i] * 0.8; q['lag_hy'] = q.get('lag_hy', 0) + head[1][i] * 0.6
			q['pack'] = q.get('pack', 0) + low[1][i] * 0.9
			still = 'chest' not in p and not p.get('img') and 'rot' not in p and p.get('walk') is None
			if still: q.update({k: q.get(k, 0) + v * 0.7 for k, v in breath((t * breaths) % 1).items()})
			if idle and 'lean' not in p: q['lean'] = 0.7 * sin(t, max(1, breaths // 2))     # ถ่ายน้ำหนักช้า ๆ
			if sec >= 0.9 and (p.get('dir', 'west') == 'west'):                              # กะพริบ 1 ครั้งต่อ ~2.6 วิ (อย่างน้อยครั้งเดียวต่อรอบ)
				blinks = max(1, round(sec / 2.6)); q['blink'] = q.get('blink') or ((t * blinks) % 1) > 0.62 and ((t * blinks) % 1) < 0.62 + 0.09 / max(sec / blinks, 0.9)
			if p.get('walk') is not None and p.get('dir', 'west') == 'west' and not (p.get('arm') or p.get('barm')):
				sw = cos(p['walk']); amp = 2.0 + 0.5 * (p.get('kmax', 4) - 4)   # เดิม 3.5 (มือไปไกลเกินตัว)
				q['arm_hand'] = (23 + amp * sw, 47 - 1.3 * abs(sw) - (1 if p.get('kmax', 4) > 4 else 0))   # ขาหน้าก้าวไปหน้า = แขนหน้าแกว่งไปหลัง · วิ่ง = งอแขนสูงขึ้น
			if p.get('walk') is not None and p.get('dir', 'west') in ('south', 'north', 'east') and not (p.get('arm') or p.get('barm')):
				d = p['dir']; ph = p['walk'] % 1                                                       # เฟสเดียวกับขา: หันขวา legs_side (cos) · หน้า/หลัง legs_front (sin)
				q['arm_swing'] = cos(ph) if d == 'east' else sin(ph); q['arm_lift'] = 1.5 if p.get('kmax', 4) > 4 else 1.0
		else:
			q['hx'] = q.get('hx', 0) + head[0][i] * 0.6; q['hy'] = q.get('hy', 0) + head[1][i] * 0.5
			q['tx'] = q.get('tx', 0) + low[0][i] * 0.9; q['ty'] = q.get('ty', 0) + low[1][i] * 0.7
			if 'chest' not in p and 'squash' not in p and p.get('walk') is None and 'rear' not in p:
				q.update({k: q.get(k, 0) + v * 0.6 for k, v in breath((t * breaths) % 1).items()})
		out.append(q)
	return out

def render(pid):
	who, group, label, cycle, fn, hold, clip_id = P[pid]
	draw = DRAW.get(pid) or (rion_frame if who == 'rion' else dog_frame)
	ps = [fn(i / (N - 1) if hold else i / N) for i in range(N)]
	if pid not in DRAW: ps = realism(pid, who, cycle, hold, ps)   # ตัวอย่างระดับ 2 (DRAW เอง) ตั้งค่าครบแล้ว
	frames = [draw(p) for p in ps]
	return PA.dedupe(frames)

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'w').close()
	for f in os.listdir(OUT):
		if f.endswith('.png'): os.remove(os.path.join(OUT, f))
	index = []
	for pid, (who, group, label, cycle, fn, hold, clip_id) in P.items():
		uniq, order = render(pid)
		for i, im in enumerate(uniq): im.save(os.path.join(OUT, '%s_%d.png' % (pid, i)))
		row = {'id': pid, 'who': who, 'group': group, 'label': label, 'n': N, 'unique': len(uniq), 'order': order}
		row['cycle' if not isinstance(cycle, str) else 'timing'] = cycle
		if hold: row['hold'] = True
		if clip_id: row['clip_id'] = clip_id
		if pid in COMPARE: row['compare_with'] = COMPARE[pid]
		index.append(row)
	json.dump({'_doc': 'ทุกคลิปในแท็บท่าขยับแบบ 64 เฟรม (tools/sprites/poses64.py) · order = ลำดับภาพไม่ซ้ำที่เล่น · cycle = วินาทีต่อรอบ · timing = รอบจากค่าคงที่ในเกม (walk/idle/attack/hurt/ko)', 'poses': index},
		open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print('ok', len(index), 'clips ×', N, '· ภาพไม่ซ้ำรวม', sum(r['unique'] for r in index))
	for r in index: print(' ', r['id'], r['unique'])
