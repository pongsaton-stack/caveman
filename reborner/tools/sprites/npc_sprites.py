# tools/sprites/npc_sprites.py — NPC ชาวบ้าน (ร่าง · ยังไม่เข้าเกม)
# ทำจากร่าง Rion มุมหน้า: เปลี่ยนสีตามโซน (หมวก/ผม/เสื้อ/กางเกง/เป้/รองเท้า) แล้วสวมอุปกรณ์ทับ (หมวก เครา ผ้ากันเปื้อน ไม้เท้า ...)
# ทุกคนสไตล์เดียวกับตัวเอก · เด็กย่อ 0.8 · ท่า: ยืนหายใจ · คุย (พยักหน้า + ...) · เดินหน้า
# รายชื่อ: docs/art-bible/world/npcs.json · ผล: assets/sprites/npcs_draft/<id>_<i>.png
import json, os
from PIL import Image
from pixkit import Sprite, ramp
import poses_anim as PA

ROOT = PA.ROOT
OUT = os.path.join(ROOT, 'assets/sprites/npcs_draft')
R = os.path.join(ROOT, 'assets/sprites/rion_lastlight_draft/')
hx = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
BLUES = {hx(c) for c in ('#507895', '#395472', '#4c6880', '#7a8993')}
BROWNS = {hx(c) for c in ('#825335', '#653a21', '#412c1e', '#2f1b10', '#9a6038', '#3e2214', '#21160f')}
CLOTH = {hx(c) for c in ('#d2bd9a', '#6c5947', '#383a37', '#7a8993')}
SKIN = {hx('#d4b08a'): 3, hx('#b37a55'): 1}

def zone(x, y, c):
	if c in BLUES and y <= 22: return 'cap'
	if c in BROWNS and y <= 33: return 'hair'
	if c in BLUES and y >= 44: return 'pants'
	if c in BROWNS and y >= 57: return 'shoes'
	if c in CLOTH and 30 <= y <= 56 and 20 <= x <= 44: return 'shirt'
	if c in BROWNS and 30 <= y <= 57: return 'pack'
	if c in SKIN: return 'skin'
	return None

def recolor(im, pal):
	"""pal: โซน → สีฐาน · ไล่เฉดตามความสว่างของสีเดิมในโซนนั้น · 'cap': 'hair' = ถอดหมวกเหลือผม"""
	src = im.load(); groups = {}
	for y in range(64):
		for x in range(64):
			p = src[x, y]
			if p[3]:
				z = zone(x, y, p[:3])
				if z: groups.setdefault(z, set()).add(p[:3])
	lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
	maps = {}
	for z, cols in groups.items():
		base = pal.get(z if not (z == 'cap' and pal.get('cap') == 'hair') else 'hair')
		if z == 'cap' and pal.get('cap') == 'hair': base = pal.get('hair')
		if not base: continue
		rp = ramp(base); srt = sorted(cols, key=lum)
		for i, c in enumerate(srt): maps[(z, c)] = rp[1 + round(3 * i / max(1, len(srt) - 1))]
	out = im.copy(); o = out.load()
	for y in range(64):
		for x in range(64):
			p = src[x, y]
			if p[3]:
				z = zone(x, y, p[:3])
				if (z, p[:3]) in maps: o[x, y] = maps[(z, p[:3])] + (255,)
				elif z == 'skin' and 'skin' in pal: o[x, y] = ramp(pal['skin'])[SKIN[p[:3]]] + (255,)
	return out

