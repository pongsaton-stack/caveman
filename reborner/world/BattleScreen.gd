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
const ALLY_SLOTS := [Vector2(188, 102), Vector2(184, 76)]   # หนอนชิดขอบใสด้านซ้ายของรูป Rion · บอส 96px เกยแค่ 6px
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
			_play_events()
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
	_play_events()
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
	_play_events()
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
	const PANEL_EDGE := 98.0             # รูปกว้าง (บอส 96px) ห้ามทับแผงรายชื่อศัตรู
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
		var w := tex.get_size().x
		var x: float = FOE_AREA.x + (step * i if n > 1 else (FOE_AREA.y - FOE_AREA.x - w) / 2.0)
		x = maxf(x, PANEL_EDGE)
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

# ── เอฟเฟกต์สกิล ─────────────────────────────────────────────────
# อ่าน b.events (เก็บตอน capture) หลังแต่ละการกระทำ: ป้ายชื่อท่า · เอฟเฟกต์ตามสาย · ตัวเลขดาเมจลอย
# ไม่ await (เล่นขนานกับท่าฟันของ Rion) · เทสต์ที่ตั้ง step_delay = 0 ข้ามทั้งหมด
const FX_COLOR := {"คม": Color("ff5a4a"), "แทง": Color("7ad0e0"), "ทุบ": Color("e39253"), "ยิง": Color("f2c08a"), "กล": Color("8ad0a0")}
const FX_DEFAULT := Color("ffd0c0")
const FX_SEC := 0.5          # kwan 3 ต.ค.: "ใหญ่/ชัดขึ้น" (เดิม 0.28)
var _fx_layer: Control
var _banner: Label
var _banner_tw: Tween       # ป้ายใหม่ต้องหยุดการจางของป้ายเก่า (ไม่งั้นป้ายเก่าซ่อนป้ายใหม่ไปด้วย)

func _fx_root() -> Control:
	if _fx_layer == null:
		_fx_layer = Control.new()
		_fx_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
		_fx_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		get_child(0).add_child(_fx_layer)   # ลูกตัวสุดท้ายของ root = วาดทับทุกอย่างบนเวที
	return _fx_layer

func _play_events() -> void:
	var evs: Array = b.events.duplicate()
	b.events.clear()
	if evs.is_empty() or step_delay <= 0.0:
		return
	var ult := false
	for e in evs:
		if e.has("tech"):
			ult = _is_ultimate(e)
			_show_banner(e)
			if ult:
				_ultimate_intro(e, evs)
			break
	var nth := 0     # ตัวเลขหลายตัวในครั้งเดียว (ท่าหมู่/ไม้ตาย) → เหลื่อมขึ้นทีละแถว ไม่ทับกัน
	for e in evs:
		var to := _actor_point(e["tgt"])
		if to == Vector2.INF:
			continue
		if e.has("dot"):
			_float_number(to, "%d %s" % [e["dmg"], e["dot"]], Color("c08ad0"))
			continue
		var from := _actor_point(e["src"])
		var col: Color = Color("f2c94c") if e["glimmer"] or str(e["tech"]).begins_with("คอมโบ") else FX_COLOR.get(e["school"], FX_DEFAULT)
		match str(e["school"]):
			"คม": _fx_slash(to, col, from)
			"แทง": _fx_pierce(to, col, from)
			"ทุบ": _fx_crush(to, col)
			"ยิง": _fx_shoot(from, to, col)
			_: _fx_claw(to, col, from)
		if ult:
			_fx_burst(to, col)
		_hit_flash(e["tgt"])
		nth += 1
		_float_number(to + Vector2(0, 11 * ((nth - 1) % 3)), ("%d!" % e["dmg"]) if e["weak"] else str(e["dmg"]), Color("ffe08a") if e["weak"] else Color.WHITE)

## จุดกลางตัวบนเวที (Vector2.INF = ตัวนี้ไม่มีรูปบนเวที)
func _actor_point(a) -> Vector2:
	if a == null:
		return Vector2.INF
	if a == hero and _hero_tex != null:
		return _hero_tex.position + Vector2(32, 34)
	if _foe_rects.has(a):
		var r: TextureRect = _foe_rects[a]
		return r.position + r.size * Vector2(0.5, 0.55)
	return Vector2.INF

