# tools/data/weapons_csv.py — ส่งออกรายชื่ออาวุธจาก docs/art-bible/weapons/weapons_full.json → data/weapons.csv (ที่เกมอ่าน)
#
#   python3 tools/data/weapons_csv.py
#
# JSON คือแหล่งเดียว (ใช้ร่วมกับ tools/sprites/weapons*.py) · แก้ชื่อ/สาย/กิ่งที่ JSON แล้วรันใหม่ · ห้ามแก้ CSV ตรงๆ
# คอลัมน์: weapon_id · existing_id (รหัสเดิมใน workbook เช่น W11) · name · school (= สายท่าใน techs.csv) · tier (1–5 ของไฟล์)
#          weapon_base (ว่าง = kwan ยังไม่กำหนด) · steer (กิ่งที่ชี้ทาง ×2 ตอนประกาย · ว่าง = ไม่ชี้ทาง · GDD 6.3)
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'docs/art-bible/weapons/weapons_full.json')
OUT = os.path.join(ROOT, 'data/weapons.csv')
TECHS = os.path.join(ROOT, 'data/techs.csv')

def main():
	d = json.load(open(SRC, encoding='utf-8'))
	branches = {}
	for r in csv.DictReader(open(TECHS, encoding='utf-8')):
		if r['branch']:
			branches.setdefault(r['school'], set()).add(r['branch'])
	rows, seen = [], {}
	for fam in d['families']:
		for w in fam['weapons']:
			steer = w.get('steer') or ''
			if steer and steer not in branches.get(fam['school'], ()):
				sys.exit('%s ชี้กิ่ง %s ซึ่งไม่มีในสาย %s' % (w['id'], steer, fam['school']))
			if steer:
				if (fam['school'], steer) in seen:
					sys.exit('กิ่ง %s/%s มีอาวุธประจำกิ่ง 2 ชิ้น (%s, %s) — GDD 6.3 ให้ 1 ชิ้นต่อกิ่ง' % (fam['school'], steer, seen[(fam['school'], steer)], w['id']))
				seen[(fam['school'], steer)] = w['id']
			base = w.get('weapon_base')
			rows.append([w['id'], w.get('existing_id', ''), w['name'], fam['school'], w['tier'], '' if base is None else base, steer])
	missing = [(s, b) for s in branches for b in branches[s] if (s, b) not in seen]
	with open(OUT, 'w', encoding='utf-8', newline='') as f:
		wr = csv.writer(f, lineterminator='\n')
		wr.writerow(['weapon_id', 'existing_id', 'name', 'school', 'tier', 'weapon_base', 'steer'])
		wr.writerows(rows)
	print('ok', len(rows), 'ชิ้น · ชี้ทาง', len(seen), 'กิ่ง', ('· กิ่งที่ยังไม่มีอาวุธประจำ: %s' % missing) if missing else '· ครบทุกกิ่ง')

if __name__ == '__main__':
	main()
