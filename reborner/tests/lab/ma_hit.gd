extends "res://tests/lab/lab_stage.gd"
## มอนโจมตีกลับใน Godot — ย้ายจากหน้าเว็บ mon_M01_hit / mon_M01_guard (maGeo/monAtkView/monAtkSound)
## มอนกระดึ๊บ 2 ครั้งเข้าหา → ถีบพุ่งตัวยืด → กระแทกตอนตกถึงตัว Rion → ตัวแบนแปะ แล้วเด้งกลับที่
## ไฟล์นี้ = Rion โดนตี (ภาพ PixelLab hurt 6 ภาพ + กระเด็น) · ma_guard.gd = ตั้งรับ (ภาพ guard · ดาเมจครึ่งหนึ่ง · มอนกระดอนมึน)
## หน้าเว็บมีแค่ M01 · ที่นี่เลือกมอนได้ 5 ตัว (บทบาทภาพเหมือนกัน) · ดาเมจ = ATK มอน × 100/100 × MIT_K/(MIT_K + DEF Rion 30) × ตั้งรับ 0.5 (สูตรเดียวกับหน้าเว็บ)

const MX := 74
const END := 92
const WAIT := 16
const H1 := 22
const L1 := 30
const H2 := 32
const L2 := 40
const LEAP := 42
const HIT := 48
const BACK := 51
const GRD := 37
const DEF := 30   # Rion ความชำนาญ 20 (csDef = 20 + prof × 0.5)
const MIT_K := 100.0   # Formulas.MIT_K
const ROLE := {"idle": 0, "wind": 3, "atk": 4, "follow": 5, "hurt": 6}

var front := 0.0
var near := 0.0
var atk := 0
var mon_ghosts: Array[Sprite2D] = []

func guard() -> bool: return false
func tech_id() -> String: return "ma"
func end_frame() -> int: return END
func stops() -> Array: return [[HIT, 0.1]]
func caption() -> String:
	return ("โจมตี → Rion ตั้งรับ (ดาเมจครึ่งหนึ่ง)" if guard() else "โจมตี → Rion โดนตี") + " · มอน ATK %d · Rion DEF %d" % [atk, DEF]

func setup() -> void:
	for r in CsvDb.load_csv("res://data/monsters.csv"):
		if str(r.monster_id) == foe:
			atk = int(r.atk)
	dmg = maxi(1, int(roundf(atk * 100 / 100.0 * MIT_K / (MIT_K + DEF) * (0.5 if guard() else 1.0))))
	place_monster(MX)
	front = home - 60 + 40   # ขอบหน้าตัว Rion (ผืน x40) · Rion ยืนที่ W−100
	near = roundf(front - mw / 2.0 + 6)
	for i in 2:
		var s := Sprite2D.new()
		s.material = fx_mat()
		s.z_index = 1
		add_child(s)
		mon_ghosts.append(s)

func _home() -> float:
	return W - 100.0

