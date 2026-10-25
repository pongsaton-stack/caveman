extends Node2D
## ห้องทดลอง: ฉาก bl9 จันทร์เสี้ยวกลางหาว ทำใน Godot เทียบกับหน้าเว็บ (jg_bl9 ใน tools/web/anim_test.tpl.html)
## ไม่ใช่ฉากในเกม · อยู่ใต้ tests/ จึงไม่ถูก export · ภาพร่างโหลดจากไฟล์ตรง (โฟลเดอร์ร่างมี .gdignore)
## เปิด: <godot> --path . res://tests/lab/jg_bl9.tscn -- --foe=M01        (M01 ขาด · M15/B1 รอด)
## อัดวิดีโอ: xvfb-run -a <godot> --path . --rendering-driver opengl3 --resolution 600x336 --write-movie <out>/f.png --fixed-fps 60 res://tests/lab/jg_bl9.tscn -- --foe=M01
## จังหวะ/ตำแหน่งเหมือนหน้าเว็บทุกเฟรม (เฟรมละ 0.06 วิ) แต่ตำแหน่งคิดต่อเนื่องที่ 60 fps · ที่ Godot เพิ่ม: อนุภาค (หิมะ ฝุ่น ประกาย ผง) แสงบวก หยุดภาพตอนโดน ซีกที่ขาดหมุนคว่ำแล้วสลาย

const W := 300
const H := 168
const G := 158
const MX := 112
const SEC := 0.06
const END := 112
const RAISE := 8
const TONBO := 12
const SHOUT := 28
const RUN := 34
const LEAP := 39
const APEX := 45
const CUT := 48
const LAND := 53
const SPLIT := 65
const TURN := 72
const BACK := 74
const HOME := 90
const HITSTOP := 0.1
const PX := "res://assets/sprites/pixellab_draft/px_set/"
const MPX := "res://assets/sprites/monsters_px_draft/"
const BG := "res://docs/art-bible/pixellab_test/bg_frost_volcano.jpg"
## ดาเมจ [ค่า, ธาตุ/ร่างกาย +1 อ่อนแอ -1 ต้านทาน] = ค่าเดียวกับหน้าเว็บ csHit('bl9', มอน) (prof 20 + มีดครัว 14) · ยังไม่ต่อสูตรเกมตรง
const DMG := {"M01": [110, 0], "M15": [113, 1], "B1": [62, -1]}

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
var t := 0.0
var hold := 0.0
var split_done := false
var last_fi := -1
var tex := {}
var mon_img: Image
var mw := 48
var mh := 48
var mx0 := 0
var my := 0
var mcx := 0.0
var bh := 0
var home := W - 40
var moon_y := 0.0
var moon_x := 0.0
var apex_l := 0.0
var x0 := 0.0
var xland := 0.0
var p0 := Vector2.ZERO
var p1 := Vector2.ZERO
var p2 := Vector2.ZERO
var chord := Vector2.ZERO
var kill := false
var dmg := 0
var aff := 0
var hp := 0
var mon_name := ""

var cam: Camera2D
var dim: ColorRect
var moon: Sprite2D
var moon_glow: Sprite2D
var mon: Sprite2D
var piece_up: Polygon2D
var piece_dn: Polygon2D
var wound_mask: Sprite2D
var wound_dark: Line2D
var wound_lit: Line2D
var trail: Node2D
var trail_glow: Node2D
var rion: Sprite2D
var ghosts: Array[Sprite2D] = []
var rim: Sprite2D
var shadow: ColorRect
var snow: CPUParticles2D
var embers: CPUParticles2D
var lamp: Sprite2D
var breath: CPUParticles2D
var dust: CPUParticles2D
var sparks: CPUParticles2D
var flash_spr: Sprite2D
var ash_up: CPUParticles2D
var ash_dn: CPUParticles2D
var ui: CanvasLayer
var lbl_hit: Label
var lbl_dots: Label
var lbl_dmg: Label
var lbl_tag: Label
var bubble: Node2D
var bubble_w := 0.0
var caption: Label

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--foe="):
			foe = a.substr(6)
	var win := get_window()
	win.content_scale_size = Vector2i(W, H)
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	win.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	_load_monster()
	_build()
	_tick(0.0)

# ── ข้อมูล ───────────────────────────────────────────────

func _img(path: String) -> Image:
	return Image.load_from_file(ProjectSettings.globalize_path(path))

