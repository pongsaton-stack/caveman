# tools/sprites/tiles_ll.py — ไทล์แผนที่ + วัตถุ จากแผ่นที่ค่าย grok เจน (docs/art-bible/grok/)
# แผ่นต้นฉบับเป็นภาพวาดใหญ่บนพื้นกระดาษ → ครอปช่อง → ตัดพื้นกระดาษ → ย่อ → ลดสี → เส้นขอบ hue-shift
# พื้น (หญ้า/ดิน/น้ำ/หิน) ย่อเป็น 48px แล้วผ่า 4 ชิ้น 24px (`<name>_0..3`) ให้แมพวางสลับ ลายซ้ำจะห่างขึ้นเป็น 2 ช่อง
# รัน: <python+Pillow> tools/sprites/tiles_ll.py [out_dir]
import os, sys
from PIL import Image, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ll_cut
from ll_polish import hue_outline

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GROK = os.path.join(ROOT, 'docs/art-bible/grok/')
TILE = 24

# ช่องในแผ่น environment_tiles.jpg (1168x784 · 6x3 ช่อง ขนาด 172x168)
ENV_X = [28, 214, 401, 587, 774, 960]
ENV_Y = [103, 313, 527]
ENV = {(r, c): n for r, row in enumerate([
	['grass', 'dirt', 'water', 'road', 'ruins', 'stone'],
	['pine', 'bush', 'rock', 'fence', 'lamp', 'bridge'],
	['flowers', 'crate', 'barrel', 'ruin_wall', 'overgrown1', 'overgrown2']]) for c, n in enumerate(row)}
ENV_BOX = {n: (ENV_X[c], ENV_Y[r], ENV_X[c] + 172, ENV_Y[r] + 168) for (r, c), n in ENV.items()}
# วัตถุ: ครอปเข้าในกรอบช่อง 8px — ไม่งั้นเส้นกรอบกั้น flood fill ไว้ พื้นกระดาษข้างในหลุดติดมาด้วย
ENV_OBJ_BOX = {n: (b[0] + 8, b[1] + 8, b[2] - 8, b[3] - 8) for n, b in ENV_BOX.items()}

def quant(im, n):
	"""ลดสีเหลือ n สี (เฉพาะพิกเซลทึบ) ไม่ dither"""
	a = im.getchannel('A')
	q = im.convert('RGB').quantize(colors=n, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
	out = q.convert('RGBA'); out.putalpha(a.point(lambda v: 255 if v > 110 else 0))
	return out

def ground(name, size=48, inset=8, colors=10, tone=None):
	"""พื้นเต็มช่อง: ครอปข้างในกรอบ → ย่อ size → ลดสี · tone = ฟังก์ชันปรับสี (เช่น ทำดินเป็นเถ้า)"""
	src = Image.open(GROK + 'environment_tiles.jpg').convert('RGB')
	x0, y0, x1, y1 = ENV_BOX[name]
	im = src.crop((x0 + inset, y0 + inset, x1 - inset, y1 - inset)).resize((size, size), Image.LANCZOS)
	if tone:
		im = tone(im)
	return quant(im.convert('RGBA'), colors)

def split4(im):
	"""48px → 4 ชิ้น 24px: 0=ซ้ายบน 1=ขวาบน 2=ซ้ายล่าง 3=ขวาล่าง"""
	return [im.crop((x, y, x + TILE, y + TILE)) for y in (0, TILE) for x in (0, TILE)]

def obj(sheet, box, w, colors=14):
	"""วัตถุบนพื้นกระดาษ: ตัดพื้นด้วย flood fill (ll_cut) → ย่อกว้าง w (คงสัดส่วน) → ลดสี → เส้นขอบ"""
	ll_cut.SRC = GROK + sheet
	cut = ll_cut.cut(box, tol=70, shadow=True, fringe=2)
	h = max(1, round(cut.height * w / cut.width))
	small = cut.resize((w, h), Image.LANCZOS)
	return hue_outline(quant(small, colors))

def ash(im):
	"""ดิน → ดินเถ้า (ทุ่งเถ้า ภูมิภาค 1): ลดความอิ่มสี + ลดคอนทราสต์ (พื้นที่กว้างสุดของแมพ ต้องไม่แย่งสายตาจากตัวละคร)"""
	im = ImageEnhance.Color(im).enhance(0.35)
	im = ImageEnhance.Contrast(im).enhance(0.45)
	return ImageEnhance.Brightness(im).enhance(1.12)

def dark_stone(im):
	return ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.6)).enhance(0.55)

# อาคาร (buildings.jpg 1168x784 · 4x2)
BLD_BOX = {'house': (20, 25, 300, 310), 'shop': (310, 40, 590, 310), 'workshop': (595, 40, 865, 310),
	'clinic': (870, 40, 1150, 310), 'tent': (20, 400, 300, 650), 'water_tower': (320, 375, 580, 650),
	'generator': (595, 400, 865, 650), 'ruin': (850, 390, 1150, 650)}

def build(out):
	os.makedirs(out, exist_ok=True)
	made = []
	grounds = {'grass': ground('grass'), 'ash': ground('dirt', tone=ash, colors=6), 'water': ground('water', colors=8),
		'stone': ground('stone', tone=dark_stone, colors=8), 'road': ground('road')}
	for name, im in grounds.items():
		for i, part in enumerate(split4(im)):
			part.save(os.path.join(out, '%s_%d.png' % (name, i))); made.append('%s_%d' % (name, i))
	objs = {'ruins': ('environment_tiles.jpg', ENV_OBJ_BOX['ruins'], 24), 'rock': ('environment_tiles.jpg', ENV_OBJ_BOX['rock'], 22),
		'pine': ('environment_tiles.jpg', ENV_OBJ_BOX['pine'], 24), 'bush': ('environment_tiles.jpg', ENV_OBJ_BOX['bush'], 20),
		'lamp': ('environment_tiles.jpg', ENV_OBJ_BOX['lamp'], 16), 'flowers': ('environment_tiles.jpg', ENV_OBJ_BOX['flowers'], 18),
		'crate': ('environment_tiles.jpg', ENV_OBJ_BOX['crate'], 20), 'barrel': ('environment_tiles.jpg', ENV_OBJ_BOX['barrel'], 16),
		'shop': ('buildings.jpg', BLD_BOX['shop'], 56), 'house': ('buildings.jpg', BLD_BOX['house'], 64),
		'tent': ('buildings.jpg', BLD_BOX['tent'], 52), 'ruin_house': ('buildings.jpg', BLD_BOX['ruin'], 64)}
	for name, (sheet, box, w) in objs.items():
		obj(sheet, box, w).save(os.path.join(out, name + '.png')); made.append(name)
	return made

if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets/tiles_ll_draft/')
	print(len(build(out)), 'files ->', out)
