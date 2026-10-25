extends Node2D
## ฐานฉากต่อสู้ในห้องทดลอง Godot (ใช้ร่วมทุกท่า) — ท่าแต่ละท่า = สคริปต์ที่ extends ไฟล์นี้ แล้วเขียนเฉพาะส่วนของท่า:
##   end_frame() · hit_frame() (หยุดภาพ) · setup() สร้างโหนดของท่า · frame(f, F, fresh) ทุกเฟรมจอ · sounds(F) ทุกเฟรมเต็มใหม่ · caption()
## ฐานมีให้: ฉาก frost_volcano + บรรยากาศ (หยุดได้) · Rion ผืน 120x112 เท้าแถว 108 · มอน 5 ตัวแรก + ขอบเนื้อ · กล้องสั่น · หยุดภาพ
##   บับเบิลชื่อท่า · ตัวเลขดาเมจ · คำเสียง · ดาว/ประกาย/ฝุ่น/ไอ · เสียงสังเคราะห์สูตรเดียวกับหน้าเว็บ (บัส LabSfx มีเสียงก้อง + คอมเพรสเซอร์) · เมนูเลือกมอน
## ไม่ใช่ของในเกม (tests/ ไม่ถูก export กับเกม) · ห้ามมี class_name (กฎ 2) · ภาพร่างอยู่ในโฟลเดอร์ .gdignore → โหลดตรงจากไฟล์ (หน้าเว็บ lab คัดลอกไปที่เดิมแบบ import ได้)
## อัดวิดีโอ: xvfb-run -a <godot> --path . --rendering-driver opengl3 --write-movie <dir>/f.png --fixed-fps 60 res://tests/lab/<ท่า>.tscn -- --foe=M01
##   (ระบุ --foe = โหมดอัด: เล่นทันทีแล้วปิดเอง · ได้ภาพ 1152x648 + f.wav)

const W := 300
const H := 168
const G := 158
const SEC := 0.06
const HITSTOP := 0.1
const PX := "res://assets/sprites/pixellab_draft/px_set/"
const MPX := "res://assets/sprites/monsters_px_draft/"
const BG := "res://docs/art-bible/pixellab_test/bg_frost_volcano.jpg"
const FOES := ["M01", "M03", "M06", "M15", "B1"]   # มอน 5 ตัวแรกของหน้าฉากต่อสู้ (kwan 25 ต.ค. "ลองกับมอน 5 ตัวแรกก่อนพอ")
const SR := 32000

const FX_SHADER := """
shader_type canvas_item;
uniform vec4 tint : source_color = vec4(1.0);
uniform float amount = 0.0;
uniform float dissolve = 0.0;
float h(vec2 p) { return fract(sin(dot(floor(p), vec2(12.9898, 78.233))) * 43758.5453); }
void fragment() {
	COLOR.rgb = mix(COLOR.rgb, tint.rgb, amount);
	if (dissolve > 0.0) {
		float n = h(UV / TEXTURE_PIXEL_SIZE);
		if (n < dissolve) COLOR.a = 0.0;
		else if (n < dissolve + 0.12) COLOR.rgb = vec3(1.0, 0.86, 0.55);
	}
}
"""

var foe := "M01"
var recording := false
var playing := false
var t := 0.0
var hold := 0.0
var hit_done := false
var last_fi := -1
var tex := {}
var mon_img: Image
var mw := 48
var mh := 48
var mx0 := 0
var my := 0
var mcx := 0.0
var top0 := 0
var bh := 0
var home := W - 40
var mon_name := ""
var hp := 0
var body := ""
var dmg := 0
var aff := 0
var kill := false

var cam: Camera2D
var dim: ColorRect
var mon: Sprite2D
var snow: CPUParticles2D
var embers: CPUParticles2D
var lamp: Sprite2D
var puff_p: CPUParticles2D
var dust: CPUParticles2D
var sparks: CPUParticles2D
var star: Node2D
var star_r := 0.0
var flash_spr: Sprite2D
var burst_f := -100
var burst_pos := Vector2.ZERO
var ui: CanvasLayer
var lbl_word: Label
var lbl_dmg: Label
var lbl_tag: Label
var bubble: Node2D
var bubble_lbl: Label
var bubble_panel: Panel
var caption_lbl: Label
var menu: Control
var players: Array[AudioStreamPlayer] = []
var sfx_cache := {}

# ── ส่วนที่ท่าแต่ละท่าเขียนทับ ──────────────────────────
func end_frame() -> int: return 100
func hit_frame() -> int: return -1
func tech_dmg() -> Dictionary: return {}
func setup() -> void: pass
func frame(_f: float, _F: int, _fresh: bool) -> void: pass
func sounds(_F: int) -> void: pass
func caption() -> String: return ""