func _tex(key: String) -> Texture2D:
	if not tex.has(key):
		var path := (PX + key + ".png") if key.begins_with("pls_") else (MPX + key + ".png")
		tex[key] = ImageTexture.create_from_image(_img(path))
	return tex[key]

func _a(x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < mw and y < mh and mon_img.get_pixel(x, y).a > 0.15

func _edges(row: int) -> Vector2:
	for r in range(max(0, row), mh):
		var l := -1
		var rr := -1
		for x in mw:
			if _a(x, r):
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
	dmg = DMG.get(foe, [0, 0])[0]
	aff = DMG.get(foe, [0, 0])[1]
	kill = dmg >= hp
	mon_img = _img(MPX + foe + "_0.png")
	mw = mon_img.get_width()
	mh = mon_img.get_height()
	mx0 = int(round(MX - mw / 2.0))
	my = G - mh
	mcx = mx0 + mw / 2.0
	var top0 := int(round(mh * 0.3))
	var found := false
	for y in mh:
		for x in mw:
			if _a(x, y):
				top0 = y
				found = true
				break
		if found:
			break
	bh = mh - top0
	var tr := _edges(top0 + 3)
	var lb := _edges(mh - 4).x
	moon_y = max(22.0, min(52.0, G - bh - 30.0))
	moon_x = mx0 + mw / 2.0 + 16
	apex_l = min(72.0, G - 44.0 - moon_y)
	x0 = mx0 + mw + 30
	xland = max(30.0, mx0 - 26.0)
	p0 = Vector2(mx0 + tr.y + 5, G - bh - 4)
	p2 = Vector2(mx0 + max(lb, mw * 0.12) + 2, G - 2)
	chord = (p2 - p0).normalized()
	var mid_e := _edges(int(round(top0 + bh * 0.5)))
	var mid := Vector2(mx0 + (mid_e.x + mid_e.y) / 2.0, G - bh * 0.5)
	p1 = Vector2(2 * mid.x - (p0.x + p2.x) / 2.0 - (mid_e.y - mid_e.x) * 0.15, 2 * mid.y - (p0.y + p2.y) / 2.0)

func cut(u: float) -> Vector2:
	return (1 - u) * (1 - u) * p0 + 2 * u * (1 - u) * p1 + u * u * p2

## ตำแหน่ง Rion · เหมือน jgGeo บนเว็บ แต่ f เป็นทศนิยม (การเลื่อนที่ต่อเนื่อง) ส่วนภาพเลือกจากเฟรมเต็ม
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "pls_idle_bl_%d" % (posmod(int(floor(f / 4.0)), 4)), "flip": false, "sx": 1.0, "sy": 1.0, "sil": false, "back": false}
	if F < RAISE:
		return r
	if F < RUN:
		r.key = "pls_bl9_0" if F < RAISE + 2 else "pls_bl9_1" if F < TONBO else "pls_bl9_2" if F < TONBO + 2 else "pls_bl9_3" if F < SHOUT else "pls_bl9_4"
		if F >= TONBO:
			r.sy = 1 - 0.004 * min(8, F - TONBO)
		if F >= TONBO + 6:
			r.cx += (1.0 if F % 2 else -1.0) * (1.0 if F >= SHOUT else 0.5)
		return r
	if F < LEAP:
		var tt := (f - RUN + 1) / float(LEAP - RUN + 1)
		r.cx = home + (x0 - home) * (0.45 * tt * tt + 0.55 * tt)
		r.key = "pls_run_bl_%d" % ((F - RUN) % 6)
		return r
	if F < APEX:
		if F == LEAP:
			r.cx = x0
			r.key = "pls_hop_bl_2"
			r.sy = 0.94
			return r
		var tt := (f - LEAP) / float(APEX - LEAP)
		var e := 1 - (1 - tt) * (1 - tt)
		r.cx = x0 + (moon_x + 6 - x0) * e
		r.lift = apex_l * e
		r.key = "pls_bl9_3"
		return r
	if F < CUT:
		r.cx = moon_x + 6 - (f - APEX)
		r.lift = apex_l
		r.key = "pls_bl9_4"
		r.sil = true
		return r
	if F < LAND:
		var tt := (f - CUT + 1) / float(LAND - CUT)
		r.cx = moon_x + 3 + (xland - (moon_x + 3)) * tt
		r.lift = apex_l * (1 - tt * tt)
		r.key = "pls_atk_bl_5" if F < CUT + 2 else "pls_atk_bl_6"
		return r
	if F < TURN:
		var q := f - LAND
		r.cx = xland - 7 * (1 - pow(0.6, q + 1))
		r.key = "pls_atk_bl_7"
		if F - LAND < 2:
			r.sy = 0.92
			r.sx = 1.05
		return r
	var xs := xland - 7
	if F < BACK:
		r.cx = xs
		r.key = "pls_spin_bl_3" if F == TURN else "pls_spin_bl_2"
		return r
	if F < HOME - 2:
		var tt := (f - BACK + 1) / float(HOME - 2 - BACK)
		r.cx = xs + (home - xs) * tt
		r.key = "pls_run_bl_%d" % ((F - BACK) % 6)
		r.flip = true
		r.back = true
		return r
	r.cx = home
	if F < HOME:
		r.key = "pls_spin_bl_3" if F == HOME - 2 else "pls_spin_bl_0"
	return r

