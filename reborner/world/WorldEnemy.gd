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
var needs_allies := 0           # พวกขั้นต่ำก่อนมันตื่น (encounters.csv · Rion คนเดียวชนะ 0% · GDD 11.30 · kwan 30 ต.ค.)
var asleep := false             # หลับ = ไม่ไล่ · เดินชนไม่เข้าศึก
var body_color := Color("b5705a")
var _label: Label
# รูปสไตล์ Last Light (kwan อนุมัติแล้ว) · ไม่มีรูป = กล่องสีแบบเดิม
var frames: Array[Texture2D] = []   # ลำดับภาพหายใจ หันขวา (เดินทีละ IDLE_SEC/2 · ชุดเดิม 2 ภาพ = [ยืน, ยืน, idle, idle] จังหวะเท่าเดิม)
var _frame := 0
var _clock := 0.0
var _face_left := false

const LEASH := 4
const SPRITE_DIR := "res://assets/sprites/monsters_ll"
const PX_DIR := "res://assets/sprites/monsters_px"   # มอนพิกเซลชุดใหม่ (kwan 16 ต.ค. 2026) · <id>_idle<n>.png มีก่อนใช้ก่อน
const IDLE_SEC := 0.45
const FEET_Y := 11.0                 # เท้าแตะขอบล่างช่อง (ช่อง 24px · ศูนย์กลาง node = กลางช่อง)
const RING_RX := 18.0                # วงสีความอันตรายต้องกว้างกว่าตัวมอน (สไลม์ 48px บังวงเล็กมิด)
const RING_RY := 5.0

## โหลดรูปของมอนตัวแรกในกลุ่ม ถ้ามี
func load_sprite() -> void:
	frames.clear()
	if group.is_empty():
		return
	var n := 0
	while ResourceLoader.exists("%s/%s_idle%d.png" % [PX_DIR, group[0], n]):
		frames.append(load("%s/%s_idle%d.png" % [PX_DIR, group[0], n]))
		n += 1
	if n > 0:
		for k in range(n - 2, 0, -1):   # ไป-กลับ 0 1 2 1
			frames.append(frames[k])
		return
	for suffix in ["", "_idle1"]:
		var path := "%s/%s%s.png" % [SPRITE_DIR, group[0], suffix]
		if ResourceLoader.exists(path):
			frames.append(load(path))
			frames.append(load(path))

func _ready() -> void:
	z_index = 1
	_label = Label.new()
	_label.text = "%s t%d" % [label_text, tier]
	_label.add_theme_font_size_override("font_size", 6)
	_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_label.add_theme_constant_override("outline_size", 2)
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.size = Vector2(80, 10)
	# ป้ายชื่ออยู่เหนือหัวรูปจริง (บอส 96px สูงกว่ามอนทั่วไปเท่าตัว)
	# วางเหนือส่วนที่มีภาพจริง (ผืนชุดพิกเซลเผื่อที่ว่างเหนือหัวไว้ให้ท่ากระโดด → ใช้ขนาดผืนตรง ๆ ป้ายจะลอยสูงเกิน)
	var top := 0
	if not frames.is_empty():
		top = frames[0].get_image().get_used_rect().position.y
	_label.position = Vector2(-40, FEET_Y - frames[0].get_size().y + top - 10.0 if not frames.is_empty() else -24.0)
	add_child(_label)

func _process(delta: float) -> void:
	if frames.size() < 2:
		return
	_clock += delta
	if _clock >= IDLE_SEC / 2.0:
		_clock = 0.0
		_frame = (_frame + 1) % frames.size()
		queue_redraw()

## รูปหันขวา → หันซ้ายเมื่อเดินซ้าย · ขึ้น/ลง คงทางเดิม
func set_facing(dir: Vector2i) -> void:
	facing = dir
	if dir.x != 0:
		_face_left = dir.x < 0
	queue_redraw()

