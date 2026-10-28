extends "res://tests/lab/row_base.gd"
## วงล้อ bl4 ★ รอบ 2 (kwan 27 ต.ค. "ไม่สวย หมุนตัวครบรอบ แขนกางมีดออก ใบมีดกวาดทุกตัว ใช้งาน pixellab ได้เลย เอาให้สุด")
## ภาพ Rion = PixelLab State BL4_spin_T (กางแขนเป็นตัว T มีดมือขวาชี้ออก) + rot8 = ภาพหมุน 8 มุมของท่าเดียวกันจริง (pls_wheel_0–7)
## วิ่งเข้า ง้างระหว่างวิ่ง → ถึงหน้าแถวหมุนทันที: รอบ 1 เร่ง (รอยมีดวนรอบตัว) → รอบ 2 เร็วสุด มีดผ่านฝั่งแถว = ปล่อยคมลมวงโค้ง
## ขยายออกกวาดทุกตัวทีละตัว (ใกล้ → ไกล) → หมุนเลยครึ่งรอบแล้วเบรกค้างท่ากางแขนหันหน้า → หันกลับ → กระโดดถอยแบบท่าฟัน
## มุมภาพ pls_wheel_k: 0 ซ้าย · 1 ซ้ายเฉียงหน้า · 2 หน้า · 3 ขวาเฉียงหน้า · 4 ขวา · 5 ขวาเฉียงหลัง · 6 หลัง · 7 ซ้ายเฉียงหลัง
## มีด (มือขวา) อยู่ที่มุม θ = 3π/2 − k·π/4 บนวงรีรอบตัว (π = ฝั่งแถว/ซ้าย · π/2 = หน้า ใกล้กล้อง)
## รอบ 3 (kwan 28 ต.ค. "วงล้อกับกวาด ลงไปกลางดงมอนเลย"): วิ่ง → กระโดดข้ามตัวหน้าลงกลางแถว (ท่ากลาง PixelLab bl14_leap) → ตัวหน้า 2 ตัวผงะเปิดทาง
## → หมุนกลางดง คมลมแผ่ออกทั้งสองข้าง (ซ้าย/ขวา) โดนตามระยะจากตัว Rion · มอนกระเด็นออกจากตัว · บอสตัวเดียว = ลงหน้าบอสแบบเดิม
## รอบ 4 (kwan 28 ต.ค. "ท่ากงล้อ ทำท่า windmill ของ b boy ฟันหมุนแทน"): ลอยแล้วทิ้งตัวลงยันบ่า (ท่ากลาง pls_wm_dive) → windmill กลับหัว ขากาง V
## มีดมือขวาเหยียดเลียดพื้น (State BL4_windmill + rot8 = pls_windmill_0–7 แทน pls_wheel) → คมเลียดพื้น + ลมขาเตะวงบน → สะบัดขาดีดตัวลุก (pls_wm_kip) → กระโดดถอย

const RUN0 := 18     # เริ่มวิ่ง
const LEAP0 := 26    # กระโดดข้ามตัวหน้า
const SPIN0 := 34    # ลงกลางแถว เริ่มหมุน
const REV1 := 44     # จบรอบ 1
const REV2 := 50     # จบรอบ 2
const STOP := 56     # หมุนจบ (หันซ้าย) → ดีดตัวลุก
const TURN := 60     # ลุกถึงพื้น ตั้งการ์ด
const HOLD1 := 66    # เข้ากระโดดถอยของเครื่องฟัน
const ROOM_PX := 8.0 # ตัวหน้า 2 ตัวผงะเปิดทางตอน Rion ลง
const CHEST := 12    # ระดับมีดเหนือพื้น (windmill: มีดเลียดพื้น)
const LEGS := 58     # ระดับวงขาเตะ
const WAVE_V := 24.0 # ความเร็วคมลม (px/เฟรม)

var x_home := 0.0
var x_spin := 0.0
var x_jump := 0.0            # จุดถีบตัวกระโดด
var mid := false             # ลงกลางแถว (มอน 3 ตัว)
var release := 0.0           # เฟรมที่ปล่อยคมลม (มีดผ่านฝั่งแถวในรอบ 2)
var hits_f: Array[float] = []

