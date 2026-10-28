extends "res://tests/lab/lab_stage.gd"
## ตัดเอ็น bl7 แบบ Attack on Titan ใน Godot — ย้ายจากหน้าเว็บ aot_bl7 (aotGeo/aotView/aotSound/slowFx)
## ย่อชาร์จ → พุ่งหมุนสว่าน (ภาพหมุนตัวจริง 4 มุม) ทะลุใต้ขา → ไถลโผล่อีกฝั่งหันกลับ → เงียบ → แผลหลังขาระเบิด ไอพุ่ง มอนทรุดคุกเข่า
##   → ตีลังกาข้ามหัวกลับ → มอนช้าลง (นาฬิกาทราย + แถบคิว +20%)

const MX := 112
const END := 112
const CR := 18
const GO := 24
const OUT := 34
const TURN := 38
const B := 46
const B2 := 49
const UP := 56
const AIR := 58
const LAND := 72
const HOME := 77

var far := 0.0
var legs: Array[float] = []
var cy := 0.0
var pass_f: Array[int] = []
var mon_top: Sprite2D
var mon_leg: Sprite2D

func tech_id() -> String: return "bl7"
func end_frame() -> int: return END
func stops() -> Array: return [[B, 0.1], [B2, 0.06]]
func caption() -> String: return "ตัดเอ็น: ชาร์จ → สว่านใต้ขา → เงียบ → แผลระเบิด → ตีลังกากลับ"

func setup() -> void:
	place_monster(MX)
	far = mx0 - 26
	legs.append(mx0 + roundf(mw * 0.7))   # ขาหน้า → ขาหลัง ตามทางที่ Rion ผ่าน
	legs.append(mx0 + roundf(mw * 0.32))
	cy = G - maxf(4, minf(14, roundf(mh * 0.16)))
	for lx in legs:
		var pf := OUT
		for t0 in range(GO, OUT):
			if geo(t0).cx <= lx:
				pf = t0
				break
		pass_f.append(pf)
	# มอนสองท่อน: ลำตัวบน (ไม่ย่อ) + ขา 38% ล่าง (ยุบ = เข่าพับ)
	mon_top = Sprite2D.new()
	mon_leg = Sprite2D.new()
	for s in [mon_top, mon_leg]:
		s.centered = false
		s.region_enabled = true
		s.material = fx_mat()
		s.z_index = 1
		add_child(s)

func _zip_x(u: float) -> float:
	return home - 30 + (far + 12 - (home - 30)) * u

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "flip": false, "rot": 0.0, "sx": 1.0, "sy": 1.0}
	if F < CR:
		return r
	if F < GO:   # ก้าวย่อชาร์จ เข่ายุบลงเรื่อยๆ · ตัวสั่น
		var q := F - CR
		r.cx = home - 30 * pow(minf(1.0, (f - CR) / 3.0), 0.5)
		r.key = "pls_bl1_3"
		r.sy = 1 - 0.012 * mini(5, q)
		r.sx = 1 + 0.008 * mini(5, q)
		if q >= 2:
			r.cx += 1 if q % 2 else -1
		return r
	if F < OUT:   # สว่าน: ภาพหมุนจริง 1 มุม/เฟรม · ความเร็วคงที่
		r.cx = _zip_x((f - GO + 1) / (OUT - GO))
		r.key = "pls_spin_bl_%d" % ((F - GO) % 4)
		r.sy = 0.92
		r.sx = 1.04
		return r
	if F < TURN:   # ไถลเบรกในท่าย่อ
		var u := (f - OUT + 1) / (TURN - OUT)
		r.cx = far + 12 * pow(1 - minf(1.0, u), 2)
		r.key = "pls_bl1_3"
		r.sy = 0.94
		r.sx = 1.03
		return r
	if F < UP:   # หันกลับ · ยืนนิ่งมองมอน
		r.cx = far
		if F == TURN:
			r.key = "pls_spin_bl_3"
		else:
			r.key = "pls_spin_bl_2"
			r.sy = 1 - 0.012 * posmod((F - TURN) / 4, 2)
		return r
	if F < AIR:
		r.cx = far
		r.key = "pls_hop_bl_1"
		r.flip = true
		return r
	var top := minf(72, maxf(42, mh - 2))
	if F < LAND:   # ตีลังกาหน้าข้ามหัวมอน 1 รอบ
		var u := (f - AIR + 1) / (LAND - AIR + 1)
		var e := u * u * (3 - 2 * u)
		r.cx = far + (home - far) * u
		r.lift = roundf(4 * top * u * (1 - u))
		r.key = "pls_hop_bl_4"
		r.flip = true
		r.rot = TAU * e
		return r
	r.cx = home
	if F < LAND + 2:
		r.key = "pls_hop_bl_1"
		r.flip = true
		return r
	if F < HOME:
		r.key = "pls_spin_bl_2" if F < LAND + 3 else "pls_spin_bl_3"
	return r