## ตำแหน่งมอน (cx · lift · บทบาทภาพ · ยืด/ยุบ · หมุน) + Rion (x ซ้ายผืน · ภาพ · วาบ) · maGeo
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var hx := float(MX)
	var s := {"cx": hx, "lift": 0.0, "role": "idle", "ri": posmod(F / 4, 3), "sx": 1.0, "sy": 1.0, "rot": 0.0}
	var x1 := hx + (near - hx) * 0.32
	var x2 := hx + (near - hx) * 0.62
	if F >= WAIT and F < H1:   # ย่อเก็บแรง ตัวสั่น
		var q := F - WAIT
		s.role = "wind"
		s.sy = 1 - 0.03 * mini(4, q)
		s.sx = 1 + 0.025 * mini(4, q)
		s.cx = hx + ((1 if q % 2 else -1) if q >= 3 else 0)
	elif F >= H1 and F < L1:
		_hop(s, f, H1, L1 - H1, hx, x1, 10)
	elif F >= L1 and F < H2:   # ตกพื้นยุบ
		s.cx = x1
		s.role = "wind"
		s.sy = 0.86
		s.sx = 1.1
	elif F >= H2 and F < L2:
		_hop(s, f, H2, L2 - H2, x1, x2, 12)
	elif F >= L2 and F < LEAP:   # ย่อลึกก่อนพุ่ง
		s.cx = x2
		s.role = "wind"
		s.sy = 0.8
		s.sx = 1.14
	elif F >= LEAP and F < HIT:   # ถีบพุ่ง → ตกใส่ตัว Rion ตรงจังหวะกระทบ
		_hop(s, f, LEAP, HIT - LEAP, x2, near, 18)
		s.sx = 0.86
		s.sy = 1.18
	elif F >= HIT and F < BACK:   # กระแทก: ตัวแบนแปะ
		s.cx = near
		s.role = "follow"
		s.sy = 0.9
		s.sx = 1.08
	elif F >= BACK:   # เด้งกลับที่ (ตั้งรับ = ถูกดีดแรง สูงกว่า หมุนมึน)
		var n := 13 if guard() else 11
		var hb := 22.0 if guard() else 14.0
		var q := f - BACK
		if q < n:
			var u := (q + 1) / (n + 1)
			s.cx = near + (hx - near) * u
			s.lift = roundf(4 * hb * u * (1 - u))
			s.role = "hurt" if guard() else "atk"
			if guard():
				s.rot = -u * TAU
			else:
				s.sx = 0.92
				s.sy = 1.1
		elif q < n + 3:
			var k := int(q) - n
			s.cx = hx
			s.role = "wind"
			s.sy = [0.8, 0.88, 0.96][k]
			s.sx = [1.14, 1.08, 1.03][k]
		else:
			s.role = "hurt" if guard() and q < n + 16 else "idle"
	# Rion
	var r := {"x": _home(), "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "flash": 0.0}
	var d := F - HIT
	if not guard():
		if d >= 0:   # ภาพ hurt ทีละจังหวะ · กระเด็น 14 แล้วค่อยเดินกลับที่
			var ks := [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5]
			if d < ks.size():
				r.key = "pls_hurt_%d" % ks[d]
			var df := f - HIT
			r.x = _home() + (roundf(14 * _e(minf(1.0, (df + 1) / 6.0))) if d < 6 else (roundf(14 * (1 - _e((df - 5) / 12.0))) if d < 18 else 0.0))
			r.flash = 1.0 if d < 2 else 0.0
	else:
		if F >= GRD and F < HIT:   # เห็นมอนถีบตัว → ย่อตั้งการ์ด (ทันก่อนกระทบ)
			r.key = "pls_guard_%d" % (1 if F - GRD < 2 else 2)
		elif d >= 0 and d < 10:   # ปะทะ: ถูกดันถอยนิด การ์ดไม่หลุด
			r.key = "pls_guard_3"
			r.x = _home() + roundf(6 * _e(minf(1.0, (d + 1) / 3.0)) * (1.0 if d < 6 else 1 - (d - 5) / 5.0))
		elif d >= 10 and d < 14:
			r.key = "pls_guard_%d" % (2 if d < 12 else 1)
	return {"s": s, "r": r}

func _e(v: float) -> float:
	return v * v * (3 - 2 * v)

func _hop(s: Dictionary, f: float, t0: int, n: int, xa: float, xb: float, h: float) -> void:   # กระโดด: ตัวยืดตามแนวพุ่ง
	var u := (f - t0 + 1) / (n + 1)
	s.cx = xa + (xb - xa) * u
	s.lift = roundf(4 * h * u * (1 - u))
	s.role = "atk"
	s.sx = 0.9
	s.sy = 1.12

func _mon_key(s: Dictionary) -> String:
	return "%s_%d" % [foe, s.ri if s.role == "idle" else ROLE[s.role]]

func _place(sp: Sprite2D, s: Dictionary, alpha: float, white: float) -> void:   # มอน: ยึดเท้า · หมุน = รอบกลางตัว
	var mt := tx(_mon_key(s))
	var h := mt.get_height()
	sp.texture = mt
	sp.centered = false
	sp.visible = alpha > 0
	sp.modulate.a = alpha
	sp.rotation = s.rot
	sp.scale = Vector2(s.sx, s.sy)
	if s.rot != 0.0:
		sp.offset = Vector2(-roundf(mt.get_width() / 2.0), -h / 2.0)
		sp.position = Vector2(roundf(s.cx), roundf(G - s.lift) - h / 2.0)
	else:
		sp.offset = Vector2(-roundf(mt.get_width() / 2.0), -h)
		sp.position = Vector2(roundf(s.cx), roundf(G - s.lift))
	sp.material.set_shader_parameter("tint", Color.WHITE)
	sp.material.set_shader_parameter("amount", white)

func _hit_pt(r: Dictionary) -> Vector2:
	return Vector2(front + (r.x - _home()) - 2, G - 46)

func frame(f: float, F: int, fresh: bool) -> void:
	var d := F - HIT
	shake(F, (2.0 if guard() else 3.5) * (1 - d / 6.0) if d >= 0 and d < 6 else 0.0)
	var g := geo(f)
	_place(mon, g.s, 1.0, 0.0)
	for k in 2:
		if F > LEAP and F < HIT:
			_place(mon_ghosts[k], geo(f - (k + 1)).s, 0.14 * (2 - k), 0.0)
		else:
			mon_ghosts[k].visible = false
	var r: Dictionary = g.r
	set_rion(rion, {"cx": r.x + 60, "lift": 0.0, "key": r.key}, 1.0, Color.WHITE, r.flash)
	if fresh:
		var xs := [float(MX), MX + (near - MX) * 0.32, MX + (near - MX) * 0.62]
		for e in [[H1, 0, 0.6], [L1, 1, 0.7], [H2, 1, 0.7], [L2, 2, 0.9], [LEAP, 2, 1.1]]:
			if F == e[0]:
				dust_at(xs[e[1]], 1.0, e[2])
				dust_at(xs[e[1]], -1.0, e[2])
		if F == HIT:
			burst(_hit_pt(geo(HIT).r), F, Color("#ffd24a") if guard() else Color("#c8f0a0"))
	var hp := _hit_pt(r)
	if d >= 0 and d < 14:
		word("แก๊ง!" if guard() else "ปึ้ก!", hp.x - 30, maxf(18, hp.y - 22 - mini(4, d)), Color("#ffe08a") if guard() else Color.WHITE)
	pop(dmg, front + 20, G - 92, d, Color("#cfe6ff") if guard() else Color("#ff8a7a"), "ตั้งรับ −50%" if guard() else "", Color("#cfe6ff"))
	show_bubble("", 0, 0, 0, 0.0)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var d := F - HIT
	var g := geo(f)
	var s: Dictionary = g.s
	if s.lift > 2:   # เงาพื้นตอนลอย
		for i in range(-7, 8):
			if absi(i) < 7 * maxf(0.4, 1 - s.lift / 30.0):
				px(n, s.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.35), 2, 1)
	if d >= 0 and d < 8:   # รอยเท้าไถล
		for i in 6:
			px(n, front + 18 + i * 3 + d * 2, G - 1 - fb_hash(i, 9, 1) * 2, Color(216 / 255.0, 204 / 255.0, 184 / 255.0, 1 - d / 8.0), 2, 1)
	var hp := _hit_pt(g.r)
	if d >= 0 and d < 12:   # เมือกกระเซ็น (โดน) / ประกายโลหะ (ตั้งรับ)
		for i in 10:
			var a := PI * (0.75 + fb_hash(i, 5, 1) * 0.6)
			var v := 1.5 + fb_hash(i, 5, 2) * 2.5
			var y := hp.y + sin(a) * v * d + 0.3 * d * d
			if y < G - 1:
				var c := (Color.WHITE if d < 4 else Color("#ffd24a")) if guard() else (Color("#7fd36a") if i % 3 else Color("#c8f0a0"))
				px(n, hp.x + cos(a) * v * d, y, c, 2, 2)
	if guard() and d >= 0 and d < 5:   # แนวการ์ดสว่างวาบ
		for i in 3:
			px(n, hp.x - 2, hp.y - 14 + i * 9, Color(1, 1, 1, 1 - d / 5.0), 2, 6)
	if guard():   # มึน: ดาววนเหนือหัว
		var q := F - BACK - 13
		if q >= 0 and q < 16:
			var hh := tx(hurt_key()).get_height()
			for i in 3:
				var a := F * 0.35 + i * 2.1
				star_px(n, MX + cos(a) * 9, G - hh - 4 + sin(a) * 3, 2, Color.WHITE, Color("#ffe08a"))

