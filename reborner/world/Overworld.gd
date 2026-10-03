# world/Overworld.gd — ฉากแผนที่หลัก (ขั้นที่ 4 สัปดาห์ 1-2)
# วิธีใช้: Node2D เปล่า + สคริปต์นี้ → บันทึกเป็น scenes/overworld.tscn → ตั้งเป็น Main Scene → F5
# ⚠ ไฟล์นี้ต้องไม่มี class_name — เป็นสคริปต์ติด Node ไม่ใช่คลาส
#
# ศึกเปิด BattleScreen ให้ผู้เล่นกดเอง — ใช้ Battle ตัวเดียวกับ Sim (สัปดาห์ 2)
# มอนร่วมทีมมาจาก ps.party (LP · ความเชื่อใจ) · Esc = เมนู · ช่อง S = ร้านค้า (สัปดาห์ 3)
extends Node2D

const TILE := 24
const MOVE_TIME := 0.15
const CAM_TOP_PAD := 40
# ท่าเดิน: ก้าว 1 ครั้ง (2 เฟรม) ต่อ 1 ช่อง → รอบละ 2 ช่อง · เล่นต่อเนื่องข้ามช่อง หยุดเมื่อปล่อยปุ่ม
const WALK_FPS := 2.0 / MOVE_TIME
const ENEMY_STEP := 0.9
const CHASE_RANGE := 4
const MAP_PATH := "res://data/map_ashfield.txt"
const SPRITE_DIR := "res://assets/sprites/rion_lastlight_draft"

# ชื่อไฟล์เฟรมตัวเอกต่อทิศ — ถ้าทิศไหนดูผิด แก้ชื่อไฟล์ตรงนี้ได้เลย
# Rion ตามต้นแบบ Last Light (ตัดจาก docs/art-bible/lastlight_01.png · หมวกน้ำเงิน) 64x64 · ร่าง รอ kwan อนุมัติ
# เดิน 4 เฟรม/ทิศ (w0 = ยืน · w1 ก้าว · w2 ผ่าน · w3 ก้าวอีกข้าง) สร้างจาก tools/sprites/rion_anim.py · หมาใช้ชุดเดียวกัน
const HERO_ANIMS := {
	"down":  ["south_w0", "south_w1", "south_w2", "south_w3"],
	"up":    ["north_w0", "north_w1", "north_w2", "north_w3"],
	"left":  ["west_w0", "west_w1", "west_w2", "west_w3"],
	"right": ["east_w0", "east_w1", "east_w2", "east_w3"],
}

# พาเลตต์องก์ 1 โทนจิบลิ (GDD 13) — องก์ถัดไปเปลี่ยนด้วย color grading ไม่ใช่วาดใหม่
const TILE_COLORS := {
	".": Color("8a7a5c"),
	",": Color("6b7d4a"),
	"#": Color("4a4038"),
	"~": Color("3d6a7a"),
	"R": Color("c9a24a"),
	"S": Color("5c8a7a"),
}

var by_id: Dictionary = {}
var encounters: Dictionary = {}
var chests: Dictionary = {}        # symbol -> row จาก chests.csv
var chest_nodes: Dictionary = {}   # "x,y" -> Node2D
var slot_rows: Array = []          # data/party_slots.csv
var companion_rows: Array = []     # data/companions.csv
var item_rows: Array = []          # data/items.csv
var recruit_rows := {}             # data/recruits.csv — มอนที่รับเข้าทีมได้ (GDD 5.2/5.3)
var techs := TechDb.new()
var map: MapData
var ps := PlayerState.new()
var enemies: Array[WorldEnemy] = []
var rng := RandomNumberGenerator.new()

