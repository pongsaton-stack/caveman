# core/Actor.gd — ตัวละครหนึ่งตัวในสนามรบ ไม่มี node ไม่ผูกกับ UI
class_name Actor
extends RefCounted

var id: String
var name: String
var side: String          # "ally" หรือ "foe"
var tier: int
var hp: int
var max_hp: int
var atk: int
var def_val: int
var spd: int
var lp: int = 0           # ตัวเอกไม่มี LP (GDD 3.6)
var is_hero: bool = false
var is_boss: bool = false       # จากคอลัมน์ is_boss — บอสคือโรงงานประกายไม่ว่า tier เท่าไหร่
var row: String = "หน้า"
var weak: Array = []
var resist: Array = []
var immune: Array = []
var av: float = 0.0
var insight: float = 0.0
var insight_lock: int = 0        # รอบที่เหลือก่อนสะสม Insight ได้อีก
var down: bool = false
var telegraph: Dictionary = {}   # {name, dmg} — ท่าที่เปิดไว้ในคิว
var signature: String = ""      # ชื่อท่าเด่นของมอน (ใช้ตอนเปิดท่า)
var loyalty: int = 0             # ความเชื่อใจ (มอนร่วมทีม) — rank 3 ยิงคอมโบได้
var hits: int = 0                # นับครั้งที่ถูกตี ใช้วัด 'ครั้งที่ต้องตี'
var sp: int = 0
var max_sp: int = 0
var luck: int = 0

# ── ต้นไม้ท่า (ตัวเอกเท่านั้น) ──
var learned: Array[String] = []  # ชื่อท่าที่เรียนแล้ว
var school: String = "คม"        # สายอาวุธที่ถืออยู่
var steer_branch: String = ""    # กิ่งที่อาวุธชี้ทาง (ถ่วงน้ำหนักประกาย x2)
var basic_element: String = "ทุบ"

# ── สถานะ (GDD 3.11) ──
var statuses: Dictionary = {}    # ชื่อสถานะ -> เทิร์นที่เหลือ
var last_hit: int = 0            # ดาเมจที่รับล่าสุด ใช้กับ เลือดไหล
var guarding: bool = false       # ตั้งรับอยู่ไหม
var windup: bool = false         # ท่าถัดไปน้ำหนักครึ่งเดียว (จากการตั้งรับ)
var basic_status: String = ""    # สถานะที่การโจมตีปกติของตัวนี้ลง
var basic_status_chance: float = 0.0

func has_status(key: String) -> bool:
	return statuses.has(key)

func add_status(key: String) -> void:
	statuses[key] = Status.DURATION

## ลดอายุสถานะทุกตัวลง n เทิร์น คืนชื่อที่หมดอายุ
func tick_statuses(n: int = 1) -> Array:
	var expired := []
	for k in statuses.keys():
		statuses[k] -= n
		if statuses[k] <= 0:
			statuses.erase(k)
			expired.append(k)
	return expired

func clear_statuses() -> int:
	var n := statuses.size()
	statuses.clear()
	return n

func elem_mult(element: String) -> float:
	if element in immune: return 0.0
	if element in weak:   return Formulas.WEAK_MULT
	if element in resist: return Formulas.RESIST_MULT
	return 1.0

func reset_av() -> void:
	av = Formulas.av(spd)

static func from_csv(row_data: Dictionary) -> Actor:
	var a := Actor.new()
	a.id = str(row_data.get("monster_id", ""))
	a.name = str(row_data.get("name_th", ""))
	a.side = "foe"
	a.tier = int(row_data.get("tier", 1))
	a.max_hp = int(row_data.get("hp", 10))
	a.hp = a.max_hp
	a.atk = int(row_data.get("atk", 10))
	a.def_val = int(row_data.get("def", 10))
	a.spd = int(row_data.get("spd", 100))
	a.row = str(row_data.get("grid_pos", "หน้า"))
	a.weak = str(row_data.get("weak", "")).split(",", false)
	a.resist = str(row_data.get("resist", "")).split(",", false)
	a.immune = str(row_data.get("immune", "")).split(",", false)
	a.sp = 30; a.max_sp = 30
	a.basic_element = "ทุบ"
	a.signature = str(row_data.get("signature_tech", "ท่าเด่น"))
	a.is_boss = int(row_data.get("is_boss", 0)) == 1
	a.basic_status = str(row_data.get("status", ""))
	a.basic_status_chance = float(row_data.get("status_chance", 0.0))
	a.reset_av()
	return a
