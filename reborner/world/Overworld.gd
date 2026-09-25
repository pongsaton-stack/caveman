# world/Overworld.gd — ฉากแผนที่หลัก (ขั้นที่ 4 สัปดาห์ 1-2)
# วิธีใช้: Node2D เปล่า + สคริปต์นี้ → บันทึกเป็น scenes/overworld.tscn → ตั้งเป็น Main Scene → F5
# ⚠ ไฟล์นี้ต้องไม่มี class_name — เป็นสคริปต์ติด Node ไม่ใช่คลาส
#
# ศึกเปิด BattleScreen ให้ผู้เล่นกดเอง — ใช้ Battle ตัวเดียวกับ Sim (สัปดาห์ 2)
extends Node2D

const TILE := 24
const MOVE_TIME := 0.12
const ENEMY_STEP := 0.9
const CHASE_RANGE := 4
const MAP_PATH := "res://data/map_ashfield.txt"
const SPRITE_DIR := "res://assets/sprites/hero"

# ชื่อไฟล์เฟรมตัวเอกต่อทิศ — ถ้าทิศไหนดูผิด แก้ชื่อไฟล์ตรงนี้ได้เลย
const HERO_ANIMS := {
	"down":  ["idle", "walk_cycle_idle"],
	"up":    ["walk_up_1", "walk_up_2"],
	"left":  ["walk_left"],
	"right": ["walk_right"],
}

# พาเลตต์องก์ 1 โทนจิบลิ (GDD 13) — องก์ถัดไปเปลี่ยนด้วย color grading ไม่ใช่วาดใหม่
const TILE_COLORS := {
	".": Color("8a7a5c"),
	",": Color("6b7d4a"),
	"#": Color("4a4038"),
	"~": Color("3d6a7a"),
	"R": Color("c9a24a"),
}

var by_id: Dictionary = {}
var encounters: Dictionary = {}
var chests: Dictionary = {}        # symbol -> row จาก chests.csv
var chest_nodes: Dictionary = {}   # "x,y" -> Node2D
var techs := TechDb.new()
var map: MapData
var ps := PlayerState.new()
var enemies: Array[WorldEnemy] = []
var rng := RandomNumberGenerator.new()

var hero_node: Node2D
var hero_sprite: AnimatedSprite2D
var hud: Label
var panel: ColorRect
var panel_label: Label

var busy := false
var enemy_clock := 0.0

func _ready() -> void:
	rng.randomize()
	randomize()
	by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	techs.load_from("res://data/techs.csv")
	for r in CsvDb.load_csv("res://data/encounters.csv"):
		encounters[str(r["symbol"])] = r
	for r in CsvDb.load_csv("res://data/chests.csv"):
		chests[str(r["symbol"])] = r
	map = MapData.load_map(MAP_PATH)
	if map == null or by_id.is_empty() or techs.all.is_empty():
		push_error("โหลดข้อมูลไม่ครบ — ตรวจโฟลเดอร์ data/")
		return
	var loaded := SaveGame.load_into(ps)
	if not loaded:
		ps.init_new(techs, map.start)
	# เซฟเก่าอาจชี้ไปช่องที่แผนที่เปลี่ยนไปแล้ว
	if not map.walkable(ps.cell):
		ps.cell = map.start
		ps.rest_cell = map.start
	_build_hero()
	_spawn_chests()
	_spawn_enemies()
	_build_ui()
	queue_redraw()
	_show("โหลดเกมที่บันทึกไว้" if loaded else "เริ่มการเดินทางใหม่", 1.2)

# ── วาดแผนที่ ─────────────────────────────────────────────────
func _draw() -> void:
	if map == null:
		return
	for y in map.h:
		for x in map.w:
			var t := map.tile(Vector2i(x, y))
			var col: Color = TILE_COLORS.get(t, TILE_COLORS["."])
			var rect := Rect2(x * TILE, y * TILE, TILE, TILE)
			draw_rect(rect, col)
			draw_rect(rect, Color(0, 0, 0, 0.08), false, 1.0)

func _cell_center(c: Vector2i) -> Vector2:
	return Vector2(c.x * TILE + TILE / 2.0, c.y * TILE + TILE / 2.0)

