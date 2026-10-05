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

	def seg(self, length, w0, w1, color, shape='flat'):
		"""ปล้อง: ครึ่งความกว้าง w0→w1 · shape 'round' = เงากลม · 'flat' = ใบแบน (สองโทน)"""
		R = ramp(color); u0 = self.u; u1 = u0 + length
		for y in range(N):
			for x in range(N):
				u, v = self.uv(x, y)
				if u0 <= u < u1:
					t = (u - u0) / max(length, 1e-6); w = w0 + (w1 - w0) * t
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

	def glow(self, color, strength=1):
		"""แสงประกายจางรอบตัว (เฉพาะระดับ 5) — ใส่หลังเส้นขอบ เป็นพิกเซลโปร่งครึ่งเดียว"""
		self.glow_c = (hx(color), strength); return self

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
			tx = self.sx + self.u * self.dx; ty = self.sy + self.u * self.dy   # ปลายอาวุธ
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

DRAW = {'PC': PC}

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

if __name__ == '__main__':
	main(sys.argv[1:] or list(DRAW))