func _kneel(d: int) -> float:
	return 1.0 if d < 0 else (1 - 0.2 * (d / 4.0) if d < 4 else (0.8 + 0.03 * (d - 4) / 2.0 if d < 6 else 0.82))

func frame(f: float, F: int, fresh: bool) -> void:
	var d := F - B
	shake(F, 3.0 * (1 - d / 6.0) if d >= 0 and d < 6 else (2.0 * (1 - (F - B2) / 4.0) if F >= B2 and F < B2 + 4 else 0.0))
	dim_to(0.22 if F >= GO and F < OUT else (0.12 if F >= OUT and F < B else (0.22 * (1 - d / 10.0) if d >= 0 and d < 10 else 0.0)))
	# มอน: ยืนหายใจ (ไม่รู้ตัว) → วาบขาว ผงะ → ทรุดคุกเข่า → กะเผลก ช้าลง อมม่วงเทา
	var slow := d >= 12
	var kneel := _kneel(d)
	var mk := hurt_key() if d >= 0 and d < 6 else idle_key(f, 8.0 if slow else 4.0)
	var mt := tx(mk)
	var amt := 1.0 if d >= 0 and d < 2 else (0.8 if F == B2 else (0.12 + 0.06 * sin(F * 0.3) if slow else 0.0))
	var tint := Color("#6a7ab8") if slow else Color.WHITE
	var limp := 1 if slow and posmod(F / 8, 2) else 0
	var ih := mt.get_height()
	var cut := int(roundf(ih * 0.62))
	var lh := ih - cut
	var leg_h := maxi(2, int(roundf(lh - ih * (1 - kneel))) - limp)
	var mx: float = mx0 + roundf((mw - mt.get_width()) / 2.0)
	mon.visible = false
	for s in [mon_top, mon_leg]:
		s.texture = mt
		s.material.set_shader_parameter("tint", tint)
		s.material.set_shader_parameter("amount", amt)
	mon_leg.region_rect = Rect2(0, cut, mt.get_width(), lh)
	mon_leg.position = Vector2(mx, G - leg_h)
	mon_leg.scale = Vector2(1, float(leg_h) / lh)
	mon_top.region_rect = Rect2(0, 0, mt.get_width(), cut)
	mon_top.position = Vector2(mx, G - leg_h - cut)
	# Rion + ร่างติดตา (สว่าน 3 ร่างฟ้า · ตีลังกา 2 ร่าง)
	var g := geo(f)
	set_rion(rion, g)
	if F > GO and F < OUT + 1:
		for k in [3, 2, 1]:
			ghost(geo(f - k), 0.14 * (4 - k), Color("#9ae6ff"), 1.0)
	if F > AIR and F < LAND:
		for k in [2, 1]:
			ghost(geo(f - k), 0.12 * (3 - k))
	if fresh:
		for e in [[GO, home - 30 + 8, 1.0, 1.8], [OUT, far + 12, -1.0, 1.2], [OUT + 2, far + 6, -1.0, 0.8], [AIR, far, -1.0, 1.0], [LAND, float(home), 1.0, 1.1], [B + 3, mx0 + 4.0, -1.0, 1.1], [B + 3, mx0 + mw - 4.0, 1.0, 1.1]]:
			if F == e[0]:
				dust_at(e[1], e[2], e[3])
		if F == B or F == B2:
			burst(Vector2(legs[0 if F == B else 1], G - roundf((G - cy) * kneel) - 2), F, Color("#9ae6ff"))
	# ตัวหนังสือ
	if d >= 0 and d < 16:
		word("ฉึบ!", maxf(4, mon_rect().get_center().x - 64), maxf(14, mon_rect().position.y - 30 - mini(5, d)))   # ซ้ายของตัวเลข
	if F >= B2 and F < B2 + 14:
		word("ฉึบ!", minf(W - 34, mon_rect().get_center().x + 44), maxf(14, mon_rect().position.y - 30 - mini(5, F - B2)))   # ขวาของตัวเลขครั้งที่ 2
	if F >= TURN + 2 and F < B:   # เงียบ: มอนยังไม่รู้ตัว
		var k := F - TURN - 2
		word(".".repeat(1 + mini(2, k >> 1)), mx0 + mw / 2.0 - 4, G - mh - 4, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, minf(1.0, k / 2.0)), 9)
	var sd := F - LAND + 4   # ช้าลง
	if sd >= 14 and sd < 50:
		word("ช้าลง", roundf(mcx) + 9, maxf(12, G - roundf(mh * kneel) - 14) + roundf(sin(F * 0.2)) + 4 - mini(3, sd - 14), Color("#b8ccff"))
	if sd >= 8:
		var k := minf(1.0, (sd - 8) / 8.0)
		var e := k * k * (3 - 2 * k)
		word("คิว", W - 121, 13, Color(1, 1, 1, minf(1.0, (sd - 8) / 3.0)), 7)
		if k >= 1:
			word("+20%", W - 122 + 46 + roundf(e * 110 * 0.2) + 6, 13, Color("#ffb0a0"), 7)
	show_bubble("ตัดเอ็น!!", g.cx, G - 74, F - CR, (1.0 if F < GO else (GO + 3 - f) / 3.0) if F >= CR and F < GO + 3 else 0.0)
	if hits > 1:
		pop(dmg, maxf(16, mon_rect().get_center().x - 4), maxf(26.0, mon_rect().position.y - 6), F - B, Color.WHITE, aff_tag(), aff_col())
	pop(dmg, maxf(16, mon_rect().get_center().x - 4) + (32 if hits > 1 else 0), maxf(26.0, mon_rect().position.y - 6) - (6 if hits > 1 else 0), F - B2, Color.WHITE, aff_tag(), aff_col())   # เหนือตัวมอน ไม่ทับ Rion ที่ยืนหลังมอน · ครั้งที่ 2 เรียงข้าง

