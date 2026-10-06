# world/MenuScreen.gd — เมนูบนแผนที่: สถานะตัวเอก · มอนร่วมทีม (LP/ความเชื่อใจ) · ใช้ไอเท็ม
# เปิดด้วย Esc บนแผนที่ (มือถือ: ปุ่ม "กลับ") · ปิดด้วย Esc หรือปุ่ม "ปิด"
class_name MenuScreen
extends CanvasLayer

signal closed
signal practice(school: String)     # ห้องทดลองท่า — Overworld เปิดศึกทดลองสายที่เลือก (ไม่บันทึกผล)

var ps: PlayerState
var techs: TechDb
var items_rows: Array = []
var slots := 0

var _root: Control
var _body: Control
var _menu: GridContainer
var _info: Label
var _picking_lp := false

func setup(state: PlayerState, tech_db: TechDb, item_rows: Array, monster_slots: int) -> void:
	ps = state
	techs = tech_db
	items_rows = item_rows
	slots = monster_slots

func _ready() -> void:
	layer = 10
	_root = UiKit.screen(self, "เมนู")
	_info = UiKit.label("", 7, UiKit.C_GOLD)
	_info.position = Vector2(4, 148)
	_info.size = Vector2(376, 10)
	_info.clip_text = true
	_root.add_child(_info)
	_menu = GridContainer.new()
	_menu.columns = 3
	_menu.position = Vector2(4, 160)
	_menu.add_theme_constant_override("h_separation", 3)
	_menu.add_theme_constant_override("v_separation", 2)
	_root.add_child(_menu)
	_render()
	_show_actions()

func _render() -> void:
	if _body != null:
		_body.queue_free()
	_body = Control.new()
	_root.add_child(_body)

	# ── ซ้าย: Rion ──
	var left := VBoxContainer.new()
	left.position = Vector2(4, 14)
	left.size = Vector2(186, 130)
	left.add_theme_constant_override("separation", 0)
	_body.add_child(left)
	left.add_child(UiKit.label("Rion · ความชำนาญ %d" % ps.prof, 8, UiKit.C_TEXT))
	left.add_child(UiKit.label("%s (ค่าอาวุธ %d)" % [ps.weapon_name, ps.weapon_base], 7, UiKit.C_MUTED))
	left.add_child(UiKit.label("HP %d/%d · SP %d/%d · เงิน %d" % [ps.hp, ps.max_hp(), ps.sp, ps.max_sp(), ps.gold], 7, UiKit.C_TEXT))
	var used := 0
	for m in ps.active_members(slots):
		used += PlayerState.slot_cost(m)
	left.add_child(UiKit.label("EC %d · ช่องมอน %d/%d" % [ps.ec, used, slots], 7, UiKit.C_MUTED))
	left.add_child(UiKit.label("ท่าที่เรียนแล้ว %d" % ps.learned.size(), 7, UiKit.C_GOLD))
	var tech_text := UiKit.label(" · ".join(ps.learned), 7, UiKit.C_TEXT)
	tech_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tech_text.custom_minimum_size = Vector2(186, 0)
	left.add_child(tech_text)
	if not ps.seized.is_empty():
		var sz: Array = []
		for st in ps.seized:
			sz.append(str(st["name"]))
		var seized_text := UiKit.label("ท่าที่ยึด (ความจำ %d/%d): %s" % [ps.used_memory(), ps.memory_slots(), " · ".join(sz)], 7, UiKit.C_GOLD)
		seized_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		seized_text.custom_minimum_size = Vector2(186, 0)
		left.add_child(seized_text)
	if not ps.reads.is_empty():
		var rd: Array = []
		for k in ps.reads:
			rd.append(_read_label(ps.reads[k]))
		var reads_text := UiKit.label("ท่าหลบ (ติดตั้ง %d/%d): %s" % [ps.reads_on(), ps.read_slots(), " · ".join(rd)], 7, UiKit.C_GOLD)
		reads_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		reads_text.custom_minimum_size = Vector2(186, 0)
		left.add_child(reads_text)
	if not ps.materials.is_empty():
		var mats: Array = []
		for k in ps.materials.keys():
			mats.append("%s x%d" % [k, ps.materials[k]])
		var mt := UiKit.label("วัสดุ: " + " · ".join(mats), 6, UiKit.C_MUTED)
		mt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		mt.custom_minimum_size = Vector2(186, 0)
		left.add_child(mt)

	# ── ขวา: มอนร่วมทีม ──
	var right := VBoxContainer.new()
	right.position = Vector2(196, 14)
	right.size = Vector2(184, 130)
	right.add_theme_constant_override("separation", 1)
	_body.add_child(right)
	right.add_child(UiKit.label("มอนร่วมทีม", 8, UiKit.C_TEXT))
	if ps.party.is_empty():
		right.add_child(UiKit.label("— ไม่มี —", 7, UiKit.C_MUTED))
	var active := ps.active_members(slots)
	for i in ps.party.size():
		var m: Dictionary = ps.party[i]
		var lp := int(m["lp"])
		var bench := "  (สำรอง)" if not active.has(m) else ""
		if PlayerState.slot_cost(m) > 1:
			bench += "  [%d ช่อง]" % PlayerState.slot_cost(m)
		var col := UiKit.C_BAD if lp == 1 else UiKit.C_TEXT
		right.add_child(UiKit.label("%s  LP %s%s" % [m["name"], UiKit.lp_dots(lp), bench], 7, col))
		var sub := "เชื่อใจ %d/%d · สู้ด้วยกัน %d ศึก" % [m["loyalty"], Formulas.TRUST_MAX, m["battles"]]
		if lp == 1:
			sub += " · บาดเจ็บสาหัส!"
		right.add_child(UiKit.label(sub, 6, UiKit.C_BAD if lp == 1 else UiKit.C_MUTED))
	if not ps.lost.is_empty():
		right.add_child(UiKit.label("หายถาวร: " + ", ".join(ps.lost), 6, UiKit.C_BAD))
	var regen_left := Formulas.LP_REGEN_RESTS - ps.rest_count
	right.add_child(UiKit.label("LP ฟื้นอีก %d จุดพัก (ต้องสู้ก่อนพักถึงนับ)" % regen_left, 6, UiKit.C_MUTED))

