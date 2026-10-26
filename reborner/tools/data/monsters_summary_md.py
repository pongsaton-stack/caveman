# tools/data/monsters_summary_md.py — สรุปมอน + บอสทั้งหมดจาก data/*.csv → docs/design/regions/MONSTERS_SUMMARY.md (ส่งทีมวิจัย)
#
#   python3 tools/data/monsters_summary_md.py
#
# อ่านอย่างเดียว · ตัวเลขทุกตัวมาจาก CSV ของเกม · ห้ามแก้ .md ตรงๆ
import csv, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = lambda p: os.path.join(ROOT, 'data', p)
OUT = os.path.join(ROOT, 'docs/design/regions/MONSTERS_SUMMARY.md')


def rows(p):
	return list(csv.DictReader(open(D(p), encoding='utf-8')))


def main():
	mons = rows('monsters.csv')
	body = {r['monster_id']: r['body'] for r in rows('monster_body.csv')}
	onmap = set()
	for r in rows('encounters.csv'):
		onmap |= set(r['monster_ids'].split('|'))
	recruit = {r['monster_id'] for r in rows('recruits.csv')}
	comp = {r['monster_id'] for r in rows('companions.csv')}
	seize = {r['monster_id']: r['name_th'] for r in rows('seize_techs.csv')}
	regions = []
	for m in mons:
		if m['region'] not in regions:
			regions.append(m['region'])
	O = []
	o = O.append
	o('# REBORNER — สรุปมอนและบอสทั้งหมดในเกม (สำหรับทีมวิจัย)')
	o('')
	o('> สร้างอัตโนมัติด้วย `tools/data/monsters_summary_md.py` จาก `data/monsters.csv` · `monster_body.csv` · `encounters.csv` · `recruits.csv` · `companions.csv` · `seize_techs.csv`')
	o('> แนบคู่กับ `REGIONS_4_5_BRIEF.md` · ค่าทุกตัวคือค่าในเกมตอนนี้ (บางค่ายังเป็น `[เสนอ]` ตามไฟล์ CSV)')
	o('')
	o('## 1. ภาพรวม')
	o('')
	o('| กลุ่ม | จำนวน | tier | EC | HP | อยู่บนแผนที่จริง | รับเข้าทีมได้ |')
	o('|---|---|---|---|---|---|---|')
	for rg in regions:
		ms = [m for m in mons if m['region'] == rg]
		t = [int(m['tier']) for m in ms]
		h = [int(m['hp']) for m in ms]
		o('| %s | %d | %d–%d | %d–%s | %d–%d | %d | %d |' % (rg, len(ms), min(t), max(t), min(int(m['ec_min']) for m in ms),
			max(int(m['ec_max']) for m in ms), min(h), max(h), sum(m['monster_id'] in onmap for m in ms), sum(m['monster_id'] in recruit for m in ms)))
	o('')
	o('- **อยู่บนแผนที่จริง** = มีใน `encounters.csv` (แผนที่ภูมิภาค 1 ผืนเดียว): %s' % ' · '.join(sorted(onmap)))
	o('- **รับเข้าทีมได้ตอนนี้:** %s · **มอนร่วมทางตั้งแต่เริ่ม:** %s · **ท่ายึดได้:** %s' % (
		' · '.join(sorted(recruit)), ' · '.join(sorted(comp)), ' · '.join('%s (%s)' % kv for kv in sorted(seize.items()))))
	o('- ชนิดร่าง (ใช้กับความเข้ากันของสายอาวุธ `body_affinity.csv`): ' + ' · '.join('%s %d' % kv for kv in Counter(body.get(m['monster_id'], '?') for m in mons).most_common()))
	o('- จุดอ่อนที่ใช้: ' + ' · '.join('%s %d' % kv for kv in Counter(w for m in mons for w in m['weak'].split('|') if w).most_common()))
	o('- ข้อสังเกตจาก `CLAUDE.md`: ธาตุไฟ/น้ำแข็ง/แสง/มืดยังไม่มีท่าไหนของผู้เล่นใช้ · ศึกภูมิภาค 1 สั้นกว่าเป้า 5–8 รอบ · ท่ายึดมีแค่ M03/M06')
	cols = ['รหัส', 'ชื่อ', 'ย่าน', 'tier', 'EC', 'แถว', 'HP', 'ATK', 'DEF', 'SPD', 'ร่าง', 'อ่อน / ต้าน / ภูมิ', 'ท่าประจำ · ผล', 'สถานะที่ทำ', 'ดรอป', 'AI', 'บทบาทในเกม']
	for rg in regions:
		o('')
		o('## %s %s' % ('บอส 5 ตัว' if rg == 'บอส' else 'ภูมิภาค', '' if rg == 'บอส' else rg))
		o('')
		o('| ' + ' | '.join(cols) + ' |')
		o('|' + '---|' * len(cols))
		for m in [m for m in mons if m['region'] == rg]:
			flag = (' ★' if m['monster_id'] in onmap else '') + (' ♥' if m['monster_id'] in recruit else '')
			cell = lambda s: (s or '–').replace('|', '/')
			o('| %s%s | %s (%s) | %s | %s | %s–%s | %s | %s | %s | %s | %s | %s | %s / %s / %s | %s · %s | %s | %s | %s | %s |' % (
				m['monster_id'], flag, m['name_th'], m['name_en'], cell(m['sublocation']), m['tier'], m['ec_min'], m['ec_max'], m['grid_pos'],
				m['hp'], m['atk'], m['def'], m['spd'], body.get(m['monster_id'], '–'), cell(m['weak']), cell(m['resist']), cell(m['immune']),
				cell(m['signature_tech']), cell(m['tech_effect']), ('%s %d%%' % (m['status'], round(float(m['status_chance'] or 0) * 100))) if m['status'] else '–',
				(m['drop'] if '%' in m['drop'] else '%s %s%%' % (m['drop'], m['drop_rate'])) if m['drop'] not in ('', '-') else '–', cell(m['ai_profile']), cell(m['teaches'])))
	o('')
	o('★ = อยู่บนแผนที่ภูมิภาค 1 แล้ว · ♥ = รับเข้าทีมได้แล้ว')
	os.makedirs(os.path.dirname(OUT), exist_ok=True)
	open(OUT, 'w', encoding='utf-8').write('\n'.join(O) + '\n')
	print('ok', OUT, len(mons), 'ตัว')


if __name__ == '__main__':
	main()
