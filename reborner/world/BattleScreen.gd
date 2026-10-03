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
const LOG_LINES := 2   # กฎ UX ข้อ 5 ของ kwan: กล่องข้อความละไม่เกิน 2 บรรทัด
const SPRITE_DIR := "res://assets/sprites/rion_lastlight_draft"

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
# เวที (ตัดสิน 3 ต.ค. 2026): พื้นมืดทำให้มอนโทนดินจมหาย → ฟ้า/พื้นสว่างจากพาเลตต์ master (CLOTH A7B5A0 · SKIN D4B08A)
const C_STAGE_SKY := Color("a7b5a0")
const C_STAGE_GROUND := Color("d4b08a")
const C_STAGE_LINE := Color("a2927b")

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
var _tex_attack: Array[Texture2D] = []   # west_a0..a3: ง้าง → พุ่ง → ฟันเต็ม → ถอย
const ATTACK_FRAME_SEC := 0.11
var _tex_hurt: Array[Texture2D] = []     # west_h0..h1: ผงะ + ประกาย → ตั้งหลัก
var _tex_ko: Array[Texture2D] = []       # west_k0..k1: ทรุดเข่า → นอนราบ (ค้างไว้จนฟื้น)
var _hero_hp_seen := -1
const HERO_X := 222                       # ตัวเอกยืนขวาของเวที ชิดแผงปาร์ตี้
const FOE_SPRITE_DIR := "res://assets/sprites/monsters_ll"
const FOE_AREA := Vector2(100, 178)       # ช่วง x ที่ศัตรูยืน (ระหว่างแผงศัตรูกับมอนฝั่งเรา)
# มอนฝั่งเรายืนหน้า-ซ้ายของ Rion (หันซ้าย = พลิกรูป) · ช่อง 1 พื้น · ช่อง 2 ลอยสูง (ค้างคาวบินได้ ไม่บังกัน)
const ALLY_SLOTS := [Vector2(176, 102), Vector2(186, 78)]
const STAGE_FEET_Y := 100.0               # เท้าแตะพื้นทราย
const FOE_IDLE_SEC := 0.45
var _foe_rects: Dictionary = {}           # Actor → TextureRect
var _foe_frames: Dictionary = {}          # Actor → Array ของ Texture2D [ยืน, idle]
var _foe_clock := 0.0
var _foe_frame := 0
var _hero_down_seen := false
var _log_shown := 0
var _recent: Array[String] = []
var _pending: Dictionary = {}
var _choosing_target := false
var auto := true                # กฎ UX ข้อ 1: สู้อัตโนมัติเปิดตั้งแต่เริ่ม · สลับด้วยปุ่มมุมขวาบนหรือ Esc
var _waiting_player := false
var _auto_btn: Button

func setup(battle: Battle, label: String, auto_on: bool = true) -> void:
	b = battle
	title = label
	auto = auto_on

func _ready() -> void:
	layer = 10
	_load_textures()
	_build()
	b.capture = true
	b.begin()
	hero = b.hero()
	_hero_hp_seen = hero.hp if hero != null else -1
	_flush_log()
	_refresh()
	if auto:
		_info_label.text = "สู้อัตโนมัติ — Esc/กลับ หรือปุ่มมุมขวาบน = สั่งเอง"
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
			var r := b.result()
			r["auto"] = auto
			finished.emit(r)
			queue_free()
			return
		var cur := b.next_turn()
		_refresh()
		if cur == null:
			_flush_log()
			await get_tree().create_timer(step_delay).timeout
			continue
		if cur.is_hero and not auto:
			_flush_log()
			_waiting_player = true
			_show_commands()
			return
		if cur == hero:
			await _hero_auto_turn()
		else:
			b.auto_act(cur)
			_flush_log()
			_refresh()
			await _react_hero()
		await get_tree().create_timer(step_delay).timeout

func _commit(action: Dictionary) -> void:
	_waiting_player = false
	_clear_menu()
	_choosing_target = false
	var kind := str(action.get("kind"))
	b.player_act(action)
	_flush_log()
	_refresh()
	if kind != "guard" and kind != "watch":
		await _play_attack()
	await get_tree().create_timer(step_delay).timeout
	_advance()

