extends "res://tests/lab/lab_stage.gd"
## เขี้ยวพัน bl2 แบบงูพันเหยื่อใน Godot — ย้ายจากหน้าเว็บ wr_bl2 (wrGeo/wrRing/wrView/wrSound)
## วิ่งฟันหน้า → ตีลังกาข้ามหัว ฟันหลังตอนแตะพื้น → หมุนสว่านผ่านหลังมอน (ถูกบัง) ฟันหน้า → วงแสง 3 วงรัดจนแตก เลือดไหล → กระโดดถอยกลับ
## วงที่ k เกิดตอนฟันครั้งที่ k · ครึ่งหลังของวงอยู่หลังมอน ครึ่งหน้าทับ

const MX := 112
const END := 110
const RUN := 18
const WIND := 22
const H1 := 26
const LEAP := 29
const TUCK := 30
const WIND2 := 37
const H2 := 41
const DASH := 44
const H3 := 54
const CINCH := 56
const BURST := 63
const HOP := 68
const HOP2 := 77
const HOME := 86
const ROWS := [0.36, 0.56, 0.76]   # ความสูงวงที่ 1–3 (สัดส่วนจากหัวลงเท้าของเนื้อตัว)

var reach := 0.0
var tip_up := 0.0
var xr := 0.0
var xl := 0.0
var apex := 0.0
var rings: Array = []
var cuts: Array = []

func tech_id() -> String: return "bl2"
func end_frame() -> int: return END
func stops() -> Array: return [[H1, 0.05], [H2, 0.05], [H3, 0.05], [BURST, 0.1]]
func caption() -> String: return "เขี้ยวพัน: ฟันหน้า → ข้ามหัว ฟันหลัง → สว่านผ่านหลัง ฟันหน้า → วงรัด → แตก เลือดไหล"

