# world/BattleScreen.gd — หน้าจอต่อสู้ที่ผู้เล่นกดเอง (ขั้น 4 สัปดาห์ 2)
# ไม่มีลูปเทิร์นของตัวเอง — เดินผ่าน Battle.begin/is_over/next_turn/auto_act/player_act
# ชุดเดียวกับที่ Battle.run() (Sim) ใช้ ต่างแค่เทิร์นตัวเอกให้ผู้เล่นเลือก (GDD 11.15)
# วิธีใช้: screen.setup(battle, "ชื่อศึก") → add_child(screen) → await screen.finished
class_name BattleScreen
extends CanvasLayer

signal finished(result: Dictionary)

var step_delay := 0.55       # วินาทีต่อเทิร์นของตัวที่ไม่ใช่ผู้เล่น (เทสต์ตั้งให้เร็วได้)
var end_delay := 1.2
const QUEUE_SLOTS := 8          # GDD 3.1 — UI ต้องแสดงคิวล่วงหน้า 8 ช่อง
const LOG_LINES := 4
const SPRITE_DIR := "res://assets/sprites/hero"

# พาเลตต์เดียวกับแผนที่องก์ 1
const C_BG := Color("15130f")
const C_PANEL := Color("1d1a15")
const C_LINE := Color("3a3329")
const C_TEXT := Color("e8d9b5")
const C_MUTED := Color("a89b80")
const C_GOLD := Color("c9a24a")
const C_HP := Color("6b7d4a")
const C_HP_LOW := Color("b5553f")
const C_SP := Color("3d6a7a")
const C_FOE := Color("9a4a3a")
const C_ALLY := Color("4f6a44")

const SCOPE_TH := {"single": "เดี่ยว", "row": "ทั้งแถว", "column": "คอลัมน์", "all": "ทั้งหมด", "self": "ตัวเอง"}

var b: Battle
var title := ""
var hero: Actor

var _queue_box: HBoxContainer
var _ally_box: VBoxContainer
var _foe_box: VBoxContainer
var _log_label: Label
var _info_label: Label
var _menu: GridContainer
var _hero_tex: TextureRect
var _tex_idle: Texture2D
var _tex_cast: Texture2D
var _log_shown := 0
var _recent: Array[String] = []
var _pending: Dictionary = {}
var _choosing_target := false

func setup(battle: Battle, label: String) -> void:
	b = battle
	title = label

func _ready() -> void:
	layer = 10
	_load_textures()
	_build()
	b.capture = true
	b.begin()
	hero = b.hero()
	_flush_log()
	_refresh()
	_advance()

# ── ลำดับเทิร์น ───────────────────────────────────────────────
func _advance() -> void:
	while true:
		if b.is_over():
			_flush_log()
			_refresh()
			_clear_menu()
			_info_label.text = "ชนะ!" if b.won else "แพ้…"
			await get_tree().create_timer(end_delay).timeout
			finished.emit(b.result())
			queue_free()
			return
		var cur := b.next_turn()
		_refresh()
		if cur == null:
			_flush_log()
			await get_tree().create_timer(step_delay).timeout
			continue
		if cur.is_hero:
			_flush_log()
			_show_commands()
			return
		b.auto_act(cur)
		_flush_log()
		_refresh()
		await get_tree().create_timer(step_delay).timeout

func _commit(action: Dictionary) -> void:
	_clear_menu()
	_choosing_target = false
	if _hero_tex != null and _tex_cast != null and str(action.get("kind")) != "guard":
		_hero_tex.texture = _tex_cast
	b.player_act(action)
	_flush_log()
	_refresh()
	await get_tree().create_timer(step_delay).timeout
	if _hero_tex != null and _tex_idle != null:
		_hero_tex.texture = _tex_idle
	_advance()

# ── คำสั่งของผู้เล่น ─────────────────────────────────────────
func _show_commands() -> void:
	_clear_menu()
	_choosing_target = false
	_info_label.text = "เทิร์นของ %s — เลือกท่า" % hero.name
	var first: Button = null
	var opts := b.hero_options(hero)
	for t in opts:
		var cost := (" %dSP" % t.sp) if t.sp > 0 else ""
		var btn := _add_button("%s%s" % [t.name, cost])
		btn.pressed.connect(_on_tech.bind(t))
		btn.focus_entered.connect(_describe.bind(t))
		btn.mouse_entered.connect(_describe.bind(t))
		if first == null:
			first = btn
	if opts.is_empty():
		var basic := _add_button("โจมตี")
		basic.pressed.connect(_on_tech.bind(null))
		first = basic
	var partner := b.combo_partner_for(hero)
	if partner != null:
		var cb := _add_button("คอมโบ + %s" % partner.name)
		cb.pressed.connect(_on_combo)
		cb.focus_entered.connect(_hint.bind("คอมโบ: SP %d ทั้งคู่ · ดาเมจ x%.1f · ใช้เวลาทั้งสองตัว" % [Formulas.COMBO_SP, Formulas.COMBO_MULT]))
	var g := _add_button("ตั้งรับ")
	g.pressed.connect(_on_guard)
	g.focus_entered.connect(_hint.bind("ตั้งรับ: ลดดาเมจ 50% · สลัดสถานะ 1 เทิร์น · ท่าถัดไปเบาลงครึ่ง"))
	if first != null:
		first.grab_focus()

