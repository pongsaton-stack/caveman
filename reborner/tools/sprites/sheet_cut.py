# tools/sprites/sheet_cut.py — ตัดสไปรต์ชีต (เช่นที่ PixelLab/ตัวเจนภาพทำมา) เป็นคลิปพิกเซลพร้อมใช้
#
#   python3 tools/sprites/sheet_cut.py <ชีต.png|jpg> <ชื่อคลิป> [ตัวเลือก]
#
# ขั้นตอน (ทุกขั้นอัตโนมัติ ปรับได้ด้วยตัวเลือก):
#   1. ลบพื้น — ภาพมีความโปร่งอยู่แล้วใช้เลย · ไม่มี = เอาสีขอบชีต (รวมพื้นตารางหมากรุกปลอม 2 สี) แล้วเทจากขอบเข้าไป
#   2. หาเฟรม — --grid CxR แบ่งช่องเท่ากัน · ไม่ใส่ = หาแถว/คอลัมน์ว่างคั่น (ช่องว่างเล็กกว่า --gap ถือว่าเป็นตัวเดียวกัน)
#   3. ย่อ — หาขนาด "พิกเซลปลอม" เอง (ภาพพิกเซลที่ขยายมา k เท่า) · หาไม่เจอ = ย่อทุกเฟรมด้วยอัตราเดียวกันให้เฟรมสูงสุดสูง --height
#      ใช้ "สีที่มากที่สุดในบล็อก" (ไม่เบลอ ไม่เกิดสีใหม่) · ทุกเฟรมอัตราเดียวกัน → ขนาดตัวละครไม่กระเพื่อม
#   4. ล็อกสี — ทุกพิกเซลเป็นสีที่ใกล้สุดในพาเลตต์ (--palette rion|dog|master|autoN|none|<ไฟล์ png/hex>)
#      autoN = ตัวที่ยังไม่มีพาเลตต์ (มอนใหม่): ลดสีรวมทุกเฟรมเหลือ N สี ทุกเฟรมได้ชุดเดียวกัน
#   5. จัดเท้า — แถวล่างสุดของทุกเฟรมลงเส้นเดียวกัน (--baseline) · แนวนอนใช้จุดศูนย์ถ่วงของตัว (ไม่สั่นซ้ายขวา)
#      --keep-y = คงระยะสูงต่ำเดิมในแถวของชีต (ท่ากระโดด) แทนการวางเท้าทุกเฟรมบนพื้น
#   6. เขียน <out>/<ชื่อ>_<i>.png + <ชื่อ>_sheet.png (ดูตรวจ ขยาย 4 เท่า) + <ชื่อ>.json (ขนาด/อัตราย่อ/กรอบในชีต) [+ .aseprite]
#
# ค่าเริ่มต้นตรงกับ Rion ในเกม: ผืน 64x64 · เท้าแถว 62 · พาเลตต์ Rion · ออกที่ assets/sprites/sheet_cut_draft/ (.gdignore = ร่าง ไม่เข้าเกม)
# ไม่มีตัวเลขเกมในไฟล์นี้ — เป็นค่ารูปภาพทั้งหมด
import argparse, glob, json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT_DEFAULT = os.path.join(ROOT, 'assets/sprites/sheet_cut_draft')
PALETTES = {
	'rion': 'assets/sprites/rion_lastlight_draft/*.png',
	'dog': 'assets/sprites/dog_lastlight_draft/*.png',
	'master': 'docs/art-bible/master_palette.hex',
}


