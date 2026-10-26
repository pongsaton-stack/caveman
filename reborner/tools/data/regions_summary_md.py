# tools/data/regions_summary_md.py — สรุปภูมิภาค 1–3 จาก data/*.csv + แผนที่ → docs/design/regions/REGIONS_1_3_SUMMARY.md (ส่งทีมวิจัย)
#
#   python3 tools/data/regions_summary_md.py
#
# อ่านอย่างเดียว · ตารางตัวเลขมาจาก CSV ของเกม · ข้อความเรื่อง/เส้นการเติบโตอ้างหัวข้อใน GDD/STORY_DRAFT (คัดมาตามตัวอักษร)
import csv, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = lambda p: os.path.join(ROOT, 'data', p)
OUT = os.path.join(ROOT, 'docs/design/regions/REGIONS_1_3_SUMMARY.md')
REG = ['ที่ราบเถ้า', 'เมืองใต้ซาก', 'ยอดเขาคำสาป']
BOSS = {'ที่ราบเถ้า': 'B1', 'เมืองใต้ซาก': 'B2', 'ยอดเขาคำสาป': 'B3 · B4 (B4 ย้ายไปภูมิภาค 4 ตามคำตัดสิน 26 ต.ค.)'}


def rows(p):
	return list(csv.DictReader(open(D(p), encoding='utf-8')))


