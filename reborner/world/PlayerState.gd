# world/PlayerState.gd — สถานะตัวเอกที่อยู่ข้ามศึก (สิ่งที่ถูกเซฟ)
# Actor คือตัวละครในศึกเดียว · PlayerState คือตัวเอกตลอดการเดินทาง
class_name PlayerState
extends RefCounted

const SAVE_VERSION := 2   # 2 = มีปาร์ตี้มอน · ไอเท็ม · ร้าน

var prof := 8               # ความชำนาญ — เริ่มจากแทบไม่มีอะไร
var weapon_base := 14       # มีดทำครัว (weapons_workbook W11)
var weapon_name := "มีดทำครัว"
var gold := 600
var hp := 0
var sp := 0
var learned: Array[String] = []
var cell := Vector2i.ZERO
var rest_cell := Vector2i.ZERO
var ec := 0                 # Event Counter — ใช้ตอนมีเควส (สัปดาห์ 3)
var school := "คม"          # สายท่า = สายของอาวุธที่ถือ (data/weapons.csv) — ศึกใช้ได้เฉพาะท่าสายนี้ + ท่ายึด · ประกายในสายนี้
var steer := "เขี้ยว"        # กิ่งที่อาวุธชี้ทาง (×2 ตอนประกาย · GDD 6.3) — "" = อาวุธไม่ชี้ทาง
var weapon_id := "SL-1"       # แถวใน data/weapons.csv
var weapons_owned: Array[String] = ["SL-1"]   # อาวุธที่มี (สลับในเมนู)
var schools_held: Array[String] = []          # สายที่เคยถือ (ได้ท่ารากแล้ว) — ใช้แยก "ยังไม่เคยประกาย"
var opened: Array[String] = []    # หีบที่เปิดแล้ว (key "x,y") — ไม่เกิดใหม่
var defeated: Array[String] = []  # บอสที่ชนะแล้ว (key "x,y") — ไม่เกิดใหม่

# ── มอนร่วมทีม (GDD 5 · 3.6) ── แต่ละตัว {id, name, lp, loyalty, battles, clean_cd}
var party: Array[Dictionary] = []
var party_seeded := false
var lost: Array[String] = []          # มอนที่หายถาวรแล้ว (ชื่อ) — ไม่มีอะไรชุบได้ (GDD 9.2)
var met_species: Array[String] = []   # สายพันธุ์ที่เคยอยู่ในทีม — ใช้กับการเก็บครบ 100% (STORY_DRAFT 4.5)
var rest_count := 0                   # จุดพักที่นับแล้วตั้งแต่ LP ฟื้นครั้งล่าสุด
var fought_since_rest := false        # พักซ้ำโดยไม่สู้เลยไม่นับ (กันเดินวนจุดพักฟื้น LP)
var items: Dictionary = {}            # item_id -> จำนวน
var shop_stock: Dictionary = {}       # item_id -> ที่เหลือในร้าน (ภูมิภาคนี้)
var auto_battle := true                # กฎ UX ข้อ 1 ของ kwan: สู้อัตโนมัติเปิดตั้งแต่เริ่ม สลับได้
var materials: Dictionary = {}         # ชื่อของดรอป -> จำนวน (คอลัมน์ drop ใน monsters.csv)
var ground_drops: Dictionary = {}      # key_of(ช่อง) -> Array ชื่อของดรอปที่ยังไม่เก็บ (กฎ UX ข้อ 3)
var seized: Array[Dictionary] = []     # ท่าที่ยึดจากมอน (GDD 5.2): {id, name, slots} — สลับได้ (ลืมแล้วยึดใหม่)
var insight := 0.0                     # Insight ที่ค้างจากศึกก่อน (Insight.CARRY_BATTLE)
var reads: Dictionary = {}             # อ่านทางหลบ: monster_id -> {name, p, need, on} (Actor.reads · kwan 6 ต.ค. 2026)
var falls := 0                         # ตัวเอกล้มกี่ครั้ง (STORY_DRAFT: ไม่เคยล้ม → เบาะแส "อีกแล้ว" ย้ายมาหลังชนะบอส)
var demo_end_seen := false             # เห็นฉากจบเดโมแล้ว — ไม่แสดงซ้ำ