# ── 1. ลบพื้น ──
def border_colors(a, cover=0.9, tol=24):
	"""สีพื้นจากขอบชีต: สีหลักที่รวมกันครอบขอบ ≥ cover (พื้นเรียบ = 1 สี · ตารางหมากรุกปลอม = 2 สี)"""
	b = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])[:, :3].astype(int)
	q = (b // 8) * 8 + 4
	cols, cnt = np.unique(q, axis=0, return_counts=True)
	order = cnt.argsort()[::-1]; out = []; got = 0
	for i in order[:4]:
		c = b[(np.abs(q - cols[i]).max(1) == 0)].mean(0)
		if not any(np.abs(c - o).max() < tol for o in out): out.append(c)
		got += cnt[i]
		if got >= cover * len(b): break
	return out

def remove_bg(a, tol=24):
	"""คืน alpha ใหม่ (0/255) · ภาพที่โปร่งอยู่แล้วใช้ alpha เดิม (ตัดครึ่งโปร่งที่ 128)"""
	al = a[..., 3]
	if (al < 16).mean() > 0.05: return np.where(al >= 128, 255, 0).astype(np.uint8), 'alpha'
	rgb = a[..., :3].astype(int)
	near = np.zeros(al.shape, bool)
	for c in border_colors(a, tol=tol): near |= np.abs(rgb - c).max(2) <= tol
	lab, _ = ndimage.label(near)
	edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
	bg = np.isin(lab, list(edge))
	return np.where(bg, 0, 255).astype(np.uint8), 'flood'


# ── 2. หาเฟรม ──
def runs(mask1d, gap, minlen):
	"""ช่วงที่มีภาพตามแกนเดียว · ช่องว่าง < gap เชื่อมเป็นช่วงเดียว · ช่วงสั้นกว่า minlen ทิ้ง (ฝุ่น)"""
	idx = np.where(mask1d)[0]
	if not len(idx): return []
	out = [[idx[0], idx[0]]]
	for i in idx[1:]:
		if i - out[-1][1] - 1 < gap: out[-1][1] = i
		else: out.append([i, i])
	return [(s, e + 1) for s, e in out if e + 1 - s >= minlen]

def find_frames(al, grid=None, gap=None, minlen=None):
	"""กรอบเฟรม (x0,y0,x1,y1) เรียงซ้าย→ขวา บน→ล่าง · แถว = หมายเลขแถวในชีต"""
	H, W = al.shape; op = al > 0
	if grid:
		c, r = grid; out = []
		for j in range(r):
			for i in range(c):
				x0, x1 = W * i // c, W * (i + 1) // c; y0, y1 = H * j // r, H * (j + 1) // r
				if op[y0:y1, x0:x1].any(): out.append(((x0, y0, x1, y1), j))
		return out
	gap = gap or max(2, min(H, W) // 100); minlen = minlen or max(3, min(H, W) // 60)
	out = []
	for j, (y0, y1) in enumerate(runs(op.any(1), gap, minlen)):
		for x0, x1 in runs(op[y0:y1].any(0), gap, minlen):
			out.append(((x0, y0, x1, y1), j))
	return out

def tighten(op, box):
	x0, y0, x1, y1 = box; sub = op[y0:y1, x0:x1]
	ys, xs = np.where(sub)
	return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1) if len(xs) else None


# ── 3. ย่อ ──
def _edges(rgb, op, axis):
	d = np.abs(np.diff(rgb.astype(int), axis=axis)).max(2) > 24
	return d & ((op[:, 1:] | op[:, :-1]) if axis == 1 else (op[1:] | op[:-1]))

def pixel_scale(rgb, op, kmax=24):
	"""ขนาดพิกเซลปลอม k: ภาพพิกเซลที่ขยาย k เท่า ระยะระหว่างจุดเปลี่ยนสีที่ติดกันในแถว/คอลัมน์เป็นพหุคูณของ k เสมอ
	(ไม่ขึ้นกับว่าแต่ละเฟรมวางเหลื่อมกันเท่าไร) · คืน (k, ความมั่นใจ 0-1) · ภาพวาด/เบลอ → มั่นใจต่ำ → ใช้ --height แทน"""
	gaps = []
	for axis in (1, 0):
		e = _edges(rgb, op, axis); e = e if axis == 1 else e.T
		for row in e:
			i = np.where(row)[0]
			if len(i) > 1: gaps.append(np.diff(i))
	if not gaps: return 1, 0.0
	g = np.concatenate(gaps)
	if len(g) < 50: return 1, 0.0
	best = (1, 0.0)
	for k in range(2, kmax + 1):
		f = (g % k == 0).mean()
		if f >= 0.8: best = (k, f)   # k ใหญ่สุดที่ยังลงตัว (2 กับ 3 ลงตัวทั้งคู่ถ้า k จริง = 6)
	return best

def phase(pos, k):
	return int(np.bincount(pos % k, minlength=k).argmax()) if len(pos) else 0

def block_mode(rgb, op, s, ox=0.0, oy=0.0, fill=0.5):
	"""ย่อด้วยสีที่มากที่สุดในบล็อก (บล็อกกว้าง s ไม่จำเป็นต้องเป็นจำนวนเต็ม) · บล็อกที่ทึบ < fill = โปร่ง"""
	H, W = op.shape
	w, h = int(math.ceil((W - ox) / s)), int(math.ceil((H - oy) / s))
	out = np.zeros((h, w, 4), np.uint8)
	q = (rgb.astype(int) // 6) * 6
	for y in range(h):
		ya, yb = int(round(oy + y * s)), int(round(oy + (y + 1) * s))
		for x in range(w):
			xa, xb = int(round(ox + x * s)), int(round(ox + (x + 1) * s))
			m = op[ya:yb, xa:xb]
			if m.size == 0 or m.mean() < fill: continue
			px = q[ya:yb, xa:xb][m]; raw = rgb[ya:yb, xa:xb][m]
			cols, inv, cnt = np.unique(px, axis=0, return_inverse=True, return_counts=True)
			k = cnt.argmax(); out[y, x, :3] = raw[inv.ravel() == k].mean(0).round(); out[y, x, 3] = 255
	return out


# ── 4. ล็อกสี ──
def load_palette(spec):
	if spec in (None, 'none'): return None
	src = PALETTES.get(spec, spec)
	cols = set()
	if src.endswith('.hex'):
		for ln in open(os.path.join(ROOT, src) if not os.path.isabs(src) else src, encoding='utf-8'):
			ln = ln.split(';')[0].strip().lstrip('#')
			if len(ln) == 6: cols.add(tuple(int(ln[i:i + 2], 16) for i in (0, 2, 4)))
	else:
		paths = glob.glob(os.path.join(ROOT, src) if not os.path.isabs(src) else src)
		if not paths: sys.exit(f'ไม่เจอพาเลตต์ {spec}')
		for p in paths:
			a = np.asarray(Image.open(p).convert('RGBA'))
			cols |= {tuple(c) for c in a[a[..., 3] > 0][:, :3]}
	return np.array(sorted(cols), int)

def auto_palette(frames, n):
	px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames])
	q = Image.fromarray(px[None].astype(np.uint8), 'RGB').quantize(n, Image.Quantize.MEDIANCUT)
	cols = np.array(q.getpalette()[:3 * n], int).reshape(-1, 3)
	return np.unique(cols[np.unique(np.asarray(q))], axis=0)

