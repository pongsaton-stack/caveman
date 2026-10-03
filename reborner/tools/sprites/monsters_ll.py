# tools/sprites/monsters_ll.py — มอนสไตล์ Last Light ตามสเปก docs/art-bible/monster_visual_master.json
# วาดเองด้วยโค้ด (ไม่ใช้เครดิต PixelLab) · ใช้เฉพาะสีใน palette ของแต่ละตัวในสเปก
# ศัตรูอยู่ซ้ายของจอสู้ → หันขวาเข้าหาปาร์ตี้
# รัน: <python+Pillow> tools/sprites/monsters_ll.py [out_dir]
import json, math, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs/art-bible/monster_visual_master.json'), encoding='utf-8'))['entries']}

def hexc(h):
	h = h.lstrip('#')
	return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

class Canvas:
	def __init__(self, n):
		self.n = n
		self.im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
		self.p = self.im.load()
	def set(self, x, y, c):
		if 0 <= x < self.n and 0 <= y < self.n:
			self.p[x, y] = c
	def get(self, x, y):
		return self.p[x, y] if 0 <= x < self.n and 0 <= y < self.n else (0, 0, 0, 0)
	def blob(self, cx, cy, rx, ry, tones, hi=0.62, lo=-0.15, clip=None):
		"""วงรีลงเงา 3 ระดับ แสงจากซ้ายบน: tones = (เงา, กลาง, สว่าง)"""
		for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
			for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
				nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
				r2 = nx * nx + ny * ny
				if r2 > 1 or (clip and not clip(x, y)):
					continue
				L = -0.55 * nx - 0.75 * ny + 0.35 * (1 - r2)
				self.set(x, y, tones[2] if L > hi else tones[0] if L < lo else tones[1])
	def tri(self, pts, c):
		(x0, y0), (x1, y1), (x2, y2) = pts
		def side(ax, ay, bx, by, px, py):
			return (bx - ax) * (py - ay) - (by - ay) * (px - ax)
		for y in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
			for x in range(min(x0, x1, x2), max(x0, x1, x2) + 1):
				a = side(x0, y0, x1, y1, x, y); b = side(x1, y1, x2, y2, x, y); d = side(x2, y2, x0, y0, x, y)
				if (a >= 0 and b >= 0 and d >= 0) or (a <= 0 and b <= 0 and d <= 0):
					self.set(x, y, c)
	def outline(self, c):
		"""เส้นขอบ 1px รอบเงาตัว (สีเข้มในพาเลตต์ ไม่ใช่ดำ — กฎ UX ข้อ 4 ไม่มีขอบขาว)"""
		edge = []
		for y in range(self.n):
			for x in range(self.n):
				if self.p[x, y][3] == 0 and any(self.get(x + dx, y + dy)[3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
					edge.append((x, y))
		for x, y in edge:
			self.p[x, y] = c
		return self
	def over(self, other):
		self.im.alpha_composite(other.im)
		self.p = self.im.load()
		return self

# ── M01 สไลม์เถ้า ─────────────────────────────────────────────
def slime(squash=0):
	"""ก้อนโดมเถ้าทรงสูง ฐานแผ่ จุดด่างดำ ตาโตช่วงล่าง ยิ้มเล็ก ฟองเถ้าลอย · squash = idle เฟรม 2 (เตี้ยลง กว้างขึ้น)"""
	mid, light, shadow, dark = [hexc(h) for h in SPEC['M01']['palette']]   # 8A7460 D2BD9A 6C5947 383A37
	c = Canvas(48)
	base = 42
	rx, ry = 14 + squash, 16 - squash
	cy = base - ry
	c.blob(24, base - 1, 18 + squash, 3, (shadow, mid, mid))                 # ฐานแผ่ (เหมือนต้นแบบ)
	c.blob(24, cy + 1, rx, ry, (shadow, mid, light), hi=0.3, lo=-0.35, clip=lambda x, y: y <= base - 1)
	# ประกายมุมซ้ายบน
	# จุดด่างเถ้า: เม็ดเล็กสีเงา (ไม่ใช้สีเข้มสุด จะได้ไม่แย่งกับตา) + ดำแค่ 3 จุดไกลหน้า
	for x, y in ((14, 24), (20, 16), (21, 16), (30, 20), (35, 27), (12, 33), (34, 36), (17, 39)):
		if c.get(x, y + squash)[3]:
			c.set(x, y + squash, shadow)
	for x, y in ((31, 14), (36, 33), (12, 29)):
		if c.get(x, y + squash)[3]:
			c.set(x, y + squash, dark)
	# ตาโตกลม 3x4 + ประกาย · ปากยิ้มเล็ก
	ey = 27 + squash
	for ex in (17, 27):                                                       # ตาโต 4x5 มุมมน + ประกาย 2px
		for dx in range(4):
			for dy in range(5):
				if not (dy in (0, 4) and dx in (0, 3)):
					c.set(ex + dx, ey + dy, dark)
		c.set(ex + 1, ey + 1, light); c.set(ex + 1, ey + 2, light); c.set(ex + 2, ey + 1, light)
	for x, y in ((22, 34), (23, 35), (24, 35), (25, 34)):
		c.set(x, y + squash, dark)
	c.outline(dark)
	b = Canvas(48)
	b.blob(35, 7 + squash, 2.2, 2.2, (mid, mid, light))                      # ฟองเถ้าลอย
	b.blob(39, 3 + squash, 1.4, 1.4, (mid, mid, light))
	b.outline(dark)
	return c.over(b).im

# ── M15 หมาป่าคู่ ────────────────────────────────────────────
def pup(c, ox, oy, tones, light, dark, ear_up):
	"""ลูกหมาป่าตัวกลมหัวโต หันขวาเฉียงหน้า · ear_up = หูตั้งทั้งคู่ (ไม่งั้นหูขวาพับ)"""
	shadow, mid, hi = tones
	c.blob(ox - 8, oy - 1, 4.5, 3.2, tones)                                   # หางฟู ต่ำด้านหลัง
	c.blob(ox - 11, oy - 2, 1.8, 1.6, (light, light, light))                  # ปลายหาง
	for lx in (ox - 5, ox - 2, ox + 2, ox + 5):                                # ขาสั้น
		for y in range(oy + 3, oy + 7):
			c.set(lx, y, shadow); c.set(lx + 1, y, mid if lx in (ox - 5, ox + 2) else shadow)
	c.blob(ox, oy, 8, 5.5, tones)                                             # ตัว
	hx, hy = ox + 5, oy - 6
	c.tri(((hx - 6, hy - 4), (hx - 5, hy - 10), (hx - 2, hy - 6)), mid)       # หูซ้ายตั้งเสมอ
	c.set(hx - 5, hy - 7, shadow)
	if ear_up:
		c.tri(((hx + 2, hy - 6), (hx + 5, hy - 10), (hx + 6, hy - 4)), mid)
		c.set(hx + 5, hy - 7, shadow)
	else:                                                                     # หูขวาพับลง
		c.tri(((hx + 2, hy - 6), (hx + 8, hy - 6), (hx + 6, hy - 2)), shadow)
	c.blob(hx, hy, 7.5, 6.5, tones)                                           # หัวโต
	c.blob(hx + 6, hy + 2, 4.5, 3, (shadow, mid, hi))                         # ปากกระบอกยื่นยาว (หมาป่า ไม่ใช่แมว)
	c.blob(hx - 1, hy + 4, 3, 1.6, (mid, light, light))                       # ขนคอปุย
	c.set(hx + 10, hy + 1, dark); c.set(hx + 10, hy + 2, dark); c.set(hx + 9, hy + 1, dark)   # จมูกปลายปาก
	c.set(hx + 5, hy + 4, dark); c.set(hx + 6, hy + 4, dark); c.set(hx + 7, hy + 4, dark)      # ปาก
	for ex in (hx - 3, hx + 2):                                               # ตากลมใสสองข้าง
		for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)):
			c.set(ex + dx, hy - 3 + dy, dark)
		c.set(ex, hy - 3, light)

