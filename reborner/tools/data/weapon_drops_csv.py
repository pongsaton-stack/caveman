# tools/data/weapon_drops_csv.py — ดรอปอาวุธจากมอนปกติ → data/weapon_drops.csv (ที่เกมอ่าน · ระบบ pity)
#
#   python3 tools/data/weapon_drops_csv.py
#
# แหล่ง: docs/design/team_r3/WEAPON_SOURCES_60.xlsx ชีตแรก แถวที่ "แหล่ง" = ดรอป (kwan 26 ต.ค. รับเป็นแหล่งอาวุธ 60 ชิ้น)
# กติกา pity อยู่ที่ docs/design/team_r3/PITY_SPEC.md · ตัวเลข pity อยู่ใน data/economy.csv (PITY_*) · ห้ามแก้ CSV ตรงๆ
# คอลัมน์: monster_id · weapon_id · base_rate (เปอร์เซ็นต์) · source (ข้อความแหล่งเดิมจากชีต)
import csv, os, re, sys
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'docs/design/team_r3/WEAPON_SOURCES_60.xlsx')
OUT = os.path.join(ROOT, 'data/weapon_drops.csv')
WEAPONS = os.path.join(ROOT, 'data/weapons.csv')


def main():
	weapons = {r['weapon_id'] for r in csv.DictReader(open(WEAPONS, encoding='utf-8'))}
	ws = openpyxl.load_workbook(SRC, read_only=True).worksheets[0]
	rows, seen = [], set()
	for r in list(ws.iter_rows(values_only=True))[1:]:
		if not r or r[3] != 'ดรอป':
			continue
		wid, src = str(r[0]), str(r[4])
		m = re.match(r'(M\d+) .* เรต (\d+(?:\.\d+)?) เปอร์เซ็นต์', src)
		if not m:
			sys.exit('อ่านแถวดรอปไม่ได้: %s %s' % (wid, src))
		if wid not in weapons:
			sys.exit('%s ไม่มีใน data/weapons.csv' % wid)
		mid = m.group(1)
		if mid in seen:
			sys.exit('%s ดรอปอาวุธ 2 ชิ้น — ตัวนับ pity แยกตามชนิดมอน รองรับชิ้นเดียว' % mid)
		seen.add(mid)
		rows.append({'monster_id': mid, 'weapon_id': wid, 'base_rate': m.group(2), 'source': src})
	rows.sort(key=lambda x: int(x['monster_id'][1:]))
	with open(OUT, 'w', encoding='utf-8', newline='') as f:
		w = csv.DictWriter(f, fieldnames=['monster_id', 'weapon_id', 'base_rate', 'source'], lineterminator='\n')
		w.writeheader()
		w.writerows(rows)
	print('ok', OUT, len(rows), 'แถว')


if __name__ == '__main__':
	main()