func _on_tech(t: Tech) -> void:
	_pending = {"kind": "tech", "tech": t}
	_ask_target(t == null or t.scope != "all")

func _on_combo() -> void:
	var opts := b.hero_options(hero)
	_pending = {"kind": "combo", "tech": opts[0] if not opts.is_empty() else null}
	_ask_target(true)

func _on_guard() -> void:
	_commit({"kind": "guard"})

func _ask_target(needs_pick: bool) -> void:
	var fs := b.foes()
	if not needs_pick or fs.size() <= 1:
		var action := _pending.duplicate()
		action["target"] = fs[0] if not fs.is_empty() else null
		_commit(action)
		return
	_clear_menu()
	_choosing_target = true
	_info_label.text = "เลือกเป้าหมาย · Esc ย้อนกลับ"
	var first: Button = null
	for f in fs:
		var tel := "  ▼" if not f.telegraph.is_empty() else ""
		var btn := _add_button("%s %d/%d%s" % [f.name, f.hp, f.max_hp, tel])
		btn.pressed.connect(_on_target.bind(f))
		if first == null:
			first = btn
	var back := _add_button("← ย้อนกลับ")
	back.pressed.connect(_show_commands)
	first.grab_focus()

func _on_target(f: Actor) -> void:
	var action := _pending.duplicate()
	action["target"] = f
	_commit(action)

func _unhandled_input(event: InputEvent) -> void:
	if _choosing_target and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_show_commands()

func _describe(t: Tech) -> void:
	if t == null:
		return
	var s := "พลัง %d · น้ำหนัก %.1f · %s · %s" % [int(t.power), t.weight, t.element, SCOPE_TH.get(t.scope, t.scope)]
	if t.hits > 1:
		s += " · %d ครั้ง" % t.hits
	if t.status != "":
		s += " · %s" % t.status
	_info_label.text = s

func _hint(text: String) -> void:
	_info_label.text = text

# ── อัปเดตหน้าจอ ─────────────────────────────────────────────
func _flush_log() -> void:
	while _log_shown < b.log_lines.size():
		var line := b.log_lines[_log_shown].strip_edges()
		_log_shown += 1
		if line == "":
			continue
		_recent.append(line)
	while _recent.size() > LOG_LINES:
		_recent.remove_at(0)
	_log_label.text = "\n".join(_recent)

func _refresh() -> void:
	for c in _queue_box.get_children():
		c.queue_free()
	var q := b.preview(QUEUE_SLOTS)
	for i in q.size():
		var a: Actor = q[i]
		var col := C_GOLD if a.is_hero else (C_ALLY if a.side == "ally" else C_FOE)
		_queue_box.add_child(_chip(a.name, col, i == 0))
	_fill_side(_ally_box, b.actors.filter(func(a): return a.side == "ally"), true)
	_fill_side(_foe_box, b.actors.filter(func(a): return a.side == "foe"), false)

func _fill_side(box: VBoxContainer, list: Array, allies: bool) -> void:
	for c in box.get_children():
		c.queue_free()
	for x in list:
		var a: Actor = x
		var row := VBoxContainer.new()
		row.add_theme_constant_override("separation", 0)
		var name_line := a.name
		if a.down:
			name_line += "  (ล้ม)"
		if not a.telegraph.is_empty():
			name_line += "  ▼ " + str(a.telegraph["name"])
		if not a.statuses.is_empty():
			name_line += "  [" + ", ".join(a.statuses.keys()) + "]"
		var head := _label("%s   %d/%d" % [name_line, a.hp, a.max_hp], 7, C_MUTED if a.down else C_TEXT)
		head.clip_text = true
		head.custom_minimum_size = Vector2(box.size.x, 0)
		row.add_child(head)
		var ratio := float(a.hp) / maxf(float(a.max_hp), 1.0)
		row.add_child(_bar(ratio, C_HP if ratio > 0.3 else C_HP_LOW, 3))
		if allies and a.is_hero:
			row.add_child(_bar(float(a.sp) / maxf(float(a.max_sp), 1.0), C_SP, 2))
			var ins := minf(a.insight / Insight.THRESHOLD, 1.0)
			row.add_child(_bar(ins, C_GOLD, 2))
			var extra := "SP %d/%d · Insight %d%%%s" % [a.sp, a.max_sp, int(ins * 100.0), "  ◆ ท่าถัดไปประกาย" if ins >= 1.0 else ""]
			row.add_child(_label(extra, 6, C_MUTED))
		box.add_child(row)