## ไม้ตาย = ท่าขั้นปลายของต้นไม้ (req_prof ≥ ULT_PROF ใน techs.csv) · ใช้เลือกเอฟเฟกต์เท่านั้น ไม่แตะค่าเกม
const ULT_PROF := 40
const NUMBER_TOP_Y := 40.0      # ใต้ป้ายชื่อท่า (y 24-40)
var _dim: ColorRect

func _is_ultimate(e: Dictionary) -> bool:
	if b.techs == null:
		return false
	var t: Tech = b.techs.get_tech(str(e["tech"]))
	return t != null and t.req_prof >= ULT_PROF

## ไม้ตาย: จอมืดลง · จอสั่น · ท่ากวาดทั้งหมด (scope all) = วงล้อคมหมุนรอบกลุ่มศัตรู
func _ultimate_intro(e: Dictionary, evs: Array) -> void:
	if _dim == null:
		_dim = ColorRect.new()
		_dim.color = Color(0.05, 0.03, 0.08)
		_dim.set_anchors_preset(Control.PRESET_FULL_RECT)
		_dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_fx_root().add_child(_dim)
	_fx_root().move_child(_dim, 0)
	_dim.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(_dim, "modulate:a", 0.55, 0.12)
	tw.tween_interval(0.7)
	tw.tween_property(_dim, "modulate:a", 0.0, 0.35)
	_fx_root().move_child(_banner, -1)
	_shake(get_child(0), 3.0, 0.35)
	var t: Tech = b.techs.get_tech(str(e["tech"]))
	var pts: Array = []
	for ev in evs:
		var p := _actor_point(ev.get("tgt"))
		if p != Vector2.INF and not ev.has("dot"):
			pts.append(p)
	if t.scope != "single" and pts.size() > 0:
		var c := Vector2.ZERO
		for p in pts:
			c += p
		_fx_wheel(c / pts.size(), FX_COLOR.get(e["school"], FX_DEFAULT))

func _shake(n: CanvasItem, amp: float, sec: float) -> void:
	if n == null or not ("position" in n):
		return
	var base: Vector2 = n.position
	var tw := create_tween()
	tw.tween_method(func(t: float): n.position = base + Vector2(sin(t * 60.0), cos(t * 47.0)) * amp * (1.0 - t), 0.0, 1.0, sec)
	tw.tween_callback(func(): n.position = base)

## วงล้อ: ใบคม 6 ใบเรียงเป็นวง หมุน 1 รอบพร้อมขยาย แล้วจาง
func _fx_wheel(at: Vector2, col: Color) -> void:
	var wheel := Node2D.new()
	wheel.position = at
	wheel.scale = Vector2(0.4, 0.4)
	_fx_root().add_child(wheel)
	for k in 6:
		for layer in [[col.darkened(0.4), 7.0], [col, 4.5], [Color(1, 1, 1, 0.95), 1.5]]:
			var pts := PackedVector2Array()
			for i in 7:
				var ang := TAU * k / 6.0 + deg_to_rad(i * 7.0)
				var r := 40.0 - i * 1.5
				pts.append(Vector2(cos(ang), sin(ang) * 0.75) * r)
			wheel.add_child(_line(pts, layer[0], layer[1]))
	var tw := create_tween().set_parallel()
	tw.tween_property(wheel, "rotation", TAU, 0.7).set_ease(Tween.EASE_OUT)
	tw.tween_property(wheel, "scale", Vector2(1.15, 1.15), 0.5).set_ease(Tween.EASE_OUT)
	tw.tween_property(wheel, "modulate:a", 0.0, 0.3).set_delay(0.55)
	tw.chain().tween_callback(wheel.queue_free)

