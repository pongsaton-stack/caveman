extends "res://tests/lab/row_base.gd"
## มีดบินวกกลับ bl11 (kwan 27 ต.ค. "ต่อด้วย bl10 bl11 · ขอดูฝีมือ") — ตามรายงานวิจัยท่า R2 (จักรซิกข์ + ตำนานสุทรรศนจักร = วกกลับ)
## ยกมือปั่นมีดบนปลายนิ้ว (tajani · วงหมุนเร่ง + ประกายขอบถี่ขึ้น) → นิ่งแขวน 1 เฟรม → สะบัดปล่อย
## → มีดหมุนระนาบเดิมบินตัดผ่านแถว (โดนขาไป ตัวหน้า→หลัง) → ปลายทางเอียงระนาบวกกลับ → ขากลับช้าลง 15% โดนอีกรอบ (ตัวหลัง→หน้า) → รับคืนที่มือ
## กฎของท่า: Rion ไม่ขยับจากที่ · ไม่หยุดภาพ · ไม่สั่นจอ · ไม่มีดาว/วาบตัวเป้า · เลขรอบสองต่ำกว่ารอบแรก
## ภาพ Rion ประกอบจากภาพที่มีอยู่: ชูมือ pls_bl9_2–4 · ขว้าง/รอรับมือเปล่า pls_nk_atk_bl_5 + pls_nk_idle_bl · รับแล้ว pls_atk_bl_6–7

const RAISE := 18
const SPIN0 := 22
const HANG := 32
const OUT0 := 33     # ปล่อย
const OUT1 := 47     # ถึงปลายทาง
const TURN1 := 53    # วกกลับเสร็จ
const BACK1 := 69    # รับคืน
const END11 := 86

var x_home := 0.0
var x_far := 0.0
var hits_out: Array[int] = []
var hits_back: Array[int] = []

func mv() -> Dictionary:
	return {"id": "bl11", "slide": 0, "reach": 0, "kb": 0, "shk": 0.0, "sfx": "ฟิ้ว—", "what": "มีดบินวกกลับ (bl11)"}

func end_frame() -> int: return END11
func stops() -> Array: return []
func caption() -> String: return "ยืนในศึก → ปั่นมีดบนนิ้ว → ขว้างตัดผ่านแถว → วกกลับ โดนอีกรอบ → รับคืน"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 24)   # เว้นที่ซ้ายให้มีดวกกลับในจอ
	x_home = start + 60
	x_far = maxf(10.0, cxs[cxs.size() - 1] - mw * 0.5 - 8)
	hits_out.clear()
	hits_back.clear()
	for c in cxs:
		hits_out.append(_cross(c, OUT0 + 2, OUT1, _rel().x, x_far))
		hits_back.append(_cross(c, TURN1, BACK1, x_far, _catch().x))

func _cross(c: float, f0: int, f1: int, xa: float, xb: float) -> int:
	return f0 + int(round(clampf((c - xa) / (xb - xa), 0.0, 1.0) * (f1 - f0)))

func _hand() -> Vector2:   # ปลายนิ้วที่ชูขึ้น (ภาพ pls_bl9_3: ปลายมีดผืน 81,33)
	return Vector2(x_home + 20, G - 78)

func _rel() -> Vector2:   # จุดปล่อยหน้าตัว
	return Vector2(x_home - 34, G - 40)

func _catch() -> Vector2:   # มือที่ยื่นรับ (pls_nk_atk_bl_5)
	return Vector2(x_home - 26, G - 36)

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "flip": false}
	if F < RAISE:
		b.sy = 1 - 0.015 * posmod(F / 4, 2)
	elif F < SPIN0:
		b.key = "pls_bl9_2"
	elif F <= HANG:
		b.key = "pls_bl9_3" if posmod(F, 6) < 3 else "pls_bl9_4"
	elif F < OUT0 + 7:   # สะบัดข้อมือส่งไปข้างหน้า ตัวตามแรงเล็กน้อย
		b.key = "pls_nk_atk_bl_5"
		b.lean = -0.08 * maxf(0.0, 1 - (f - OUT0) / 7.0)
		b.cx = x_home - 3 * minf(1.0, (f - OUT0) / 3.0)
	elif F < BACK1 - 4:   # มือเปล่ารอมีดกลับ
		b.key = "pls_nk_idle_bl_%d" % posmod(F / 4, 4)
		b.cx = x_home - 3
	elif F < BACK1:   # ยื่นมือรับ
		b.key = "pls_nk_atk_bl_5"
		b.cx = x_home - 3
	elif F < BACK1 + 6:
		b.key = "pls_atk_bl_6" if F < BACK1 + 3 else "pls_atk_bl_7"
		b.cx = x_home - 3 + minf(3.0, (f - BACK1))
	return b

