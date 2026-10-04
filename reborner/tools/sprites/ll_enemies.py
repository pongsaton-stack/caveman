# tools/sprites/ll_enemies.py — ตัดศัตรู 8 แบบจากชีต Last Light ความละเอียดสูง (kwan ส่ง 4 ต.ค. 2026)
# ต้นฉบับ: docs/art-bible/compendium/lastlight_sheet_hires.jpg (2576x1717 · ภาพเดียวกับ lastlight_01.png แต่ชัดกว่า)
# ผลลัพธ์: assets/sprites/monsters_ll_draft/<archetype>.png + _idle1.png (48px) — **ร่าง ยังไม่เข้าเกม**
# (monsters_ll/ คือโฟลเดอร์ที่เกมอ่านอัตโนมัติ ห้ามเขียนลงตรงนั้นจนกว่า kwan อนุมัติ)
# ทุกแบบโยงกับมอนในเกมผ่าน lastlight_archetype ใน monster_visual_master.json
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ll_cut
from ll_polish import hue_outline, clamp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ll_cut.SRC = os.path.join(ROOT, 'docs/art-bible/compendium/lastlight_sheet_hires.jpg')
OUT = os.path.join(ROOT, 'assets/sprites/monsters_ll_draft')
PANEL = (650, 611)   # มุมซ้ายบนของกรอบ Enemies ในชีต
# กล่องในกรอบ Enemies (ไม่รวมป้ายชื่อ) · ชื่อไฟล์ = lastlight_archetype ใน MASTER
BOXES = {
	'mutant-rat':    (25, 85, 140, 185),
	'slime':         (180, 120, 280, 195),
	'scavenger':     (315, 65, 420, 190),
	'bandit':        (460, 75, 560, 190),
	'plant-monster': (30, 255, 150, 400),
	'robot-drone':   (180, 280, 280, 370),
	'big-mutant':    (300, 255, 445, 415),
	'flying-eye':    (470, 260, 580, 410),
}
CELL = 48
TALL = 42    # ความสูงตัวในช่อง 48 (เท่ามอนขนาด M ที่อนุมัติแล้ว)

def shrink(im, h):
	w = max(1, round(im.width * h / im.height))
	if w > CELL - 2:
		w = CELL - 2; h = max(1, round(im.height * w / im.width))
	r = im.resize((w, h), Image.LANCZOS); px = r.load()
	for y in range(h):
		for x in range(w):
			a = px[x, y][3]
			px[x, y] = px[x, y][:3] + ((255,) if a >= 128 else (0,))
	return r

def make(name, box):
	b = (box[0] + PANEL[0], box[1] + PANEL[1], box[2] + PANEL[0], box[3] + PANEL[1])
	sp = ll_cut.cut(b, tol=70, shadow=True, fringe=2)
	sp = hue_outline(clamp(shrink(sp, TALL)))
	still = ll_cut.place(sp, CELL)
	# idle 2 = ยุบลง 1px (หายใจ) แบบเดียวกับมอนที่อนุมัติแล้ว
	sq = sp.resize((sp.width, max(1, sp.height - 1)), Image.NEAREST)
	idle = ll_cut.place(sq, CELL)
	still.save(os.path.join(OUT, name + '.png'))
	idle.save(os.path.join(OUT, name + '_idle1.png'))
	return still

if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	got = [make(n, b) for n, b in BOXES.items()]
	sheet = Image.new('RGBA', (CELL * len(got), CELL), (232, 217, 181, 255))
	for i, g in enumerate(got):
		sheet.paste(g, (i * CELL, 0), g)
	sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(ROOT, 'docs/art-bible/previews/ll_enemies_draft.png'))
	print('ok', len(got))
