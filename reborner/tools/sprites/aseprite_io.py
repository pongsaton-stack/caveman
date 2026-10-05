# tools/sprites/aseprite_io.py — อ่าน/เขียนไฟล์ .aseprite ด้วย Python ล้วน (PIL + zlib)
# เขียนตามสเปกไฟล์ที่ Aseprite เปิดเผย (docs/ase-file-specs.md ใน repo aseprite) — ไม่ใช้/ไม่คัดลอกโค้ดของโปรแกรม
# ตัวโปรแกรม Aseprite เป็นสัญญา EULA ห้ามแจกจ่าย จึงไม่อยู่ใน repo นี้ · kwan เปิดไฟล์ที่ได้ใน Aseprite บนเครื่องตัวเอง
#
#   write(path, frames, durations, tags=[], layer='Layer')
#       frames = [PIL RGBA ขนาดเท่ากัน] · durations = ms ต่อเฟรม · tags = [(ชื่อ, เฟรมแรก, เฟรมสุดท้าย)]
#       เฟรมที่ภาพเหมือนกันเขียนเป็น linked cel (ไฟล์เล็ก และแก้ที่เดียวเปลี่ยนทุกเฟรมที่ลิงก์)
#   read(path) → Sprite(width, height, frames=[RGBA], durations=[ms], tags=[(ชื่อ, from, to, ทิศ)], layers=[ชื่อ])
#       รวมเลเยอร์ที่มองเห็น (ซ่อนทั้งกลุ่มถ้ากลุ่มซ่อน) ด้วยโหมดผสมปกติ + ความทึบเลเยอร์/cel · รองรับ RGBA / Grayscale / Indexed
#       ข้ามสิ่งที่เกมไม่ใช้: tilemap, slice, โหมดผสมอื่นที่ไม่ใช่ Normal (อ่านเป็น Normal และบอกใน .notes)
import struct, zlib
from collections import namedtuple
from PIL import Image

Sprite = namedtuple('Sprite', 'width height frames durations tags layers notes')
TAG_DIR = {0: 'forward', 1: 'reverse', 2: 'pingpong', 3: 'pingpong_reverse'}

# ── อ่าน ──
class _R:
	def __init__(self, b, o=0): self.b, self.o = b, o
	def take(self, fmt):
		v = struct.unpack_from('<' + fmt, self.b, self.o); self.o += struct.calcsize('<' + fmt); return v if len(v) > 1 else v[0]
	def bytes(self, n): v = self.b[self.o:self.o + n]; self.o += n; return v
	def string(self): n = self.take('H'); return self.bytes(n).decode('utf-8', 'replace')

def _to_rgba(raw, w, h, depth, palette, transparent, is_bg):
	if depth == 32: return Image.frombytes('RGBA', (w, h), raw)
	if depth == 16:
		ga = Image.frombytes('LA', (w, h), raw); return ga.convert('RGBA')
	px = []
	for i in raw[:w * h]:
		if i == transparent and not is_bg: px.append((0, 0, 0, 0))
		else: px.append(palette[i] if i < len(palette) else (0, 0, 0, 255))
	im = Image.new('RGBA', (w, h)); im.putdata(px); return im

