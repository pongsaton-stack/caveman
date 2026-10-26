# tools/sprites/battle_bg_hires.py — ฉากหลังจอต่อสู้แนวภาพคม องก์ 1 (kwan 14 ต.ค. 2026 "ทำให้เลยได้ไหม" แทนภาพ 13 ใน SHOTLIST)
#
# วาดด้วยโค้ด ไม่ใช่ภาพเจน: ลายเส้นการ์ตูนลงสีเรียบ เส้นขอบเข้ม ให้เข้ากับ Rion ภาพคม · โทนองก์ 1 ตาม GDD = เขียวชอุ่ม ฟ้าใส ทองอุ่น
# แถบเวทีในจอสู้ = Rect2(0, 24, 384, 79) (หน่วยจอฐาน) → วาดที่ ×5 = 1920x395 · เส้นพื้น y 82 → 73% ของแถบ · เท้าตัวละคร y 97 → 92%
# วาดใหญ่ ×2 แล้วย่อ (ขอบเรียบ) · รายละเอียดน้อย สีหม่นกว่าตัวละคร ให้ตัวละครเด่น (GDD: ความเงียบและพื้นที่ว่าง)
#
#   python3 tools/sprites/battle_bg_hires.py   → assets/sprites/battle_bg_hires_draft/act1.png (ร่าง ยังไม่เข้าเกม)
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets/sprites/battle_bg_hires_draft')
W, H, SS = 1920, 395, 2            # ขนาดจริง · วาดใหญ่ SS เท่า
GROUND = 0.734                     # เส้นพื้น (สัดส่วนความสูง)

