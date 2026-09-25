# world/PlayerState.gd — สถานะตัวเอกที่อยู่ข้ามศึก (สิ่งที่ถูกเซฟ)
# Actor คือตัวละครในศึกเดียว · PlayerState คือตัวเอกตลอดการเดินทาง
class_name PlayerState
extends RefCounted

const SAVE_VERSION := 1

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
	a.name = "Riona"
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

func rest() -> void:
	hp = max_hp()
	sp = max_sp()
	rest_cell = cell

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
