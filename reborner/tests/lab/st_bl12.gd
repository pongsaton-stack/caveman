extends "res://tests/lab/row_base.gd"
## พายุเถ้าใบมีด bl12 (kwan 27 ต.ค. "ต่อด้วย พายุเถ้าใบมีด ขอแบบจัดเต็ม เจนที่ต้องมีได้เลย") — รายงาน R2: กระบี่กระบอง ดาบสองมือพายุ
## หมุนติดพื้นรอบหนึ่ง → กระโดดหมุนกลางอากาศรอบสอง เร็วและสูงกว่า · เถ้าพายุฟุ้งสูงสุดรอบสอง → ลงไถล พายุสลาย → ค้างท่า → กลับ
## ในฉาก: วิ่งเข้า (ง้างระหว่างวิ่ง) → ย่อต่ำหมุนเป็นลมหมุนพุ่งทะลุแถว ขวา → ซ้าย (โดนครั้งที่ 1 ตอนผ่านแต่ละตัว)
## → ปลายแถวดีดตัวขึ้น หมุนกลางอากาศโค้งกลับข้ามแถว ซ้าย → ขวา (โดนครั้งที่ 2) → ลงหน้าแถว ไถล พายุเถ้าค่อยๆ ร่วง → ค้างท่า → กระโดดถอยแบบท่าฟัน
## ภาพ Rion = PixelLab State BL12_low_sweep (ย่อกางแขน) + BL12_air_spin (ลอยงอเข่ากางแขน) · rot8 = ภาพหมุน 8 มุมจริง (pls_storm_low_0–7 · pls_storm_air_0–7)

const RUN0 := 18
const IN0 := 28      # เข้าแถว เริ่มหมุนติดพื้น
const OUT0 := 46     # ทะลุออกปลายแถว
const LAUNCH := 49   # ดีดตัว
const LAND := 68     # ลงหน้าแถว
const HOLD1 := 80    # เข้ากระโดดถอยของเครื่องฟัน
const LOW_SPD := 1.1   # มุมภาพต่อเฟรม (รอบพื้น)
const AIR_SPD := 1.6   # รอบอากาศเร็วกว่า

var x_home := 0.0
var x_in := 0.0
var x_out := 0.0
var x_land := 0.0
var apex := 0.0
var hit1: Array[float] = []
var hit2: Array[float] = []

func mv() -> Dictionary:
	return {"id": "bl12", "slide": 0, "reach": 0, "kb": 7, "shk": 2.5, "sfx": "ฟึ่บบบ!!", "what": "พายุเถ้าใบมีด (bl12)"}

func end_frame() -> int: return HOLD1 + END - HOP0
func stops() -> Array: return []   # พายุไม่หยุด
func caption() -> String: return "วิ่งเข้า → หมุนติดพื้นทะลุแถว → ดีดตัวหมุนกลางอากาศข้ามกลับ → พายุเถ้าสลาย → กระโดดถอย"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 40, 0.62, mw * 0.5 + 60)   # เว้นที่ซ้ายให้ปลายลมหมุน
	x_home = start + 60
	x_in = cxs[0] + mw * 0.5 + 10
	x_out = maxf(30.0, cxs[cxs.size() - 1] - mw * 0.5 - 4)
	x_land = cxs[0] + mw * 0.5 + 22
	near = x_land + 6 - 60
	apex = clampf(float(mh - top0) * 0.7 + 22, 46, 70)
	hit1.clear()
	hit2.clear()
	for c in cxs:   # โดนตอนกลางตัว Rion ผ่านกลางตัวมอน
		hit1.append(IN0 + (x_in - c) / (x_in - x_out) * (OUT0 - IN0))
		hit2.append(LAUNCH + 2 + _air_u_inv((c - x_out) / (x_land - x_out)) * (LAND - LAUNCH - 2))

## สัดส่วนเวลาในอากาศ → สัดส่วนระยะ (ออกตัวเร็ว ช่วงท้ายชะลอ)
func _air_u(u: float) -> float:
	return 1 - pow(1 - u, 1.6)