func mv() -> Dictionary:
	return {"id": "bl4", "slide": 0, "reach": 0, "kb": 10, "shk": 3.0, "sfx": "ฉัวะ!!!", "what": "วงล้อ (bl4)"}

func end_frame() -> int: return HOLD1 + END - HOP0
func stops() -> Array: return [[int(ceil(hits_f[0])), 0.08]] if not hits_f.is_empty() else []
func caption() -> String: return "★ วิ่ง → กระโดดลงกลางดงมอน → windmill หมุนกลับหัว มีดเลียดพื้น 2 รอบ → คมลมแผ่สองข้าง → ดีดตัวลุก → กระโดดถอย"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 6)
	x_home = start + 60
	mid = cxs.size() == 3
	x_spin = cxs[1] if mid else cxs[0] + mw * 0.5 + 14
	x_jump = cxs[0] + mw * 0.5 + 30 if mid else x_spin + 22
	near = x_spin + 4 - 60   # จุดเริ่มกระโดดถอย = หลังเบรก
	# มีดผ่านฝั่งแถว (k = 2 → θ = π) ในรอบ 2 = v 10
	release = _f_of_v(10.0)
	hits_f.clear()
	for c in cxs:
		hits_f.append(release + maxf(0.0, (absf(x_spin - c) - 16) / WAVE_V))

## ทิศกระเด็นของมอนตัวที่ i (ออกจากตัว Rion) · ตัวกลาง (แถวหลัง) ถอยไปซ้ายเบาๆ
func _dir(i: int) -> float:
	if not mid or i == 1:
		return -1.0 if not mid else -0.4
	return signf(cxs[i] - x_spin)

## ตัวหน้าผงะเปิดทางตอน Rion ลงกลางแถว
func _room(i: int, f: float) -> float:
	if not mid or i == 1 or f < SPIN0 - 2:
		return 0.0
	var u := minf(1.0, (f - SPIN0 + 2) / 4.0)
	return _dir(i) * ROOM_PX * (1 - pow(1 - u, 2))

# ── มุมหมุน (หน่วย = มุมภาพ · 8 ต่อรอบ) ─────────────
func _v(f: float) -> float:
	if f < SPIN0:
		return 0.0
	if f < REV1:   # รอบ 1 เร่ง
		return 8.0 * pow((f - SPIN0) / (REV1 - SPIN0), 1.5)
	if f < REV2:   # รอบ 2 เร็วสุด
		return 8.0 + 6.0 * (f - REV1) / (REV2 - REV1)
	if f < STOP:   # ผ่อนจนจบที่มุมซ้าย (v 16) ก่อนดีดตัวลุก
		var u := (f - REV2) / (STOP - REV2)
		return 14.0 + 2.0 * (1 - pow(1 - u, 2.0))
	return 16.0

func _f_of_v(v: float) -> float:
	var lo := float(SPIN0)
	var hi := float(STOP)
	for i in 30:
		var m := (lo + hi) * 0.5
		if _v(m) < v:
			lo = m
		else:
			hi = m
	return lo

func _key_v(v: float) -> String:
	return "pls_windmill_%d" % posmod(int(floor(v + 0.5)), 8)

## มุมมีดบนวงรีรอบตัว
func _theta(v: float) -> float:
	return 1.5 * PI - v * PI / 4.0

## ความเร็วหมุน 0–1 (1 = รอบ 2)
func _spd(f: float) -> float:
	return clampf((_v(f) - _v(f - 1)) / 1.33, 0.0, 1.0)