# ── ตัวเอก ────────────────────────────────────────────────────
func _build_hero() -> void:
	hero_node = Node2D.new()
	hero_node.z_index = 2
	add_child(hero_node)
	var frames := SpriteFrames.new()
	var found := 0
	for anim in HERO_ANIMS.keys():
		frames.add_animation(anim)
		frames.set_animation_speed(anim, 6.0)
		frames.set_animation_loop(anim, true)
		for fname in HERO_ANIMS[anim]:
			var p := "%s/%s.png" % [SPRITE_DIR, fname]
			if ResourceLoader.exists(p):
				frames.add_frame(anim, load(p))
				found += 1
	if found > 0:
		hero_sprite = AnimatedSprite2D.new()
		hero_sprite.sprite_frames = frames
		hero_sprite.offset = Vector2(0, -10)   # เท้า (y=46 ในเฟรม 48) ตรงขอบล่างช่อง
		hero_sprite.animation = "down"
		hero_node.add_child(hero_sprite)
	else:
		# ยังไม่มีอาร์ต — ใช้สี่เหลี่ยมแทน (GDD: อาร์ตคือสิ่งสุดท้ายที่ซื้อ)
		var box := ColorRect.new()
		box.color = Color("e8d9b5")
		box.size = Vector2(14, 20)
		box.position = Vector2(-7, -14)
		hero_node.add_child(box)
	hero_node.position = _cell_center(ps.cell)
	var cam := Camera2D.new()
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = map.w * TILE
	cam.limit_bottom = map.h * TILE
	cam.position_smoothing_enabled = true
	hero_node.add_child(cam)
	cam.make_current()

func _play_anim(dir: Vector2i) -> void:
	if hero_sprite == null:
		return
	var a := "down"
	if dir == Vector2i.UP:
		a = "up"
	elif dir == Vector2i.LEFT:
		a = "left"
	elif dir == Vector2i.RIGHT:
		a = "right"
	if hero_sprite.sprite_frames.get_frame_count(a) > 0:
		hero_sprite.play(a)

# ── ศัตรูบนแมพ ─────────────────────────────────────────────────
func _spawn_enemies() -> void:
	for e in enemies:
		e.queue_free()
	enemies.clear()
	for s in map.spawns:
		var sym := str(s["sym"])
		if chests.has(sym):
			continue
		# บอสที่ชนะแล้วไม่เกิดใหม่
		if ps.defeated.has(PlayerState.key_of(s["cell"])):
			continue
		if not encounters.has(sym):
			push_warning("สัญลักษณ์ '%s' ในแผนที่ไม่มีใน encounters.csv" % sym)
			continue
		var row: Dictionary = encounters[sym]
		var e := WorldEnemy.new()
		for mid in str(row["monster_ids"]).split("|", false):
			if by_id.has(mid):
				e.group.append(mid)
		if e.group.is_empty():
			e.free()
			continue
		e.cell = s["cell"]
		e.home = e.cell
		e.label_text = str(row["label"])
		e.is_boss = str(row.get("boss", 0)) == "1"
		for mid in e.group:
			e.tier = maxi(e.tier, int(by_id[mid]["tier"]))
		e.position = _cell_center(e.cell)
		add_child(e)
		e.set_danger(ps.prof)
		enemies.append(e)

# ── หีบสมบัติ ─────────────────────────────────────────────────
func _spawn_chests() -> void:
	for k in chest_nodes.keys():
		chest_nodes[k]["node"].queue_free()
	chest_nodes.clear()
	for s in map.spawns:
		var sym := str(s["sym"])
		if not chests.has(sym):
			continue
		var key := PlayerState.key_of(s["cell"])
		if ps.opened.has(key):
			continue
		var box := ColorRect.new()
		box.color = Color("a0602a")
		box.size = Vector2(14, 10)
		box.position = _cell_center(s["cell"]) - Vector2(7, 5)
		add_child(box)
		chest_nodes[key] = {"node": box, "row": chests[sym]}

func _open_chest(key: String) -> void:
	var entry: Dictionary = chest_nodes[key]
	var row: Dictionary = entry["row"]
	entry["node"].queue_free()
	chest_nodes.erase(key)
	ps.opened.append(key)
	var base := int(row["weapon_base"])
	var label := str(row["label"])
	if base > ps.weapon_base:
		var old := ps.weapon_name
		ps.weapon_base = base
		ps.weapon_name = label
		_show("🎁 ได้ %s! (%s → %s · ค่าอาวุธ %d)" % [label, old, label, base], 2.0)
	else:
		ps.gold += 50
		_show("🎁 %s — อาวุธที่มีดีกว่าแล้ว ขายได้ +50 เงิน" % label, 1.6)
	SaveGame.save(ps)

func _enemy_at(c: Vector2i) -> WorldEnemy:
	for e in enemies:
		if e.cell == c:
			return e
	return null

func _enemies_step() -> void:
	for e in enemies:
		if e.is_boss:
			continue
		var dir := _enemy_dir(e)
		if dir == Vector2i.ZERO:
			continue
		e.facing = dir
		e.queue_redraw()
		var nxt := e.cell + dir
		if nxt == ps.cell:
			# ศัตรูเป็นฝ่ายเข้าหา = ถูกลอบตี (GDD 3.10)
			_encounter(e, "foe")
			return
		if not map.walkable(nxt) or map.tile(nxt) == "R" or _enemy_at(nxt) != null or not e.within_leash(nxt):
			continue
		e.cell = nxt
		var tw := create_tween()
		tw.tween_property(e, "position", _cell_center(nxt), 0.3)