func _air_u_inv(x: float) -> float:
	return 1 - pow(1 - clampf(x, 0.0, 1.0), 1 / 1.6)

# ── ตำแหน่ง Rion ─────────────────────────────────
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < RUN0:
		return super.geo(f)
	if F >= HOLD1:
		return super.geo(f - HOLD1 + HOP0)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false}
	if F < IN0:   # วิ่งเร่ง · 4 เฟรมท้ายย่อเข้าท่ากวาด (ภาพข้างของ State = มีดง้างหลัง)
		var u := (f - RUN0) / (IN0 - RUN0)
		b.cx = x_home + (x_in - x_home) * (u * u * 0.5 + u * 0.5)
		b.lean = -0.07 * minf(1.0, u * 2)
		b.key = "pls_run_bl_%d" % ((F - RUN0) % 6) if F < IN0 - 4 else "pls_storm_coil_0"
		return b
	if F < OUT0:   # ลมหมุนติดพื้นทะลุแถว
		var u := (f - IN0) / (OUT0 - IN0)
		b.cx = x_in + (x_out - x_in) * u
		b.key = "pls_storm_low_%d" % posmod(int(floor((f - IN0) * LOW_SPD)), 8)
		b.lift = absf(sin(f * 1.7)) * 1.5
		return b
	if F < LAUNCH:   # เบรกปลายแถว ย่อดีดตัว (ยังหมุนช้าลง)
		var q := f - OUT0
		b.cx = x_out - 3 * minf(1.0, q / 2.0)
		b.key = "pls_storm_low_%d" % posmod(int(floor((OUT0 - IN0) * LOW_SPD + q * 0.6)), 8)
		b.sy = 0.9
		b.sx = 1.05
		return b
	if F < LAND:   # หมุนกลางอากาศ โค้งกลับข้ามแถว
		var u := (f - LAUNCH) / (LAND - LAUNCH)
		b.cx = (x_out - 3) + (x_land - (x_out - 3)) * _air_u(u)
		b.lift = 4 * apex * u * (1 - u)
		b.key = "pls_storm_air_%d" % posmod(int(floor((f - LAUNCH) * AIR_SPD)), 8)
		return b
	var q := f - LAND   # ลงพื้น ไถล ค้างท่าหันหน้ากางแขน (ภาพหน้าของท่าย่อ)
	b.cx = x_land + 6 * (1 - pow(1 - minf(1.0, q / 6.0), 2))
	b.key = "pls_storm_low_2" if q < HOLD1 - LAND - 3 else ("pls_storm_low_1" if q < HOLD1 - LAND - 1 else "pls_storm_low_0")
	if q < 2:
		b.sy = 0.88
		b.sx = 1.06
	return b

## มอนเซตามทิศลม: ครั้งแรกถูกปัดไปซ้าย (ทางวิ่ง) · ครั้งสองถูกปัดขวา
func _sway(i: int, f: float) -> float:
	var d1 := f - hit1[i]
	var d2 := f - hit2[i]
	var x := 0.0
	if d1 >= 0 and d1 < 14:
		x -= BM.kb * (minf(1.0, d1 / 3.0) if d1 < 3 else maxf(0.0, 1 - (d1 - 3) / 11.0))
	if d2 >= 0 and d2 < 14:
		x += BM.kb * 0.8 * (minf(1.0, d2 / 3.0) if d2 < 3 else maxf(0.0, 1 - (d2 - 3) / 11.0))
	return x

