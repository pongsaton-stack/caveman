extends Node2D
## ฐานฉากต่อสู้ในห้องทดลอง Godot (ใช้ร่วมทุกท่า) — ท่าแต่ละท่า = สคริปต์ที่ extends ไฟล์นี้ แล้วเขียนเฉพาะส่วนของท่า:
##   tech_id() · end_frame() · stops() หยุดภาพ [[เฟรม, วินาที]] · setup() · frame(f, F, fresh) ทุกเฟรมจอ · sounds(F) ทุกเฟรมเต็มใหม่
##   draw_fx(n) วาดหน้าสุด · draw_mid(n) ระหว่างมอนกับ Rion · draw_back(n) วาดหลังมอน (พิกเซลแบบ fbPx ของหน้าเว็บ) · caption()
## ฐานมีให้: ฉากหลัง 3 ฉาก + ของขยับในฉาก (หยุดได้) · เพลงต่อสู้ (หลบตอนกระแทก) · Rion ผืน 120x112 เท้าแถว 108 (หมุนรอบแถว 72)
##   มอน 5 ตัวแรก + ขอบเนื้อ · กล้องสั่น · หยุดภาพ · บับเบิล/ตัวเลข/คำเสียง · ร่างติดตา · ดาว/ประกาย/ฝุ่น/ไอ
##   เสียงสังเคราะห์สูตรเดียวกับหน้าเว็บ (บัส LabSfx ก้อง + คอมเพรส) · เมนูเลือกท่า/มอน/ฉาก
## ไม่ใช่ของในเกม (tests/ ไม่ถูก export กับเกม) · ห้ามมี class_name (กฎ 2) · ภาพร่าง/ฉาก/เพลงอยู่ในโฟลเดอร์ .gdignore → โหลดตรงจากไฟล์
##   (หน้าเว็บ lab คัดลอกไปที่ทางเดิมแบบ import ได้ → โหลดผ่าน load())
## อัดวิดีโอ: xvfb-run -a <godot> --path . --rendering-driver opengl3 --write-movie <dir>/f.png --fixed-fps 60 res://tests/lab/<ท่า>.tscn -- --foe=M01 [--bg=frost_volcano] [--music=0]
##   (ระบุ --foe = โหมดอัด: เล่นทันทีแล้วปิดเอง · ได้ภาพ 600x336 + f.wav)
## ถ่ายเฉพาะเฟรม (ตรวจเร็ว ไม่ต้องอัดทั้งเรื่อง): xvfb-run -a <godot> --path . --rendering-driver opengl3 --fixed-fps 60 res://tests/lab/<ท่า>.tscn -- --foe=M01 --snap=30,36,40 --snapdir=<dir>
##   → <dir>/<ท่า>_<มอน>_f030.png ขนาด 300x168
## ตารางวิจัยรอบ 2 (r2_tables.gd): feel(พลัง) = หยุดภาพ/จอสั่น/กระเด็นตามระดับท่า · react(สาย) = ปฏิกิริยาร่างมอนตัวนี้ · debris_at() = เศษตามวัสดุ (เลือด/เจล/ขนนก/เปลือก...)

const W := 300
const H := 168
const G := 158
const SEC := 0.06
const PX := "res://assets/sprites/pixellab_draft/px_set/"
const MPX := "res://assets/sprites/monsters_px_draft/"
const FPX := "res://assets/sprites/flow_draft/bt/"
const WSK := "res://assets/sprites/pixellab_draft/weapon_skin/"   # ไม้เบสบอลระดับอื่นบนภาพ pls_bat* (tools/sprites/bat_tiers.py)
## ปุ่มเลือกอาวุธ (kwan 26 ต.ค.): สายของท่า → อาวุธ 5 ระดับใน weapons.csv · ชื่อสั้นบนปุ่ม · ภาพเปลี่ยนได้เฉพาะไม้เบสบอล (WSK) · มีดยังเป็นภาพมีดครัว
const SCHOOL := {"bl": "คม", "bt": "ทุบ", "pt": "แทง", "rg": "ยิง", "dv": "กล", "fs": "มือเปล่า"}
const WSHORT := {"SL-1": "มีดครัว", "SL-2": "อีโต้", "SL-3": "พร้าเลื่อย", "SL-4": "ใบพัดลม", "SL-5": "มีดเชฟ",
	"CR-1": "ไม้ร้าว", "CR-2": "อลูมิเนียม", "CR-3": "ตอกตะปู", "CR-4": "หัวเฟือง", "CR-5": "โฮมรัน"}   # ภาพ Rion จาก Flow (Muse เจน · flow_to_px.py) ชื่อ flw_*
const MUSIC := "res://docs/art-bible/audio/battle_bgm_preview.mp3"   # เพลงต่อสู้แนวรอบ 4 (kwan 5 ต.ค.) อัดจากหน้าเว็บ
const FOES := ["M01", "M03", "M06", "M15", "B1"]   # มอน 5 ตัวแรกของหน้าฉากต่อสู้ (kwan 25 ต.ค.)
## ท่าที่ย้ายมาแล้ว: [id, ชื่อในเมนู, ฉาก]
const TECHS := [["bl0", "ฟัน", "res://tests/lab/blc_bl0.tscn"], ["bl1", "เขี้ยวพุ่ง", "res://tests/lab/blc_bl1.tscn"], ["bl2", "เขี้ยวพัน", "res://tests/lab/wr_bl2.tscn"],
	["bl7", "ตัดเอ็น", "res://tests/lab/aot_bl7.tscn"], ["bl8", "ผ่าเกราะ", "res://tests/lab/kw_bl8.tscn"], ["bl9", "จันทร์เสี้ยว", "res://tests/lab/jg_bl9.tscn"],
	["★", "เขี้ยวพุ่ง", "res://tests/lab/glim_bl1.tscn"], ["★", "กวาด", "res://tests/lab/glim_bl3.tscn"], ["★", "ปาดไว", "res://tests/lab/glim_bl5.tscn"],
	["มอนตี", "โดน", "res://tests/lab/ma_hit.tscn"], ["มอนตี", "ตั้งรับ", "res://tests/lab/ma_guard.tscn"],
	["ทุบ", "Flow", "res://tests/lab/flw_bt0.tscn"], ["ทุบ", "PL", "res://tests/lab/pl_bt0.tscn"]]   # แถวบน 6 ท่า · แถวล่าง ★ = ประกายได้ท่าใหม่ + มอนตีกลับ + ท่าภาพ Flow