var hero_node: Node2D
var hero_sprite: AnimatedSprite2D
# หมาคู่หู (Last Light) เดินตามหลังหนึ่งช่อง — ประดับเท่านั้น ไม่ชนศัตรู ไม่เข้าศึก
const DOG_DIR := "res://assets/sprites/dog_lastlight_draft"
var dog_node: Node2D
var dog_sprite: AnimatedSprite2D
var _moving := false   # กำลังเลื่อนช่อง (busy จากการเดิน ไม่ใช่จากเมนู)
var dog_cell := Vector2i.ZERO
var hud: Label
var hud2: Label
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
	slot_rows = CsvDb.load_csv("res://data/party_slots.csv")
	companion_rows = CsvDb.load_csv("res://data/companions.csv")
	item_rows = CsvDb.load_csv("res://data/items.csv")
	recruit_rows = CsvDb.index_by(CsvDb.load_csv("res://data/recruits.csv"), "monster_id")
	map = MapData.load_map(MAP_PATH)
	if map == null or by_id.is_empty() or techs.all.is_empty():
		push_error("โหลดข้อมูลไม่ครบ — ตรวจโฟลเดอร์ data/")
		return
	var loaded := SaveGame.load_into(ps)
	if not loaded:
		ps.init_new(techs, map.start)
	# เซฟเก่า (v1) ไม่มีปาร์ตี้/ร้าน — ตั้งให้ครั้งเดียว
	ps.seed_party(companion_rows)
	if ps.shop_stock.is_empty():
		for r in item_rows:
			ps.shop_stock[str(r["item_id"])] = int(r["stock"])
	# เซฟเก่าอาจชี้ไปช่องที่แผนที่เปลี่ยนไปแล้ว
	if not map.walkable(ps.cell):
		ps.cell = map.start
		ps.rest_cell = map.start
	_build_hero()
	_build_dog()
	_build_drops()
	_spawn_chests()
	_label_shops()
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
		frames.set_animation_speed(anim, WALK_FPS)
		frames.set_animation_loop(anim, true)
		for fname in HERO_ANIMS[anim]:
			var p := "%s/%s.png" % [SPRITE_DIR, fname]
			if ResourceLoader.exists(p):
				frames.add_frame(anim, load(p))
				found += 1
	if found > 0:
		hero_sprite = AnimatedSprite2D.new()
		hero_sprite.sprite_frames = frames
		hero_sprite.offset = Vector2(0, -18)   # เท้า (y=62 ในเฟรม 64) ตรงขอบล่างช่อง
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
	# ตัวเอกสูง 64px ยื่นเหนือช่องราว 38px → ยืนแถวบนแล้วหัวหลุดจอ · ให้กล้องเลื่อนเหนือแมพได้ แล้วระบายส่วนนั้นเป็นสีกำแพง
	cam.limit_top = -CAM_TOP_PAD
	RenderingServer.set_default_clear_color(TILE_COLORS["#"])
	cam.limit_right = map.w * TILE
	cam.limit_bottom = map.h * TILE
	cam.position_smoothing_enabled = true
	hero_node.add_child(cam)
	cam.make_current()

## ── ของดรอป (กฎ UX ข้อ 3 ของ kwan) ──
## มอนตาย → ไอคอนตรงจุดทันที · เดินทับเก็บ · ของ/โอกาสจากคอลัมน์ drop / drop_rate
var drop_nodes := {}   # key_of(ช่อง) -> Label

func _drop_loot(e: WorldEnemy, rows: Array) -> void:
	var got: Array = []
	for r in rows:
		var name := str(r.get("drop", ""))
		if name != "" and rng.randf() * 100.0 < float(r.get("drop_rate", 0)):
			got.append(name)
	if got.is_empty():
		return
	var key := PlayerState.key_of(e.cell)
	var arr: Array = ps.ground_drops.get(key, [])
	arr.append_array(got)
	ps.ground_drops[key] = arr
	_place_drop_icon(e.cell)

func _place_drop_icon(c: Vector2i) -> void:
	var key := PlayerState.key_of(c)
	if drop_nodes.has(key):
		return
	var l := Label.new()
	l.text = "🎁"
	_style(l, 10)
	l.position = Vector2(c.x * TILE + 4, c.y * TILE + 2)
	l.z_index = 1
	add_child(l)
	drop_nodes[key] = l

func _build_drops() -> void:
	for key in ps.ground_drops.keys():
		var parts := str(key).split(",")
		if parts.size() == 2:
			_place_drop_icon(Vector2i(int(parts[0]), int(parts[1])))

func _pick_up_drops() -> bool:
	var key := PlayerState.key_of(ps.cell)
	if not ps.ground_drops.has(key):
		return false
	var names: Array = ps.ground_drops[key]
	for n in names:
		ps.materials[str(n)] = int(ps.materials.get(str(n), 0)) + 1
	ps.ground_drops.erase(key)
	if drop_nodes.has(key):
		drop_nodes[key].queue_free()
		drop_nodes.erase(key)
	SaveGame.save(ps)
	_show("🎁 เก็บ " + " · ".join(names), 1.4)
	return true

