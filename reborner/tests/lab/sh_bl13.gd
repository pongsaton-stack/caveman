extends "res://tests/lab/fl_base.gd"
## ก้าวเงา bl13 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: ปันจักสีลัต ย่างก้าวลังกา — ก้าวไขว้ต่ำเลื้อยเฉียงเข้า ปาดสั้น ก้าวไขว้ถอยออกด้านข้าง)
## วิ่งออกตัวสั้น → ทรุดต่ำเลื้อยก้าวไขว้เข้า (State BL13_slither · โค้ดยกย่อทีละก้าว + เงาเข้มทอดตามพื้น)
## → ถึงตัวปาดสั้นระดับเข่าทันที (ภาพเดิม pls_bl7_3) → เลื้อยถอยเฉียงออกด้านข้าง (ภาพเดิมของท่านี้ · ไม่ถอยตรง) → กระโดดถอย

const LOW := 22     # ทรุดต่ำเริ่มเลื้อย
const HITF := 34
const OUT0 := 38    # เริ่มถอยเลื้อย
const HOLDF := 46

var x_low := 0.0
var x_hit := 0.0

func mv() -> Dictionary:
	return {"id": "bl13", "slide": 0, "reach": 0, "kb": 3, "shk": 1.2, "sfx": "แฉ่บ!", "what": "ก้าวเงา (bl13)"}

func caption() -> String: return "ออกตัว → ทรุดต่ำก้าวไขว้เลื้อยเข้า → ปาดสั้นระดับเข่า → เลื้อยถอยเฉียงออก → กระโดดถอย"

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	hit_f.append(float(HITF))
	x_hit = vis.end.x + 26
	x_low = x_home - 30
	set_end(x_hit + 22)
	bubble_name = "ก้าวเงา"
	bubble_at = Vector2(LOW - 2, HITF)

## ยก/ย่อทีละก้าวไขว้ (ก้าวละ 4 เฟรม)
func _gait(f: float, a: float) -> float:
	return absf(sin(PI * (f - a) / 4.0))

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < LOW:   # ออกตัวสั้น
		return {"cx": x_home + (x_low - x_home) * ((f - IDLE) / (LOW - IDLE)), "lean": -0.05, "key": "pls_run_bl_%d" % ((F - IDLE) % 6)}
	if F < HITF:   # เลื้อยก้าวไขว้เข้า (ช้าแล้วเร่ง) · ตัวต่ำลงเรื่อยๆ
		var u := (f - LOW) / (HITF - LOW)
		var s := _gait(f, LOW)
		return {"cx": x_low + (x_hit - x_low) * (u * u * 0.6 + u * 0.4), "key": "pls_slither_0", "lift": s * 2.0,
			"sy": 1.0 - 0.06 * u - 0.03 * (1 - s), "sx": 1.0 + 0.03 * (1 - s), "lean": -0.05 - 0.04 * s}
	if F < OUT0:   # ปาดสั้นจังหวะเดียว (ระดับเข่า)
		var q := f - HITF
		return {"cx": x_hit - 2 * minf(1.0, q / 2.0), "key": "pls_bl7_3", "sy": 0.9, "sx": 1.04, "lean": -0.08}
	# เลื้อยถอยเฉียงออกด้านข้าง: ถอยขวา + ยกไกลจากกล้องนิด (ย่อขนาดลง)
	var u := minf(1.0, (f - OUT0) / (HOLDF - OUT0))
	var s := _gait(f, OUT0)
	return {"cx": x_hit - 2 + 24 * (1 - pow(1 - u, 2)), "key": "pls_slither_0", "lift": 3 * u + s * 1.5, "sx": 0.97, "sy": 0.95 - 0.02 * (1 - s)}

func rion_ghosts(f: float, F: int) -> void:
	if F >= LOW and F < HOLDF:   # เงาเข้มต่ำตามหลัง 3 ร่าง (ชื่อท่า)
		for k in [3, 2, 1]:
			ghost(geo(f - k * 1.2), 0.16 * (4 - k), Color("#141833"), 0.8, true)

func frame(f0: float, F0: int, fresh: bool) -> void:
	super.frame(f0, F0, fresh)
	var F := F0
	if fresh and F >= LOW and F < HOLDF and (F - LOW) % 4 == 0:   # ฝุ่นทุกก้าว
		var g := geo(f0)
		dust_at(g.cx + 4, 1.0 if F < HITF else -1.0, 0.7)
	if fresh and F == HITF:
		burst(Vector2(vis.end.x - 6, G - 16), F, Color("#9ae6ff"))

func fx(n: Node2D, f: float) -> void:
	var F := int(floor(f))
	var g := geo(f)
	if F >= LOW and F < HOLDF:   # เงาทอดยาวบนพื้นใต้ตัว
		var al := 0.35 if F < OUT0 else 0.35 * (1 - (f - OUT0) / (HOLDF - OUT0))
		for i in 18:
			px(n, g.cx - 14 + i * 2 + 10, G - 1, Color(0.06, 0.07, 0.15, al * (1 - i / 22.0)), 2, 1)
	var d := f - HITF
	if d >= 0 and d < 3:   # รอยปาดสั้นตามมือ
		slash_line(n, g.cx - 10, G - 30, g.cx - 40, G - 14, 3, minf(1.0, (d + 1) / 1.5), 1 - d / 3.0)
	if d >= 0 and d < 14:   # แผลต่ำระดับเข่าบนมอน
		var kb := mon_kb(f)
		var cx := vis.get_center().x + kb
		var half := vis.size.x * 0.3
		var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 8.0)
		slash_line(n, cx + half, G - 20, cx - half, G - 12, 2, minf(1.0, (d + 1) / 2.0), al)

func snd(F: int) -> void:
	step_snd(F, IDLE, LOW)
	if F >= LOW and F < HOLDF and (F - LOW) % 4 == 0 and (F < HITF or F >= OUT0):   # ก้าวเลื้อยเบาๆ ลากเท้า
		play_sfx("sh_step", [N(0.1, "lowpass", 700, 200, 0.28, 1.5)])
	if F == HITF:   # ปาดสั้น ไม่ตูม
		play_sfx("sh_cut", [N(0.06, "highpass", 4200, 2400, 0.6, 2), N(0.12, "bandpass", 3600, 2200, 0.25, 10, 0.01)])
		sfx_hit(false)