# ── อุปกรณ์ (มุมหน้า ผืน 64x64 เดียวกับตัว) ──
def acc_layer(items, seed):
	front, back = Sprite(64, 64, seed), Sprite(64, 64, seed + 'b')
	for a in items:
		k, *arg = a if isinstance(a, tuple) else (a,)
		col = arg[0] if arg else None
		if k == 'straw_hat':
			front.part(col or (214, 180, 100), lambda d: d.ellipse([8, 11, 56, 19]), tex=0.3); front.part(col or (214, 180, 100), lambda d: d.chord([18, 1, 46, 23], 180, 360), tex=0.3)
			front.part((150, 60, 50), lambda d: d.rectangle([19, 10, 45, 12]), tex=0)
		elif k == 'scarf_head':
			front.part(col, lambda d: (d.chord([15, 3, 49, 27], 180, 360), d.rectangle([15, 15, 17, 22]), d.rectangle([47, 15, 49, 22])), tex=0.15)
		elif k == 'helmet':
			front.part(col or (120, 126, 120), lambda d: (d.chord([15, 2, 49, 30], 180, 360), d.rectangle([13, 14, 51, 17])), tex=0.2)
		elif k == 'hood':
			front.part(col, lambda d: (d.chord([11, 1, 53, 34], 180, 360), d.rectangle([11, 17, 17, 36]), d.rectangle([47, 17, 53, 36])), tex=0.2)
		elif k == 'headband':
			front.part(col, lambda d: d.rectangle([15, 13, 49, 15]), tex=0)
		elif k == 'goggles':
			front.part((60, 56, 52), lambda d: d.rectangle([16, 9, 48, 11]), tex=0)
			for x in (24, 36): front.part((120, 180, 190), lambda d, x=x: d.ellipse([x - 4, 6, x + 4, 14]), tex=0.05)
		elif k == 'glasses':
			for x in (26, 38): front.part((60, 50, 40), lambda d, x=x: d.ellipse([x - 3, 19, x + 3, 25], fill=None, outline=255), light=False, tex=0, outline=False)
		elif k == 'beard':
			front.part(col or (200, 200, 196), lambda d: d.polygon([(26, 30), (38, 30), (36, 35), (32, 37), (28, 35)]), tex=0.3)
		elif k == 'apron':
			front.part(col, lambda d: (d.rectangle([23, 37, 41, 56]), d.line([(24, 37), (21, 31)], fill=255), d.line([(40, 37), (43, 31)], fill=255)), tex=0.15)
		elif k == 'shawl':
			front.part(col, lambda d: d.polygon([(17, 34), (47, 34), (45, 41), (32, 46), (19, 41)]), tex=0.25)
		elif k == 'vest':
			front.part(col, lambda d: (d.rectangle([20, 33, 27, 52]), d.rectangle([37, 33, 44, 52])), tex=0.25)
		elif k == 'cane':
			front.part((110, 80, 56), lambda d: (d.line([(50, 40), (51, 63)], fill=255, width=2), d.line([(46, 40), (51, 40)], fill=255, width=2)))
		elif k == 'spear':
			front.part((110, 80, 56), lambda d: d.line([(52, 4), (52, 63)], fill=255, width=2))
			front.part((170, 176, 180), lambda d: d.polygon([(50, 6), (53, -2), (55, 6)]), tex=0)
		elif k == 'hoe':
			front.part((110, 80, 56), lambda d: d.line([(51, 10), (51, 63)], fill=255, width=2)); front.part((140, 146, 150), lambda d: d.polygon([(46, 8), (52, 8), (52, 14), (48, 12)]), tex=0)
		elif k == 'hammer':
			front.part((110, 80, 56), lambda d: d.line([(48, 44), (54, 34)], fill=255, width=2)); front.part((100, 104, 110), lambda d: d.rectangle([50, 29, 58, 34]), tex=0.1)
		elif k == 'basket':
			front.part((180, 140, 80), lambda d: (d.rectangle([44, 44, 54, 52]), d.arc([44, 38, 54, 50], 180, 360, fill=255, width=1)), tex=0.4)
			front.part((90, 160, 80), lambda d: d.ellipse([45, 41, 53, 46]), tex=0.2)
		elif k == 'ladle':
			front.part((150, 150, 146), lambda d: (d.line([(50, 32), (50, 46)], fill=255, width=1), d.ellipse([47, 44, 53, 49])), tex=0)
		elif k == 'big_pack':
			back.part(col or (120, 90, 60), lambda d: d.rounded_rectangle([12, 4, 52, 44], 4), tex=0.3)
			back.part((150, 150, 146), lambda d: d.ellipse([40, 0, 50, 10]), tex=0.1)          # หม้อห้อยบนเป้
			back.part((180, 60, 50), lambda d: d.rectangle([14, 8, 22, 14]), tex=0.1)
		elif k == 'sack':
			front.part((170, 150, 110), lambda d: d.ellipse([42, 36, 58, 54]), tex=0.35)
		elif k == 'book':
			front.part((60, 50, 90), lambda d: d.rectangle([43, 40, 52, 50]), tex=0.1)
	return front.im, back.im

def build(base, spec):
	body = recolor(base, spec['pal'])
	if spec.get('hunch'): body = PA.shift_part(body, lambda x, y: y < 31, 0, 2, keep=True)   # หลังค่อม: หัวต่ำลง
	front, back = acc_layer(spec.get('acc', []), spec['id'])
	im = Image.new('RGBA', (64, 64)); im.alpha_composite(back); im.alpha_composite(body); im.alpha_composite(front)
	return im

def place(im, scale=1.0):
	c = Image.new('RGBA', (64, 64 + PA.TOP))
	if scale != 1.0:
		w = round(64 * scale); im = im.resize((w, w), Image.NEAREST); c.alpha_composite(im, ((64 - w) // 2, 64 + PA.TOP - w))
	else: c.alpha_composite(im, (0, PA.TOP))
	return c

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'w').close()
	for f in os.listdir(OUT):
		if f.endswith('.png'): os.remove(os.path.join(OUT, f))
	npcs = json.load(open(os.path.join(ROOT, 'docs/art-bible/world/npcs.json'), encoding='utf-8'))['npcs']
	S = Image.open(R + 'south.png').convert('RGBA'); WALK = [Image.open(R + 'south_w%d.png' % i).convert('RGBA') for i in range(4)]
	for n in npcs:
		spec = dict(n, pal={k: hx(v) if isinstance(v, str) and v.startswith('#') else v for k, v in n['pal'].items()},
			acc=[tuple(a) if isinstance(a, list) else a for a in n.get('acc', [])])
		spec['acc'] = [(a[0], hx(a[1])) if isinstance(a, tuple) and len(a) > 1 else a for a in spec['acc']]
		sc = n.get('scale', 1.0); stand = build(S, spec)
		frames = [stand, PA.breathe(stand, 40)]                                                # 0-1 ยืนหายใจ
		t1 = PA.shift_part(stand, lambda x, y: y < 33, 0, 1); frames += [stand, t1]             # 2-3 คุย
		frames += [build(w, spec) for w in WALK]                                                # 4-7 เดิน
		for i, f in enumerate(frames):
			c = place(f, sc)
			if i == 3: PA.glyph(c, 'dots', 44, PA.TOP - 6 + round(64 * (1 - sc)))
			c.save(os.path.join(OUT, '%s_%d.png' % (n['id'], i)))
	print('ok', len(npcs), 'npcs')