## เล่นท่าโจมตี 4 เฟรมแล้วกลับท่ายืน · เทสต์ตั้ง step_delay ต่ำ → เฟรมสั้นตาม
func _play_attack() -> void:
	if _hero_tex == null or _tex_attack.size() == 0:
		return
	var sec := minf(ATTACK_FRAME_SEC, step_delay / 4.0)
	for t in _tex_attack:
		_hero_tex.texture = t
		if sec > 0.0:
			await get_tree().create_timer(sec).timeout
	_hero_tex.texture = _rest_tex()

func _rest_tex() -> Texture2D:
	if hero != null and hero.down and _tex_ko.size() > 0:
		return _tex_ko[_tex_ko.size() - 1]
	return _tex_idle

## ตัวอื่นเล่นจบเทิร์น → ดูว่าตัวเอกโดนตี/ล้ม/ฟื้นไหม แล้วเล่นท่าตาม
func _react_hero() -> void:
	if _hero_tex == null or hero == null:
		return
	var hit := _hero_hp_seen >= 0 and hero.hp < _hero_hp_seen
	var fell := hero.down and not _hero_down_seen
	_hero_hp_seen = hero.hp
	_hero_down_seen = hero.down
	var sec := minf(ATTACK_FRAME_SEC, step_delay / 4.0)
	var seq: Array[Texture2D] = []
	if fell:
		if _tex_hurt.size() > 0:
			seq.append(_tex_hurt[0])
		seq.append_array(_tex_ko)
	elif hit and not hero.down:
		seq.append_array(_tex_hurt)
	for t in seq:
		_hero_tex.texture = t
		if sec > 0.0:
			await get_tree().create_timer(sec).timeout
	_hero_tex.texture = _rest_tex()

func _hero_auto_turn() -> void:
	b.auto_act(hero)
	_flush_log()
	_refresh()
	if not hero.guarding:
		await _play_attack()

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
	var w := _add_button("จับตา")
	w.pressed.connect(_on_watch)
	w.focus_entered.connect(_hint.bind("จับตา: เสียเทิร์น · เข้าใจท่าเด่นศัตรู +%d · ครบแล้วชนะ = รับเข้าทีมได้" % Formulas.WATCH_POINTS))
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

func _on_watch() -> void:
	_pending = {"kind": "watch"}
	_ask_target(true)

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
		if str(_pending.get("kind")) == "watch":
			var u := b.understanding_of(f)
			tel = "  ◇ %d/%d" % [u[0], u[1]]
		var btn := _add_button("%s %d/%d%s" % [f.name, f.hp, f.max_hp, tel])
		btn.pressed.connect(_on_target.bind(f))
		if first == null:
			first = btn
	var back := _add_button("ย้อนกลับ")
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
	elif event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_toggle_auto()

## สลับอัตโนมัติ/สั่งเอง — เปิดอัตโนมัติตอนเมนูรออยู่ = ให้ AI เล่นเทิร์นนี้แทนทันที
func _toggle_auto() -> void:
	auto = not auto
	_update_auto_btn()
	if auto and _waiting_player:
		_waiting_player = false
		_choosing_target = false
		_clear_menu()
		await _hero_auto_turn()
		await get_tree().create_timer(step_delay).timeout
		_advance()
	elif not auto and not _waiting_player:
		_info_label.text = "สั่งเอง — รอเทิร์นของ %s" % hero.name
	elif auto:
		_info_label.text = "สู้อัตโนมัติ — Esc/กลับ หรือปุ่มมุมขวาบน = สั่งเอง"