func setup() -> void:
	place_monster(MX)
	var sw := swing_pt(SWING.A[1])
	reach = roundf(sw.x - 60)
	tip_up = 108 - roundf(sw.y)
	var e := edges(int(mh - tip_up))
	xr = mx0 + e.y - 4 - reach   # ปลายมีดจมเนื้อ 4 จุด · ฝั่งหน้า / ฝั่งหลัง
	xl = maxf(22, mx0 + e.x + 4 + reach)
	for fr in ROWS:
		var row := int(roundf(top0 + bh * fr))
		var re := edges(row)
		var rx: float = (re.y - re.x) / 2 + 7
		rings.append({"cx": mx0 + (re.x + re.y) / 2, "cy": G - mh + row, "rx": rx, "ry": maxf(3, roundf(rx * 0.2))})
	apex = maxf(30, minf(86, bh + 8))
	var ty := G - tip_up
	cuts = [[xr + reach, ty, 8, -10, -8, 9], [xl - reach, ty, -7, 9, 8, -10], [xr + reach - 1, ty, 1, -13, -2, 10]]   # แผล: เฉียงลง · เฉียงขึ้น · ดิ่ง

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "flip": false, "rot": 0.0, "sx": 1.0, "sy": 1.0, "back": false}
	if F < RUN:
		return r
	if F < H1:   # วิ่งเร่ง → ง้างระหว่างวิ่ง
		var tt := (f - RUN + 1) / (H1 - RUN + 1)
		r.cx = home + (xr - home) * (0.4 * tt * tt + 0.6 * tt)
		r.key = "pls_run_bl_%d" % ((F - RUN) % 6) if F < WIND else "pls_atk_bl_%d" % (1 + F - WIND)
		return r
	if F < LEAP:   # ฟัน 1 ตอนถึงตัว · ตามแรง
		r.cx = xr - (f - H1)
		r.key = "pls_atk_bl_%d" % (5 + F - H1)
		if F == H1:
			r.sx = 1.04
			r.sy = 0.95
		return r
	if F < H2:   # ตีลังกาข้ามหัวมอน ลงฝั่งหลัง
		var xa := xr - 2
		var tt := (f - LEAP + 1) / (H2 - LEAP + 1)
		r.cx = xa + (xl - xa) * tt
		r.lift = roundf(4 * apex * tt * (1 - tt))
		if F == LEAP:
			r.key = "pls_hop_bl_2"
		elif F < WIND2:   # ขดตัวหมุนหน้า 1 รอบ · กลับหัวกลางรอบ = หันขวา
			var e := (f - TUCK + 1) / (WIND2 - TUCK)
			r.key = "pls_hop_bl_4"
			r.rot = -TAU * e
			r.flip = e > 0.5
		else:
			r.key = "pls_atk_bl_%d" % mini(4, 1 + F - WIND2)
			r.flip = true
		return r
	if F < DASH:   # ฟัน 2 ตอนเท้าแตะ (เฉียงขึ้น) · ไถลออก
		r.cx = xl - 2 * (f - H2 + 1) + 2
		r.key = "pls_atk_bl_%d" % (5 + F - H2)
		r.flip = true
		if F == H2:
			r.sx = 1.04
			r.sy = 0.95
		return r
	var xd := xl - 6
	if F < H3:
		if F == DASH:   # ย่อถีบ
			r.cx = xd
			r.key = "pls_bl1_3"
			r.flip = true
			r.sy = 0.94
			return r
		var tt := (f - DASH) / (H3 - DASH)   # สว่านผ่านหลังมอน (ถูกบัง) · เฟรมก่อนฟันโผล่ออกมาข้างหน้า
		r.cx = xd + (xr - xd) * tt
		r.key = "pls_spin_bl_%d" % posmod(3 - (H3 - 1 - F), 4)
		r.sx = 0.94
		r.sy = 0.94
		r.back = F < H3 - 1
		return r
	if F < CINCH:   # ฟัน 3 ดิ่งลง
		r.cx = xr - (f - H3)
		r.key = "pls_atk_bl_%d" % (5 + F - H3)
		if F == H3:
			r.sx = 1.05
			r.sy = 0.94
		return r
	if F < BURST:   # ค้างแรง ขึงวงแสง (ตัวสั่น)
		r.cx = xr - 2 + (1 if F - CINCH > 2 and F % 2 else 0)
		r.key = "pls_atk_bl_7"
		r.sy = 0.97
		return r
	var x0 := xr + 1
	var xm := x0 + roundf((home - x0) * 0.62)
	if F < HOP:   # กระตุกมีดกลับ = วงรัด
		r.cx = x0 + (3 if F - BURST < 3 else 2)
		r.key = "pls_atk_bl_1" if F - BURST < 3 else "pls_atk_bl_0"
		return r
	if F < HOP2:
		_hop(r, f, HOP, HOP2, x0, xm, 14)
		return r
	if F < HOME:
		_hop(r, f, HOP2, HOME, xm, home, 8)
		return r
	r.cx = home
	if F < HOME + 2:
		r.key = "pls_hop_bl_1"
		r.sy = 0.94
	return r

func _hop(r: Dictionary, f: float, t0: int, t1: int, xa: float, xb: float, h: float) -> void:   # กระโดดถอยหันหน้าหาเป้า
	var q := f - t0
	if q < 1:
		r.cx = xa
		r.key = "pls_hop_bl_1"
		r.sy = 0.94
		return
	var tt := minf(1.0, q / (t1 - t0 - 1))
	r.cx = xa + (xb - xa) * tt
	r.lift = roundf(4 * h * tt * (1 - tt))
	r.key = "pls_hop_bl_2" if int(q) == 1 else "pls_hop_bl_3"

func _hk(F: int) -> Array:
	return [F - H1, F - H2, F - H3]

func _kb(F: int) -> float:
	var kbs := [-3, 3, -3]
	var hk := _hk(F)
	var kb := 0.0
	for i in 3:
		if hk[i] >= 0 and hk[i] < 4:
			kb += roundf(kbs[i] * (1 - hk[i] / 4.0))
	var db := F - BURST
	if db >= 0 and db < 6:
		kb -= roundf(4 * (1 - db / 6.0))
	return kb

