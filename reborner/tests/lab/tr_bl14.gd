extends "res://tests/lab/row_base.gd"
## ปาดข้ามแถว bl14 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: กาลี ก้าวสามเหลี่ยม — ตัวแถวหลังโดนเต็ม)
## รอบ 2 (kwan 28 ต.ค. "ปาดข้ามแถว กระโดดไปแถวหลังเลย" · "ท่าดูไม่ลื่น เจนเพิ่มให้ไหลลื่นได้"):
## วิ่งสั้น → ย่อถีบ → กระโดดสูงข้ามตัวหน้า (State BL14_air ลอยง้างมีด · ท่ากลาง bl14_leap ช่วงลงฟัน) → ลงแถวหลังข้างตัวเป้า ฟันลงทันทีตอนแตะพื้น
## (ยืนระดับแถวหลัง: ยกขึ้น BACK · ตัวเล็กลงนิด · วาดหลังตัวหน้า = อยู่ในดงจริง) → กระโดดถอยข้ามตัวหน้ากลับที่
## เป้า = ตัวแถวหลัง (ตัวกลางของแถว 3 ตัว) · บอสตัวเดียว = กระโดดฟันลงหน้าบอส · ตัวหน้าแค่สะดุ้งตอนถูกข้ามหัว

const JUMP := 24     # ถีบตัว
const HITF := 35     # แตะพื้นแถวหลัง = ฟัน
const B0 := 42       # เริ่มกระโดดกลับ
const HOMEF := 54
const ENDF := 66

var x_home := 0.0
var x_jump := 0.0
var x_land := 0.0
var back := 0.0      # ยกขึ้นระดับแถวหลัง
var tgt := 0

func mv() -> Dictionary:
	return {"id": "bl14", "slide": 0, "reach": 0, "kb": 6, "shk": 1.8, "sfx": "แฉ่บ!", "what": "ปาดข้ามแถว (bl14)"}

func end_frame() -> int: return ENDF
func stops() -> Array: return [[HITF, 0.08]]
func caption() -> String: return "วิ่ง → กระโดดข้ามแนวหน้า → ลงแถวหลังฟันทันที → กระโดดกลับข้ามแนวหน้า"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 6)
	tgt = 1 if cxs.size() == 3 else 0
	back = dep[tgt]
	x_home = start + 60
	x_jump = cxs[0] + mw * 0.5 + 34
	x_land = cxs[tgt] + mw * 0.42
	if cxs.size() == 3:   # Rion อยู่หลังตัวหน้า แต่หน้าตัวแถวหลัง (ลำดับวาดตอน z เท่ากัน)
		move_child(rion, mons[1].get_index() + 1)