def wolf_pair(hop=0):
	"""ลูกหมาป่าแฝดวิ่งชิดกัน: ตัวหลังหูพับ (ซ้ายบน เงาเข้มกว่า = อยู่ลึก) · ตัวหน้าหูตั้ง (ขวาล่าง) หัวไม่ซ้อนกัน · hop = idle เฟรม 2 (กระโดดพร้อมกัน)"""
	mid, shadow, light, dark = [hexc(h) for h in SPEC['M15']['palette']]   # 8A7460 6C5947 D2BD9A 383A37
	back = Canvas(48)
	pup(back, 11, 22 - hop, (shadow, shadow, mid), light, dark, ear_up=False)
	back.outline(dark)
	front = Canvas(48)
	pup(front, 24, 35 - hop, (shadow, mid, light), light, dark, ear_up=True)
	front.outline(dark)
	return back.over(front).im

SPRITES = {
	'M01': [lambda: slime(0), lambda: slime(1)],
	'M15': [lambda: wolf_pair(0), lambda: wolf_pair(1)],
}

if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/sprites/monsters_ll/')
	os.makedirs(out, exist_ok=True)
	allowed = {mid: {hexc(h)[:3] for h in SPEC[mid]['palette']} for mid in SPRITES}
	for mid, frames in SPRITES.items():
		for i, f in enumerate(frames):
			im = f()
			used = {px[:3] for px in im.get_flattened_data() if px[3]}
			assert used <= allowed[mid], (mid, used - allowed[mid])     # ห้ามสีนอกสเปก
			im.save(os.path.join(out, '%s%s.png' % (mid, '' if i == 0 else '_idle%d' % i)))
	print('ok ->', out)