# ── สร้างฉาก ─────────────────────────────────────────────

func _fx_mat() -> ShaderMaterial:
	var sh := Shader.new()
	sh.code = FX_SHADER
	var m := ShaderMaterial.new()
	m.shader = sh
	return m

func _add_mat() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return m

func _radial(col: Color, size: int) -> Texture2D:
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

func _ramp(cols: Array) -> Gradient:
	var gr := Gradient.new()
	gr.offsets = PackedFloat32Array()
	gr.colors = PackedColorArray()
	for i in cols.size():
		gr.add_point(float(i) / (cols.size() - 1), cols[i])
	return gr

func _particles(amount: int, life: float) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.amount = amount
	p.lifetime = life
	p.emitting = false
	p.one_shot = true
	p.explosiveness = 1.0
	p.texture = null
	add_child(p)
	return p

func _moon_tex(R: int) -> Texture2D:
	var im := Image.create(R * 2 + 1, R * 2 + 1, false, Image.FORMAT_RGBA8)
	for j in range(-R, R + 1):
		for i in range(-R, R + 1):
			if i * i + j * j > R * R:
				continue
			var a := i - R * 0.45
			var b := j + R * 0.3
			if a * a + b * b < R * R * 0.78:
				continue
			var c := Color("#e8c878") if i * i + j * j > (R - 1.5) * (R - 1.5) else (Color("#fffbe6") if i < -R * 0.5 else Color("#f6e7b4"))
			im.set_pixel(i + R, j + R, c)
	return ImageTexture.create_from_image(im)

func _label(size: int, col: Color, outline: int, bold: bool) -> Label:
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
	ui.add_child(l)
	return l

