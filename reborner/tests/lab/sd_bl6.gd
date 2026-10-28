extends "res://tests/lab/fl_base.gd"
## เงาสองคม bl6 (ตามรายงานทีม R2: นิเท็นอิจิริว — สองคมมือละเล่ม รูป X เกิดจากคมสองเล่มไขว้กันเอง)
## รอบ 2 (kwan 28 ต.ค. "เงาสองคม ทำเป็นเสกมีดเงาออกมาอีกอัน" · "ท่าดูไม่ลื่น เจนเพิ่มให้ไหลลื่นได้"):
## Rion ถือมีดจริงเล่มเดียว (มือขวา ตามกฎ) → ยืนที่เดิมเสกมีดเงา: ควันเงาไหลเข้ามือซ้าย ก่อเป็นมีดสีม่วงเข้ม (ท่ากลาง PixelLab bl6_summon · มีดมือซ้ายย้อมเงาด้วยโค้ด tools/sprites/shadow_knife.py)
## → ไถลเข้าในท่าสองคม (ร่างติดตาม่วง) → ฟันมีดจริง \ (ท่ากลาง bl6_cut · โดน 1) → มีดเงาไขว้ตาม / (ท่ากลาง bl6_x · โดน 2 สีม่วง)
## → ค้างท่าไขว้ → มีดเงาสลายกลับเป็นควัน → กระโดดถอย (ท่าถอยของเครื่องฟัน = มือซ้ายว่างตามเดิม)

const STEP1 := 21   # ก้าวเข้า 1 ก้าว
const SUM1 := 31    # เสกเสร็จ
const GO := 32      # ไถลเข้า
const CUT0 := 37    # ภาพฟัน (ท่ากลาง)
const H1 := 39
const X0 := 41
const H2 := 43
const FADE := 48    # มีดเงาสลาย
const HOLDF := 54

## ตำแหน่งมีดเงาบนผืน 120x112 ของแต่ละภาพ (กลางใบมีด) · จาก shadow_knife.py (วัดหลังสร้างชุดภาพ)
const SDK := {"pls_sd_summon_2": Vector2(84.4, 77.9), "pls_sd_summon_3": Vector2(84.5, 80.5), "pls_sd_cut_0": Vector2(84.8, 86.8), "pls_sd_cut_1": Vector2(78.5, 71.3), "pls_sd_cut_2": Vector2(73.6, 69.3), "pls_sd_x_0": Vector2(47.1, 83.4), "pls_sd_x_1": Vector2(48.6, 78.8), "pls_sd_x_2": Vector2(49.6, 76.7)}

var x_hit := 0.0
var x_sum := 0.0
var cx_m := 0.0
var cy_m := 0.0

func mv() -> Dictionary:
	return {"id": "bl6", "slide": 0, "reach": 0, "kb": 6, "shk": 2.5, "sfx": "ฉับ ฉับ!", "what": "เงาสองคม (bl6)"}

func caption() -> String: return "เสกมีดเงามือซ้าย → ไถลเข้า → ฟันมีดจริง → มีดเงาไขว้ตามเป็น X → มีดเงาสลายเป็นควัน → กระโดดถอย"

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	hit_f.append(float(H1))
	hit_f.append(float(H2))
	x_hit = vis.end.x + 30
	x_sum = x_home - 22
	cx_m = vis.get_center().x
	cy_m = vis.get_center().y
	set_end(x_hit - 6)
	bubble_name = "เงาสองคม"
	bubble_at = Vector2(STEP1, SUM1 + 2)

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < STEP1:   # ก้าวเข้าในจอ 1 ก้าวก่อนเสก (ไม่เสกชิดขอบจอ)
		var u := (f - IDLE) / (STEP1 - IDLE)
		return {"cx": x_home + (x_sum - x_home) * u, "key": "pls_run_bl_%d" % ((F - IDLE) % 6), "lean": -0.04}
	if F < SUM1:   # เสกมีดเงา ยืนนิ่ง (ภาพท่ากลาง 4 ภาพ)
		var u := (f - STEP1) / (SUM1 - STEP1)
		return {"cx": x_sum, "key": "pls_sd_summon_%d" % mini(3, int(u * 4.0))}
	if F < CUT0:   # ไถลเข้าในท่าสองคม (เร่ง)
		var u := (f - GO) / (CUT0 - GO)
		return {"cx": x_sum + (x_hit - x_sum) * u * u, "key": "pls_sd_summon_3", "lean": -0.08 * u}
	if F < X0:   # ฟันมีดจริง (ภาพ 0–3)
		var q := f - CUT0
		return {"cx": x_hit - 3 * minf(1.0, q / 3.0), "key": "pls_sd_cut_%d" % mini(2, int(q * 1.2)), "sy": 0.96 if F == H1 else 1.0}
	var q := f - X0   # มีดเงาไขว้ + ค้าง · สลายแล้วใช้ภาพไม่มีมีดเงา
	var k := mini(2, int(q * 1.2))
	return {"cx": x_hit - 3 - 3 * minf(1.0, q / 3.0), "key": ("pls_sd_x_%d" % k) if F < FADE else "pls_sd_x_2n", "sy": 0.96 if F == H2 else 1.0}

