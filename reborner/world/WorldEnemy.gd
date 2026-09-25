# world/WorldEnemy.gd — ศัตรูที่มองเห็นบนแมพ (GDD: ไม่มี random encounter)
class_name WorldEnemy
extends Node2D

var cell := Vector2i.ZERO
var home := Vector2i.ZERO       # เดินห่างจากจุดเกิดได้ไม่เกิน LEASH ช่อง
var facing := Vector2i.DOWN     # ทิศที่หัน — เข้าหาจากด้านหลัง = ลอบตี
var group: Array[String] = []   # รหัสมอนในกลุ่ม เช่น ["M15", "M15"]
var label_text := ""
var tier := 1
var is_boss := false
var body_color := Color("b5705a")
var _label: Label

const LEASH := 4

func _ready() -> void:
	z_index = 1
	_label = Label.new()
	_label.text = "%s t%d" % [label_text, tier]
	_label.add_theme_font_size_override("font_size", 6)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_label.add_theme_constant_override("outline_size", 2)
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.size = Vector2(80, 10)
	_label.position = Vector2(-40, -24)
	add_child(_label)

## สีบอกความอันตรายเทียบกับตัวเอก — ผู้เล่นต้องเห็นก่อนเดินเข้าไป
##   เทา = ตบทิ้งได้ · เขียว = ง่าย · เหลือง = สูสี · แดง = อันตราย
func set_danger(prof: int) -> void:
	if Formulas.is_swat(tier, prof) and not is_boss:
		body_color = Color("7a7a7a")
	elif tier < prof:
		body_color = Color("5fa88a")
	elif tier <= prof + 5:
		body_color = Color("d9b84a")
	else:
		body_color = Color("d25a5a")
	queue_redraw()

func within_leash(c: Vector2i) -> bool:
	return absi(c.x - home.x) + absi(c.y - home.y) <= LEASH

func _draw() -> void:
	var s := 10.0 if is_boss else 8.0
	draw_rect(Rect2(-s, -s, s * 2.0, s * 2.0), body_color)
	draw_rect(Rect2(-s, -s, s * 2.0, s * 2.0), Color.BLACK, false, 1.0)
	# จุดขาวบอกทิศที่หัน — เดินเข้าหาจากฝั่งตรงข้ามจุดนี้ = ลอบตี
	var f := Vector2(facing) * (s - 2.0)
	draw_rect(Rect2(f.x - 2.0, f.y - 2.0, 4.0, 4.0), Color.WHITE)