# ── ตำแหน่ง Rion ─────────────────────────────────
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < RUN0:
		return super.geo(f)
	if F >= HOLD1:
		return super.geo(f - HOLD1 + HOP0)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false}
	if F < LEAP0:   # วิ่งเร่งถึงจุดถีบ
		var u := (f - RUN0) / (LEAP0 - RUN0)
		b.cx = x_home + (x_jump - x_home) * (u * u * 0.5 + u * 0.5)
		b.lean = -0.07 * minf(1.0, u * 2)
		b.key = "pls_run_bl_%d" % ((F - RUN0) % 6)
		return b
	if F < SPIN0:   # กระโดดโค้งข้ามตัวหน้า → ทิ้งตัวลงยันบ่ากลางแถว
		var u := (f - LEAP0) / (SPIN0 - LEAP0)
		b.cx = x_jump + (x_spin - x_jump) * u
		b.lift = (40.0 if mid else 18.0) * sin(PI * u)
		b.key = "pls_hop_bl_1" if u < 0.12 else ("pls_lair_0" if u < 0.5 else "pls_wm_dive_%d" % mini(3, int((u - 0.5) * 8.0)))   # ย่อถีบ → ลอย → ทิ้งตัว
		return b
	if F < STOP:   # windmill
		b.key = _key_v(_v(f))
		b.cx = x_spin
		if F < SPIN0 + 2:   # บ่ากระแทกพื้น
			b.sy = 0.93
			b.sx = 1.05
		return b
	b.cx = x_spin + 3
	if F < TURN:   # สะบัดขาดีดตัวลุก
		b.key = "pls_wm_kip_%d" % mini(1, int((f - STOP) / 2.0))
		b.sy = 0.95 if F < STOP + 1 else 1.0
	else:   # ตั้งการ์ดค้าง zanshin
		b.key = "pls_atk_bl_0"
	return b