func _update_auto_btn() -> void:
	if _auto_btn != null:
		_auto_btn.text = "อัตโนมัติ: %s" % ("เปิด" if auto else "ปิด")

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
		# แผงแคบ (ผังแบบ A) → บรรทัดแรก ชื่อ+HP · บรรทัดสองตัวเล็ก: ล้ม/ท่าที่เปิด/ความเข้าใจ/สถานะ
		var name_line := a.name
		if allies and not a.is_hero and a.lp > 0:
			name_line += " " + UiKit.lp_dots(a.lp)
		var notes: Array[String] = []
		if not a.telegraph.is_empty():
			notes.append("▼ " + str(a.telegraph["name"]))
		if not allies:
			var u := b.understanding_of(a)
			if u[0] > 0:
				notes.append("◇%d/%d" % [mini(u[0], u[1]), u[1]])
		if not a.statuses.is_empty():
			notes.append("[" + ", ".join(a.statuses.keys()) + "]")
		var hp_txt := "ล้ม" if a.down else "%d/%d" % [a.hp, a.max_hp]
		var head := _label("%s %s" % [name_line, hp_txt], 6, C_MUTED if a.down else C_TEXT)
		head.clip_text = true
		head.custom_minimum_size = Vector2(box.size.x, 0)
		row.add_child(head)
		var ratio := float(a.hp) / maxf(float(a.max_hp), 1.0)
		row.add_child(_bar(ratio, C_HP if ratio > 0.3 else C_HP_LOW, 3))
		if not notes.is_empty():
			var nl := _label(" ".join(notes), 6, C_GOLD if not a.telegraph.is_empty() else C_MUTED)
			nl.clip_text = true
			nl.custom_minimum_size = Vector2(box.size.x, 0)
			row.add_child(nl)
		if allies and a.is_hero:
			row.add_child(_bar(float(a.sp) / maxf(float(a.max_sp), 1.0), C_SP, 2))
			var ins := minf(a.insight / Insight.THRESHOLD, 1.0)
			row.add_child(_bar(ins, C_GOLD, 2))
			row.add_child(_label("SP %d/%d · Insight %d%%" % [a.sp, a.max_sp, int(ins * 100.0)], 6, C_MUTED))
			if ins >= 1.0:
				row.add_child(_label("◆ ท่าถัดไปประกาย", 6, C_GOLD))
		box.add_child(row)

# ── สร้าง UI ─────────────────────────────────────────────────
func _load_textures() -> void:
	# ปาร์ตี้อยู่ขวา หันซ้ายเข้าหาศัตรู · ท่าโจมตี west_a0-3 (ร่าง รอ kwan อนุมัติ)
	for i in 4:
		var pa := "%s/west_a%d.png" % [SPRITE_DIR, i]
		if ResourceLoader.exists(pa):
			_tex_attack.append(load(pa))
		for pair in [["h", _tex_hurt], ["k", _tex_ko]]:
			var ph := "%s/west_%s%d.png" % [SPRITE_DIR, pair[0], i]
			if ResourceLoader.exists(ph):
				pair[1].append(load(ph))
	var p_idle := "%s/west.png" % SPRITE_DIR
	if ResourceLoader.exists(p_idle):
		_tex_idle = load(p_idle)

func _build() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(bg)
	for r in [[Rect2(0, 24, 384, 58), C_STAGE_SKY], [Rect2(0, 82, 384, 21), C_STAGE_GROUND], [Rect2(0, 82, 384, 1), C_STAGE_LINE]]:
		var st := ColorRect.new()
		st.position = r[0].position
		st.size = r[0].size
		st.color = r[1]
		root.add_child(st)
	# แผงเข้มรองตัวหนังสือบนเวทีสว่าง (ตัวหนังสือสีครีมอ่านไม่ออกบนพื้นสว่าง)
	for r in [Rect2(2, 26, 96, 76), Rect2(288, 26, 94, 76)]:
		var pn := Panel.new()
		pn.add_theme_stylebox_override("panel", UiKit.box(Color(C_PANEL, 0.88), C_LINE))
		pn.position = r.position
		pn.size = r.size
		root.add_child(pn)

	var head := _label(title, 7, C_GOLD)
	head.position = Vector2(4, 1)
	root.add_child(head)

	_auto_btn = UiKit.button("", 82)
	_auto_btn.position = Vector2(298, 0)
	_auto_btn.focus_mode = Control.FOCUS_NONE   # ไม่แย่งโฟกัสจากเมนูคำสั่ง
	_auto_btn.pressed.connect(_toggle_auto)
	root.add_child(_auto_btn)
	_update_auto_btn()

	_queue_box = HBoxContainer.new()
	_queue_box.position = Vector2(4, 12)
	_queue_box.add_theme_constant_override("separation", 2)
	root.add_child(_queue_box)

	# จอสู้ side-view: ศัตรูซ้าย · ปาร์ตี้ขวา (MASTER §5)
	_ally_box = VBoxContainer.new()
	_ally_box.position = Vector2(290, 28)
	_ally_box.size = Vector2(90, 74)
	_ally_box.add_theme_constant_override("separation", 1)
	_ally_box.clip_contents = true   # ล้นแผงเมื่อไหร่ ตัดทิ้ง ไม่ทับช่อง log
	root.add_child(_ally_box)

	_hero_tex = TextureRect.new()
	_hero_tex.texture = _tex_idle
	_hero_tex.position = Vector2(HERO_X, 34)
	_hero_tex.size = Vector2(64, 64)
	_hero_tex.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(_hero_tex)

	_build_foe_sprites(root)
	_build_ally_sprites(root)

	_foe_box = VBoxContainer.new()
	_foe_box.position = Vector2(4, 28)
	_foe_box.size = Vector2(92, 74)
	_foe_box.add_theme_constant_override("separation", 1)
	_foe_box.clip_contents = true
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

