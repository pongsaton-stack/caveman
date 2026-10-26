# tools/sprites/vfx_game_fx.py — แสงจากชีต VFX Protagonist → ภาพพิกเซลขนาดเกม (ตัวอย่างก่อนเข้าเกม · kwan เลือก 6 ต.ค. "แสงโจมตี+โดนตี")
#
#   python3 tools/sprites/vfx_game_fx.py      (ต้องรัน vfx_sheet_cut.py ก่อน)
#
# ต่อชุด (SETS): หยิบชั้นแสงจาก atlas ของ vfx_sheet_cut.py ตามตำแหน่ง (แผง, แถว, เฟรม) ที่เลือกด้วยตาจากภาพแสงทุกเฟรม
#   → เก็บเฉพาะก้อนแสงใหญ่ (เศษตัวเอกที่หลุดมาเป็นจุดเล็ก ๆ ทิ้ง) → ความทึบเหลือ 4 ขั้น (พิกเซลคม ไม่ฟุ้ง)
#   → ลดสีรวมทั้งชุดเหลือ COLORS สี (ทุกเฟรมพาเลตต์เดียวกัน) → ผืนเท่ากันทุกเฟรม จุดกลางแสงอยู่กลางผืน
# ขนาด 1:1 กับชีต — ตัวเอกในชีตสูง ~35px Rion ในเกมสูง 58px แสงจึงเล็กกว่าที่เห็นในแท็บ "ปรับแล้ว" (ขยาย 1.6) ให้ดูบนเวทีขนาดจริงก่อนตัดสิน
# ออก assets/sprites/vfx_fx_draft/<ชุด>_<i>.png + index.json (.gdignore · ร่าง ไม่เข้าเกม) · ภาพตรวจ docs/art-bible/vfx/vfx_fx_preview.png
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

SRC = os.path.join(sc.ROOT, 'assets/sprites/vfx_sheet_draft')
OUT = os.path.join(sc.ROOT, 'assets/sprites/vfx_fx_draft')
COLORS = 8   # ระดับความสว่าง (ภาพเป็นโทนเทา) → ย้อมแล้วได้ไม่เกิน 8 สีต่อชุด
ALPHA_STEPS = [0, 96, 176, 255]
# ชุด: (คำอธิบาย, [(แผง, แถว, เฟรม)]) — เลือกด้วยตาจากภาพแสงทุกเฟรมของแต่ละแผง (เฟรมที่มีแต่เศษตัวเอกไม่เอา)
# ทุกชุดเก็บเป็นโทนขาว-เทา (ความสว่างล้วน) → หน้าเทส/เกมย้อมสีด้วยสีของท่าเอง จึงเข้ากับแสงของสกิลจากชีตทุกท่า
SETS = {
	'SL_hit': ('ฟัน · เสี้ยวฟันที่เป้า เล็ก → เต็ม → ใหญ่', [('slash', 1, 4), ('slash', 0, 2), ('slash', 1, 5)]),
	'PC_fly': ('แทง · ลำแทงยืดจากมือ', [('pierce', 2, 1), ('pierce', 0, 4), ('pierce', 3, 4)]),
	'PC_hit': ('แทง · ดาวแตกที่เป้า', [('pierce', 0, 2)]),
	'CR_hit': ('ทุบ · ระเบิดโผล่จากพื้น', [('blunt', 1, 2), ('blunt', 2, 1), ('blunt', 2, 4)]),
	'BD_hit': ('ร่างกาย · ประกายหมัด', [('body', 0, 3), ('body', 3, 2), ('body', 3, 4)]),
	'ST_fly': ('ยิง · ลูกกระสุนไฟ', [('shoot', 1, 3)]),
	'ST_hit': ('ยิง · ระเบิดที่เป้า', [('shoot', 2, 5), ('shoot', 3, 6)]),
	'DV_hit': ('กล · เสาแสงที่เป้า', [('skill', 2, 3), ('skill', 2, 4)]),
	'spark': ('ประกายตอนโดน (ทุกสาย)', [('hit', 0, 1)]),
}

