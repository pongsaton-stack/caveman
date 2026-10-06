# tools/web/ui_mock_build.py — หน้าตัวอย่าง UI/HUD/เมนูในเกม (แยกจากหน้า animation test · kwan 6 ต.ค. 2026)
#
#   GODOT=/path/to/godot python3 tools/web/ui_mock_build.py <out.html>
#
# ค่าทุกตัวบนจอตัวอย่างมาจากเกมจริง: tools/web/ui_mock_dump.gd ถาม Godot (สูตร Formulas · PlayerState · Actor.from_csv)
# รูปมาจาก assets/sprites (ร่างทั้งหมด) ฝังเป็น data URI · แม่แบบหน้า = tools/web/ui_mock.tpl.html
# อ้างอิงหน้าตา: ชีต UI ที่ kwan ส่ง + ภาพเมนู RS3 (โครงวาง/ลำดับเท่านั้น — ไม่มีรูป/โค้ดจากเกมอื่นในหน้านี้)
import base64, csv, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL = os.path.join(ROOT, 'tools/web/ui_mock.tpl.html')
SPR = os.path.join(ROOT, 'assets/sprites')

def b64(rel):
	with open(os.path.join(SPR, rel), 'rb') as f:
		return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

def dump():
	g = os.environ.get('GODOT', 'godot')
	env = dict(os.environ, REBORNER_SAVE='user://test_save.json')
	out = subprocess.run([g, '--headless', '--path', ROOT, '-s', 'tools/web/ui_mock_dump.gd'],
		capture_output=True, text=True, timeout=180, env=env).stdout
	for line in out.splitlines():
		if line.startswith('JSON:'):
			return json.loads(line[5:])
	sys.exit('ui_mock_dump.gd ไม่คืนค่า — ตั้ง GODOT ให้ถูก')

def rows(path):
	return list(csv.DictReader(open(os.path.join(ROOT, path), encoding='utf-8')))

def main():
	out = sys.argv[1] if len(sys.argv) > 1 else 'ui_mock.html'
	data = dump()
	data['weapons'] = rows('data/weapons.csv')
	data['affinity'] = rows('data/body_affinity.csv')
	data['items'] = rows('data/items.csv')
	data['dialogue'] = rows('data/dialogue.csv')
	img = {
		'rion_s': 'rion_lastlight_draft/south.png', 'rion_w': 'rion_lastlight_draft/west.png',
		'B1': 'monsters_ll/B1.png', 'M06': 'monsters_ll/M06.png', 'M03': 'monsters_ll/M03.png',
		'M01': 'monsters_ll/M01.png', 'M15': 'monsters_ll/M15.png',
		'C03': 'monsters_ll/COMP-M03.png', 'C06': 'monsters_ll/COMP-M06.png',
		'I01': 'items_draft/I01.png', 'L01': 'items_draft/L01.png', 'DB1': 'items_draft/D-B1.png',
	}
	for w in data['weapons']:
		img['W' + w['weapon_id']] = 'weapons_draft/%s.png' % w['weapon_id']
	data['img'] = {k: b64(v) for k, v in img.items()}
	html = open(TPL, encoding='utf-8').read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
	open(out, 'w', encoding='utf-8').write(html)
	print(out, len(html), 'bytes ·', len(img), 'รูป ·', len(data['techs']), 'ท่า')

if __name__ == '__main__':
	main()