func _cz(F: int) -> float:   # รัด: วงหดเข้า เร่งตอนท้าย
	var dz := F - CINCH
	return 0.0 if dz < 0 else (pow((dz + 1.0) / (BURST - CINCH), 2) if F < BURST else 0.0)

func frame(f: float, F: int, fresh: bool) -> void:
	var hk := _hk(F)
	var dz := F - CINCH
	var db := F - BURST
	var hit_shk := 0.0
	for d in hk:
		if d >= 0 and d < 3:
			hit_shk = maxf(hit_shk, 2 * (1 - d / 3.0))
	shake(F, hit_shk if hit_shk > 0 else (3.5 * (1 - db / 6.0) if db >= 0 and db < 6 else (0.6 if dz >= 0 and db < 0 else 0.0)))
	dim_to(0.12 if F >= LEAP and F < H3 else (0.22 if dz >= 0 and db < 6 else 0.0))
	# มอน: ผงะทุกครั้งที่โดน · ถูกบีบตอนรัด · แตก = วาบ → เลือดไหล (อมแดงเป็นจังหวะ)
	var cz := _cz(F)
	var hurt := cz > 0.3 or (db >= 0 and db < 10)
	var flash := db >= 0 and db < 2
	for d in hk:
		hurt = hurt or (d >= 0 and d < 5)
		flash = flash or (d >= 0 and d < 2)
	var bleed := db >= 6
	var fl := 1.0 if flash else (0.05 + 0.07 * maxf(0.0, sin(F * 0.5)) if bleed else 0.0)
	var sqx := 1 - 0.1 * cz + (0.06 if db >= 0 and db < 3 else 0.0)
	var sqy := 1 + 0.05 * cz - (0.08 if db >= 0 and db < 3 else 0.0)
	show_mon(hurt_key() if hurt else idle_key(f), _kb(F), fl, Color("#c02838") if bleed and fl < 1 else Color.WHITE, sqx, sqy)
	# Rion: หลังมอนตอนสว่าน (ถูกบัง) + ร่างติดตา
	var g := geo(f)
	rion.z_index = 0 if g.back else 4
	set_rion(rion, g, 0.9 if g.back else 1.0)
	if g.back:
		for k in [2, 1]:
			var gp := geo(f - k)
			if gp.back:
				ghost(gp, 0.12 * (3 - k), Color("#9ae6ff"), 1.0, true)
	else:
		if F > LEAP and F < H2:
			for k in [2, 1]:
				ghost(geo(f - k), 0.14 * (3 - k), Color("#9ae6ff"), 1.0)
		if F > DASH and F < H3:
			for k in [2, 1]:
				var gp := geo(f - k)
				if not gp.back:
					ghost(gp, 0.14 * (3 - k), Color("#9ae6ff"), 1.0)
	if fresh:
		for e in [[LEAP, xr, 1.0, 1.0], [H2, xl, -1.0, 1.1], [DASH, xl - 6, -1.0, 1.2], [H3, xr, 1.0, 0.9], [HOP, xr + 1, -1.0, 0.9], [HOP2, geo(HOP2).cx, -1.0, 0.7], [HOME, float(home), 1.0, 0.6]]:
			if F == e[0]:
				dust_at(e[1], e[2], e[3])
		if F >= RUN + 1 and F < H1 and (F - RUN - 1) % 3 == 0:
			dust_at(g.cx + 6, 1.0, 0.5 + 0.5 * (F - RUN) / 8.0)
		for i in 3:
			if hk[i] == 0:
				burst(Vector2(cuts[i][0] + _kb(F), cuts[i][1]), F, Color("#9ae6ff"))
		if db == 0:
			burst(Vector2(mx0 + mw / 2.0 + _kb(F), rings[1].cy), F, Color("#ff8a7a"))
	# ตัวหนังสือ
	var ty := G - tip_up
	var px0 := roundf(clampf(mx0 + mw / 2.0, 34, W - 34))
	for i in 3:
		var d: int = hk[i]
		if d >= 0 and d < 8:
			var wx := maxf(4, xl - reach - 6) if i == 1 else minf(W - 36, xr + reach + 6 + i * 4)
			if i == 2:   # ครั้งที่ 3: เลื่อนพ้นตัวเลข + ป้ายอ่อนแอ/ต้านทานของครั้งนี้
				wx = minf(W - 36, maxf(wx, px0 + 28 + maxf(10, text_w(aff_tag(), 8) / 2) + 4))
			word("ฉับ!", wx, maxf(16, ty - (30 if i == 1 else 22 + i * 8) - mini(4, d)))
	if dz >= 2 and db < 0:
		word("รัด…", maxf(4, mx0 - 6), maxf(16, G - bh - 8), Color("#9ae6ff"))
	if db >= 0 and db < 14:
		word("ฟึ่บ!!", maxf(4, mx0 - 10), maxf(18, G - bh - 6 - mini(5, db)))
	if bleed and db >= 14 and db < 60:
		word("เลือดไหล", roundf(mx0 + mw / 2.0 + _kb(F)) + 8, maxf(14, G - bh - 12) + roundf(sin(F * 0.25)) + 7, Color(1, 154 / 255.0, 168 / 255.0, minf(1.0, maxf(0.0, (db - 14) / 4.0))))
	show_bubble("เขี้ยวพัน!", g.cx, maxf(14, G - g.lift - 74), F - WIND + 2, (1.0 if F < H1 else (H1 + 3 - f) / 3.0) if F >= WIND - 2 and F < H1 + 3 else 0.0)
	for i in 3:
		pop(dmg, px0 + (i - 1) * 28, maxf(30, G - bh - 12) - i * 6, hk[i], Color.WHITE, aff_tag() if i == 2 else "", aff_col())