## ตำแหน่งมีด · ry = ความหนาของวงรีระนาบหมุน (เอียงตอนวก) · on = มีดลอยอยู่ไหม
func _disc(f: float) -> Dictionary:
	if f < SPIN0 or f >= BACK1:
		return {"on": false}
	if f < OUT0:   # บนปลายนิ้ว
		return {"on": true, "p": _hand(), "rx": 4.0 + 3.0 * (f - SPIN0) / (OUT0 - SPIN0), "ry": 2.0}
	if f < OUT0 + 2:   # ปล่อย: จากเหนือหัวลงมาหน้าตัว
		var u := (f - OUT0) / 2.0
		return {"on": true, "p": _hand().lerp(_rel(), u), "rx": 7.0, "ry": 2.6}
	if f < OUT1:   # ขาไป: ระนาบนิ่ง เส้นตรงระดับเอว ค่อยๆ ลดระดับ
		var u := (f - OUT0 - 2) / (OUT1 - OUT0 - 2)
		return {"on": true, "p": Vector2(lerpf(_rel().x, x_far, u), lerpf(_rel().y, G - 26, u)), "rx": 7.0, "ry": 2.6}
	if f < TURN1:   # วกกลับ: โค้งครึ่งวงด้านซ้าย ล่าง→บน · ระนาบเอียงชัดขึ้น
		var u := (f - OUT1) / (TURN1 - OUT1)
		var a := PI / 2 + PI * u
		return {"on": true, "p": Vector2(x_far + 4, G - 36) + Vector2(cos(a) * 10, sin(a) * 10), "rx": 7.0, "ry": 2.6 + 3.0 * sin(PI * u)}
	var u := (f - TURN1) / (BACK1 - TURN1)   # ขากลับ: สูงกว่าเล็กน้อย ช้าลง (เสียพลังงานไปกับการตัด)
	return {"on": true, "p": Vector2(lerpf(x_far + 4, _catch().x, u), lerpf(G - 46, _catch().y, u * u)), "rx": 7.0, "ry": 2.6 + 1.0 * (1 - u)}

func _jolt(d: int, dir: float) -> float:   # เซเล็กน้อยตามทิศมีด
	if d < 0 or d > 8:
		return 0.0
	return dir * 3.0 * (1 - d / 8.0)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	cam.offset = Vector2.ZERO
	var g := geo(f)
	for i in mons.size():
		var d1 := F - hits_out[i]
		var d2 := F - hits_back[i]
		var hurt := (d1 >= 0 and d1 < 8) or (d2 >= 0 and d2 < 8)
		_show(i, hurt_key() if hurt else idle_key(f + i * 3), _jolt(d1, -1.0) + _jolt(d2, 1.0), 0.0)
	set_rion(rion, g)
	if fresh:
		for i in mons.size():
			if F == hits_out[i]:
				debris_at(Vector2(cxs[i] - 4, G - 26), "คม", F, 0.45)
			if F == hits_back[i]:
				debris_at(Vector2(cxs[i] + 4, G - 40), "คม", F, 0.35)
	var b0 := SPIN0
	show_bubble("มีดบินวกกลับ!", g.cx, G - 86, F - b0, (1.0 if F < OUT0 + 4 else (OUT0 + 8 - f) / 4.0) if F >= b0 and F < OUT0 + 8 else 0.0)
	for i in mons.size():   # ตัวเลขสองครั้งต่อตัว · รอบสองต่ำกว่า
		var d1 := F - hits_out[i]
		var d2 := F - hits_back[i]
		pop(dmg, maxf(16, cxs[i]), my + roundf(mh * 0.25) - (i % 2) * 14, d1, Color.WHITE, aff_tag(), aff_col())
		pop(dmg, maxf(16, cxs[i] + 6), my + roundf(mh * 0.25) + 14 - (i % 2) * 14, d2, Color("#e8f0ff"), "", Color.WHITE)

