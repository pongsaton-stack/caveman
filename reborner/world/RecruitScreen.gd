# world/RecruitScreen.gd — ชนะแล้วเข้าใจท่าเด่นครบ → ถามว่าจะรับเข้าทีมไหม (GDD 5.2)
# ทางเลือก "ยึดท่า" ยังไม่ทำ · ทีมเต็มก็รับได้ ตัวที่เกินช่องไปสำรอง
class_name RecruitScreen
extends CanvasLayer

signal decided(accepted: bool)

var mon_name := ""
var tech_name := ""
var cost := 1
var full := false

func setup(monster_name: String, signature: String, slot_cost: int, team_full: bool) -> void:
	mon_name = monster_name
	tech_name = signature
	cost = slot_cost
	full = team_full

func _ready() -> void:
	layer = 11
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.55)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(dim)
	var panel := Panel.new()
	panel.add_theme_stylebox_override("panel", UiKit.box(UiKit.C_PANEL, UiKit.C_GOLD))
	panel.position = Vector2(62, 64)
	panel.size = Vector2(260, 80)
	root.add_child(panel)
	var head := UiKit.label("◇ เข้าใจท่า %s ของ%sแล้ว" % [tech_name, mon_name], 8, UiKit.C_GOLD)
	head.position = Vector2(70, 68)
	head.size = Vector2(244, 12)
	head.clip_text = true
	root.add_child(head)
	# กฎ UX ข้อ 5: กล่องละไม่เกิน 2 บรรทัด (หัว 1 + เนื้อ 1)
	var body := UiKit.label("รับเข้าทีมไหม? กิน %d ช่อง · %s" % [cost,
		"ทีมเต็ม → ไปสำรอง" if full else "ลงสนามศึกหน้าเลย"], 7, UiKit.C_TEXT)
	body.position = Vector2(70, 82)
	body.size = Vector2(244, 12)
	body.clip_text = true
	root.add_child(body)
	var yes := UiKit.button("รับเข้าทีม", 118)
	yes.position = Vector2(70, 116)
	yes.pressed.connect(_done.bind(true))
	root.add_child(yes)
	var no := UiKit.button("ไม่รับ", 118)
	no.position = Vector2(196, 116)
	no.pressed.connect(_done.bind(false))
	root.add_child(no)
	yes.grab_focus()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_done(false)

func _done(accepted: bool) -> void:
	decided.emit(accepted)
	queue_free()
