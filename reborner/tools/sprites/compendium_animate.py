# tools/sprites/compendium_animate.py — ทำสไปรต์ 64px + ท่าขยับ 4 ท่า จากภาพในชีต Monster Compendium โดยไม่ใช้ตัวเจนภาพ
# ขั้น: ตัดตัวใหญ่สุดในช่อง (compendium_cut) → เร่งคม → ย่อ (BOX) → ลดสี ≤16 → ตัดขอบโปร่งแข็ง → ลบจุดโดด → เส้นขอบ hue-shift
# ท่า: idle1 = ตัวหลัก · idle2 = ยุบ 1 จุด กว้างขึ้น 1 · attack = เอียงพุ่งไปขวา + ยืดตามแนวนอน · hit = เอียงถอยซ้าย + สว่างวาบ
# ผล: assets/sprites/compendium_anim/<id>_{idle1,idle2,attack,hit}.png (ช่อง 80x64) — ร่าง ยังไม่เข้าเกม
import os, sys, json
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compendium_cut as cc
from ll_polish import hue_outline

ROOT = cc.ROOT
OUT = os.path.join(ROOT, 'assets/sprites/compendium_anim')
LONG = 56            # ด้านยาวสุดของตัว (จุด)
CW, CH = 80, 64      # ช่องเผื่อที่ให้ท่าพุ่ง/ถอย

def largest_blob(sp):
	"""ช่องที่วาดหลายตัวชิดกัน (สไลม์ 4 ตัว) — เก็บก้อนใหญ่สุด · ตัดเงาพื้นสีอ่อนใต้ตัว"""
	from scipy import ndimage as nd
	a = np.asarray(sp).copy(); m = a[..., 3] > 0
	r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
	shadow = m & (r > 170) & (g > 145) & (b > 115) & (r - b < 80) & (np.arange(m.shape[0])[:, None] > m.shape[0] * 0.8)
	m &= ~shadow
	lab, n = nd.label(nd.binary_closing(m, iterations=1))
	if n > 1:
		sizes = nd.sum(m, lab, range(1, n + 1)); keep = lab == (int(np.argmax(sizes)) + 1)
		m &= keep
	a[..., 3] = np.where(m, 255, 0)
	im = Image.fromarray(a, 'RGBA'); return im.crop(im.getbbox())

def crisp(sp, long=LONG, colors=16):
	sp = largest_blob(sp)
	a = np.asarray(sp)[..., 3]
	rgb = sp.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=170, threshold=2))
	k = long / max(sp.size)
	w, h = max(1, round(sp.width * k)), max(1, round(sp.height * k))
	small = rgb.resize((w, h), Image.BOX)
	al = Image.fromarray(a).resize((w, h), Image.BOX).point(lambda v: 255 if v >= 140 else 0)
	q = small.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
	out = Image.merge('RGBA', (*q.split(), al)); px = out.load()
	for _ in range(2):   # ลบจุดโดด/ติ่งพิกเซลเดียว
		kill = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] and
			sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3]) <= 1]
		for k2 in kill: px[k2] = (0, 0, 0, 0)
	return hue_outline(out)

def shear(im, k):
	"""เอียงตามแนวนอน: แถวบนเลื่อน k จุด แถวล่างอยู่กับที่"""
	w, h = im.size; pad = abs(int(k)) + 1
	out = Image.new('RGBA', (w + pad * 2, h), (0, 0, 0, 0))
	for y in range(h):
		dx = round(k * (1 - y / max(1, h - 1)))
		out.paste(im.crop((0, y, w, y + 1)), (pad + dx, y))
	return out.crop(out.getbbox())

def flash(im, amt=0.35):
	a = np.asarray(im).astype(float); m = a[..., 3] > 0
	a[m, :3] = a[m, :3] + (255 - a[m, :3]) * amt
	return Image.fromarray(a.astype('uint8'), 'RGBA')

def place(sp, dx=0):
	cv = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
	cv.paste(sp, ((CW - sp.width) // 2 + dx, CH - sp.height - 2), sp); return cv

def frames(sp):
	w, h = sp.size
	idle2 = sp.resize((w + 1, h - 1), Image.NEAREST)
	atk = shear(sp.resize((w + max(3, w // 7), h - 2), Image.NEAREST), max(4, h // 6))
	hit = flash(shear(sp, -max(2, h // 12)))
	return {'idle1': place(sp), 'idle2': place(idle2), 'attack': place(atk, 5), 'hit': place(hit, -4)}

def main(only=None):
	img = Image.open(cc.SRC).convert('RGB'); os.makedirs(OUT, exist_ok=True); done = []
	for key, th, box, names in cc.REGIONS:
		c, lab, cards = cc.cut_region(img, box, names)
		for n, (m, name) in enumerate(zip(cards, names)):
			fid = '%s_%02d_%s' % (key, n + 1, cc.slug(name))
			if only and fid not in only or not m['spr']: continue
			big = max(m['spr'], key=lambda t: (t[0][0].stop - t[0][0].start) * (t[0][1].stop - t[0][1].start))
			for k, f in frames(crisp(cc.to_rgba(c, lab, [big]))).items():
				f.save(os.path.join(OUT, '%s_%s.png' % (fid, k)))
			done.append(fid)
	return done

if __name__ == '__main__':
	print('ok', len(main(sys.argv[1:] or None)))
