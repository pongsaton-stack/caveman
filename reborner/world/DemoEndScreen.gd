# world/DemoEndScreen.gd — จบเดโม (ภูมิภาค 1) หลังชนะบอสครั้งแรก (kwan เลือก 4 ต.ค. 2026)
#   ขั้น 1: จอดำ + บทพูดทีละบรรทัด (data/dialogue.csv · STORY_DRAFT ฉากที่ 7)
#   ขั้น 2: การ์ดสรุปการเดินทาง + ปุ่ม เดินเล่นต่อ / เริ่มเกมใหม่
class_name DemoEndScreen
extends CanvasLayer

signal decided(choice: String)   # "continue" · "new_game"

const LINE_SECS := 1.8   # เวลาต่อบทพูดหนึ่งบรรทัด (กด ตกลง เพื่อข้ามได้)

var lines: Array[String] = []
var summary: Array[String] = []
var line_secs := LINE_SECS        # เทสต์ตั้ง 0 ได้
var _root: Control
var _say: Label
var _step := 0
var _clock := 0.0
var _phase := "lines"

func setup(dialogue: Array[String], rows: Array[String]) -> void:
	lines = dialogue
	summary = rows

func _ready() -> void:
	layer = 12
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_root)
	var bg := ColorRect.new()
	bg.color = Color.BLACK
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(bg)
	_say = UiKit.label("", 10, UiKit.C_TEXT)
	_say.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_say.position = Vector2(0, 100)
	_say.size = Vector2(384, 16)
	_root.add_child(_say)
	_next_line()

func _process(delta: float) -> void:
	if _phase != "lines":
		return
	_clock += delta
	if _clock >= line_secs:
		_next_line()

func _next_line() -> void:
	_clock = 0.0
	if _step >= lines.size():
		_show_summary()
		return
	_say.text = lines[_step]
	_say.modulate.a = 0.0
	create_tween().tween_property(_say, "modulate:a", 1.0, 0.4)
	_step += 1

func _show_summary() -> void:
	_phase = "summary"
	_say.queue_free()
	# ความสูงกล่องตามจำนวนบรรทัดสรุป ให้อยู่กลางจอ 384x216
	var h := 20.0 + 12.0 * summary.size() + 36.0
	var top := (216.0 - h) / 2.0
	var panel := Panel.new()
	panel.add_theme_stylebox_override("panel", UiKit.box(UiKit.C_PANEL, UiKit.C_GOLD))
	panel.position = Vector2(42, top)
	panel.size = Vector2(300, h)
	_root.add_child(panel)
	var head := UiKit.label("จบเดโม — ภูมิภาค 1 ทุ่งเถ้า", 10, UiKit.C_GOLD)
	head.position = Vector2(50, top + 4)
	_root.add_child(head)
	var y := top + 22.0
	for r in summary:
		var l := UiKit.label(r, 7, UiKit.C_TEXT)
		l.position = Vector2(50, y)
		l.size = Vector2(284, 11)
		l.clip_text = true
		_root.add_child(l)
		y += 12.0
	var note := UiKit.label("ภูมิภาคถัดไปยังไม่เปิด — เดินเล่นต่อได้ เซฟยังอยู่", 7, UiKit.C_MUTED)
	note.position = Vector2(50, y + 2)
	_root.add_child(note)
	var cont := UiKit.button("เดินเล่นต่อ", 110)
	cont.position = Vector2(66, y + 16)
	cont.pressed.connect(_done.bind("continue"))
	_root.add_child(cont)
	var fresh := UiKit.button("เริ่มเกมใหม่", 110)
	fresh.position = Vector2(206, y + 16)
	fresh.pressed.connect(_done.bind("new_game"))
	_root.add_child(fresh)
	cont.grab_focus()

func _unhandled_input(event: InputEvent) -> void:
	if _phase == "lines" and event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		_next_line()

func _done(choice: String) -> void:
	decided.emit(choice)
	queue_free()
