extends "res://tests/lab/row_base.gd"
## ปาดข้ามแถว bl14 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: กาลี ก้าวสามเหลี่ยม — อ้อมแนวหน้า ปาดตัวแถวหลัง แล้วย้อนทางเดิมกลับที่)
## ท่าเดี่ยวที่ตีแถวหลังเต็ม: เป้า = ตัวไกลสุดของแถว · ตัวหน้าแค่สะดุ้ง
## ก้าวเฉียง 45° ลงหน้า (เข้าหากล้อง · State BL14_stride ตัวใหญ่ขึ้นนิด) → ก้าวเฉียงขึ้นอ้อมไปหน้าตัวหลัง → ปาดทันทีตอนถึง (ภาพเดิม pls_bl7_3)
## → ย้อนเส้นสามเหลี่ยมกลับ (ภาพก้าวเดิม หันซ้ายตลอด) → ตั้งท่า (ภาพเดิม pls_atk_bl_0)

const L1 := 26      # จบก้าวที่ 1 (ลงหน้า)
const HITF := 34     # จบก้าวที่ 2 = ปาด
const B0 := 38      # เริ่มย้อน
const B1 := 46
const HOMEF := 54
const ENDF := 64
const DEPTH := 14.0   # ก้าวลงหน้าลึกกี่พิกเซล

var x_home := 0.0
var p1 := Vector2.ZERO   # (x, lift) จุดหักสามเหลี่ยม
var p2 := Vector2.ZERO   # จุดปาดหน้าตัวหลัง
var tgt := 0

func mv() -> Dictionary:
	return {"id": "bl14", "slide": 0, "reach": 0, "kb": 6, "shk": 1.6, "sfx": "แฉ่บ!", "what": "ปาดข้ามแถว (bl14)"}

func end_frame() -> int: return ENDF
func stops() -> Array: return [[HITF, 0.07]]
func caption() -> String: return "ก้าวเฉียงลงหน้า → อ้อมแนวหน้า → ปาดตัวแถวหลัง → ย้อนก้าวสามเหลี่ยมกลับ"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 6)
	tgt = cxs.size() - 1
	x_home = start + 60
	p1 = Vector2(cxs[0] + mw * 0.15, -DEPTH)
	p2 = Vector2(cxs[tgt] + mw * 0.42, -4)

