extends "res://tests/lab/blc_bl0.gd"
## ฐานท่าเดี่ยวกิ่งลื่นไหล (bl5 ปาดไว · bl6 เงาสองคม · bl13 ก้าวเงา) — kwan 28 ต.ค. เลือก "2" แบบผสม: key pose ที่ตาจำได้เป็น State ของ PixelLab
## ช่วงยืน (< IDLE) และกระโดดถอยหลังจบท่า (≥ hold1) ใช้เครื่องฟัน blc_bl0 · ช่วงกลางท่าเขียนใน _move(f)
## ท่าลูกเขียน: mv() · setup() (ตั้ง hold1 · hit_f · x_end) · _move(f) · fx(n, f) · snd(F) · rion_ghosts(f, F)

var hold1 := 60
var hit_f: Array[float] = []      # เฟรมที่โดน (ทศนิยมได้)
var x_end := 0.0                 # กลางตัว Rion ตอนจบท่า (จุดเริ่มกระโดดถอย)
var x_home := 0.0
var bubble_name := ""
var bubble_at := Vector2(18, 30)  # [เริ่ม, จบ] ของบับเบิลชื่อท่า

func end_frame() -> int: return hold1 + END - HOP0
func stops() -> Array: return [[int(ceil(hit_f[0])), 0.08]] if not hit_f.is_empty() else []

var vis := Rect2()   # ขอบตัวมอนจริง (พิกเซลที่มีสี) บนจอ · กรอบภาพมอนกว้างกว่าตัวจริง

func setup() -> void:
	super.setup()
	x_home = start + 60
	vis = mon_rect()

## ระดับมีด (ใกล้พื้น G − h) แต่ไม่เลยตัวมอน
func blade_y(h: float) -> float:
	return clampf(G - h, vis.position.y + 6, G - 8)

## เริ่มกระโดดถอยจาก x_end (เรียกท้าย setup ของท่าลูก)
func set_end(x: float) -> void:
	x_end = x
	near = x - 60

func _move(_f: float) -> Dictionary:
	return {}

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < IDLE:
		return super.geo(f)
	if F >= hold1:
		return super.geo(f - hold1 + HOP0)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false, "rot": 0.0}
	b.merge(_move(f), true)
	return b

## วิ่งเข้าแบบเครื่องฟัน: x จาก x_home ไป x1 ในช่วง [a, b)
func run_x(f: float, a: float, b: float, x1: float) -> float:
	var u := clampf((f - a) / (b - a), 0.0, 1.0)
	return x_home + (x1 - x_home) * (u * u * 0.5 + u * 0.5)

## มอนกระเด็นจากโดนครั้งล่าสุด
func mon_kb(f: float) -> float:
	var x := 0.0
	for h in hit_f:
		var d := f - h
		if d >= 0 and d < 16:
			x = -BM.kb * ((1 - pow(1 - d / 4.0, 2)) if d < 4 else maxf(0.0, 1 - (d - 4) / 12.0))
	return x

func freeze(_f: float) -> bool: return false   # โลกหยุด (หิมะ/ถ่านค้าง) ช่วงไหน
func rion_ghosts(_f: float, _F: int) -> void: pass
func fx(_n: Node2D, _f: float) -> void: pass
func snd(_F: int) -> void: pass

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(freeze(f))
	var dl := -1
	for h in hit_f:
		if F >= int(ceil(h)):
			dl = F - int(ceil(h))
	shake(F, BM.shk * (1 - dl / 5.0) if dl >= 0 and dl < 5 else 0.0)
	var hurt := false
	var flash := 0.0
	for h in hit_f:
		var d := F - int(ceil(h))
		if d >= 0 and d < 10:
			hurt = true
		if d == 0:
			flash = 0.25 if foe.begins_with("B") else 0.45
	show_mon(hurt_key() if hurt else idle_key(f), mon_kb(f), flash)
	var g := geo(f)
	set_rion(rion, g)
	rion_ghosts(f, F)
	if fresh:
		if F >= IDLE and F < hold1 and g.key.begins_with("pls_run") and (F - IDLE) % STEP == 0:
			dust_at(g.cx + 6, 1.0, 0.5 + 0.4 * (F - IDLE) / RUN)
		for i in hit_f.size():
			if F == int(ceil(hit_f[i])):
				debris_at(Vector2(vis.end.x - 6 + mon_kb(f), vis.get_center().y), "คม", F, 0.8)
		var bf := F - hold1 + HOP0
		if F >= hold1:   # ฝุ่นกระโดดถอยของเครื่องฟัน
			var t0 := HOP0
			for h in HOPS:
				if h.has("skid"):
					for k in range(0, h.skid - 2, 2):
						if bf == t0 + k:
							dust_at(g.cx + 6, 1.0, 0.9 - k * 0.08)
					t0 += h.skid
					continue
				if bf == t0 + 1:
					dust_at(g.cx - 6, -1.0, 0.4 + h.d)
				t0 += h.c + h.a
				if bf == t0:
					dust_at(g.cx + 6, 1.0, 0.4 + h.d * 1.4)
				t0 += h.l
	var b0 := int(bubble_at.x)
	var b1 := int(bubble_at.y)
	show_bubble(bubble_name + "!", g.cx, maxf(14.0, G - g.lift - 74), F - b0, (1.0 if F < b1 - 3 else (b1 - f) / 3.0) if F >= b0 and F < b1 else 0.0)
	if not hit_f.is_empty():
		var d0 := F - int(ceil(hit_f[0]))
		if d0 >= 0 and d0 < 14:
			word(BM.sfx, maxf(4, vis.get_center().x + mon_kb(f) - 64), maxf(14, vis.position.y - 30 - mini(5, d0)), Color.WHITE)   # ซ้ายของตัวเลข
	for i in hit_f.size():   # ตัวเลขทีละครั้ง เหลื่อมขึ้น
		pop(dmg, maxf(16, vis.get_center().x + mon_kb(f) - 4 + i * 32), maxf(26.0, vis.position.y - 6) - i * 6, F - int(ceil(hit_f[i])), Color.WHITE, aff_tag(), aff_col())

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var st := geo(f)
	fx(n, f)
	if st.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - st.lift / 40.0):
				px(n, st.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)

func sounds(F: int) -> void:
	if F < IDLE or F >= hold1:   # ยืน · กระโดดถอย = เครื่องฟันเดิม
		var bf := F if F < IDLE else F - hold1 + HOP0
		if bf < IDLE or bf >= HOP0:
			super.sounds(bf)
		return
	snd(F)
	for i in hit_f.size():
		if F == int(ceil(hit_f[i])):
			sfx_mon(i == hit_f.size() - 1, 0.6 if foe == "B1" else 1.0)

## เสียงฝีเท้าวิ่ง (ท่าลูกเรียกในช่วงวิ่ง)
func step_snd(F: int, a: int, b: int) -> void:
	if F >= a and F < b and (F - a) % STEP == 0:
		var pk := snappedf(0.35 + 0.25 * (F - a) / maxf(1.0, b - a), 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
