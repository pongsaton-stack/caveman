# tools/sprites/vfx_sheet_cut.py — ตัด "VFX Protagonist" (kwan ส่ง 6 ต.ค. 2026) เป็นชิ้น ๆ ลงหน้า animation test แท็บแยก
#
#   python3 tools/sprites/vfx_sheet_cut.py
#
# ชีต: docs/art-bible/vfx/vfx_protagonist_sheet.png (1536x1024 · พื้นมืด · 21 แผง)
# แผง = กรอบที่วัดจากเส้นขอบสีในชีตนี้ (PANELS) · ในแผงหาแถวจากแถบว่างแนวนอน แล้วแยกเฟรมตามร่องแสงต่ำแนวตั้ง (ช่วงกว้างเกินหาร = แยกที่ร่องลึกสุด)
# แผงท่า (anim): ทุกแถว = 1 คลิป · ต่อเฟรมเก็บ
#   - กรอบในชีต + กรอบตัวเอก (ก้อนสีไม่อิ่มตัวรูปคน · ไว้จัดตำแหน่งให้ตัวเอกนิ่ง)
#   - ชั้นแสงอย่างเดียว (ลบพื้น + ลบตัวเอก + ถอดสีพื้น) ลงแผ่นรวมของแผง atlas_<แผง>.png
# แผงภาพนิ่ง (still): แต่ละชิ้น = ภาพเดียว (ตัดจากชีตตรง ๆ หน้าเทสแสดงจากภาพชีต)
# หน้าเทสเล่นคู่ ต้นฉบับ (ครอปจากชีต จัดตัวเอกให้ตรงกันทุกเฟรม) | ปรับแล้ว (Rion ตัวจริงถืออาวุธตามแผง + แสงจากชีต + เฟดระหว่างเฟรม)
# ออก assets/sprites/vfx_sheet_draft/ (.gdignore · ร่าง): index.json + atlas_*.png · ชีตตรวจกรอบ docs/art-bible/vfx/vfx_cut_boxes.png
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

ROOT = sc.ROOT
SRC = os.path.join(ROOT, 'docs/art-bible/vfx/vfx_protagonist_sheet.png')
OUT = os.path.join(ROOT, 'assets/sprites/vfx_sheet_draft')
# id: (ชื่อ, x0, y0, x1, y1, ความสูงหัวแผง, ชนิด, ท่า Rion ในแบบ "ปรับแล้ว") — กรอบวัดจากเส้นขอบสีในชีตนี้
PANELS = {
	'turn':    ('Idle / Turn Around', 366, 28, 562, 116, 6, 'still', None),
	'face':    ('Face / Emotion', 584, 24, 792, 118, 20, 'still', None),
	'equip':   ('Equipment / Props', 812, 24, 1098, 118, 20, 'still', None),
	'idle':    ('Idle / Movement', 11, 133, 366, 414, 28, 'still', None),
	'slash':   ('Attack / Slash', 381, 133, 690, 414, 28, 'anim', 'SL'),
	'pierce':  ('Attack / Pierce', 706, 133, 964, 414, 28, 'anim', 'PC'),
	'blunt':   ('Attack / Blunt', 981, 134, 1216, 413, 28, 'anim', 'CR'),
	'body':    ('Attack / Body', 1234, 135, 1524, 413, 28, 'anim', 'BD'),
	'shoot':   ('Attack / Shoot', 12, 426, 375, 711, 28, 'anim', 'ST'),
	'skill':   ('Skill / Special', 390, 426, 716, 711, 28, 'anim', 'DV'),
	'dash':    ('Dash / Teleport', 728, 426, 983, 711, 28, 'anim', 'DASH'),
	'hit':     ('Hit / Damage / Impact', 998, 426, 1237, 711, 28, 'anim', 'HIT'),
	'status':  ('Status / Buff / Debuff', 1254, 426, 1522, 711, 28, 'anim', 'IDLE'),
	'env':     ('Environmental Interaction', 14, 722, 388, 922, 26, 'still', None),
	'summon':  ('Summon / Partner / Drone', 403, 722, 614, 975, 26, 'still', None),
	'weather': ('Weather / Elemental', 630, 722, 899, 975, 26, 'still', None),
	'ult':     ('Ultimate / Big Skill', 914, 722, 1288, 975, 26, 'still', None),
	'ui':      ('UI / VFX Elements', 1300, 722, 1530, 940, 26, 'still', None),
}
# แผงภาพนิ่งที่ภาพชิดกันจนหาก้อนแยกไม่ได้ → กรอบวัดด้วยมือจากภาพขยาย 2 เท่า (x0, y0, x1, y1 ในชีต)
MANUAL = {
	'ult': [(919, 748, 1120, 812), (1123, 748, 1286, 812),
		(919, 815, 1036, 889), (1039, 815, 1116, 889), (1119, 815, 1286, 889),
		(919, 892, 1000, 970), (1002, 892, 1103, 970), (1105, 892, 1176, 970), (1178, 892, 1286, 970)],
	'weather': [(632, 748, 700, 813), (700, 748, 767, 813), (767, 748, 835, 813), (835, 748, 897, 813),
		(632, 818, 685, 893), (685, 818, 762, 893), (762, 818, 802, 893), (802, 818, 840, 893), (840, 818, 897, 893),
		(632, 898, 715, 973), (715, 898, 772, 973), (772, 898, 830, 973), (830, 898, 897, 973)],
}
FRAME_W = 48     # ความกว้างเฟรมโดยประมาณในชีต (ช่วงที่กว้างเกิน 1.6 เท่าแบ่งเป็นหลายเฟรม)