func _enemy_dir(e: WorldEnemy) -> Vector2i:
	var d := ps.cell - e.cell
	# ตัวที่ตบทิ้งได้ไม่ไล่ — ไม่มีเหตุผลจะเสียเวลาผู้เล่น
	var chase := not Formulas.is_swat(e.tier, ps.prof) and absi(d.x) + absi(d.y) <= CHASE_RANGE
	if chase and rng.randf() < 0.6:
		if absi(d.x) > absi(d.y):
			return Vector2i(signi(d.x), 0)
		return Vector2i(0, signi(d.y))
	if rng.randf() < 0.5:
		var dirs := [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]
		return dirs[rng.randi() % dirs.size()]
	return Vector2i.ZERO

func _refresh_enemy_colors() -> void:
	for e in enemies:
		e.set_danger(ps.prof)

# ── อินพุต ────────────────────────────────────────────────────
func _process(delta: float) -> void:
	if busy or map == null:
		return
	enemy_clock += delta
	if enemy_clock >= ENEMY_STEP:
		enemy_clock = 0.0
		_enemies_step()
		if busy:
			return
	var dir := Vector2i.ZERO
	if Input.is_action_pressed("ui_up"):
		dir = Vector2i.UP
	elif Input.is_action_pressed("ui_down"):
		dir = Vector2i.DOWN
	elif Input.is_action_pressed("ui_left"):
		dir = Vector2i.LEFT
	elif Input.is_action_pressed("ui_right"):
		dir = Vector2i.RIGHT
	if dir != Vector2i.ZERO:
		_try_move(dir)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F9:
		SaveGame.clear()
		_show("ลบเซฟแล้ว — ปิดแล้วเปิดใหม่เพื่อเริ่มต้น", 1.5)

func _try_move(dir: Vector2i) -> void:
	_play_anim(dir)
	var nxt := ps.cell + dir
	if not map.walkable(nxt):
		return
	var e := _enemy_at(nxt)
	if e != null:
		# เดินชนจากด้านหลัง (ทิศเดียวกับที่มันหัน) = ลอบตีสำเร็จ
		var amb := "ally" if dir == e.facing else ""
		_encounter(e, amb)
		return
	busy = true
	ps.cell = nxt
	var tw := create_tween()
	tw.tween_property(hero_node, "position", _cell_center(nxt), MOVE_TIME)
	tw.finished.connect(_on_move_done)

func _on_move_done() -> void:
	busy = false
	if hero_sprite != null:
		hero_sprite.stop()
		hero_sprite.frame = 0
	var key := PlayerState.key_of(ps.cell)
	if chest_nodes.has(key):
		_open_chest(key)
	elif map.tile(ps.cell) == "R":
		_rest()

func _rest() -> void:
	ps.rest()
	var ok := SaveGame.save(ps)
	_spawn_enemies()
	_show("จุดพัก — HP/SP เต็ม · ศัตรูฟื้นคืน · %s" % ("บันทึกเกมแล้ว" if ok else "บันทึกไม่สำเร็จ!"), 1.6)

# ── การต่อสู้ ─────────────────────────────────────────────────
func _make_party() -> Array[Actor]:
	var out: Array[Actor] = []
	for spec in [{"n": "หนอนหินร่วมทาง", "id": "M03"}, {"n": "ค้างคาวร่วมทาง", "id": "M06"}]:
		if not by_id.has(spec["id"]):
			continue
		var m := Actor.from_csv(by_id[spec["id"]])
		m.name = str(spec["n"])
		m.side = "ally"
		m.lp = 3
		m.loyalty = 3
		m.max_hp = int(m.max_hp * 1.6)
		m.hp = m.max_hp
		out.append(m)
	return out