## ชนะแล้วเข้าใจท่าเด่นครบ → ถามทีละสายพันธุ์ว่ารับเข้าทีมไหม (GDD 5.2)
func _offer_recruits(ids: Array) -> Array[String]:
	var notes: Array[String] = []
	for id in ids:
		if not recruit_rows.has(str(id)) or not by_id.has(str(id)):
			continue
		var row: Dictionary = recruit_rows[str(id)]
		var slots := _monster_slots()
		var used := 0
		for m in ps.active_members(slots):
			used += PlayerState.slot_cost(m)
		var screen := RecruitScreen.new()
		screen.setup(str(row["name"]), str(by_id[str(id)]["signature_tech"]), int(row["slots"]), used + int(row["slots"]) > slots)
		add_child(screen)
		var ok: bool = await screen.decided
		if ok:
			var nm := ps.recruit(row)
			var bench := not ps.active_members(slots).has(ps._member(nm))
			notes.append("◇ %s เข้าทีมแล้ว%s" % [nm, " (สำรอง)" if bench else ""])
	return notes

func _build_dog() -> void:
	var frames := SpriteFrames.new()
	var found := 0
	for anim in ["down", "up", "left", "right"]:
		var base: String = {"down": "south", "up": "north", "left": "west", "right": "east"}[anim]
		frames.add_animation(anim)
		frames.set_animation_speed(anim, WALK_FPS)
		frames.set_animation_loop(anim, true)
		for fname in ["%s_w0" % base, "%s_w1" % base, "%s_w2" % base, "%s_w3" % base]:
			var p := "%s/%s.png" % [DOG_DIR, fname]
			if ResourceLoader.exists(p):
				frames.add_frame(anim, load(p))
				found += 1
	if found == 0:
		return
	dog_node = Node2D.new()
	dog_node.z_index = 1
	add_child(dog_node)
	dog_sprite = AnimatedSprite2D.new()
	dog_sprite.sprite_frames = frames
	dog_sprite.offset = Vector2(0, -4)   # เท้า (y=32 ในเฟรม 34) ตรงขอบล่างช่อง
	dog_sprite.animation = "down"
	dog_node.add_child(dog_sprite)
	_dog_snap()

## วางหมาที่ช่องตัวเอก (เริ่มเกม · โหลดเซฟ · แพ้แล้วกลับจุดพัก)
func _dog_snap() -> void:
	if dog_node == null:
		return
	# ยืนข้างตัวเอก (ช่องเดินได้ช่องแรก) — ไม่ทับกันจนหมาหายหลังตัวเอก
	dog_cell = ps.cell
	# ข้างซ้าย/ขวาก่อน — ช่องบนโดนตัวเอก (สูง 64px ≈ 2.6 ช่อง) บังมิด
	for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.UP]:
		var c: Vector2i = ps.cell + d
		if map.walkable(c) and _enemy_at(c) == null:
			dog_cell = c
			break
	dog_node.position = _cell_center(dog_cell)
	dog_sprite.offset.x = _dog_side(dog_cell, ps.cell)

## หมาอยู่แนวตั้งเดียวกับตัวเอก → เยื้องขวาให้โผล่ข้างตัว (ไม่หายหลังตัวเอก/ไม่บังขา)
const DOG_SIDE_PX := 16.0
func _dog_side(dog_c: Vector2i, hero_c: Vector2i) -> float:
	return DOG_SIDE_PX if dog_c.x == hero_c.x else 0.0

## หมาเดินไปช่องที่ตัวเอกเพิ่งออกมา
func _dog_follow(to: Vector2i) -> void:
	if dog_node == null or to == dog_cell:
		return
	var d := to - dog_cell
	var a := "down"
	if d.y < 0:
		a = "up"
	elif d.x < 0:
		a = "left"
	elif d.x > 0:
		a = "right"
	dog_cell = to
	_walk(dog_sprite, a, true)
	var tw := create_tween().set_parallel()
	tw.tween_property(dog_node, "position", _cell_center(to), MOVE_TIME)
	tw.tween_property(dog_sprite, "offset:x", _dog_side(to, ps.cell), MOVE_TIME)

## เล่นท่าเดินต่อจากเฟรมเดิม (ไม่รีเซ็ตทุกช่อง) · เริ่มจากยืน → เข้าเฟรมก้าวทันที · moving=false = หันหน้าเฉยๆ
func _walk(spr: AnimatedSprite2D, a: String, moving: bool) -> void:
	if spr == null or spr.sprite_frames.get_frame_count(a) == 0:
		return
	if not moving:
		spr.stop()
		spr.animation = a
		spr.frame = 0
		return
	if spr.is_playing():
		if spr.animation != a:
			var f := spr.frame
			spr.play(a)
			spr.frame = f
		return
	spr.play(a)
	spr.frame = 1

func _stop_walk() -> void:
	for spr in [hero_sprite, dog_sprite]:
		if spr != null and spr.is_playing():
			spr.stop()
			spr.frame = 0

