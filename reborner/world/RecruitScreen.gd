# world/RecruitScreen.gd — ชนะแล้วเข้าใจท่าเด่นครบ → เลือกทางเดียว (GDD 5.2)
#   ยึดท่า     = ได้ 1 ท่า เสียช่องความจำ (สลับได้ในเมนู)
#   รับเข้าทีม = ได้ทั้งตัว เสียช่องปาร์ตี้ · ทีมเต็มก็รับได้ ตัวที่เกินช่องไปสำรอง
# แสดงเฉพาะทางที่มอนตัวนั้นมี (กฎ 5.3: ท่ายึดได้ = seize_techs.csv · รับได้ = recruits.csv)
class_name RecruitScreen
extends CanvasLayer

signal decided(choice: String)   # "seize" · "recruit" · "" (ไม่เอา)

var mon_name := ""
var tech_name := ""
var cost := 1               # ช่องปาร์ตี้ (-1 = รับเข้าทีมไม่ได้)
var full := false
var seize_cost := 0         # ช่องความจำ (0 = ยึดไม่ได้)
var memory_left := 0        # ช่องความจำที่ยังว่าง

func setup(monster_name: String, signature: String, slot_cost: int, team_full: bool,
		seize_slots: int = 0, memory_free: int = 0) -> void:
	mon_name = monster_name
	tech_name = signature
	cost = slot_cost
	full = team_full
	seize_cost = seize_slots
	memory_left = memory_free

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
	panel.position = Vector2(52, 64)
	panel.size = Vector2(280, 80)
	root.add_child(panel)
	var head := UiKit.label("◇ เข้าใจท่า %s ของ%sแล้ว" % [tech_name, mon_name], 8, UiKit.C_GOLD)
	head.position = Vector2(60, 68)
	head.size = Vector2(264, 12)
	head.clip_text = true
	root.add_child(head)
	# กฎ UX ข้อ 5: กล่องละไม่เกิน 2 บรรทัด (หัว 1 + เนื้อ 1)
	var parts: Array[String] = []
	if seize_cost > 0:
		parts.append("ยึดท่า กินความจำ %d (ว่าง %d)" % [seize_cost, memory_left])
	if cost > 0:
		parts.append("รับเข้าทีม กิน %d ช่อง%s" % [cost, " · ทีมเต็ม→สำรอง" if full else ""])
	var body := UiKit.label("เลือกทางเดียว: " + " · ".join(parts), 7, UiKit.C_TEXT)
	body.position = Vector2(60, 82)
	body.size = Vector2(264, 12)
	body.clip_text = true
	root.add_child(body)
	var buttons: Array[Button] = []
	if seize_cost > 0:
		var sz := UiKit.button("ยึดท่า", 84)
		sz.disabled = seize_cost > memory_left
		sz.pressed.connect(_done.bind("seize"))
		buttons.append(sz)
	if cost > 0:
		var rc := UiKit.button("รับเข้าทีม", 84)
		rc.pressed.connect(_done.bind("recruit"))
		buttons.append(rc)
	var no := UiKit.button("ไม่เอา", 84)
	no.pressed.connect(_done.bind(""))
	buttons.append(no)
	var x := 60.0
	for b in buttons:
		b.position = Vector2(x, 116)
		root.add_child(b)
		x += 90.0
	for b in buttons:
		if not b.disabled:
			b.grab_focus()
			break

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_done("")

func _done(choice: String) -> void:
	decided.emit(choice)
	queue_free()