def bands(prof, thr, mingap, minlen):
	on = prof > thr; out = []; s = None; gap = 0; e = 0
	for i, v in enumerate(on):
		if v:
			if s is None: s = i
			gap = 0; e = i
		elif s is not None:
			gap += 1
			if gap >= mingap: out.append((s, e + 1)); s = None
	if s is not None: out.append((s, e + 1))
	return [b for b in out if b[1] - b[0] >= minlen]

def split_cols(m, fw):
	prof = ndimage.uniform_filter1d(m.mean(0), 3); out = []
	for s, e in bands(prof, 0.04, 3, 10):
		w = e - s
		if w > fw * 1.6:
			n = round(w / fw); cuts = []
			for k in range(1, n):
				c = int(s + w * k / n); lo, hi = max(s + 5, c - 10), min(e - 5, c + 10)
				cuts.append(lo + int(np.argmin(prof[lo:hi])))
			edges = [s] + cuts + [e]; out += list(zip(edges[:-1], edges[1:]))
		else: out.append((s, e))
	return out

def hero_box(rgb):
	"""กรอบตัวเอกในเฟรม: ก้อนสีไม่อิ่มตัว (ผิว เสื้อ หมวก + เส้นขอบ) ที่สูงเกือบเต็มเฟรม · ไม่เจอ = None"""
	mx = rgb.max(2); sat = (mx - rgb.min(2)) / np.maximum(mx, 1)
	m = ndimage.binary_fill_holes(ndimage.binary_closing((mx > 45) & (mx < 245) & (sat < 0.55), iterations=2))
	lab, n = ndimage.label(ndimage.binary_erosion(m, iterations=1))
	best = None; h = rgb.shape[0]
	for i, sl in enumerate(ndimage.find_objects(lab), 1):   # ก้อนต้องลงไปถึงส่วนล่างของเฟรม (ตัวเอกยืนบนพื้น)
		hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start; area = (lab[sl] == i).sum()
		blob = rgb[lab == i]; bmx = blob.max(1); bsat = (bmx - blob.min(1)) / np.maximum(bmx, 1)
		glowy = ((bmx > 170) & (bsat > 0.5)).mean()   # ก้อนแสงสีจัดที่บังเอิญรูปทรงคล้ายคน ไม่ใช่ตัวเอก
		if hh >= h * 0.45 and sl[0].stop >= h * 0.75 and ww <= 46 and area / (hh * ww) > 0.3 and bmx.mean() < 175 and glowy < 0.25 and (best is None or area > best[0]):
			best = (area, [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop], lab == i)
	return (best[1], ndimage.binary_dilation(best[2], iterations=2) & m) if best else (None, None)