func _play_anim(dir: Vector2i, moving := true) -> void:
	if hero_sprite == null:
		return
	var a := "down"
	if dir == Vector2i.UP:
		a = "up"
	elif dir == Vector2i.LEFT:
		a = "left"
	elif dir == Vector2i.RIGHT:
		a = "right"
	_walk(hero_sprite, a, moving)

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
		e.load_sprite()
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
		e.set_facing(dir)
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
	var chase := not Formulas.map_swat(e.tier, ps.prof) and absi(d.x) + absi(d.y) <= CHASE_RANGE
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
## ใครอยู่ต่ำกว่าบนจอวาดทีหลัง (บังตัวที่อยู่สูงกว่า) — เดิม z คงที่: หมาโดน Rion ทับเสมอแม้ยืนอยู่ช่องล่าง
func _y_sort() -> void:
	for n in [hero_node, dog_node]:
		if n != null:
			n.z_index = 2 + int(n.position.y)
	for e in enemies:
		if is_instance_valid(e):
			e.z_index = 2 + int(e.position.y)

func _process(delta: float) -> void:
	_y_sort()
	if busy or map == null:
		if not _moving:
			_stop_walk()   # เมนู/หีบ/ศึก/ร้าน = ยืนนิ่ง
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
	else:
		_stop_walk()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F9:
		SaveGame.clear()
		_show("ลบเซฟแล้ว — ปิดแล้วเปิดใหม่เพื่อเริ่มต้น", 1.5)
	elif event.is_action_pressed("ui_cancel") and not busy:
		get_viewport().set_input_as_handled()
		_open_menu()

# ── เมนู / ร้านค้า ─────────────────────────────────────────────
func _open_menu() -> void:
	busy = true
	var m := MenuScreen.new()
	m.setup(ps, techs, item_rows, _monster_slots())
	m.closed.connect(_on_screen_closed)
	add_child(m)

func _open_shop() -> void:
	busy = true
	var s := ShopScreen.new()
	s.setup(ps, item_rows)
	s.closed.connect(_on_screen_closed)
	add_child(s)

func _on_screen_closed() -> void:
	SaveGame.save(ps)
	busy = false
	_update_hud()

func _label_shops() -> void:
	for y in map.h:
		for x in map.w:
			if map.tile(Vector2i(x, y)) == "S":
				var l := Label.new()
				l.text = "ร้าน"
				l.add_theme_font_size_override("font_size", 6)
				l.add_theme_color_override("font_outline_color", Color.BLACK)
				l.add_theme_constant_override("outline_size", 2)
				l.position = Vector2(x * TILE + 2, y * TILE + 6)
				l.z_index = 1
				add_child(l)

func _try_move(dir: Vector2i) -> void:
	var nxt := ps.cell + dir
	if not map.walkable(nxt):
		_play_anim(dir, false)   # ชนกำแพง = หันหน้า ไม่ย่ำอยู่กับที่
		_stop_walk()
		return
	var e := _enemy_at(nxt)
	_play_anim(dir, e == null)
	if e != null:
		_stop_walk()
		# เดินชนจากด้านหลัง (ทิศเดียวกับที่มันหัน) = ลอบตีสำเร็จ
		var amb := "ally" if dir == e.facing else ""
		_encounter(e, amb)
		return
	busy = true
	_moving = true
	var prev := ps.cell
	ps.cell = nxt
	_dog_follow(prev)
	var tw := create_tween()
	tw.tween_property(hero_node, "position", _cell_center(nxt), MOVE_TIME)
	tw.finished.connect(_on_move_done)

func _on_move_done() -> void:
	busy = false
	_moving = false
	if _pick_up_drops():
		return
	var key := PlayerState.key_of(ps.cell)
	if chest_nodes.has(key):
		_open_chest(key)
	elif map.tile(ps.cell) == "R":
		_rest()
	elif map.tile(ps.cell) == "S":
		_open_shop()

func _rest() -> void:
	var lp_msg := ps.rest()
	var ok := SaveGame.save(ps)
	_spawn_enemies()
	var msg := "จุดพัก — HP/SP เต็ม · ศัตรูฟื้นคืน · %s" % ("บันทึกเกมแล้ว" if ok else "บันทึกไม่สำเร็จ!")
	if lp_msg != "":
		msg += "\n" + lp_msg
	_show(msg, 1.8)

# ── การต่อสู้ ─────────────────────────────────────────────────
func _monster_slots() -> int:
	return PlayerState.monster_slots_for(ps.ec, slot_rows)