def lock(img, pal):
	"""สีที่ใกล้สุดแบบถ่วงน้ำหนักการรับรู้ (เขียวหนักสุด) · คืน (ภาพ, ระยะเฉลี่ย)"""
	if pal is None: return img, 0.0
	op = img[..., 3] > 0; px = img[op][:, :3].astype(int)
	if not len(px): return img, 0.0
	w = np.array([2, 4, 3])
	d = (((px[:, None, :] - pal[None]) ** 2) * w).sum(2)
	i = d.argmin(1); out = img.copy(); out[op, :3] = pal[i]
	return out, float(np.sqrt(d[np.arange(len(i)), i] / w.sum()).mean())

def drop_orphans(img):
	"""ลบจุดทึบเดี่ยวที่ไม่ติดอะไรเลย (เศษพื้นที่ลบไม่หมด)"""
	op = img[..., 3] > 0
	n = ndimage.convolve(op.astype(int), np.ones((3, 3), int), mode='constant') - op
	out = img.copy(); out[op & (n == 0)] = 0
	return out


# ── 5. จัดเท้า ──
def place(frames, size, baseline, keep_y=None):
	"""วางทุกเฟรมบนผืนเดียวกัน · เท้า (แถวล่างสุด) ลง baseline · x = จุดศูนย์ถ่วงของตัวกลางผืน
	keep_y = [ระยะจากพื้นของแถวในชีต (ย่อแล้ว)] → ยกเฟรมนั้นขึ้นตามเดิม"""
	W, H = size; out = []; info = []
	for n, f in enumerate(frames):
		op = f[..., 3] > 0; ys, xs = np.where(op)
		cx = xs.mean(); bot = ys.max()
		dx = int(round(W / 2 - cx))
		if xs.max() - xs.min() < W: dx = min(max(dx, -int(xs.min())), W - 1 - int(xs.max()))   # ตัวยาวข้างเดียว (ท่าพุ่ง) เลื่อนเข้าผืน
		dy = int(baseline - bot - (keep_y[n] if keep_y else 0))
		can = np.zeros((H, W, 4), np.uint8)
		fy0, fx0 = max(0, -dy), max(0, -dx); ty0, tx0 = max(0, dy), max(0, dx)
		h = min(f.shape[0] - fy0, H - ty0); w = min(f.shape[1] - fx0, W - tx0)
		clipped = h < f.shape[0] or w < f.shape[1]
		if h > 0 and w > 0: can[ty0:ty0 + h, tx0:tx0 + w] = f[fy0:fy0 + h, fx0:fx0 + w]
		out.append(can); info.append({'dx': dx, 'dy': dy, 'clipped': bool(clipped)})
	return out, info