func _in_row(F: int) -> bool:
	return cxs.size() == 3 and F >= HITF - 2 and F < B0 + 3

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < IDLE:
		return super.geo(f)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false}
	var hi := 46.0 if cxs.size() == 3 else 26.0
	if F < JUMP:   # วิ่งสั้นถึงจุดถีบ
		var u := (f - IDLE) / (JUMP - IDLE)
		b.cx = x_home + (x_jump - x_home) * (u * u * 0.5 + u * 0.5)
		b.key = "pls_run_bl_%d" % ((F - IDLE) % 6)
		b.lean = -0.06
	elif F < HITF:   # ย่อ → ถีบ → ลอยข้ามหัวตัวหน้า → ลง
		var u := (f - JUMP) / (HITF - JUMP)
		b.cx = x_jump + (x_land - x_jump) * u
		b.lift = hi * sin(PI * u) + back * u
		b.key = "pls_hop_bl_1" if u < 0.1 else ("pls_lair_0" if u < 0.7 else ("pls_leap_4" if u < 0.9 else "pls_leap_5"))
		var s := 1.0 - 0.06 * u * (back / maxf(1.0, BACK))
		b.sx = s
		b.sy = s
	elif F < B0:   # ฟันลงตอนแตะพื้นแถวหลัง → ย่อรับ → ลุก
		var q := f - HITF
		b.cx = x_land - 3 * minf(1.0, q / 2.0)
		b.lift = back
		b.key = "pls_leap_5" if q < 2 else ("pls_leap_6" if q < 5 else "pls_leap_7")
		var s := 1.0 - 0.06 * (back / maxf(1.0, BACK))
		b.sx = s * (1.04 if q < 2 else 1.0)
		b.sy = s * (0.94 if q < 2 else 1.0)
	elif F < HOMEF:   # กระโดดถอยข้ามตัวหน้ากลับ (หันซ้ายตลอด)
		var u := (f - B0) / (HOMEF - B0)
		b.cx = x_land - 3 + (x_home - x_land + 3) * (1 - pow(1 - u, 1.4))
		b.lift = hi * 0.85 * sin(PI * u) + back * (1 - u)
		b.key = "pls_hop_bl_%d" % [1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 1][mini(11, F - B0)]
	else:
		b.key = "pls_hop_bl_1" if F < HOMEF + 2 else ("pls_atk_bl_0" if F < HOMEF + 6 else "pls_idle_bl_%d" % posmod(F / 4, 4))
		if F < HOMEF + 2:
			b.sy = 0.94
	return b

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var d := F - HITF
	shake(F, BM.shk * (1 - d / 4.0) if d >= 0 and d < 4 else 0.0)
	var g := geo(f)
	for i in mons.size():
		var dx := 0.0
		var key := idle_key(f + i * 3)
		var amt := 0.0
		if i == tgt:
			if d >= 0 and d < 12:
				key = hurt_key()
				dx = -BM.kb * ((1 - pow(1 - d / 4.0, 2)) if d < 4 else maxf(0.0, 1 - (d - 4) / 8.0))
			if d == 0:
				amt = 0.25 if foe.begins_with("B") else 0.6
		else:   # ตัวหน้า: ก้มหลบตอนถูกข้ามหัว (ขาไปและขากลับ)
			for pass_f in [JUMP + 4, B0 + 3]:
				if F >= pass_f and F < pass_f + 6:
					dx = 2.0 * sin(PI * (f - pass_f) / 6.0) * (1.0 if i == 0 else -1.0)
					key = hurt_key()
		_show(i, key, dx, amt)
	rion.z_index = 1 if _in_row(F) else 4   # อยู่ในดง: ตัวหน้าบังขา
	set_rion(rion, g)
	if (F >= JUMP and F < HITF) or (F >= B0 and F < HOMEF):   # ร่างติดตาตอนลอย
		for k in [2, 1]:
			ghost(geo(f - k * 1.3), 0.13 * (3 - k))
	if fresh:
		if F >= IDLE and F < JUMP and (F - IDLE) % 3 == 0:
			dust_at(g.cx + 4, 1.0, 0.6)
		if F == JUMP or F == B0:
			dust_at(g.cx + (6 if F == JUMP else -4), 1.0 if F == JUMP else -1.0, 1.1)
		if F == HITF:
			debris_at(Vector2(cxs[tgt] + 2, gy(tgt) - 30), "คม", F, 0.8)
			burst(Vector2(cxs[tgt] + mw * 0.25, gy(tgt) - 34), F, Color("#9ae6ff"))
			dust_at(x_land, 1.0, 1.2)
			dust_at(x_land, -1.0, 1.0)
		if F == HOMEF:
			dust_at(x_home, 1.0, 1.0)
	show_bubble("ปาดข้ามแถว!", g.cx, maxf(14.0, G - g.lift - 74), F - IDLE, (1.0 if F < JUMP + 4 else (JUMP + 8 - f) / 4.0) if F >= IDLE and F < JUMP + 8 else 0.0)
	if d >= 0 and d < 14:
		word(BM.sfx, clampf(cxs[tgt] - 60, 4, W - 60), maxf(14, my + top0 - 30 - back - mini(5, d)), Color.WHITE)   # ซ้ายของตัวเลข
	pop(dmg, maxf(16, cxs[tgt] - 4), maxf(26.0, my + top0 - 10 - back), d, Color.WHITE, "แถวหลัง" + (" · " + aff_tag() if aff_tag() != "" else ""), Color("#ffe08a"))

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	if g.lift > 4:   # เงาบนพื้นตอนลอย (เงาอยู่ระดับพื้นตามแนวกระโดด)
		var gyy := G - (back if (F >= HITF - 3 and F < B0 + 3) else 0.0) - 1
		for i in range(-8, 9):
			if absi(i) < 8 * maxf(0.35, 1 - g.lift / 60.0):
				px(n, g.cx + i * 1.6, gyy, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.35), 2, 1)
	var d := f - HITF
	if d >= 0 and d < 3:   # รอยปาดตามมือ
		slash_line(n, g.cx - 6, G - back - 58, g.cx - 36, G - back - 14, 3, minf(1.0, (d + 1) / 1.5), 1 - d / 3.0)   # ฟันลงเฉียงจากกลางอากาศ
	if d >= 0 and d < 14:   # แผลบนตัวหลัง
		var cx: float = cxs[tgt] - BM.kb * minf(1.0, d / 4.0)
		var half := mw * 0.22
		var cy := my + mh * 0.5 - back
		var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 8.0)
		slash_line(n, cx + half, cy - 6, cx - half, cy + 6, 3, minf(1.0, (d + 1) / 2.0), al)

func sounds(F: int) -> void:
	if F < IDLE:
		super.sounds(F)
		return
	if F >= IDLE and F < JUMP and (F - IDLE) % 3 == 0:
		play_sfx("tr_step", [N(0.07, "lowpass", 900, 220, 0.4, 1)])
	if F == JUMP or F == B0:   # ถีบตัว
		play_sfx("tr_jump", [N(0.22, "bandpass", 300, 1000, 0.4, 2), T(0.2, "sine", 150, 330, 0.25, 0, 0.004)])
	if F == HITF:
		play_sfx("tr_cut", [N(0.07, "highpass", 4200, 2200, 0.65, 2), N(0.14, "bandpass", 3600, 2200, 0.3, 10, 0.01)])
		sfx_hit(false)
		sfx_mon(true, 0.6 if foe == "B1" else 1.0)
	if F == HOMEF:
		play_sfx("tr_set", [T(0.06, "triangle", 900, 700, 0.1)])