def read(path):
	b = open(path, 'rb').read(); r = _R(b)
	size, magic, nframes, W, H, depth, flags, speed = r.take('IHHHHHIH')
	if magic != 0xA5E0: raise ValueError('ไม่ใช่ไฟล์ .aseprite: ' + path)
	r.o = 28; transparent = r.take('B'); r.o = 128
	layers, palette, tags, notes, new_pal = [], [(0, 0, 0, 255)] * 256, [], set(), False
	cels, durations = [], []                     # cels[f] = {layer: (x, y, opacity, Image)}
	for f in range(nframes):
		start = r.o; fbytes, fmagic, old_n, dur, _, new_n = r.take('IHHHHI')
		if fmagic != 0xF1FA: raise ValueError('เฟรม %d เสีย' % f)
		durations.append(dur or speed); cels.append({}); n = new_n or old_n
		for _ in range(n):
			cstart = r.o; csize, ctype = r.take('IH'); c = _R(b[cstart + 6:cstart + csize])
			if ctype == 0x2004:
				lf, lt, child, _, _, blend, op = c.take('HHHHHHB'); c.bytes(3); name = c.string()
				layers.append({'name': name, 'visible': bool(lf & 1), 'type': lt, 'child': child, 'opacity': op if flags & 1 else 255, 'bg': bool(lf & 8)})
				if blend: notes.add('เลเยอร์ "%s" ใช้โหมดผสม %d — อ่านเป็น Normal' % (name, blend))
			elif ctype == 0x2005:
				li, x, y, op, ct, z = c.take('HhhBHh'); c.bytes(5)
				if ct == 1: lk = c.take('H'); src = cels[lk].get(li); cels[f][li] = (src[0], src[1], op, src[3]) if src else None   # linked cel ใช้ตำแหน่ง+ภาพของ cel ต้นทาง
				elif ct in (0, 2):
					w, h = c.take('HH'); raw = c.b[c.o:] if ct == 0 else zlib.decompress(c.b[c.o:])
					is_bg = layers[li]['bg'] if li < len(layers) else False
					cels[f][li] = (x, y, op, _to_rgba(raw, w, h, depth, palette, transparent, is_bg))
				else: notes.add('มี tilemap — ข้าม')
				if z: notes.add('มี z-index ต่อ cel — เรียงตามเลเยอร์ปกติ')
			elif ctype == 0x2019:
				new_pal = True
				total, first, last = c.take('III'); c.bytes(8)
				palette = list(palette) + [(0, 0, 0, 255)] * max(0, total - len(palette))
				for i in range(first, last + 1):
					ef = c.take('H'); palette[i] = c.take('BBBB')
					if ef & 1: c.string()
			elif ctype == 0x0004 and not new_pal:                    # พาเลตต์แบบเก่า (ใช้เมื่อไม่มีแบบใหม่)
				pk = c.take('H'); idx = 0
				for _ in range(pk):
					idx += c.take('B'); k = c.take('B') or 256
					for _ in range(k):
						if idx < 256: palette[idx] = c.take('BBB') + (255,)
						idx += 1
			elif ctype == 0x2018:
				nt = c.take('H'); c.bytes(8)
				for _ in range(nt):
					a, z, d = c.take('HHB'); c.take('H'); c.bytes(6); c.bytes(3); c.bytes(1)
					tags.append((c.string(), a, z, TAG_DIR.get(d, 'forward')))
			r.o = cstart + csize
		r.o = start + fbytes
	# มองเห็นจริง = ตัวเองเปิด และกลุ่มแม่ทุกชั้นเปิด
	vis, stack = [], []
	for L in layers:
		stack = stack[:L['child']]; vis.append(L['visible'] and all(stack)); stack.append(L['visible'])
	frames = []
	for f in range(nframes):
		im = Image.new('RGBA', (W, H))
		for li, L in enumerate(layers):
			cel = cels[f].get(li)
			if L['type'] != 0 or not vis[li] or not cel: continue
			x, y, op, src = cel; a = op * L['opacity'] / (255 * 255)
			if a < 1: src = src.copy(); src.putalpha(src.getchannel('A').point(lambda v: int(v * a)))
			layer = Image.new('RGBA', (W, H)); layer.paste(src, (x, y)); im.alpha_composite(layer)
		frames.append(im)
	return Sprite(W, H, frames, durations, tags, [L['name'] for L in layers], sorted(notes))

# ── เขียน ──
def _chunk(ctype, data): return struct.pack('<IH', len(data) + 6, ctype) + data
def _str(s): e = s.encode('utf-8'); return struct.pack('<H', len(e)) + e

def write(path, frames, durations, tags=(), layer='Layer'):
	W, H = frames[0].size
	if any(f.size != (W, H) for f in frames): raise ValueError('ทุกเฟรมต้องขนาดเท่ากัน')
	if len(durations) != len(frames): raise ValueError('จำนวน durations ไม่เท่าเฟรม')
	# พาเลตต์ = สีที่ใช้จริง (ไม่เกิน 256 สี เพื่อให้แผงพาเลตต์ใน Aseprite มีสีของตัวละครพร้อมใช้)
	cols = []
	for f in frames:
		for c in (f.getcolors(1 << 16) or []):
			rgba = c[1]
			if rgba[3] and rgba not in cols: cols.append(rgba)
			if len(cols) >= 256: break
	seen, out = {}, []
	for i, f in enumerate(frames):
		ch = []
		if i == 0:
			ch.append(_chunk(0x2007, struct.pack('<HHI8x', 1, 0, 0)))                         # สี sRGB
			if cols:
				pal = struct.pack('<III8x', len(cols), 0, len(cols) - 1)
				for c in cols: pal += struct.pack('<HBBBB', 0, *c)
				ch.append(_chunk(0x2019, pal))
			ch.append(_chunk(0x2004, struct.pack('<HHHHHHB3x', 1 | 2, 0, 0, 0, 0, 0, 255) + _str(layer)))
			if tags:
				t = struct.pack('<H8x', len(tags))
				for name, a, z in tags: t += struct.pack('<HHBH6x3sx', a, z, 0, 0, b'\0\0\0') + _str(name)
				ch.append(_chunk(0x2018, t))
		key = f.tobytes()
		if key in seen:
			li, lb = seen[key]
			if lb: ch.append(_chunk(0x2005, struct.pack('<HhhBHh5xH', 0, lb[0], lb[1], 255, 1, 0, li)))   # linked cel (ตำแหน่งเดียวกับต้นทาง)
		else:
			bb = f.getbbox(); seen[key] = (i, bb)
			if bb:
				crop = f.crop(bb)
				ch.append(_chunk(0x2005, struct.pack('<HhhBHh5xHH', 0, bb[0], bb[1], 255, 2, 0, *crop.size) + zlib.compress(crop.tobytes(), 9)))
		body = b''.join(ch)
		out.append(struct.pack('<IHHH2xI', 16 + len(body), 0xF1FA, min(len(ch), 0xFFFF), max(1, round(durations[i])), len(ch)) + body)   # หัวเฟรม 16 ไบต์
	data = b''.join(out)
	header = struct.pack('<IHHHHHIHII', 128 + len(data), 0xA5E0, len(frames), W, H, 32, 1, max(1, round(durations[0])), 0, 0)
	header += struct.pack('<B3xHBBhhHH', 0, len(cols), 1, 1, 0, 0, 16, 16)
	header += b'\0' * (128 - len(header))
	open(path, 'wb').write(header + data)
	return len(seen)
