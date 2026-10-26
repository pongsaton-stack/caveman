# world/MapData.gd — อ่านแผนที่จากไฟล์ข้อความ ไม่มี node ทดสอบได้เดี่ยวๆ
# แผนที่เป็นข้อมูล ไม่ใช่โค้ด — แก้ data/map_ashfield.txt แล้วเกมเปลี่ยนตาม
class_name MapData
extends RefCounted

const TERRAIN := "#~.,RS"  # ตัวอักษรที่เป็นพื้นที่ นอกจากนี้คือจุดเกิดศัตรู (S = ร้านค้า)
const BLOCKED := "#~"      # เดินผ่านไม่ได้

var rows: Array[String] = []
var w := 0
var h := 0
var start := Vector2i.ZERO
var spawns: Array[Dictionary] = []   # [{cell, sym}]

static func load_map(path: String) -> MapData:
	if not FileAccess.file_exists(path):
		push_error("ไม่พบแผนที่: %s" % path)
		return null
	var text := FileAccess.get_file_as_string(path)
	var m := MapData.new()
	for line in text.split("\n", false):
		# ตัด \r ท้ายบรรทัด (ไฟล์ที่แก้บน Windows)
		var clean := line.strip_edges(false, true)
		if clean == "" or clean.begins_with(";"):
			continue
		m.rows.append(clean)
	m.h = m.rows.size()
	for r in m.rows:
		m.w = maxi(m.w, r.length())
	for y in m.h:
		var r: String = m.rows[y]
		for x in r.length():
			var ch := r[x]
			if ch == "H":
				m.start = Vector2i(x, y)
			elif not TERRAIN.contains(ch):
				m.spawns.append({"cell": Vector2i(x, y), "sym": ch})
	return m

func tile(c: Vector2i) -> String:
	if c.x < 0 or c.y < 0 or c.y >= h or c.x >= rows[c.y].length():
		return "#"
	var ch := rows[c.y][c.x]
	return ch if TERRAIN.contains(ch) else "."

func walkable(c: Vector2i) -> bool:
	return not BLOCKED.contains(tile(c))