## สีบอกความอันตรายเทียบกับตัวเอก — ผู้เล่นต้องเห็นก่อนเดินเข้าไป
##   เทา = ตบทิ้งได้ · เขียว = ง่าย · เหลือง = สูสี · แดง = อันตราย
func set_danger(prof: int) -> void:
	if Formulas.map_swat(tier, prof) and not is_boss:
		body_color = Color("7a7a7a")
	elif tier < prof:
		body_color = Color("5fa88a")
	elif tier <= prof + 5:
		body_color = Color("d9b84a")
	else:
		body_color = Color("d25a5a")
	queue_redraw()

func set_asleep(v: bool) -> void:
	asleep = v
	modulate = Color(0.75, 0.75, 0.85, 0.8) if v else Color.WHITE
	queue_redraw()

func within_leash(c: Vector2i) -> bool:
	return absi(c.x - home.x) + absi(c.y - home.y) <= LEASH

func _draw() -> void:
	if not frames.is_empty():
		_draw_sprite()
		return
	var s := 10.0 if is_boss else 8.0
	draw_rect(Rect2(-s, -s, s * 2.0, s * 2.0), body_color)
	draw_rect(Rect2(-s, -s, s * 2.0, s * 2.0), Color.BLACK, false, 1.0)
	# จุดขาวบอกทิศที่หัน — เดินเข้าหาจากฝั่งตรงข้ามจุดนี้ = ลอบตี
	if asleep:
		_draw_zz(Vector2(s - 2.0, -s - 4.0))
	var f := Vector2(facing) * (s - 2.0)
	draw_rect(Rect2(f.x - 2.0, f.y - 2.0, 4.0, 4.0), Color.WHITE)

## วงเงาใต้เท้า = สีความอันตราย · ลูกศรเล็กชี้ทิศที่หัน (เข้าจากฝั่งตรงข้าม = ลอบตี) · รูปมอนยืนบนวง
func _draw_sprite() -> void:
	var tex: Texture2D = frames[mini(_frame, frames.size() - 1)]
	var sz := tex.get_size()
	var k := sz.x / 48.0                 # วงกว้างตามขนาดรูป (บอส 96px = 2 เท่า)
	var ring := PackedVector2Array()
	for i in 20:
		var a := TAU * i / 20.0
		ring.append(Vector2(cos(a) * RING_RX * k, FEET_Y + 1.0 + sin(a) * RING_RY * k))
	draw_colored_polygon(ring, Color(body_color, 0.85))
	ring.append(ring[0])
	draw_polyline(ring, Color.BLACK, 1.0)
	var tip := Vector2(facing) * Vector2(RING_RX * k + 7.0, RING_RY * k + 7.0) + Vector2(0, FEET_Y + 1.0)
	var side := Vector2(-facing.y, facing.x) * 3.0
	var back := tip - Vector2(facing) * 4.0
	draw_colored_polygon(PackedVector2Array([tip, back + side, back - side]), Color.WHITE)
	draw_polyline(PackedVector2Array([tip, back + side, back - side, tip]), Color.BLACK, 1.0)
	var rect := Rect2(Vector2(-sz.x / 2.0, FEET_Y - sz.y), sz)
	if _face_left:
		rect.size.x = -rect.size.x   # ขนาดติดลบ = พลิกซ้าย-ขวาในกรอบเดิม (ไม่ต้องเลื่อนตำแหน่ง)
	draw_texture_rect(tex, rect, false)
	if asleep:
		_draw_zz(Vector2(sz.x * 0.3, FEET_Y - sz.y * 0.8))

## Zz ลอยเหนือหัว (วาดเป็นพิกเซล ไม่พึ่งฟอนต์)
func _draw_zz(at: Vector2) -> void:
	for i in 2:
		var o := at + Vector2(i * 6.0, -i * 6.0)
		var w := 5.0 - i
		var pts := PackedVector2Array([o, o + Vector2(w, 0), o + Vector2(0, w), o + Vector2(w, w)])
		draw_polyline(pts, Color.BLACK, 2.0)
		draw_polyline(pts, Color.WHITE, 1.0)