## ศัตรูที่มีรูป (assets/sprites/monsters_ll/<id>.png) ยืนบนเวทีระหว่างแผงศัตรูกับตัวเอก · ตัวที่ไม่มีรูปมีแค่ชื่อในแผง
func _build_foe_sprites(root: Control) -> void:
	var foes: Array = b.actors.filter(func(a): return a.side == "foe")
	var n := foes.size()
	if n == 0:
		return
	var step := (FOE_AREA.y - FOE_AREA.x - 48.0) / maxf(float(n - 1), 1.0)
	# วาดแถวหลัง (ลำดับคี่ ยืนสูงกว่า) ก่อน ให้แถวหน้าทับ
	var order: Array = range(n)
	order.sort_custom(func(i, j): return (i % 2) > (j % 2))
	for i in order:
		var a: Actor = foes[i]
		var frames: Array = []
		for suffix in ["", "_idle1"]:
			var path := "%s/%s%s.png" % [FOE_SPRITE_DIR, a.id, suffix]
			if ResourceLoader.exists(path):
				frames.append(load(path))
		if frames.is_empty():
			continue
		var tex: Texture2D = frames[0]
		var r := TextureRect.new()
		r.texture = tex
		r.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		r.size = tex.get_size()
		var x: float = FOE_AREA.x + (step * i if n > 1 else (FOE_AREA.y - FOE_AREA.x - 48.0) / 2.0)
		r.position = Vector2(x, STAGE_FEET_Y - tex.get_size().y - (6.0 if i % 2 == 1 else 0.0))
		root.add_child(r)
		_foe_rects[a] = r
		_foe_frames[a] = frames

## มอนฝั่งเรา: COMP-<id> (เวอร์ชันเพื่อน) ก่อน · ไม่มีก็ใช้รูปศัตรู <id> · พลิกหันซ้ายเข้าหาศัตรู
func _build_ally_sprites(root: Control) -> void:
	var allies: Array = b.actors.filter(func(a): return a.side == "ally" and not a.is_hero)
	for i in mini(allies.size(), ALLY_SLOTS.size()):
		var a: Actor = allies[i]
		var frames: Array = []
		for base in ["COMP-" + a.id, a.id]:
			for suffix in ["", "_idle1"]:
				var path := "%s/%s%s.png" % [FOE_SPRITE_DIR, base, suffix]
				if ResourceLoader.exists(path):
					frames.append(load(path))
			if not frames.is_empty():
				break
		if frames.is_empty():
			continue
		var tex: Texture2D = frames[0]
		var r := TextureRect.new()
		r.texture = tex
		r.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		r.flip_h = true
		r.size = tex.get_size()
		var slot: Vector2 = ALLY_SLOTS[i]
		r.position = Vector2(slot.x, slot.y - tex.get_size().y)
		root.add_child(r)
		_foe_rects[a] = r       # ใช้ลูป idle/จางตอนล้ม ชุดเดียวกับศัตรู
		_foe_frames[a] = frames

func _process(delta: float) -> void:
	if _foe_rects.is_empty():
		return
	_foe_clock += delta
	if _foe_clock < FOE_IDLE_SEC:
		return
	_foe_clock = 0.0
	_foe_frame = 1 - _foe_frame
	for a in _foe_rects:
		var fr: Array = _foe_frames[a]
		_foe_rects[a].texture = fr[mini(_foe_frame, fr.size() - 1)]
		_foe_rects[a].modulate = Color(1, 1, 1, 0.3) if a.down else Color.WHITE   # ล้ม = จาง