## วาดมีดหมุน: แผ่นวงรีเหล็ก ขอบเข้ม · ประกายขอบวิ่งรอบตามรอบหมุน · rate = รอบต่อเฟรม
func _draw_disc(n: Node2D, p: Vector2, rx: float, ry: float, f: float, rate: float, al := 1.0) -> void:
	var O := Color(42 / 255.0, 26 / 255.0, 20 / 255.0, al)
	for k in 24:
		var a := TAU * k / 24
		px(n, p.x + cos(a) * (rx + 1), p.y + sin(a) * (ry + 1), O)
	for k in 24:
		var a := TAU * k / 24
		px(n, p.x + cos(a) * rx * 0.6, p.y + sin(a) * ry * 0.6, Color(0.78, 0.84, 0.9, al))
		px(n, p.x + cos(a) * rx, p.y + sin(a) * ry, Color(0.9, 0.95, 1, al))
	for k in 24:   # เนื้อแผ่นทึบ (มองเห็นจากระยะ)
		var a := TAU * k / 24
		px(n, p.x + cos(a) * rx * 0.3, p.y + sin(a) * ry * 0.3, Color(0.62, 0.68, 0.78, al))
	px(n, p.x - 1, p.y - 1, Color(0.4, 0.44, 0.52, al), 2, 2)
	var ga := TAU * f * rate   # ประกายขอบ (วาบตอนคมผ่านมุมรับแสง)
	px(n, p.x + cos(ga) * rx - 1, p.y + sin(ga) * ry - 1, Color(1, 1, 1, al), 2, 2)
	if fposmod(ga, TAU) < 0.9:
		star_px(n, p.x + cos(ga) * rx, p.y + sin(ga) * ry, 3, Color(1, 1, 1, 0.8 * al), Color(0.6, 0.9, 1, 0.5 * al))

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var ds := _disc(f)
	if ds.get("on", false):
		var spinning := f < OUT0
		if spinning:   # เกลียวฝุ่นดูดเข้ารอบมือ
			var u := (f - SPIN0) / (OUT0 - SPIN0)
			for k in 8:
				var a := TAU * (k / 8.0 + u * 2.5)
				var r := 16 * (1 - fposmod(u * 3 + k / 8.0, 1.0))
				px(n, ds.p.x + cos(a) * r, ds.p.y + 4 + sin(a) * r * 0.5, Color(0.85, 0.8, 0.72, 0.6), 1, 1)
		else:   # เส้นลมบางในระนาบวง (ไม่ใช่เส้นพลังงาน) + ร่างติดตาวงจาง 2 แผ่น
			for k in range(1, 9):
				var q := _disc(f - k * 0.6)
				if q.get("on", false):   # เส้นลมสองเส้นบน-ล่างของระนาบวง
					px(n, q.p.x, q.p.y - q.ry, Color(0.9, 0.96, 1, 0.55 * (1 - k / 9.0)), 3, 1)
					px(n, q.p.x, q.p.y + q.ry, Color(0.9, 0.96, 1, 0.4 * (1 - k / 9.0)), 3, 1)
			for k in [2, 1]:
				var q := _disc(f - k * 1.2)
				if q.get("on", false) and f - OUT0 < 6:
					_draw_disc(n, q.p, q.rx, q.ry, f, 1.2, 0.25 * (3 - k))
		var rate := 0.3 + 1.2 * clampf((f - SPIN0) / (OUT0 - SPIN0), 0.0, 1.0) if spinning else (1.2 if f < TURN1 else 1.0)
		_draw_disc(n, ds.p, ds.rx, ds.ry, f, rate)
	# แผลสั้นแนวนอน · รอบสองเล็กและสูงกว่า
	for i in mons.size():
		for r in 2:
			var d := F - (hits_out[i] if r == 0 else hits_back[i])
			if d >= 0 and d < 10:
				var al := 1.0 if d < 5 else maxf(0.0, 1 - (d - 5) / 5.0)
				var y := G - 26 if r == 0 else G - 40
				var hw := 9.0 if r == 0 else 6.0
				slash_line(n, cxs[i] + hw, y - 1, cxs[i] - hw, y + 1, 2, minf(1.0, (d + 1) / 2.0), al)
	if F >= BACK1 and F < BACK1 + 4:   # ประกายรับคืน
		var c := _catch()
		star_px(n, c.x, c.y, 3 + (F - BACK1) * 2, Color(1, 1, 1, 0.9), Color(0.6, 0.9, 1, 0.6))

func sounds(F: int) -> void:
	if F == SPIN0 or F == SPIN0 + 1:   # นิ้วประคองวง
		play_sfx("tb_tick", [T(0.03, "square", 2600, 2600, 0.05, 0, 0.002, {"lp": 5000})])
	if F == SPIN0 + 1:   # หวีดปั่นไต่ระดับ 300 → 900 Hz พัลส์เร่ง (นับถอยหลังก่อนปล่อย)
		play_sfx("tb_spin", [T(0.62, "sine", 300, 900, 0.2, 0, 0.12, {"fm": 18, "fmDepth": 140}), N(0.6, "bandpass", 600, 1800, 0.18, 4, 0, {"attack": 0.4})])
	if F == OUT0:   # สะบัด "เฟี้ยว" → เสียงบินเต็มตัว ต่อกันสนิท
		play_sfx("tb_flick", [N(0.05, "highpass", 5000, 9000, 0.6, 4), N(0.85, "bandpass", 1900, 1300, 0.42, 6, 0.03, {"attack": 0.05}), T(0.85, "sine", 900, 760, 0.07, 0.03)])
	if F == TURN1 - 2:   # ขากลับ: ต่ำลงและเบาลง (พลังงานหายไปกับการตัด)
		play_sfx("tb_back", [N(1.0, "bandpass", 1500, 1000, 0.32, 6, 0, {"attack": 0.1}), T(1.0, "sine", 700, 560, 0.05)])
	for i in mons.size():
		if F == hits_out[i]:
			play_sfx("tb_cut%d" % i, [N(0.06, "highpass", 4500 - i * 300, 2500, 0.5 - i * 0.08, 3)])
			sfx_mon(false, 0.6 if foe == "B1" else 1.0)
		if F == hits_back[i]:
			play_sfx("tb_cutb%d" % i, [N(0.06, "highpass", 3600 - i * 200, 2000, 0.38, 3)])
			sfx_mon(false, (0.6 if foe == "B1" else 1.0) * 0.95)
	if F == BACK1:   # รับคืน: กระทบด้ามเบาๆ
		play_sfx("tb_catch", [T(0.05, "square", 2200, 1800, 0.12, 0, 0.002, {"lp": 5000}), N(0.04, "highpass", 3000, 5000, 0.3, 2)])