## ไม้ตาย: วงแสงขาว + ประกายแฉกใหญ่ที่ตัวเป้าทุกตัว
func _fx_burst(at: Vector2, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 17:
		var ang := TAU * i / 16.0
		pts.append(Vector2(cos(ang), sin(ang)) * 10.0)
	var ring := _line(pts, Color(1, 1, 1, 0.9), 3.0)
	ring.position = at
	_fx_root().add_child(ring)
	_fade_free(ring, 2.8)
	for k in 4:
		var ang := PI / 4.0 * k
		var ray := _line(PackedVector2Array([Vector2.ZERO, Vector2(cos(ang), sin(ang)) * 18.0]), col.lightened(0.4), 3.0)
		ray.add_child(_line(PackedVector2Array([Vector2.ZERO, -Vector2(cos(ang), sin(ang)) * 18.0]), col.lightened(0.4), 3.0))
		ray.position = at
		_fx_root().add_child(ray)
		_fade_free(ray, 1.8)

func _show_banner(e: Dictionary) -> void:
	if _banner == null:
		_banner = _label("", 11, C_TEXT)
		_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_banner.position = Vector2(98, 24)
		_banner.size = Vector2(188, 16)
		_banner.add_theme_color_override("font_outline_color", Color.BLACK)
		_banner.add_theme_constant_override("outline_size", 3)
		_fx_root().add_child(_banner)
	var src = e.get("src")
	var who: String = src.name if src != null else ""
	_banner.add_theme_font_size_override("font_size", 14 if _is_ultimate(e) else 11)
	if _is_ultimate(e):
		_banner.text = "◆ ไม้ตาย! %s · %s" % [who, e["tech"]]
		_banner.add_theme_color_override("font_color", Color("ffd27a"))
	elif e["glimmer"]:
		_banner.text = "★ ประกาย! %s · %s" % [who, e["tech"]]
		_banner.add_theme_color_override("font_color", Color("f2c94c"))
	else:
		_banner.text = "%s · %s" % [who, e["tech"]]
		_banner.add_theme_color_override("font_color", FX_COLOR.get(e["school"], FX_DEFAULT).lightened(0.3))
	if _banner_tw != null and _banner_tw.is_valid():
		_banner_tw.kill()
	_banner.modulate = Color.WHITE
	_banner_tw = create_tween()
	_banner_tw.tween_interval(1.0)
	_banner_tw.tween_property(_banner, "modulate:a", 0.0, 0.3)

func _fade_free(n: CanvasItem, grow: float) -> void:
	var tw := create_tween().set_parallel()
	tw.tween_property(n, "modulate:a", 0.0, FX_SEC).set_ease(Tween.EASE_IN)
	if grow != 1.0:
		tw.tween_property(n, "scale", n.scale * grow, FX_SEC)
	tw.chain().tween_callback(n.queue_free)

func _line(points: PackedVector2Array, col: Color, w: float) -> Line2D:
	var l := Line2D.new()
	l.points = points
	l.width = w
	l.default_color = col
	l.begin_cap_mode = Line2D.LINE_CAP_ROUND
	l.end_cap_mode = Line2D.LINE_CAP_ROUND
	return l

func _side(from: Vector2, to: Vector2) -> float:
	return 1.0 if from == Vector2.INF or from.x <= to.x else -1.0

## คม: ส่วนโค้งฟันสองชั้น (สี + แกนขาว)
func _fx_slash(at: Vector2, col: Color, from: Vector2) -> void:
	var d := _side(from, at)
	for layer in [[col.darkened(0.4), 9.0, 26.0], [col, 6.0, 26.0], [Color(1, 1, 1, 0.95), 2.0, 25.0]]:
		var pts := PackedVector2Array()
		for i in 9:
			var ang := deg_to_rad(-70.0 + i * 20.0)
			pts.append(Vector2(-cos(ang) * d, sin(ang)) * layer[2])
		var l := _line(pts, layer[0], layer[1])
		l.position = at
		l.scale = Vector2(0.7, 0.7)
		_fx_root().add_child(l)
		_fade_free(l, 1.6)

## แทง: เส้นพุ่งทะลุตัวเป้า + หัวลูกศร
func _fx_pierce(at: Vector2, col: Color, from: Vector2) -> void:
	var d := _side(from, at)
	var l := _line(PackedVector2Array([Vector2(-40 * d, 0), Vector2(26 * d, 0)]), col, 5.0)
	l.add_child(_line(PackedVector2Array([Vector2(-36 * d, 0), Vector2(24 * d, 0)]), Color.WHITE, 1.5))
	l.position = at - Vector2(10 * d, 0)
	_fx_root().add_child(l)
	var head := Polygon2D.new()
	head.polygon = PackedVector2Array([Vector2(36 * d, 0), Vector2(24 * d, -7), Vector2(24 * d, 7)])
	head.color = Color.WHITE
	l.add_child(head)
	var tw := create_tween()
	tw.tween_property(l, "position:x", at.x + 10 * d, FX_SEC * 0.6)
	_fade_free(l, 1.0)

## ทุบ: วงแรงกระแทกขยาย + เศษหินกระเด็น
func _fx_crush(at: Vector2, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 17:
		var ang := TAU * i / 16.0
		pts.append(Vector2(cos(ang), sin(ang) * 0.6) * 9.0)
	var ring := _line(pts, col, 4.0)
	ring.position = at + Vector2(0, 10)
	_fx_root().add_child(ring)
	_fade_free(ring, 3.5)
	for i in 8:
		var bit := ColorRect.new()
		bit.color = col.darkened(0.3)
		bit.size = Vector2(4, 4)
		bit.position = at + Vector2(0, 8)
		_fx_root().add_child(bit)
		var dir := Vector2(cos(PI + i * PI / 7.0), sin(PI + i * PI / 7.0)) * 24.0
		var tw := create_tween().set_parallel()
		tw.tween_property(bit, "position", bit.position + dir, FX_SEC)
		tw.tween_property(bit, "modulate:a", 0.0, FX_SEC)
		tw.chain().tween_callback(bit.queue_free)

## ยิง: กระสุนวิ่งจากผู้ยิงเข้าเป้า แล้วแตกเป็นประกาย
func _fx_shoot(from: Vector2, to: Vector2, col: Color) -> void:
	if from == Vector2.INF:
		_fx_claw(to, col, from)
		return
	var shot := ColorRect.new()
	shot.color = col
	shot.size = Vector2(6, 6)
	shot.position = from - Vector2(3, 3)
	_fx_root().add_child(shot)
	var tw := create_tween()
	tw.tween_property(shot, "position", to - Vector2(3, 3), FX_SEC * 0.5)
	tw.tween_callback(func():
		shot.queue_free()
		_fx_claw(to, col, Vector2.INF))

## ท่ามอน/มือเปล่า/อื่นๆ: รอยข่วน 3 เส้น + ประกายกากบาท
func _fx_claw(at: Vector2, col: Color, from: Vector2) -> void:
	var d := _side(from, at)
	for i in 3:
		var off := Vector2((i - 1) * 8, 0)
		var l := _line(PackedVector2Array([Vector2(-11 * d, -14) + off, Vector2(8 * d, 14) + off]), col, 3.5)
		l.position = at
		_fx_root().add_child(l)
		_fade_free(l, 1.3)
	var star := _line(PackedVector2Array([Vector2(-10, 0), Vector2(10, 0)]), Color.WHITE, 2.0)
	star.add_child(_line(PackedVector2Array([Vector2(0, -10), Vector2(0, 10)]), Color.WHITE, 2.0))
	star.position = at
	_fx_root().add_child(star)
	_fade_free(star, 2.0)

## ตัวที่โดน: สว่างวาบ + สั่น (ใช้ self_modulate ไม่ชนกับ modulate ที่ _process ใช้ทำตัวล้มให้จาง)
func _hit_flash(a) -> void:
	var n: Control = _hero_tex if a == hero else _foe_rects.get(a)
	if n == null:
		return
	if not n.has_meta("fx_base"):
		n.set_meta("fx_base", n.position)
	var base: Vector2 = n.get_meta("fx_base")
	var old = n.get_meta("fx_tw") if n.has_meta("fx_tw") else null   # get_meta(k, null) ยังพ่น error ใน 4.7
	if old != null and old.is_valid():
		old.kill()
	n.position = base
	n.self_modulate = Color(2.4, 2.4, 2.4)
	var tw := create_tween()
	n.set_meta("fx_tw", tw)
	tw.tween_property(n, "self_modulate", Color.WHITE, 0.25)
	tw.parallel().tween_method(func(t: float): n.position = base + Vector2(sin(t * 40.0) * 3.0 * (1.0 - t), 0), 0.0, 1.0, 0.3)
	tw.tween_callback(func(): n.position = base)

func _float_number(at: Vector2, text: String, col: Color) -> void:
	var l := _label(text, 13, col)
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 3)
	l.position = at + Vector2(-10, -30)
	l.position.y = maxf(l.position.y, NUMBER_TOP_Y)   # ตัวบนแถวลอย (ค้างคาว) → ตัวเลขไม่หลุดขึ้นไปทับแถบคิว/ป้ายท่า
	_fx_root().add_child(l)
	var tw := create_tween().set_parallel()
	tw.tween_property(l, "position:y", l.position.y - 16.0, 0.5).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "modulate:a", 0.0, 0.3).set_delay(0.8)
	tw.chain().tween_callback(l.queue_free)