def cut(src, name, out=OUT_DEFAULT, grid=None, gap=None, height=None, scale=None, palette='rion',
		size=(64, 64), baseline=62, keep_y=False, aseprite=False, ms=100, tol=24, fill=0.5, verbose=True):
	a = np.asarray(Image.open(src).convert('RGBA'))
	al, how = remove_bg(a, tol)
	op = al > 0
	boxes = find_frames(al, grid, gap)
	if not boxes: sys.exit('ไม่เจอเฟรมในชีต')
	tight = [(tighten(op, b), r) for b, r in boxes]
	tight = [(b, r) for b, r in tight if b]
	k, conf = pixel_scale(a[..., :3], op)
	if scale: s, mode = float(scale), 'กำหนดเอง'
	elif conf >= 0.8 and k > 1: s, mode = float(k), f'พิกเซลปลอม k={k} (มั่นใจ {conf:.2f})'
	else:
		target = height or (size[1] - 8)
		sh = max(b[3] - b[1] for b, _ in tight) / target
		sw = max(b[2] - b[0] for b, _ in tight) / (size[0] - 4)   # ตัวกว้าง (สไลม์ ฯลฯ) ต้องไม่ล้นผืนด้านข้าง
		s = max(sh, sw)
		mode = (f'ย่อให้เฟรมสูงสุดสูง {target}px' if sh >= sw else f'ย่อให้เฟรมกว้างสุดกว้าง {size[0] - 4}px') + f' (ไม่เจอพิกเซลปลอม · มั่นใจ {conf:.2f})'
	pal = None if palette.startswith('auto') else load_palette(palette)
	frames, dists, meta = [], [], []
	pixel = mode.startswith('พิกเซลปลอม')
	for (x0, y0, x1, y1), r in tight:
		if pixel:   # ต่อกริดพิกเซลเดิมของเฟรมนี้ ไม่ตัดกลางบล็อก (แต่ละเฟรมในชีตวางเหลื่อมกันได้)
			sub, so = a[y0:y1, x0:x1, :3], op[y0:y1, x0:x1]
			x0 = max(0, x0 - (-phase(np.where(_edges(sub, so, 1))[1] + 1, k)) % k)
			y0 = max(0, y0 - (-phase(np.where(_edges(sub, so, 0))[0] + 1, k)) % k)
		small = block_mode(a[y0:y1, x0:x1, :3], op[y0:y1, x0:x1], s, fill=fill)
		small = drop_orphans(small)
		if not (small[..., 3] > 0).any(): continue
		frames.append(small); meta.append({'box': [int(x0), int(y0), int(x1), int(y1)], 'row': r})
	if palette.startswith('auto'):   # ไม่มีพาเลตต์ให้: ลดสีรวมทุกเฟรมพร้อมกัน (median cut) → ทุกเฟรมใช้ชุดสีเดียวกัน
		pal = auto_palette(frames, int(palette[4:] or 16))
	for i, f in enumerate(frames):
		frames[i], d = lock(f, pal); dists.append(d)
	lift = None
	if keep_y:   # ระยะจากเท้าต่ำสุดของแถวเดียวกันในชีต (หน่วยพิกเซลที่ย่อแล้ว)
		low = {}
		for m in meta: low[m['row']] = max(low.get(m['row'], 0), m['box'][3])
		lift = [int(round((low[m['row']] - m['box'][3]) / s)) for m in meta]
	placed, info = place(frames, size, baseline, lift)
	os.makedirs(out, exist_ok=True)
	gd = os.path.join(out, '.gdignore')
	if not os.path.exists(gd): open(gd, 'w').close()
	for old in glob.glob(os.path.join(out, f'{name}_[0-9]*.png')): os.remove(old)
	files = []
	for i, f in enumerate(placed):
		p = os.path.join(out, f'{name}_{i}.png'); Image.fromarray(f, 'RGBA').save(p); files.append(os.path.basename(p))
	W, H = size; strip = Image.new('RGBA', (W * len(placed), H + 1), (60, 64, 72, 255))
	for i, f in enumerate(placed): strip.alpha_composite(Image.fromarray(f, 'RGBA'), (i * W, 0))
	for x in range(strip.width): strip.putpixel((x, baseline + 1), (200, 90, 80, 255))   # เส้นพื้น
	strip.resize((strip.width * 4, strip.height * 4), Image.NEAREST).save(os.path.join(out, f'{name}_sheet.png'))
	rep = {
		'source': os.path.relpath(src, ROOT) if src.startswith(ROOT) else os.path.basename(src),
		'background': how, 'frames': len(placed), 'size': list(size), 'baseline': baseline,
		'scale': round(s, 3), 'scale_mode': mode, 'palette': palette,
		'palette_dist': round(float(np.mean(dists)), 1) if dists else 0,
		'ms': ms, 'files': files,
		'cells': [dict(m, **inf) for m, inf in zip(meta, info)],
	}
	json.dump(rep, open(os.path.join(out, f'{name}.json'), 'w'), ensure_ascii=False, indent=1)
	if aseprite:
		sys.path.insert(0, HERE); import aseprite_io
		aseprite_io.write(os.path.join(out, f'{name}.aseprite'), [Image.fromarray(f, 'RGBA') for f in placed],
			[ms] * len(placed), [(name, 0, len(placed) - 1)])
	if verbose:
		print(f'{name}: {len(placed)} เฟรม · พื้น={how} · {mode} · อัตรา {s:.2f} · พาเลตต์ {palette} (ห่างเฉลี่ย {rep["palette_dist"]})')
		cl = [i for i, x in enumerate(info) if x['clipped']]
		if cl: print(f'  ⚠ เฟรมล้นผืน {size[0]}x{size[1]}: {cl} — เพิ่ม --size หรือลด --height')
	return rep, placed


