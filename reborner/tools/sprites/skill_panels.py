# tools/sprites/skill_panels.py — แบ่งชีต "Skill Sprite Sheet 173 ท่า" (kwan ส่ง 4 ต.ค. 2026) เป็นภาพละสาย
# ใช้เป็นภาพอ้างอิงในหน้า animation test เท่านั้น — ชื่อ/จำนวนท่าในชีตขัดกับ techs.csv (42 ท่า) ยังไม่ตัดสิน
import os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'docs/art-bible/compendium/skill_sprite_sheet.jpg')
OUT = os.path.join(ROOT, 'docs/art-bible/compendium/skill_panels')
# กรอบแต่ละสาย (พิกัดในภาพย่อ 2000 กว้าง · คูณกลับเป็นขนาดจริง) · ชื่อสายตาม techs.csv
PANELS = [('SL', 'คม', (12, 135, 657, 697)), ('PC', 'แทง', (667, 135, 1318, 697)), ('CR', 'ทุบ', (1328, 135, 1988, 697)),
	('BD', 'มือเปล่า', (12, 707, 657, 1212)), ('ST', 'ยิง', (667, 707, 1318, 1212)), ('DV', 'กล', (1328, 707, 1988, 1212))]
if __name__ == '__main__':
	im = Image.open(SRC).convert('RGB'); k = im.width / 2000
	os.makedirs(OUT, exist_ok=True)
	for code, th, b in PANELS:
		im.crop(tuple(int(v * k) for v in b)).save(os.path.join(OUT, code + '.jpg'), quality=82)
	print('ok', len(PANELS))
