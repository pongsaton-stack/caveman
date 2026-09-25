# core/Tech.gd — ท่าหนึ่งท่าจากต้นไม้ท่า โหลดจาก techs.csv ไม่มีค่า hardcode
class_name Tech
extends RefCounted

var id: String
var name: String
var school: String        # คม ทุบ แทง ยิง กล มือเปล่า
var branch: String        # กิ่งในต้นไม้ ใช้ถ่วงน้ำหนักตอนประกาย
var parent: String        # ท่าที่ต้องเรียนก่อน ("" = ราก)
var req_prof: int
var power: float
var weight: float         # ActionWeight
var sp: int
var element: String
var scope: String         # single / row / column / all / self
var hits: int = 1
var ignore_def: float = 0.0
var self_av_mult: float = 1.0
var target_av_mult: float = 1.0
var ignore_pos: bool = false
var free_row: bool = false
var note: String
var status: String = ""          # สถานะที่ท่านี้ลง
var status_chance: float = 0.0   # โอกาสฐาน ก่อนหัก DEF

static func from_csv(d: Dictionary) -> Tech:
	var t := Tech.new()
	t.id = str(d.get("tech_id", ""))
	t.name = str(d.get("name_th", ""))
	t.school = str(d.get("school", ""))
	t.branch = str(d.get("branch", ""))
	t.parent = str(d.get("parent", ""))
	t.req_prof = int(d.get("req_prof", 0))
	t.power = float(d.get("power", 0))
	t.weight = float(d.get("weight", 1.0))
	t.sp = int(d.get("sp", 0))
	t.element = str(d.get("element", ""))
	t.scope = str(d.get("scope", "single"))
	t.hits = maxi(1, int(d.get("hits", 1)))
	t.ignore_def = float(d.get("ignore_def", 0.0))
	t.self_av_mult = float(d.get("self_av_mult", 1.0))
	t.target_av_mult = float(d.get("target_av_mult", 1.0))
	t.ignore_pos = int(d.get("ignore_pos", 0)) == 1
	t.free_row = int(d.get("free_row", 0)) == 1
	t.note = str(d.get("note", ""))
	t.status = str(d.get("status", ""))
	t.status_chance = float(d.get("status_chance", 0.0))
	return t

func is_attack() -> bool:
	return power > 0.0
