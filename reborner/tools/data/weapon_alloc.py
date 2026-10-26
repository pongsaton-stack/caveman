# tools/data/weapon_alloc.py — แม่แบบ + ตัวตรวจผลงานจัดสรรความสามารถอาวุธ 60 ชิ้น (โจทย์ docs/design/weapons60/WEAPON_ALLOCATION_BRIEF.md)
#
#   python3 tools/data/weapon_alloc.py template <out.md>   สร้างไฟล์แม่แบบ (60 แถวเรียงแล้ว ช่องที่ล็อกกรอกให้แล้ว)
#   python3 tools/data/weapon_alloc.py check <file.md>     ตรวจตามรายการ F + กติกา H ของโจทย์ · exit 0 = ผ่าน
#
# ตัวเดียวกับที่ Claude ใช้ตรวจรับ · ทีมรันเองได้ (Python 3.8+ ไม่ต้องลงอะไรเพิ่ม) · ระบุ --json <weapons_full.json> ถ้ารันนอก repo
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON = os.path.join(ROOT, 'docs/art-bible/weapons/weapons_full.json')
FAMS = ['SL', 'CR', 'PC', 'ST', 'DV', 'BD']
SCHOOL = {'SL': 'คม', 'CR': 'ทุบ', 'PC': 'แทง', 'ST': 'ยิง', 'DV': 'กล', 'BD': 'มือเปล่า'}
BRANCH = {'SL': ['เขี้ยว', 'กวาด', 'ลื่นไหล', 'ไม้ตาย'], 'CR': ['สั่นสะเทือน', 'ถ่วง', 'ทลาย'], 'PC': ['จังหวะ', 'ระยะ', 'เจาะ'],
	'ST': ['กระจาย', 'ตั้งท่า', 'แม่นยำ'], 'DV': ['อัตโนมัติ', 'รบกวน', 'สนับสนุน'], 'BD': ['เร็ว', 'ต่อเนื่อง', 'ประสาน']}
MODS = ['คมเฉียบ', 'เบามือ', 'หนักหน่วง', 'เขี้ยวคู่', 'สลักปริศนา', 'ครูฝึก', 'ดวงตานักเรียน', 'ยาวถึง', 'ตลับความจำ', 'ยันต์ชีวิต',
	'หัวคิว', 'ส่งไม้', 'ประกายคับขัน', 'อ่านก่อนศึก', 'ตั้งหลักแถวหลัง', 'จำแม่น ลืมไว', 'ประหยัด SP', 'ฝังสถานะ', 'เกราะ LP สำรอง', 'เครื่องทน เติมคุ้ม']
WEAKABLE = ['คมเฉียบ', 'เบามือ', 'หนักหน่วง', 'สลักปริศนา', 'ครูฝึก', 'ตลับความจำ', 'หัวคิว', 'ประกายคับขัน', 'ประหยัด SP']
HARD = ['ส่งไม้', 'จำแม่น ลืมไว', 'เกราะ LP สำรอง']
DMG_ST = ['พิษ', 'เลือดไหล']
CTL_ST = ['หน่วง', 'ตรึง', 'ผนึก', 'สับสน']
RATE = {'dmg': {6: 20, 7: 20, 8: 20, 9: 25, 10: 25}, 'ctl': {6: 15, 7: 15, 8: 15, 9: 20, 10: 20}}
LIMITS = {'ทนทาน': 'ครั้ง', 'ขว้าง': 'ครั้ง', 'กระสุน': 'นัด', 'แบต': 'เทิร์น', 'พลัง': 'เทิร์น', 'ประจุ': 'ครั้ง', 'แรงแขน': 'ครั้ง'}
VALUE = {1: 16, 2: 22, 3: 30, 4: 40, 5: 54, 6: 70, 7: 84, 8: 95, 9: 118, 10: 135}
EXCEPT = {'SL-1': 14, 'CR-2': 28}
COLS = ['รหัส', 'ชื่อ', 'ชี้ทาง', 'ตัวปรับ 1', 'ตัวปรับ 2', 'ตัวปรับอ่อน', 'สถานะ', 'อัตรา %', 'ข้อจำกัด', 'จำนวนต่อเติม', 'หน่วย', 'ค่าเติม', 'ค่าบำรุง', 'เหตุผล']
DASHES = {'-', '–', '—', '−', ''}
BANNED = ['ActionWeight', 'PushMult', 'AV', 'rank', 'ThreatFactor', 'Insight', 'PosMult', 'LP']