# ── สร้าง UI ─────────────────────────────────────────────────
func _load_textures() -> void:
	var p_idle := "%s/idle.png" % SPRITE_DIR
	var p_cast := "%s/attack_cast.png" % SPRITE_DIR
	if ResourceLoader.exists(p_idle):
		_tex_idle = load(p_idle)
	if ResourceLoader.exists(p_cast):
		_tex_cast = load(p_cast)

func _build() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(bg)

	var head := _label(title, 7, C_GOLD)
	head.position = Vector2(4, 1)
	root.add_child(head)

	_queue_box = HBoxContainer.new()
	_queue_box.position = Vector2(4, 12)
	_queue_box.add_theme_constant_override("separation", 2)
	root.add_child(_queue_box)

	_ally_box = VBoxContainer.new()
	_ally_box.position = Vector2(4, 28)
	_ally_box.size = Vector2(150, 74)
	_ally_box.add_theme_constant_override("separation", 3)
	root.add_child(_ally_box)

	_hero_tex = TextureRect.new()
	_hero_tex.texture = _tex_idle
	_hero_tex.position = Vector2(160, 40)
	_hero_tex.size = Vector2(48, 48)
	_hero_tex.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(_hero_tex)

	_foe_box = VBoxContainer.new()
	_foe_box.position = Vector2(216, 28)
	_foe_box.size = Vector2(164, 74)
	_foe_box.add_theme_constant_override("separation", 3)
	root.add_child(_foe_box)

	var log_bg := ColorRect.new()
	log_bg.color = C_PANEL
	log_bg.position = Vector2(2, 104)
	log_bg.size = Vector2(380, 42)
	root.add_child(log_bg)
	_log_label = _label("", 7, C_TEXT)
	_log_label.position = Vector2(6, 105)
	_log_label.size = Vector2(372, 40)
	_log_label.clip_text = true
	_log_label.max_lines_visible = LOG_LINES
	_log_label.add_theme_constant_override("line_spacing", -4)
	root.add_child(_log_label)

	_info_label = _label("", 7, C_GOLD)
	_info_label.position = Vector2(4, 148)
	_info_label.size = Vector2(376, 10)
	_info_label.clip_text = true
	root.add_child(_info_label)

	_menu = GridContainer.new()
	_menu.columns = 3
	_menu.position = Vector2(4, 160)
	_menu.size = Vector2(376, 54)
	_menu.add_theme_constant_override("h_separation", 3)
	_menu.add_theme_constant_override("v_separation", 2)
	root.add_child(_menu)

func _clear_menu() -> void:
	for c in _menu.get_children():
		_menu.remove_child(c)
		c.queue_free()

func _add_button(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(123, 12)
	btn.clip_text = true
	btn.focus_mode = Control.FOCUS_ALL
	btn.add_theme_font_size_override("font_size", 7)
	btn.add_theme_color_override("font_color", C_TEXT)
	btn.add_theme_color_override("font_focus_color", C_BG)
	btn.add_theme_color_override("font_hover_color", C_BG)
	btn.add_theme_color_override("font_pressed_color", C_BG)
	btn.add_theme_stylebox_override("normal", _box(C_PANEL, C_LINE))
	btn.add_theme_stylebox_override("hover", _box(C_GOLD, C_GOLD))
	btn.add_theme_stylebox_override("focus", _box(C_GOLD, C_TEXT))
	btn.add_theme_stylebox_override("pressed", _box(C_TEXT, C_TEXT))
	_menu.add_child(btn)
	return btn

func _box(fill: Color, border: Color) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fill
	s.border_color = border
	s.set_border_width_all(1)
	s.set_corner_radius_all(2)
	s.content_margin_left = 4
	s.content_margin_right = 4
	s.content_margin_top = 0
	s.content_margin_bottom = 0
	return s

func _chip(text: String, col: Color, now: bool) -> Control:
	var p := PanelContainer.new()
	p.custom_minimum_size = Vector2(44, 12)
	p.add_theme_stylebox_override("panel", _box(col if now else C_PANEL, col))
	var l := _label(text, 6, C_BG if now else C_TEXT)
	l.clip_text = true
	l.custom_minimum_size = Vector2(36, 0)
	p.add_child(l)
	return p

func _bar(ratio: float, col: Color, h: int) -> Control:
	var back := ColorRect.new()
	back.color = C_LINE
	back.custom_minimum_size = Vector2(0, h)
	var fill := ColorRect.new()
	fill.color = col
	fill.size = Vector2(0, h)
	back.add_child(fill)
	back.resized.connect(func(): fill.size = Vector2(back.size.x * clampf(ratio, 0.0, 1.0), h))
	return back

func _label(text: String, size: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	return l