def hero_x(rgb, bg):
	"""สำรองเมื่อหาก้อนตัวเอกไม่เจอ: แนวตั้งที่มีพิกเซล "ตัวคน" (ต่างจากพื้น ไม่ใช่แสงจัด) หนาแน่นสุด กว้าง 10–48px → กลางช่วง"""
	mx = rgb.max(2); sat = (mx - rgb.min(2)) / np.maximum(mx, 1)
	body = ndimage.binary_opening((np.abs(rgb - bg).max(2) > 38) & (mx < 235) & ~((sat > 0.6) & (mx > 150)), iterations=1)
	prof = ndimage.uniform_filter1d(body.sum(0).astype(float), 3); runs = []; st = None
	for i, o in enumerate(list(prof > rgb.shape[0] * 0.22) + [False]):
		if o and st is None: st = i
		if not o and st is not None: runs.append((st, i)); st = None
	runs = [r for r in runs if 10 <= r[1] - r[0] <= 48]
	return (lambda r: (r[0] + r[1]) / 2)(max(runs, key=lambda r: prof[r[0]:r[1]].sum())) if runs else None

def glow_layer(rgb, hero_mask):
	"""ชั้นแสง (หน้าเทสวาดแบบบวกแสง): ความทึบ = สว่าง × อิ่มตัว + แกนขาวจัด · ตัดเศษที่ไม่ติดแกนแสง · ลบก้อนตัวเอก
	(รุ่นแรกใช้ "ต่างจากพื้น" → ตัวเอกติดมาทั้งตัว เพราะในชีตตัวเอกกับแสงสีพอ ๆ กัน)"""
	mx = rgb.max(2); sat = (mx - rgb.min(2)) / np.maximum(mx, 1)
	g = np.clip(np.clip((mx - 120) / 80, 0, 1) * np.clip((sat - 0.3) / 0.3, 0, 1) + np.clip((mx - 225) / 25, 0, 1), 0, 1)
	g *= ndimage.binary_dilation(ndimage.binary_opening(g > 0.35, iterations=1), iterations=2)
	if hero_mask is not None: g[hero_mask] = 0
	out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
	out[..., :3] = rgb.clip(0, 255); out[..., 3] = (g * 255).round()
	out[out[..., 3] < 10] = 0
	return out

def still_pieces(m):
	"""ภาพนิ่ง: ก้อนที่ต่อกัน (ปิดรู 2px) · ทิ้งเศษเล็ก + ป้ายตัวหนังสือ (สูงไม่ถึง 16px) · เรียงตามแถว (y ห่างกันเกิน 12px = แถวใหม่) แล้วซ้าย→ขวา"""
	lab, _ = ndimage.label(ndimage.binary_dilation(ndimage.binary_closing(m, iterations=2), iterations=1))
	bx = [(sl[1].start, sl[0].start, sl[1].stop, sl[0].stop) for sl in ndimage.find_objects(lab)]
	bx = sorted((b for b in bx if (b[2] - b[0]) * (b[3] - b[1]) >= 120 and min(b[2] - b[0], b[3] - b[1]) >= 8 and b[3] - b[1] >= 16), key=lambda b: (b[1] + b[3]) / 2)
	rows = []
	for b in bx:
		if rows and (b[1] + b[3]) / 2 - rows[-1][0] <= 12: rows[-1][1].append(b)
		else: rows.append([(b[1] + b[3]) / 2, [b]])
	return [sorted(r[1]) for r in rows]