func _clear_menu() -> void:
	for c in _menu.get_children():
		_menu.remove_child(c)
		c.queue_free()

func _add(btn: Button) -> Button:
	_menu.add_child(btn)
	return btn

func _show_actions() -> void:
	_clear_menu()
	_picking_lp = false
	var first: Button = null
	for r in items_rows:
		var id := str(r["item_id"])
		var n := ps.item_count(id)
		var btn := _add(UiKit.button("ใช้ %s x%d" % [r["name"], n], 123))
		btn.disabled = n <= 0
		btn.pressed.connect(_on_item.bind(r))
		btn.focus_entered.connect(func(): _info.text = str(r["note"]).split("·")[0].strip_edges())
		if first == null and not btn.disabled:
			first = btn
	if ps.party.size() > 1:
		var arrange := _add(UiKit.button("จัดทีม", 123))
		arrange.pressed.connect(_pick_front)
		arrange.focus_entered.connect(func(): _info.text = "เลือกมอนขึ้นหัวทีม — ตัวหัวทีมได้ลงสนามก่อน ที่เกินช่องไปสำรอง")
	if not ps.seized.is_empty():
		var mem := _add(UiKit.button("ท่าที่ยึด %d/%d" % [ps.used_memory(), ps.memory_slots()], 123))
		mem.pressed.connect(_pick_forget)
		mem.focus_entered.connect(func(): _info.text = "ท่าที่ยึดจากมอน กินช่องความจำ · ลืมท่าเพื่อคืนช่อง (ยึดใหม่ต้องเข้าใจท่าอีกรอบ)")
	if not ps.reads.is_empty():
		var rb := _add(UiKit.button("ท่าหลบ %d/%d" % [ps.reads_on(), ps.read_slots()], 123))
		rb.pressed.connect(_pick_read)
		rb.focus_entered.connect(func(): _info.text = "อ่านทางท่าเด่นมอน หลบได้ตาม % · ครบ 100% แล้วถอด/ติดตั้งได้ · ติดตั้งพร้อมกัน = ช่องความจำ ÷ 2")
	var lab := _add(UiKit.button("ทดลองท่า", 123))
	lab.pressed.connect(_pick_practice_school)
	lab.focus_entered.connect(func(): _info.text = "ศึกทดลอง: Rion ใช้ได้ทุกท่าในสาย รวมไม้ตาย · ผลไม่บันทึก")
	var close := _add(UiKit.button("ปิด", 123))
	close.pressed.connect(_close)
	if first == null:
		first = close
	first.grab_focus()

## ห้องทดลอง: เลือกสายจาก techs.csv (ทุกสายที่มีในข้อมูล) · Esc = กลับเมนูหลัก
func _pick_practice_school() -> void:
	_clear_menu()
	_picking_lp = true   # ให้ Esc กลับหน้าเมนูหลัก (กลไกเดียวกับตอนเลือกมอนใช้ไอเท็ม)
	_info.text = "เลือกสายอาวุธที่จะทดลอง — ใช้ได้ทุกท่าในสาย รวมไม้ตาย · ผลไม่บันทึก"
	var first: Button = null
	for sc in techs.schools():
		var n := 0
		for t in techs.all:
			if t.school == sc:
				n += 1
		var btn := _add(UiKit.button("%s (%d ท่า)" % [sc, n], 123))
		btn.pressed.connect(func():
			practice.emit(sc)
			queue_free())
		if first == null or sc == ps.school:
			first = btn
	var back := _add(UiKit.button("กลับ", 123))
	back.pressed.connect(_show_actions)
	first.grab_focus()

