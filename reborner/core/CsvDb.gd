# core/CsvDb.gd — โหลด CSV เป็นข้อมูลเกม (แหล่งความจริงเดียว ห้าม hardcode ค่าใดๆ)
class_name CsvDb
extends RefCounted

## โหลดไฟล์ CSV เป็น Array ของ Dictionary โดยใช้แถวแรกเป็นชื่อคอลัมน์
static func load_csv(path: String) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("เปิดไฟล์ไม่ได้: %s" % path)
		return rows
	var headers := f.get_csv_line()
	while not f.eof_reached():
		var line := f.get_csv_line()
		if line.size() < 2:
			continue
		var row := {}
		for i in headers.size():
			var key := headers[i].strip_edges()
			var val := line[i].strip_edges() if i < line.size() else ""
			row[key] = _cast(val)
		rows.append(row)
	f.close()
	return rows

## แปลงข้อความเป็นตัวเลขถ้าทำได้ ไม่งั้นคืนเป็น String
static func _cast(v: String):
	if v == "":
		return ""
	if v.is_valid_int():
		return v.to_int()
	if v.is_valid_float():
		return v.to_float()
	return v

## ทำ index จากคอลัมน์ใดคอลัมน์หนึ่ง เช่น by("monster_id")
static func index_by(rows: Array[Dictionary], key: String) -> Dictionary:
	var d := {}
	for r in rows:
		d[r.get(key)] = r
	return d