## กลางมีดเงาบนจอ (ไม่มี = Vector2.INF)
func _knife(f: float) -> Vector2:
	var g := geo(f)
	if not SDK.has(g.key):
		return Vector2.INF
	var p: Vector2 = SDK[g.key]
	return Vector2(g.cx - 60 + p.x, G - g.lift - 108 + p.y)

func rion_ghosts(f: float, F: int) -> void:
	if F >= GO and F < X0 + 2:   # ร่างติดตาสีเงาตอนไถล/ฟัน
		for k in [2, 1]:
			ghost(geo(f - k * 1.2), 0.15 * (3 - k), Color("#2a1f5a"), 0.75, true)

func fx(n: Node2D, f: float) -> void:
	var F := int(floor(f))
	var g := geo(f)
	# เสก: ควันเงาไหลวนเข้ามือซ้าย แล้ววาบม่วงตอนมีดก่อตัว
	var hand := Vector2(g.cx + 8, G - 34)
	var kp := _knife(f)
	if kp != Vector2.INF:
		hand = kp
	if F >= STEP1 and F < SUM1 + 2:
		var u := clampf((f - STEP1) / (SUM1 - 4 - STEP1), 0.0, 1.0)
		var on := minf(1.0, (f - STEP1) / 3.0) * (1.0 if F < SUM1 - 2 else maxf(0.0, 1 - (f - SUM1 + 2) / 4.0))
		disc(n, hand.x, hand.y, 6 + 8 * u, Color(0.1, 0.05, 0.22, 0.35 * on))   # ไอมืดรวมที่มือ (ใหญ่ขึ้นตามที่ควันไหลเข้า)
		for k in 36:
			var ph := fmod(f * 0.07 + fb_hash(k, 1, 2), 1.0)   # 0 ไกล → 1 ถึงมือ
			var a := k * 2.4 + ph * 4.5
			var r := (1 - ph) * (30 + fb_hash(k, 2, 2) * 16)
			var al := sin(PI * ph) * on
			var p := hand + Vector2(cos(a) * r, sin(a) * r * 0.6 - (1 - ph) * 6)
			px(n, p.x - 1, p.y - 1, Color(0.1, 0.05, 0.24, 0.85 * al), 3, 3)
			px(n, p.x + cos(a - 0.3) * 3, p.y + sin(a - 0.3) * 2, Color(0.5, 0.32, 0.9, 0.5 * al), 2, 1)
		var e := f - (SUM1 - 4)
		if e >= 0 and e < 5:   # มีดก่อตัว: วาบม่วง
			disc(n, hand.x, hand.y, 4 + e * 2, Color(0.55, 0.35, 1, 0.35 * (1 - e / 5.0)))
			star_px(n, hand.x, hand.y, 5 + e * 2, Color(0.85, 0.75, 1), Color("#6a4cff"))
	# มีดเงา: ไอมืดบางๆ ลอยขึ้นจากใบมีดตลอดที่ยังอยู่
	if kp != Vector2.INF and F >= SUM1 - 4 and F < FADE:
		disc(n, kp.x, kp.y, 5, Color(0.35, 0.2, 0.75, 0.22))   # ไอม่วงรอบมีดเงา (อ่านออกบนจอเล็ก)
		for k in 7:
			var ph := fmod(f * 0.1 + k / 5.0, 1.0)
			px(n, kp.x + (fb_hash(k, 3, 1) - 0.5) * 8, kp.y - ph * 12, Color(0.2, 0.12, 0.4, 0.6 * (1 - ph)), 2, 2)
	# สลาย: มีดเงาแตกเป็นควันลอยขึ้น
	var dfz := f - FADE
	if dfz >= 0 and dfz < 10:
		var p0 := Vector2(g.cx - 60 + (SDK["pls_sd_x_2"] as Vector2).x, G - 108 + (SDK["pls_sd_x_2"] as Vector2).y)
		for k in 14:
			var a := k * 0.45
			var r := dfz * (1.2 + fb_hash(k, 4, 1) * 1.5)
			px(n, p0.x + cos(a) * r, p0.y + sin(a) * r * 0.5 - dfz * 1.6, Color(0.22, 0.14, 0.42, 0.7 * (1 - dfz / 10.0)), 2, 2)
	# แผล \ (มีดจริง ฟ้า) · / (มีดเงา ม่วง) · จุดไขว้เรือง
	var kb := mon_kb(f)
	var cx := cx_m + kb
	var s := minf(16.0, minf(vis.size.x, vis.size.y) * 0.32)
	var cyc := cy_m
	var d1 := f - H1
	if d1 >= 0 and d1 < 22:
		var al := 1.0 if d1 < 12 else maxf(0.0, 1 - (d1 - 12) / 10.0)
		slash_line(n, cx + s, cyc - s, cx - s, cyc + s, 3, minf(1.0, (d1 + 1) / 2.0), al)
	var d2 := f - H2
	if d2 >= 0 and d2 < 16:
		var al := 1.0 if d2 < 8 else maxf(0.0, 1 - (d2 - 8) / 8.0)
		var pr := minf(1.0, (d2 + 1) / 2.0)
		for w in 3:   # รอยมีดเงา: ม่วงเข้ม ขอบม่วงสว่าง
			var o := float(w - 1)
			for i in 26:
				var u := i / 25.0
				if u > pr:
					break
				var x := cx - s + 2 * s * u + o
				var y := cyc - s + 2 * s * u
				px(n, x - 1, y - 1, Color(0.18, 0.1, 0.38, al) if w == 1 else Color(0.62, 0.45, 1, al * 0.7), 2 if w == 1 else 1, 2 if w == 1 else 1)
		if d2 < 4:   # จุดไขว้เรือง (ขาว + ม่วง)
			star_px(n, cx, cyc, 6 + d2 * 3, Color.WHITE, Color("#8a6cff"))
		if d2 >= 3:   # เลือดหยดจากจุดไขว้ (สถานะเลือดไหลของท่า · ภาพเท่านั้น)
			for i in 6:
				var t0 := fb_hash(i, 2, 4) * 4
				var q := d2 - 3 - t0
				if q < 0:
					continue
				var x := cx + (fb_hash(i, 1, 1) - 0.5) * s * 1.4
				var y := cyc + (fb_hash(i, 3, 2) - 0.5) * s + q * q * 0.35
				if y < G - 2:
					px(n, x, y, Color(0.7, 0.08, 0.1, maxf(0.0, 0.9 - q * 0.06)), 2, 2)