## ชั้นกลาง (หลังมอน หน้า Rion ตามลำดับวาดของเว็บ): แผลที่ขา · วงเกลียวสว่าน · ชาร์จ
func draw_mid(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var d := F - B
	var kneel := _kneel(d)
	var g := geo(f)
	for i in 2:   # รอยแผลหลังขา: ตอนผ่าน = เส้นบางจางค้าง · ระเบิด = แผลเปิด
		var lx := legs[i]
		var t0 := pass_f[i]
		var bt := B if i == 0 else B2
		var ky: float = G - roundf((G - cy) * kneel)
		if F >= t0 and F < bt:
			var al := 0.9 if F < t0 + 2 else 0.35 + 0.15 * sin(F * 0.8)
			for k in 8:
				px(n, lx + 4 - k, ky - 5 + roundf(k * 7 / 8.0), Color(1, 1, 1, al))
		if F >= bt and F < bt + 12:
			slash_line(n, lx + 7, ky - 8, lx - 7, ky + 4, 3, minf(1.0, (F - bt + 1) / 2.0), 1.0 if F < bt + 6 else 1 - (F - bt - 5) / 7.0)
	if g.lift > 2:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.35, 1 - g.lift / 90.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	if F >= GO and F < OUT + 2:   # สว่าน: วงเกลียวฟ้า-ขาวพันรอบตัว ไหลไปหลังตัว + เส้นความเร็ว
		var al := 1.0 if F < OUT else 0.4
		var mid := G - 30
		for k in 4:
			var ex: float = g.cx + 6 + k * 9
			var ph := F * 1.9 + k * 1.3
			var rr := 22 - k * 3
			for i in 22:
				var a := ph + i * 0.22
				if sin(a + 0.6) < -0.2:
					continue
				var big := i > 16
				px(n, ex + cos(a) * 4, mid + sin(a) * rr, Color(1, 1, 1, al * (1 - k * 0.22)) if big else Color(154 / 255.0, 230 / 255.0, 1, al * (0.5 - k * 0.1)), 2 if big else 1, 2 if big else 1)
		for i in 7:
			px(n, g.cx + 26 + roundf(fb_hash(i, F, 3) * 14), G - 6 - roundf(fb_hash(i, 4, 1) * 52), Color(230 / 255.0, 248 / 255.0, 1, 0.75 * al), 14 + roundf(fb_hash(i, F, 2) * 26), 1)
	if F >= CR + 1 and F < GO:   # ชาร์จ: ลมดูดเข้าหาตัว · ฝุ่นวน · ประกายวิ่งตามใบมีด
		var q := F - CR
		for i in 6:
			px(n, g.cx - 34 + ((q * 7 + i * 13) % 20), G - 8 - roundf(fb_hash(i, 2, 1) * 48), Color(230 / 255.0, 248 / 255.0, 1, 0.3 + 0.1 * q), 8 + roundf(fb_hash(i, q, 3) * 10), 1)
		for i in 6:
			var a := q * 0.9 + i * 1.05
			px(n, g.cx + cos(a) * (16 - q), G - 2 - absf(sin(a)) * (2 + q * 0.6), Color("#e2d6c0"), 2, 1)
		if q >= 3:
			star_px(n, g.cx - 22, G - 44, 2 + (q - 3) * 2, Color.WHITE, Color("#9ae6ff"))

## ชั้นหน้า: ประกายแวบที่ขาตอนผ่าน · รอยไถล · ไอพุ่งจากแผล · นาฬิกาทราย + แถบคิว
func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var d := F - B
	var kneel := _kneel(d)
	for i in 2:
		var q := F - pass_f[i]
		if q >= 0 and q < 3:
			star_px(n, legs[i], cy - 1, 3 + q * 2, Color.WHITE, Color("#9ae6ff"))
	if F >= OUT and F < TURN + 4:
		for i in 8:
			px(n, far + 14 + i * 4, G - 1, Color(216 / 255.0, 204 / 255.0, 184 / 255.0, 1 - (F - OUT) / 8.0), 2, 1)
	for i in 2:   # ระเบิดแผล: เส้นแรงระเบิด + ไอพุ่ง (ขาว → เทา ลอยขึ้นไปหลังมอน)
		var lx := legs[i]
		var q := F - (B if i == 0 else B2)
		var ky: float = G - roundf((G - cy) * kneel)
		if q < 0:
			continue
		if q < 4:
			for j in 7:
				var a := PI * (0.95 + j * 0.16)
				for s in range(2, 6 + q * 6):
					px(n, lx + cos(a) * s, ky - 2 + sin(a) * s, Color(1, 1, 1, 1 - q / 4.0))
		for j in 14:
			var a := q - j * 0.9
			if a < 0 or a > 26:
				continue
			var r := fb_hash(i, j, 7)
			var x := lx - (0.5 + r * 1.3) * a * 1.6 - 2
			var y: float = ky - 3 - (1.1 + fb_hash(i, j, 8) * 1.2) * a * 1.6 + 0.012 * a * a
			var s: float = roundf(2 + a * 0.3 + r * 2)
			var al := maxf(0.0, 1 - a / 26.0)
			disc(n, x, y, s / 2.0, Color(1, 1, 1, al) if a < 6 else Color(214 / 255.0, 220 / 255.0, 228 / 255.0, al * 0.85))
	var sd := F - LAND + 4   # slowFx
	if sd >= 12:
		var k := minf(1.0, (sd - 12) / 4.0)
		var hx: float = roundf(mcx)
		var hy: float = maxf(12, G - roundf(mh * kneel) - 14) + roundf(sin(F * 0.2))
		var O := Color(42 / 255.0, 26 / 255.0, 20 / 255.0, k)
		var sand := Color(232 / 255.0, 184 / 255.0, 74 / 255.0, k)
		px(n, hx - 5, hy - 7, O, 11, 2)
		px(n, hx - 5, hy + 6, O, 11, 2)
		px(n, hx - 4, hy - 6, Color(200 / 255.0, 160 / 255.0, 96 / 255.0, k), 9, 1)
		px(n, hx - 4, hy + 6, Color(200 / 255.0, 160 / 255.0, 96 / 255.0, k), 9, 1)
		for r in 5:
			var w := 7 - r * 1.4
			for yy in [hy - 5 + r, hy + 5 - r]:
				px(n, hx - w / 2 - 1, yy, O)
				px(n, hx + w / 2, yy, O)
				px(n, hx - w / 2, yy, Color(223 / 255.0, 234 / 255.0, 1, k), maxf(1, w), 1)
		var sa := (posmod(F / 6, 8)) / 8.0
		px(n, hx - 2, hy - 4 + roundf(sa * 2), sand, 4, maxf(1, 3 - roundf(sa * 3)))
		px(n, hx, hy, sand, 1, 2)
		px(n, hx - 3 + roundf(sa), hy + 3 - roundf(sa * 2), sand, 6 - roundf(sa * 2), 1 + roundf(sa * 2))
	if sd >= 8:   # แถบคิวมุมขวาบน: เครื่องหมายมอนเลื่อนถอย 20%
		var k := minf(1.0, (sd - 8) / 8.0)
		var e := k * k * (3 - 2 * k)
		var x0 := W - 122
		var x1 := W - 12
		var a := minf(1.0, (sd - 8) / 3.0)
		px(n, x0 - 2, 4, Color(16 / 255.0, 10 / 255.0, 40 / 255.0, 0.75 * a), x1 - x0 + 4, 17)
		px(n, x0, 10, Color(138 / 255.0, 144 / 255.0, 168 / 255.0, a), x1 - x0, 1)
		var rx := x0 + 20
		var mxk: float = x0 + 46 + roundf(e * (x1 - x0) * 0.2)
		px(n, rx - 3, 7, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, a), 7, 7)
		px(n, rx - 2, 8, Color(65 / 255.0, 132 / 255.0, 201 / 255.0, a), 5, 5)
		px(n, mxk - 3, 7, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, a), 7, 7)
		px(n, mxk - 2, 8, Color(208 / 255.0, 80 / 255.0, 64 / 255.0, a), 5, 5)
		if k > 0 and k < 1:
			for i in range(1, 4):
				px(n, mxk - 4 - i * 3, 10, Color(208 / 255.0, 80 / 255.0, 64 / 255.0, 0.5 - i * 0.12), 2, 1)