func init_new(techs: TechDb, start: Vector2i) -> void:
	learned.clear()
	reads.clear()
	insight = 0.0
	schools_held.clear()
	_learn_root(techs)
	cell = start
	rest_cell = start
	hp = max_hp()
	sp = max_sp()

## ช่องความจำท่า = 4 + floor(Σ Prof / 150) (GDD 5.2) — ตอนนี้ตัวเอกถือสายเดียว Σ = prof
func memory_slots() -> int:
	return Formulas.tech_slots(prof)

func used_memory() -> int:
	var n := 0
	for s in seized:
		n += int(s.get("slots", 1))
	return n

func has_seized(monster_id: String) -> bool:
	for s in seized:
		if str(s.get("id", "")) == monster_id:
			return true
	return false

func can_seize(t: Tech) -> bool:
	return t != null and not has_seized(t.src_monster) and used_memory() + t.slots <= memory_slots()

func seize(t: Tech) -> bool:
	if not can_seize(t):
		return false
	seized.append({"id": t.src_monster, "name": t.name, "slots": t.slots})
	return true

func forget(monster_id: String) -> void:
	for i in range(seized.size() - 1, -1, -1):
		if str(seized[i].get("id", "")) == monster_id:
			seized.remove_at(i)

# ── อาวุธ (kwan 6 ต.ค. 2026: "ปรับอาวุธชี้ทางให้ตรงสกิลและประกาย ตามสายของอาวุธ") ──
static var _weapons := {}
## data/weapons.csv (สร้างจาก docs/art-bible/weapons/weapons_full.json ด้วย tools/data/weapons_csv.py) · weapon_id → แถว
static func weapon_table() -> Dictionary:
	if _weapons.is_empty() and FileAccess.file_exists("res://data/weapons.csv"):
		_weapons = CsvDb.index_by(CsvDb.load_csv("res://data/weapons.csv"), "weapon_id")
	return _weapons

## หาแถวอาวุธจากรหัสใหม่ (SL-1) หรือรหัสเดิมใน workbook (W23 ที่ chests.csv ใช้) · ไม่เจอ = {}
static func weapon_row(id: String) -> Dictionary:
	var t := weapon_table()
	if t.has(id):
		return t[id]
	for k in t:
		if str(t[k].get("existing_id", "")) == id:
			return t[k]
	return {}

## ถืออาวุธชิ้นนี้ — สายท่าและกิ่งชี้ทางเปลี่ยนตามอาวุธ · ถือสายใหม่ครั้งแรกได้ท่ารากของสายนั้น · ท่าสายอื่นที่เรียนแล้วไม่หาย
## base = ค่าอาวุธ (weapons.csv ยังว่างเกือบทุกชิ้น · kwan ยังไม่กำหนด → ใช้ค่าจากหีบที่ให้มา)
func equip(row: Dictionary, techs: TechDb, base: int = -1) -> void:
	weapon_id = str(row["weapon_id"])
	weapon_name = str(row["name"])
	school = str(row["school"])
	steer = str(row.get("steer", ""))
	var wb = row.get("weapon_base", "")
	if base >= 0:
		weapon_base = base
	elif str(wb) != "":
		weapon_base = int(wb)
	if not weapons_owned.has(weapon_id):
		weapons_owned.append(weapon_id)
	_learn_root(techs)

func _learn_root(techs: TechDb) -> void:
	if not schools_held.has(school):
		schools_held.append(school)
	var root := techs.root_of(school)
	if root != null and not learned.has(root.name):
		learned.append(root.name)