## ความแรงพายุ 0–1 (เริ่มตอนเข้าแถว · พีครอบอากาศ · สลายหลังลง)
func _storm(f: float) -> float:
	if f < IN0 - 2:
		return 0.0
	if f < LAUNCH:
		return 0.55 * minf(1.0, (f - IN0 + 2) / 4.0)
	if f < LAND:
		return 0.55 + 0.45 * minf(1.0, (f - LAUNCH) / 5.0)
	return maxf(0.0, 1 - (f - LAND) / 14.0)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var sm := _storm(f)
	dim_to(0.38 * minf(1.0, maxf(0.0, (f - RUN0) / 8.0)) * (1.0 if f < LAND else maxf(0.0, 1 - (f - LAND) / 12.0)), Color("#1a1210"))   # มืดอมน้ำตาลเถ้า
	if f >= IN0 and f < LAND + 6:
		shake(F, 0.5 + 1.3 * sm if f < LAND else BM.shk * (1 - (f - LAND) / 6.0))
	else:
		cam.offset = Vector2.ZERO
	var g := geo(f)
	for i in mons.size():
		var d1 := F - int(ceil(hit1[i]))
		var d2 := F - int(ceil(hit2[i]))
		var hurt := (f >= hit1[i] and f < hit1[i] + 12) or (f >= hit2[i] and f < hit2[i] + 12)
		var amt := (0.2 if foe.begins_with("B") else 0.4) if d1 == 0 or d2 == 0 else 0.0
		_show(i, hurt_key() if hurt else idle_key(f + i * 3), _sway(i, f), amt)
	set_rion(rion, g)
	if f >= IN0 and f < LAND:   # ร่างติดตาสีเถ้า 3 ร่าง
		for k in [3, 2, 1]:
			ghost(geo(f - k * 0.8), 0.1 * (4 - k), Color("#d8c8b0"), 0.35)
	if F >= IN0 - 4 and F < IN0:
		ghost(geo(f - 1.5), 0.15)
	if fresh:
		if F >= RUN0 and F < IN0 and (F - RUN0) % 3 == 0:
			dust_at(g.cx + 6, 1.0, 0.5 + 0.5 * (F - RUN0) / (IN0 - RUN0))
		if F >= IN0 and F < OUT0 and F % 2 == 0:   # ลมหมุนกวาดฝุ่นเป็นทาง
			dust_at(g.cx + 8, 1.0, 1.0)
			dust_at(g.cx - 8, -1.0, 0.8)
		if F == LAUNCH:
			dust_at(g.cx, 1.0, 1.6)
			dust_at(g.cx, -1.0, 1.6)
		if F == LAND:
			dust_at(g.cx, -1.0, 1.8)
			dust_at(g.cx, 1.0, 1.4)
		if F > LAND and F < LAND + 8 and F % 2 == 0:
			dust_at(g.cx + 6, 1.0, 1.0 - (F - LAND) * 0.1)
		for i in mons.size():
			if F == int(ceil(hit1[i])):
				debris_at(Vector2(cxs[i] - 4, gy(i) - 26), "คม", F, 0.7)
			if F == int(ceil(hit2[i])):
				debris_at(Vector2(cxs[i] + 4, gy(i) - (mh - top0) * 0.6), "คม", F, 0.8)
				if i == 0:
					burst(Vector2(cxs[0] + 6, G - (mh - top0) * 0.55), F, Color("#ffb070"))
		var bf := F - HOLD1 + HOP0
		if F >= HOLD1:
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
	show_bubble("พายุเถ้าใบมีด!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < IN0 + 2 else (IN0 + 6 - f) / 4.0) if F >= b0 and F < IN0 + 6 else 0.0)
	var dl := F - LAUNCH
	if dl >= 0 and dl < 16:
		word(BM.sfx, clampf(cxs[cxs.size() / 2] - 30, 4, W - 80), 34 - mini(5, dl), Color("#ffe0c0"), 16, 4)
	for i in mons.size():   # ตัวเลข 2 ชุด: ครั้งแรกต่ำ · ครั้งสองสูงกว่า
		var x := maxf(16, cxs[i] + _sway(i, f))
		pop(dmg, x, my + roundf(mh * 0.3) - (i % 2) * 12, F - int(ceil(hit1[i])), Color.WHITE, aff_tag(), aff_col())
		pop(dmg, x + 8, my + roundf(mh * 0.3) - 30 - (i % 2) * 12, F - int(ceil(hit2[i])), Color("#ffe0c0"), aff_tag(), aff_col())   # ครั้งสองสีเถ้าส้ม สูงกว่า

# ── พายุเถ้า ─────────────────────────────────────
## ลมหมุนรอบตัว Rion = กรวยพายุเถ้า: เนื้อกรวยโปร่ง + เกลียวเถ้าหนา 3 ชั้นสี + ถ่านไฟเรือง + ใบมีดเงิน 5 ใบวน · back = ครึ่งหลัง
func _vortex(n: Node2D, f: float, back: bool) -> void:
	var sm := _storm(f)
	if sm <= 0.0:
		return
	var g := geo(f)
	var air := f >= LAUNCH and f < LAND
	var after := f >= LAND
	var foot: float = G - (g.lift * 0.25 if air else 0.0)   # รอบอากาศ: ปลายกรวยยังจรดใกล้พื้น
	var top: float = G - g.lift - 82 - (16 if air else 0)
	var Ht: float = foot - top
	var r0 := 12.0 if not air else 18.0   # รัศมีปลายล่าง
	var r1 := 38.0 if not air else 54.0   # รัศมีปากบน
	if after:
		var q := f - LAND
		r0 += q * 3
		r1 += q * 4
	var cx: float = g.cx - 2
	var spin := f * (1.0 if not air else 1.45)
	var R := func(h: float) -> float: return r0 + (r1 - r0) * pow(h / Ht, 0.8)
	# เนื้อกรวยโปร่ง (ครึ่งหลังเท่านั้น ให้เห็นเป็นรูปทรง)
	if back:
		var y := 0.0
		while y < Ht:
			var r: float = R.call(y)
			for e in 3:   # ขอบนุ่ม: 3 ชั้นแคบ → กว้าง · ด้านบนจางเป็นควัน
				var re: float = r * [0.45, 0.7, 0.92][e]
				px(n, cx - re, foot - y - 2, Color(0.55, 0.5, 0.45, 0.1 * sm * (1 - 0.75 * y / Ht)), re * 2, 2)
			y += 2
	# เกลียวเถ้า 6 เส้น (หนา 3 ชั้น: ขอบเข้ม · เทาเถ้า · ไฮไลต์ครีม)
	for sline in 6:
		for k in 110:
			var u := float(k) / 109
			var h: float = u * Ht
			var a := spin * 1.3 + sline * TAU / 6 + u * 5.2
			var front := sin(a) > 0
			if front == back:
				continue
			var r: float = R.call(h)
			var p := Vector2(cx + cos(a) * r, foot - h + sin(a) * r * 0.24)
			var wv := 1.5 + 2.2 * (1 - absf(cos(a)))   # กว้างสุดตอนอยู่ด้านหน้า/หลัง
			var al := sm * (0.95 if front else 0.5)
			px(n, p.x - wv / 2 - 1, p.y - 1, Color(0.24, 0.2, 0.18, al * 0.8), wv + 2, 3)
			px(n, p.x - wv / 2, p.y - 1, Color(0.66, 0.6, 0.54, al), wv, 2)
			if front and k % 2 == 0:
				px(n, p.x - wv / 2, p.y - 1, Color(0.95, 0.9, 0.8, al), maxf(1.0, wv - 1), 1)
	# ฝุ่นวงฐานพายุ (กวาดพื้น)
	if not back and not air:
		for k in 40:
			var a := spin * 2.2 + k * 0.157
			var rr := r0 + 10 + fb_hash(k, 7, 1) * 10
			px(n, cx + cos(a) * rr, G - 3 + sin(a) * 3 - fb_hash(k, 8, 2) * 4, Color(0.8, 0.74, 0.66, 0.6 * sm), 3 if k % 3 == 0 else 2, 2)
	# เถ้าและถ่านไฟ 80 ชิ้นปลิวตามเกลียว
	for k in 80:
		var h: float = fmod(k * 0.618 * Ht + f * (3.0 if not after else -1.2), Ht)
		var a := spin * 1.7 + k * 2.39996
		var front := sin(a) > 0
		if front == back:
			continue
		var r: float = R.call(h) + 4 + fb_hash(k, 1, 3) * 8
		var p := Vector2(cx + cos(a) * r, foot - h + sin(a) * r * 0.24)
		if k % 6 == 0:   # ถ่านไฟ: แกนเหลือง ขอบส้ม
			px(n, p.x - 1, p.y - 1, Color(1.0, 0.45, 0.15, sm * (0.8 if front else 0.4)), 3, 3)
			px(n, p.x, p.y, Color(1.0, 0.88, 0.45, sm * (1.0 if front else 0.5)), 1, 1)
		else:
			px(n, p.x, p.y, Color(0.78, 0.72, 0.66, sm * (0.85 if front else 0.4)), 2 if k % 4 == 0 else 1, 1)
	# ใบมีดเงิน 5 ใบวนในพายุ (3 ชั้นแบบรอยคม)
	if not after:
		for b in 5:
			var a := spin * 2.0 + b * TAU / 5
			var front := sin(a) > 0
			if front == back:
				continue
			var h: float = Ht * (0.22 + 0.13 * b)
			var r: float = R.call(h) - 2
			var p := Vector2(cx + cos(a) * r, foot - h + sin(a) * r * 0.24)
			var tg := Vector2(-sin(a) * r, cos(a) * r * 0.24).normalized()
			var al := sm * (1.0 if front else 0.5)
			for layer in [[Color("#1a3a9a"), 3.0], [Color("#9ae6ff"), 2.0], [Color.WHITE, 1.0]]:
				var col: Color = layer[0]
				col.a = al
				for j in 9:
					var q := p - tg * j * 1.3
					var w: float = layer[1] * (1 - j / 10.0)
					if w >= 1:
						px(n, q.x - w / 2, q.y - w / 2, col, ceil(w), ceil(w))

## เถ้าฟุ้งทั้งจอตอนพายุพีค (ลอยตามลมจากทิศที่ Rion เคลื่อน)
func _ash_screen(n: Node2D, f: float) -> void:
	var sm := _storm(f)
	if sm < 0.3:
		return
	var a := minf(1.0, (sm - 0.3) / 0.5)
	for k in 90:
		var x := fmod(fb_hash(k, 1, 9) * W + f * (5 + fb_hash(k, 2, 9) * 4) * (1 if f > LAUNCH else -1), W + 20) - 10
		if x < -10:
			x += W + 20
		var y := fmod(fb_hash(k, 3, 9) * G + f * (0.8 + fb_hash(k, 5, 9)), G)
		var ember := k % 7 == 0
		px(n, x, y, Color(1, 0.6, 0.3, 0.8 * a) if ember else Color(0.72, 0.68, 0.64, 0.7 * a), 2 if k % 5 == 0 else 1, 1)

func draw_back(n: Node2D) -> void:
	_ash_screen(n, t / SEC)

func draw_mid(n: Node2D) -> void:
	_vortex(n, t / SEC, true)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var g := geo(f)
	_vortex(n, f, false)
	# แผล: ครั้งแรกแนวนอนต่ำ (ลมหมุนติดพื้น) · ครั้งสองเฉียงสูง (จากกลางอากาศ)
	for i in mons.size():
		var x0: float = cxs[i] + _sway(i, f)
		var d1 := f - hit1[i]
		if d1 >= 0 and d1 < 12:
			var al := 1.0 if d1 < 6 else maxf(0.0, 1 - (d1 - 6) / 6.0)
			var half := mw * 0.22
			slash_line(n, x0 + half, gy(i) - 22, x0 - half, gy(i) - 26, 2, minf(1.0, (d1 + 1) / 2.0), al)
		var d2 := f - hit2[i]
		if d2 >= 0 and d2 < 12:
			var al := 1.0 if d2 < 6 else maxf(0.0, 1 - (d2 - 6) / 6.0)
			var vy := gy(i) - (mh - top0) * 0.55
			var sz := minf(18.0, mw * 0.2)
			slash_line(n, x0 - sz, vy - sz * 0.8, x0 + sz, vy + sz * 0.6, 3 if i == 0 else 2, minf(1.0, (d2 + 1) / 2.0), al)
	if f >= IN0 and f < OUT0 + 4:   # รอยลมหมุนบนพื้น
		var q := minf(f, float(OUT0)) - IN0
		for i in 18:
			var u := float(i) / 17
			var xx := x_in + (x_out - x_in) * minf(1.0, q / (OUT0 - IN0)) * u
			var al := (0.55 - 0.4 * (1 - u)) * (1.0 if f < OUT0 else maxf(0.0, 1 - (f - OUT0) / 4.0))
			px(n, xx, G - 1 - fb_hash(i, 2, 5) * 2, Color(0.82, 0.76, 0.68, al), 3, 1)
	if f >= LAND and f < LAND + 10:   # รอยไถลหลังลง
		var q := f - LAND
		for i in 6:
			px(n, x_land - 14 + i * 4 + minf(q, 6.0), G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)
	if g.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - g.lift / 70.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)