# ── เริ่ม ─────────────────────────────────────────────
func _ready() -> void:
	foe = str(Engine.get_meta("lab_foe", "M01"))
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--foe="):
			foe = a.substr(6)
			recording = true
	playing = recording or bool(Engine.get_meta("lab_auto", false))
	var win := get_window()
	win.content_scale_size = Vector2i(W, H)
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	win.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	_audio_bus()
	_load_monster()
	_build_stage()
	setup()
	_build_ui()
	_step(0.0)

func _img(path: String) -> Image:
	if ResourceLoader.exists(path):   # หน้าเว็บ lab: ไฟล์ถูก import เป็นเท็กซ์เจอร์
		return (load(path) as Texture2D).get_image()
	return Image.load_from_file(ProjectSettings.globalize_path(path))

func tx(key: String) -> Texture2D:
	if not tex.has(key):
		var path := (PX + key + ".png") if key.begins_with("pls_") else (MPX + key + ".png")
		tex[key] = ImageTexture.create_from_image(_img(path))
	return tex[key]

func solid(x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < mw and y < mh and mon_img.get_pixel(x, y).a > 0.15

## ขอบซ้าย/ขวาของเนื้อมอนที่แถว row (ไม่มีเนื้อ = หาแถวล่างลงไป) · เหมือน wrEdges บนเว็บ
func edges(row: int) -> Vector2:
	for r in range(max(0, row), mh):
		var l := -1
		var rr := -1
		for x in mw:
			if solid(x, r):
				if l < 0:
					l = x
				rr = x
		if l >= 0:
			return Vector2(l, rr)
	return Vector2(round(mw * 0.2), round(mw * 0.8))

func _load_monster() -> void:
	for r in CsvDb.load_csv("res://data/monsters.csv"):
		if str(r.monster_id) == foe:
			hp = int(r.hp)
			mon_name = str(r.name_th)
	for r in CsvDb.load_csv("res://data/monster_body.csv"):
		if str(r.monster_id) == foe:
			body = str(r.body)
	var d: Array = tech_dmg().get(foe, [0, 0])
	dmg = d[0]
	aff = d[1]
	kill = dmg >= hp
	mon_img = _img(MPX + foe + "_0.png")
	mw = mon_img.get_width()
	mh = mon_img.get_height()
	my = G - mh
	top0 = int(round(mh * 0.3))
	var found := false
	for y in mh:
		for x in mw:
			if solid(x, y):
				top0 = y
				found = true
				break
		if found:
			break
	bh = mh - top0

func place_monster(mx: int) -> void:
	mx0 = int(round(mx - mw / 2.0))
	mcx = mx0 + mw / 2.0

## ภาพมอนตามบทบาท (idle 0–2 · hurt 6) วางกลางช่อง เท้าที่พื้น
func show_mon(key: String, dx := 0.0, white := 0.0) -> void:
	var mt := tx(key)
	mon.visible = true
	mon.texture = mt
	mon.position = Vector2(mx0 + dx + round((mw - mt.get_width()) / 2.0), G - mt.get_height())
	mon.material.set_shader_parameter("tint", Color.WHITE)
	mon.material.set_shader_parameter("amount", white)

# ── ของใช้สร้างโหนด ─────────────────────────────────────
func fx_mat() -> ShaderMaterial:
	var sh := Shader.new()
	sh.code = FX_SHADER
	var m := ShaderMaterial.new()
	m.shader = sh
	return m

func add_mat() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return m

func radial(col: Color, size: int) -> Texture2D:
	var gr := Gradient.new()
	gr.set_color(0, col)
	gr.set_color(1, Color(col.r, col.g, col.b, 0))
	var gt := GradientTexture2D.new()
	gt.gradient = gr
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	gt.width = size
	gt.height = size
	return gt

func ramp(cols: Array) -> Gradient:
	var gr := Gradient.new()
	gr.offsets = PackedFloat32Array()
	gr.colors = PackedColorArray()
	for i in cols.size():
		gr.add_point(float(i) / (cols.size() - 1), cols[i])
	return gr

func particles(amount: int, life: float, z := 5) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.amount = amount
	p.lifetime = life
	p.emitting = false
	p.one_shot = true
	p.explosiveness = 1.0
	p.z_index = z
	add_child(p)
	return p

func rion_sprite(z := 4) -> Sprite2D:
	var s := Sprite2D.new()
	s.centered = false
	s.offset = Vector2(-60, -108)
	s.material = fx_mat()
	s.z_index = z
	add_child(s)
	return s

## วาง Rion ตาม geo ของท่า: {cx, lift, key, flip, sx, sy}
func set_rion(s: Sprite2D, g: Dictionary, alpha := 1.0, tint := Color.WHITE, amt := 0.0) -> void:
	s.texture = tx(g.key)
	s.flip_h = g.flip
	s.position = Vector2(g.cx, G - g.lift)
	s.scale = Vector2(g.sx, g.sy)
	s.modulate.a = alpha
	s.material.set_shader_parameter("tint", tint)
	s.material.set_shader_parameter("amount", amt)
	s.visible = alpha > 0.0

func label(size: int, col: Color, outline: int, bold: bool, parent: Node = null) -> Label:
	var l := Label.new()
	var ls := LabelSettings.new()
	var fv := FontVariation.new()
	fv.base_font = load("res://assets/fonts/game_font.tres")
	if bold:
		fv.variation_embolden = 0.9
	ls.font = fv
	ls.font_size = size
	ls.font_color = col
	ls.outline_size = outline
	ls.outline_color = Color("#2a1a14")
	l.label_settings = ls
	(parent if parent else ui).add_child(l)
	return l

# ── ฉากหลัง บรรยากาศ อนุภาค ─────────────────────────────
func _build_stage() -> void:
	RenderingServer.set_default_clear_color(Color.BLACK)
	cam = Camera2D.new()
	cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
	add_child(cam)
	cam.make_current()
	ui = CanvasLayer.new()
	add_child(ui)
	# ครอปแบบเดียวกับหน้าเว็บ: ย่อกว้าง 300 · เส้นพื้นของภาพ (1250/1376) ที่แถว 158
	var bimg := _img(BG)
	var nh := int(round(bimg.get_height() * 300.0 / bimg.get_width()))
	bimg.resize(300, nh, Image.INTERPOLATE_LANCZOS)
	var y0 := clampi(int(round(nh * 1250.0 / 1376.0)) - 158, 0, nh - H)
	var bg := Sprite2D.new()
	bg.centered = false
	bg.texture = ImageTexture.create_from_image(bimg.get_region(Rect2i(0, y0, 300, H)))
	add_child(bg)
	lamp = Sprite2D.new()
	lamp.texture = radial(Color("#ff9a40"), 68)
	lamp.material = add_mat()
	lamp.position = Vector2(208, 72)
	add_child(lamp)
	embers = particles(6, 1.4, 0)
	embers.one_shot = false
	embers.explosiveness = 0.0
	embers.emitting = true
	embers.position = Vector2(208, 72)
	embers.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	embers.emission_rect_extents = Vector2(4, 1)
	embers.direction = Vector2(0, -1)
	embers.spread = 15
	embers.gravity = Vector2.ZERO
	embers.initial_velocity_min = 14
	embers.initial_velocity_max = 20
	embers.color_ramp = ramp([Color("#ffd27a"), Color("#ff7a2a"), Color(1, 0.48, 0.16, 0)])
	embers.preprocess = 2
	snow = particles(75, 6.0, 0)
	snow.one_shot = false
	snow.explosiveness = 0.0
	snow.emitting = true
	snow.position = Vector2(W / 2.0, -4)
	snow.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	snow.emission_rect_extents = Vector2(W * 0.6, 2)
	snow.direction = Vector2(-0.3, 1)
	snow.spread = 10
	snow.gravity = Vector2(0, 2)
	snow.initial_velocity_min = 18
	snow.initial_velocity_max = 30
	snow.color = Color(0.95, 0.96, 1.0, 0.75)
	snow.preprocess = 8
	dim = ColorRect.new()
	dim.color = Color("#0c1028")
	dim.position = Vector2(-8, -8)
	dim.size = Vector2(W + 16, H + 16)
	dim.modulate.a = 0.0
	add_child(dim)
	mon = Sprite2D.new()
	mon.centered = false
	mon.material = fx_mat()
	mon.z_index = 1
	add_child(mon)
	puff_p = particles(4, 0.4)
	puff_p.direction = Vector2(-1, -0.4)
	puff_p.spread = 12
	puff_p.gravity = Vector2(0, -6)
	puff_p.initial_velocity_min = 16
	puff_p.initial_velocity_max = 24
	puff_p.scale_amount_min = 2
	puff_p.scale_amount_max = 2
	puff_p.color_ramp = ramp([Color(0.92, 0.94, 1, 0.55), Color(0.92, 0.94, 1, 0)])
	dust = particles(10, 0.6)
	dust.spread = 25
	dust.gravity = Vector2(0, 30)
	dust.initial_velocity_min = 25
	dust.initial_velocity_max = 55
	dust.damping_min = 40
	dust.damping_max = 60
	dust.scale_amount_min = 1.5
	dust.scale_amount_max = 3.0
	dust.color_ramp = ramp([Color("#e2d6c0"), Color("#cdbfa6"), Color(0.8, 0.75, 0.65, 0)])
	flash_spr = Sprite2D.new()
	flash_spr.texture = radial(Color(1, 0.95, 0.8), 64)
	flash_spr.material = add_mat()
	flash_spr.z_index = 6
	flash_spr.visible = false
	add_child(flash_spr)
	sparks = particles(28, 0.45, 6)
	sparks.spread = 180
	sparks.gravity = Vector2(0, 160)
	sparks.initial_velocity_min = 60
	sparks.initial_velocity_max = 150
	sparks.damping_min = 80
	sparks.damping_max = 120
	sparks.scale_amount_min = 1.5
	sparks.scale_amount_max = 2.5
	sparks.color_ramp = ramp([Color.WHITE, Color("#ffd27a"), Color(1, 0.6, 0.2, 0)])
	star = Node2D.new()
	star.z_index = 6
	star.draw.connect(_draw_star)
	add_child(star)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CANVAS
	e.glow_enabled = true
	e.glow_intensity = 0.6
	e.glow_bloom = 0.0
	e.glow_hdr_threshold = 0.92
	env.environment = e
	add_child(env)

## ทั้งโลกกลั้นหายใจ: หิมะ/ถ่าน/ไฟตะเกียงหยุดนิ่ง
func world_stop(stop: bool) -> void:
	snow.speed_scale = 0.0 if stop else 1.0
	embers.speed_scale = 0.0 if stop else 1.0
	if not stop:
		lamp.modulate.a = 0.48 * (0.75 + 0.25 * sin(t * 9) * sin(t * 5.3 + 1))

func shake(F: int, amount: float) -> void:
	cam.offset = Vector2(round((_hash(F, 1) * 2 - 1) * amount), round((_hash(F, 2) * 2 - 1) * amount))

func puff(pos: Vector2) -> void:
	puff_p.position = pos
	puff_p.restart()

func dust_at(x: float, dir: float, size := 1.0) -> void:
	dust.position = Vector2(x, G - 1)
	dust.direction = Vector2(dir, -0.35)
	dust.scale_amount_max = 3.0 * size
	dust.restart()

## จุดโดน: ประกายกระเด็น + ดาว 8 แฉก (เหมือน pkStar) + แสงวาบ 4 เฟรม
func burst(pos: Vector2, F: int) -> void:
	burst_f = F
	burst_pos = pos
	sparks.position = pos
	sparks.restart()

func _draw_star() -> void:
	if star_r <= 0.0:
		return
	for i in 8:
		var a := i * PI / 4
		var L := star_r * (0.55 if i % 2 else 1.0)
		var d := Vector2(cos(a), sin(a))
		star.draw_line(Vector2.ZERO, d * L * 0.5, Color.WHITE, 2.0)
		star.draw_line(d * L * 0.5, d * L, Color("#ffd27a"), 2.0)
	star.draw_rect(Rect2(-2, -2, 4, 4), Color.WHITE)

func _burst_step(f: float, F: int) -> void:
	var d := F - burst_f
	var q := f - burst_f
	star.position = burst_pos
	star_r = 10 + d * 6 if d >= 0 and d < 4 else 0.0
	star.queue_redraw()
	flash_spr.visible = d >= 0 and d < 4
	if flash_spr.visible:
		flash_spr.position = burst_pos
		flash_spr.scale = Vector2.ONE * (0.6 + q * 0.35)
		flash_spr.modulate.a = 0.6 * (1 - q / 4.0)

func _hash(a: int, b: int) -> float:
	return fposmod(sin(a * 127.1 + b * 311.7) * 43758.5453, 1.0)

# ── ตัวหนังสือ: บับเบิลชื่อท่า · ตัวเลขดาเมจ · คำเสียง ──────────
func _build_ui() -> void:
	bubble = Node2D.new()
	ui.add_child(bubble)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color.WHITE
	sb.border_color = Color("#140a04")
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(6)
	sb.shadow_color = Color(0, 0, 0, 0.35)
	sb.shadow_offset = Vector2(2, 2)
	sb.shadow_size = 1
	bubble_panel = Panel.new()
	bubble_panel.add_theme_stylebox_override("panel", sb)
	bubble.add_child(bubble_panel)
	var tail := Polygon2D.new()
	tail.polygon = PackedVector2Array([Vector2(-4, 17), Vector2(0, 25), Vector2(4, 17)])
	tail.color = Color.WHITE
	tail.name = "tail"
	bubble.add_child(tail)
	var tail_line := Line2D.new()
	tail_line.points = PackedVector2Array([Vector2(-4, 18), Vector2(0, 25), Vector2(4, 18)])
	tail_line.width = 2
	tail_line.default_color = Color("#140a04")
	tail_line.name = "tail_line"
	bubble.add_child(tail_line)
	bubble_lbl = label(12, Color("#b80d16"), 3, true, bubble)
	bubble_lbl.label_settings.outline_color = Color.WHITE
	bubble_lbl.label_settings.font.variation_embolden = 1.0
	bubble_lbl.position = Vector2(8, -1)
	bubble.visible = false
	lbl_word = label(12, Color("#fff4c8"), 3, true)
	lbl_dmg = label(14, Color("#fff4c8"), 4, true)
	lbl_dmg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_dmg.size = Vector2(160, 20)
	lbl_dmg.pivot_offset = Vector2(80, 12)
	lbl_tag = label(8, Color("#ffe08a") if aff > 0 else Color("#c8e6ff"), 3, true)
	lbl_tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_tag.size = Vector2(160, 12)
	lbl_tag.text = ("อ่อนแอ! · " if aff > 0 else "ต้านทาน · " if aff < 0 else "") + ("HP %d · ฟันเดียวขาด" % hp if kill else "HP %d รอด" % hp)
	lbl_word.visible = false
	lbl_dmg.visible = false
	lbl_tag.visible = false
	var bar := ColorRect.new()
	bar.color = Color(16 / 255.0, 12 / 255.0, 8 / 255.0, 0.62)
	bar.position = Vector2(0, H - 10)
	bar.size = Vector2(W, 10)
	ui.add_child(bar)
	caption_lbl = label(7, Color("#f0e4c8"), 0, false)
	caption_lbl.position = Vector2(4, H - 11)
	caption_lbl.text = caption()
	_build_menu()

## บับเบิลชื่อท่า (เหมือน rs3Bubble): เด้ง 2 เฟรมแรก · ไม่ล้นจอ · หางชี้ผู้พูด
func show_bubble(text: String, x: float, y: float, d: int, alpha: float) -> void:
	bubble.visible = alpha > 0.0
	if not bubble.visible:
		return
	bubble_lbl.text = text
	var bw := bubble_lbl.get_minimum_size().x + 16
	bubble_panel.size = Vector2(bw, 19)
	var sc: float = 1.3 - d * 0.15 if d < 2 else 1.0
	var bx: float = max(2.0, min(W - bw * sc - 2, x - bw * sc / 2))
	bubble.position = Vector2(bx, max(2.0, y - 19 - 8))
	bubble.scale = Vector2(sc, sc)
	bubble.modulate.a = minf(1.0, alpha)
	var tl: float = clamp((x - bx) / sc, 8, bw - 8)
	bubble.get_node("tail").position.x = tl
	bubble.get_node("tail_line").position.x = tl

## ตัวเลขดาเมจ (เหมือน dmgPop): เด้ง แล้วลอยช้า ค้าง ~1.3 วิ แล้วจาง · d = เฟรมหลังโดน
func dmg_pop(d: int, y: float) -> void:
	lbl_dmg.visible = d >= 0 and d < 22
	lbl_tag.visible = lbl_dmg.visible
	if not lbl_dmg.visible:
		return
	var pop: float = [-6, -10, -8][d] if d < 3 else -8 - minf(6.0, (d - 3) * 0.5)
	var x := dmg_x()
	var yy: float = max(18.0, round(y + pop))
	lbl_dmg.text = str(dmg)
	lbl_dmg.scale = Vector2.ONE * (1.4 if d == 0 else 1.15 if d == 1 else 1.0)
	lbl_dmg.position = Vector2(x - 80, yy - 19)
	lbl_dmg.modulate.a = 1.0 if d < 16 else 1 - (d - 16) / 6.0
	lbl_tag.position = Vector2(x - 80, yy + 1)
	lbl_tag.modulate.a = lbl_dmg.modulate.a

func dmg_x() -> float:
	return roundf(clampf(mcx, 30.0, W - 30.0))

## คำเสียง (ฉับ!! / ขาด!!) ข้างมอน · มอนตัวเล็กที่บรรทัด HP ยาวเกินตัว → เลื่อนไปขวาพ้นบรรทัด
func show_word(text: String, y: float, visible_now: bool) -> void:
	lbl_word.visible = visible_now
	if not visible_now:
		return
	lbl_word.text = text
	var tag_r := dmg_x() + lbl_tag.label_settings.font.get_string_size(lbl_tag.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x / 2
	lbl_word.position = Vector2(minf(W - 44, maxf(mx0 + mw + 4, roundf(tag_r) + 4)), y - 14)

# ── เมนู (หน้าเว็บ): เลือกมอน · เล่นซ้ำ · เปิด/ปิดเสียง ─────────────
func _build_menu() -> void:
	menu = Control.new()
	menu.size = Vector2(W, H)
	ui.add_child(menu)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.04, 0.09, 0.82)
	shade.size = Vector2(W, H - 10)
	menu.add_child(shade)
	var title := label(10, Color("#fff4c8"), 3, true, menu)
	title.text = "จันทร์เสี้ยวกลางหาว · ทำใน Godot"
	title.position = Vector2(8, 6)
	var hint := label(8, Color("#e8ecff"), 2, false, menu)
	hint.text = "เลือกมอนที่จะโดน แล้วฉากเล่นทันที"
	hint.position = Vector2(8, 22)
	var names := {}
	for r in CsvDb.load_csv("res://data/monsters.csv"):
		names[str(r.monster_id)] = str(r.name_th)
	for i in FOES.size():   # ปุ่มมอน: ชื่อบน รูปล่าง ในกรอบเดียว
		var id: String = FOES[i]
		var b := _button("%s\n%s" % [id, names.get(id, "")], Vector2(6 + i * 58, 38), Vector2(56, 62), 22)
		b.modulate = Color(1, 1, 0.7) if id == foe else Color.WHITE
		b.pressed.connect(func(): _start(id))
		var ic := TextureRect.new()
		ic.texture = tx(id + "_0")
		ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		ic.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		ic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		ic.position = Vector2(4, 24)
		ic.size = Vector2(48, 35)
		b.add_child(ic)
	var again := _button("เล่นซ้ำ (%s)" % foe, Vector2(6, 106), Vector2(112, 16), 16)
	again.pressed.connect(func(): _start(foe))
	var snd := _button(_sound_text(), Vector2(124, 106), Vector2(90, 16), 16)
	snd.pressed.connect(_toggle_sound.bind(snd))
	var note := label(7, Color("#c8d0e0"), 2, false, menu)
	note.text = "เสียงสร้างด้วยโค้ด · ดาเมจสูตรเดียวกับหน้าเว็บ"
	note.position = Vector2(8, 128)
	menu.visible = not playing

func _toggle_sound(b: Button) -> void:
	Engine.set_meta("lab_mute", not bool(Engine.get_meta("lab_mute", false)))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabSfx"), bool(Engine.get_meta("lab_mute", false)))
	(b.get_meta("lbl") as Label).text = _sound_text()

func _sound_text() -> String:
	return "เสียง: ปิด" if bool(Engine.get_meta("lab_mute", false)) else "เสียง: เปิด"

## ปุ่มกรอบเปล่า + ป้ายข้างใน (ตัวหนังสือในปุ่มเองทำให้ปุ่มยืดเกินขนาดที่ตั้ง)
func _button(text: String, pos: Vector2, size: Vector2, text_h: float) -> Button:
	var b := Button.new()
	b.position = pos
	b.custom_minimum_size = size
	b.size = size
	for st in ["normal", "hover", "pressed"]:
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.12, 0.13, 0.2, 0.95) if st == "normal" else Color(0.25, 0.22, 0.14, 0.95)
		sb.border_color = Color("#c9a24a")
		sb.set_border_width_all(1)
		sb.set_corner_radius_all(3)
		sb.set_content_margin_all(0)
		b.add_theme_stylebox_override(st, sb)
	b.focus_mode = Control.FOCUS_NONE
	menu.add_child(b)
	var l := label(7, Color("#f0e4c8"), 0, false, b)
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.label_settings.line_spacing = -3
	l.position = Vector2(0, 0)
	l.size = Vector2(size.x, text_h)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.set_meta("lbl", l)
	return b