## หลังโหลดเซฟ: สาย/กิ่งตามอาวุธที่ถือเสมอ (เซฟเก่าเก็บไม้เบสบอลแต่สายยังเป็น คม) · ไม่มี weapon_id = หาจากชื่อ
func sync_weapon(techs: TechDb) -> void:
	var row := weapon_row(weapon_id)
	if row.is_empty() or str(row["name"]) != weapon_name:
		for k in weapon_table():
			if str(weapon_table()[k]["name"]) == weapon_name:
				row = weapon_table()[k]
	if row.is_empty():
		_learn_root(techs)
		return
	equip(row, techs, weapon_base)

## ติดตั้งท่าหลบได้พร้อมกัน = ช่องความจำท่า ÷ 2 (kwan 6 ต.ค. 2026)
func read_slots() -> int:
	return memory_slots() / 2

func reads_on() -> int:
	var n := 0
	for k in reads:
		if bool(reads[k].get("on", false)):
			n += 1
	return n

## ถอด/ติดตั้งท่าหลบ — ทำได้เมื่ออ่านครบ 100% แล้วเท่านั้น · ติดตั้งต้องมีช่องว่าง · คืน true ถ้าเปลี่ยนได้
func toggle_read(monster_id: String) -> bool:
	if not reads.has(monster_id):
		return false
	var r: Dictionary = reads[monster_id]
	if int(r.get("p", 0)) < int(r.get("need", 1)):
		return false
	if bool(r.get("on", false)):
		r["on"] = false
		return true
	if reads_on() >= read_slots():
		return false
	r["on"] = true
	return true

func max_hp() -> int:
	return Formulas.hero_hp(prof)

func max_sp() -> int:
	return Formulas.hero_sp(prof, 0)

## สร้างตัวเอกสำหรับศึกหนึ่งศึก — HP/SP ต่อเนื่องจากศึกก่อน (ต้องไปจุดพักเพื่อฟื้นเต็ม)
func make_hero() -> Actor:
	var a := Actor.new()
	a.id = "hero"
	a.name = "Rion"
	a.side = "ally"
	a.is_hero = true
	a.tier = prof
	a.max_hp = max_hp()
	a.hp = clampi(hp, 1, a.max_hp)
	a.max_sp = max_sp()
	a.sp = clampi(sp, 0, a.max_sp)
	a.atk = Formulas.hero_atk(prof, weapon_base)
	a.def_val = Formulas.hero_def(prof)
	a.spd = 120
	a.school = school
	a.steer_branch = steer
	a.learned.clear()
	for n in learned:
		a.learned.append(n)
	# ยังไม่เคยประกาย = รู้แค่ท่ารากของสายที่เคยถือ (ท่ายึดแยกอยู่ใน seized ไม่นับ)
	a.first_glimmer_pending = learned.size() <= maxi(schools_held.size(), 1)
	a.seized.clear()
	for sz in seized:
		a.seized.append(str(sz.get("name", "")))
	a.reads = reads.duplicate(true)
	a.read_slots = read_slots()
	a.insight = insight
	return a

## รับผลจากศึกกลับมา — ท่าที่ประกาย · ความชำนาญโบนัสจาก Insight · HP/SP ที่เหลือ
## enemy_tier = tier สูงสุดของศัตรูในศึก (ใช้คิดว่า Insight ที่ได้ค้างต่อเท่าไร · Insight.carry)
func absorb(a: Actor, enemy_tier: int) -> void:
	insight = Insight.carry(insight, a.insight, enemy_tier, prof)
	prof = a.tier
	hp = a.hp
	sp = a.sp
	learned.clear()
	for n in a.learned:
		learned.append(n)
	reads = a.reads.duplicate(true)

static func key_of(c: Vector2i) -> String:
	return "%d,%d" % [c.x, c.y]

