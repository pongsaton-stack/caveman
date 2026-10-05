# tools/sprites/weapons.py — วาดอาวุธพิกเซลด้วยโค้ด (ไม่ใช้ตัวเจนภาพ) จาก docs/art-bible/weapons/weapons_full.json
# อาวุธวางแนวทแยง 45° ปลายชี้ขวาบน · ช่อง 32x32 · แสงจากซ้ายบน · เส้นขอบ hue-shift (ไม่มีขอบขาว)
# รูปทรง = รายการ "ปล้อง" ตามแนวแกน (ยาว · ครึ่งความกว้างต้น→ปลาย · ชุดสี) + ของประดับ (แถบเทป · จุด · แสง)
# รัน: python3 tools/sprites/weapons.py [family_id ...]  → assets/sprites/weapons_draft/<id>.png + previews/weapons_<fam>.png
import os, sys, json, math, colorsys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = os.path.join(ROOT, 'docs/art-bible/weapons/weapons_full.json')
OUT = os.path.join(ROOT, 'assets/sprites/weapons_draft')
FONT = os.path.join(ROOT, 'assets/fonts/Sarabun-Regular.ttf')
N = 32

def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def ramp(base, n=4):
	"""ชุดสี 4 ขั้น (มืด→สว่าง) จากสีกลาง · เงาเลื่อน hue ไปทางม่วง ไฮไลต์ไปทางเหลือง"""
	r, g, b = [c / 255 for c in hx(base)]; h, s, v = colorsys.rgb_to_hsv(r, g, b)
	out = []
	for k, (dv, ds, dh) in enumerate(((-0.30, 0.12, 0.04), (-0.13, 0.05, 0.02), (0, 0, 0), (0.14, -0.18, -0.03))):
		hh = (h + dh * (1 if h > 0.5 else -1)) % 1 if dh else h
		R, G, B = colorsys.hsv_to_rgb(hh, min(1, max(0, s + ds)), min(1, max(0.05, v + dv)))
		out.append((int(R * 255), int(G * 255), int(B * 255), 255))
	return out

