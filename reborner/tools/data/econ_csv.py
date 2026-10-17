# tools/data/econ_csv.py — เสนอราคาเศรษฐกิจจากข้อมูลที่มีอยู่ (GDD 9) · รันซ้ำได้ ไม่ทับค่าที่ kwan แก้แล้ว
#
#   python3 tools/data/econ_csv.py && python3 tools/data/weapons_csv.py
#
# 1) data/materials.csv — ของดรอปที่ขายได้ (หมวด วัตถุดิบ/เงิน ใน assets/sprites/items_draft/index.json)
#    sell_base = round(tier × MATERIAL_INCOME_SHARE × 100 ÷ drop_rate) → ค่าคาดหวังต่อตัว = tier × share = share ของเงินชนะศึก
#    แถวที่ status ไม่ใช่ "เสนอ" (kwan ยืนยัน/แก้แล้ว) เก็บไว้ตามเดิม
# 2) docs/art-bible/weapons/weapons_full.json — ใส่ "price" ให้อาวุธที่ยังไม่มี (price_status "เสนอ")
#    price = ค่าอาวุธ × WEAPON_PRICE_PER_VALUE · ไม่มี weapon_base ใช้กลางช่วง value_range ของ tier
#    แทรกเป็นข้อความในบรรทัดเดิม (ไม่จัดรูปแบบไฟล์ใหม่) · มี price แล้วไม่แตะ
# ค่าตั้งต้นทั้งสองอยู่ใน data/economy.csv
import csv, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ECON = os.path.join(ROOT, 'data/economy.csv')
MONSTERS = os.path.join(ROOT, 'data/monsters.csv')
ITEMS = os.path.join(ROOT, 'assets/sprites/items_draft/index.json')
MATERIALS = os.path.join(ROOT, 'data/materials.csv')
WEAPONS = os.path.join(ROOT, 'docs/art-bible/weapons/weapons_full.json')
SELLABLE = ('วัตถุดิบ', 'เงิน')   # ตำรา/ของสำคัญ ห้ามขาย

def knobs():
	return {r['key']: float(r['value']) for r in csv.DictReader(open(ECON, encoding='utf-8'))}

def materials(k):
	mons = {r['monster_id']: r for r in csv.DictReader(open(MONSTERS, encoding='utf-8'))}
	kept = {}
	if os.path.exists(MATERIALS):
		for r in csv.DictReader(open(MATERIALS, encoding='utf-8')):
			if r['status'] != 'เสนอ':
				kept[r['item_id']] = r
	share = k['MATERIAL_INCOME_SHARE']
	rows = []
	for it in json.load(open(ITEMS, encoding='utf-8'))['items']:
		if it.get('cat') not in SELLABLE:
			continue
		if it['id'] in kept:
			rows.append(kept[it['id']])
			continue
		src = it['sources'][0]
		m = mons[src['monster_id']]
		tier, rate = int(m['tier']), float(m['drop_rate'])
		base = max(1, round(tier * share * 100 / rate))
		rows.append({'item_id': it['id'], 'name': it['name'], 'monster_id': src['monster_id'], 'sell_base': base,
			'status': 'เสนอ', 'note': 'tier %d × %.2f × 100 ÷ ดรอป %g%% · %s' % (tier, share, rate, it['cat'])})
	with open(MATERIALS, 'w', encoding='utf-8', newline='') as f:
		w = csv.DictWriter(f, ['item_id', 'name', 'monster_id', 'sell_base', 'status', 'note'], lineterminator='\n')
		w.writeheader()
		w.writerows(rows)
	return len(rows), len(kept)

def weapon_prices(k):
	d = json.load(open(WEAPONS, encoding='utf-8'))
	per = k['WEAPON_PRICE_PER_VALUE']
	want = {}
	for fam in d['families']:
		for w in fam['weapons']:
			if 'price' in w:
				continue
			base = w.get('weapon_base')
			if base is None:
				lo, hi = d['tiers'][str(w['tier'])]['value_range']
				base, how = (lo + hi) / 2, 'กลางช่วง %d–%d' % (lo, hi)
			else:
				how = 'weapon_base %d' % base
			want[w['id']] = (round(base * per), how)
	text = open(WEAPONS, encoding='utf-8').read()
	for wid, (price, how) in want.items():
		pat = re.compile(r'(\{"id": "%s",.*?)("concept":)' % re.escape(wid))
		text, n = pat.subn(lambda m: '%s"price": %d, "price_status": "เสนอ", "price_note": "%s × %g", %s'
			% (m.group(1), price, how, per, m.group(2)), text, count=1)
		if n != 1:
			raise SystemExit('หาแถวอาวุธ %s ใน JSON ไม่เจอ' % wid)
	json.loads(text)
	open(WEAPONS, 'w', encoding='utf-8').write(text)
	return len(want)

if __name__ == '__main__':
	k = knobs()
	n, kept = materials(k)
	print('materials.csv %d แถว (เก็บค่าที่ยืนยันแล้ว %d) · อาวุธใส่ราคาใหม่ %d ชิ้น' % (n, kept, weapon_prices(k)))