def main():
	mons = rows('monsters.csv')
	byid = {m['monster_id']: m for m in mons}
	shops = rows('shops.csv')
	items = {r['item_id']: r for r in rows('items.csv')}
	tomes = {r['spell_id']: r for r in rows('tomes.csv')}
	weap = {r['weapon_id']: r for r in rows('weapons.csv')}
	mats = rows('materials.csv')
	infl = rows('inflation.csv')
	slots = rows('party_slots.csv')
	enc = rows('encounters.csv')
	chests = rows('chests.csv')
	dlg = rows('dialogue.csv')
	mp = open(D('map_ashfield.txt'), encoding='utf-8').read().splitlines()
	O = []
	o = O.append
	o('# REBORNER — สรุปภูมิภาค 1–3 (สำหรับทีมวิจัย)')
	o('')
	o('> สร้างอัตโนมัติด้วย `tools/data/regions_summary_md.py` จาก `data/*.csv` + `data/map_ashfield.txt` · แนบคู่กับ `REGIONS_4_5_BRIEF.md` และ `MONSTERS_SUMMARY.md`')
	o('> **สถานะจริง:** ภูมิภาค 1 เล่นได้ (แผนที่ · ศึก · หีบ · ร้าน · บอส · จุดพัก) · ภูมิภาค 2–3 มีแค่ข้อมูลมอน + ร้าน **ยังไม่มีแผนที่/ตารางศึก/หีบ/เควส/บทพูด**')
	o('')
	o('## 1. ภาพรวม 3 ภูมิภาค')
	o('')
	o('| ภูมิภาค | ร้าน (เปิดที่ EC) | มอน | tier | ย่าน | บอส | สถานะ |')
	o('|---|---|---|---|---|---|---|')
	for rg in REG:
		ms = [m for m in mons if m['region'] == rg]
		sh = sorted({(r['shop_id'], r['ec_min']) for r in shops if r['region'] == rg})
		subs = sorted({m['sublocation'] for m in ms})
		t = [int(m['tier']) for m in ms]
		o('| %s | %s | %d | %d–%d | %s | %s | %s |' % (rg, ' · '.join('%s (%s)' % s for s in sh), len(ms), min(t), max(t), ' · '.join(subs), BOSS[rg],
			'เล่นได้' if rg == 'ที่ราบเถ้า' else 'ข้อมูลเท่านั้น'))
	o('')
	o('**ช่วงเรื่อง / เงินเฟ้อ / ช่องมอน** (`inflation.csv` · `party_slots.csv`):')
	o('')
	o('| EC ตั้งแต่ | ตัวคูณราคา | หมายเหตุ |')
	o('|---|---|---|')
	for r in infl:
		o('| %s | ×%s | %s |' % (r['ec'], r['price_mult'], r['note']))
	o('')
	o('ช่องมอน: ' + ' · '.join('EC %s = %s ตัว' % (r['ec'], r['monster_slots']) for r in slots))
	o('')
	o('**เส้นการเติบโตที่จำลองไว้ (GDD 4.5 · เส้นทางหลัก ~190 ศึก ≈ 10–12 ชม. · คัดตามตัวอักษร):**')
	o('')
	o('| ช่วง | ศึกสะสม | ความชำนาญ | ATK | HP | ท่าที่ประกาย |')
	o('|---|---|---|---|---|---|')
	for r in [('ภูมิภาค 1 ต้น', 18, 16, 57, 122, 1), ('ภูมิภาค 1 ปลาย / บอส 1', 57, 30, 103, 152, 4), ('ภูมิภาค 2 ปลาย', 122, 48, 170, 193, 6),
		('บอส 3', 145, 58, 204, 213, 6), ('บอส 4 มังกร', 168, 66, 222, 231, 6), ('บอส 5', 189, 73, 312, 243, '6/6')]:
		o('| %s | %s | %s | %s | %s | %s |' % r)
	o('')
	o('ค่าวัดเศรษฐกิจ (GDD 9 · 12.4): รายได้ต่อศึกภูมิภาค 1 ≈ 10.5 (Sim) · ภูมิภาค 3 ≈ 35 (ประมาณจาก "ยา 130 = 3.7 ศึก" ไม่ใช่ค่าวัด) · เงินเริ่ม 600 · ตายเสียเงินครึ่ง')
	for n, rg in enumerate(REG, 1):
		o('')
		o('## %d. ภูมิภาค %d — %s' % (n + 1, n, rg))
		o('')
		ms = [m for m in mons if m['region'] == rg]
		o('### มอนตามย่าน')
		o('')
		o('| ย่าน | มอน (รหัส ชื่อ tier EC) |')
		o('|---|---|')
		for sub in sorted({m['sublocation'] for m in ms}):
			o('| %s | %s |' % (sub, ' · '.join('%s %s t%s EC%s–%s' % (m['monster_id'], m['name_th'], m['tier'], m['ec_min'], m['ec_max']) for m in ms if m['sublocation'] == sub)))
		o('')
		o('### ร้าน')
		o('')
		o('| ประเภท | ของ | ราคาฐาน | สต๊อก | สถานะแถว | หมายเหตุ |')
		o('|---|---|---|---|---|---|')
		for r in [r for r in shops if r['region'] == rg]:
			k, ref = r['kind'], r['ref_id']
			if k == 'item':
				nm, pr = items[ref]['name'], items[ref]['price']
			elif k == 'tome':
				nm, pr = '%s (%s)' % (tomes[ref]['name'], tomes[ref]['school']), tomes[ref]['price']
			else:
				w = weap[ref]
				nm, pr = '%s %s' % (ref, w['name']), w['price'] + ('' if w['weapon_base'] else ' (ยังไม่ขึ้นร้าน: ไม่มีค่าพลังจริง)')
			o('| %s | %s | %s | %s | %s | %s |' % (k, nm, pr, r['stock'], r['status'], (r.get('note') or '–').replace('|', '/')))
		o('')
		mm = [x for x in mats if byid.get(x['monster_id'], {}).get('region') == rg]
		o('### ของดรอปขายได้ (`materials.csv`)')
		o('')
		o(' · '.join('%s (%s) %s' % (x['name'], x['monster_id'], x['sell_base']) for x in mm) or '–')
		if rg == 'ที่ราบเถ้า':
			o('')
			o('### แผนที่ภูมิภาค 1 (`data/map_ashfield.txt` · 40×24)')
			o('')
			o('```')
			o('\n'.join(mp))
			o('```')
			o('')
			cnt = Counter(ch for ln in mp if not ln.startswith(';') for ch in ln)
			o('- จุดพัก R: %d · จุดเริ่ม H: %d · ร้าน S: %d · บอส B: %d · หีบ: %d' % (cnt['R'], cnt['H'], cnt['S'], cnt['B'], sum(cnt[c['symbol']] for c in chests)))
			o('- จุดเกิดศัตรู: ' + ' · '.join('`%s` %s ×%d จุด' % (e['symbol'], e['label'], cnt[e['symbol']]) for e in enc if e['boss'] == '0'))
			o('- หีบ: ' + ' · '.join('`%s` %s (%s · ค่า %s)' % (c['symbol'], c['label'], c['weapon_id'], c['weapon_base']) for c in chests))
			o('- มอนร่วมทางตั้งแต่เริ่ม: หนอนหิน M03 + ค้างคาวเงา M06 (`companions.csv`) · บทพูดในเกมตอนนี้ %d บรรทัด (`dialogue.csv`): %s' % (
				len(dlg), ' · '.join('"%s"' % d['text'] for d in dlg)))
			o('- ลำดับฉากเปิดเรื่อง 0–7 (30–40 นาที) อยู่ที่ `docs/STORY_DRAFT.md` หัวข้อ 4 — โค้ดกล่องข้อความ/ธงฉากยังไม่ได้ทำ')
			o('- มอนภูมิภาค 1 ที่ยังไม่อยู่บนแผนที่: ' + ' · '.join('%s %s' % (m['monster_id'], m['name_th']) for m in ms if m['monster_id'] not in {i for e in enc for i in e['monster_ids'].split('|')}))
	o('')
	o('## 5. ช่องว่างที่ทีมวิจัยควรรู้')
	o('')
	o('- **เควส:** GDD 8 ออกแบบ 24 เควส (เห็นได้ 14 ต่อรอบ) แต่ **ยังไม่มีข้อมูลเควสใน `data/` เลย** · EC ตอนนี้เพิ่มเมื่อชนะบอสเท่านั้น')
	o('- **ภูมิภาค 2–3:** ไม่มีแผนที่ · ตารางศึก · หีบ · จุดพัก · บทพูด — มีแค่มอน 15 ตัว/ภูมิภาค + ร้าน')
	o('- **ยังไม่มีในเกม:** หนี · ใช้ไอเท็มในศึก · สมุดบันทึก · ระบบเควส · สายเวทย์ (ร่างในหน้าเทสเท่านั้น)')
	o('- **ตำรา 16 เล่ม** ใน `tomes.csv` (ขาว 4 · ดำ 6 · แดง 5 · อัญเชิญ 1) · GDD 7 วางไว้ 28 เล่ม')
	os.makedirs(os.path.dirname(OUT), exist_ok=True)
	open(OUT, 'w', encoding='utf-8').write('\n'.join(O) + '\n')
	print('ok', OUT, len(O), 'บรรทัด')


if __name__ == '__main__':
	main()