func _start(id: String) -> void:
	Engine.set_meta("lab_foe", id)
	Engine.set_meta("lab_auto", true)
	get_tree().reload_current_scene()

# ── เดินเวลา ─────────────────────────────────────────
func _process(delta: float) -> void:
	if not playing:
		return
	if hold > 0.0:
		hold -= delta
	else:
		t += delta
	var hf := hit_frame()
	if hf >= 0 and not hit_done and t / SEC >= hf:
		hit_done = true
		t = hf * SEC
		hold = HITSTOP
	_step(delta)
	if t > end_frame() * SEC + 0.5:
		if recording:
			get_tree().quit()
		else:
			playing = false
			menu.visible = true

func _step(_delta: float) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var fresh := F != last_fi
	last_fi = F
	frame(f, F, fresh)
	_burst_step(f, F)
	if fresh and playing:
		sounds(F)

# ── เสียงสังเคราะห์ (สูตรเดียวกับ auNoise/auTone บนหน้าเว็บ) ───────────
## เสียงหนึ่งก้อน = รายการเสียงย่อย · สร้างครั้งเดียวต่อชื่อ แล้วเก็บไว้เล่นซ้ำ
func N(dur: float, type: String, f0: float, f1: float, peak: float, q := 1.0, delay := 0.0, o := {}) -> Dictionary:
	return {"k": "n", "dur": dur, "type": type, "f0": f0, "f1": f1, "peak": peak, "q": q, "delay": delay, "attack": o.get("attack", 0.004), "drive": o.get("drive", false)}

