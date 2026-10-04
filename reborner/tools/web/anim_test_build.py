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
	# ร่างศัตรูจากชีต Last Light (tools/sprites/ll_enemies.py) — แสดงในหน้านี้อย่างเดียว ยังไม่เข้าเกม
	dd = os.path.join(SPR, 'monsters_ll_draft')
	if os.path.isdir(dd):
		for f in sorted(os.listdir(dd)):
			if f.endswith('.png'):
				out['draft/' + f[:-4]] = png(os.path.join(dd, f))
	# ร่างมอนจาก Monster Compendium (tools/sprites/compendium_cut.py) — ตัวหลัก + ท่าหายใจ (ไม่ฝังภาพการ์ดรวม)
	# 64px + 4 ท่า (tools/sprites/compendium_animate.py) แทนชุด 48px เดิม
	cd = os.path.join(SPR, 'compendium_anim')
	if os.path.isdir(cd):
		for f in sorted(os.listdir(cd)):
			if f.endswith('.png'):
				out['cmp/' + f[:-4]] = png(os.path.join(cd, f))
	# ตัวอย่างมอนที่เจนรายตัว (แปลงกลับเป็นพิกเซลจริงแล้ว) — ร่างทดลอง
	sd = os.path.join(SPR, 'compendium_samples')
	if os.path.isdir(sd):
		for f in sorted(os.listdir(sd)):
			if f.endswith('.png'):
				out['smp/' + f[:-4]] = png(os.path.join(sd, f))
	# ไทล์ฉากหลังสำหรับจอศึกแบบ SaGa (พื้น + ของประดับ · เฉพาะชิ้นฐาน ไม่เอาชิ้นขอบ mask)
	td = os.path.join(ROOT, 'assets/tiles_ll')
	for n in ['ash_0', 'ash_1', 'ash_2', 'ash_3', 'grass_0', 'grass_1', 'grass_2', 'grass_3', 'stone_0', 'stone_1', 'stone_2', 'stone_3',
			'ruins', 'rock', 'pine', 'bush', 'ruin_house', 'flowers']:
		f = os.path.join(td, n + '.png')
		if os.path.exists(f):
			out['tile/' + n] = png(f)
	return out

def techs():
	rows = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/techs.csv'), encoding='utf-8')):
		rows.append({k: r[k] for k in ('tech_id', 'name_th', 'school', 'branch', 'parent', 'req_prof', 'power',
			'weight', 'sp', 'element', 'scope', 'hits', 'ignore_def', 'note', 'status', 'status_chance')})
	# ท่ายึด (GDD 5.2) — สาย "ยึด" ในหน้าทดลอง · ค่าจาก seize_techs.csv ตรง ๆ
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/seize_techs.csv'), encoding='utf-8')):
		eff = {'def_up': 'DEF ตัวเอง +%d%% %s เทิร์น' % (round(float(r['value']) * 100), r['turns']),
			'av_cut': 'ลด AV ตัวเอง %d%%' % round(float(r['value']) * 100)}.get(r['effect'], r['effect'])
		rows.append({'tech_id': 'seize_' + r['monster_id'], 'name_th': r['name_th'], 'school': 'ยึด', 'branch': 'จาก ' + r['monster_id'],
			'parent': '', 'req_prof': '0', 'power': r['power'], 'weight': r['weight'], 'sp': r['sp'], 'element': r['element'],
			'scope': r['scope'], 'hits': '1', 'ignore_def': '0', 'status': '', 'status_chance': '',
			'note': eff + (' · ครั้งเดียวต่อศึก' if r['once'] == '1' else '') + ' · ความจำ %s ช่อง · %s' % (r['slots'], r['status']),
			'effect': r['effect'], 'value': float(r['value'])})
	return rows

def monsters(ids):
	out = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8')):
		if r['monster_id'] in ids:
			out.append({k: r[k] for k in ('monster_id', 'name_th', 'name_en', 'tier', 'hp', 'atk', 'def', 'spd',
				'weak', 'resist', 'immune', 'signature_tech')})
	return out

def compendium():
	f = os.path.join(SPR, 'compendium_draft/index.json')
	return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []

def skill_ref():
	"""ชีตสกิล 173 ท่า แบ่งเป็นภาพละสาย (tools/sprites/skill_panels.py) — ภาพอ้างอิงเท่านั้น"""
	d = os.path.join(ROOT, 'docs/art-bible/compendium/skill_panels'); out = []
	for code, th in (('SL', 'คม'), ('PC', 'แทง'), ('CR', 'ทุบ'), ('BD', 'มือเปล่า'), ('ST', 'ยิง'), ('DV', 'กล')):
		f = os.path.join(d, code + '.jpg')
		if os.path.exists(f):
			out.append({'code': code, 'school': th, 'img': 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()})
	return out

def draft_map():
	"""ร่างแต่ละแบบ → มอนในเกมที่ MASTER ให้ใช้แบบนั้น (lastlight_archetype)"""
	names = {r['monster_id']: r['name_th'] for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8'))}
	out = {}
	for e in json.load(open(os.path.join(ROOT, 'docs/art-bible/monster_visual_master.json'), encoding='utf-8'))['entries']:
		if e['id'] in names:
			out.setdefault(e['lastlight_archetype'], []).append('%s %s' % (e['id'], names[e['id']]))
	return out

def main(out_path):
	spr = sprites()
	mon_ids = sorted({k.split('/')[1].split('_')[0] for k in spr if k.startswith('mon/') and not k.split('/')[1].startswith('COMP')})
	data = {
		'sprites': spr,
		'techs': techs(),
		'fx': {k: v for k, v in json.load(open(os.path.join(ROOT, 'data/fx/ultimates.json'), encoding='utf-8')).items() if k != '_doc'},
		'monsters': monsters(mon_ids),
		'draft_map': draft_map(),
		'compendium': compendium(),
		'skill_ref': skill_ref(),
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