## พัก — HP/SP เต็ม · LP มอนฟื้น 1 ทุก LP_REGEN_RESTS ครั้ง (GDD 9.3) · คืนข้อความให้ UI
func rest() -> String:
	hp = max_hp()
	sp = max_sp()
	rest_cell = cell
	if not fought_since_rest:
		return ""
	fought_since_rest = false
	rest_count += 1
	if rest_count < Formulas.LP_REGEN_RESTS:
		return ""
	rest_count = 0
	var healed: Array[String] = []
	for m in party:
		if int(m["lp"]) < Formulas.LP_MAX:
			m["lp"] = int(m["lp"]) + 1
			healed.append(str(m["name"]))
	return ("LP ฟื้น: " + ", ".join(healed)) if not healed.is_empty() else ""

# ── ปาร์ตี้มอน ────────────────────────────────────────────────
## ตั้งทีมเริ่มต้นจาก data/companions.csv (ครั้งเดียวต่อเซฟ)
func seed_party(rows: Array) -> void:
	if party_seeded:
		return
	party_seeded = true
	party.clear()
	for r in rows:
		party.append({"id": str(r["monster_id"]), "name": str(r["name"]), "lp": int(r["lp"]),
			"loyalty": int(r["loyalty"]), "battles": 0, "clean_cd": 0, "slots": 1})
		if not met_species.has(str(r["monster_id"])):
			met_species.append(str(r["monster_id"]))

## จำนวนช่องมอนตาม EC จาก data/party_slots.csv (GDD 5.5 ฉบับวัดแล้ว)
static func monster_slots_for(ec_now: int, rows: Array) -> int:
	var n := 0
	for r in rows:
		if ec_now >= int(r["ec"]):
			n = maxi(n, int(r["monster_slots"]))
	return n

## รับมอนเข้าทีม (GDD 5.2) — ทีมเต็มก็รับได้ ตัวที่เกินช่องไปนั่งสำรอง · คืนชื่อที่ได้
func recruit(row: Dictionary) -> String:
	var base := str(row["name"])
	var nm := base
	var n := 2
	while not _member(nm).is_empty() or lost.has(nm):
		nm = "%s %d" % [base, n]
		n += 1
	party.append({"id": str(row["monster_id"]), "name": nm, "lp": Formulas.LP_MAX,
		"loyalty": int(row["loyalty"]), "battles": 0, "clean_cd": 0, "slots": int(row["slots"])})
	if not met_species.has(str(row["monster_id"])):
		met_species.append(str(row["monster_id"]))
	return nm

static func slot_cost(m: Dictionary) -> int:
	return maxi(1, int(m.get("slots", 1)))

## ตัวที่ได้ลงสนาม (ตามลำดับในทีม · ใส่ได้เท่าที่ช่องพอ · บอสกิน 2 ช่อง) — ที่เหลือคือสำรอง
func active_members(slots: int) -> Array:
	var out: Array = []
	var used := 0
	for m in party:
		if int(m["lp"]) <= 0:
			continue
		var c := slot_cost(m)
		if used + c > slots:
			continue
		used += c
		out.append(m)
	return out

## ย้ายมอนขึ้นหัวทีม (ได้ลงสนามก่อน)
func move_to_front(name: String) -> void:
	var m := _member(name)
	if m.is_empty():
		return
	party.erase(m)
	party.push_front(m)

## มอนที่ลงสนาม — ตามลำดับในทีม ไม่เกินจำนวนช่อง
func make_companions(by_id: Dictionary, slots: int) -> Array[Actor]:
	var out: Array[Actor] = []
	for m in active_members(slots):
		if not by_id.has(str(m["id"])):
			continue
		var a := Actor.from_csv(by_id[str(m["id"])])
		a.name = str(m["name"])
		a.side = "ally"
		a.lp = int(m["lp"])
		a.loyalty = int(m["loyalty"])
		a.max_hp = int(a.max_hp * Formulas.COMPANION_HP_MULT)
		a.hp = a.max_hp
		out.append(a)
	return out