func T(dur: float, wave: String, f0: float, f1: float, peak: float, delay := 0.0, attack := 0.004, o := {}) -> Dictionary:
	return {"k": "t", "dur": dur, "type": wave, "f0": f0, "f1": f1, "peak": peak, "delay": delay, "attack": attack, "drive": o.get("drive", false),
		"lp": o.get("lp", 0.0), "q": o.get("q", 1.0), "fm": o.get("fm", 0.0), "fm_depth": o.get("fmDepth", 200.0)}

func play_sfx(key: String, voices: Array) -> void:
	if not sfx_cache.has(key):
		sfx_cache[key] = _render(voices)
	for p in players:
		if not p.playing:
			p.stream = sfx_cache[key]
			p.play()
			return

func _audio_bus() -> void:
	if AudioServer.get_bus_index("LabSfx") < 0:
		AudioServer.add_bus()
		var i := AudioServer.bus_count - 1
		AudioServer.set_bus_name(i, "LabSfx")
		var rv := AudioEffectReverb.new()   # ห้องก้อง (บนเว็บใช้ convolver 1.6 วิ)
		rv.room_size = 0.55
		rv.damping = 0.4
		rv.wet = 0.22
		rv.dry = 1.0
		AudioServer.add_bus_effect(i, rv)
		var cp := AudioEffectCompressor.new()   # เหมือนบนเว็บ: threshold −14 · ratio 6
		cp.threshold = -14
		cp.ratio = 6
		cp.attack_us = 3000
		cp.release_ms = 200
		AudioServer.add_bus_effect(i, cp)
		AudioServer.set_bus_volume_db(i, linear_to_db(0.85))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabSfx"), bool(Engine.get_meta("lab_mute", false)))
	for k in 12:
		var p := AudioStreamPlayer.new()
		p.bus = "LabSfx"
		add_child(p)
		players.append(p)