def hexc(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
SKY_TOP, SKY_LOW = hexc('7fb9e0'), hexc('d9eedf')
CLOUD, CLOUD_SH, CLOUD_LINE = hexc('fbfcf6'), hexc('d5e2ea'), hexc('8aa3b8')
FAR, FAR_LINE = hexc('9cc3b0'), hexc('7fa596')
MID, MID_SH, MID_LINE = hexc('7db866'), hexc('689f55'), hexc('4d7a45')
TREE, TREE_SH, TREE_LINE = hexc('4f8f4c'), hexc('3f7741'), hexc('2f5634')
GRASS, GRASS_SH, GRASS_LINE = hexc('8cc65a'), hexc('76b04c'), hexc('4f7a3a')
DIRT, DIRT_SH, DIRT_LINE = hexc('e3c48d'), hexc('d2ae74'), hexc('a3835a')
SUN = hexc('fff2c4')

def S(v): return int(round(v * SS))

def poly_line(d, pts, fill, line, w):
	d.polygon([(S(x), S(y)) for x, y in pts], fill=fill)
	d.line([(S(x), S(y)) for x, y in pts + pts[:1]], fill=line, width=S(w), joint='curve')

def ridge(y0, amp, waves, seed, step=8):
	"""เส้นสันเขาลูกคลื่นนุ่ม (ผลรวมไซน์) · คืนจุดซ้าย→ขวา"""
	rnd = random.Random(seed); ph = [rnd.random() * 6.28 for _ in waves]
	return [(x, y0 - sum(a * amp * math.sin(x / l * 6.28 + p) for (a, l), p in zip(waves, ph))) for x in range(-20, W + 21, step)]

def blob(im, cx, cy, rs, fill, line, w, shade=None):
	"""กลุ่มวงกลมรวมเป็นก้อน (เมฆ/พุ่มไม้): เส้นขอบรอบนอก + เงาเสี้ยวเดียวใต้ก้อน (แสงจากบน) · วาดบนแผ่นเล็กแล้วแปะ"""
	pad = w + 4; x0 = min(dx - r for dx, dy, r in rs) - pad; x1 = max(dx + r for dx, dy, r in rs) + pad
	y0 = min(dy - r for dx, dy, r in rs) - pad; y1 = max(dy + r for dx, dy, r in rs) + pad
	tw, th = S(x1 - x0), S(y1 - y0)
	def mask(grow):
		m = Image.new('L', (tw, th), 0); md = ImageDraw.Draw(m)
		for dx, dy, r in rs: md.ellipse([S(dx - x0 - r - grow), S(dy - y0 - r - grow), S(dx - x0 + r + grow), S(dy - y0 + r + grow)], fill=255)
		return m
	outer, inner = mask(w), mask(0)
	tile = Image.new('RGB', (tw, th), line); tile.paste(Image.new('RGB', (tw, th), fill), mask=inner)
	if shade:                                                            # เสี้ยวล่าง = ในก้อน แต่ไม่อยู่ในก้อนที่เลื่อนลง
		lift = max(r for _, _, r in rs) * 0.38
		up = Image.new('L', (tw, th), 0); up.paste(inner, (0, -S(lift)))
		from PIL import ImageChops
		tile.paste(Image.new('RGB', (tw, th), shade), mask=ImageChops.subtract(inner, up))
	im.paste(tile, (S(cx + x0), S(cy + y0)), mask=outer)

def build():
	im = Image.new('RGB', (W * SS, H * SS)); d = ImageDraw.Draw(im)
	# ฟ้าไล่สี (ฟ้าคือตัวละคร: บนเข้ม → ใกล้ขอบฟ้าสว่างอุ่น)
	for y in range(H * SS):
		k = min(1.0, y / (H * SS * 0.62)) ** 1.3
		d.line([(0, y), (W * SS, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(SKY_TOP, SKY_LOW)))
	# แสงแดดอุ่นมุมซ้ายบน
	glow = Image.new('L', im.size, 0); ImageDraw.Draw(glow).ellipse([S(-260), S(-300), S(520), S(260)], fill=110)
	im.paste(Image.new('RGB', im.size, SUN), mask=glow.filter(ImageFilter.GaussianBlur(S(120))))
	d = ImageDraw.Draw(im)
	# เมฆ: ก้อนกลมฐานแบน
	for cx, cy, sc in ((300, 70, 1.0), (880, 46, 0.75), (1420, 88, 1.15), (1800, 40, 0.6)):
		rs = [(-60 * sc, 6 * sc, 30 * sc), (-22 * sc, -10 * sc, 40 * sc), (26 * sc, -4 * sc, 34 * sc), (62 * sc, 8 * sc, 24 * sc), (0, 14 * sc, 30 * sc)]
		blob(im, cx, cy, rs, CLOUD, CLOUD_LINE, 2.2, CLOUD_SH)
	# ภูเขาไกล (สีอมฟ้า เส้นจาง)
	far = ridge(H * 0.50, 1.0, [(18, 900), (9, 380), (4, 170)], 3)
	poly_line(d, far + [(W + 20, H), (-20, H)], FAR, FAR_LINE, 2.5)
	# เนินกลาง + ดงไม้
	mid = ridge(H * 0.62, 1.0, [(16, 700), (7, 260)], 8)
	poly_line(d, mid + [(W + 20, H), (-20, H)], MID, MID_LINE, 3)
	rnd = random.Random(11)
	for cx in (120, 190, 640, 700, 760, 1180, 1520, 1585, 1840):
		gy = min(y for x, y in mid if abs(x - cx) < 10) + 6
		sc = 0.8 + rnd.random() * 0.5
		d.rectangle([S(cx - 4 * sc), S(gy - 18 * sc), S(cx + 4 * sc), S(gy)], fill=TREE_LINE)
		blob(im, cx, gy - 34 * sc, [(-14 * sc, 6 * sc, 16 * sc), (12 * sc, 4 * sc, 17 * sc), (0, -10 * sc, 20 * sc)], TREE, TREE_LINE, 2.6, TREE_SH)
	# พื้นหญ้าหน้า (เส้นพื้น 73%)
	gy = H * GROUND
	grass = [(x, gy + 2.5 * math.sin(x / 140) + 1.5 * math.sin(x / 47)) for x in range(-20, W + 21, 6)]
	poly_line(d, grass + [(W + 20, H + 10), (-20, H + 10)], GRASS, GRASS_LINE, 3.2)
	# ทางดิน (ที่ตัวละครยืน ~80–100%) ขอบโค้งนุ่ม
	top = [(x, H * 0.815 + 4 * math.sin(x / 210 + 1) + 2 * math.sin(x / 63)) for x in range(-20, W + 21, 6)]
	poly_line(d, top + [(W + 20, H + 10), (-20, H + 10)], DIRT, DIRT_LINE, 3)
	# รอยดิน/กอหญ้าเล็กๆ (น้อยๆ ให้ตาพัก)
	rnd = random.Random(5)
	for _ in range(26):
		x, y = rnd.uniform(0, W), rnd.uniform(H * 0.85, H * 0.98)
		d.ellipse([S(x - 14), S(y - 2.5), S(x + 14), S(y + 2.5)], fill=DIRT_SH)
	for _ in range(34):
		x, y = rnd.uniform(0, W), rnd.uniform(H * 0.745, H * 0.80)
		for k in (-5, 0, 5):
			d.line([(S(x + k * 0.6), S(y + 6)), (S(x + k), S(y - 3 - abs(4 - abs(k))))], fill=GRASS_SH, width=S(2))
	return im.resize((W, H), Image.LANCZOS)

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'w').close()
	build().save(os.path.join(OUT, 'act1.png'), optimize=True)
	print('→', os.path.join(OUT, 'act1.png'))