## ฉากหลัง (เหมือน combat_bgs ของ anim_test_build.py): ไฟล์ · ขยายกี่เท่า · เส้นพื้น (สัดส่วนความสูง) → ครอป 300x168 พื้นที่แถว 158
const BGS := {"frost_volcano": ["ภูเขาไฟหิมะ", "res://docs/art-bible/pixellab_test/bg_frost_volcano.jpg", 1, 1250.0 / 1376.0, true],
	"ash_village": ["หมู่บ้านเถ้า", "res://docs/art-bible/pixellab_test/bg_ash_village.jpg", 3, 0.69, false],
	"flooded_ruins": ["เมืองน้ำท่วม", "res://docs/art-bible/pixellab_test/bg_flooded_ruins.jpg", 3, 0.80, false]}
## ดาเมจ [ค่า, +1 อ่อนแอ/−1 ต้านทาน, จำนวนครั้ง] = csHit(ท่า, มอน) ของหน้าเว็บ (prof 20 + มีดครัว 14) · ยังไม่ต่อสูตรเกมตรง
const DMG := {"bl0": {"M01": [55, 0, 1], "M03": [17, -1, 1], "M06": [53, 0, 1], "M15": [57, 1, 1], "B1": [31, -1, 1]},
	"bl1": {"M01": [80, 0, 1], "M03": [24, -1, 1], "M06": [77, 0, 1], "M15": [82, 1, 1], "B1": [45, -1, 1]},
	"bl3": {"M01": [50, 0, 1], "M03": [15, -1, 1], "M06": [48, 0, 1], "M15": [51, 1, 1], "B1": [28, -1, 1]},
	"bl5": {"M01": [44, 0, 1], "M03": [13, -1, 1], "M06": [42, 0, 1], "M15": [45, 1, 1], "B1": [25, -1, 1]},
	"bl2": {"M01": [34, 0, 3], "M03": [10, -1, 3], "M06": [33, 0, 3], "M15": [35, 1, 3], "B1": [19, -1, 3]},
	"bl7": {"M01": [44, 0, 1], "M03": [13, -1, 1], "M06": [42, 0, 1], "M15": [45, 1, 1], "B1": [25, -1, 1]},
	"bt0": {"M01": [27, -1, 1], "M03": [90, 1, 1], "M06": [51, -1, 1], "M15": [57, 0, 1], "B1": [56, 1, 1]},   # ไม้เบสบอลอลูมิเนียม CR-2 (ฐาน 28) · prof 20 · ทุบ
	"bl8": {"M01": [69, 0, 1], "M03": [22, -1, 1], "M06": [67, 0, 1], "M15": [74, 1, 1], "B1": [43, -1, 1]},
	"bl9": {"M01": [110, 0, 1], "M03": [33, -1, 1], "M06": [106, 0, 1], "M15": [113, 1, 1], "B1": [62, -1, 1]}}
## ทางปลายมีดของภาพฟัน pls_atk_bl (วัดอัตโนมัติ blade_tip.py → DATA.swing ของหน้าเว็บ): จุดหมุนไหล่ P · มุม A · รัศมี R · ภาพแรก f0
const SWING := {"P": [62, 68], "f0": 4, "A": [-14, -200.7, -237.4, -248.2], "R": [24.7, 39.6, 29.7, 26.9], "TAIL": -140}
const SR := 32000
const R2 := preload("res://tests/lab/r2_tables.gd")
const HARD_BODIES := ["เกราะ", "หิน", "กระดูก", "กลไก"]   # ร้าวได้ (ตารางปฏิกิริยา: ร้าวเฉพาะวัสดุเปราะ · ไม้ = แตกตามเสี้ยน)

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
var bg_id := "frost_volcano"
var recording := false
var playing := false
var t := 0.0
var amb_t := 0.0
var stopped := false
var hold := 0.0
var stops_done := {}
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
var hits := 1
var kill := false

var cam: Camera2D
var bg_tex: Texture2D
var amb: Node2D
var dim: ColorRect
var mon: Sprite2D
var back_fx: Node2D
var front_fx: Node2D
var mid_fx: Node2D
var flakes: CPUParticles2D
var embers: CPUParticles2D
var lamp: Sprite2D
var mist_tex: Texture2D
var puff_p: CPUParticles2D
var dust: CPUParticles2D
var sparks: CPUParticles2D
var star: Node2D
var star_r := 0.0
var star_c2 := Color("#ffd27a")
var flash_spr: Sprite2D
var burst_f := -100
var burst_pos := Vector2.ZERO
var rion: Sprite2D
var ghosts: Array[Sprite2D] = []
var n_ghost := 0
var ui: CanvasLayer
var words: Array[Label] = []
var n_word := 0
var pops: Array = []   # [ตัวเลข, ป้าย] หลายชุด
var n_pop := 0
var bubble: Node2D
var bubble_lbl: Label
var bubble_panel: Panel
var caption_lbl: Label
var menu: Control
var players: Array[AudioStreamPlayer] = []
var sfx_cache := {}
var snaps := {}
var snap_dir := ""
var weapons: Array = []   # [รหัส, ชื่อ, weapon_base หรือ -1] ของสายท่านี้
var weapon_id := ""
var speed := 1.0   # ความเร็วเล่น (ปุ่มในเมนู · เก็บใน Engine meta "lab_speed")
var debris: Array = []   # [kind, สี, x, y, vx, vy, g, life, เฟรมเกิด]

# ── ส่วนที่ท่าแต่ละท่าเขียนทับ ──────────────────────────
func tech_id() -> String: return "bl0"
func end_frame() -> int: return 100
func stops() -> Array: return []
func setup() -> void: pass
func frame(_f: float, _F: int, _fresh: bool) -> void: pass
func sounds(_F: int) -> void: pass
func draw_fx(_n: Node2D) -> void: pass
func draw_back(_n: Node2D) -> void: pass
func draw_mid(_n: Node2D) -> void: pass
func caption() -> String: return ""

# ── เริ่ม ─────────────────────────────────────────────
func _ready() -> void:
	foe = str(Engine.get_meta("lab_foe", "M01"))
	bg_id = str(Engine.get_meta("lab_bg", "frost_volcano"))
	speed = float(Engine.get_meta("lab_speed", 1.0))
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--foe="):
			foe = a.substr(6)
			recording = true
		elif a.begins_with("--bg="):
			bg_id = a.substr(5)
		elif a == "--music=0":
			Engine.set_meta("lab_music_off", true)
		elif a.begins_with("--snap="):
			for v in a.substr(7).split(","):
				snaps[int(v)] = false
		elif a.begins_with("--snapdir="):
			snap_dir = a.substr(10)
		elif a.begins_with("--speed="):
			speed = float(a.substr(8))
		elif a.begins_with("--weapon="):   # ทดสอบอาวุธจากบรรทัดคำสั่ง เช่น --weapon=CR-4
			Engine.set_meta("lab_weapon_" + tech_id().substr(0, 2), a.substr(9))
	if not BGS.has(bg_id):
		bg_id = "frost_volcano"
	playing = recording or bool(Engine.get_meta("lab_auto", false))
	var win := get_window()
	win.content_scale_size = Vector2i(W, H)
	win.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	win.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP
	if recording:
		win.size = Vector2i(W * 2, H * 2) if snaps.is_empty() else Vector2i(W, H)
	_audio_bus()
	_load_monster()
	_build_stage()
	setup()
	_build_ui()
	_step()

