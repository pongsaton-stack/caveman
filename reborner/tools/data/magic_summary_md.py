# tools/data/magic_summary_md.py — สรุประบบเวทย์ทั้งหมด → docs/design/magic/MAGIC_SUMMARY.md (ส่งทีมวิจัย)
#
#   python3 tools/data/magic_summary_md.py
#
# อ่านอย่างเดียว · ตารางมาจาก data/tomes.csv · data/shops.csv · data/monsters.csv · docs/art-bible/spells/spells_full.json
# ข้อความกติกา/บทเรียนอ้างหัวข้อ GDD 7 และ 11 (คัดสาระ ไม่แต่งตัวเลขเพิ่ม)
import csv, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = lambda p: os.path.join(ROOT, 'data', p)
SPELLS = os.path.join(ROOT, 'docs/art-bible/spells/spells_full.json')
SPR = os.path.join(ROOT, 'assets/sprites/spells_draft')
OUT = os.path.join(ROOT, 'docs/design/magic/MAGIC_SUMMARY.md')


def rows(p):
	return list(csv.DictReader(open(D(p), encoding='utf-8')))


def main():
	tomes = {r['spell_id']: r for r in rows('tomes.csv')}
	shops = rows('shops.csv')
	mons = rows('monsters.csv')
	sp = json.load(open(SPELLS, encoding='utf-8'))
	frames = Counter(f.split('_')[0] for f in os.listdir(SPR) if f.endswith('.png')) if os.path.isdir(SPR) else Counter()
	sold = {}
	for r in shops:
		if r['kind'] == 'tome':
			sold.setdefault(r['ref_id'], []).append('%s (EC %s)' % (r['region'], r['ec_min']))
	drops = [(m['monster_id'], m['name_th'], m['region'], m['drop'], m['drop_rate']) for m in mons if 'ตำรา' in m['drop']]
	weak = Counter(w for m in mons for w in m['weak'].split('|') if w)
	O = []
	o = O.append
	o('# REBORNER — สรุประบบเวทย์ (สำหรับทีมวิจัย)')
	o('')
	o('> สร้างอัตโนมัติด้วย `tools/data/magic_summary_md.py` จาก `data/tomes.csv` · `shops.csv` · `monsters.csv` · `docs/art-bible/spells/spells_full.json` · กติกาอ้าง `docs/GDD.md` หมวด 7 และ 11')
	o('> แนบคู่กับ `REGIONS_1_3_SUMMARY.md` · `MONSTERS_SUMMARY.md` · `REGIONS_4_5_BRIEF.md`')
	o('')
	o('## 1. สถานะในเกมตอนนี้')
	o('')
	o('- **ยังใช้เวทย์ในศึกไม่ได้** — สายเวทย์ยังไม่เข้าเกม (CLAUDE.md "ยังไม่มี: สายเวทย์ (ร่างในหน้าเทสเท่านั้น)")')
	o('- **ซื้อตำราได้แล้วแต่อ่านไม่ได้** — `PlayerState.tomes` เก็บไว้ · ร้านขึ้นข้อความ "ยังอ่านไม่ได้ — สายเวทย์ยังไม่เข้าเกม"')
	o('- **มีในโค้ดแล้ว:** สูตร MAG และ SP (`core/Formulas.gd`) · ราคาตำรา (`core/Economy.gd`) · ไม่มีต้นไม้ท่าเวทย์ใน `data/techs.csv` (มีแค่ 6 สายอาวุธ 52 ท่า)')
	o('- **ภาพร่าง:** ท่าร่าย + เอฟเฟกต์ %d คาถา %d ไฟล์ใน `assets/sprites/spells_draft/` (`tools/sprites/spells_anim.py`) · ดูได้ในหน้า animation test' % (len(frames), sum(frames.values())))
	o('')
	o('## 2. กติกาใน GDD หมวด 7')
	o('')
	o('**สูตร (GDD 4):** `MAG = 20 + MagicProf × 1.6 + StaffBase` · `SP = 34 + WeaponProf + MagicProf` · ดาเมจ Base = (เวทย์ ? MAG : ATK) × SkillPower ÷ 100 · INT ยุบรวมกับ MAG แล้ว')
	o('')
	o('| สาย | รุ่น | ตัวตน (GDD 7.1) |')
	o('|---|---|---|')
	for s in sp['schools']:
		o('| %s (%s) | %s | %s |' % (s['name'], s['gdd'], s['version'], s['identity']))
	o('')
	o('- **White ต้องเป็นสายป้องกัน ไม่ใช่สายเติม HP** — ฮีลเชิงตอบสนองในศึกสั้นและร้ายแรงแพ้เสมอ (11.7) · เติม HP เป็นหน้าที่ของไอเทม')
	o('- **เรือธงของ Red = "ใส่จุดอ่อน"** ธาตุกายภาพ (ฟัน/ทุบ) — เปิด PushMult ให้ศัตรูที่ไม่มีจุดอ่อน ทั้งปาร์ตี้ได้ประโยชน์')
	o('- **ตำรา = ราก · ประกาย = กิ่ง** (7.2) — ตำราปลดโหนดรากของต้นไม้เวทย์ ประกายแตกกิ่งต่อเอง · **จำเป็น** ไม่งั้นสายเวทย์เลิกประกายถาวร (11.6)')
	o('- **แหล่งตำรา** (7.3): พื้นฐาน → ร้าน/รางวัลเควส 100% · ระดับกลาง → ดรอป 15–25% จากมอนที่สู้ซ้ำได้ · ชั้นสูง + อัญเชิญ → บอสดรอป 100% · **อะไรที่ขาดแล้วเกมพัง ห้ามเป็น RNG**')
	o('- **อ่านได้เฉพาะที่จุดพัก** (7.4): จุดพักละ 3 ช่วงเวลา · อ่าน 1 เล่ม = 1 ช่วง · ทั้งเกม ~14 จุดพัก = 42 ช่วง · วางแผนตำรา 28 เล่ม · **ตำราพื้นฐาน 8 เล่มแรกอ่านฟรี** · ต้องมีความชำนาญสายนั้นถึงเกณฑ์')
	o('- Summoner: ครั้งเดียวต่อศึก · เผา Insight ทั้งหมด · พลัง = 110 + Insight × 2.8')
	o('- เส้นทางจำลอง (GDD 4.5): ตอนจบ White 63 · Black 67 · เวทย์ 5 คาถา · MAG 39 (ต้นเกม) → 168 (บอส 5)')
	o('')
	o('## 3. คาถา 16 คาถา (ร่าง 5 ต.ค. · `spells_full.json` + `tomes.csv`)')
	o('')
	o('| รหัส | ชื่อ | สาย | ธาตุ | เป้า | ผล | พลัง | ราคาตำรา | ขายที่ | หมายเหตุตำรา | ภาพร่าง |')
	o('|---|---|---|---|---|---|---|---|---|---|---|')
	for s in sp['schools']:
		for x in s['spells']:
			t = tomes.get(x['id'], {})
			o('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (x['id'], x['name'], s['name'], x.get('element') or '–', x.get('scope') or '–',
				x.get('effect') or '–', x['power'] if x.get('power') is not None else ('(ยังไม่กำหนด)' if 'power' in x else '–'), t.get('price', '–'),
				' · '.join(sold.get(x['id'], [])) or 'ไม่วางขาย', (t.get('note') or '–').replace('|', '/'), '%d เฟรม' % frames[x['id']] if frames[x['id']] else '–'))
	o('')
	o('## 4. มอนที่ดรอปตำรา (`monsters.csv`)')
	o('')
	o('| มอน | ภูมิภาค | ดรอป | อัตรา % |')
	o('|---|---|---|---|')
	for d in drops:
		o('| %s %s | %s | %s | %s |' % (d[0], d[1], d[2], d[3].replace('|', '/'), d[4]))
	o('')
	o('## 5. บทเรียนที่วัดแล้ว (GDD 11 · คัดสาระ)')
	o('')
	o('- **11.5** ความชำนาญเวทย์ 0 → ชนะ 89% · 12 → 70% · 26 → 91% (กราฟตัว U — ⚠ 11.19 ชี้ว่าอาจเป็นผลของ AI จำลอง ต้องยืนยันด้วยคนเล่น)')
	o('- **11.6** เวทย์ฆ่าประกาย ถ้าเวทย์ประกายไม่ได้: วัดครั้งแรกตัวเอกใช้ท่าดาบ 0 ครั้ง อัตราประกาย 0.0% → แก้ด้วยให้สายเวทย์แตกกิ่งได้')
	o('- **11.7** ฮีลเชิงตอบสนองแพ้ในศึกสั้นและร้ายแรง (เสียเทิร์นเต็มเพื่อซื้อเวลาไม่ถึงครึ่งเทิร์น)')
	o('- **11.18** ล้างสถานะไม่เคยถูกใช้ (0.00/ศึก) เพราะ AI รอ 2 สถานะ → ลดเป็น 1 ได้ 0.51/ศึก')
	o('- **11.19** ศึกหมาป่า ตัวเอกสายเวทย์: AI จำลอง (มีซัพพอร์ต) ชนะ 49% · เล่นทุ่มดาเมจอย่างเดียว 100% — อัตราชนะทุกตัวคือขอบล่าง')
	o('')
	o('## 6. ช่องว่างและจุดเชื่อมที่ทีมวิจัยควรรู้')
	o('')
	o('- **ค่าพลังคาถา Black ทั้ง 6 = ยังไม่กำหนด** (GDD ไม่ระบุ · ร่างใส่เฉพาะตัวเลขที่ GDD มี)')
	o('- **ไม่มีต้นไม้ท่าเวทย์** — GDD 7.2 ต้องการ ราก (ตำรา) → กิ่ง (ประกาย) แต่ยังไม่มีโหนดกิ่งเลย')
	o('- **ตำรา 16 เล่ม** (ขาว 4 · ดำ 6 · แดง 5 · อัญเชิญ 1) เทียบแผน 28 เล่ม · บอส B2/B4 ดรอปตำราอัญเชิญ #1/#2 แต่มีอัญเชิญในรายการแค่ SM-1 · B3 ดรอป Red "หยุดเวลา" ซึ่งไม่อยู่ใน 16 คาถา')
	o('- **StaffBase ของ MAG ไม่มีอาวุธรองรับ** — ชุดอาวุธ 60 ชิ้น (MASTER) ไม่มีสายไม้เท้า/เวทย์ → StaffBase = 0 ตลอด ต้องตัดสินว่าจะเพิ่มของเสริม MAG หรือแก้สูตร')
	o('- **ธาตุจากเวทย์เท่านั้น:** ท่าอาวุธทั้งหมดไม่มีธาตุ ไฟ/น้ำแข็ง/แสง/มืด แต่มอนอ่อนแอต่อ ' + ' · '.join('%s %d' % (k, weak[k]) for k in ('ไฟ', 'แสง', 'น้ำแข็ง', 'มืด') if weak[k]) + ' ตัว (`monsters.csv`) — เวทย์ Black คือทางเดียวที่ใช้จุดอ่อนเหล่านี้ (ท่าอาวุธมีธาตุ ฟัน/ทุบ/แทง + สายฟ้า 2 ท่า)')
	o('- **ภูมิภาค 4–5:** ยังไม่มีการวางว่าตำราไหนได้ที่ภูมิภาคใหม่ · ช่วงเวลาที่จุดพัก 42 ช่วงคิดจาก 3 ภูมิภาค')
	os.makedirs(os.path.dirname(OUT), exist_ok=True)
	open(OUT, 'w', encoding='utf-8').write('\n'.join(O) + '\n')
	print('ok', OUT, len(O), 'บรรทัด')


if __name__ == '__main__':
	main()