## วงแสงที่ k: กวาดออกจากจุดฟันตามทางที่ Rion วน · front = ครึ่งหน้า · s = สเกลตอนรัด
func _ring(n: Node2D, k: int, F: int, front: bool, s: float) -> void:
	var rg: Dictionary = rings[k]
	var t0: int = [H1, H2, H3][k]
	var p := minf(1.0, (F - t0 + 1.0) / [9, 9, 6][k])
	if p <= 0 or F >= BURST:
		return
	var a0: float = [-0.3, PI + 0.3, 0.0][k]
	var cnt := maxi(24, int(roundf(rg.rx * 4)))
	var lit := 0.6 + 0.4 * sin(F * 1.7) if F >= CINCH else 1.0
	for i in int(cnt * p) + 1:
		var a := a0 + TAU * i / cnt
		var sn := sin(a)
		if (sn >= 0) != front:
			continue
		var x: float = rg.cx + cos(a) * rg.rx * s
		var y: float = rg.cy + sn * rg.ry * s
		var head := i > cnt * p - 4 and p < 1
		px(n, x - 1, y - 1, Color(154 / 255.0, 230 / 255.0, 1, (0.75 if front else 0.45) * lit), 3, 2)
		px(n, x, y - 1, Color.WHITE if head else Color(1, 1, 1, (0.95 if front else 0.55) * lit))

func draw_back(n: Node2D) -> void:
	var F := int(floor(t / SEC))
	for k in 3:
		_ring(n, k, F, false, 1 - 0.42 * _cz(F))

