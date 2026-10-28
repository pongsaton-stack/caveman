extends "res://tests/lab/fl_base.gd"
## ก้าวเงา bl13 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: ปันจักสีลัต ย่างก้าวลังกา — ก้าวไขว้ต่ำเลื้อยเฉียงเข้า ปาดสั้น ก้าวไขว้ถอยออกด้านข้าง)
## รอบ 2 (kwan 28 ต.ค. "ก้าวเงา ชาร์ทพลังนานกว่านี้หน่อย" · "ท่าดูไม่ลื่น เจนเพิ่มให้ไหลลื่นได้"):
## วิ่งออกตัวสั้น → ทรุดต่ำชาร์จ 24 เฟรม (เงาใต้เท้าแผ่ · เส้นเงาไต่จากพื้นเข้าตัว · เงายืดไปหามอน · จอมืดลง · ตัวสั่น · ตาวาบ)
## → เลื้อยก้าวไขว้พุ่งเข้าเร็ว (ท่ากลาง PixelLab bl13_glide 6 เฟรม) → ดีดตัวปาดต่ำ (bl13_cut 4 เฟรม: เลื้อย → ปาดระดับเข่า)
## → เลื้อยถอยเฉียงออกด้านข้าง → กระโดดถอย

const LOW := 24     # ทรุดต่ำ เริ่มชาร์จ
const CHG := 48     # ชาร์จจบ พุ่ง
const CUT0 := 56    # เริ่มดีดตัวปาด (ภาพ pls_sh_cut)
const HITF := 58
const OUT0 := 62    # เริ่มถอยเลื้อย
const HOLDF := 72

var x_low := 0.0
var x_hit := 0.0

func mv() -> Dictionary:
	return {"id": "bl13", "slide": 0, "reach": 0, "kb": 3, "shk": 1.6, "sfx": "แฉ่บ!", "what": "ก้าวเงา (bl13)"}

func caption() -> String: return "ออกตัว → ทรุดต่ำชาร์จเงา → เลื้อยก้าวไขว้พุ่งเข้า → ดีดตัวปาดระดับเข่า → เลื้อยถอยเฉียงออก → กระโดดถอย"

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	hit_f.append(float(HITF))
	x_hit = vis.end.x + 26
	x_low = x_home - 24
	set_end(x_hit + 22)
	bubble_name = "ก้าวเงา"
	bubble_at = Vector2(LOW + 2, CHG)

## ความแรงชาร์จ 0–1
func _chg(f: float) -> float:
	return clampf((f - LOW) / (CHG - LOW), 0.0, 1.0)

func _glide(f: float) -> String:
	return "pls_sh_glide_%d" % posmod(int(floor(f / 1.5)), 6)

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < LOW:   # ออกตัวสั้น
		return {"cx": x_home + (x_low - x_home) * ((f - IDLE) / (LOW - IDLE)), "lean": -0.05, "key": "pls_run_bl_%d" % ((F - IDLE) % 6)}
	if F < CHG:   # ชาร์จ: ทรุดลงเรื่อยๆ · ครึ่งหลังตัวสั่น · 3 เฟรมท้ายบีบตัวสุดก่อนดีด
		var u := _chg(f)
		var tr := 0.6 * maxf(0.0, u - 0.5) * 2 * (1.0 if F % 2 == 0 else -1.0)
		var sq := 0.05 if F >= CHG - 3 else 0.0
		return {"cx": x_low + tr, "key": "pls_slither_0", "sy": 1.0 - 0.09 * u - sq, "sx": 1.0 + 0.04 * u + sq * 0.6, "lean": -0.04 - 0.05 * u}
	if F < CUT0:   # พุ่งเลื้อยก้าวไขว้ (เร่งออกจากชาร์จ)
		var u := (f - CHG) / (CUT0 - CHG)
		return {"cx": x_low + (x_hit + 4 - x_low) * (1 - pow(1 - u, 1.6)), "key": _glide(f), "lift": 1.5 * absf(sin(PI * f / 3.0)), "sy": 0.94, "lean": -0.08}
	if F < OUT0:   # ดีดตัวปาด: เลื้อย → ดีด → ปาด (โดน) → ค้างปลายปาด
		var q := f - CUT0
		return {"cx": x_hit + 4 - 6 * minf(1.0, q / 2.0), "key": "pls_sh_cut_%d" % mini(3, int(q)), "sy": 0.96, "lean": -0.06}
	# เลื้อยถอยเฉียงออกด้านข้าง: ถอยขวา + ยกไกลจากกล้องนิด (ย่อขนาดลง)
	var u := minf(1.0, (f - OUT0) / (HOLDF - OUT0))
	return {"cx": x_hit - 2 + 24 * (1 - pow(1 - u, 2)), "key": _glide(f), "flip": false, "lift": 3 * u, "sx": 0.97, "sy": 0.94}