def clean(g):
	"""เก็บก้อนแสงที่ใหญ่ ≥ 20% ของก้อนใหญ่สุด · ความทึบปัดเป็น ALPHA_STEPS"""
	lab, n = ndimage.label(g[..., 3] > 40)
	if n:
		size = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
		keep = ndimage.binary_dilation(np.isin(lab, [i + 1 for i in range(n) if size[i] >= size.max() * 0.2]), iterations=1)
		g[~keep] = 0
	a = g[..., 3].astype(int)
	g[..., 3] = np.array(ALPHA_STEPS)[np.abs(a[..., None] - np.array(ALPHA_STEPS)).argmin(-1)]
	g[g[..., 3] == 0] = 0
	return g

def main():
	idx = json.load(open(os.path.join(SRC, 'index.json'), encoding='utf-8'))
	panels = {p['id']: p for p in idx['panels']}
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	out = {'_doc': 'แสงจากชีต VFX Protagonist ขนาดเกม · ร่าง ยังไม่เข้าเกม · tools/sprites/vfx_game_fx.py', 'sets': {}}
	rows = []
	for name, (label, picks) in SETS.items():
		frames = []
		for pid, r, f in picks:
			fr = panels[pid]['rows'][r][f]; x, y, w, h = fr['fx']
			g = np.asarray(Image.open(os.path.join(SRC, panels[pid]['atlas'] + '.png')).convert('RGBA'))[y:y + h, x:x + w].copy()
			g = clean(g)
			ys, xs = np.where(g[..., 3] > 0)
			frames.append(g[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
		for g in frames:   # โทนขาว-เทา: ความสว่าง ยืดช่วงให้ส่วนมืดสุด 25% → แกนสว่างสุด (เปอร์เซ็นไทล์ 97) ขาว · เก็บลายในแสงไว้ให้ย้อมสีแล้วมีมิติ
			l = g[..., :3].max(2) * 0.5 + g[..., :3].mean(2) * 0.5; op = g[..., 3] > 0
			lo, hi = np.percentile(l[op], 3), np.percentile(l[op], 97)
			v = np.clip(0.25 + 0.75 * (l - lo) / max(1, hi - lo), 0, 1) * 255
			g[..., :3] = np.repeat(v[..., None], 3, 2).astype(np.uint8)
		pal = sc.auto_palette(frames, COLORS)
		frames = [sc.lock(g, pal)[0] for g in frames]
		W = max(g.shape[1] for g in frames); H = max(g.shape[0] for g in frames)
		files = []
		for i, g in enumerate(frames):
			can = np.zeros((H, W, 4), np.uint8); oy, ox = (H - g.shape[0]) // 2, (W - g.shape[1]) // 2
			can[oy:oy + g.shape[0], ox:ox + g.shape[1]] = g
			Image.fromarray(can, 'RGBA').save(os.path.join(OUT, f'{name}_{i}.png')); files.append(f'{name}_{i}')
			rows.append(can)
		out['sets'][name] = {'label': label, 'frames': files, 'size': [W, H], 'from': [list(p) for p in picks]}
		print(f'{name}: {len(files)} เฟรม · ผืน {W}x{H} · {len(pal)} สี')
	json.dump(out, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	W = sum(g.shape[1] + 4 for g in rows); H = max(g.shape[0] for g in rows)
	pv = Image.new('RGBA', (W, H), (24, 22, 30, 255)); x = 0
	for g in rows: pv.alpha_composite(Image.fromarray(g, 'RGBA'), (x, (H - g.shape[0]) // 2)); x += g.shape[1] + 4
	pv.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(sc.ROOT, 'docs/art-bible/vfx/vfx_fx_preview.png'))

if __name__ == '__main__':
	main()