## ชั้นกลาง (ทับมอน ใต้ Rion): แผล 3 รอย · ครึ่งหน้าของวง · เส้นขึงตอนรัด · วงขาด + เลือดพุ่ง · หยดเลือด · เงา
func draw_mid(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var hk := _hk(F)
	var db := F - BURST
	var dz := F - CINCH
	var kb := _kb(F)
	var s := 1 - 0.42 * _cz(F)
	for i in 3:
		var d: int = hk[i]
		if d < 0 or db >= 14:
			continue
		var c: Array = cuts[i]
		var al := 1.0 if db < 0 else 1 - db / 14.0
		if d < 3:
			slash_line(n, c[0] + c[2] + kb, c[1] + c[3], c[0] + c[4] + kb, c[1] + c[5], 2, minf(1.0, (d + 1) / 2.0), al)
		else:
			var L := Vector2(c[4] - c[2], c[5] - c[3]).length()
			for j in int(L) + 1:
				var x: float = c[0] + kb + c[2] + (c[4] - c[2]) * j / L
				var y: float = c[1] + c[3] + (c[5] - c[3]) * j / L
				px(n, x, y, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, 0.8 * al), 2, 1)
				px(n, x, y, Color(208 / 255.0, 40 / 255.0, 56 / 255.0, al))
	for k in 3:
		_ring(n, k, F, true, s)
	if dz >= 0 and db < 0:   # เส้นขึงจากปลายมีดถึงวงล่าง
		var g := geo(f)
		var rg: Dictionary = rings[2]
		var tp := Vector2(g.cx + reach, G - tip_up)
		var ep := Vector2(rg.cx + rg.rx * s * cos(0.35), rg.cy + rg.ry * s * sin(0.35))
		var L := (ep - tp).length()
		for i in int(L) + 1:
			var q := tp + (ep - tp) * i / L
			px(n, q.x, q.y, Color(220 / 255.0, 248 / 255.0, 1, 0.6 + 0.3 * sin(F + i * 0.3)))
	if db >= 0 and db < 18:   # วงขาดเป็นเศษแสง + เลือดกระเซ็นจากทั่วรอยวง
		for k in 3:
			var rg: Dictionary = rings[k]
			for i in 14:
				var a := i * TAU / 14 + k
				var v := 1.2 + fb_hash(i, k, 3) * 1.6
				if db < 10:
					px(n, rg.cx + cos(a) * rg.rx * 0.58 + cos(a) * v * db * 1.4, rg.cy + sin(a) * rg.ry * 0.58 - 0.6 * v * db + 0.12 * db * db, Color(220 / 255.0, 248 / 255.0, 1, 1 - db / 10.0))
				var bx3: float = rg.cx + (fb_hash(i, k, 7) - 0.5) * rg.rx + (fb_hash(i, k, 5) - 0.5) * 3.2 * db
				var by3: float = rg.cy + (fb_hash(i, k, 8) - 0.5) * rg.ry * 2 - (1.2 + fb_hash(i, k, 6) * 2) * db + 0.16 * db * db
				if i < 10 and db >= 1 and by3 < G - 1:
					disc(n, bx3, by3, maxf(0.6, 1.6 - db * 0.06), Color((190 + (i % 3) * 20) / 255.0, 30 / 255.0, (40 + (i % 2) * 10) / 255.0, maxf(0.0, 1 - db / 18.0)))
	if db >= 6 and F < END - 4:   # หยดเลือดจากรอยวง
		for k in 3:
			var rg: Dictionary = rings[k]
			for j in 2:
				var t0 := BURST + 6 + k * 3 + j * 7
				if F < t0:
					continue
				var q := (F - t0) % 14
				var y: float = rg.cy + rg.ry * 0.5 + q * q * 0.18
				if y < G - 1:
					var x: float = rg.cx + (-0.4 if j else 0.35) * rg.rx * 0.6
					px(n, x, y, Color("#2a1a14"), 2, 3)
					px(n, x, y + 1, Color("#d02838"))
	var g := geo(f)
	if not g.back and g.lift > 2:
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.35, 1 - g.lift / 90.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)