func _render(voices: Array) -> AudioStreamWAV:
	var total := 0.0
	for v in voices:
		total = maxf(total, v.delay + v.dur + 0.05)
	var buf := PackedFloat32Array()
	buf.resize(int(total * SR) + 1)
	buf.fill(0.0)
	var seed := 12345
	for v in voices:
		seed = _voice(buf, v, seed)
	var data := PackedByteArray()
	data.resize(buf.size() * 2)
	for i in buf.size():
		data.encode_s16(i * 2, int(tanh(buf[i] * 0.8) * 32000))
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = SR
	w.stereo = false
	w.data = data
	return w

func _voice(buf: PackedFloat32Array, v: Dictionary, seed: int) -> int:
	var n0 := int(v.delay * SR)
	var n := mini(int((v.dur + 0.05) * SR), buf.size() - n0)
	var dur: float = v.dur
	var att: float = clampf(v.attack, 0.001, dur * 0.95)
	var peak: float = v.peak
	var f0: float = v.f0
	var f1: float = maxf(20.0, v.f1)
	var noise: bool = v.k == "n"
	var ftype: String = v.type if noise else ("lowpass" if v.lp > 0 else "")
	var q: float = v.q
	var b0 := 0.0
	var b1 := 0.0
	var b2 := 0.0
	var a1 := 0.0
	var a2 := 0.0
	var x1 := 0.0
	var x2 := 0.0
	var y1 := 0.0
	var y2 := 0.0
	var ph := 0.0
	var mph := 0.0
	var e := 0.0001
	var ra := pow(peak / 0.0001, 1.0 / (att * SR))
	var rd := pow(0.0001 / peak, 1.0 / ((dur - att) * SR))
	var f := f0
	for i in n:
		var tt := float(i) / SR
		if i % 16 == 0:
			f = f0 * pow(f1 / f0, minf(tt / dur, 1.0))
			if ftype != "":
				var fc := clampf(f if noise else v.lp, 20.0, SR * 0.45)
				var w0 := TAU * fc / SR
				var c := cos(w0)
				var al := sin(w0) / (2.0 * q)
				var a0 := 1.0 + al
				if ftype == "lowpass":
					b0 = (1 - c) / 2 / a0
					b1 = (1 - c) / a0
					b2 = b0
				elif ftype == "highpass":
					b0 = (1 + c) / 2 / a0
					b1 = -(1 + c) / a0
					b2 = b0
				else:
					b0 = al / a0
					b1 = 0.0
					b2 = -al / a0
				a1 = -2 * c / a0
				a2 = (1 - al) / a0
		var s := 0.0
		if noise:
			seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
			s = seed / 2147483648.0 - 1.0
		else:
			var fr := f
			if v.fm > 0.0:
				mph += v.fm / SR
				fr += sin(TAU * mph) * v.fm_depth
			ph = fposmod(ph + fr / SR, 1.0)
			match v.type:
				"sine":
					s = sin(TAU * ph)
				"square":
					s = 1.0 if ph < 0.5 else -1.0
				_:
					s = 2.0 * ph - 1.0
		if ftype != "":
			var y := b0 * s + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
			x2 = x1
			x1 = s
			y2 = y1
			y1 = y
			s = y
		if tt < att:
			e *= ra
		elif tt < dur:
			e *= rd
		else:
			e = 0.0
		s *= e
		if v.drive:
			s = tanh(s * 3.2)
		buf[n0 + i] += s
	return seed