func rion_ghosts(f: float, F: int) -> void:
	if F >= LOW + 2 and F < CHG + 2:   # ชาร์จ: ออร่าเงาพองรอบตัว (ร่างเงาขยายใหญ่ เต้นตามจังหวะ)
		var u := _chg(f)
		var pulse := 0.5 + 0.5 * sin(f * 1.3)
		var out := 1.0 if F < CHG else 1 - (f - CHG) / 2.0
		for k in 2:
			var gg := geo(f)
			var sc := 1.05 + 0.05 * u + 0.03 * pulse + k * 0.05
			gg.sx = sc
			gg.sy = sc * gg.get("sy", 1.0)
			ghost(gg, (0.3 + 0.35 * u) * (1.0 - k * 0.45) * out, Color("#1a0f3a"), 1.0, true)
	if F >= CHG and F < HOLDF:   # เงาเข้มต่ำตามหลัง 3 ร่าง (ชื่อท่า)
		for k in [3, 2, 1]:
			ghost(geo(f - k * 1.2), 0.18 * (4 - k), Color("#141833"), 0.8, true)

func frame(f0: float, F0: int, fresh: bool) -> void:
	super.frame(f0, F0, fresh)
	var F := F0
	var u := _chg(f0)
	dim_to(0.55 * u if F < HITF + 4 else maxf(0.0, 0.55 * (1 - (f0 - HITF - 4) / 8.0)), Color("#070816"))
	if F >= LOW + 12 and F < CHG:
		shake(F, 0.5 * u)
	if fresh and F == LOW:
		dust_at(x_low + 6, 1.0, 0.9)
	if fresh and F == CHG:   # ดีดออก
		dust_at(x_low + 8, 1.0, 1.4)
		dust_at(x_low - 4, -1.0, 0.8)
	if fresh and F >= CHG and F < HOLDF and (F - CHG) % 3 == 0 and F != HITF:   # ฝุ่นทุกก้าว
		var g := geo(f0)
		dust_at(g.cx + 4, 1.0 if F < HITF else -1.0, 0.7)
	if fresh and F == HITF:
		burst(Vector2(vis.end.x - 6, G - 16), F, Color("#b8a0ff"))