def main():
	ap = argparse.ArgumentParser(description='ตัดสไปรต์ชีตเป็นคลิปพิกเซล')
	ap.add_argument('sheet'); ap.add_argument('name')
	ap.add_argument('--out', default=OUT_DEFAULT)
	ap.add_argument('--grid', help='CxR เช่น 8x1 (ไม่ใส่ = หาเอง)')
	ap.add_argument('--gap', type=int, help='ช่องว่างขั้นต่ำระหว่างเฟรม (พิกเซลชีต)')
	ap.add_argument('--height', type=int, help='ความสูงเฟรมสูงสุดหลังย่อ (ใช้เมื่อหาพิกเซลปลอมไม่เจอ)')
	ap.add_argument('--scale', type=float, help='บังคับอัตราย่อ (พิกเซลชีตต่อ 1 พิกเซล)')
	ap.add_argument('--palette', default='rion', help='rion | dog | master | auto16 (ลดสีเอง N สี) | none | ไฟล์ .png/.hex/glob')
	ap.add_argument('--size', default='64x64', help='ผืนต่อเฟรม WxH')
	ap.add_argument('--baseline', type=int, help='แถวเท้า (ค่าเริ่ม = สูงผืน - 2)')
	ap.add_argument('--keep-y', action='store_true', help='คงระยะสูงต่ำเดิม (ท่ากระโดด)')
	ap.add_argument('--ms', type=int, default=100, help='ms ต่อเฟรม (ใช้ใน .aseprite/หน้าเทส)')
	ap.add_argument('--tol', type=int, default=24, help='ความต่างสีที่ยังนับเป็นพื้น')
	ap.add_argument('--aseprite', action='store_true', help='เขียน .aseprite ด้วย')
	g = ap.parse_args()
	W, H = map(int, g.size.lower().split('x'))
	cut(g.sheet, g.name, g.out, tuple(map(int, g.grid.lower().split('x'))) if g.grid else None, g.gap, g.height, g.scale,
		g.palette, (W, H), g.baseline if g.baseline is not None else H - 2, g.keep_y, g.aseprite, g.ms, g.tol)

if __name__ == '__main__':
	main()