def main():
	a = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	check = Image.fromarray(a.astype(np.uint8)).convert('RGB'); dr = ImageDraw.Draw(check)
	index = {'sheet': 'docs/art-bible/vfx/vfx_protagonist_sheet.png', 'panels': []}
	tot_rows = tot_frames = 0
	for pid, (name, x0, y0, x1, y1, head, kind, pose) in PANELS.items():
		sub = a[y0 + head:y1 - 3, x0 + 3:x1 - 3]; bg = np.median(sub.reshape(-1, 3), axis=0)
		m = np.abs(sub - bg).max(2) > 38
		panel = {'id': pid, 'name': name, 'kind': kind, 'pose': pose, 'box': [x0, y0, x1, y1], 'bg': [int(v) for v in bg], 'rows': []}
		if kind == 'still':
			if pid in MANUAL:
				groups = {}
				for b in MANUAL[pid]: groups.setdefault(b[1], []).append(list(b))
				prow = [groups[k] for k in sorted(groups)]
			else:
				prow = [[[x0 + 3 + b[0], y0 + head + b[1], x0 + 3 + b[2], y0 + head + b[3]] for b in r] for r in still_pieces(m)]
			for r in prow:
				for b in r: dr.rectangle([b[0], b[1], b[2] - 1, b[3] - 1], outline=(255, 220, 0))
				panel['rows'].append([{'box': [int(v) for v in b]} for b in r]); tot_rows += 1; tot_frames += len(r)
			index['panels'].append(panel)
			print(f'{pid:8s} still แถว {len(prow)} · ชิ้น {sum(len(r) for r in prow)}'); continue
		atlas_parts = []; ax = 0
		for rs, re in bands(m.mean(1), 0.03, 3, 14):
			while re - rs > 14 and m[re - 1].mean() > 0.5: re -= 1   # เส้นพื้นสีใต้แถวในชีต ไม่ใช่ส่วนของภาพ
			row = []
			for cs, ce in split_cols(m[rs:re], FRAME_W):
				fx0, fy0, fx1, fy1 = x0 + 3 + cs, y0 + head + rs, x0 + 3 + ce, y0 + head + re
				rgb = a[fy0:fy1, fx0:fx1]
				fr = {'box': [int(fx0), int(fy0), int(fx1), int(fy1)]}
				dr.rectangle([fx0, fy0, fx1 - 1, fy1 - 1], outline=(0, 255, 0))
				if kind == 'anim':
					hb, hm = hero_box(rgb)
					fr['hero'] = [int(v) for v in hb] if hb else None
					hx = (hb[0] + hb[2]) / 2 if hb else hero_x(rgb, bg)
					if hx is not None and pose not in ('DASH', 'HIT', 'IDLE') and hx > rgb.shape[1] * 0.6:   # ตัวเอกในชีตหันขวา แสงท่าโจมตีอยู่หน้า → "ตัวเอก" ชิดขวาของเฟรมคือแสงที่หาผิด
						hx = None; hb = hm = None; fr['hero'] = None
					# จุดยึด (x ในชีต): กลางตัวเอก · เฟรมแสงล้วนของท่าโจมตี = แสงพุ่งออกจากด้านหน้า (ขอบซ้ายเฟรม) ·
					# เฟรมแสงล้วนของ พุ่ง/โดนตี/สถานะ = แสงรอบตัว (กลางเฟรม)
					if hx is not None: fr['ax'] = int(round(fx0 + hx)); fr['src'] = 'hero'
					elif pose in ('DASH', 'HIT', 'IDLE'): fr['ax'] = int((fx0 + fx1) / 2); fr['src'] = 'center'
					else: fr['ax'] = int(fx0 - 6); fr['src'] = 'edge'
					if pose in ('HIT', 'IDLE'): hm = None   # ออร่า/แสงโดนตีอยู่รอบตัว → เก็บทั้งชั้น หน้าเทสวาดไว้หลัง Rion
					elif hx is not None:   # ตัวเอกในชีตย้อมสีแผง (แดง/ฟ้า) จนผ่านเกณฑ์แสง → ตัดแถบกว้าง 26px รอบตัวเอกออกทั้งแถบ (ตรงนั้น Rion ยืนบังอยู่แล้ว)
						band = np.zeros(rgb.shape[:2], bool); band[:, max(0, int(hx - 13)):int(hx + 13)] = True
						hm = band if hm is None else (hm | band)
					g = glow_layer(rgb, hm)
					fr['fx'] = [ax, 0, g.shape[1], g.shape[0]]; atlas_parts.append((ax, g)); ax += g.shape[1] + 1
				row.append(fr); tot_frames += 1
			panel['rows'].append(row); tot_rows += 1
		if atlas_parts:
			H = max(g.shape[0] for _, g in atlas_parts); at = np.zeros((H, ax, 4), np.uint8)
			for x, g in atlas_parts: at[:g.shape[0], x:x + g.shape[1]] = g
			Image.fromarray(at, 'RGBA').save(os.path.join(OUT, f'atlas_{pid}.png')); panel['atlas'] = f'atlas_{pid}'
		index['panels'].append(panel)
		print(f'{pid:8s} {kind:5s} แถว {len(panel["rows"])} · เฟรม {sum(len(r) for r in panel["rows"])}' +
			(f' · มีตัวเอก {sum(1 for r in panel["rows"] for f in r if f.get("hero"))}' if kind == 'anim' else ''))
	json.dump(index, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	check.save(os.path.join(ROOT, 'docs/art-bible/vfx/vfx_cut_boxes.png'))
	print('รวม', tot_rows, 'แถว ·', tot_frames, 'ชิ้น')

if __name__ == '__main__':
	main()
