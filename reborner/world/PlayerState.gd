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
var school := "คม"
var steer := "เขี้ยว"
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

func init_new(techs: TechDb, start: Vector2i) -> void:
	learned.clear()
	var root := techs.root_of(school)
	if root != null:
		learned.append(root.name)
	cell = start
	rest_cell = start
	hp = max_hp()
	sp = max_sp()

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
	return a

## รับผลจากศึกกลับมา — ท่าที่ประกาย · ความชำนาญโบนัสจาก Insight · HP/SP ที่เหลือ
func absorb(a: Actor) -> void:
	prof = a.tier
	hp = a.hp
	sp = a.sp
	learned.clear()
	for n in a.learned:
		learned.append(n)

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
			"loyalty": int(r["loyalty"]), "battles": 0, "clean_cd": 0})
		if not met_species.has(str(r["monster_id"])):
			met_species.append(str(r["monster_id"]))

## จำนวนช่องมอนตาม EC จาก data/party_slots.csv (GDD 5.5 ฉบับวัดแล้ว)
static func monster_slots_for(ec_now: int, rows: Array) -> int:
	var n := 0
	for r in rows:
		if ec_now >= int(r["ec"]):
			n = maxi(n, int(r["monster_slots"]))
	return n

## มอนที่ลงสนาม — ตามลำดับในทีม ไม่เกินจำนวนช่อง
func make_companions(by_id: Dictionary, slots: int) -> Array[Actor]:
	var out: Array[Actor] = []
	for m in party:
		if out.size() >= slots:
			break
		if int(m["lp"]) <= 0 or not by_id.has(str(m["id"])):
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
		"ec": ec, "school": school, "steer": steer,
		"party": party.duplicate(true), "party_seeded": party_seeded, "lost": lost.duplicate(),
		"met_species": met_species.duplicate(), "rest_count": rest_count,
		"fought_since_rest": fought_since_rest, "items": items.duplicate(), "shop_stock": shop_stock.duplicate(),
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
			"loyalty": int(md.get("loyalty", 0)), "battles": int(md.get("battles", 0)), "clean_cd": int(md.get("clean_cd", 0))})
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
	shop_stock.clear()
	var st: Dictionary = d.get("shop_stock", {})
	for k in st.keys():
		shop_stock[str(k)] = int(st[k])
