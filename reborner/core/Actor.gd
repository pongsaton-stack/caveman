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
var comprehension: int = 3       # ความเข้าใจที่ต้องสะสมจากท่าเด่นนี้ (คอลัมน์ comprehension · GDD 5.2)
var loyalty: int = 0             # ความเชื่อใจ (มอนร่วมทีม) — rank 3 ยิงคอมโบได้
var hits: int = 0                # นับครั้งที่ถูกตี ใช้วัด 'ครั้งที่ต้องตี'
var sp: int = 0
var max_sp: int = 0
var luck: int = 0
var first_glimmer_pending: bool = false   # ผู้เล่นยังไม่เคยประกาย → Insight ครั้งแรกเต็มทันที (Insight.FIRST_GLIMMER_SURE) · ตั้งจาก PlayerState เท่านั้น Sim ไม่ใช้

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

# ── ผลพิเศษ (ท่าเด่นมีผลจริง · data/sig_effects.csv) ──
var base_def: int = 0            # DEF ก่อนบัฟ (ใช้คืนค่าตอนบัฟหมด)
var buffs: Dictionary = {}       # "def_up" -> เทิร์นที่เหลือ
var sig_effect: Dictionary = {}  # แถวจาก sig_effects.csv ของมอนตัวนี้ ({} = ท่าเด่นเป็นการตีแรงแบบเดิม)
var once_used: Array[String] = []   # ชื่อท่าแบบ "ครั้งเดียวต่อการต่อสู้" ที่ใช้ไปแล้ว
var seized: Array[String] = []   # ตัวเอก: ชื่อท่าที่ยึดมา (แยกจาก learned — ไม่นับในต้นไม้ท่า/โอกาสประกาย)

# ── อ่านทางหลบ (ตัวเอกเท่านั้น · kwan 6 ต.ค. 2026) ──
# โดนท่าเด่นมอน → โรลสูตรประกาย → ติด = เริ่มอ่านทางท่านั้น · โดนซ้ำ +1 (ตั้งรับ +2) จนครบความเข้าใจของมอน (comprehension)
# หลบได้ = แต้ม/ที่ต้องครบ (ครบ = 100%) · ใช้ได้เฉพาะอันที่ติดตั้ง · ติดตั้งพร้อมกันได้ read_slots อัน (= ช่องความจำท่า ÷ 2)
# อ่านใหม่ติดตั้งเองถ้ายังมีช่องว่าง · ครบ 100% แล้วถอด/ติดตั้งได้เหมือนท่าโจมตี (PlayerState.toggle_read)
var reads: Dictionary = {}       # monster_id → {"name": ชื่อท่าเด่น, "p": แต้มที่อ่านได้, "need": แต้มที่ต้องครบ, "on": ติดตั้งอยู่ไหม}
var read_slots: int = 0
var counter_used: bool = false   # ประกายสวนกลับได้ครั้งเดียวต่อการตั้งรับหนึ่งครั้ง

func reads_on() -> int:
	var n := 0
	for k in reads:
		if bool(reads[k].get("on", false)):
			n += 1
	return n

## โอกาสหลบท่าเด่นของมอนตัวนี้ (0 ถ้ายังไม่อ่าน หรืออ่านแล้วแต่ไม่ได้ติดตั้ง)
func dodge_chance(monster_id: String) -> float:
	if not reads.has(monster_id):
		return 0.0
	var r: Dictionary = reads[monster_id]
	if not bool(r.get("on", false)):
		return 0.0
	return clampf(float(r.get("p", 0)) / maxf(float(r.get("need", 1)), 1.0), 0.0, 1.0)

static var _sig_table := {}
static func sig_table() -> Dictionary:
	if _sig_table.is_empty() and FileAccess.file_exists("res://data/sig_effects.csv"):
		_sig_table = CsvDb.index_by(CsvDb.load_csv("res://data/sig_effects.csv"), "monster_id")
	return _sig_table

## บัฟ DEF ของตัวเอง (เกราะแข็ง) — ใช้ซ้ำระหว่างบัฟยังอยู่ = ต่ออายุ ไม่ซ้อน
func apply_def_up(value: float, turns: int) -> void:
	if base_def == 0: base_def = def_val
	buffs["def_up"] = turns
	def_val = int(round(float(base_def) * (1.0 + value)))

## ลดอายุบัฟตอนเริ่มเทิร์นของตัวเอง คืนชื่อที่หมด
func tick_buffs() -> Array:
	var expired := []
	for k in buffs.keys():
		buffs[k] -= 1
		if buffs[k] <= 0:
			buffs.erase(k)
			expired.append(k)
			if k == "def_up":
				def_val = base_def
	return expired

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
	a.comprehension = int(row_data.get("comprehension", 3))
	a.is_boss = int(row_data.get("is_boss", 0)) == 1
	a.basic_status = str(row_data.get("status", ""))
	a.basic_status_chance = float(row_data.get("status_chance", 0.0))
	a.sig_effect = sig_table().get(a.id, {})
	a.reset_av()
	return a