## มอนกระเด็นตามคมลม (ไปทางซ้าย) แล้วค่อยกลับ
func _sweep_kb(d: float) -> float:
	if d < 0:
		return 0.0
	if d < 5:
		return -BM.kb * (1 - pow(1 - d / 5.0, 2))
	return -BM.kb * maxf(0.0, 1 - (d - 5) / 14.0)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var dm := 0.0
	if f >= RUN0 and f < STOP + 4:
		dm = 0.42 * minf(1.0, (f - RUN0) / 8.0)
	elif f >= STOP + 4:
		dm = maxf(0.0, 0.42 * (1 - (f - STOP - 4) / 10.0))
	dim_to(dm, Color("#0a0e26"))
	var dw := f - release
	if dw >= 0 and dw < 10:
		shake(F, BM.shk * (1 - dw / 10.0))
	elif f >= SPIN0 and f < REV2:
		shake(F, 0.6)
	else:
		cam.offset = Vector2.ZERO
	var g := geo(f)
	for i in mons.size():
		var d := f - hits_f[i]
		var dF := F - int(ceil(hits_f[i]))
		var key := hurt_key() if (d >= 0 and d < 14) or (_room(i, f) != 0.0 and f < SPIN0 + 4) else idle_key(f + i * 3)
		var amt := (0.25 if foe.begins_with("B") else 0.5) if dF == 0 else 0.0
		_show(i, key, _room(i, f) - _sweep_kb(d) * _dir(i), amt, 0.0, 0.95 if d >= 0 and d < 2 else 1.0)
	set_rion(rion, g)
	if f >= SPIN0 + 3 and f < STOP:   # ร่างติดตาตอนหมุน: มุมก่อนหน้า (ฟ้าจาง)
		var v := _v(f)
		for k in [2, 1]:
			var gg := g.duplicate()
			gg.key = _key_v(v - k * 0.9)
			ghost(gg, 0.13 * (3 - k) * _spd(f), Color("#9ae6ff"), 0.4)
	if F >= LEAP0 and F < SPIN0:   # ร่างติดตาตอนกระโดด
		ghost(geo(f - 1.5), 0.18)
		ghost(geo(f - 3), 0.1)
	if fresh:
		if F >= RUN0 and F < LEAP0 and (F - RUN0) % 3 == 0:
			dust_at(g.cx + 6, 1.0, 0.5 + 0.5 * (F - RUN0) / (SPIN0 - RUN0))
		if F == LEAP0:
			dust_at(g.cx + 6, 1.0, 1.1)
		if F == SPIN0:   # ลงกลางแถว
			dust_at(g.cx, 1.0, 1.5)
			dust_at(g.cx, -1.0, 1.5)
		if F > SPIN0 and F < STOP and F % 2 == 0:   # ฝุ่นวนรอบเท้า
			dust_at(g.cx + (10 if F % 4 == 0 else -10), 1.0 if F % 4 == 0 else -1.0, 0.9)
		for i in mons.size():
			if F == int(ceil(hits_f[i])):
				debris_at(Vector2(cxs[i] - 2, gy(i) - CHEST + 8), "คม", F, 1.0 - i * 0.15)
				if i == 0:
					burst(Vector2(cxs[0] + mw * 0.3, G - CHEST + 6), F, Color("#9ae6ff"))
		var bf := F - HOLD1 + HOP0
		if F >= HOLD1:   # ฝุ่นกระโดดถอยของเครื่องฟัน
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
	var b0 := RUN0 - 2
	show_bubble("วงล้อ!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < SPIN0 + 2 else (SPIN0 + 6 - f) / 4.0) if F >= b0 and F < SPIN0 + 6 else 0.0)
	var dws := F - int(ceil(hits_f[0]))
	if dws >= 0 and dws < 18:   # เหนือหัว Rion ตอนโดนตัวแรก (ไม่ทับตัวเลขของแถว)
		word(BM.sfx, clampf(x_spin - 26, 4, W - 72), 26 - mini(6, dws), Color("#e8f8ff"), 18 if dws < 2 else 16, 4)   # บนสุดของจอ เหนือแถวตัวเลข (ไม่ทับเลข)
	for i in mons.size():
		pop(dmg, maxf(16, cxs[i] + _room(i, f) - _sweep_kb(f - hits_f[i]) * _dir(i)), my + roundf(mh * 0.25) - (i % 2) * 18, F - int(ceil(hits_f[i])), Color.WHITE, aff_tag(), aff_col())

# ── วาด ───────────────────────────────────────────
## รอยมีดวนรอบตัว (วงรีระดับอก) · back = ครึ่งหลังตัว (วาดใต้ Rion)
## legs = วงลมขาเตะของ windmill (สูงระดับขา · ขาวจาง · อยู่ตรงข้ามมีด)
func _trail(n: Node2D, f: float, back: bool, legs := false) -> void:
	if f < SPIN0 or f >= STOP + 2:
		return
	var spd := _spd(f)
	var fade := (1.0 if f < STOP else maxf(0.0, 1 - (f - STOP) / 2.0)) * (0.55 if legs else 1.0)
	var g := geo(f)
	var c := Vector2(g.cx - 2, G - (LEGS if legs else CHEST))
	var R := Vector2((22 if legs else 32) + 4 * spd, 6 if legs else 8)
	var L := 1.0 + 3.2 * spd   # หางยาวตามความเร็ว · รอบ 2 เกือบเต็มวง
	var head := _theta(_v(f)) + (PI if legs else 0.0)
	var layers := [[Color(0.75, 0.8, 0.9), 1.0], [Color(0.97, 0.98, 1.0), -1.0]] if legs else [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]
	for layer in layers:
		for k in 72:
			var u := float(k) / 71   # 0 หาง · 1 หัว
			var a := head + L * (1 - u)
			var front := sin(a) > 0
			if front == back:
				continue
			var w: float = (1.2 + 2.6 * spd) * pow(u, 0.8) * (1.3 if front else 0.8) + layer[1]
			if w < 1:
				continue
			var p := c + Vector2(cos(a) * R.x, sin(a) * R.y)
			var col: Color = layer[0]
			col.a = fade * (0.25 + 0.75 * u) * (1.0 if front else 0.6)
			px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))

## คมลม: วงโค้งแนวนอนขยายจากตัว Rion ไปทางแถว (ฝั่งซ้าย ±70°) · back = ส่วนหลังแถว
func _wave(n: Node2D, f: float, back: bool) -> void:
	_wave1(n, f, back, 0.0, 1.0)
	_wave1(n, f, back, 2.5, 0.45)   # ระลอกที่สอง บางกว่า ตามหลัง