func _img(path: String) -> Image:
	if ResourceLoader.exists(path):   # หน้าเว็บ lab: ไฟล์ถูก import แล้ว
		return (load(path) as Texture2D).get_image()
	return Image.load_from_file(ProjectSettings.globalize_path(path))

func tx(key: String) -> Texture2D:
	if not tex.has(key):
		var path := (PX + key + ".png") if key.begins_with("pls_") else ((FPX + key + ".png") if key.begins_with("flw_") else (MPX + key + ".png"))
		if key.begins_with("pls_bat") and weapon_id.begins_with("CR-") and weapon_id != "CR-2":
			path = WSK + "wsk_%s__%s.png" % [key, weapon_id]
		tex[key] = ImageTexture.create_from_image(_img(path))
	return tex[key]

## เนื้อมอน (อัลฟา > 100 เหมือน kwAlpha บนเว็บ)
func solid(x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < mw and y < mh and mon_img.get_pixel(x, y).a > 0.392

func rgb(x: int, y: int) -> Color:
	var c := mon_img.get_pixel(clampi(x, 0, mw - 1), clampi(y, 0, mh - 1))
	c.a = 1.0
	return c

## ขอบซ้าย/ขวาของเนื้อมอนที่แถว row (ไม่มีเนื้อ = หาแถวล่างลงไป) · เหมือน wrEdges
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
	var d: Array = DMG.get(tech_id(), {}).get(foe, [0, 0, 1])
	dmg = d[0]
	_load_weapons()
	aff = d[1]
	hits = d[2]
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

func school() -> String:
	return SCHOOL.get(tech_id().substr(0, 2), "")

## อาวุธของสายท่า + ที่เลือกไว้ (Engine meta lab_weapon_<bl/bt…> · ชื่อ meta ต้องเป็นอักษรอังกฤษ · ค่าเริ่ม = ชิ้นที่มี weapon_base = ชิ้นที่ตาราง DMG ใช้)
## ดาเมจคิดใหม่เฉพาะเมื่อทั้งสองชิ้นมี weapon_base (ATK = 20 + prof 20 × 1.6 + ฐาน) · ชิ้นที่ kwan ยังไม่กำหนดฐาน = ดาเมจเท่าเดิม
func _load_weapons() -> void:
	var sc := school()
	if sc == "":
		return
	var base_id := ""
	for r in CsvDb.load_csv("res://data/weapons.csv"):
		if str(r.school) == sc:
			var b := int(r.weapon_base) if str(r.weapon_base) != "" else -1
			weapons.append([str(r.weapon_id), str(r.name), b])
			if b >= 0 and base_id == "":
				base_id = str(r.weapon_id)
	weapon_id = str(Engine.get_meta("lab_weapon_" + tech_id().substr(0, 2), base_id))
	var wb := -1
	var db := -1
	for w in weapons:
		if w[0] == weapon_id:
			wb = w[2]
		if w[0] == base_id:
			db = w[2]
	if wb >= 0 and db >= 0 and wb != db:
		dmg = int(roundf(dmg * (52.0 + wb) / (52.0 + db)))

func weapon_name() -> String:
	for w in weapons:
		if w[0] == weapon_id:
			return w[1] + ("" if w[2] >= 0 else " (ยังไม่มีค่าพลัง)")
	return ""

func place_monster(mx: int) -> void:
	mx0 = int(round(mx - mw / 2.0))
	mcx = mx0 + mw / 2.0

## ภาพมอน (idle 0–2 · hurt 6) วางกลางช่อง เท้าที่พื้น · ย้อมสี tint เท่า amt · ยืด/หด sx sy รอบกลางเท้า
func show_mon(key: String, dx := 0.0, amt := 0.0, tint := Color.WHITE, sx := 1.0, sy := 1.0) -> void:
	var mt := tx(key)
	mon.visible = true
	mon.texture = mt
	mon.offset = Vector2(-mt.get_width() / 2.0, -mt.get_height())   # ยืด/หดรอบกลางเท้า · มุมซ้ายบนตรงพิกเซลแบบหน้าเว็บ
	mon.position = Vector2(mx0 + round(dx) + round((mw - mt.get_width()) / 2.0) + mt.get_width() / 2.0, G)
	mon.scale = Vector2(sx, sy)
	mon.material.set_shader_parameter("tint", tint)
	mon.material.set_shader_parameter("amount", amt)

func idle_key(f: float, slow := 4.0) -> String:
	return "%s_%d" % [foe, posmod(int(floor(f / slow)), 3)]

func hurt_key() -> String:
	return foe + "_6"

## ปลายมีดภาพฟัน: มุม (องศา) → จุดในผืน 120x112 (เหมือน blcSwingPt)
func swing_pt(a: float) -> Vector2:
	var A: Array = SWING.A
	var R: Array = SWING.R
	var k := 0
	while k < A.size() - 2 and a < A[k + 1]:
		k += 1
	var u: float = (a - A[k]) / (A[k + 1] - A[k])
	var r: float = R[k] + (R[k + 1] - R[k]) * u
	var q := deg_to_rad(a)
	return Vector2(SWING.P[0] + cos(q) * r, SWING.P[1] + sin(q) * r)

func fb_hash(a: float, b: float, c: float) -> float:   # fbHash ของหน้าเว็บ
	return fposmod(sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453, 1.0)

func bg_h(i: float) -> float:   # bgH ของหน้าเว็บ
	return fposmod(sin(i * 12.9898 + 78.233) * 43758.5453, 1.0)

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
	s.material = fx_mat()
	s.z_index = z
	add_child(s)
	return s

## วาง Rion ตาม geo ของท่า: {cx, lift, key, flip, sx, sy, rot} · หมุน = รอบแถว 72 ของผืน · ไม่หมุน = ยึดเท้า (แถว 108) เหมือน aotDraw
func set_rion(s: Sprite2D, g: Dictionary, alpha := 1.0, tint := Color.WHITE, amt := 0.0) -> void:
	var rot: float = g.get("rot", 0.0)
	var py := 72.0 if rot != 0.0 else 108.0
	if g.get("lean", 0.0) != 0.0:   # เอนตัว = หมุนรอบเท้า (blcState lean)
		rot = g.lean
	s.texture = tx(g.key)
	s.flip_h = g.get("flip", false)
	s.offset = Vector2(-60, -py)
	s.position = Vector2(round(g.cx), round(G - g.lift - (108 - py)))
	s.rotation = rot
	s.scale = Vector2(g.get("sx", 1.0), g.get("sy", 1.0))
	s.modulate.a = alpha
	s.material.set_shader_parameter("tint", tint)
	s.material.set_shader_parameter("amount", amt)
	s.visible = alpha > 0.0

## ร่างติดตา (ต่อเฟรม) · behind = หลังมอน
func ghost(g: Dictionary, alpha: float, tint := Color.WHITE, amt := 0.0, behind := false) -> void:
	if n_ghost >= ghosts.size():
		ghosts.append(rion_sprite())
	var s: Sprite2D = ghosts[n_ghost]
	n_ghost += 1
	s.z_index = 0 if behind else 3
	set_rion(s, g, alpha, tint, amt)

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

func text_w(text: String, size: int) -> float:
	return (load("res://assets/fonts/game_font.tres") as Font).get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x

# ── วาดพิกเซล (แบบ fbPx/pkStar/pkSlashLine ของหน้าเว็บ) ───────────
func px(n: Node2D, x: float, y: float, col: Color, w := 1.0, h := 1.0) -> void:
	n.draw_rect(Rect2(round(x), round(y), w, h), col)

## ดาวกระแทก 8 แฉก (pkStar)
func star_px(n: Node2D, x: float, y: float, r: float, c1: Color, c2: Color) -> void:
	for i in 8:
		var a := i * PI / 4
		var L := r * (0.55 if i % 2 else 1.0)
		for k in int(L) + 1:
			px(n, x + cos(a) * k, y + sin(a) * k, c1 if k < L * 0.5 else c2, 2, 2)
	px(n, x - 2, y - 2, c1, 4, 4)

## แผลแสง 3 ชั้น หนากลาง บางปลาย (pkSlashLine)
func slash_line(n: Node2D, x0: float, y0: float, x1: float, y1: float, th: float, prog: float, al: float) -> void:
	if al <= 0.0:
		return
	var cnt := maxi(8, int(round(Vector2(x1 - x0, y1 - y0).length() / 2)))
	var m := int(round(cnt * prog))
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
		var col: Color = layer[0]
		col.a = al
		for i in m + 1:
			var u := float(i) / cnt
			var w: float = maxf(0.0, th * pow(sin(PI * u), 0.6) + layer[1])
			if w < 1.0:
				continue
			px(n, x0 + (x1 - x0) * u - w / 2, y0 + (y1 - y0) * u - w / 2, col, ceil(w), ceil(w))

## ก้อนกลม (ไอ/ควัน/เลือด · pxDisc)
func disc(n: Node2D, x: float, y: float, r: float, col: Color) -> void:
	var R := maxi(1, int(round(r)))
	for j in range(-R, R + 1):
		var w := int(round(sqrt(maxf(0.0, R * R - j * j + R * 0.6))))
		px(n, x - w, y + j, col, maxi(1, 2 * w), 1)

# ── ฉากหลัง บรรยากาศ อนุภาค ─────────────────────────────
func _build_stage() -> void:
	RenderingServer.set_default_clear_color(Color.BLACK)
	cam = Camera2D.new()
	cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
	add_child(cam)
	cam.make_current()
	ui = CanvasLayer.new()
	add_child(ui)
	var b: Array = BGS[bg_id]
	var bimg := _img(b[1])
	if b[2] > 1:
		bimg.resize(bimg.get_width() / b[2], bimg.get_height() / b[2], Image.INTERPOLATE_NEAREST)
	var nh := int(round(bimg.get_height() * 300.0 / bimg.get_width()))
	bimg.resize(300, nh, Image.INTERPOLATE_LANCZOS if b[4] else Image.INTERPOLATE_NEAREST)
	var y0 := clampi(int(round(nh * b[3])) - 158, 0, nh - H)
	bg_tex = ImageTexture.create_from_image(bimg.get_region(Rect2i(0, y0, 300, H)))
	var bg := Sprite2D.new()
	bg.centered = false
	bg.texture = bg_tex
	add_child(bg)
	mist_tex = radial(Color("#e6eef8"), 44)
	amb = Node2D.new()
	amb.draw.connect(_draw_amb)
	add_child(amb)
	_build_ambient_particles()
	dim = ColorRect.new()
	dim.color = Color("#10142a")
	dim.position = Vector2(-8, -8)
	dim.size = Vector2(W + 16, H + 16)
	dim.modulate.a = 0.0
	add_child(dim)
	back_fx = Node2D.new()
	back_fx.draw.connect(func(): draw_back(back_fx))
	add_child(back_fx)
	rion = rion_sprite()
	mon = Sprite2D.new()
	mon.centered = false
	mon.material = fx_mat()
	mon.z_index = 1
	add_child(mon)
	mid_fx = Node2D.new()
	mid_fx.z_index = 2
	mid_fx.draw.connect(func(): draw_mid(mid_fx))
	add_child(mid_fx)
	front_fx = Node2D.new()
	front_fx.z_index = 5
	front_fx.draw.connect(func():
		_draw_debris(front_fx)
		draw_fx(front_fx))
	add_child(front_fx)
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

func _build_ambient_particles() -> void:
	if bg_id == "frost_volcano" or bg_id == "ash_village":   # หิมะ / เถ้าร่วง
		flakes = particles(75 if bg_id == "frost_volcano" else 55, 7.0, 0)
		flakes.one_shot = false
		flakes.explosiveness = 0.0
		flakes.emitting = true
		flakes.position = Vector2(W / 2.0 + 20, -4)
		flakes.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		flakes.emission_rect_extents = Vector2(W * 0.6, 2)
		flakes.direction = Vector2(-0.3, 1) if bg_id == "frost_volcano" else Vector2(-0.8, 1)
		flakes.spread = 10
		flakes.gravity = Vector2(0, 2)
		flakes.initial_velocity_min = 18 if bg_id == "frost_volcano" else 10
		flakes.initial_velocity_max = 30 if bg_id == "frost_volcano" else 18
		flakes.color = Color(0.95, 0.96, 1.0, 0.75) if bg_id == "frost_volcano" else Color(0.84, 0.8, 0.75, 0.6)
		flakes.preprocess = 10
	if bg_id == "frost_volcano":   # ไฟตะเกียง: แสงวูบ (บวกแสง) + ถ่านลอย
		lamp = Sprite2D.new()
		lamp.texture = radial(Color("#ff9a40"), 68)
		lamp.material = add_mat()
		lamp.position = Vector2(208, 72)
		add_child(lamp)
		embers = _embers(Vector2(208, 70), Vector2(4, 1), 6, 1.4, 14, 20)
	elif bg_id == "ash_village":   # ถ่านไฟลอยจากหมู่บ้าน
		embers = _embers(Vector2(240, 100), Vector2(60, 2), 14, 5.0, 14, 24)
		embers.direction = Vector2(-0.1, -1)

func _embers(pos: Vector2, ext: Vector2, amount: int, life: float, v0: float, v1: float) -> CPUParticles2D:
	var p := particles(amount, life, 0)
	p.one_shot = false
	p.explosiveness = 0.0
	p.emitting = true
	p.position = pos
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = ext
	p.direction = Vector2(0, -1)
	p.spread = 15
	p.gravity = Vector2.ZERO
	p.initial_velocity_min = v0
	p.initial_velocity_max = v1
	p.color_ramp = ramp([Color("#ffd27a"), Color("#ff7a2a"), Color(1, 0.48, 0.16, 0)])
	p.preprocess = life
	return p

## ของขยับในฉาก (แบบ bgAmbient ของหน้าเว็บ) · เวลาฉาก amb_t หยุดได้
func _draw_amb() -> void:
	var tt := amb_t
	if bg_id == "frost_volcano":
		_fall(168, 186, 0, 52, tt, 26, 11, 55)
		_fall(223, 242, 0, 26, tt, 18, 31, 55)   # น้ำตกน้ำแข็ง 2 สาย
		for i in 3:   # หมอกในหุบเหว ลอยช้า
			var x := 70 + fposmod(tt * (3 + i) + i * 40, 110.0)
			var y := 52 + i * 12 + sin(tt * 0.4 + i) * 3
			amb.draw_texture(mist_tex, Vector2(x - 22, y - 22), Color(1, 1, 1, 0.10))
		for dx in range(-4, 5):   # เปลวไฟพิกเซล
			var h := maxi(0, 9 - absi(dx) * 2 + int(round(sin(tt * 14 + dx * 1.7) * 1.5 + sin(tt * 23 + dx))))
			for k in h:
				var c := Color("#d8401c") if k > h * 0.7 else Color("#ff9a30") if k > h * 0.35 else Color("#ffe68a")
				c.a = 0.85
				px(amb, 208 + dx, 79 - k, c)
	elif bg_id == "ash_village":
		for y in range(125, 168):   # ธงขาดบนเสา: แถวผ้าเหลื่อมตามคลื่นลม
			var k := (y - 125) / 43.0
			var off := int(round(sin(tt * 2.4 - y * 0.22) * 1.6 * k))
			if off != 0:
				amb.draw_texture_rect_region(bg_tex, Rect2(207 + off, y, 26, 1), Rect2(207, y, 26, 1))
		for c in [[232, 7, 0], [290, 11, 9]]:   # ควันปล่อง
			for i in 5:
				var ph := fposmod(tt * 0.25 + i / 5.0 + bg_h(c[2]), 1.0)
				var col := Color("#5d544d") if i % 2 else Color("#7a7068")
				col.a = 0.4 * (1 - ph) * minf(1.0, ph * 6)
				amb.draw_circle(Vector2(c[0] - ph * 18 + sin(tt + i) * 1.5, c[1] - ph * 14), 2 + ph * 7, col)
	elif bg_id == "flooded_ruins":
		_fall(83, 92, 33, 56, tt, 14, 3, 40)
		_fall(117, 123, 34, 56, tt, 9, 13, 40)
		_fall(96, 101, 6, 18, tt, 6, 23, 35)
		_fall(273, 287, 62, 80, tt, 12, 43, 40)   # น้ำตก 4 สาย
		_foam(88, 57, 10, tt, 5)
		_foam(120, 57, 7, tt, 15)
		_foam(280, 81, 12, tt, 25)
		for i in 14:   # ประกายบนแอ่งน้ำ
			var ph := fposmod(tt * 0.9 + bg_h(500 + i), 1.0)
			var a := pow(maxf(0.0, sin(ph * PI)), 3)
			var q: Array = [27, 112, 72, 16] if i % 2 else [202, 102, 76, 15]
			var x: float = q[0] + bg_h(520 + i) * q[2]
			var y: float = q[1] + bg_h(540 + i) * q[3]
			px(amb, x, y, Color(1, 1, 1, a))
			if a > 0.6:
				px(amb, x - 1, y, Color(0.85, 0.96, 1, a * 0.5), 3, 1)
				px(amb, x, y - 1, Color(0.85, 0.96, 1, a * 0.5), 1, 3)
		for j in 3:   # วงน้ำหยด
			var ph := fposmod(tt / 1.6 + j / 3.0, 1.0)
			var n := floorf(tt / 1.6 + j / 3.0)
			var q: Array = [32, 114, 64, 12] if j % 2 else [206, 104, 68, 12]
			var x: float = q[0] + bg_h(n * 7 + j) * q[2]
			var y: float = q[1] + bg_h(n * 7 + j + 3) * q[3]
			var r := 1 + ph * 7
			amb.draw_set_transform(Vector2(round(x) + 0.5, round(y) + 0.5), 0, Vector2(1, 0.4))
			amb.draw_arc(Vector2.ZERO, r, 0, TAU, 24, Color(0.89, 0.97, 1, 0.5 * (1 - ph)), 1.0)
			amb.draw_set_transform(Vector2.ZERO)
		for i in 10:   # ระลอกคลองบน
			var ph := fposmod(tt * 0.5 + bg_h(700 + i), 1.0)
			px(amb, 105 + bg_h(710 + i) * 60 + ph * 6, 2 + bg_h(720 + i) * 14, Color(0.81, 0.94, 0.96, 0.35 * sin(ph * PI)), 2, 1)

func _fall(x0: int, x1: int, y0: int, y1: int, tt: float, n: int, seed: int, sp: float) -> void:   # น้ำตก (bgFall)
	var hh := y1 - y0
	for i in n:
		var x := x0 + floorf(bg_h(seed + i) * (x1 - x0 + 1))
		var len := 2 + floorf(bg_h(seed + i + 50) * 4)
		var y := y0 + fposmod(bg_h(seed + i + 90) * hh + tt * sp * (0.8 + bg_h(seed + i + 7) * 0.5), float(hh))
		var e := minf(1.0, minf((y - y0) / 4.0, (y1 - y) / 4.0))
		var c := Color("#cfefff") if i % 3 else Color.WHITE
		c.a = 0.55 * maxf(0.0, e)
		px(amb, x, y, c, 1, len)

func _foam(cx: float, cy: float, w: float, tt: float, seed: int) -> void:   # ฟองน้ำตก (bgFoam)
	for i in 7:
		var ph := fposmod(tt * 3 + bg_h(seed + i), 1.0)
		var x := cx + (bg_h(seed + i + 20) - 0.5) * w + (ph - 0.5) * 2 * (1 if i % 2 else -1)
		px(amb, x, cy - ph * 4, Color(1, 1, 1, 0.7 * (1 - ph)))

## ทั้งโลกกลั้นหายใจ: ของขยับในฉาก + อนุภาคหยุดนิ่ง
func world_stop(stop: bool) -> void:
	stopped = stop
	for p in [flakes, embers]:
		if p:
			p.speed_scale = 0.0 if stop else 1.0

func dim_to(a: float, col := Color("#10142a")) -> void:
	dim.color = col
	dim.modulate.a = a

func shake(F: int, amount: float) -> void:
	cam.offset = Vector2(round((fb_hash(F, 1, 0) * 2 - 1) * amount), round((fb_hash(F, 2, 0) * 2 - 1) * amount))

func puff(pos: Vector2) -> void:
	puff_p.position = pos
	puff_p.restart()

func dust_at(x: float, dir: float, size := 1.0) -> void:
	dust.position = Vector2(x, G - 1)
	dust.direction = Vector2(dir, -0.35)
	dust.scale_amount_max = 3.0 * size
	dust.restart()

## จุดโดน: ประกายกระเด็น (อนุภาค) + ดาว 8 แฉก + แสงวาบ 4 เฟรม
func burst(pos: Vector2, F: int, c2 := Color("#ffd27a")) -> void:
	burst_f = F
	burst_pos = pos
	star_c2 = c2
	sparks.position = pos
	sparks.restart()

func _draw_star() -> void:
	if star_r > 0.0:
		star_px(star, 0, 0, star_r, Color.WHITE, star_c2)

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

# ── ตารางวิจัยรอบ 2: feel ตามพลังท่า · ปฏิกิริยาตามร่าง · เศษตามวัสดุ ──────────
## ระดับ feel ของท่าพลัง power (ต้นสาย ≤90 · กลาง ≤130 · ปลาย ≤170 · ไม้ตาย) · finisher = จังหวะสังหาร/เกราะแตก (หยุดภาพ 4 เฟรม)
## คืน {hitstop_frames, shake_px, shake_frames, knockback_px, flash_frames} · หยุดภาพเป็นวินาที = hitstop_frames * SEC
func feel(power: int, finisher := false) -> Dictionary:
	if finisher:
		return R2.FEEL[R2.FEEL.size() - 1]
	for row in R2.FEEL:
		if power <= int(row.power_max):
			return row
	return R2.FEEL[R2.FEEL.size() - 2]

## ฮิตกลางทางของท่าหลายฮิต: หยุดภาพครึ่งค่าฐาน (ปัดขึ้น)
func feel_mid(power: int) -> int:
	return ceili(int(feel(power).hitstop_frames) * 0.5)

## ปฏิกิริยาของมอนตัวนี้ต่อการโจมตีสาย atk (คม ทุบ แทง ยิง กล มือเปล่า): {motion, shift, frames, mark, mark_life, ko, debris}
func react(atk: String) -> Dictionary:
	return R2.REACT.get(body + "|" + atk, R2.REACT.get("เนื้อ|" + atk, {}))

func hard_body() -> bool:
	return body in HARD_BODIES

## โปรยเศษตามตารางปฏิกิริยาที่จุดโดน (ทิศ 0° = พุ่งออกจากผิวมอนกลับฝั่ง Rion ทางขวา ให้เห็นบนฉากหลัง ไม่จมในตัวมอน · บวก = ลงล่าง) · ใช้สีตารางเว้นแต่ use_body = สีตัวมอนตรงจุดนั้น (เจล/เปลือก)
func debris_at(pos: Vector2, atk: String, F: int, mul := 1.0) -> void:
	var r := react(atk)
	var big := foe.begins_with("B")   # บอส: เศษ x1.5 ความเร็ว x0.7 (ตาราง boss_scale)
	var i := 0
	for d in r.get("debris", []):
		var n := int(roundf(int(d.n) * mul * (1.5 if big else 1.0)))
		for k in n:
			i += 1
			var a := deg_to_rad(lerpf(float(d.deg[0]), float(d.deg[1]), fb_hash(i, F, 11)))
			var v := lerpf(float(d.v[0]), float(d.v[1]), fb_hash(i, F, 12)) * (0.7 if big else 1.0)
			var col := Color(d.col)
			if d.kind in ["gel_drop", "gel_bubble", "shell_chip", "stone_chip", "bone_chip"]:
				var sx := int(pos.x - mx0)
				var sy := int(pos.y - (G - mh))
				if solid(sx, sy):
					col = rgb(sx, sy)
			debris.append([d.kind, col, pos.x, pos.y, cos(a) * v, sin(a) * v, float(d.g), int(d.life), F])

func _draw_debris(n: Node2D) -> void:
	var f := t / SEC
	for e in debris:
		var q: float = f - e[8]
		if q < 0 or q > e[7]:
			continue
		var x: float = e[2] + e[4] * q
		var y: float = e[3] + e[5] * q + 0.5 * e[6] * q * q
		var col: Color = e[1]
		var life: float = e[7]
		var al: float = 1.0 - maxf(0.0, q - life * 0.6) / (life * 0.4)
		match e[0]:
			"feather":   # ขนนก: ร่วงช้า ส่ายซ้ายขวา
				x += sin(q * 0.5 + e[3]) * 2
				y = minf(y, G - 2)
				px(n, x, y, Color(col, al), 2, 1)
			"dust", "stone_dust", "bone_dust", "sawdust", "smoke_wisp", "ectoplasm_wisp":   # ฝุ่น/ไอ: ขยายแล้วจาง
				disc(n, x, minf(y, G - 2), 1 + q * 0.15, Color(col, 0.5 * al))
			"spark", "spark_pale", "arc_spark", "light_mote":   # ประกาย: สว่าง + หางสั้น
				px(n, x, y, Color(1, 1, 1, al))
				px(n, x - e[4], y - e[5], Color(col, 0.6 * al))
			"shell_chip", "stone_chip", "bone_chip", "metal_panel", "wood_splinter", "gear_small", "ricochet_stone":   # เศษแข็ง: กระดอนพื้น ขอบเข้ม
				if y > G - 2:
					y = G - 2
				px(n, x, y, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, al), 3, 3)
				px(n, x, y, Color(col, al), 2, 2)
			"gel_drop", "gel_bubble", "oil_drop":   # เจล: หยดกลม แตะพื้นแล้วแผ่
				if y > G - 2:
					px(n, x - 1, G - 1, Color(col, al), 3, 1)
				else:
					disc(n, x, y, 1.2, Color(col, al))
			_:   # หยดเลือด: 1 จุด แตะพื้นแล้วค้าง
				px(n, x, minf(y, G - 1), Color(col, al))

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
	var bar := ColorRect.new()
	bar.color = Color(16 / 255.0, 12 / 255.0, 8 / 255.0, 0.62)
	bar.position = Vector2(0, H - 10)
	bar.size = Vector2(W, 10)
	ui.add_child(bar)
	caption_lbl = label(7, Color("#f0e4c8"), 0, false)
	caption_lbl.position = Vector2(4, H - 11)
	caption_lbl.text = "GODOT · %s %s · %s%s" % [mon_name, foe, caption(), (" · อาวุธ: " + weapon_name()) if weapon_id != "" else ""]
	_build_menu()

