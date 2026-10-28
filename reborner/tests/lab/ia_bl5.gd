extends "res://tests/lab/fl_base.gd"
## ปาดไว bl5 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: ไออิโด ชักฟันจังหวะเดียว jo-ha-kyu)
## วิ่งเข้า → ไถลลงท่าย่อ iaigoshi มือแตะด้ามในซอง (State BL5_iai_crouch) → ความเงียบ 6 เฟรม (โลกหยุด จอมืดลง · ข้อยกเว้นท่าตั้งใจค้างแบบจิเง็นริว)
## → ชักฟันพุ่งแว้บเดียว 2 เฟรม ปลายจังหวะ (State BL5_iai_cut) โดนตอนถึงตัว · เส้นคมขาวยาวพาดจอ
## → สะบัดคม chiburi (โค้ดหมุน −25°) → เก็บเข้าซองช้าๆ noto (ภาพย่อ) → "แกร๊ก" แผลวาบซ้ำ → zanshin → กระโดดถอยแบบท่าฟัน
## ทีม: อย่าเจนท่ากลางจังหวะชัก (PixelLab พัง) → เจนท่าปลายจังหวะแล้วเร่งด้วยโค้ด/ร่างติดตา
## รอบ 2 (kwan 28 ต.ค. "ท่าดูไม่ลื่นเลย เจนเพิ่มให้ไหลลื่นได้"): ท่ากลางแบบสองภาพหัวท้าย (ไม่ใช่สั่งท่าชักลอยๆ) ผ่าน →
## ชัก = pls_iai_draw_1–5 (ย่อ → ปลายจังหวะ 6 ภาพ) · สะบัด + เก็บเข้าซอง = pls_iai_noto_1–5 (ปลายจังหวะ → ย่อ) แทนการหมุนภาพเดียว

const CR := 26      # ถึงจุดย่อ เริ่มไถลในท่าย่อ
const STILL := 30   # นิ่งสนิท
const DRAW := 36    # ชัก
const HITF := 39     # ถึงตัว = โดน
const CHIB := 43    # สะบัดคม
const NOTO := 45    # เก็บคม
const CLICK := 51   # คมเข้าซอง
const HOLDF := 57

var x_cr := 0.0
var x_hit := 0.0
var cut_y := 0.0

func mv() -> Dictionary:
	return {"id": "bl5", "slide": 0, "reach": 0, "kb": 4, "shk": 2.0, "sfx": "ฉั่บ!", "what": "ปาดไว (bl5)"}

func caption() -> String: return "วิ่ง → ไถลลงท่าย่อ มือแตะด้าม → เงียบ → ชักฟันแว้บเดียว → สะบัดคม เก็บเข้าซอง แกร๊ก → กระโดดถอย"

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	hit_f.append(float(HITF))
	var edge := vis.end.x   # ขอบหน้าตัวมอนจริง
	x_cr = edge + 64
	x_hit = edge + 30   # ปลายมีดของภาพชักฟันอยู่ ~46 px ซ้ายกลางตัว → จมเข้าตัวมอน ~16 px
	cut_y = blade_y(48)
	set_end(x_hit + 6)
	bubble_name = "ปาดไว"
	bubble_at = Vector2(CR - 2, DRAW)

func freeze(f: float) -> bool: return f >= STILL and f < DRAW + 1

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < CR:   # วิ่งเข้า · 3 เฟรมท้ายเริ่มลดตัว
		return {"cx": run_x(f, IDLE, CR, x_cr + 6), "lean": -0.06, "key": "pls_run_bl_%d" % ((F - IDLE) % 6)}
	if F < STILL:   # ไถลลงท่าย่อ
		var u := (f - CR) / (STILL - CR)
		return {"cx": x_cr + 6 - 6 * (1 - pow(1 - u, 2)), "key": "pls_iai_crouch_0", "sy": 0.96 + 0.04 * u}
	if F < DRAW:   # นิ่งสนิท
		return {"cx": x_cr, "key": "pls_iai_crouch_0"}
	if F < HITF:   # ชักพุ่งแว้บ 3 เฟรม: ภาพท่ากลางชักออกจากซอง 5 ภาพ
		var u := (f - DRAW) / (HITF - DRAW)
		return {"cx": x_cr + (x_hit - x_cr) * (u * u), "key": "pls_iai_draw_%d" % (1 + mini(4, int(u * 5.0))), "sx": 1.04, "sy": 0.98}
	if F < CHIB:   # ปลายจังหวะ ไถลตามแรงนิดเดียว
		var q := f - HITF
		return {"cx": x_hit + 6 * (1 - pow(1 - minf(1.0, q / 4.0), 2)), "key": "pls_iai_draw_5"}
	if F < NOTO:   # chiburi: สะบัดคมลงด้านข้าง (ภาพ noto 1)
		return {"cx": x_hit + 6, "key": "pls_iai_noto_1"}
	# noto → zanshin: เก็บเข้าซองช้าๆ (ภาพ noto 2–5) ถอยครึ่งก้าว · ค้างท่าย่อ
	var q := f - NOTO
	var k := 2 + mini(3, int(q / ((CLICK - NOTO) / 4.0)))
	return {"cx": x_hit + 6 + 4 * minf(1.0, q / 6.0), "key": "pls_iai_noto_%d" % k if f < CLICK else "pls_iai_crouch_0", "sy": 1.0 - 0.02 * minf(1.0, q / 6.0)}