func _encounter(e: WorldEnemy, ambush: String) -> void:
	busy = true
	_stop_walk()
	var rows: Array = []
	for mid in e.group:
		rows.append(by_id[mid])

	# ตบทิ้งบนแมพ — ทุกตัวในกลุ่มอ่อนกว่าเกณฑ์ ไม่เข้าฉากต่อสู้ (GDD 3.9)
	# บอสไม่ถูกตบทิ้งเด็ดขาด — ศึกบอสคือเนื้อเรื่อง ไม่ใช่มอนขยะ
	var all_swat := not e.is_boss
	for r in rows:
		if not Formulas.map_swat(int(r["tier"]), ps.prof):
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
	var comps := ps.make_companions(by_id, _monster_slots())
	for m in comps:
		b.actors.append(m)
	var max_tier := 0
	for r in rows:
		var f := Actor.from_csv(r)
		b.actors.append(f)
		max_tier = maxi(max_tier, f.tier)
	var prof_before := ps.prof
	var screen := BattleScreen.new()
	var amb_txt := {"ally": " · ลอบตีสำเร็จ", "foe": " · ถูกลอบตี"}
	screen.setup(b, "%s%s%s" % ["บอส: " if e.is_boss else "", e.label_text, amb_txt.get(ambush, "")], ps.auto_battle)
	add_child(screen)
	var res: Dictionary = await screen.finished
	ps.auto_battle = bool(res.get("auto", ps.auto_battle))

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
			# จบบอส = จบเควสหลัก 1 เควส (STORY_DRAFT ฉากที่ 7) · EC เพิ่มจากตรงนี้จนกว่าจะมีระบบเควส
			ps.ec += 1
			lines.append("…%s  (EC %d)" % ["หนึ่ง" if ps.ec == 1 else str(ps.ec), ps.ec])
		_drop_loot(e, rows)
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
		_dog_snap()
		lines.append("แพ้ %s — เสียเงิน %d · กลับจุดพัก" % [e.label_text, lost])
	for n in ps.after_battle(comps):
		lines.append(n)
	if res["won"]:
		for n in await _offer_recruits(res.get("understood", [])):
			lines.append(n)
	SaveGame.save(ps)
	_refresh_enemy_colors()
	_show("\n".join(lines), 2.8 + 0.4 * maxi(0, lines.size() - 3))

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
	hud2 = Label.new()
	hud2.position = Vector2(4, 13)
	_style(hud2, 6)
	layer.add_child(hud2)
	var hint := Label.new()
	hint.text = "ลูกศร เดิน · Esc เมนู · ช่องทอง = จุดพัก · ช่องเขียวอมฟ้า = ร้าน · ต่อสู้: Enter ยืนยัน · F9 ลบเซฟ"
	hint.position = Vector2(4, 202)
	_style(hint, 6)
	layer.add_child(hint)
	panel = ColorRect.new()
	panel.color = Color(0.05, 0.06, 0.08, 0.85)
	panel.position = Vector2(32, 84)
	panel.size = Vector2(320, 44)   # 2 บรรทัด (กฎ UX ข้อ 5)
	panel.visible = false
	layer.add_child(panel)
	panel_label = Label.new()
	panel_label.position = Vector2(8, 5)
	panel_label.size = Vector2(304, 34)
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
	if hud2 != null:
		var parts: Array[String] = []
		for m in ps.party:
			parts.append("%s %s" % [m["name"], UiKit.lp_dots(int(m["lp"]))])
		hud2.text = "EC %d · มอน: %s" % [ps.ec, " · ".join(parts) if not parts.is_empty() else "ไม่มี"]

## กฎ UX ข้อ 5 ของ kwan: กล่องข้อความละไม่เกิน 2 บรรทัด — ข้อความยาวแบ่งเป็นหน้าละ 2 บรรทัด เล่นต่อกันเอง
const SHOW_LINES := 2
const SHOW_PAGE_MIN := 1.2
var _pages: Array[String] = []
var _page_secs := 0.0

func _show(msg: String, secs: float) -> void:
	busy = true
	_update_hud()
	if panel == null:
		busy = false
		return
	var lines := msg.split("\n")
	var pages: Array[String] = []
	for i in range(0, lines.size(), SHOW_LINES):
		pages.append("\n".join(lines.slice(i, i + SHOW_LINES)))
	_pages.clear()
	_pages.append_array(pages)
	_page_secs = maxf(SHOW_PAGE_MIN, secs / float(pages.size()))
	_next_page()

func _next_page() -> void:
	panel_label.text = _pages.pop_front()
	panel.visible = true
	get_tree().create_timer(_page_secs).timeout.connect(_hide_panel, CONNECT_ONE_SHOT)

func _hide_panel() -> void:
	if not _pages.is_empty():
		_next_page()
		return
	panel.visible = false
	busy = false
	_update_hud()