## บับเบิลชื่อท่า (rs3Bubble): เด้ง 2 เฟรมแรก · ไม่ล้นจอ · หางชี้ผู้พูด
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

## คำเสียง (pkText 12px) ต่อเฟรม · x, y = จุดเริ่ม/เส้นฐานแบบหน้าเว็บ
func word(text: String, x: float, y: float, col := Color.WHITE, size := 12, outline := 3) -> void:
	if n_word >= words.size():
		words.append(label(12, Color.WHITE, 3, true))
	var l: Label = words[n_word]
	n_word += 1
	l.visible = true
	l.text = text
	l.label_settings.font_size = size
	l.label_settings.font_color = col
	l.label_settings.outline_size = outline
	l.position = Vector2(round(x), round(y) - size - 2)

## ตัวเลขดาเมจ (dmgPop): เด้ง แล้วลอยช้า ค้าง ~1.3 วิ แล้วจาง · d = เฟรมหลังโดน
func pop(val: int, x: float, y: float, d: int, col := Color.WHITE, tag := "", tag_col := Color("#ffe08a")) -> void:
	if d < 0 or d >= 22:
		return
	if n_pop >= pops.size():
		var a := label(14, Color.WHITE, 4, true)
		a.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		a.size = Vector2(160, 20)
		a.pivot_offset = Vector2(80, 12)
		var b := label(8, Color.WHITE, 3, true)
		b.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.size = Vector2(160, 12)
		pops.append([a, b])
	var l: Label = pops[n_pop][0]
	var tl: Label = pops[n_pop][1]
	n_pop += 1
	var dy: float = [-6, -10, -8][d] if d < 3 else -8 - minf(6.0, (d - 3) * 0.5)
	var yy: float = max(18.0, round(y + dy))
	var al := 1.0 if d < 16 else 1 - (d - 16) / 6.0
	l.visible = true
	l.text = str(val)
	l.label_settings.font_color = col
	l.scale = Vector2.ONE * (1.4 if d == 0 else 1.15 if d == 1 else 1.0)
	l.position = Vector2(round(x) - 80, yy - 19)
	l.modulate.a = al
	tl.visible = tag != ""
	tl.text = tag
	tl.label_settings.font_color = tag_col
	tl.position = Vector2(round(x) - 80, yy + 1)
	tl.modulate.a = al