## เสียงชุดเดียวกับ AU_SFX บนหน้าเว็บ (สาย SL = คม)
func sfx_charge() -> void:
	play_sfx("charge", [N(0.62, "bandpass", 180, 2600, 0.5, 3, 0, {"attack": 0.5}), T(0.62, "sawtooth", 48, 96, 0.22, 0, 0.45, {"lp": 420, "q": 4})])

func sfx_release() -> void:
	play_sfx("release", [N(0.28, "bandpass", 500, 3800, 1.0, 1.8), N(0.22, "highpass", 3200, 9000, 0.6, 9, 0.03), T(0.18, "sawtooth", 2200, 700, 0.18, 0.02, 0.004, {"lp": 5000})])

func sfx_hit(big: bool) -> void:
	var v := [T(0.95 if big else 0.6, "sine", 95 if big else 120, 28, 1.0, 0, 0.002, {"drive": true}), N(0.9 if big else 0.5, "lowpass", 5200, 160, 1.0, 0.8, 0, {"drive": true}),
		N(0.05, "highpass", 3500, 3500, 0.9, 1), N(0.35, "bandpass", 4200, 2600, 0.5, 14, 0.01)]
	if big:
		v.append(N(1.4, "lowpass", 600, 50, 0.6, 0.7, 0.05))
	play_sfx("hit%s" % big, v)