func _encounter(e: WorldEnemy, ambush: String) -> void:
	busy = true
	var rows: Array = []
	for mid in e.group:
		rows.append(by_id[mid])

	# ตบทิ้งบนแมพ — ทุกตัวในกลุ่มอ่อนกว่าเกณฑ์ ไม่เข้าฉากต่อสู้ (GDD 3.9)
	# บอสไม่ถูกตบทิ้งเด็ดขาด — ศึกบอสคือเนื้อเรื่อง ไม่ใช่มอนขยะ
	var all_swat := not e.is_boss
	for r in rows:
		if not Formulas.is_swat(int(r["tier"]), ps.prof):
			all_swat = false
	if all_swat:
		var coins := 2 * rows.size()
		ps.gold += coins
		_remove_enemy(e)
		_show("✋ ตบทิ้ง %s — ไม่เข้าฉากต่อสู้ (+%d เงิน)" % [e.label_text, coins], 1.2)
		return

	var b := Battle.new()
	b.techs = techs
	b.ambush = ambush
	var hero := ps.make_hero()
	b.actors.append(hero)
	for m in _make_party():
		b.actors.append(m)
	var max_tier := 0
	for r in rows:
		var f := Actor.from_csv(r)
		b.actors.append(f)
		max_tier = maxi(max_tier, f.tier)
	var prof_before := ps.prof
	var screen := BattleScreen.new()
	var amb_txt := {"ally": " · ลอบตีสำเร็จ", "foe": " · ถูกลอบตี"}
	screen.setup(b, "%s%s%s" % ["บอส: " if e.is_boss else "", e.label_text, amb_txt.get(ambush, "")])
	add_child(screen)
	var res: Dictionary = await screen.finished

	var lines: Array[String] = []
	if ambush == "ally":
		lines.append("◆ ลอบตีสำเร็จ — ฝ่ายเราได้ทำก่อน")
	elif ambush == "foe":
		lines.append("◆ ถูกลอบตี — ศัตรูได้ทำก่อน")
	if res["won"]:
		ps.absorb(hero)
		ps.prof += Formulas.prof_gain(max_tier, ps.prof)
		var loot := max_tier * rows.size()
		ps.gold += loot
		ps.sp = mini(ps.max_sp(), ps.sp + int(ps.max_sp() * Formulas.SP_RESTORE))
		if e.is_boss:
			ps.defeated.append(PlayerState.key_of(e.home))
			SaveGame.save(ps)
		_remove_enemy(e)
		lines.append("%sชนะ %s · %.0f AV" % ["★ ชนะบอส! " if e.is_boss else "", e.label_text, res["time"]])
		lines.append("ความชำนาญ %d → %d · เงิน +%d · HP %d/%d" % [prof_before, ps.prof, loot, ps.hp, ps.max_hp()])
		for g in res["glimmer_log"]:
			lines.append("★ ประกาย! เรียนรู้ %s" % g)
		if int(res["combos"]) > 0 or int(res["interrupts"]) > 0:
			lines.append("คอมโบ %d · ขัดจังหวะ %d" % [res["combos"], res["interrupts"]])
	else:
		# ตัวเอกล้ม = แพ้ทันที เสียเงินครึ่งหนึ่ง กลับจุดพักล่าสุด (GDD 3.6)
		var lost := int(ps.gold / 2.0)
		ps.gold -= lost
		ps.cell = ps.rest_cell
		ps.rest()
		hero_node.position = _cell_center(ps.cell)
		lines.append("แพ้ %s — เสียเงิน %d · กลับจุดพัก" % [e.label_text, lost])
	_refresh_enemy_colors()
	_show("\n".join(lines), 2.8)

func _remove_enemy(e: WorldEnemy) -> void:
	enemies.erase(e)
	e.queue_free()

# ── UI ────────────────────────────────────────────────────────
func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(4, 2)
	_style(hud, 8)
	layer.add_child(hud)
	var hint := Label.new()
	hint.text = "ลูกศร เดิน · เข้าหาด้านหลังศัตรู = ลอบตี · ช่องสีทอง = จุดพัก/บันทึก · ต่อสู้: ลูกศรเลือก Enter ยืนยัน · F9 ลบเซฟ"
	hint.position = Vector2(4, 202)
	_style(hint, 6)
	layer.add_child(hint)
	panel = ColorRect.new()
	panel.color = Color(0.05, 0.06, 0.08, 0.85)
	panel.position = Vector2(32, 64)
	panel.size = Vector2(320, 88)
	panel.visible = false
	layer.add_child(panel)
	panel_label = Label.new()
	panel_label.position = Vector2(8, 6)
	panel_label.size = Vector2(304, 76)
	panel_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_style(panel_label, 8)
	panel.add_child(panel_label)
	_update_hud()

func _style(l: Label, size: int) -> void:
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 2)

func _update_hud() -> void:
	if hud == null:
		return
	hud.text = "ความชำนาญ %d · %s (%d) · เงิน %d · HP %d/%d · SP %d/%d · ท่า %d" % [
		ps.prof, ps.weapon_name, ps.weapon_base, ps.gold, ps.hp, ps.max_hp(), ps.sp, ps.max_sp(), ps.learned.size()]

func _show(msg: String, secs: float) -> void:
	busy = true
	_update_hud()
	if panel == null:
		busy = false
		return
	panel_label.text = msg
	panel.visible = true
	get_tree().create_timer(secs).timeout.connect(_hide_panel, CONNECT_ONE_SHOT)

func _hide_panel() -> void:
	panel.visible = false
	busy = false
	_update_hud()