func _build() -> void:
	RenderingServer.set_default_clear_color(Color.BLACK)
	cam = Camera2D.new()
	cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
	add_child(cam)
	cam.make_current()
	# ฉากหลัง: ครอปแบบเดียวกับหน้าเว็บ (ย่อกว้าง 300 · เส้นพื้นที่แถว 158)
	var bimg := _img(BG)
	var nh := int(round(bimg.get_height() * 300.0 / bimg.get_width()))
	bimg.resize(300, nh, Image.INTERPOLATE_LANCZOS)
	var y0 := clampi(int(round(nh * 1250.0 / 1376.0)) - 158, 0, nh - H)
	var bg := Sprite2D.new()
	bg.centered = false
	bg.texture = ImageTexture.create_from_image(bimg.get_region(Rect2i(0, y0, 300, H)))
	bg.position = Vector2(-0, 0)
	add_child(bg)
	# บรรยากาศฉาก: ไฟตะเกียง ถ่าน หิมะ (หยุดนิ่งตอนตั้งท่า)
	lamp = Sprite2D.new()
	lamp.texture = _radial(Color("#ff9a40"), 68)
	lamp.material = _add_mat()
	lamp.position = Vector2(208, 72)
	add_child(lamp)
	embers = _particles(6, 1.4)
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
	embers.color_ramp = _ramp([Color("#ffd27a"), Color("#ff7a2a"), Color(1, 0.48, 0.16, 0)])
	embers.preprocess = 2
	snow = _particles(75, 6.0)
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
	add_child(dim)
	# พระจันทร์ + แสงฟุ้ง (บวกแสง)
	moon_glow = Sprite2D.new()
	moon_glow.texture = _radial(Color("#fff4c8"), 96)
	moon_glow.material = _add_mat()
	add_child(moon_glow)
	moon = Sprite2D.new()
	moon.texture = _moon_tex(18)
	add_child(moon)
	# Rion (ด้านหลังมอนตอนวิ่งกลับ ใช้ z_index)
	shadow = ColorRect.new()
	shadow.color = Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4)
	add_child(shadow)
	rim = _rion_sprite()
	for i in 2:
		ghosts.append(_rion_sprite())
	rion = _rion_sprite()
	# มอน · ชิ้นตามแนวฟัน · แผล (ตัดด้วยเนื้อมอน = clip_children)
	mon = Sprite2D.new()
	mon.centered = false
	mon.material = _fx_mat()
	mon.z_index = 1
	add_child(mon)
	var line := PackedVector2Array()
	var poly: Array[Vector2] = []
	for i in 25:
		poly.append(cut(i / 24.0))
	var a0 := poly[0] + (poly[0] - poly[1]).normalized() * 300
	var a1 := poly[24] + (poly[24] - poly[23]).normalized() * 300
	line.append(a0)
	line.append_array(PackedVector2Array(poly))
	line.append(a1)
	var up := line.duplicate()
	up.append(a1 - Vector2(600, 600))
	up.append(a0 - Vector2(600, 600))
	var dn := line.duplicate()
	dn.append(a1 + Vector2(600, 600))
	dn.append(a0 + Vector2(600, 600))
	var rect := PackedVector2Array([Vector2(mx0, my), Vector2(mx0 + mw, my), Vector2(mx0 + mw, my + mh), Vector2(mx0, my + mh)])
	piece_up = _piece(up, rect)
	piece_dn = _piece(dn, rect)
	ash_up = _ash(piece_up)
	ash_dn = _ash(piece_dn)
	wound_mask = Sprite2D.new()
	wound_mask.centered = false
	wound_mask.clip_children = CanvasItem.CLIP_CHILDREN_ONLY
	wound_mask.z_index = 2
	add_child(wound_mask)
	wound_dark = Line2D.new()
	wound_lit = Line2D.new()
	for ln in [wound_dark, wound_lit]:
		ln.antialiased = false
		for i in 81:
			ln.add_point(cut(i / 80.0) - Vector2(mx0, my))
		wound_mask.add_child(ln)
	wound_dark.width = 2.5
	wound_lit.width = 1
	# รอยเสี้ยวจันทร์ (ริบบิ้นหนากลาง บางปลาย) + ชั้นเรืองแสง
	trail_glow = Node2D.new()
	trail_glow.material = _add_mat()
	trail_glow.z_index = 3
	trail_glow.draw.connect(_draw_trail.bind(true))
	add_child(trail_glow)
	trail = Node2D.new()
	trail.z_index = 3
	trail.draw.connect(_draw_trail.bind(false))
	add_child(trail)
	for s in [rim, ghosts[0], ghosts[1], rion, shadow]:
		s.z_index = 4
	# อนุภาค: ลมหายใจ · ฝุ่น · ประกายตอนโดน
	breath = _particles(4, 0.4)
	breath.direction = Vector2(-1, -0.4)
	breath.spread = 12
	breath.gravity = Vector2(0, -6)
	breath.initial_velocity_min = 16
	breath.initial_velocity_max = 24
	breath.scale_amount_min = 2
	breath.scale_amount_max = 2
	breath.color_ramp = _ramp([Color(0.92, 0.94, 1, 0.55), Color(0.92, 0.94, 1, 0)])
	breath.z_index = 5
	dust = _particles(10, 0.6)
	dust.spread = 25
	dust.gravity = Vector2(0, 30)
	dust.initial_velocity_min = 25
	dust.initial_velocity_max = 55
	dust.damping_min = 40
	dust.damping_max = 60
	dust.scale_amount_min = 1.5
	dust.scale_amount_max = 3.0
	dust.color_ramp = _ramp([Color("#e2d6c0"), Color("#cdbfa6"), Color(0.8, 0.75, 0.65, 0)])
	dust.z_index = 5
	flash_spr = Sprite2D.new()
	flash_spr.texture = _radial(Color(1, 0.95, 0.8), 64)
	flash_spr.material = _add_mat()
	flash_spr.z_index = 6
	flash_spr.visible = false
	add_child(flash_spr)
	sparks = _particles(28, 0.45)
	sparks.spread = 180
	sparks.gravity = Vector2(0, 160)
	sparks.initial_velocity_min = 60
	sparks.initial_velocity_max = 150
	sparks.damping_min = 80
	sparks.damping_max = 120
	sparks.scale_amount_min = 1
	sparks.scale_amount_max = 2
	sparks.color_ramp = _ramp([Color.WHITE, Color("#ffd27a"), Color(1, 0.6, 0.2, 0)])
	sparks.material = _add_mat()
	sparks.z_index = 6
	# ตัวหนังสือ (ไม่สั่นตามกล้อง)
	ui = CanvasLayer.new()
	add_child(ui)
	bubble = Node2D.new()
	ui.add_child(bubble)
	var bl := Label.new()
	var bls := LabelSettings.new()
	var bfv := FontVariation.new()
	bfv.base_font = load("res://assets/fonts/game_font.tres")
	bfv.variation_embolden = 1.0
	bls.font = bfv
	bls.font_size = 12
	bls.font_color = Color("#b80d16")
	bls.outline_size = 3
	bls.outline_color = Color.WHITE
	bl.label_settings = bls
	bl.text = "จันทร์เสี้ยวกลางหาว!"
	bubble_w = bl.get_minimum_size().x + 16
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color.WHITE
	sb.border_color = Color("#140a04")
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(6)
	sb.shadow_color = Color(0, 0, 0, 0.35)
	sb.shadow_offset = Vector2(2, 2)
	sb.shadow_size = 1
	var panel := Panel.new()
	panel.add_theme_stylebox_override("panel", sb)
	panel.size = Vector2(bubble_w, 19)
	bubble.add_child(panel)
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
	bl.position = Vector2(8, -1)
	bubble.add_child(bl)
	lbl_hit = _label(12, Color("#fff4c8"), 3, true)
	lbl_dots = _label(9, Color("#e8ecff"), 0, true)
	lbl_dmg = _label(14, Color("#fff4c8"), 4, true)
	lbl_dmg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_dmg.size = Vector2(160, 20)
	lbl_dmg.pivot_offset = Vector2(80, 12)
	lbl_tag = _label(8, Color("#ffe08a") if aff > 0 else Color("#c8e6ff"), 3, true)
	lbl_tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_tag.size = Vector2(160, 12)
	var bar := ColorRect.new()
	bar.color = Color(16 / 255.0, 12 / 255.0, 8 / 255.0, 0.62)
	bar.position = Vector2(0, H - 10)
	bar.size = Vector2(W, 10)
	ui.add_child(bar)
	caption = _label(7, Color("#f0e4c8"), 0, false)
	caption.position = Vector2(4, H - 11)
	caption.text = "GODOT · %s %s · จันทร์เสี้ยวกลางหาว → %s" % [mon_name, foe, "ขาด" if kill else "แผลเรือง (รอด)"]
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CANVAS
	e.glow_enabled = true
	e.glow_intensity = 0.6
	e.glow_bloom = 0.0
	e.glow_hdr_threshold = 0.92
	env.environment = e
	add_child(env)