## เสียงมอนโดน ตามร่างกาย (เหมือน auMon + monVoice) · p = คูณความถี่ (ตัวใหญ่ต่ำลง)
func sfx_mon(last: bool, p := 1.0) -> void:
	var kind := "wing" if body.contains("ปีก") else "slime" if (body.contains("นุ่ม") or body.contains("ของเหลว") or body.contains("เมือก")) else "beast" if (body.contains("ขน") or body.contains("สัตว์") or body.contains("เนื้อ")) else "hard" if (body.contains("เกราะ") or body.contains("หิน") or body.contains("เปลือก") or body.contains("กระดูก") or body.contains("โลหะ") or body.contains("กลไก") or body.contains("ไม้")) else "slime"
	var v := []
	if kind == "slime":
		for a in [[0, 900, 1500], [0.11, 1100, 1700]]:
			v.append(T(0.09, "sine", a[1] * p, a[2] * p, 0.35, a[0], 0.004, {"fm": 38, "fmDepth": 90}))
		v.append(N(0.12, "bandpass", 900 * p, 400 * p, 0.35, 4, 0.02))
		if last:
			v.append(T(0.45, "sine", 1600 * p, 320 * p, 0.4, 0.22, 0.01, {"fm": 9, "fmDepth": 60}))
			v.append(N(0.35, "lowpass", 1200 * p, 200 * p, 0.4, 1, 0.25))
	elif kind == "wing":
		for i in 3:
			v.append(T(0.05, "square", 2600 * p, 3400 * p, 0.12, i * 0.06, 0.002, {"lp": 6000}))
		v.append(N(0.08, "bandpass", 700 * p, 500 * p, 0.3, 2, 0.03))
		if last:
			v.append(T(0.4, "square", 3200 * p, 900 * p, 0.12, 0.2, 0.004, {"lp": 5000}))
			for i in 4:
				v.append(N(0.07, "bandpass", 600 * p, 400 * p, 0.3 - i * 0.06, 2, 0.3 + i * 0.12 * (1 + i * 0.3)))
	elif kind == "beast":
		v.append(T(0.16, "sawtooth", 700 * p, 380 * p, 0.3, 0, 0.004, {"lp": 2400}))
		if last:
			v.append(T(0.5, "sawtooth", 520 * p, 140 * p, 0.3, 0.15, 0.01, {"lp": 1800}))
	else:
		v.append(T(0.08, "square", 1300 * p, 900 * p, 0.18, 0, 0.002, {"lp": 3500}))
		v.append(N(0.1, "highpass", 3000 * p, 6000 * p, 0.3, 3))
		if p < 0.8:
			v.append(T(0.35, "sawtooth", 160 * p * 2, 70 * p * 2, 0.35, 0.03, 0.01, {"lp": 900, "drive": true}))
		if last:
			v.append(N(0.5, "lowpass", 2000 * p, 200 * p, 0.5, 1, 0.1))
			if p < 0.8:
				v.append(T(0.9, "sawtooth", 140, 45, 0.4, 0.12, 0.02, {"lp": 700, "drive": true}))
	play_sfx("mon_%s_%s_%s" % [kind, last, p], v)
