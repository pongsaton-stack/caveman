# tools/sprites/aseprite_check.py — ตรวจไป-กลับ: ไฟล์ .aseprite ทุกไฟล์ที่ aseprite_export.py ส่งออก อ่านกลับแล้วต้องได้ภาพเท่าต้นทางทุกพิกเซล
# (ไม่นับค่าสีในจุดที่โปร่งใสทั้งคู่) · รันหลังแก้ aseprite_io.py ทุกครั้ง: python3 tools/sprites/aseprite_check.py
import json, os, sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import aseprite_io as A
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
same = lambda a, b: all(p == q or (p[3] == 0 and q[3] == 0) for p, q in zip(a.convert('RGBA').getdata(), b.convert('RGBA').getdata()))
png = lambda p: Image.open(R + p)
checks = bad = 0
for who, folder in (('rion', 'rion_lastlight_draft'), ('dog', 'dog_lastlight_draft')):
	s = A.read(R + 'docs/art-bible/aseprite/game/%s.aseprite' % who)
	for name, a, z, _ in s.tags:
		for i in range(a, z + 1):
			f = name if a == z else '%s%d' % (name, i - a); checks += 1
			if not same(s.frames[i], png('assets/sprites/%s/%s.png' % (folder, f))): bad += 1; print('DIFF game', who, f)
for p in json.load(open(R + 'assets/sprites/poses64_draft/index.json'))['poses']:
	s = A.read(R + 'docs/art-bible/aseprite/poses64/%s.aseprite' % p['id'])
	for i, u in enumerate(p['order']):
		checks += 1
		if not same(s.frames[i], png('assets/sprites/poses64_draft/%s_%d.png' % (p['id'], u))): bad += 1; print('DIFF', p['id'], i); break
for f in sorted(os.listdir(R + 'docs/art-bible/aseprite/spells')):
	s = A.read(R + 'docs/art-bible/aseprite/spells/' + f)
	for i in range(8):
		checks += 1
		if not same(s.frames[i], png('assets/sprites/spells_draft/%s_%d.png' % (f[:-9], i))): bad += 1; print('DIFF', f, i)
for f in sorted(os.listdir(R + 'docs/art-bible/aseprite/npcs')):
	s = A.read(R + 'docs/art-bible/aseprite/npcs/' + f)
	for i in range(8):
		checks += 1
		if not same(s.frames[i], png('assets/sprites/npcs_draft/%s_%d.png' % (f[:-9], i))): bad += 1; print('DIFF', f, i)
print('round-trip frames checked', checks, 'mismatch', bad)
sys.exit(1 if bad else 0)