## ชั้นหน้า: ประกายเหล็กที่ปลายมีด · ไอคอนหยดเลือดเหนือหัว
func draw_fx(n: Node2D) -> void:
	var F := int(floor(t / SEC))
	var hk := _hk(F)
	var db := F - BURST
	var kb := _kb(F)
	for i in 3:
		var d: int = hk[i]
		if d < 0 or d >= 4:
			continue
		var c: Array = cuts[i]
		star_px(n, c[0] + kb, c[1], 3 + d * 3, Color.WHITE, Color("#9ae6ff"))
		for j in 6:
			var a := (0.0 if i == 1 else PI) + (fb_hash(j, i, 1) - 0.5) * 1.6
			var v := 2 + fb_hash(j, i, 2) * 2
			px(n, c[0] + cos(a) * v * d, c[1] + sin(a) * v * d + 0.3 * d * d, Color.WHITE if d < 2 else Color("#9ae6ff"))
	if db >= 6:
		var a := minf(1.0, maxf(0.0, (db - 14) / 4.0))
		if a > 0:
			var ix := roundf(mx0 + mw / 2.0 + kb)
			var iy := maxf(14, G - bh - 12) + roundf(sin(F * 0.25))
			for r in 7:
				var w := 1 + r if r < 2 else (4 + (r - 2) if r < 5 else 7 - (r - 4) * 2)
				px(n, ix - w / 2.0 - 1, iy + r, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, a), w + 2, 1)
				px(n, ix - w / 2.0, iy + r, Color(1, 138 / 255.0, 138 / 255.0, a) if r == 2 else Color(208 / 255.0, 40 / 255.0, 56 / 255.0, a), w, 1)
			px(n, ix - 4, iy + 7, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, a), 7, 1)

func sounds(F: int) -> void:
	var big := 0.6 if foe == "B1" else 1.0
	if F >= RUN and F < H1 and (F - RUN) % 3 == 0:
		var pk := snappedf(0.22 + 0.2 * (F - RUN) / 8.0, 0.02)
		play_sfx("step%s" % pk, [N(0.06, "lowpass", 900, 200, pk, 1)])
	if F == WIND or F == WIND2:
		sfx_release()
	if F == H1 or F == H2 or F == H3:   # ฉับ + วงแสงเริ่มพัน
		sfx_hit(false)
		play_sfx("ring", [T(0.08, "triangle", 2600, 3400, 0.06)])
		if F == H1:
			sfx_mon(false, big)
	if F == LEAP:
		play_sfx("leap", [N(0.08, "lowpass", 700, 150, 0.35, 1), N(0.3, "bandpass", 600, 1800, 0.18, 2, 0.04)])
	if F == DASH:
		play_sfx("dash", [N(0.1, "lowpass", 600, 120, 0.5, 1)])
	if F > DASH and F < H3 and (F - DASH) % 2 == 1:   # สว่านหวีด
		play_sfx("drill%d" % F, [N(0.1, "bandpass", 1400 + (F - DASH) * 110, 3000, 0.18, 3)])
	if F >= CINCH and F < BURST and (F - CINCH) % 2 == 0:   # วงรัด: เสียงขึงตึงไต่
		play_sfx("cinch%d" % F, [T(0.12, "sawtooth", 160 + (F - CINCH) * 40, 220 + (F - CINCH) * 46, 0.05, 0, 0.002, {"lp": 1800})])
	if F == BURST:   # ฟึ่บ: วงขาด + เลือดพุ่ง
		play_sfx("burst", [N(0.05, "highpass", 3000, 7000, 0.55, 3), N(0.5, "bandpass", 900, 400, 0.4, 1, 0.02), N(0.2, "lowpass", 400, 80, 0.6, 1)])
		sfx_mon(false, big)
		duck()
	if F == HOP + 1 or F == HOP2 + 1:
		play_sfx("hopk", [N(0.06, "bandpass", 600, 1600, 0.2, 2)])
	if F == HOP2 or F == HOME:
		play_sfx("hopl", [N(0.09, "lowpass", 700, 150, 0.3, 1)])
