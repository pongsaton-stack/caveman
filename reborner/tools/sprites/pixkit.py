# tools/sprites/pixkit.py — ชุดวาดพิกเซลแบบลงเงา (ใช้กับไอเท็ม/สิ่งก่อสร้าง/ยานพาหนะ/อุปกรณ์ NPC)
# วาดรูปทรงลง mask แล้วลงสีตามทิศแสง (บนซ้ายสว่าง ล่างขวาเข้ม) + เม็ดสีสุ่มแบบคงที่ + เส้นขอบเข้มสีเดียวกับวัตถุ
# โทนเดียวกับไทล์ Last Light (ภาพกลางแสงอุ่น เงาออกเขียวคล้ำ)
import colorsys, random
from PIL import Image, ImageDraw

def ramp(rgb, n=5):
	"""สีฐาน → [ขอบ, เงาเข้ม, เงา, กลาง, สว่าง] เงาเลื่อนไปทางเย็น ส่วนสว่างเลื่อนไปทางอุ่น"""
	h, l, s = colorsys.rgb_to_hls(*[c / 255 for c in rgb])
	spec = [(-0.04, 0.28, 0.9), (-0.025, 0.62, 1.0), (-0.012, 0.8, 1.0), (0, 1.0, 1.0), (0.02, 1.22, 0.85)]
	out = []
	for dh, kl, ks in spec:
		r, g, b = colorsys.hls_to_rgb((h + dh) % 1, max(0, min(0.95, l * kl)), max(0, min(1, s * ks)))
		out.append((round(r * 255), round(g * 255), round(b * 255)))
	return out

class Pen:
	"""ImageDraw ที่เติม fill=255 ให้เองทุกคำสั่ง (ส่ง fill=None เพื่อวาดแค่เส้น)"""
	def __init__(self, m): self.d = ImageDraw.Draw(m)
	def __getattr__(self, n):
		f = getattr(self.d, n)
		def call(*a, **k):
			k.setdefault('fill', 255); return f(*a, **k)
		return call

class Sprite:
	def __init__(self, w, h, seed=0):
		self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); self.w, self.h = w, h; self.rnd = random.Random(seed)

	def part(self, rgb, draw, tex=0.18, outline=True, light=True, alpha=255):
		"""draw(d) วาดรูปทรงสีขาวลง mask · rgb = สีฐาน (หรือ ramp ที่ทำแล้ว)"""
		m = Image.new('L', (self.w, self.h), 0); draw(Pen(m)); mp = m.load()
		R = rgb if isinstance(rgb, list) else ramp(rgb); p = self.im.load()
		inside = lambda x, y: 0 <= x < self.w and 0 <= y < self.h and mp[x, y] > 127
		for y in range(self.h):
			for x in range(self.w):
				if not inside(x, y): continue
				lv = 3
				if light:
					if not inside(x, y - 1) or not inside(x - 1, y): lv = 4
					elif not inside(x, y + 1) or not inside(x + 1, y): lv = 1
					elif not inside(x + 1, y + 1) or not inside(x, y + 2): lv = 2
				r = self.rnd.random()
				if r < tex / 2: lv = max(1, lv - 1)
				elif r < tex: lv = min(4, lv + 1) if lv < 4 else 3
				p[x, y] = R[lv] + (alpha,)
		if outline:
			for y in range(self.h):
				for x in range(self.w):
					if inside(x, y): continue
					if any(inside(x + ox, y + oy) for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1))): p[x, y] = R[0] + (255,)
		return self

	def flat(self, rgb, draw, alpha=255):
		"""สีเดียวไม่ลงเงา (ไฟ แสง ตัวอักษร)"""
		m = Image.new('L', (self.w, self.h), 0); draw(Pen(m)); mp = m.load(); p = self.im.load()
		for y in range(self.h):
			for x in range(self.w):
				if mp[x, y] > 127: p[x, y] = tuple(rgb) + (alpha,)
		return self

	def px(self, pts, rgb, alpha=255):
		p = self.im.load()
		for x, y in pts:
			if 0 <= x < self.w and 0 <= y < self.h: p[x, y] = tuple(rgb) + (alpha,)
		return self

	def shadow(self, cx, y, rx, ry=2):
		sh = Image.new('RGBA', self.im.size); ImageDraw.Draw(sh).ellipse([cx - rx, y - ry, cx + rx, y + ry], fill=(20, 18, 14, 80))
		sh.alpha_composite(self.im); self.im = sh; return self

	def copy(self):
		s = Sprite(self.w, self.h); s.im = self.im.copy(); s.rnd = random.Random(self.rnd.random()); return s