func aff_tag() -> String:
	return "อ่อนแอ!" if aff > 0 else "ต้านทาน" if aff < 0 else ""

func aff_col() -> Color:
	return Color("#ffe08a") if aff > 0 else Color("#c8c8c8")

# ── เมนู (หน้าเว็บ): ท่า · มอน · ฉาก · เล่นซ้ำ · เสียง · เพลง ─────────────
func _build_menu() -> void:
	menu = Control.new()
	menu.size = Vector2(W, H)
	ui.add_child(menu)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.04, 0.09, 0.84)
	shade.size = Vector2(W, H - 10)
	menu.add_child(shade)
	var title := label(9, Color("#fff4c8"), 3, true, menu)
	title.text = "ห้องทดลองฉากต่อสู้ Godot · เลือกท่า มอน ฉาก"
	title.position = Vector2(6, 2)
	var step2 := floori(295.0 / (TECHS.size() - 6))
	for i in TECHS.size():   # แถวท่า: บน 6 ท่า · ล่าง ประกาย 3 + มอนตี 2 + ทุบ
		var tc: Array = TECHS[i]
		var row2 := i >= 6
		var b := _button("%s %s" % [tc[0], tc[1]], Vector2(4 + (i - 6) * step2 if row2 else 4 + i * 49, 31 if row2 else 16), Vector2(step2 - 2 if row2 else 48, 13), 13)
		b.modulate = Color(1, 1, 0.6) if tc[2] == scene_file_path else Color.WHITE
		b.pressed.connect(func(): _start(foe, bg_id, tc[2]))
	var names := {}
	for r in CsvDb.load_csv("res://data/monsters.csv"):
		names[str(r.monster_id)] = str(r.name_th)
	for i in FOES.size():   # แถวมอน: ชื่อบน รูปล่าง (กดแล้วเล่นทันที)
		var id: String = FOES[i]
		var b := _button("%s\n%s" % [id, names.get(id, "")], Vector2(4 + i * 59, 46), Vector2(57, 45), 20)
		b.modulate = Color(1, 1, 0.6) if id == foe else Color.WHITE
		b.pressed.connect(func(): _start(id, bg_id, scene_file_path))
		var ic := TextureRect.new()
		ic.texture = tx(id + "_0")
		ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		ic.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		ic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		ic.position = Vector2(4, 19)
		ic.size = Vector2(49, 25)
		b.add_child(ic)
	var keys := BGS.keys()
	for i in keys.size():   # แถวฉาก
		var id: String = keys[i]
		var b := _button("ฉาก: " + BGS[id][0], Vector2(4 + i * 98, 94), Vector2(95, 14), 14)
		b.modulate = Color(1, 1, 0.6) if id == bg_id else Color.WHITE
		b.pressed.connect(func(): _start(foe, id, scene_file_path))
	var again := _button("เล่นซ้ำ (%s)" % foe, Vector2(4, 111), Vector2(95, 16), 16)
	again.pressed.connect(func(): _start(foe, bg_id, scene_file_path))
	var snd := _button(_onoff("เสียง", "lab_mute"), Vector2(102, 111), Vector2(95, 16), 16)
	snd.pressed.connect(_toggle.bind(snd, "เสียง", "lab_mute"))
	var mus := _button(_onoff("เพลง", "lab_music_off"), Vector2(200, 111), Vector2(96, 16), 16)
	mus.pressed.connect(_toggle.bind(mus, "เพลง", "lab_music_off"))
	if not weapons.is_empty():   # อาวุธของสายท่านี้ 5 ระดับ: กดแล้วเล่นท่าเดิมใหม่ด้วยอาวุธนั้น
		var w_l := label(7, Color("#f0e4c8"), 2, false, menu)
		w_l.text = "อาวุธ"
		w_l.position = Vector2(6, 146)
		for i in weapons.size():
			var w: Array = weapons[i]
			var b := _button(WSHORT.get(w[0], w[1]), Vector2(40 + i * 51, 145), Vector2(48, 13), 13)
			b.modulate = Color(1, 1, 0.6) if w[0] == weapon_id else Color.WHITE
			b.pressed.connect(func():
				Engine.set_meta("lab_weapon_" + tech_id().substr(0, 2), w[0])
				_start(foe, bg_id, scene_file_path))
	var sp_l := label(7, Color("#f0e4c8"), 2, false, menu)   # ความเร็วเล่น: กดแล้วเล่นท่าเดิมใหม่ทันที (ช้า = ดูทีละจังหวะ)
	sp_l.text = "ความเร็ว"
	sp_l.position = Vector2(6, 131)
	var speeds := [0.25, 0.5, 1.0, 1.5, 2.0]
	for i in speeds.size():
		var v: float = speeds[i]
		var b := _button(("×%s" % v).replace(".0", ""), Vector2(40 + i * 51, 130), Vector2(48, 13), 13)
		b.modulate = Color(1, 1, 0.6) if is_equal_approx(v, speed) else Color.WHITE
		b.pressed.connect(func():
			Engine.set_meta("lab_speed", v)
			_start(foe, bg_id, scene_file_path))
	menu.visible = not playing