func _rion_sprite() -> Sprite2D:
	var s := Sprite2D.new()
	s.centered = false
	s.offset = Vector2(-60, -108)
	s.material = _fx_mat()
	add_child(s)
	return s

func _piece(poly: PackedVector2Array, rect: PackedVector2Array) -> Polygon2D:
	var best := PackedVector2Array()
	for p in Geometry2D.intersect_polygons(poly, rect):
		if p.size() > best.size():
			best = p
	var c := Vector2.ZERO
	for v in best:
		c += v
	c /= max(1, best.size())
	var pg := Polygon2D.new()
	var loc := PackedVector2Array()
	var uv := PackedVector2Array()
	for v in best:
		loc.append(v - c)
		uv.append(v - Vector2(mx0, my))
	pg.polygon = loc
	pg.uv = uv
	pg.set_meta("c", c)
	pg.set_meta("world", best)
	pg.material = _fx_mat()
	pg.z_index = 1
	pg.visible = false
	add_child(pg)
	return pg

## ผงสลาย: จุดปล่อย = พิกเซลจริงของซีกนั้น สีเดียวกับเนื้อ
func _ash(pg: Polygon2D) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.amount = 90
	p.lifetime = 1.1
	p.one_shot = true
	p.explosiveness = 0.6
	p.emitting = false
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_POINTS
	var pts := PackedVector2Array()
	var cols := PackedColorArray()
	var world: PackedVector2Array = pg.get_meta("world")
	var c: Vector2 = pg.get_meta("c")
	for y in range(0, mh, 2):
		for x in range(0, mw, 2):
			var w := Vector2(mx0 + x, my + y)
			if _a(x, y) and Geometry2D.is_point_in_polygon(w, world):
				pts.append(w - c)
				cols.append(mon_img.get_pixel(x, y))
	p.emission_points = pts
	p.emission_colors = cols
	p.direction = Vector2(0, -1)
	p.spread = 35
	p.gravity = Vector2(0, -22)
	p.initial_velocity_min = 4
	p.initial_velocity_max = 16
	p.color_ramp = _ramp([Color.WHITE, Color(1, 1, 1, 0.7), Color(1, 1, 1, 0)])
	p.local_coords = false
	p.z_index = 2
	pg.add_child(p)
	return p