def lv(wid):
	return int(wid.split('-')[1])


def half_up(x):
	return int(x + 0.5)


def price(wid):
	return EXCEPT.get(wid, VALUE[lv(wid)]) * 10


def refill(wid):
	return half_up(price(wid) * 0.05)


def visible_len(s):
	"""นับอักษรที่ตาเห็น: ไม่นับสระบน/ล่างและวรรณยุกต์ (Unicode Mn) — กติกา H1"""
	return sum(1 for c in s if unicodedata.category(c) != 'Mn')


def norm(c):
	c = c.strip()
	return '' if c in DASHES else c


def weapons(path):
	d = json.load(open(path, encoding='utf-8'))
	return [(w['id'], w['name']) for f in d['families'] for w in f['weapons']]


def template(out, jpath):
	ws = weapons(jpath)
	O = ['# ผลงานจัดสรรความสามารถอาวุธ 60 ชิ้น', '', '> ทีม: … · วันที่: … · ตรวจด้วย `python3 tools/data/weapon_alloc.py check <ไฟล์นี้>` ก่อนส่ง', '',
		'## 1. นิยามตัวปรับ', '',
		'| ชื่อ | ผลทางกลไก (ตัวเลขครบ) | ฉบับอ่อน Lv.5 (ตัวเลขครบ หรือ –) | คำอธิบายผู้เล่น (≤ 40) | คำอธิบายผู้เล่นฉบับอ่อน (≤ 40 หรือ –) |',
		'|---|---|---|---|---|']
	O += ['| %s |  | %s |  | %s |' % (m, '' if m in WEAKABLE else '–', '' if m in WEAKABLE else '–') for m in MODS]
	O += ['', '### 1b. คำอธิบายสถานะ', '', '| สถานะ | คำอธิบายผู้เล่น (≤ 40) |', '|---|---|']
	O += ['| %s |  |' % s for s in DMG_ST + CTL_ST]
	O += ['', '## 2. ตารางอาวุธ', '', '| ' + ' | '.join(COLS) + ' |', '|' + '---|' * len(COLS)]
	for wid, name in ws:
		L = lv(wid)
		row = {c: '' for c in COLS}
		row['รหัส'], row['ชื่อ'] = wid, name
		if L <= 4 or wid == 'CR-3':
			for c in COLS[3:13]:
				row[c] = '–'
		if L == 5:
			for c in ['ตัวปรับ 1', 'ตัวปรับ 2', 'สถานะ', 'อัตรา %', 'ข้อจำกัด', 'จำนวนต่อเติม', 'หน่วย', 'ค่าเติม', 'ค่าบำรุง']:
				row[c] = '–'
			if wid == 'DV-5':
				row['ตัวปรับอ่อน'] = 'ตลับความจำ'
		if 6 <= L <= 8:
			row['ตัวปรับอ่อน'], row['ค่าบำรุง'], row['ค่าเติม'] = '–', '–', str(refill(wid))
		if L >= 9:
			for c in ['ตัวปรับ 2', 'ตัวปรับอ่อน', 'ข้อจำกัด', 'จำนวนต่อเติม', 'หน่วย', 'ค่าเติม']:
				row[c] = '–'
			row['ค่าบำรุง'] = str(refill(wid))
		if L == 3 or (L == 10 and wid != 'SL-10'):
			row['ชี้ทาง'] = '–'
		if wid == 'SL-10':
			row['ชี้ทาง'] = 'ไม้ตาย'
		O.append('| ' + ' | '.join(row[c] for c in COLS) + ' |')
	O += ['', '## 3. สมมติฐานอายุข้อจำกัด', '', '| ประเภท | อัตราใช้ต่อศึก | จำนวนต่อเติม | อายุ (ศึก) |', '|---|---|---|---|']
	O += ['| %s |  |  |  |' % k for k in LIMITS]
	O += ['', '## 4. ผลตรวจตัวเอง', '', '(วางผลจาก `weapon_alloc.py check` + เหตุผลของข้อที่แย้ง/ข้อยกเว้นที่ตั้งใจ)', '']
	open(out, 'w', encoding='utf-8').write('\n'.join(O) + '\n')
	print('แม่แบบ →', out)