func fx(n: Node2D, f: float) -> void:
	var F := int(floor(f))
	var g := geo(f)
	var u := _chg(f)
	if F >= LOW and F < CHG + 4:   # ชาร์จ: บ่อเงาใต้เท้า + เส้นเงาไต่เข้าตัว + เงายืดไปหามอน
		var out := 1.0 if F < CHG else 1 - (f - CHG) / 4.0
		var rx := 14 + 30 * u
		for i in range(-int(rx), int(rx) + 1, 2):   # บ่อเงา (วงรีแบน เข้มตรงกลาง)
			var k := 1 - absf(i) / rx
			var hh := 1 + int(3 * k)
			px(n, x_low + i - 2, G - 2 - hh, Color(0.03, 0.02, 0.09, 0.85 * sqrt(k) * out), 2, hh * 2)
			px(n, x_low + i - 2, G - 3 - hh, Color(0.55, 0.38, 1, 0.55 * out * (1 - k * 0.6) * (0.6 + 0.4 * sin(f * 0.9 + i * 0.4))), 2, 1)   # ขอบม่วงสว่างของบ่อเงา
		var reach := (x_low - 14 - (vis.end.x + 4)) * u   # เงายืดไปทางมอน (ยาวขึ้นตามชาร์จ)
		for i in int(reach / 2):
			var x := x_low - 14 - i * 2
			var w := 1.0 + absf(sin(i * 0.7 + f * 0.6))
			px(n, x, G - 3 - (1 if i % 5 == 0 else 0), Color(0.04, 0.03, 0.1, 0.75 * out * (1 - i * 2 / maxf(1.0, reach) * 0.5)), 2, w + 1)
			if i % 3 == 0:
				px(n, x, G - 4 - (1 if i % 5 == 0 else 0), Color(0.55, 0.38, 1, 0.45 * out), 2, 1)   # ประกายม่วงตามขอบเงา
		for k in 12:   # เส้นเงาไต่จากพื้นเข้าตัว (วนเกลียวขึ้น ถี่ขึ้นตามชาร์จ) · หัวเส้น 3 จุด + หาง
			var ph := fmod(f * (0.05 + 0.07 * u) + k / 12.0, 1.0)
			var a := k * 0.9 + ph * 5
			var r := (1 - ph) * (18 + 16 * u)
			var y := G - 3 - ph * 46
			var al := (0.45 + 0.5 * u) * out * sin(PI * ph)
			for j in 4:   # หางไล่ลงตามทางขึ้น
				var a2 := a - j * 0.35
				var r2 := r + j * 2.5
				px(n, x_low - 2 + cos(a2) * r2 - 1, y + j * 3 - 1, Color(0.3, 0.16, 0.6, al * (1 - j * 0.22)), 3 - mini(2, j), 3 - mini(2, j))
			px(n, x_low - 2 + cos(a) * r - 1, y - 1, Color(0.78, 0.66, 1, al * 0.9), 2, 1)
		if F >= CHG - 6 and F < CHG:   # ตาวาบตอนชาร์จเต็ม
			var e := 1 - absf((f - (CHG - 3)) / 3.0)
			px(n, g.cx - 16, G - 58 * (1 - 0.1 * u), Color(0.75, 0.6, 1, e), 3, 1)
			px(n, g.cx - 22, G - 58 * (1 - 0.1 * u), Color(0.75, 0.6, 1, e * 0.6), 6, 1)
	if F >= CHG and F < HOLDF:   # เงาทอดยาวบนพื้นใต้ตัว
		var al := 0.4 if F < OUT0 else 0.4 * (1 - (f - OUT0) / (HOLDF - OUT0))
		for i in 18:
			px(n, g.cx - 14 + i * 2 + 10, G - 1, Color(0.06, 0.07, 0.15, al * (1 - i / 22.0)), 2, 1)
	var d := f - HITF
	if d >= 0 and d < 3:   # รอยปาดต่ำตามมือ (ม่วงเงา)
		slash_line(n, g.cx - 10, G - 30, g.cx - 44, G - 12, 3, minf(1.0, (d + 1) / 1.5), 1 - d / 3.0)
	if d >= 0 and d < 14:   # แผลต่ำระดับเข่าบนมอน
		var kb := mon_kb(f)
		var cx := vis.get_center().x + kb
		var half := vis.size.x * 0.3
		var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 8.0)
		slash_line(n, cx + half, G - 20, cx - half, G - 12, 2, minf(1.0, (d + 1) / 2.0), al)

func snd(F: int) -> void:
	step_snd(F, IDLE, LOW)
	if F == LOW:   # ชาร์จ: เสียงต่ำบวมขึ้นช้าๆ
		play_sfx("sh_charge", [T(1.4, "sine", 45, 95, 0.45, 0, 0.5), N(1.3, "bandpass", 180, 700, 0.25, 1.5, 0, {"attack": 1.0})])
	if F == CHG:   # ดีดออก
		play_sfx("sh_go", [N(0.18, "lowpass", 1200, 200, 0.6, 1.5), T(0.2, "sine", 120, 50, 0.4, 0, 0.003)])
	if F > CHG and F < HOLDF and (F - CHG) % 3 == 0 and (F < CUT0 or F >= OUT0):   # ก้าวเลื้อยเบาๆ ลากเท้า
		play_sfx("sh_step", [N(0.1, "lowpass", 700, 200, 0.28, 1.5)])
	if F == HITF:   # ปาดต่ำ
		play_sfx("sh_cut", [N(0.06, "highpass", 4200, 2400, 0.6, 2), N(0.12, "bandpass", 3600, 2200, 0.25, 10, 0.01)])
		sfx_hit(false)