func snd(F: int) -> void:
	step_snd(F, IDLE, STEP1)
	if F == STEP1:   # เสก: ลมเงาดูดเข้า (ต่ำ ไม่มีกริ๊ง)
		play_sfx("sd_summon", [N(0.7, "bandpass", 250, 900, 0.35, 1.5, 0, {"attack": 0.5}), T(0.7, "sine", 60, 110, 0.3, 0, 0.4)])
	if F == SUM1 - 4:   # มีดก่อตัว
		play_sfx("sd_form", [N(0.12, "highpass", 2500, 1200, 0.4, 3), T(0.25, "sine", 140, 70, 0.35, 0, 0.003)])
	if F == GO:
		play_sfx("sd_go", [N(0.2, "bandpass", 600, 1800, 0.4, 2)])
	if F == H1:
		sfx_hit(false)
	if F == H2:   # มีดเงาไขว้: เฉือนสูง + ทุ้ม
		play_sfx("sd_cross", [N(0.09, "highpass", 4800, 2000, 0.7, 2), N(0.2, "bandpass", 3800, 2400, 0.3, 10, 0.01), T(0.3, "sine", 120, 45, 0.6, 0, 0.002, {"drive": true})])
	if F == FADE:   # มีดเงาสลาย
		play_sfx("sd_fade", [N(0.5, "bandpass", 1200, 300, 0.25, 1.5, 0, {"attack": 0.05})])