# ── วาดรอยเสี้ยว ───────────────────────────────────────

var trail_p := 0.0
var trail_lit := 1.0

func _draw_trail(glow: bool) -> void:
	var node: Node2D = trail_glow if glow else trail
	if trail_p <= 0.0:
		return
	var n := 90
	var u0 := -0.12
	var left := PackedVector2Array()
	var right := PackedVector2Array()
	var head := Vector2.ZERO
	for i in n + 1:
		if float(i) / n > trail_p:
			break
		var u := u0 + (1.05 - u0) * i / n
		var pt := cut(u)
		if pt.y > G - 1 or pt.y < 3:
			continue
		var tg := (cut(u + 0.01) - cut(u - 0.01)).normalized()
		var nm := Vector2(-tg.y, tg.x)
		var w := maxf(1.0, 1 + 4 * sin(PI * i / n)) * (2.4 if glow else 1.0)
		left.append(pt + nm * w / 2)
		right.append(pt - nm * w / 2)
		head = pt
	if left.size() < 2:
		return
	right.reverse()
	var poly := left + right
	if glow:
		node.draw_colored_polygon(poly, Color(0.91, 0.78, 0.47, 0.5 * trail_lit))
	else:
		node.draw_colored_polygon(poly, Color(1, 0.97, 0.86, trail_lit))
		if trail_p < 1.0:
			node.draw_rect(Rect2(head - Vector2(1, 1), Vector2(3, 3)), Color.WHITE)

# ── เดินเวลา ─────────────────────────────────────────

func _process(delta: float) -> void:
	if hold > 0.0:
		hold -= delta
	else:
		t += delta
	if not split_done and t / SEC >= SPLIT:
		split_done = true
		t = SPLIT * SEC
		hold = HITSTOP
	_tick(delta)
	if t > END * SEC + 0.5:
		get_tree().quit()

func _hash(a: int, b: int) -> float:
	return fposmod(sin(a * 127.1 + b * 311.7) * 43758.5453, 1.0)

func _set_rion(s: Sprite2D, g: Dictionary, alpha: float, tint: Color, amt: float) -> void:
	s.texture = _tex(g.key)
	s.flip_h = g.flip
	s.position = Vector2(g.cx, G - g.lift)
	s.scale = Vector2(g.sx, g.sy)
	s.modulate.a = alpha
	s.material.set_shader_parameter("tint", tint)
	s.material.set_shader_parameter("amount", amt)
	s.visible = alpha > 0.0