class Weapon:
	def __init__(self, start=(4.5, 27.5), angle=45):
		self.px = [[None] * N for _ in range(N)]
		self.sx, self.sy = start
		a = math.radians(angle); self.dx, self.dy = math.cos(a), -math.sin(a)
		self.u = 0.0   # ความยาวที่วาดไปแล้วตามแกน

	def uv(self, x, y):
		px, py = x + 0.5 - self.sx, y + 0.5 - self.sy
		return px * self.dx + py * self.dy, px * -self.dy + py * self.dx   # v>0 = ฝั่งล่างขวา

	def axis(self, start, angle):
		"""เริ่มแกนใหม่ (ง่ามหนังสติ๊ก ด้ามแยก) — ความยาวนับใหม่จาก 0"""
		self.sx, self.sy = start; a = math.radians(angle); self.dx, self.dy = math.cos(a), -math.sin(a); self.u = 0.0
		return self

	def at(self, u, v=0.0):
		"""พิกัดจอของจุด (u, v) บนแกนปัจจุบัน"""
		return (self.sx + u * self.dx - v * self.dy, self.sy + u * self.dy + v * self.dx)

	def seg(self, length, w0, w1, color, shape='flat', off0=0.0, off1=None):
		"""ปล้อง: ครึ่งความกว้าง w0→w1 · off = เลื่อนกึ่งกลาง (ใบมีดที่สันตรง คมโค้ง) · 'round' เงากลม · 'flat' ใบแบน"""
		R = ramp(color); u0 = self.u; u1 = u0 + length; off1 = off0 if off1 is None else off1
		for y in range(N):
			for x in range(N):
				u, v = self.uv(x, y)
				if u0 <= u < u1:
					t = (u - u0) / max(length, 1e-6); w = w0 + (w1 - w0) * t; v = v - (off0 + (off1 - off0) * t)
					if abs(v) <= w:
						k = (v / max(w, 0.5))   # -1 ซ้ายบน .. +1 ขวาล่าง
						if shape == 'flat': c = R[3] if k < -0.35 else R[2] if k < 0.45 else R[1]
						else: c = R[3] if k < -0.5 else R[2] if k < 0.2 else R[1] if k < 0.7 else R[0]
						self.px[y][x] = c
		self.u = u1
		return self

	def band(self, u0, u1, color, w=9):
		"""แถบรัด (เทป ลวด) ทับปล้องเดิม — เฉพาะพิกเซลที่มีสีแล้ว"""
		R = ramp(color)
		for y in range(N):
			for x in range(N):
				u, v = self.uv(x, y)
				if u0 <= u < u1 and self.px[y][x] is not None and abs(v) <= w:
					self.px[y][x] = R[3] if v < -0.8 else R[2] if v < 0.8 else R[1]
		return self

	def dot(self, u, v, color):
		x = int(self.sx - 0.5 + u * self.dx - v * self.dy); y = int(self.sy - 0.5 + u * self.dy + v * self.dx)
		if 0 <= x < N and 0 <= y < N: self.px[y][x] = hx(color) + (255,) if isinstance(color, str) else color
		return self

	def edge(self, u0, u1, color, side=1):
		"""ขอบคม/แถบตามความยาว: พิกเซลชั้นนอกสุดฝั่ง side (+1 ขวาล่าง · -1 ซ้ายบน) ในช่วง u0..u1"""
		c = hx(color) + (255,)
		for y in range(N):
			for x in range(N):
				u, v = self.uv(x, y)
				if u0 <= u < u1 and self.px[y][x] is not None:
					nx, ny = (x + (1 if side > 0 else -1), y) if abs(self.dy) < 0.9 else (x, y)
					probe = [(x + dx, y + dy) for dx, dy in ((1, 0), (0, 1)) ] if side > 0 else [(x + dx, y + dy) for dx, dy in ((-1, 0), (0, -1))]
					if any(not (0 <= a < N and 0 <= b < N) or self.px[b][a] is None for a, b in probe): self.px[y][x] = c
		return self

	def circle(self, cx, cy, r, color, shade=True):
		R = ramp(color)
		for y in range(N):
			for x in range(N):
				dx, dy = x + 0.5 - cx, y + 0.5 - cy
				if dx * dx + dy * dy <= r * r:
					k = (dx + dy) / max(r, 0.5)
					self.px[y][x] = (R[3] if k < -0.7 else R[2] if k < 0.4 else R[1]) if shade else R[2]
		return self

	def line(self, a, b, color, width=0.6):
		c = hx(color) + (255,) if isinstance(color, str) else color
		(x0, y0), (x1, y1) = a, b; L = max(1, int(math.hypot(x1 - x0, y1 - y0) * 3))
		for i in range(L + 1):
			t = i / L; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
			for dx in (-width, 0, width):
				for dy in (-width, 0, width):
					xi, yi = int(x + dx), int(y + dy)
					if 0 <= xi < N and 0 <= yi < N and math.hypot(dx, dy) <= width + 0.01: self.px[yi][xi] = c
		return self

	def poly(self, pts, color):
		"""รูปหลายเหลี่ยม เงาอัตโนมัติ: ขอบซ้าย/บนสว่าง ขอบขวา/ล่างมืด"""
		R = ramp(color); m = Image.new('L', (N, N), 0); ImageDraw.Draw(m).polygon(pts, fill=255); mp = m.load()
		for y in range(N):
			for x in range(N):
				if not mp[x, y]: continue
				up = y == 0 or not mp[x, y - 1]; lf = x == 0 or not mp[x - 1, y]
				dn = y == N - 1 or not mp[x, y + 1]; rt = x == N - 1 or not mp[x + 1, y]
				self.px[y][x] = R[3] if (up or lf) and not (dn or rt) else R[1] if (dn or rt) else R[2]
		return self

	def glow(self, color, strength=1, tip=None):
		"""ประกายที่ปลาย (เฉพาะระดับ 5) — ใส่หลังเส้นขอบ · tip = พิกัดจอ (ไม่ใส่ = ปลายแกนปัจจุบัน)"""
		self.glow_c = (hx(color), strength); self.glow_tip = tip; return self

	def image(self):
		im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); p = im.load()
		for y in range(N):
			for x in range(N):
				if self.px[y][x]: p[x, y] = self.px[y][x]
		# เส้นขอบ: พิกเซลว่างที่ติดตัว 4 ทิศ = สีเข้มของเพื่อนบ้าน เลื่อน hue ไปทางเงา
		edge = []
		for y in range(N):
			for x in range(N):
				if p[x, y][3]: continue
				nb = [p[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < N and 0 <= y + dy < N and p[x + dx, y + dy][3] == 255]
				if nb:
					r, g, b = [sum(c[i] for c in nb) / len(nb) / 255 for i in range(3)]
					h, s, v = colorsys.rgb_to_hsv(r, g, b); h = (h + ((0.72 - h + 0.5) % 1 - 0.5) * 0.25) % 1
					R, G, B = colorsys.hsv_to_rgb(h, min(1, s * 0.9 + 0.25), max(0.08, min(0.24, v * 0.3)))
					edge.append((x, y, (int(R * 255), int(G * 255), int(B * 255), 255)))
		for x, y, c in edge: p[x, y] = c
		if getattr(self, 'glow_c', None):
			(gr, gg, gb), st = self.glow_c
			tx, ty = self.glow_tip or (self.sx + self.u * self.dx, self.sy + self.u * self.dy)   # ปลายอาวุธ
			for dx, dy, a in ((0, 0, 255), (1, 0, 150), (-1, 0, 150), (0, 1, 150), (0, -1, 150), (2, 0, 70), (0, -2, 70)):
				x, y = int(tx + 1 + dx), int(ty - 1 + dy)
				if 0 <= x < N and 0 <= y < N and not p[x, y][3]: p[x, y] = (gr, gg, gb, a)
			for k in range(st):   # จุดประกายเล็กข้างตัว
				x, y = int(tx - 6 - 5 * k), int(ty - 2 + 2 * k)
				if 0 <= x < N and 0 <= y < N and not p[x, y][3]: p[x, y] = (gr, gg, gb, 200)
		return im

# ── ตระกูล PC (แทง) ดินสอ → ปากกาผู้นับเหตุการณ์ ── ปล้องเรียงจากท้าย (ล่างซ้าย) ไปปลาย (ขวาบน)
def PC(n):
	w = Weapon()
	if n == 1:   # ดินสอไม้เหลือง ยางลบชมพู ปลอกโลหะ เหลาแหลม
		w.seg(3, 1.6, 1.6, '#e88aa0', 'round').seg(2, 1.7, 1.7, '#b8b4a8', 'round').seg(17, 1.6, 1.6, '#e8b830', 'flat')
		w.seg(4, 1.6, 0.4, '#e6c59a', 'round').seg(1.6, 0.6, 0.0, '#3a3438', 'round')
	elif n == 2:   # ดินสอสองแท่งมัดเทป ปลายตะปู
		w.seg(2, 2.3, 2.3, '#e88aa0', 'round').seg(20, 2.4, 2.4, '#d9a62a', 'flat').seg(2.5, 2.2, 0.8, '#e6c59a', 'round')
		w.seg(5, 0.7, 0.0, '#9aa3ad', 'round')
		w.band(7, 9, '#cfc7b8').band(15, 17, '#cfc7b8')
		for u in range(3, 22, 4): w.dot(u, 0, '#7a5a1a')   # รอยต่อระหว่างสองแท่ง
	elif n == 3:   # ดินสอกดเหล็ก ยาวเท่าหอกสั้น คลิปหนีบ ไส้เหล็กแหลม
		w.seg(2.5, 1.4, 1.4, '#c9d3da', 'round').seg(2, 1.8, 1.8, '#4a5560', 'round').seg(15, 1.9, 1.9, '#8fa1b0', 'round')
		w.seg(4, 1.9, 1.0, '#b8c4cc', 'round').seg(8, 0.7, 0.0, '#6f7a84', 'round')
		w.band(9, 10, '#4a5560', 3).band(12, 13, '#4a5560', 3)   # ร่องกันลื่น
		for u in range(6, 11): w.dot(u, -2, '#dfe6ea')   # คลิปหนีบชิดตัว
	elif n == 4:   # ปากกาหมึกซึมทหาร ด้ามเขียวเข้ม แหวนทอง หัวปากกาทองเหลืองเป็นใบหอก
		w.seg(3, 1.9, 1.9, '#2f5a46', 'round').seg(12, 2.1, 2.1, '#3f7058', 'round').seg(1.2, 2.2, 2.2, '#d6a83e', 'round')
		w.seg(2.5, 1.9, 1.5, '#2f5a46', 'round').seg(9.5, 2.3, 0.0, '#e7c25a', 'flat')
		for u in (21.5, 22.5, 23.5, 24.5): w.dot(u, 0, '#6a4612')   # ร่องหัวปากกา
		w.dot(20.5, 0, '#2a1a08')
		w.band(5, 6, '#d6a83e', 3)
	else:   # ปากกาผู้นับเหตุการณ์ ด้ามดำ รอยขีดนับสีงาช้าง แหวนทอง หัวปากกาเรืองแสงยาว
		w.seg(2.5, 1.8, 1.8, '#e9d9a8', 'round').seg(14, 2.1, 2.1, '#352c42', 'round').seg(1.2, 2.3, 2.3, '#f0c75a', 'round')
		w.seg(2, 2.0, 1.7, '#352c42', 'round').seg(1, 2.2, 2.2, '#f0c75a', 'round').seg(11, 2.4, 0.0, '#ffe08a', 'flat')
		for u in range(4, 17, 2): w.dot(u, -1, '#e9d9a8')   # รอยขีดนับเหตุการณ์
		for u in (22.5, 23.5, 24.5, 25.5, 26.5): w.dot(u, 0, '#b07a1a')
		w.dot(21.5, 0, '#fff6d0')
		w.glow('#ffd36a', 2)
	return w.image()

# ── ตระกูล SL (คม) มีดทำครัว → มีดเชฟแห่งเตาสุดท้าย ── ใบมีด: สันตรงฝั่งซ้ายบน (off ลบ) คมฝั่งขวาล่าง
def SL(n):
	w = Weapon(start=(5.5, 26.5))
	if n == 1:   # มีดหั่นผักด้ามไม้ บิ่นนิดๆ
		w.seg(8, 1.3, 1.4, '#8a5a34', 'round').seg(1, 1.6, 1.6, '#9aa3ad', 'round').seg(13, 2.0, 0.2, '#c7d0d6', 'flat', 0, -1.2)
		w.dot(1.5, 0, '#c7b08a').dot(5.5, 0, '#c7b08a').edge(9, 22, '#eef3f6')
		w.dot(15.5, 1.6, (0, 0, 0, 0))   # รอยบิ่น
	elif n == 2:   # มีดอีโต้พันเทป สันหนา
		w.seg(8, 1.5, 1.5, '#6e4a2c', 'round').seg(1, 1.8, 1.8, '#5a5f66', 'round').seg(15, 2.9, 2.4, '#aab4bb', 'flat', 0, 0.3).seg(2.5, 2.4, 0.3, '#aab4bb', 'flat', 0.3, -1.5)
		w.band(1, 3, '#cfc7b8', 2).band(5, 7, '#cfc7b8', 2).edge(9, 26, '#e9eef1').edge(9, 24, '#6f7880', -1)
	elif n == 3:   # มีดพร้าใบเลื่อย ด้ามท่อ PVC
		w.seg(8, 1.6, 1.6, '#d8dde0', 'round').seg(1.2, 2.0, 2.0, '#4a8fd0', 'round').seg(14, 3.2, 3.4, '#9fa9b0', 'flat', 0, 0.4).seg(3.5, 3.4, 0.4, '#9fa9b0', 'flat', 0.4, -2)
		w.band(0, 1, '#4a8fd0', 2).edge(9, 27, '#e9eef1')
		for u in range(10, 24, 2): w.dot(u + 0.5, -3.6, '#6f7880')   # ฟันเลื่อยบนสัน
	elif n == 4:   # ใบพัดพัดลมลับคม ติดด้ามมีด มีมอเตอร์เล็ก
		w.seg(8, 1.6, 1.6, '#3d3a44', 'round')
		w.seg(17, 2.4, 4.2, '#7fb7b0', 'flat', 0, 0.8).seg(3.5, 4.2, 0.3, '#7fb7b0', 'flat', 0.8, -2.5)
		w.band(2, 3, '#c9a24a', 2).band(5, 6, '#c9a24a', 2).edge(9, 29, '#e8fbf6')
		cx, cy = w.at(9.5); w.circle(cx, cy, 2.6, '#5c6670'); w.dot(9.5, 0, '#e0b040')
	else:   # มีดเชฟจากเหล็กเตาเถ้า ใบเรืองส้มเหมือนถ่าน
		w.seg(8, 1.6, 1.7, '#3a2418', 'round').seg(1.2, 2.2, 2.2, '#c9a24a', 'round').seg(16, 3.0, 2.6, '#4a4448', 'flat', 0, 0.2).seg(4, 2.6, 0.2, '#4a4448', 'flat', 0.2, -2.2)
		w.dot(2.5, 0, '#e8c56a').dot(5.5, 0, '#e8c56a').edge(9, 29, '#ffb24a').edge(12, 26, '#ff7a2a', -1)
		for u in (13, 17, 21): w.dot(u, 0.5, '#ff9a3a')
		w.glow('#ffb24a', 2)
	return w.image()

# ── ตระกูล CR (ทุบ) ไม้เบสบอล ── ด้ามเรียว → ปลายป่อง
def bat(w, wood, grip=None, tip=2.8):
	w.seg(1.2, 1.6, 1.6, wood, 'round').seg(7, 1.0, 1.1, wood, 'round').seg(8, 1.2, tip, wood, 'round').seg(9, tip, tip, wood, 'round').seg(1.5, tip, 1.6, wood, 'round')
	if grip: w.band(1.2, 7.5, grip, 2)
	return w

def CR(n):
	w = Weapon(start=(4.5, 27.5))
	if n == 1:   # ไม้เบสบอลไม้เก่า รอยร้าวพันเทป
		bat(w, '#b98a55', tip=2.5)
		for u, v in ((17, -1), (18, 0), (19, 0), (20, 1)): w.dot(u, v, '#5a3a1e')
		w.band(18.5, 20, '#cfc7b8', 3)
	elif n == 2:   # ไม้อลูมิเนียม บุบ ด้ามพันผ้า
		bat(w, '#9fb2c4', grip='#3a3a44', tip=2.7)
		w.dot(20, -1, '#6c7d8e').dot(22, 1, '#6c7d8e')
	elif n == 3:   # ไม้อลูมิเนียมตอกตะปูรอบปลาย รัดลวด
		bat(w, '#8fa3b6', grip='#3a3a44', tip=2.8)
		w.band(16, 17, '#c08a4a', 3).band(23, 24, '#c08a4a', 3)
		for u in (18, 20.5, 23): w.dot(u, -3.8, '#d0d6da').dot(u, 3.8, '#d0d6da').dot(u, -3, '#7a848c').dot(u, 3, '#7a848c')
	elif n == 4:   # ปลายสวมเฟืองเกียร์รถ หนัก
		bat(w, '#7f8f9e', grip='#5a2a22', tip=2.4)
		cx, cy = w.at(21); w.circle(cx, cy, 5.2, '#8a7a5a')
		for k in range(8):
			a = k * math.pi / 4; w.circle(cx + math.cos(a) * 5.6, cy + math.sin(a) * 5.6, 1.1, '#8a7a5a', False)
		w.circle(cx, cy, 2.0, '#4a4036'); w.circle(cx, cy, 0.8, '#c9b48a', False)
	else:   # ไม้ตีโฮมรันครั้งสุดท้าย ไม้สีงาช้าง แถบเรืองแสงฟ้า ประกายดาว
		bat(w, '#ead9b4', grip='#2f4a7a', tip=3.0)
		w.band(15, 16, '#5ad0ff', 4).band(19, 20, '#5ad0ff', 4).band(23, 24, '#5ad0ff', 4)
		for u in (17, 21): w.dot(u, -1, '#7a5a3a')   # ลายเซ็นจางๆ
		w.glow('#8ae4ff', 2)
	return w.image()

# ── ตระกูล ST (ยิง) หนังสติ๊ก ── ด้าม 45° แล้วแยกง่ามสองข้าง ยางขึงระหว่างปลายง่าม
def sling(w, col, handle=11, prong=11, hw=1.5, pw=1.2, spread=24):
	w.seg(handle, hw, hw, col, 'round')
	fork = w.at(handle - 0.5)
	w.axis(fork, 45 + spread).seg(prong, pw, pw, col, 'round'); a = w.at(prong - 0.7)
	w.axis(fork, 45 - spread).seg(prong, pw, pw, col, 'round'); b = w.at(prong - 0.7)
	return w, a, b, fork

def pouch(w, a, b, rubber, leather='#7a4a2a', width=0.4):
	m = ((a[0] + b[0]) / 2 - 2.5, (a[1] + b[1]) / 2 + 2.5)   # ถุงหนังดึงถอยมาทางด้าม
	w.line(a, m, rubber, width); w.line(b, m, rubber, width); w.circle(m[0], m[1], 1.3, leather, False)
	return m

def ST(n):
	w = Weapon(start=(7.5, 27.5))
	w.axis((4.5, 28.5), 45)
	if n == 1:   # กิ่งไม้ง่าม ยางวง
		w, a, b, f = sling(w, '#8a6238', 11, 10, 1.3, 1.0)
		pouch(w, a, b, '#c9a06a', '#a67a4a', 0.2)
	elif n == 2:   # ง่ามท่อเหล็ก ยางในจักรยาน
		w, a, b, f = sling(w, '#8f99a3')
		pouch(w, a, b, '#2a2a30', '#2a2a30', 0.4); w.axis((4.5, 28.5), 45).band(1, 9, '#2a2a30', 2)
	elif n == 3:   # มีที่รองข้อมือ ศูนย์เล็งไม้บรรทัด
		w0 = Weapon(start=(7.5, 27.5)); w = w0
		w.axis((5.5, 30.5), 45).seg(5, 2.6, 2.6, '#6a4a30', 'flat')   # ที่รองข้อมือ
		w.axis((6.5, 28.5), 45)
		w, a, b, f = sling(w, '#5f6b76')
		pouch(w, a, b, '#c03a3a', '#5a3a2a', 0.4)
		fx, fy = f; w.poly([(fx - 1, fy - 1), (fx + 4, fy - 6), (fx + 5, fy - 5), (fx, fy)], '#e2c04a')   # ไม้บรรทัด
	elif n == 4:   # หน้าไม้จากโครงร่มหัก
		w.seg(20, 1.4, 1.4, '#3a3a40', 'round')          # ก้านร่ม = ตัวหน้าไม้
		tip = w.at(18)
		w.axis(tip, 135).seg(9, 1.0, 0.6, '#5a5a62', 'round'); a = w.at(8.5)
		w.axis(tip, -45).seg(9, 1.0, 0.6, '#5a5a62', 'round'); b = w.at(8.5)
		w.line(a, b, '#d9d2c2', 0.3)
		w.poly([(tip[0] - 4, tip[1] + 1), (tip[0] - 1, tip[1] - 4), (tip[0] + 1, tip[1] - 2), (tip[0] - 2, tip[1] + 3)], '#b8423a')   # ผ้าร่มเศษ
		w.axis((6.5, 26.5), 45).u = 22; w.seg(4, 0.6, 0.0, '#cfd6da', 'round')   # ปลายลูกดอก
	else:   # หนังสติ๊กทองเหลือง ยางเรืองแสง ลูกแก้วดาว
		w, a, b, f = sling(w, '#d8a84a', 11, 11, 1.7, 1.4)
		m = pouch(w, a, b, '#7ae0ff', '#5a3a6a', 0.4)
		w.circle(m[0], m[1], 1.6, '#6a8cff'); w.px[int(m[1])][int(m[0])] = hx('#fff6d0') + (255,)
		w.glow('#bfe8ff', 2, (b[0] + 1, b[1] - 1))
	return w.image()

# ── ตระกูล DV (กล) ที่เย็บกระดาษ ── มุมข้าง หัวหันขวา: ฐาน + แขนบนโค้ง + บานพับท้าย
def stapler(w, top, base='#3a3a40', x0=4, x1=27, y=20):
	w.poly([(x0, y + 3), (x1, y + 3), (x1, y + 6), (x0, y + 6)], base)                         # ฐาน
	w.poly([(x0, y + 3), (x0 + 3, y - 3), (x1 - 2, y - 2), (x1 + 1, y), (x1, y + 2), (x0 + 1, y + 3)], top)   # แขนบน
	w.poly([(x0 + 4, y + 1), (x1 - 3, y + 1), (x1 - 3, y + 3), (x0 + 4, y + 3)], '#9aa3ad')     # รางลวดเย็บ
	w.circle(x0 + 2.5, y + 2.5, 1.6, '#5a5f66')                                                   # บานพับ
	return w

def DV(n):
	w = Weapon()
	if n == 1:   # ที่เย็บกระดาษตั้งโต๊ะ
		stapler(w, '#c8423a')
	elif n == 2:   # แม็กยิงบอร์ด: ตัวทรงตัว L มีคันโยกด้าม พันเทป
		w.poly([(5, 13), (26, 13), (26, 19), (5, 19)], '#4a7a3a')
		w.poly([(6, 9), (22, 9), (24, 13), (6, 13)], '#3a3a40')                                     # คันโยกบน
		w.poly([(6, 19), (11, 19), (10, 29), (6, 29)], '#3a3a40')                                    # ด้ามจับ
		w.poly([(6, 22), (10, 22), (10, 26), (6, 26)], '#cfc7b8')                                    # เทปพันด้าม
		w.poly([(24, 19), (27, 19), (27, 21), (24, 21)], '#9aa3ad')
	elif n == 3:   # ปืนยิงตะปูลม + ถังลม + สาย
		w.poly([(4, 10), (24, 10), (26, 13), (24, 16), (4, 16)], '#d0882a')
		w.poly([(24, 12), (30, 12), (30, 14), (24, 14)], '#9aa3ad')                                  # ปากยิง
		w.poly([(7, 16), (12, 16), (11, 26), (7, 26)], '#2a2a30')                                    # ด้าม
		for y in range(17, 22, 2): w.line((13, y), (20, y), '#e0d8c8', 0.3)                          # แถบตะปู
		w.circle(23, 25, 4.0, '#b83a32'); w.line((10, 26), (19, 26), '#2a2a30', 0.5)
	elif n == 4:   # เครื่องเย็บเล่มสนาม ต่อแบตรถ (ใหญ่ หนัก)
		stapler(w, '#2f6f8f', '#4a4f58', 2, 29, 15)
		w.poly([(4, 24), (14, 24), (14, 30), (4, 30)], '#3a3a40'); w.poly([(5, 23), (7, 23), (7, 24), (5, 24)], '#d03a2a')
		w.line((6, 23), (9, 20), '#d03a2a', 0.3); w.line((12, 24), (14, 21), '#2a2a2a', 0.3)
	else:   # ที่เย็บกระดาษทองเหลืองโบราณ ลวดเย็บเรืองฟ้า
		stapler(w, '#d8a84a', '#6a4a24', 3, 28, 18)
		for x in (9, 14, 19): w.px[17][x] = hx('#fff0b0') + (255,)
		w.line((26, 24), (29, 24), '#7ae0ff', 0.3); w.line((29, 22), (29, 24), '#7ae0ff', 0.3)
		w.glow('#9ae8ff', 2, (28, 23))
	return w.image()

# ── ตระกูล BD (มือเปล่า) ถุงมือ ── วาดตั้ง นิ้วชี้ขึ้น เอียงเล็กน้อย
def glove(w, col, cuff, x=9):
	w.poly([(x, 30), (x + 13, 30), (x + 13, 26), (x, 26)], cuff)                          # ข้อมือ
	w.poly([(x - 1, 26), (x + 14, 26), (x + 15, 15), (x - 2, 16)], col)                    # ฝ่ามือ
	for i, (dx, top) in enumerate(((0, 8), (4, 5), (8, 6), (12, 9))):                      # นิ้ว 4 นิ้ว
		w.poly([(x - 1 + dx, 17), (x + 2 + dx, 17), (x + 2 + dx, top + 1), (x + 1 + dx, top), (x - 1 + dx, top + 1)], col)
	w.poly([(x - 2, 23), (x - 6, 18), (x - 4, 16), (x - 1, 19)], col)                       # นิ้วโป้ง
	return w

def BD(n):
	w = Weapon()
	if n == 1:   # ถุงมือผ้าฝ้ายเปื้อนดิน
		glove(w, '#e6dcc4', '#c9bea4')
		for x, y in ((11, 20), (16, 23), (20, 18)): w.px[y][x] = hx('#8a6a44') + (255,)
	elif n == 2:   # ถุงมือหนังช่างเชื่อม เย็บน็อตข้อนิ้ว
		glove(w, '#9a6232', '#6e4424')
		for x in (9, 13, 17, 21): w.circle(x + 0.5, 17.5, 1.0, '#b8c0c6')
	elif n == 3:   # ร้อยพวงกุญแจเป็นสนับมือ
		glove(w, '#7a4a2a', '#4a3a30')
		w.poly([(7, 16), (24, 16), (24, 19), (7, 19)], '#aab4bb')
		for x in (9, 13, 17, 21): w.circle(x + 0.5, 17.5, 1.2, '#d0d8dc')
		w.line((22, 20), (25, 25), '#c9a24a', 0.4)
	elif n == 4:   # ถุงมือติดสปริงโช้คประตู
		glove(w, '#5a5a62', '#3a3a40')
		for y in range(19, 30, 2): w.line((22, y), (27, y - 1), '#c0c8cc', 0.3)
		w.poly([(24, 16), (27, 16), (27, 19), (24, 19)], '#d06a2a')
	else:   # ถุงมือผืนแรกที่ปะซ่อม รอยปะเรืองอุ่น
		glove(w, '#e6dcc4', '#c9bea4')
		w.poly([(10, 19), (14, 19), (14, 23), (10, 23)], '#ffb86a'); w.poly([(16, 10), (19, 10), (19, 14), (16, 14)], '#ffd08a')
		w.poly([(18, 21), (22, 21), (22, 24), (18, 24)], '#ff9a5a')
		w.glow('#ffd36a', 2, (21, 5))
	return w.image()

DRAW = {'SL': SL, 'PC': PC, 'CR': CR, 'ST': ST, 'DV': DV, 'BD': BD}

def label_sheet(fam, spec, imgs, scale=8):
	"""ชีตตรวจ: ช่องละอาวุธ · ขยาย nearest · รหัส ชื่อ ระดับใต้ภาพ (ภาพตัวจริงใน assets ไม่มีตัวหนังสือ)"""
	cw = N * scale + 40; ch = N * scale + 70
	sheet = Image.new('RGBA', (cw * len(imgs), ch), (0, 0, 0, 0)); d = ImageDraw.Draw(sheet)
	f1 = ImageFont.truetype(FONT, 22); f2 = ImageFont.truetype(FONT, 18)
	for i, (w, im) in enumerate(zip(spec['weapons'], imgs)):
		x0 = i * cw
		sheet.paste(im.resize((N * scale, N * scale), Image.NEAREST), (x0 + 20, 6))
		d.text((x0 + 20, N * scale + 10), '%s  T%d' % (w['id'], w['tier']), font=f2, fill=(232, 217, 181, 255))
		d.text((x0 + 20, N * scale + 34), w['name'], font=f1, fill=(255, 255, 255, 255))
	return sheet

def full_sheet(spec, size=4096):
	"""ชีตเต็มตามสเปก: 4096x4096 พื้นโปร่ง · แถว = ตระกูล · คอลัมน์ = ระดับ 1-5 · ขยาย nearest · ป้าย รหัส/ชื่อ/ระดับใต้ภาพ"""
	rows = len(spec['families']); cw, ch = size // 5, size // rows; sc = min(cw - 120, ch - 150) // N
	sheet = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(sheet)
	f1 = ImageFont.truetype(FONT, 44); f2 = ImageFont.truetype(FONT, 36)
	for r, f in enumerate(spec['families']):
		for w in f['weapons']:
			c = w['tier'] - 1; x0, y0 = c * cw, r * ch
			im = Image.open(os.path.join(OUT, w['id'] + '.png')).resize((N * sc, N * sc), Image.NEAREST)
			sheet.alpha_composite(im, (x0 + (cw - N * sc) // 2, y0 + 10))
			for txt, fnt, yy, col in (('%s  T%d' % (w['id'], w['tier']), f2, N * sc + 16, (232, 217, 181, 255)), (w['name'], f1, N * sc + 56, (255, 255, 255, 255))):
				tw = d.textlength(txt, font=fnt)
				d.text((x0 + (cw - tw) / 2, y0 + yy), txt, font=fnt, fill=col, stroke_width=3, stroke_fill=(20, 16, 14, 255))
	return sheet

def main(fams):
	spec = json.load(open(SPEC, encoding='utf-8')); os.makedirs(OUT, exist_ok=True)
	for f in spec['families']:
		if f['family_id'] not in fams or f['family_id'] not in DRAW: continue
		imgs = []
		for w in f['weapons']:
			im = DRAW[f['family_id']](w['tier']); im.save(os.path.join(OUT, w['id'] + '.png')); imgs.append(im)
		sh = label_sheet(f, f, imgs)
		bg = Image.new('RGBA', sh.size, (38, 34, 30, 255)); bg.alpha_composite(sh)
		bg.save(os.path.join(ROOT, 'docs/art-bible/previews/weapons_%s.png' % f['family_id']))
		print(f['family_id'], len(imgs))
	if set(fams) >= set(DRAW):
		full_sheet(spec).save(os.path.join(ROOT, 'docs/art-bible/weapons/weapons_sheet_4096.png'))
		print('sheet ok')

if __name__ == '__main__':
	main(sys.argv[1:] or list(DRAW))
