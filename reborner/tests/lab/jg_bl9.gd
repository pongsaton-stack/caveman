extends "res://tests/lab/lab_stage.gd"
## จันทร์เสี้ยวกลางหาว bl9 ใน Godot — เทียบกับหน้าเว็บ jg_bl9 (tools/web/anim_test.tpl.html) · ส่วนกลางอยู่ใน lab_stage.gd
## จังหวะเฟรมเท่าเว็บ (0.06 วิ) ตำแหน่งต่อเนื่อง 60 fps · เพิ่ม: ซีกที่ขาดหมุนคว่ำแล้วสลายเป็นผงสีจริง · แผลเรืองตัดด้วยเนื้อมอน (clip_children) · รอยเสี้ยวเรืองแสง · หยุดภาพตอนแยก
## เปิด/อัด: ดูหัวไฟล์ lab_stage.gd (ใส่ res://tests/lab/jg_bl9.tscn)

const MX := 112
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

var moon_y := 0.0
var moon_x := 0.0
var apex_l := 0.0
var x0 := 0.0
var xland := 0.0
var p0 := Vector2.ZERO
var p1 := Vector2.ZERO
var p2 := Vector2.ZERO
var chord := Vector2.ZERO
var moon: Sprite2D
var moon_glow: Sprite2D
var piece_up: Polygon2D
var piece_dn: Polygon2D
var wound_mask: Sprite2D
var wound_dark: Line2D
var wound_lit: Line2D
var trail: Node2D
var trail_glow: Node2D
var trail_p := 0.0
var trail_lit := 1.0
var shadow: ColorRect
var ash_up: CPUParticles2D
var ash_dn: CPUParticles2D
var lbl_dots: Label

func tech_id() -> String: return "bl9"
func end_frame() -> int: return END
func stops() -> Array: return [[SPLIT, 0.1]]
func caption() -> String: return "จันทร์เสี้ยวกลางหาว → %s" % ("ขาด" if kill else "แผลเรือง (รอด)")

func cut(u: float) -> Vector2:
	return (1 - u) * (1 - u) * p0 + 2 * u * (1 - u) * p1 + u * u * p2

## ตำแหน่ง Rion · เหมือน jgGeo บนเว็บ แต่ f เป็นทศนิยม (เลื่อนต่อเนื่อง) ส่วนภาพเลือกจากเฟรมเต็ม
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

# ── สร้าง ────────────────────────────────────────────
func setup() -> void:
	place_monster(MX)
	var tr := edges(top0 + 3)
	var lb := edges(mh - 4).x
	moon_y = max(22.0, min(52.0, G - bh - 30.0))
	moon_x = mx0 + mw / 2.0 + 16
	apex_l = min(72.0, G - 44.0 - moon_y)
	x0 = mx0 + mw + 30
	xland = max(30.0, mx0 - 26.0)
	p0 = Vector2(mx0 + tr.y + 5, G - bh - 4)
	p2 = Vector2(mx0 + max(lb, mw * 0.12) + 2, G - 2)
	chord = (p2 - p0).normalized()
	var mid_e := edges(int(round(top0 + bh * 0.5)))
	var mid := Vector2(mx0 + (mid_e.x + mid_e.y) / 2.0, G - bh * 0.5)
	p1 = Vector2(2 * mid.x - (p0.x + p2.x) / 2.0 - (mid_e.y - mid_e.x) * 0.15, 2 * mid.y - (p0.y + p2.y) / 2.0)   # กลางเส้นผ่ากลางตัว · โป่งซ้าย 15%
	moon_glow = Sprite2D.new()
	moon_glow.texture = radial(Color("#fff4c8"), 96)
	moon_glow.material = add_mat()
	add_child(moon_glow)
	move_child(moon_glow, dim.get_index() + 1)
	moon = Sprite2D.new()
	moon.texture = _moon_tex(18)
	add_child(moon)
	move_child(moon, moon_glow.get_index() + 1)
	shadow = ColorRect.new()
	shadow.color = Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4)
	shadow.z_index = 4
	add_child(shadow)
	# ชิ้นมอนสองซีกตามแนวฟัน (เส้นโค้ง + ปลายต่อเป็นเส้นตรงตามทิศสัมผัส)
	var poly: Array[Vector2] = []
	for i in 25:
		poly.append(cut(i / 24.0))
	var a0 := poly[0] + (poly[0] - poly[1]).normalized() * 300
	var a1 := poly[24] + (poly[24] - poly[23]).normalized() * 300
	var line := PackedVector2Array([a0])
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
	trail_glow = Node2D.new()
	trail_glow.material = add_mat()
	trail_glow.z_index = 3
	trail_glow.draw.connect(_draw_trail.bind(true))
	add_child(trail_glow)
	trail = Node2D.new()
	trail.z_index = 3
	trail.draw.connect(_draw_trail.bind(false))
	add_child(trail)
	lbl_dots = label(9, Color("#e8ecff"), 0, true)
	lbl_dots.visible = false

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
	pg.material = fx_mat()
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
			if solid(x, y) and Geometry2D.is_point_in_polygon(w, world):
				pts.append(w - c)
				cols.append(mon_img.get_pixel(x, y))
	p.emission_points = pts
	p.emission_colors = cols
	p.direction = Vector2(0, -1)
	p.spread = 35
	p.gravity = Vector2(0, -22)
	p.initial_velocity_min = 4
	p.initial_velocity_max = 16
	p.color_ramp = ramp([Color.WHITE, Color(1, 1, 1, 0.7), Color(1, 1, 1, 0)])
	p.local_coords = false
	p.z_index = 2
	pg.add_child(p)
	return p