func sounds(F: int) -> void:
	var p := 0.6 if foe == "B1" else 1.0
	if F == WAIT:   # ย่อเก็บแรง (เมือกบีบ)
		play_sfx("squeeze", [N(0.25, "lowpass", 500, 160, 0.25, 3, 0, {"attack": 0.15})])
	if F == H1 or F == H2:   # ดึ๋ง
		play_sfx("boing", [T(0.16, "sine", 160, 420, 0.32, 0, 0.004)])
	if F == LEAP:
		play_sfx("leap", [T(0.2, "sine", 140, 520, 0.4, 0, 0.004), N(0.16, "bandpass", 500, 1800, 0.25, 2)])
	if F == L1 or F == L2:   # แปะพื้น
		play_sfx("splat", [N(0.1, "lowpass", 900, 200, 0.35, 2)])
	if F == HIT:
		if guard():   # แก๊ง: โลหะ + แรงกระแทกเบา
			play_sfx("gclang", [T(0.22, "square", 1900, 1300, 0.16, 0, 0.002, {"lp": 5000}), N(0.18, "bandpass", 3800, 2600, 0.45, 12),
				T(0.2, "sine", 130, 42, 1.0, 0, 0.002, {"drive": true}), N(0.12, "bandpass", 900, 300, 0.9, 1.2, 0, {"drive": true}), N(0.03, "highpass", 3000, 3000, 0.5)])
		else:   # ปึ้ก + เมือกแตก
			sfx_hit(false, "CR")
			play_sfx("goo", [N(0.25, "lowpass", 1200, 300, 0.4, 3, 0.02)])
		duck()
		sfx_mon(false, p)
	if not guard() and F == HIT + 5:   # เซถอยลากเท้า
		play_sfx("stagger", [N(0.22, "lowpass", 1400, 300, 0.25, 2)])
	if F == BACK:   # เด้งกลับ
		play_sfx("back%s" % guard(), [T(0.18, "sine", 300 if guard() else 220, 700 if guard() else 480, 0.3, 0, 0.004)])
	if F == BACK + (13 if guard() else 11):
		play_sfx("splat", [N(0.1, "lowpass", 900, 200, 0.35, 2)])
	if guard() and F == BACK + 14:   # มึน
		play_sfx("dizzy", [T(0.08, "triangle", 1400, 1100, 0.06), T(0.08, "triangle", 1400, 1100, 0.06, 0.1), T(0.08, "triangle", 1400, 1100, 0.06, 0.2)])
