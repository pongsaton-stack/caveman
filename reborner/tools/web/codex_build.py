#!/usr/bin/env python3
# สร้างหน้า "สมุดรวม REBORNER" (สกิล เวทย์ ประกาย อาวุธ มอน บอส ไอเท็ม NPC ยานพาหนะ) จากไฟล์ข้อมูลเกมโดยตรง
# ใช้: python3 tools/web/codex_build.py <out.html>
# ไม่มีตัวเลขพิมพ์เอง — ทุกค่ามาจาก data/*.csv · docs/art-bible/**.json · core/Insight.gd · core/Formulas.gd · world/BattleScreen.gd
import base64, csv, json, os, re, sys
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)

def rows(path):
	return list(csv.DictReader(open(P(path), encoding='utf-8')))

def img(path):
	f = P(path)
	return 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode() if os.path.isfile(f) else ''

def gd_consts(path):
	out = {}
	for line in open(P(path), encoding='utf-8'):
		m = re.match(r'\s*const\s+(\w+)\s*:?=\s*([-\d.]+)\s*(?:#\s*(.*))?$', line)
		if m:
			out[m.group(1)] = {'v': float(m.group(2)), 'why': (m.group(3) or '').strip()}
	return out

def skills():
	ult = int(gd_consts('world/BattleScreen.gd')['ULT_PROF']['v'])
	out = []
	for r in rows('data/techs.csv'):
		out.append({k: r.get(k, '') for k in ('tech_id', 'name_th', 'school', 'branch', 'parent', 'req_prof', 'power', 'weight', 'sp',
			'element', 'scope', 'hits', 'ignore_def', 'target_av_mult', 'ignore_pos', 'free_row', 'note', 'status', 'status_chance', 'effect')})
	return out, ult

def glimmer():
	f, i = gd_consts('core/Formulas.gd'), gd_consts('core/Insight.gd')
	src = [('ALLY_DOWN', 'เพื่อนร่วมทีมล้ม', 'วิกฤต'), ('HP_CRITICAL', 'HP ตัวเองต่ำกว่า 15%', 'วิกฤต'),
		('GUARD_HIT', 'ตั้งรับแล้วถูกโจมตี', 'วิกฤต'), ('ALLY_HURT', 'เพื่อนร่วมทีม HP ต่ำกว่า %d%%' % round(i['ALLY_HURT_RATIO']['v'] * 100), 'วิกฤต'),
		('HP_LOW', 'HP ตัวเองต่ำกว่า 30%', 'วิกฤต'), ('HEAVY_HIT', 'โดนโจมตีหนัก (เกิน 18% ของ HP สูงสุด)', 'วิกฤต'),
		('GOT_STATUS', 'ติดสถานะ', 'วิกฤต'), ('FIGHTING_BOSS', 'สู้บอส (ต่อเทิร์นของบอส)', 'ทุกเทิร์น'),
		('STRONGER_FOE', 'ศัตรูแข็งเท่าหรือเกินความชำนาญ (ต่อเทิร์น)', 'ทุกเทิร์น'),
		('TECH_ON_STRONG', 'ใช้ท่ากับศัตรูที่แข็งกว่า', 'ทุกเทิร์น'), ('HIT_WEAKNESS', 'ตีจุดอ่อน', 'ทุกเทิร์น')]
	return {'base': f['GLIM_BASE']['v'], 'threshold': i['THRESHOLD']['v'], 'carry': i['CARRY']['v'], 'lock': int(i['LOCK_ROUNDS']['v']),
		'insight': [{'what': w, 'kind': k, 'v': i[c]['v']} for c, w, k in src]}

def weapons():
	w = json.load(open(P('docs/art-bible/weapons/weapons_full.json'), encoding='utf-8'))
	csvw = {r['weapon_id']: r for r in rows('data/weapons.csv')}
	fams = []
	for fam in w['families']:
		ws = []
		for x in fam['weapons']:
			c = csvw.get(x['id'], {})
			ws.append({'id': x['id'], 'name': x['name'], 'tier': x['tier'], 'base': c.get('weapon_base') or '', 'steer': c.get('steer') or '',
				'concept': x.get('concept', ''), 'icon': img('assets/sprites/weapon_icons/%s.png' % x['id'])})
		fams.append({'id': fam['family_id'], 'school': fam['school'], 'object': fam['object'], 'concept': fam.get('concept', ''), 'weapons': ws})
	tiers = {k: {'label': v['label'], 'range': v.get('value_range')} for k, v in w['tiers'].items()}
	return {'status': w['status'], 'tiers': tiers, 'families': fams}

def monsters():
	body = {r['monster_id']: r['body'] for r in rows('data/monster_body.csv')}
	out = []
	for r in rows('data/monsters.csv'):
		mid = r['monster_id']
		pic = img('assets/sprites/monsters_px/%s_idle0.png' % mid) or img('assets/sprites/monsters_ll/%s.png' % mid)
		out.append({'id': mid, 'name': r['name_th'], 'en': r['name_en'], 'region': r['region'], 'sub': r['sublocation'], 'tier': r['tier'],
			'hp': r['hp'], 'atk': r['atk'], 'def': r['def'], 'spd': r['spd'], 'row': r['grid_pos'], 'weak': r['weak'], 'resist': r['resist'],
			'immune': r['immune'], 'sig': r['signature_tech'], 'sig_fx': r['tech_effect'], 'teaches': r['teaches'], 'drop': r['drop'],
			'rate': r['drop_rate'], 'boss': r['is_boss'] == '1', 'status': r['status'], 'body': body.get(mid, ''), 'img': pic})
	return out

def items():
	d = json.load(open(P('assets/sprites/items_draft/index.json'), encoding='utf-8'))
	return [dict(x, icon=img('assets/sprites/items_draft/%s.png' % x['id'])) for x in d['items']]

def spells():
	d = json.load(open(P('docs/art-bible/spells/spells_full.json'), encoding='utf-8'))
	return {'status': d['status'], 'schools': d['schools']}

def world(name, key):
	d = json.load(open(P('docs/art-bible/world/%s.json' % name), encoding='utf-8'))
	return {'status': d['status'], 'items': d[key]}

def main(out):
	sk, ult = skills()
	veh = world('vehicles', 'items')
	for v in veh['items']:
		v['img'] = img('assets/sprites/vehicles_draft/%s_0.png' % v['id'])
	data = {'built': date.today().isoformat(), 'ult': ult, 'skills': sk, 'spells': spells(), 'glimmer': glimmer(), 'weapons': weapons(),
		'monsters': monsters(), 'items': items(), 'npcs': world('npcs', 'npcs'), 'vehicles': veh}
	tpl = open(P('tools/web/codex.tpl.html'), encoding='utf-8').read()
	html = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
	open(out, 'w', encoding='utf-8').write(html)
	print(out, len(html.encode()), 'bytes ·', len(sk), 'techs ·', len(data['monsters']), 'monsters ·', len(data['items']), 'items')

if __name__ == '__main__':
	main(sys.argv[1])
