# tools/web/anim_test_build.py — สร้างหน้า "animation test" จากข้อมูลเกมปัจจุบัน
# อ่านสไปรต์จาก assets/ + techs.csv + monsters.csv + ค่าคงที่จาก Formulas.gd / BattleScreen.gd / Overworld.gd
# แล้วฝังทั้งหมดลงไฟล์ HTML เดียว (Artifact ห้ามโหลดไฟล์ภายนอก) · รัน: python3 tools/web/anim_test_build.py <out.html>
import base64, csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPR = os.path.join(ROOT, 'assets/sprites')

def png(path):
	with open(path, 'rb') as f:
		return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

def const(file, name):
	"""อ่านค่าคงที่ตัวเลขจากไฟล์ .gd — หน้าเว็บไม่มีเลขที่พิมพ์เอง"""
	src = open(os.path.join(ROOT, file), encoding='utf-8').read()
	m = re.search(r'const %s\s*:?=\s*([0-9.]+)' % name, src)
	if not m:
		raise SystemExit('ไม่เจอ %s ใน %s' % (name, file))
	return float(m.group(1))

def sprites():
	out = {}
	for folder, key in (('rion_lastlight_draft', 'rion'), ('dog_lastlight_draft', 'dog'), ('monsters_ll', 'mon')):
		d = os.path.join(SPR, folder)
		for f in sorted(os.listdir(d)):
			if f.endswith('.png'):
				out['%s/%s' % (key, f[:-4])] = png(os.path.join(d, f))
	return out

def techs():
	rows = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/techs.csv'), encoding='utf-8')):
		rows.append({k: r[k] for k in ('tech_id', 'name_th', 'school', 'branch', 'parent', 'req_prof', 'power',
			'weight', 'sp', 'element', 'scope', 'hits', 'ignore_def', 'note', 'status', 'status_chance')})
	return rows

def monsters(ids):
	out = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8')):
		if r['monster_id'] in ids:
			out.append({k: r[k] for k in ('monster_id', 'name_th', 'name_en', 'tier', 'hp', 'atk', 'def', 'spd',
				'weak', 'resist', 'immune', 'signature_tech')})
	return out

def main(out_path):
	spr = sprites()
	mon_ids = sorted({k.split('/')[1].split('_')[0] for k in spr if k.startswith('mon/') and not k.split('/')[1].startswith('COMP')})
	data = {
		'sprites': spr,
		'techs': techs(),
		'fx': {k: v for k, v in json.load(open(os.path.join(ROOT, 'data/fx/ultimates.json'), encoding='utf-8')).items() if k != '_doc'},
		'monsters': monsters(mon_ids),
		'k': {
			'MIT_K': const('core/Formulas.gd', 'MIT_K'),
			'WEAK_MULT': const('core/Formulas.gd', 'WEAK_MULT'),
			'RESIST_MULT': const('core/Formulas.gd', 'RESIST_MULT'),
			'ATTACK_FRAME_SEC': const('world/BattleScreen.gd', 'ATTACK_FRAME_SEC'),
			'FOE_IDLE_SEC': const('world/BattleScreen.gd', 'FOE_IDLE_SEC'),
			'MOVE_TIME': const('world/Overworld.gd', 'MOVE_TIME'),
			'FX_SEC': const('world/BattleScreen.gd', 'FX_SEC'),
			'ULT_PROF': const('world/BattleScreen.gd', 'ULT_PROF'),
		},
	}
	tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anim_test.tpl.html'), encoding='utf-8').read()
	html = tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
	open(out_path, 'w', encoding='utf-8').write(html)
	print(out_path, len(html), 'bytes ·', len(spr), 'sprites ·', len(data['techs']), 'techs ·', len(data['monsters']), 'monsters')

if __name__ == '__main__':
	main(sys.argv[1] if len(sys.argv) > 1 else 'anim_test.html')