func sounds(F: int) -> void:
	if F < RUN0 or F >= HOLD1:
		var bf := F if F < RUN0 else F - HOLD1 + HOP0
		if bf < RUN0 or bf >= HOP0:
			super.sounds(bf)
		return
	if F < IN0 and (F - RUN0) % 3 == 0:
		var pk := snappedf(0.4 + 0.3 * (F - RUN0) / (IN0 - RUN0), 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == IN0 - 1:   # พายุก่อตัว: ลมทุ้มยาวตลอดรอบพื้น (คลื่นขึ้นลงตามรอบหมุน)
		var v := [N(1.3, "bandpass", 400, 900, 0.45, 1.2, 0, {"attack": 0.2})]
		for k in 5:
			v.append(N(0.28, "bandpass", 900, 2200, 0.35, 2.2, k * 0.24, {"attack": 0.08}))
		play_sfx("st_ground", v)
	if F == LAUNCH:   # ดีดตัว + พายุพีค: ลมสูงหวีดแรงกว่า
		var v := [N(0.12, "lowpass", 900, 150, 0.7, 1), N(1.3, "bandpass", 600, 1400, 0.5, 1.2, 0.02, {"attack": 0.15})]
		for k in 6:
			v.append(N(0.2, "bandpass", 1300, 3200, 0.38, 2.5, 0.05 + k * 0.18, {"attack": 0.05}))
		play_sfx("st_air", v)
	for i in mons.size():
		if F == int(ceil(hit1[i])):
			play_sfx("st_cut1_%d" % i, [N(0.08, "highpass", 3600 - i * 300, 1500, 0.55, 2), N(0.14, "bandpass", 3400, 2200, 0.25, 10, 0.01)])
			sfx_mon(false, (0.6 if foe == "B1" else 1.0) * (1.0 - i * 0.05))
		if F == int(ceil(hit2[i])):
			play_sfx("st_cut2_%d" % i, [N(0.1, "highpass", 4200 - i * 300, 1800, 0.65, 2), N(0.2, "bandpass", 3800, 2400, 0.3, 10, 0.01), T(0.25, "sine", 130, 45, 0.45, 0, 0.002)])
			sfx_mon(i == 0, (0.6 if foe == "B1" else 1.0) * (1.0 - i * 0.05))
	if F == LAND:
		sfx_hit(false)
		play_sfx("brake", [N(0.36, "lowpass", 1600, 300, 0.45, 2)])
	if F == LAND + 2:   # พายุสลาย: ลมจางลง
		play_sfx("st_fade", [N(1.0, "bandpass", 900, 300, 0.3, 1.5)])