func _tick(_delta: float) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var ds := F - SPLIT
	var q := f - SPLIT
	var g := geo(f)
	var new_frame := F != last_fi
	last_fi = F
	# กล้องสั่น: ตะโกน / แยก
	var shk: float = 2.0 * (1 - (F - SHOUT) / 4.0) if F >= SHOUT and F < SHOUT + 4 else (4.0 * (1 - ds / 6.0) if ds >= 0 and ds < 6 else 0.0)
	cam.offset = Vector2(round((_hash(F, 1) * 2 - 1) * shk), round((_hash(F, 2) * 2 - 1) * shk))
	# ทั้งโลกกลั้นหายใจ
	var stop := F >= TONBO and F < SPLIT
	snow.speed_scale = 0.0 if stop else 1.0
	embers.speed_scale = 0.0 if stop else 1.0
	if not stop:
		lamp.modulate.a = 0.22 * (0.75 + 0.25 * sin(t * 9) * sin(t * 5.3 + 1)) * 2.2
	var dv := 0.0 if f < TONBO else (0.45 * (f - TONBO) / (SHOUT - TONBO) if f < SHOUT else (0.45 if ds < 6 else maxf(0.0, 0.45 * (1 - (q - 6) / 16.0))))
	dim.modulate.a = dv
	# พระจันทร์
	var mp := 0.0 if f < TONBO else minf(1.0, (f - TONBO) / (SHOUT - TONBO))
	var me := 1 - (1 - mp) * (1 - mp)
	var fade_m := 1.0 if ds < 8 else maxf(0.0, 1 - (q - 8) / 14.0)
	var flash := F == SPLIT - 5 or F == SPLIT - 4
	var mal := me * fade_m * (1.0 if flash else 0.92)
	moon.position = Vector2(round(moon_x), round(moon_y + (1 - me) * 26))
	moon.modulate.a = mal
	moon.scale = Vector2.ONE * (19.0 / 18.0 if flash else 1.0)
	moon_glow.position = moon.position
	moon_glow.modulate.a = mal * (0.55 if flash else 0.32)
	moon_glow.scale = Vector2.ONE * (1.5 if flash else 1.0)
	# Rion
	var behind: bool = g.back and not kill
	var front_z := 0 if behind else 4
	rion.z_index = front_z
	if g.sil:
		var gr := g.duplicate()
		gr.cx -= 1
		gr.lift += 1
		_set_rion(rim, gr, 0.95, Color("#fff4c8"), 1.0)
		_set_rion(rion, g, 1.0, Color("#141a33"), 1.0)
	else:
		rim.visible = false
		_set_rion(rion, g, 1.0, Color.WHITE, 0.0)
	var trailing := (F > LEAP and F < APEX) or (F >= CUT and F < LAND)
	for k in 2:
		if trailing and not behind:
			_set_rion(ghosts[k], geo(f - (k + 1)), 0.14 * (2 - k), Color("#fff4c8"), 1.0)
		else:
			ghosts[k].visible = false
	var sw: float = 18.0 * 1.6 * maxf(0.35, 1 - g.lift / 90.0)
	shadow.visible = g.lift > 2 and not behind
	shadow.position = Vector2(g.cx - sw / 2, G - 1)
	shadow.size = Vector2(sw, 1)
	# มอน
	piece_up.visible = false
	piece_dn.visible = false
	wound_mask.visible = false
	mon.visible = true
	if ds < 0:
		var mk := "%s_%d" % [foe, posmod(int(floor(f / (6.0 if F >= LAND else 4.0))), 3)]
		var mt := _tex(mk)
		mon.texture = mt
		mon.position = Vector2(mx0 + round((mw - mt.get_width()) / 2.0), G - mt.get_height())
		mon.material.set_shader_parameter("amount", 0.0)
	elif kill:
		mon.visible = false
		var s := 1.2 * q + 0.16 * q * q
		for pg in [piece_up, piece_dn]:
			pg.visible = true
			pg.texture = _tex(foe + "_0")
			pg.material.set_shader_parameter("tint", Color.WHITE)
			pg.material.set_shader_parameter("amount", 1.0 if ds < 2 else 0.0)
			pg.material.set_shader_parameter("dissolve", clamp((q - 8) / 8.0, 0.0, 1.0))
		piece_dn.position = piece_dn.get_meta("c") + Vector2(0.35 * q, 0)
		piece_dn.rotation = 0.004 * q * q
		piece_up.position = piece_up.get_meta("c") + chord * s + Vector2(0, 0.08 * q * q)
		piece_up.rotation = -min(1.4, 0.006 * q * q)
		if new_frame and ds == 8:
			ash_up.restart()
			ash_dn.restart()
	else:
		var open: int = [0, 2, 3, 2, 1][ds] if ds < 5 else 0
		var mk := (foe + "_6") if ds < 10 else "%s_%d" % [foe, posmod(int(floor(f / 4.0)), 3)]
		var mt := _tex(mk)
		var kb: float = -roundf(3 * (1 - q / 8.0)) if ds < 8 else 0.0
		var white := 1.0 if ds < 2 else 0.0
		if open > 0 and mt.get_width() == mw and mt.get_height() == mh:
			mon.visible = false
			for pg in [piece_up, piece_dn]:
				pg.visible = true
				pg.texture = mt
				pg.rotation = 0
				pg.material.set_shader_parameter("tint", Color.WHITE)
				pg.material.set_shader_parameter("amount", white)
				pg.material.set_shader_parameter("dissolve", 0.0)
			piece_dn.position = piece_dn.get_meta("c")
			piece_up.position = piece_up.get_meta("c") + chord * open
		else:
			mon.texture = mt
			mon.position = Vector2(mx0 + kb + round((mw - mt.get_width()) / 2.0), G - mt.get_height())
			mon.material.set_shader_parameter("tint", Color.WHITE)
			mon.material.set_shader_parameter("amount", white)
		if ds < 40:
			wound_mask.visible = true
			wound_mask.texture = mt
			wound_mask.position = Vector2(mx0 + kb + round((mw - mt.get_width()) / 2.0), G - mt.get_height())
			wound_dark.default_color = Color(42 / 255.0, 26 / 255.0, 20 / 255.0, 0.7 * (1 - q / 40.0))
			wound_lit.default_color = Color("#fff4c8") if ds < 10 else Color(232 / 255.0, 200 / 255.0, 120 / 255.0, 1 - q / 40.0)
	# รอยเสี้ยว
	trail_p = minf(1.0, (f - CUT + 1) / float(LAND - CUT)) if F >= CUT and ds < 2 else 0.0
	trail_lit = 1.0 if flash else (0.55 if F >= LAND else 1.0)
	trail.queue_redraw()
	trail_glow.queue_redraw()
	# อนุภาค: ลมหายใจ · ฝุ่น · ประกาย
	if new_frame:
		if F >= TONBO + 4 and F < RUN and (F - TONBO - 4) % 10 == 0:
			breath.position = Vector2(g.cx - 18, G - 58)
			breath.restart()
		for ev in [[LEAP, x0, 1.0, 1.2], [LAND, xland, -1.0, 1.2], [HOME - 2, float(home), 1.0, 0.6]]:
			if F == ev[0]:
				dust.position = Vector2(ev[1], G - 1)
				dust.direction = Vector2(ev[2], -0.35)
				dust.scale_amount_max = 3.0 * ev[3]
				dust.restart()
		if ds == 0:
			sparks.position = cut(0.5)
			sparks.restart()
	flash_spr.visible = ds >= 0 and ds < 4
	if flash_spr.visible:
		flash_spr.position = cut(0.5)
		flash_spr.scale = Vector2.ONE * (0.6 + q * 0.35)
		flash_spr.modulate.a = 1 - q / 4.0
	# ตัวหนังสือ
	lbl_hit.visible = ds >= 0 and ds < 14
	lbl_hit.text = "ขาด!!" if kill else "ฉับ!!"
	lbl_hit.position = Vector2(min(W - 44, mx0 + mw + 4), max(18, G - bh - 4 - min(5, ds)) - 14)
	lbl_dots.visible = F >= LAND + 3 and ds < 0
	if lbl_dots.visible:
		var k := F - LAND - 3
		lbl_dots.modulate.a = minf(1.0, k / 2.0)
		lbl_dots.text = ".".repeat(1 + mini(2, k >> 2))
		lbl_dots.position = Vector2(mcx - 4, G - bh - 6 - 12)
	bubble.visible = F >= SHOUT and F < RUN + 3
	if bubble.visible:
		var d := F - SHOUT
		var sc: float = 1.3 - d * 0.15 if d < 2 else 1.0
		var bx: float = max(2.0, min(W - bubble_w * sc - 2, g.cx - bubble_w * sc / 2))
		var by: float = max(2.0, max(14.0, G - g.lift - 74) - 19 - 8)
		bubble.position = Vector2(bx, by)
		bubble.scale = Vector2(sc, sc)
		bubble.modulate.a = 1.0 if F < RUN else (RUN + 3 - f) / 3.0
		var tl: float = clamp((g.cx - bx) / sc, 8, bubble_w - 8)
		bubble.get_node("tail").position.x = tl
		bubble.get_node("tail_line").position.x = tl
	lbl_dmg.visible = ds >= 0 and ds < 22
	lbl_tag.visible = lbl_dmg.visible
	if lbl_dmg.visible:
		var pop: float = [-6, -10, -8][ds] if ds < 3 else -8 - minf(6.0, (ds - 3) * 0.5)
		var x: float = roundf(clampf(mcx, 30.0, W - 30.0))
		var yy: float = max(18.0, round(max(30.0, G - bh - 14) + pop))
		lbl_dmg.text = str(dmg)
		lbl_dmg.scale = Vector2.ONE * (1.4 if ds == 0 else 1.15 if ds == 1 else 1.0)
		lbl_dmg.position = Vector2(x - 80, yy - 14)
		lbl_dmg.modulate.a = 1.0 if ds < 16 else 1 - (ds - 16) / 6.0
		lbl_tag.text = ("อ่อนแอ! · " if aff > 0 else "ต้านทาน · " if aff < 0 else "") + ("HP %d · ฟันเดียวขาด" % hp if kill else "HP %d รอด" % hp)
		lbl_tag.position = Vector2(x - 80, yy - 2)
		lbl_tag.modulate.a = lbl_dmg.modulate.a