func sounds(F: int) -> void:
	var big := 0.6 if foe == "B1" else 1.0
	if F == CR:
		sfx_charge()
	if F == GO:   # ถีบพื้นระเบิดออก
		play_sfx("go", [N(0.12, "lowpass", 700, 110, 0.7, 1)])
		sfx_release()
	if F > GO and F < OUT and (F - GO) % 2 == 1:   # สว่านหวีดหมุน
		play_sfx("drill%d" % F, [N(0.1, "bandpass", 1400 + (F - GO) * 120, 3200, 0.22, 3)])
	if F in pass_f:   # ติ๊งเบาตอนผ่านขา
		play_sfx("tink", [T(0.04, "triangle", 3200, 2600, 0.06)])
	if F == OUT:
		play_sfx("brake", [N(0.32, "lowpass", 1500, 300, 0.35, 2)])
	if F == B or F == B2:   # ฉึบ + ไอพุ่งฟู่
		play_sfx("shub", [N(0.06, "highpass", 3000, 7000, 0.55, 3), T(0.05, "square", 1800, 900, 0.09, 0.01, 0.002, {"lp": 4000}), N(0.9, "highpass", 5000, 2500, 0.22, 1, 0.03)])
		duck()
	if F == B:
		sfx_mon(false, big)
	if F == B + 4:   # ทรุดเข่ากระแทกพื้น
		play_sfx("kneel", [N(0.16, "lowpass", 500, 90, 0.55 * (1.3 if big < 1 else 1.0), 1)])
	if F == AIR:
		play_sfx("air", [N(0.08, "lowpass", 700, 150, 0.35, 1), N(0.25, "bandpass", 600, 1800, 0.18, 2, 0.04)])
	if F == LAND:
		play_sfx("land", [N(0.09, "lowpass", 700, 150, 0.4, 1)])
	if F == LAND + 8:   # ช้าลง: เสียงไล่ต่ำ
		play_sfx("slow", [T(0.7, "sine", 520, 130, 0.12), T(0.7, "triangle", 780, 196, 0.05, 0.05)])