## หลังศึก — ล้ม = LP -1 · LP หมด = หายถาวร · ความเชื่อใจโตจากการสู้ด้วยกัน (GDD 3.6 / 5.4)
func after_battle(actors: Array) -> Array[String]:
	fought_since_rest = true
	var notes: Array[String] = []
	for a in actors:
		var m := _member(a.name)
		if m.is_empty():
			continue
		m["battles"] = int(m["battles"]) + 1
		m["clean_cd"] = maxi(0, int(m["clean_cd"]) - 1)
		var trust_up := 0
		if int(m["battles"]) % Formulas.TRUST_BATTLES == 0:
			trust_up += 1
		if a.down:
			m["lp"] = int(m["lp"]) - 1
			if int(m["lp"]) <= 0:
				notes.append("✂ %s หายไปถาวร…" % m["name"])
				lost.append(str(m["name"]))
				party.erase(m)
				continue
			notes.append("%s ล้ม — LP เหลือ %d%s" % [m["name"], m["lp"], " · บาดเจ็บสาหัส!" if int(m["lp"]) == 1 else ""])
		elif int(m["clean_cd"]) == 0:
			trust_up += 1
			m["clean_cd"] = Formulas.TRUST_CLEAN_COOLDOWN
		if trust_up > 0 and int(m["loyalty"]) < Formulas.TRUST_MAX:
			m["loyalty"] = mini(Formulas.TRUST_MAX, int(m["loyalty"]) + trust_up)
			notes.append("%s เชื่อใจมากขึ้น → %d" % [m["name"], m["loyalty"]])
	return notes

func _member(n: String) -> Dictionary:
	for m in party:
		if str(m["name"]) == n:
			return m
	return {}

# ── ไอเท็ม ────────────────────────────────────────────────────
func item_count(id: String) -> int:
	return int(items.get(id, 0))

func add_item(id: String, n: int = 1) -> void:
	items[id] = item_count(id) + n

## ใช้ไอเท็ม — คืนข้อความ ("" = ใช้ไม่ได้ ไม่เสียของ)
func use_item(row: Dictionary, target_name: String = "") -> String:
	var id := str(row["item_id"])
	if item_count(id) <= 0:
		return ""
	match str(row["kind"]):
		"heal_hp":
			if hp >= max_hp():
				return ""
			var before := hp
			hp = mini(max_hp(), hp + int(ceil(max_hp() * float(row["value"]))))
			items[id] = item_count(id) - 1
			return "%s — HP %d → %d" % [row["name"], before, hp]
		"restore_lp":
			var m := _member(target_name)
			if m.is_empty() or int(m["lp"]) >= Formulas.LP_MAX:
				return ""
			m["lp"] = int(m["lp"]) + int(row["value"])
			items[id] = item_count(id) - 1
			return "%s — %s LP %d" % [row["name"], m["name"], m["lp"]]
	return ""

func to_dict() -> Dictionary:
	var names: Array = []
	for n in learned:
		names.append(n)
	var op: Array = []
	for k in opened:
		op.append(k)
	var df: Array = []
	for k in defeated:
		df.append(k)
	return {
		"version": SAVE_VERSION,
		"prof": prof, "weapon_base": weapon_base, "weapon_name": weapon_name, "gold": gold,
		"opened": op, "defeated": df,
		"hp": hp, "sp": sp, "learned": names,
		"cell": [cell.x, cell.y], "rest_cell": [rest_cell.x, rest_cell.y],
		"ec": ec, "school": school, "steer": steer, "weapon_id": weapon_id,
		"weapons_owned": weapons_owned.duplicate(), "schools_held": schools_held.duplicate(),
		"party": party.duplicate(true), "party_seeded": party_seeded, "lost": lost.duplicate(),
		"met_species": met_species.duplicate(), "rest_count": rest_count,
		"fought_since_rest": fought_since_rest, "items": items.duplicate(), "shop_stock": shop_stock.duplicate(),
		"auto_battle": auto_battle, "materials": materials.duplicate(), "ground_drops": ground_drops.duplicate(true),
		"seized": seized.duplicate(true), "reads": reads.duplicate(true), "insight": insight,
		"falls": falls, "demo_end_seen": demo_end_seen,
	}