func _wave1(n: Node2D, f: float, back: bool, lag: float, amp: float) -> void:
	var q := f - release - lag
	if q < 0 or q > 12:
		return
	var g := geo(f)
	var c := Vector2(g.cx - 2, G - CHEST + 6)
	var R := 22.0 + WAVE_V * q
	var ry := R * 0.16
	var al := 1.0 if q < 7 else maxf(0.0, 1 - (q - 7) / 5.0)
	var th := maxf(1.5, 5.5 - q * 0.35) * (0.6 + 0.4 * amp)   # บางลงเมื่อไกล
	var span := 1.25
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.2]]:
		for k in (240 if mid else 120):   # กลางแถว: วงโค้งสองฝั่ง (ซ้าย π · ขวา 0)
			var side := 0.0 if k >= 120 else PI
			var u := float(k % 120) / 119
			var a := side - span + 2 * span * u
			var front := sin(a) < 0   # มุม sin < 0 = ล่าง (หน้า ใกล้กล้อง) ตามแกน y ลง · ทั้งสองฝั่ง
			if front == back:
				continue
			var mid := 1 - absf(u - 0.5) * 2   # หนาสุดตรงกลาง (ระดับแถว)
			var w: float = th * (0.25 + 0.75 * pow(mid, 0.6)) * (1.15 if front else 0.75) + layer[1]
			if w < 1:
				continue
			var p := c + Vector2(cos(a) * R, -sin(a) * ry)
			var col: Color = layer[0]
			col.a = al * amp * (1.0 if front else 0.55) * (0.3 + 0.7 * mid)
			px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))
	if not back and lag == 0.0:   # เศษลม/เถ้าที่ขอบนำ
		for i in (20 if mid else 10):
			var a := (PI if i < 10 else 0.0) + (fb_hash(i, 3, 2) - 0.5) * 1.6
			var r := R + fb_hash(i, floor(f), 6) * 6
			px(n, c.x + cos(a) * r, c.y + sin(a) * r * 0.16 - fb_hash(i, 5, 1) * 10, Color(0.88, 0.95, 1, al * 0.8), 2 if i % 3 == 0 else 1, 1)

func draw_back(n: Node2D) -> void:
	_wave(n, t / SEC, true)

func draw_mid(n: Node2D) -> void:
	_trail(n, t / SEC, true)
	_trail(n, t / SEC, true, true)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var g := geo(f)
	# แถบภาพยนตร์
	var lb := 0.0
	if f >= RUN0 and f < HOLD1:
		lb = 11 * minf(1.0, (f - RUN0) / 5.0)
	elif f >= HOLD1 and f < HOLD1 + 6:
		lb = 11 * (1 - (f - HOLD1) / 6.0)
	if lb > 0:
		px(n, -8, -8, Color("#05060e"), W + 16, 8 + lb)
		px(n, -8, H - lb, Color("#05060e"), W + 16, lb + 8)
	# ลมหมุนรอบตัว: เส้นลมโค้งบางๆ 3 ระดับ + เถ้าวน
	if f >= SPIN0 and f < STOP + 4:
		var spd := _spd(f)
		var fade := 1.0 if f < STOP else maxf(0.0, 1 - (f - STOP) / 4.0)
		var c := Vector2(g.cx - 2, G)
		for lv in 3:
			var hy: float = [6.0, 24.0, 52.0][lv]
			var rx: float = [26.0, 34.0, 30.0][lv]
			var a0 := _theta(_v(f)) * (1.0 + lv * 0.15) + lv
			for k in 20:
				var a := a0 + k * 0.09
				if sin(a) < 0:
					continue
				px(n, c.x + cos(a) * rx, c.y - hy + sin(a) * 4, Color(0.85, 0.93, 1, 0.35 * spd * fade * (1 - k / 20.0)), 1, 1)
		for k in 14:
			var a := _theta(_v(f)) * 0.8 + k * 0.45
			var r := 22.0 + fb_hash(k, 2, 7) * 18
			var y := G - 4 - fmod(f * 2.2 + k * 9, 56)
			if sin(a) > 0:
				px(n, c.x + cos(a) * r, y + sin(a) * 4, Color(0.86, 0.8, 0.72, 0.75 * fade), 2 if k % 4 == 0 else 1, 1)
	_trail(n, f, false)
	_trail(n, f, false, true)
	_wave(n, f, false)
	# แผลแนวนอนบนมอนแต่ละตัว ตอนคมลมผ่าน
	for i in mons.size():
		var d := f - hits_f[i]
		if d >= 0 and d < 12:
			var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 6.0)
			var half := mw * (0.2 if hard_body() else 0.26)
			var x0: float = cxs[i] + _room(i, f) - _sweep_kb(d) * _dir(i)
			var wy := gy(i) - CHEST + 7
			slash_line(n, x0 + half, wy - 2, x0 - half, wy + 2, 3 if i == 0 else 2, minf(1.0, (d + 1) / 2.0), al)
	var dw := f - release
	if dw >= 0 and dw < 2:   # จอวาบเบาตอนปล่อย
		px(n, -8, -8, Color(0.9, 0.97, 1, 0.15 * (1 - dw / 2.0)), W + 16, H + 16)
	if f >= REV2 and f < STOP + 6:   # รอยเบรกเท้า
		var q := f - REV2
		for i in 6:
			px(n, x_spin - 12 + i * 4 + minf(q, 6.0) * 0.6, G - 1 - fb_hash(i, 9, 1) * 2, Color(0.85, 0.8, 0.72, maxf(0.0, 0.8 - q * 0.05)), 2, 1)