func _lerp(a: Vector2, b: Vector2, u: float) -> Vector2:
	var e := u * u * (3 - 2 * u)
	return a + (b - a) * e

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < IDLE:
		return super.geo(f)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_stride_0", "flip": false}
	var h := Vector2(x_home, 0)
	var p := h
	if F < L1:
		p = _lerp(h, p1, (f - IDLE) / (L1 - IDLE))
	elif F < HITF:
		p = _lerp(p1, p2, (f - L1) / (HITF - L1))
	elif F < B0:
		p = p2
		b.key = "pls_bl7_3"
		b.lean = -0.08
		if F - HITF < 2:
			b.sx = 1.05
			b.sy = 0.94
	elif F < B1:
		p = _lerp(p2, p1, (f - B0) / (B1 - B0))
	elif F < HOMEF:
		p = _lerp(p1, h, (f - B1) / (HOMEF - B1))
	else:
		p = h
		b.key = "pls_atk_bl_0" if F < HOMEF + 4 else "pls_idle_bl_%d" % posmod(F / 4, 4)
	b.cx = p.x
	b.lift = p.y
	var near_cam := clampf(-p.y / DEPTH, 0.0, 1.0)   # ใกล้กล้อง = ใหญ่ขึ้นนิด
	b.sx *= 1.0 + 0.06 * near_cam
	b.sy *= 1.0 + 0.06 * near_cam
	if (F >= IDLE and F < HITF) or (F >= B0 and F < HOMEF):   # จังหวะก้าว: ยกย่อ
		b.sy *= 1.0 - 0.03 * absf(sin(PI * (f - IDLE) / 4.0))
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
		else:   # ตัวหน้า: สะดุ้งตอน Rion ก้าวผ่านหน้า
			var pass_f := L1 + 2 + i * 2
			if F >= pass_f and F < pass_f + 6:
				dx = 1.5 * sin(PI * (f - pass_f) / 6.0)
		_show(i, key, dx, amt)
	set_rion(rion, g)
	if (F >= IDLE and F < HITF) or (F >= B0 and F < HOMEF):
		for k in [2, 1]:
			ghost(geo(f - k * 1.3), 0.12 * (3 - k))
	if fresh:
		if ((F >= IDLE and F < HITF) or (F >= B0 and F < HOMEF)) and (F - IDLE) % 4 == 0:
			dust_at(g.cx + 4, 1.0 if F < HITF else -1.0, 0.7)
		if F == HITF:
			debris_at(Vector2(cxs[tgt] + 2, G - 30), "คม", F, 0.8)
			burst(Vector2(cxs[tgt] + mw * 0.25, G - 34), F, Color("#9ae6ff"))
	show_bubble("ปาดข้ามแถว!", g.cx, maxf(14.0, G - g.lift - 74), F - IDLE, (1.0 if F < L1 + 2 else (L1 + 6 - f) / 4.0) if F >= IDLE and F < L1 + 6 else 0.0)
	if d >= 0 and d < 14:
		word(BM.sfx, clampf(cxs[tgt] - 14, 4, W - 60), maxf(14, my + mh - (mh - top0) - 48 - mini(5, d)), Color.WHITE)
	pop(dmg, maxf(16, cxs[tgt] - 8), my + top0 - 6, d, Color.WHITE, "แถวหลัง" + (" · " + aff_tag() if aff_tag() != "" else ""), Color("#ffe08a"))

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	# เส้นทางสามเหลี่ยมจางๆ บนพื้น (เห็นทางอ้อม)
	if F >= IDLE and F < HOMEF + 4:
		var al := 0.3 if F < HOMEF else 0.3 * (1 - (f - HOMEF) / 4.0)
		var pts := [Vector2(x_home, 0), p1, p2]
		for s in 2:
			var a: Vector2 = pts[s]
			var b: Vector2 = pts[s + 1]
			for k in 24:
				var u := k / 23.0
				if k % 3 == 0:
					px(n, a.x + (b.x - a.x) * u, G - (a.y + (b.y - a.y) * u) - 1, Color(0.85, 0.92, 1, al), 2, 1)
	var d := f - HITF
	if d >= 0 and d < 3:   # รอยปาดตามมือ
		slash_line(n, g.cx - 8, G + 4 - 46, g.cx - 40, G + 4 - 24, 3, minf(1.0, (d + 1) / 1.5), 1 - d / 3.0)
	if d >= 0 and d < 14:   # แผลบนตัวหลัง
		var cx: float = cxs[tgt] - BM.kb * minf(1.0, d / 4.0)
		var half := mw * 0.22
		var cy := my + mh * 0.5
		var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 8.0)
		slash_line(n, cx + half, cy - 6, cx - half, cy + 6, 3, minf(1.0, (d + 1) / 2.0), al)
	if g.lift < -1:   # เงาใต้เท้าเมื่อก้าวลงหน้า
		for i in range(-8, 9):
			px(n, g.cx + i * 1.6, G - g.lift - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.35), 2, 1)

func sounds(F: int) -> void:
	if F < IDLE:
		super.sounds(F)
		return
	if ((F >= IDLE and F < HITF) or (F >= B0 and F < HOMEF)) and (F - IDLE) % 4 == 0:
		play_sfx("tr_step", [N(0.07, "lowpass", 900, 220, 0.4, 1)])
	if F == HITF:
		play_sfx("tr_cut", [N(0.07, "highpass", 4200, 2200, 0.65, 2), N(0.14, "bandpass", 3600, 2200, 0.3, 10, 0.01)])
		sfx_hit(false)
		sfx_mon(true, 0.6 if foe == "B1" else 1.0)
	if F == HOMEF:
		play_sfx("tr_set", [T(0.06, "triangle", 900, 700, 0.1)])