func _onoff(what: String, key: String) -> String:
	return what + (": ปิด" if bool(Engine.get_meta(key, false)) else ": เปิด")

func _toggle(b: Button, what: String, key: String) -> void:
	Engine.set_meta(key, not bool(Engine.get_meta(key, false)))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabSfx"), bool(Engine.get_meta("lab_mute", false)))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabMusic"), bool(Engine.get_meta("lab_music_off", false)))
	(b.get_meta("lbl") as Label).text = _onoff(what, key)

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
	l.size = Vector2(size.x, text_h)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.set_meta("lbl", l)
	return b

func _start(id: String, bg: String, scene: String) -> void:
	Engine.set_meta("lab_foe", id)
	Engine.set_meta("lab_bg", bg)
	Engine.set_meta("lab_auto", true)
	get_tree().change_scene_to_file(scene)

# ── เดินเวลา ─────────────────────────────────────────
func _process(delta: float) -> void:
	if not stopped:
		amb_t += delta
		if lamp:
			lamp.modulate.a = 0.48 * (0.75 + 0.25 * sin(amb_t * 9) * sin(amb_t * 5.3 + 1))
	amb.queue_redraw()
	if not playing:
		return
	if hold > 0.0:
		hold -= delta * speed
	else:
		t += delta * speed
	for s in stops():
		if not stops_done.has(s[0]) and t / SEC >= s[0]:
			stops_done[s[0]] = true
			t = s[0] * SEC
			hold = s[1]
	_step()
	var Fn := int(floor(t / SEC))
	if snaps.has(Fn) and not snaps[Fn]:
		snaps[Fn] = true
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/%s_%s_f%03d.png" % [snap_dir, scene_file_path.get_file().get_basename(), foe, Fn])
	if not snaps.is_empty() and snaps.values().all(func(v): return v):
		get_tree().quit()
	if t > end_frame() * SEC + 0.5:
		if recording:
			get_tree().quit()
		else:
			playing = false
			ui.move_child(menu, -1)   # เมนูอยู่บนสุด (ป้ายที่สร้างทีหลังไม่ทับ)
			front_fx.visible = false   # ซ่อนป้าย/เอฟเฟกต์ค้างของท่า (เช่น ป้ายได้ท่าใหม่) ไม่ให้โผล่จางใต้เมนู
			bubble.visible = false
			for l in words:
				l.visible = false
			for pp in pops:
				pp[0].visible = false
				pp[1].visible = false
			menu.visible = true

