extends "res://tests/lab/fl_base.gd"
## เงาสองคม bl6 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: นิเท็นอิจิริว — สองมีดมือละเล่มอิสระ รูป X เกิดจากคมสองเล่มไขว้กันเอง)
## ข้อยกเว้นกฎ "ถือมือขวามือเดียว" เฉพาะท่านี้ตามทีม (มีดครัวมือขวา + มีดสั้นมือซ้าย)
## วิ่งเข้า ตั้งท่า enso ระหว่างวิ่ง (State BL6_enso) → ถึงตัวฟันมีดขวา \ (State BL6_cut1 · โดน 1)
## → ก้าวสั้น มีดซ้ายไขว้ตาม / (State BL6_cross · โดน 2) ทิ้งเงาของท่าแรกค้างข้างตัว → ค้างท่าไขว้ enkyoku · แผล X เรือง + เลือดหยด → กระโดดถอย

const ENSO := 25    # เริ่มตั้งท่าระหว่างวิ่ง
const H1 := 30      # ถึงตัว ฟันมีดขวา
const STEP2 := 34   # ก้าวสั้น
const H2 := 38      # มีดซ้ายไขว้
const HOLDF := 48

var x_hit := 0.0
var cx_m := 0.0
var cy_m := 0.0

func mv() -> Dictionary:
	return {"id": "bl6", "slide": 0, "reach": 0, "kb": 6, "shk": 2.5, "sfx": "ฉับ ฉับ!", "what": "เงาสองคม (bl6)"}

func caption() -> String: return "วิ่ง ตั้งท่าสองมีด → ฟันมีดขวา → มีดซ้ายไขว้ตามเป็น X ทิ้งเงา → ค้างท่าไขว้ → กระโดดถอย"

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	hit_f.append(float(H1))
	hit_f.append(float(H2))
	x_hit = vis.end.x + 30
	cx_m = vis.get_center().x
	cy_m = vis.get_center().y
	set_end(x_hit - 4)
	bubble_name = "เงาสองคม"
	bubble_at = Vector2(ENSO - 2, H1 + 6)

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < H1:   # วิ่งเข้า · ตั้งท่าสองมีดช่วงท้าย (ไถลในท่า)
		var b := {"cx": run_x(f, IDLE, H1, x_hit), "lean": -0.06, "key": "pls_run_bl_%d" % ((F - IDLE) % 6)}
		if F >= ENSO:
			b.key = "pls_enso_0"
			b.lean = -0.04
		return b
	if F < STEP2:   # ฟันมีดขวา ไถลตามแรง
		var q := f - H1
		return {"cx": x_hit - 3 * minf(1.0, q / 3.0), "key": "pls_tcut_0", "sy": 0.95 if q < 2 else 1.0, "sx": 1.04 if q < 2 else 1.0}
	if F < H2:   # ก้าวสั้นเข้า ยังท่าฟัน (มือซ้ายง้างอยู่หน้าอก)
		var u := (f - STEP2) / (H2 - STEP2)
		return {"cx": x_hit - 3 - 5 * u, "key": "pls_tcut_0", "lean": -0.06 * u}
	var q := f - H2   # ไขว้ + ค้าง enkyoku
	return {"cx": x_hit - 8 - 2 * minf(1.0, q / 3.0), "key": "pls_cross_0", "sy": 0.95 if q < 2 else 1.0, "sx": 1.04 if q < 2 else 1.0}

func rion_ghosts(f: float, F: int) -> void:
	if F >= ENSO and F < H1:   # ร่างติดตาตอนวิ่งตั้งท่า
		ghost(geo(f - 1.5), 0.16)
	if F >= H2 and F < H2 + 12:   # เงา: ท่าฟันแรกค้างข้างตัว สีครามเข้มแล้วจาง
		var gg := geo(float(H1) + 1)
		gg.cx += 6
		ghost(gg, 0.55 * (1 - (f - H2) / 12.0), Color("#1a1f4a"), 0.85, true)

func fx(n: Node2D, f: float) -> void:
	var kb := mon_kb(f)
	var cx := cx_m + kb
	var s := minf(16.0, minf(vis.size.x, vis.size.y) * 0.32)
	var cyc := cy_m
	# แผล \ (มีดขวา) · / (มีดซ้าย) · X เรืองตอนครบ
	var d1 := f - H1
	if d1 >= 0 and d1 < 22:
		var al := 1.0 if d1 < 12 else maxf(0.0, 1 - (d1 - 12) / 10.0)
		slash_line(n, cx + s, cyc - s, cx - s, cyc + s, 3, minf(1.0, (d1 + 1) / 2.0), al)
	var d2 := f - H2
	if d2 >= 0 and d2 < 16:
		var al := 1.0 if d2 < 8 else maxf(0.0, 1 - (d2 - 8) / 8.0)
		slash_line(n, cx - s, cyc - s, cx + s, cyc + s, 3, minf(1.0, (d2 + 1) / 2.0), al)
		if d2 < 4:   # จุดไขว้เรือง
			star_px(n, cx, cyc, 6 + d2 * 3, Color.WHITE, Color("#9ae6ff"))
		# เลือดหยดจากจุดไขว้ (สถานะเลือดไหลของท่า · ภาพเท่านั้น)
		if d2 >= 3:
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
	step_snd(F, IDLE, ENSO)
	if F == ENSO:   # ตั้งท่า: มีดสองเล่มกระทบลม
		play_sfx("sd_enso", [N(0.06, "highpass", 4200, 3000, 0.3, 3), N(0.06, "highpass", 3600, 2600, 0.25, 3, 0.06)])
	if F == H1:
		sfx_hit(false)
	if F == H2:   # ไขว้: เสียงคมเฉือนสูงกว่า + ทุ้ม
		play_sfx("sd_cross", [N(0.09, "highpass", 4800, 2000, 0.7, 2), N(0.2, "bandpass", 3800, 2400, 0.3, 10, 0.01), T(0.3, "sine", 120, 45, 0.6, 0, 0.002, {"drive": true})])