func sounds(F: int) -> void:
	if F < RUN0 or F >= HOLD1:   # ยืน · กระโดดถอย = เครื่องฟันเดิม
		var bf := F if F < RUN0 else F - HOLD1 + HOP0
		if bf < RUN0 or bf >= HOP0:
			super.sounds(bf)
		return
	if F == RUN0:   # ไม้ตาย: เสียงต่ำบวมขึ้น
		play_sfx("wl_charge", [T(1.2, "sine", 50, 85, 0.5, 0, 0.3), N(1.0, "bandpass", 300, 1200, 0.28, 1.5, 0, {"attack": 0.6})])
	if F < SPIN0 and (F - RUN0) % 3 == 0:
		var pk := snappedf(0.4 + 0.3 * (F - RUN0) / (SPIN0 - RUN0), 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == SPIN0:   # ปักเท้า
		play_sfx("wl_plant", [N(0.12, "lowpass", 900, 150, 0.7, 1)])
	if F > SPIN0 and F < STOP and floor(_v(F) / 4.0) > floor(_v(F - 1) / 4.0):   # หวีดทุกครึ่งรอบ สูงขึ้นตามความเร็ว
		var p := snappedf(0.8 + 0.12 * _v(F), 0.1)
		play_sfx("wl_rev%s" % p, [N(0.24, "bandpass", 700 * p, 1900 * p, 0.5, 2.5, 0, {"attack": 0.05})])
	if F == int(floor(release)):   # ปล่อยคมลม
		play_sfx("wl_release", [N(0.5, "bandpass", 3200, 900, 0.75, 2.2), N(0.3, "highpass", 5000, 2500, 0.35, 4, 0.02), T(0.5, "sine", 90, 35, 0.6, 0, 0.003, {"drive": true})])
	for i in mons.size():
		if F == int(ceil(hits_f[i])):
			if i == 0:
				sfx_hit(true)
			else:
				play_sfx("wl_cut%d" % i, [N(0.08, "highpass", 3800 - i * 400, 1600, 0.6, 2), N(0.16, "bandpass", 3600 - i * 300, 2200, 0.3, 10, 0.01), T(0.25, "sine", 140, 50, 0.4, 0, 0.002)])
			sfx_mon(i == mons.size() - 1, (0.6 if foe == "B1" else 1.0) * (1.0 - i * 0.05))
	if F == REV2:
		play_sfx("brake", [N(0.36, "lowpass", 1600, 300, 0.45, 2)])
	if F == STOP:   # ค้างท่า
		play_sfx("wl_pose", [T(0.08, "triangle", 900, 700, 0.12)])
	if F == TURN:
		play_sfx("kick0.5", [N(0.06, "bandpass", 600, 1600, 0.3, 2)])