## ความจำ (GDD 5.2): ลืมท่าที่ยึด = คืนช่องความจำ · ท่ากลับมาได้โดยเข้าใจท่าของมอนตัวนั้นอีกครั้ง
func _pick_forget() -> void:
	_clear_menu()
	_picking_lp = true
	_info.text = "ลืมท่าไหน? (คืนช่องความจำ)"
	var first: Button = null
	for st in ps.seized:
		var id := str(st["id"])
		var nm := str(st["name"])
		var btn := _add(UiKit.button("ลืม %s (%d)" % [nm, int(st["slots"])], 123))
		btn.pressed.connect(func():
			ps.forget(id)
			_info.text = "ลืม %s แล้ว · ความจำ %d/%d" % [nm, ps.used_memory(), ps.memory_slots()]
			_render()
			_show_actions())
		if first == null:
			first = btn
	var back := _add(UiKit.button("ย้อนกลับ", 123))
	back.pressed.connect(_show_actions)
	first.grab_focus()

func _read_label(r: Dictionary) -> String:
	var pct := int(round(100.0 * float(r.get("p", 0)) / maxf(float(r.get("need", 1)), 1.0)))
	return "%s %d%%%s" % [str(r.get("name", "")), pct, "" if bool(r.get("on", false)) else " (ถอด)"]

## ท่าหลบ (kwan 6 ต.ค. 2026): ครบ 100% แล้วถอด/ติดตั้งได้ · ยังไม่ครบ = ปุ่มกดไม่ได้
func _pick_read() -> void:
	_clear_menu()
	_picking_lp = true
	_info.text = "ถอด/ติดตั้งท่าหลบ (ติดตั้ง %d/%d)" % [ps.reads_on(), ps.read_slots()]
	var first: Button = null
	for k in ps.reads:
		var id := str(k)
		var r: Dictionary = ps.reads[id]
		var on := bool(r.get("on", false))
		var btn := _add(UiKit.button("%s %s" % ["ถอด" if on else "ติดตั้ง", _read_label(r)], 123))
		btn.disabled = int(r.get("p", 0)) < int(r.get("need", 1)) or (not on and ps.reads_on() >= ps.read_slots())
		btn.pressed.connect(func():
			ps.toggle_read(id)
			_render()
			_pick_read())
		if first == null and not btn.disabled:
			first = btn
	var back := _add(UiKit.button("ย้อนกลับ", 123))
	back.pressed.connect(_show_actions)
	if first == null:
		first = back
	first.grab_focus()

func _pick_front() -> void:
	_clear_menu()
	_picking_lp = true
	_info.text = "ให้ใครขึ้นหัวทีม?"
	var first: Button = null
	for m in ps.party:
		var nm := str(m["name"])
		var btn := _add(UiKit.button("%s %s" % [nm, UiKit.lp_dots(int(m["lp"]))], 123))
		btn.pressed.connect(func():
			ps.move_to_front(nm)
			_info.text = "%s ขึ้นหัวทีมแล้ว" % nm
			_render()
			_show_actions())
		if first == null:
			first = btn
	var back := _add(UiKit.button("ย้อนกลับ", 123))
	back.pressed.connect(_show_actions)
	first.grab_focus()

func _on_item(r: Dictionary) -> void:
	if str(r["kind"]) == "restore_lp":
		_pick_lp_target(r)
		return
	var msg := ps.use_item(r)
	_info.text = msg if msg != "" else "ใช้ไม่ได้ตอนนี้ (HP เต็มแล้ว)"
	_render()
	_show_actions()

func _pick_lp_target(r: Dictionary) -> void:
	_clear_menu()
	_picking_lp = true
	_info.text = "ให้ใคร? (มอนที่หายถาวรแล้วชุบไม่ได้)"
	var first: Button = null
	for m in ps.party:
		var btn := _add(UiKit.button("%s %s" % [m["name"], UiKit.lp_dots(int(m["lp"]))], 123))
		btn.disabled = int(m["lp"]) >= Formulas.LP_MAX
		btn.pressed.connect(func():
			_info.text = ps.use_item(r, str(m["name"]))
			_render()
			_show_actions())
		if first == null and not btn.disabled:
			first = btn
	var back := _add(UiKit.button("ย้อนกลับ", 123))
	back.pressed.connect(_show_actions)
	if first == null:
		first = back
	first.grab_focus()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _picking_lp:
			_show_actions()
		else:
			_close()

func _close() -> void:
	closed.emit()
	queue_free()