def tables(text):
	"""แยกตารางตามหัวข้อ ## / ### → {หัวข้อ: [แถว(list ช่อง)]}"""
	out, cur = {}, None
	for ln in text.splitlines():
		m = re.match(r'#{2,3}\s+(\S+)', ln)
		if m:
			cur = m.group(1).rstrip('.')
			out.setdefault(cur, [])
			continue
		if cur and ln.strip().startswith('|') and not re.match(r'^\|\s*-{3}', ln.strip()):
			out[cur].append([c.strip() for c in ln.strip().strip('|').split('|')])
	return out


def check(path, jpath):
	T = tables(open(path, encoding='utf-8').read())
	fails, warns = [], []
	F = lambda k, msg: fails.append('%s  %s' % (k, msg))
	W = lambda k, msg: warns.append('%s  %s' % (k, msg))
	ws = dict(weapons(jpath))
	# --- ส่วน 2
	rows = T.get('2', [])
	if not rows or rows[0] != COLS:
		F('H3', 'หัวตารางส่วน 2 ต้องเป็น %d คอลัมน์ตามแม่แบบ: %s' % (len(COLS), ' | '.join(COLS)))
		return report(fails, warns)
	R = {}
	for r in rows[1:]:
		if len(r) != len(COLS):
			F('H3', '%s: มี %d ช่อง (ต้อง %d) — ห้ามใช้ | ในเหตุผล' % (r[0], len(r), len(COLS)))
			continue
		x = dict(zip(COLS, r))
		for c in COLS[2:13]:
			if '·' in x[c] or ',' in x[c]:
				F('H4', '%s ช่อง %s มีหลายค่า — 1 ช่อง 1 ชื่อ' % (x['รหัส'], c))
			x[c] = norm(x[c])
		if x['รหัส'] in R:
			F('F1', 'รหัสซ้ำ %s' % x['รหัส'])
		R[x['รหัส']] = x
	if sorted(R) != sorted(ws) or len(R) != 60:
		F('F1', 'ต้องมี 60 รหัสตรงรายชื่อ · ขาด %s · เกิน %s' % (sorted(set(ws) - set(R)), sorted(set(R) - set(ws))))
	for k, x in R.items():
		if k in ws and x['ชื่อ'] != ws[k]:
			F('F1', '%s ชื่อไม่ตรงรายชื่อล็อก (%s ≠ %s)' % (k, x['ชื่อ'], ws[k]))
	# --- ชี้ทาง
	steer = {k: x['ชี้ทาง'] for k, x in R.items() if x['ชี้ทาง']}
	if len(steer) != 19 or len(set(steer.values())) != 19:
		F('F2', 'ชี้ทางต้อง 19 ชิ้น 19 กิ่งไม่ซ้ำ (ได้ %d ชิ้น %d กิ่ง)' % (len(steer), len(set(steer.values()))))
	for k, b in steer.items():
		if b not in BRANCH[k.split('-')[0]]:
			F('F2', '%s ชี้กิ่ง %s ซึ่งไม่ใช่กิ่งของสาย%s' % (k, b, SCHOOL[k.split('-')[0]]))
	if steer.get('SL-10') != 'ไม้ตาย':
		F('F2', 'SL-10 ต้องชี้ ไม้ตาย')
	for fam in FAMS:
		for name, lo, hi in (('ต้น', 1, 2), ('กลาง', 4, 6), ('ปลาย', 7, 9)):
			n = [k for k in steer if k.startswith(fam + '-') and lo <= lv(k) <= hi]
			if len(n) != 1:
				F('F3', 'สาย%s ช่วง%s (Lv.%d–%d) ต้องมีชี้ทาง 1 ชิ้นพอดี (ได้ %s)' % (SCHOOL[fam], name, lo, hi, n or 'ไม่มี'))
		for k in steer:
			if k.startswith(fam + '-') and (lv(k) == 3 or (lv(k) == 10 and k != 'SL-10')):
				F('F3', '%s: Lv.3 / Lv.10 ไม่อยู่ในช่วงชี้ทาง (ยกเว้น SL-10)' % k)
		if fam != 'CR' and not any(k.startswith(fam + '-') and lv(k) == 4 for k in steer):
			W('ทีม', 'สาย%s ชี้ทางช่วงกลางไม่อยู่ Lv.4 (ทีมเสนอให้ Lv.4 กันหลุม Lv.3–4)' % SCHOOL[fam])
	# --- ต่อชิ้น
	full_use = {}
	for k, x in sorted(R.items(), key=lambda kv: (FAMS.index(kv[0].split('-')[0]), lv(kv[0]))):
		L = lv(k)
		mods = [m for m in (x['ตัวปรับ 1'], x['ตัวปรับ 2']) if m]
		weak, st = x['ตัวปรับอ่อน'], x['สถานะ']
		for m in mods + ([weak] if weak else []):
			if m not in MODS:
				F('H2', '%s ตัวปรับ "%s" ไม่อยู่ในรายการ 20 ตัว (สะกดต้องตรงทุกตัวอักษร)' % (k, m))
		if st and st not in DMG_ST + CTL_ST:
			F('H2', '%s สถานะ "%s" ไม่อยู่ในรายการ 6 แบบ' % (k, st))
		if len(set(mods)) != len(mods):
			F('H2', '%s ตัวปรับซ้ำในชิ้นเดียว' % k)
		lim = x['ข้อจำกัด']
		has = lambda c: bool(x[c])
		if L <= 4 or k == 'CR-3':
			if mods or weak or st or lim or has('ค่าบำรุง') or has('อัตรา %'):
				F('F4', '%s (Lv.%d) มีได้แค่ชี้ทาง' % (k, L))
			continue
		if L == 5:
			if mods or st or lim or has('ค่าบำรุง'):
				F('F5', '%s: Lv.5 มีได้แค่ตัวปรับอ่อน 1 ตัว (ข้อจำกัด Lv.5 = ไม่มี · กติกา H5)' % k)
			if weak not in WEAKABLE:
				F('F5', '%s: ตัวปรับอ่อนต้องเป็น 1 ใน %s' % (k, ' / '.join(WEAKABLE)))
			if k == 'DV-5' and weak != 'ตลับความจำ':
				F('F5', 'DV-5 ตัวปรับอ่อนต้องเป็น ตลับความจำ')
			continue
		if weak:
			F('F5', '%s: ตัวปรับอ่อนมีได้เฉพาะ Lv.5' % k)
		for m in mods:
			full_use.setdefault(m, []).append(k)
		items = len(mods) + (1 if st else 0)
		if 6 <= L <= 8:
			if items != 2:
				F('F6', '%s: Lv.6–8 ต้องมีของ 2 อย่างพอดี (ตัวปรับ + สถานะ) ได้ %d' % (k, items))
			if not lim:
				F('F6', '%s: Lv.6–8 ต้องมีข้อจำกัด' % k)
			if has('ค่าบำรุง'):
				F('F6', '%s: Lv.6–8 ไม่มีค่าบำรุง' % k)
		if L >= 9:
			if len(mods) != 1 or not st:
				F('F7', '%s: Lv.9–10 ต้องมีตัวปรับ 1 + สถานะ 1' % k)
			if lim:
				F('F7', '%s: Lv.9–10 ไม่มีข้อจำกัด' % k)
			if x['ค่าบำรุง'] != str(refill(k)):
				F('F7', '%s: ค่าบำรุงต้อง %d' % (k, refill(k)))
			if 'ยันต์ชีวิต' in mods:
				W('ทีม', '%s: ยันต์ชีวิตเป็นตัวปรับเดี่ยว Lv.9–10 (Kawazu ห้าม)' % k)
		if 'หนักหน่วง' in mods and 'คมเฉียบ' in mods:
			F('F9', '%s: หนักหน่วง + คมเฉียบ อยู่ชิ้นเดียวกัน' % k)
		if 'เบามือ' in mods and ({'หนักหน่วง', 'คมเฉียบ', 'หัวคิว'} & set(mods) or st == 'หน่วง'):
			W('H6', '%s: เบามือร่วมกับ %s → ใช้ค่า −0.08' % (k, ' / '.join(sorted(({'หนักหน่วง', 'คมเฉียบ', 'หัวคิว'} & set(mods)) | ({'หน่วง'} if st == 'หน่วง' else set())))))
		if 'หัวคิว' in mods and {'เบามือ', 'คมเฉียบ'} & set(mods):
			W('ทีม', '%s: หัวคิวอยู่ร่วมกับตัวเร่งคิวต่อเนื่อง (Kawazu ห้าม)' % k)
		if st:
			want = RATE['dmg' if st in DMG_ST else 'ctl'][L]
			try:
				got = float(x['อัตรา %'])
			except ValueError:
				got = None
			if got != want:
				F('F10', '%s: อัตรา %s ต้อง %s (ใส่อัตราฐานตามตาราง · ฝังสถานะเกมหัก −5 เอง · กติกา H7)' % (k, st, want))
		elif has('อัตรา %'):
			F('F10', '%s: มีอัตราแต่ไม่มีสถานะ' % k)
		for m in mods:
			if m in HARD and L < 8:
				W('F11', '%s: %s ต่ำกว่า Lv.8 — ต้องมีเหตุผลในส่วน 4' % (k, m))
		if 'ฝังสถานะ' in mods and not st:
			F('H7', '%s: ฝังสถานะต้องมีสถานะของตัวเอง' % k)
		if ('เกราะ LP สำรอง' in mods or 'เครื่องทน เติมคุ้ม' in mods) and not lim:
			F('H8', '%s: เกราะ LP สำรอง / เครื่องทน เติมคุ้ม ต้องอยู่ชิ้นที่มีข้อจำกัด' % k)
		if lim:
			if lim not in LIMITS:
				F('H2', '%s: ประเภทข้อจำกัด "%s" ไม่อยู่ในรายการ %s' % (k, lim, ' / '.join(LIMITS)))
			elif x['หน่วย'] != LIMITS[lim]:
				F('H2', '%s: หน่วยของ %s ต้องเป็น %s' % (k, lim, LIMITS[lim]))
			if not x['จำนวนต่อเติม'].isdigit():
				F('H9', '%s: จำนวนต่อเติมต้องเป็นจำนวนเต็ม' % k)
			if x['ค่าเติม'] != str(refill(k)):
				F('F13', '%s: ค่าเติมต้อง %d' % (k, refill(k)))
		if not x['เหตุผล']:
			W('ทีม', '%s: ไม่มีเหตุผล' % k)
	for m, ks in full_use.items():
		if len(ks) > 3:
			F('F8', '%s ปรากฏ %d ชิ้น (เพดาน 3): %s' % (m, len(ks), ' '.join(ks)))
	for fam in FAMS:
		own = {m for m, ks in full_use.items() if all(k.startswith(fam + '-') for k in ks)}
		if not own:
			F('F12', 'สาย%s ไม่มีตัวปรับ (ฉบับเต็ม) ที่เป็นของสายนี้สายเดียว' % SCHOOL[fam])
		if not any(R[k]['สถานะ'] for k in R if k.startswith(fam + '-') and lv(k) in (6, 7)):
			W('ทีม', 'สาย%s ไม่มีสถานะใน Lv.6–7' % SCHOOL[fam])
	n68 = sum(1 for k in R if 6 <= lv(k) <= 8 and R[k]['สถานะ'])
	if n68 < 12:
		W('ทีม', 'Lv.6–8 มีสถานะ %d ชิ้น (ทีมตั้งพื้น 12)' % n68)
	# --- ส่วน 3: อายุข้อจำกัด
	life = {}
	for r in T.get('3', [])[1:]:
		if len(r) >= 3 and r[0] in LIMITS:
			try:
				life[r[0]] = float(r[1])
			except ValueError:
				F('H9', 'ส่วน 3: อัตราใช้ของ %s ต้องเป็นตัวเลข' % r[0])
	for k, x in R.items():
		lim = x['ข้อจำกัด']
		if lim in LIMITS and x['จำนวนต่อเติม'].isdigit():
			if lim not in life:
				F('F14', 'ส่วน 3 ไม่มีอัตราใช้ของ %s (ใช้ใน %s)' % (lim, k))
				continue
			yrs = int(x['จำนวนต่อเติม']) / life[lim]
			if not 2.5 <= yrs <= 3.5:
				F('F14', '%s: %s %s ÷ %.1f ต่อศึก = %.2f ศึก (ต้อง 2.5–3.5 · นับจำนวนฐานก่อนคูณเครื่องทน)' % (k, lim, x['จำนวนต่อเติม'], life[lim], yrs))
	# --- ส่วน 1 / 1b: คำอธิบาย
	defs = {r[0]: r for r in T.get('1', [])[1:] if r and r[0] in MODS}
	for m in MODS:
		if m not in defs:
			F('H2', 'ส่วน 1 ไม่มีนิยาม %s' % m)
			continue
		r = defs[m] + [''] * 5
		if not norm(r[1]):
			F('H10', '%s: ไม่มีผลทางกลไก' % m)
		for i, what in ((3, 'คำอธิบาย'), (4, 'คำอธิบายฉบับอ่อน')):
			s = norm(r[i])
			if i == 4 and m not in WEAKABLE:
				continue
			if i == 4 and m in [R[k]['ตัวปรับอ่อน'] for k in R] and not s:
				F('H10', '%s: ใช้เป็นตัวปรับอ่อนแต่ไม่มีคำอธิบายฉบับอ่อน' % m)
			if not s:
				if i == 3:
					F('F15', '%s: ไม่มีคำอธิบายผู้เล่น' % m)
				continue
			if visible_len(s) > 40:
				F('F15', '%s %s ยาว %d ตัวที่ตาเห็น (เพดาน 40)' % (m, what, visible_len(s)))
			bad = [b for b in BANNED if re.search(r'(?<![A-Za-z])%s(?![A-Za-z])' % b, s)]
			if bad:
				F('F15', '%s %s มีศัพท์ระบบ %s' % (m, what, bad))
	sdefs = {r[0]: r for r in T.get('1b', [])[1:] if r and r[0] in DMG_ST + CTL_ST}
	for s in DMG_ST + CTL_ST:
		t = norm((sdefs.get(s, ['', '']) + [''])[1])
		if not t:
			F('H10', 'ส่วน 1b ไม่มีคำอธิบายสถานะ %s' % s)
		elif visible_len(t) > 40:
			F('F15', 'สถานะ %s ยาว %d ตัวที่ตาเห็น' % (s, visible_len(t)))
	return report(fails, warns)


def report(fails, warns):
	for w in warns:
		print('เตือน ', w)
	for f in fails:
		print('ไม่ผ่าน', f)
	print('== ไม่ผ่าน %d · เตือน %d' % (len(fails), len(warns)))
	return 1 if fails else 0


if __name__ == '__main__':
	a = sys.argv[1:]
	jp = JSON
	if '--json' in a:
		i = a.index('--json')
		jp = a[i + 1]
		del a[i:i + 2]
	if len(a) == 2 and a[0] == 'template':
		template(a[1], jp)
	elif len(a) == 2 and a[0] == 'check':
		sys.exit(check(a[1], jp))
	else:
		sys.exit(__doc__ or 'ใช้: weapon_alloc.py template <out.md> | check <file.md>')