## รอยเสี้ยว: ริบบิ้นหนากลาง บางปลาย เผยตามปลายมีด · glow = ชั้นบวกแสงกว้างกว่า
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

# ── ทุกเฟรม ──────────────────────────────────────────
func frame(f: float, F: int, fresh: bool) -> void:
	var ds := F - SPLIT
	var q := f - SPLIT
	var g := geo(f)
	shake(F, 2.0 * (1 - (F - SHOUT) / 4.0) if F >= SHOUT and F < SHOUT + 4 else (4.0 * (1 - ds / 6.0) if ds >= 0 and ds < 6 else 0.0))
	world_stop(F >= TONBO and F < SPLIT)
	dim_to(0.0 if f < TONBO else (0.45 * (f - TONBO) / (SHOUT - TONBO) if f < SHOUT else (0.45 if ds < 6 else maxf(0.0, 0.45 * (1 - (q - 6) / 16.0)))), Color("#0c1028"))
	# พระจันทร์: ขึ้นช่วงตั้งท่า · วาบพร้อมรอยเสี้ยวก่อนแยก · จางหลังแยก
	var mp := 0.0 if f < TONBO else minf(1.0, (f - TONBO) / (SHOUT - TONBO))
	var me := 1 - (1 - mp) * (1 - mp)
	var flash := F == SPLIT - 5 or F == SPLIT - 4
	var mal := me * (1.0 if ds < 8 else maxf(0.0, 1 - (q - 8) / 14.0)) * (1.0 if flash else 0.92)
	moon.position = Vector2(round(moon_x), round(moon_y + (1 - me) * 26))
	moon.modulate.a = mal
	moon.scale = Vector2.ONE * (19.0 / 18.0 if flash else 1.0)
	moon_glow.position = moon.position
	moon_glow.modulate.a = mal * (0.55 if flash else 0.32)
	moon_glow.scale = Vector2.ONE * (1.5 if flash else 1.0)
	# Rion: วิ่งกลับทางฝั่งไกล = หลังมอน (มอนรอด) · ยอด = เงาดำตัดพระจันทร์ ขอบแสงจันทร์ · ร่างติดตาตอนขึ้น/ฟันลง
	var behind: bool = g.back and not kill
	rion.z_index = 0 if behind else 4
	if g.sil:
		var gr := g.duplicate()
		gr.cx -= 1
		gr.lift += 1
		ghost(gr, 0.95, Color("#fff4c8"), 1.0)   # ขอบแสงจันทร์
		set_rion(rion, g, 1.0, Color("#141a33"), 1.0)
	else:
		set_rion(rion, g)
	if ((F > LEAP and F < APEX) or (F >= CUT and F < LAND)) and not behind:
		for k in 2:
			ghost(geo(f - (k + 1)), 0.14 * (2 - k), Color("#fff4c8"), 1.0)
	var sw: float = 18.0 * 1.6 * maxf(0.35, 1 - g.lift / 90.0)
	shadow.visible = g.lift > 2 and not behind
	shadow.position = Vector2(g.cx - sw / 2, G - 1)
	shadow.size = Vector2(sw, 1)
	# มอน: หายใจปกติจนแยก · ขาด = สองซีกแยก (ซีกบนไถลหมุนคว่ำ) แล้วสลาย · รอด = เปิดแว้บแล้วประกบ + แผลเรือง
	piece_up.visible = false
	piece_dn.visible = false
	wound_mask.visible = false
	if ds < 0:
		show_mon("%s_%d" % [foe, posmod(int(floor(f / (6.0 if F >= LAND else 4.0))), 3)])
	elif kill:
		mon.visible = false
		var s := 1.2 * q + 0.16 * q * q
		for pg in [piece_up, piece_dn]:
			pg.visible = true
			pg.texture = tx(foe + "_0")
			pg.material.set_shader_parameter("tint", Color.WHITE)
			pg.material.set_shader_parameter("amount", 1.0 if ds < 2 else 0.0)
			pg.material.set_shader_parameter("dissolve", clamp((q - 8) / 8.0, 0.0, 1.0))
		piece_dn.position = piece_dn.get_meta("c") + Vector2(0.35 * q, 0)
		piece_dn.rotation = 0.004 * q * q
		piece_up.position = piece_up.get_meta("c") + chord * s + Vector2(0, 0.08 * q * q)
		piece_up.rotation = -min(1.4, 0.006 * q * q)
		if fresh and ds == 8:
			ash_up.restart()
			ash_dn.restart()
	else:
		var open: int = [0, 2, 3, 2, 1][ds] if ds < 5 else 0
		var mk := (foe + "_6") if ds < 10 else "%s_%d" % [foe, posmod(int(floor(f / 4.0)), 3)]
		var mt := tx(mk)
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
			show_mon(mk, kb, white)
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
	# อนุภาค: ไอหายใจ · ฝุ่นถีบ/ลง/ถึงบ้าน · จุดโดน
	if fresh:
		if F >= TONBO + 4 and F < RUN and (F - TONBO - 4) % 10 == 0:
			puff(Vector2(g.cx - 18, G - 58))
		if F == LEAP:
			dust_at(x0, 1.0, 1.2)
		if F == LAND:
			dust_at(xland, -1.0, 1.2)
		if F == HOME - 2:
			dust_at(home, 1.0, 0.6)
		if ds == 0:
			burst(cut(0.5), F)
	# ตัวหนังสือ
	var tag := ("อ่อนแอ! · " if aff > 0 else "ต้านทาน · " if aff < 0 else "") + ("HP %d · ฟันเดียวขาด" % hp if kill else "HP %d รอด" % hp)
	var dx := roundf(clampf(mcx, 30.0, W - 30.0))
	if ds >= 0 and ds < 14:   # มอนตัวเล็ก: บรรทัด HP ยาวเกินตัว → เลื่อนคำเสียงไปขวาพ้นบรรทัด
		word("ขาด!!" if kill else "ฉับ!!", minf(W - 44, maxf(mx0 + mw + 4, roundf(dx + text_w(tag, 8) / 2) + 4)), max(18, G - bh - 4 - min(5, ds)), Color("#fff4c8"))
	lbl_dots.visible = F >= LAND + 3 and ds < 0   # เงียบ
	if lbl_dots.visible:
		var k := F - LAND - 3
		lbl_dots.modulate.a = minf(1.0, k / 2.0)
		lbl_dots.text = ".".repeat(1 + mini(2, k >> 2))
		lbl_dots.position = Vector2(mcx - 4, G - bh - 6 - 12)
	show_bubble("จันทร์เสี้ยวกลางหาว!", g.cx, max(14.0, G - g.lift - 74), F - SHOUT, (1.0 if F < RUN else (RUN + 3 - f) / 3.0) if F >= SHOUT and F < RUN + 3 else 0.0)
	pop(dmg, dx, max(30, G - bh - 14), ds, Color("#fff4c8"), tag, Color("#ffe08a") if aff > 0 else Color("#c8e6ff"))