func _step() -> void:
	var f := t / SEC
	var F := int(floor(f))
	var fresh := F != last_fi
	last_fi = F
	n_ghost = 0
	n_word = 0
	n_pop = 0
	frame(f, F, fresh)
	for i in range(n_ghost, ghosts.size()):
		ghosts[i].visible = false
	for i in range(n_word, words.size()):
		words[i].visible = false
	for i in range(n_pop, pops.size()):
		pops[i][0].visible = false
		pops[i][1].visible = false
	_burst_step(f, F)
	back_fx.queue_redraw()
	mid_fx.queue_redraw()
	front_fx.queue_redraw()
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
	if AudioServer.get_bus_index("LabMusic") < 0:   # เพลง: เบากว่าเสียงสกิล (บนเว็บ 0.28 ของเสียงสกิล)
		AudioServer.add_bus()
		AudioServer.set_bus_name(AudioServer.bus_count - 1, "LabMusic")
		AudioServer.set_bus_volume_db(AudioServer.bus_count - 1, linear_to_db(0.28 * 0.85))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabSfx"), bool(Engine.get_meta("lab_mute", false)))
	AudioServer.set_bus_mute(AudioServer.get_bus_index("LabMusic"), bool(Engine.get_meta("lab_music_off", false)))
	_music()
	for k in 12:
		var p := AudioStreamPlayer.new()
		p.bus = "LabSfx"
		add_child(p)
		players.append(p)

