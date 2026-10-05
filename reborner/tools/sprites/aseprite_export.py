# tools/sprites/aseprite_export.py — ส่งสไปรต์ออกเป็นไฟล์ .aseprite ให้ kwan เปิดแก้ใน Aseprite
# รัน: python3 tools/sprites/aseprite_export.py [ชุด ...]   (ไม่ระบุ = ทุกชุด)
#   game    → docs/art-bible/aseprite/game/{rion,dog}.aseprite   สไปรต์ที่เกมใช้จริง · แท็กตั้งชื่อตามชื่อไฟล์ (south_w, west_a ...)
#   poses64 → docs/art-bible/aseprite/poses64/<id>.aseprite      ท่าขยับ 64 เฟรม (ร่าง)
#   spells  → docs/art-bible/aseprite/spells/<id>.aseprite       ท่าร่ายเวทย์ (ร่าง)
#   npcs    → docs/art-bible/aseprite/npcs/<id>.aseprite         NPC: แท็ก idle / talk / walk (ร่าง)
# จังหวะเฟรมอ่านจากค่าคงที่ในเกม (MOVE_TIME · ATTACK_FRAME_SEC · FOE_IDLE_SEC) — ภาพนิ่งใช้ FOE_IDLE_SEC แค่ให้ดูใน Aseprite
# แก้เสร็จแล้วดึงกลับด้วย aseprite_import.py
import json, os, re, sys
from PIL import Image
import aseprite_io as A

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPR = os.path.join(ROOT, 'assets/sprites')
OUT = os.path.join(ROOT, 'docs/art-bible/aseprite')

def const(file, name):
	m = re.search(r'const %s\s*:?=\s*([0-9.]+)' % name, open(os.path.join(ROOT, file), encoding='utf-8').read())
	if not m: raise SystemExit('ไม่เจอ %s ใน %s' % (name, file))
	return float(m.group(1))
MOVE = const('world/Overworld.gd', 'MOVE_TIME'); ATK = const('world/BattleScreen.gd', 'ATTACK_FRAME_SEC'); IDLE = const('world/BattleScreen.gd', 'FOE_IDLE_SEC')
png = lambda p: Image.open(p).convert('RGBA')

def save(path, groups):
	"""groups = [(แท็ก, [ภาพ], ms ต่อเฟรม)] → ไฟล์เดียว แท็กละช่วง"""
	frames, durs, tags = [], [], []
	for name, ims, ms in groups:
		tags.append((name, len(frames), len(frames) + len(ims) - 1)); frames += ims; durs += [ms] * len(ims)
	os.makedirs(os.path.dirname(path), exist_ok=True)
	uniq = A.write(path, frames, durs, tags)
	return len(frames), uniq

def game():
	out = []
	for who, folder in (('rion', 'rion_lastlight_draft'), ('dog', 'dog_lastlight_draft')):
		d = os.path.join(SPR, folder); g = []
		for dr in ('south', 'west', 'north', 'east'):
			g.append((dr, [png(os.path.join(d, dr + '.png'))], IDLE * 1000))
			g.append((dr + '_w', [png(os.path.join(d, '%s_w%d.png' % (dr, i))) for i in range(4)], MOVE / 2 * 1000))
		for pre in ('west_a', 'west_h', 'west_k'):
			fs = sorted(f for f in os.listdir(d) if re.fullmatch(pre + r'\d\.png', f))
			if fs: g.append((pre, [png(os.path.join(d, f)) for f in fs], ATK * 1000))
		out.append((who, save(os.path.join(OUT, 'game', who + '.aseprite'), g)))
	return out

def poses64():
	d = os.path.join(SPR, 'poses64_draft'); out = []
	cyc = {'walk': 2 * MOVE, 'idle': 2 * IDLE, 'attack': 4 * ATK, 'hurt': 2 * ATK, 'ko': 3 * ATK}
	for p in json.load(open(os.path.join(d, 'index.json'), encoding='utf-8'))['poses']:
		ms = (p.get('cycle') or cyc[p['timing']]) / p['n'] * 1000
		ims = [png(os.path.join(d, '%s_%d.png' % (p['id'], u))) for u in p['order']]
		out.append((p['id'], save(os.path.join(OUT, 'poses64', p['id'] + '.aseprite'), [(p['id'], ims, ms)])))
	return out

def spells():
	d = os.path.join(SPR, 'spells_draft'); out = []
	for f in sorted(x[:-6] for x in os.listdir(d) if x.endswith('_0.png')):
		ims = [png(os.path.join(d, '%s_%d.png' % (f, i))) for i in range(8)]
		out.append((f, save(os.path.join(OUT, 'spells', f + '.aseprite'), [('cast', ims, ATK * 1.6 * 1000)])))
	return out

def npcs():
	d = os.path.join(SPR, 'npcs_draft'); out = []
	for f in sorted(x[:-6] for x in os.listdir(d) if x.endswith('_0.png')):
		im = lambda i: png(os.path.join(d, '%s_%d.png' % (f, i)))
		out.append((f, save(os.path.join(OUT, 'npcs', f + '.aseprite'), [('idle', [im(0), im(1)], IDLE * 1000), ('talk', [im(2), im(3)], IDLE * 1000), ('walk', [im(i) for i in range(4, 8)], MOVE / 2 * 1000)])))
	return out

SETS = {'game': game, 'poses64': poses64, 'spells': spells, 'npcs': npcs}
if __name__ == '__main__':
	for name in sys.argv[1:] or SETS:
		res = SETS[name]()
		print('%-8s %3d ไฟล์ · เฟรมรวม %d · ภาพไม่ซ้ำ %d' % (name, len(res), sum(r[1][0] for r in res), sum(r[1][1] for r in res)))