# ── เสียง (เหมือน jgSound บนหน้าเว็บ) ───────────────────────
func sounds(F: int) -> void:
	if F == TONBO:
		sfx_charge()   # เก็บแรง
	if F >= TONBO + 4 and F < SHOUT and (F - TONBO - 4) % 10 == 0:
		play_sfx("breath", [N(0.35, "bandpass", 500, 300, 0.08, 1)])   # ลมหายใจ
	if F == SHOUT:
		play_sfx("shout", [N(0.3, "bandpass", 1800, 900, 0.35, 2), T(0.25, "sawtooth", 220, 160, 0.06, 0, 0.002, {"lp": 1500})])   # ตะโกน (ไม่ใช้เสียงพูด)
		duck()
	if (F >= RUN and F < LEAP and (F - RUN) % 2 == 0) or (F >= BACK and F < HOME - 2 and (F - BACK) % 3 == 0):
		var pk := 0.3 if F < LEAP else 0.18
		play_sfx("step%s" % pk, [N(0.05, "lowpass", 900, 200, pk, 1)])   # ฝีเท้า (วิ่งไป / วิ่งกลับเบากว่า)
	if F == LEAP:
		play_sfx("leap", [N(0.1, "lowpass", 600, 120, 0.6, 1), N(0.4, "bandpass", 500, 1600, 0.2, 2, 0.04)])   # ถีบตัวขึ้น
	if F == APEX:
		play_sfx("apex", [N(0.6, "lowpass", 400, 200, 0.12, 1)])   # ยอด: ลมว่างเปล่า
	if F == CUT:
		sfx_release()   # ฟันลง (ยังไม่มีเสียงโดน)
	if F == LAND:
		play_sfx("slide", [N(0.25, "lowpass", 1200, 300, 0.25, 2)])   # ไถลเท้า แล้วเงียบ
	if F == SPLIT:   # เสียงโดนมาทีหลังความเงียบ
		sfx_hit(false)
		play_sfx("split", [N(0.06, "highpass", 3000, 7000, 0.6, 3), T(0.15, "sine", 150, 45, 0.45)])
		sfx_mon(false, 0.6 if foe == "B1" else 1.0)
		duck()
	if kill and F == SPLIT + 10:
		play_sfx("fall", [N(0.3, "lowpass", 500, 80, 0.5, 1)])   # ครึ่งบนหล่นกระแทก