func from_dict(d: Dictionary) -> void:
	prof = int(d.get("prof", prof))
	weapon_base = int(d.get("weapon_base", weapon_base))
	gold = int(d.get("gold", gold))
	hp = int(d.get("hp", hp))
	sp = int(d.get("sp", sp))
	ec = int(d.get("ec", ec))
	school = str(d.get("school", school))
	steer = str(d.get("steer", steer))
	weapon_name = str(d.get("weapon_name", weapon_name))
	weapon_id = str(d.get("weapon_id", ""))   # เซฟเก่าไม่มี → sync_weapon หาจากชื่อ
	weapons_owned.clear()
	for w in d.get("weapons_owned", ["SL-1"]):   # เซฟเก่า: มีดทำครัวคือของเริ่มเกมเสมอ
		weapons_owned.append(str(w))
	schools_held.clear()
	for s in d.get("schools_held", [school]):
		schools_held.append(str(s))
	learned.clear()
	for n in d.get("learned", []):
		learned.append(str(n))
	opened.clear()
	for k in d.get("opened", []):
		opened.append(str(k))
	defeated.clear()
	for k in d.get("defeated", []):
		defeated.append(str(k))
	var c: Array = d.get("cell", [0, 0])
	cell = Vector2i(int(c[0]), int(c[1]))
	var rc: Array = d.get("rest_cell", [0, 0])
	rest_cell = Vector2i(int(rc[0]), int(rc[1]))
	party.clear()
	for m in d.get("party", []):
		var md: Dictionary = m
		party.append({"id": str(md.get("id", "")), "name": str(md.get("name", "")), "lp": int(md.get("lp", 0)),
			"loyalty": int(md.get("loyalty", 0)), "battles": int(md.get("battles", 0)), "clean_cd": int(md.get("clean_cd", 0)),
			"slots": int(md.get("slots", 1))})
	party_seeded = bool(d.get("party_seeded", false))
	lost.clear()
	for n in d.get("lost", []):
		lost.append(str(n))
	met_species.clear()
	for n in d.get("met_species", []):
		met_species.append(str(n))
	rest_count = int(d.get("rest_count", 0))
	fought_since_rest = bool(d.get("fought_since_rest", false))
	items.clear()
	var it: Dictionary = d.get("items", {})
	for k in it.keys():
		items[str(k)] = int(it[k])
	auto_battle = bool(d.get("auto_battle", true))
	materials.clear()
	var mt: Dictionary = d.get("materials", {})
	for k in mt:
		materials[str(k)] = int(mt[k])
	ground_drops.clear()
	var gd: Dictionary = d.get("ground_drops", {})
	for k in gd:
		var arr: Array = []
		for n in gd[k]:
			arr.append(str(n))
		ground_drops[str(k)] = arr
	seized.clear()
	for sz in d.get("seized", []):
		var sd: Dictionary = sz
		seized.append({"id": str(sd.get("id", "")), "name": str(sd.get("name", "")), "slots": int(sd.get("slots", 1))})
	insight = float(d.get("insight", 0.0))
	reads.clear()
	var rd: Dictionary = d.get("reads", {})
	for k in rd:
		var r: Dictionary = rd[k]
		reads[str(k)] = {"name": str(r.get("name", "")), "p": int(r.get("p", 0)),
			"need": maxi(1, int(r.get("need", 1))), "on": bool(r.get("on", false))}
	falls = int(d.get("falls", 0))
	demo_end_seen = bool(d.get("demo_end_seen", false))
	shop_stock.clear()
	var st: Dictionary = d.get("shop_stock", {})
	for k in st.keys():
		shop_stock[str(k)] = int(st[k])