## เพลงต่อสู้: ผู้เล่นอยู่ที่ราก (ไม่ถูกลบตอนเปลี่ยนท่า → เพลงเล่นต่อเนื่อง) · วนซ้ำ
func _music() -> void:
	var root := get_tree().root
	if root.has_node("LabMusic"):
		return
	var st: AudioStream = null
	if ResourceLoader.exists(MUSIC):
		st = load(MUSIC)
	else:
		var mp := AudioStreamMP3.new()
		mp.data = FileAccess.get_file_as_bytes(ProjectSettings.globalize_path(MUSIC))
		st = mp
	st.set("loop", true)
	var p := AudioStreamPlayer.new()
	p.name = "LabMusic"
	p.bus = "LabMusic"
	p.stream = st
	root.add_child.call_deferred(p)
	p.play.call_deferred()

## เพลงหลบลงแวบหนึ่งตอนกระแทก (bgmDuck: 0.28 → 0.1 ใน 0.02 วิ แล้วคืนใน 0.45 วิ)
func duck() -> void:
	var i := AudioServer.get_bus_index("LabMusic")
	var base := linear_to_db(0.28 * 0.85)
	var tw := get_tree().create_tween()
	tw.tween_method(func(v: float): AudioServer.set_bus_volume_db(i, v), base, base + linear_to_db(0.1 / 0.28), 0.02)
	tw.tween_method(func(v: float): AudioServer.set_bus_volume_db(i, v), base + linear_to_db(0.1 / 0.28), base, 0.43)

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
				"triangle":
					s = 4.0 * absf(ph - 0.5) - 1.0
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

func sfx_hit(big: bool, fam := "SL") -> void:
	var v := [T(0.95 if big else 0.6, "sine", 95 if big else 120, 28, 1.0, 0, 0.002, {"drive": true}), N(0.9 if big else 0.5, "lowpass", 5200, 160, 1.0, 0.8, 0, {"drive": true}),
		N(0.05, "highpass", 3500, 3500, 0.9, 1)]
	if fam == "SL" or fam == "PC":   # โลหะสะท้าน (กรองแคบ ไม่ใช่เสียงระฆัง)
		v.append(N(0.35, "bandpass", 4200, 2600, 0.5, 14, 0.01))
	if big:
		v.append(N(1.4, "lowpass", 600, 50, 0.6, 0.7, 0.05))
	play_sfx("hit%s%s" % [big, fam], v)

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