func rion_ghosts(_f: float, F: int) -> void:
	if F >= DRAW and F < HITF + 3:   # ร่างติดตาตามทางพุ่ง 4 ร่าง
		for k in 4:
			var gg := geo(float(DRAW) - 0.5 + k * 0.6)
			gg.key = "pls_iai_draw_%d" % (1 + k)
			ghost(gg, 0.28 - k * 0.04 if F < HITF + 1 else 0.12, Color("#9ae6ff"), 0.5)

func frame(f0: float, F0: int, fresh: bool) -> void:
	super.frame(f0, F0, fresh)
	var f := f0
	var F := F0
	# ความเงียบ: จอมืดลงช้าๆ แล้วคลายหลังชัก
	var dm := 0.0
	if f >= CR and f < DRAW:
		dm = 0.3 * minf(1.0, (f - CR) / (STILL - CR))
	elif f >= DRAW and f < HITF + 8:
		dm = 0.3 * maxf(0.0, 1 - (f - DRAW) / 10.0)
	dim_to(dm, Color("#0b0d1c"))
	if fresh:
		if F == CR:
			dust_at(x_cr + 8, 1.0, 1.0)
		if F == DRAW:
			dust_at(x_cr, 1.0, 1.6)
		if F == HITF:
			burst(Vector2(vis.end.x - 10, cut_y), F, Color("#9ae6ff"))
		if F == CLICK:
			burst(Vector2(vis.get_center().x, cut_y), F, Color("#e8f8ff"))
	var dc := F - CLICK
	if dc >= 0 and dc < 12:
		word("แกร๊ก", x_hit - 30, G - 70 - mini(4, dc), Color("#cfe6ff"), 10, 3)

func fx(n: Node2D, f: float) -> void:
	var F := int(floor(f))
	var g := geo(f)
	# ประกายเล็กที่ด้ามตอนท้ายความเงียบ (บอกว่ากำลังจะชัก)
	if F >= DRAW - 2 and F < DRAW:
		var hx: float = g.cx - 6
		var hy := G - 40.0
		star_px(n, hx, hy, 3 + (F - DRAW + 2) * 2, Color.WHITE, Color("#9ae6ff"))
	# เส้นคมยาวพาดจอ: จากจุดย่อผ่านตัวมอนเลยไปซ้าย · หนาแล้วบาง
	var d := f - DRAW
	if d >= 0 and d < 10:
		var x1 := x_cr - 4
		var x0 := maxf(4.0, vis.position.x - 40.0)
		var prog := minf(1.0, (d + 0.5) / 2.0)
		var al := 1.0 if d < 4 else 1 - (d - 4) / 6.0
		slash_line(n, x1, cut_y - 1, x1 + (x0 - x1) * prog, cut_y + 1, 4 if d < 3 else 2, 1.0, al)
		for i in 8:   # เส้นความเร็ว
			var y := cut_y - 14 + fb_hash(i, 3, 1) * 28
			px(n, x1 - 10 - fb_hash(i, 1, 2) * 80, y, Color(0.9, 0.97, 1, 0.6 * al), 14 + fb_hash(i, 5, 3) * 20, 1)
	# แผลบนตัวมอน: เปิดหลังโดน · วาบซ้ำตอนคมเข้าซอง (แกร๊ก)
	var dh := f - HITF
	if dh >= 0 and dh < 24:
		var kb := mon_kb(f)
		var half := vis.size.x * (0.36 if hard_body() else 0.46)
		var cx := vis.get_center().x + kb
		var al := 1.0 if dh < 8 else maxf(0.35, 1 - (dh - 8) / 10.0)
		var th := 2.0
		var dc := f - CLICK
		if dc >= 0 and dc < 6:
			al = 1.0
			th = 4.0 - dc * 0.4
		slash_line(n, cx + half, cut_y - 1, cx - half, cut_y + 1, th, minf(1.0, (dh + 1) / 2.0), al)
	if F >= CR and F < STILL + 2:   # รอยไถลท่าย่อ
		for i in 5:
			px(n, x_cr - 8 + i * 4 + (F - CR), G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)

func snd(F: int) -> void:
	step_snd(F, IDLE, CR)
	if F == CR:
		play_sfx("ia_slide", [N(0.26, "lowpass", 1400, 300, 0.4, 2)])
	if F == STILL:   # ความเงียบ: ลมหยุด เหลือเสียงต่ำจางๆ
		duck()
		play_sfx("ia_hush", [T(0.4, "sine", 70, 60, 0.25, 0, 0.1)])
	if F == DRAW:   # ชัก: เสียงคมรูดซองสั้น + ลมแหวก
		play_sfx("ia_draw", [N(0.07, "highpass", 5000, 3000, 0.6, 3), N(0.2, "bandpass", 4200, 1200, 0.8, 2.5, 0.02)])
	if F == HITF:
		sfx_hit(false)
	if F == CHIB:
		play_sfx("ia_chiburi", [N(0.1, "bandpass", 2600, 1200, 0.4, 3)])
	if F == CLICK:   # แกร๊ก: คลิกไม้/โลหะสั้น ไม่ใช่กริ๊ง
		play_sfx("ia_click", [N(0.03, "highpass", 2500, 2500, 0.8, 1), T(0.06, "square", 900, 500, 0.12, 0, 0.001, {"lp": 2500})])
