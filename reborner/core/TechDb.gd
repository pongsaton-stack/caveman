# core/TechDb.gd — คลังท่าทั้งหมด + ตรรกะต้นไม้ท่าและการประกาย
class_name TechDb
extends RefCounted

var all: Array[Tech] = []
var by_id: Dictionary = {}
var by_name: Dictionary = {}

func load_from(path: String) -> void:
	all.clear(); by_id.clear(); by_name.clear()
	for row in CsvDb.load_csv(path):
		var t := Tech.from_csv(row)
		all.append(t)
		by_id[t.id] = t
		by_name[t.name] = t

func get_tech(id_or_name: String) -> Tech:
	if by_id.has(id_or_name): return by_id[id_or_name]
	if by_name.has(id_or_name): return by_name[id_or_name]
	return null

## ท่ารากของสายนั้น — ตัวเอกเริ่มด้วยท่านี้ท่าเดียว
func root_of(school: String) -> Tech:
	for t in all:
		if t.school == school and t.parent == "":
			return t
	return null

func schools() -> Array:
	var s := []
	for t in all:
		if not s.has(t.school): s.append(t.school)
	return s

## ท่าที่ประกายได้ตอนนี้: พ่อแม่เรียนแล้ว + ความชำนาญถึง + ยังไม่เคยเรียน
func candidates(learned: Array, school: String, prof: int) -> Array[Tech]:
	var out: Array[Tech] = []
	for t in all:
		if t.school != school: continue
		if t.parent == "": continue
		if learned.has(t.name): continue
		if prof < t.req_prof: continue
		var p: Tech = get_tech(t.parent)
		if p == null or not learned.has(p.name): continue
		out.append(t)
	return out

## สุ่มท่าที่จะประกาย พร้อมถ่วงน้ำหนัก (GDD 4.3)
##   ท่าที่ใช้เป็นพ่อแม่โดยตรง x4 · อยู่กิ่งเดียวกัน x2 · อาวุธชี้ทางกิ่งนั้น x2
func roll_glimmer(learned: Array, school: String, prof: int,
		used_tech: Tech, steer_branch: String = "") -> Tech:
	var cand := candidates(learned, school, prof)
	if cand.is_empty(): return null
	var weights: Array[float] = []
	var total := 0.0
	for t in cand:
		var w := 1.0
		if used_tech != null:
			if t.parent == used_tech.name: w *= 4.0
			elif t.branch != "" and t.branch == used_tech.branch: w *= 2.0
		if steer_branch != "" and t.branch == steer_branch: w *= 2.0
		weights.append(w); total += w
	var r := randf() * total
	for i in cand.size():
		r -= weights[i]
		if r <= 0.0: return cand[i]
	return cand[cand.size() - 1]
