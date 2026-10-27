extends "res://tests/lab/blc_bl0.gd"
## กวาด bl3 (kwan 27 ต.ค. "ขอดูฝีมือ จัดท่านี้มา") — ตามรายงานวิจัยท่า R2 (ดาบเต๋าอู่ตัง · ม้วนเกลียว chan si jin) ปรับจังหวะตามรสนิยม kwan
## วิ่งเข้า → ม้วนเก็บระหว่างวิ่ง (วงแสงจางรอบตัว + เถ้าวน · ไม่ยืนง้าง) → ถึงตัวคลายเกลียว
## → คมกวาดแนวนอนระดับเอวเป็นวงรีรอบทั้งแถว: ครึ่งหน้าผ่านหน้ามอนทีละตัว (โดน HIT · +4 · +8) → ครึ่งหลังวนอ้อมหลังแถวกลับมา (wrap ไม่หยุด)
## → ไถลตามแรงเหวี่ยง → กระโดดถอยแบบท่าฟัน · มอน 3 ตัวเรียงแถว (บอส 1 ตัว) · หยุดภาพ 1 เฟรมเฉพาะตัวแรก · มอนไถลตามทิศกวาด (ไม่กระเด็นตรง)
## ภาพ Rion ประกอบจากภาพที่มีอยู่ (ยังไม่เจนใหม่): วิ่ง pls_run_bl · ม้วน pls_glim_shift_0–1 + pls_atk_bl_3–4 · กวาด pls_bl7_2–3 (แขนเหยียดแนวนอน) · วน pls_atk_bl_6–7

const EX := 10            # เฟรมที่เพิ่มหลังโดนก่อนเริ่มกระโดดถอย (ท่าฟัน 8 → กวาด 18)
const GAP := 4            # เฟรมระหว่างโดนแต่ละตัว (รายงาน: 16/20/24)
const COIL := 8           # ม้วนเก็บ 8 เฟรมสุดท้ายของการวิ่ง
const WAIST := 22         # ระดับเอวเหนือพื้น (จุดที่คมผ่าน)

var mons: Array[Sprite2D] = []
var cxs: Array[float] = []   # กลางตัวมอนแต่ละตัว · [0] = ใกล้ Rion ที่สุด (ขวาสุด)
var arc_c := Vector2.ZERO
var arc_r := Vector2.ZERO

func mv() -> Dictionary:
	return {"id": "bl3", "slide": 6, "reach": 24, "kb": 5, "shk": 1.5, "sfx": "ซวบ!!", "what": "กวาด (bl3)"}

func end_frame() -> int: return END + EX
func stops() -> Array: return [[HIT, 0.06]]   # หยุดภาพ 1 เฟรม เฉพาะตัวแรก (รายงาน: คมเต๋าไม่หยุด)
func caption() -> String: return "ยืนในศึก → วิ่ง ม้วนเก็บ → กวาดทั้งแถว → กระโดดถอย"

func _count() -> int:
	return 1 if foe.begins_with("B") else 3

func setup() -> void:
	super.setup()
	# แถว 3 ตัวต้องอยู่ในจอครบ: ตัวไกลสุดชิดขอบซ้าย · ซ้อนกันเล็กน้อย (62% ของความกว้าง)
	var sp := roundf(mw * 0.62)
	var c0 := mw * 0.5 + 2 + sp * (_count() - 1) if _count() > 1 else float(MX)
	place_monster(int(c0))
	if _count() == 1:   # เป้าเดียว (บอส): ไถลสั้น ไม่ทะลุเข้าตัว
		BM.slide = 3
		BM.reach = 12
	near = mx0 + mw - 17 - BM.reach
	for i in _count():
		cxs.append(c0 - sp * i)
	mons.append(mon)
	for i in range(1, _count()):
		var s := Sprite2D.new()
		s.centered = false
		s.material = fx_mat()
		s.z_index = 1
		add_child(s)
		mons.append(s)
	# วงรีของคม: ขวาสุด = มือ Rion ตอนถึงตัว · ซ้ายสุด = เลยตัวไกลสุดไป 10 · แบนแบบมองเฉียง
	var right := near + 60 - 34
	var left := maxf(8.0, cxs[cxs.size() - 1] - mw * 0.42)   # ปลายวงต้องอยู่ในจอ (วนกลับให้เห็น)
	arc_c = Vector2((right + left) / 2.0, G - WAIST - 2)
	arc_r = Vector2((right - left) / 2.0, 21)   # ครึ่งหน้าลงต่ำใกล้กล้อง · ครึ่งหลังสูงอ้อมหลังแถว = เห็นเป็นวง

## เฟรมฉาก → เฟรมของเครื่องฟัน (ช่วงกวาดยืด EX เฟรม)
func _base_f(f: float) -> float:
	return f if f < HIT else (f - EX if f >= HOP0 + EX else -1.0)

func _hit_f(i: int) -> int:
	return HIT + i * GAP

func _key(F: int) -> String:
	if F >= HIT - COIL and F < HIT:   # ม้วนเก็บระหว่างวิ่ง: มีดลดลงอก → ขึ้นหลังไหล่
		return ["pls_glim_shift_0", "pls_glim_shift_0", "pls_glim_shift_1", "pls_glim_shift_1", "pls_atk_bl_3", "pls_atk_bl_3", "pls_atk_bl_4", "pls_atk_bl_4"][F - (HIT - COIL)]
	return super._key(F)

func geo(f: float) -> Dictionary:
	var bf := _base_f(f)
	if bf >= 0.0:
		return super.geo(bf)
	var q := f - HIT   # 0 … HOP0 − HIT + EX
	var n := float(HOP0 - HIT + EX)
	var F := int(floor(f))
	var key := "pls_bl7_2" if q < 2 else ("pls_bl7_3" if q < 9 else ("pls_atk_bl_6" if q < 13 else "pls_atk_bl_7"))
	var b := {"cx": near - BM.slide * (1 - pow(1 - minf(1.0, q / n), 2.2)), "lift": 0.0, "lean": -0.16 * maxf(0.0, 1 - q / 10.0), "sx": 1.0, "sy": 1.0, "key": key, "flip": false}
	if F - HIT < 2:
		b.sy = 0.94
		b.sx = 1.05
	b.cx += 60.0
	return b

## หัวคมบนวงรี: มุม 0 = ขวา (มือ) · ครึ่งหน้า (ผ่านหน้ามอน) 0→π · ครึ่งหลัง (อ้อมหลังแถว) π→2π
func _theta(f: float) -> float:
	var t0 := HIT - 1.0
	var t1 := float(_hit_f(cxs.size() - 1)) + 2
	if f < t0:
		return -1.0
	if f < t1:   # ครึ่งหน้า: เร็วขึ้นกลางทาง (คลายเกลียว)
		var u := (f - t0) / (t1 - t0)
		return PI * (u * u * (3 - 2 * u))
	return PI + PI * minf(1.0, (f - t1) / 10.0)   # ครึ่งหลัง: ช้าลงแล้วจาง

func _arc_pt(a: float) -> Vector2:
	return arc_c + Vector2(cos(a) * arc_r.x, sin(a) * arc_r.y)

## มุมที่คมผ่านกลางตัวมอน i (ครึ่งหน้า)
func _theta_at(i: int) -> float:
	return acos(clampf((cxs[i] - arc_c.x) / arc_r.x, -1.0, 1.0))

func _show(i: int, key: String, dx: float, amt: float) -> void:
	var s: Sprite2D = mons[i]
	var mt := tx(key)
	s.visible = true
	s.texture = mt
	s.offset = Vector2(-mt.get_width() / 2.0, -mt.get_height())
	s.position = Vector2(roundf(cxs[i] - mw / 2.0) + roundf(dx) + roundf((mw - mt.get_width()) / 2.0) + mt.get_width() / 2.0, G)
	s.material.set_shader_parameter("tint", Color.WHITE)
	s.material.set_shader_parameter("amount", amt)

## มอนไถลตามทิศกวาด (ไปทางซ้าย) แล้วค่อยกลับ · ไม่ใช่กระเด็นถอยตรง
func _slide(d: int) -> float:
	if d < 0:
		return 0.0
	if d < 6:
		return -BM.kb * (1 - pow(1 - d / 6.0, 2))
	return -BM.kb * maxf(0.0, 1 - (d - 6) / 10.0)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var d0 := F - HIT
	shake(F, BM.shk * (1 - d0 / 4.0) if d0 >= 0 and d0 < 4 else 0.0)
	var g := geo(f)
	for i in mons.size():
		var d := F - _hit_f(i)
		var hurt := d >= 0 and d < 10
		_show(i, hurt_key() if hurt else idle_key(f + i * 3), _slide(d), 0.7 if d == 0 and i == 0 else 0.0)   # วาบ 1 เฟรม ไม่ขาวทึบ (ตรวจแสงวาบ R2)
	set_rion(rion, g)
	# ร่างติดตา: ช่วงม้วนเก็บ (วิ่ง) · ช่วงกวาดไถล · สเตปถอยแรก
	if F > HIT - COIL and F < HIT:
		for k in [2, 1]:
			ghost(geo(f - k), 0.15 * (4 - k))
	if d0 >= 0 and d0 < 8:
		ghost(geo(f - 2), 0.18)
	for k in [2, 1]:
		var hp := _hop(int(_base_f(f)) - k) if _base_f(f) >= 0 else {}
		if not hp.is_empty() and hp.k == 0 and hp.q >= hp.h.c and hp.q < hp.h.c + hp.h.a:
			ghost(geo(f - k), 0.12 * (3 - k))
	if fresh:
		if F >= IDLE and F < HIT and (F - IDLE) % STEP == 0:
			dust_at(g.cx + 6, 1.0, 0.45 + 0.4 * (F - IDLE) / RUN)
		if F == HIT:
			dust_at(g.cx + 6, 1.0, 1.4)
			burst(Vector2(cxs[0] + 4, G - WAIST), F, Color("#9ae6ff"))
		if d0 >= 0 and d0 < 10 and d0 % 3 == 0:   # ไถลตามแรงเหวี่ยง
			dust_at(g.cx + 6, 1.0, 0.8 - d0 * 0.05)
		for i in mons.size():
			if F == _hit_f(i):
				debris_at(Vector2(cxs[i] - 4, G - WAIST), "คม", F, 0.7)
		var bf := int(_base_f(f))
		if bf >= HOP0:   # ฝุ่นกระโดดถอยของเครื่องฟัน
			var t0 := HOP0
			for h in HOPS:
				if h.has("skid"):
					for k in range(0, h.skid - 2, 2):
						if bf == t0 + k:
							dust_at(g.cx + 6, 1.0, 0.9 - k * 0.08)
					t0 += h.skid
					continue
				if bf == t0 + 1:
					dust_at(g.cx - 6, -1.0, 0.4 + h.d)
				t0 += h.c + h.a
				if bf == t0:
					dust_at(g.cx + 6, 1.0, 0.4 + h.d * 1.4)
				t0 += h.l
	# ตัวหนังสือ: ชื่อท่าตอนเริ่มม้วน · คำเสียงกลางแถว · ตัวเลขทีละตัวตามจังหวะโดน
	if d0 >= 0 and d0 < 16:
		word(BM.sfx, clampf(cxs[0] - 14, 4, W - 60), maxf(16, my - 10 - mini(5, d0)), Color.WHITE)   # เหนือตัวแรก (ตัวกลางมีตัวเลขยกสูง)
	var b0 := HIT - COIL - 2
	show_bubble("กวาด!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < HIT + 6 else (HIT + 10 - f) / 4.0) if F >= b0 and F < HIT + 10 else 0.0)
	for i in mons.size():
		var d := F - _hit_f(i)
		pop(dmg, maxf(16, cxs[i] + _slide(d)), my + roundf(mh * 0.25) - (i % 2) * 18, d, Color.WHITE, aff_tag(), aff_col())

## วงรีของคม: ชั้นหลังแถว (ครึ่งหลัง) วาดใต้มอน · ชั้นหน้า (ครึ่งหน้า) วาดเหนือมอน
func _band(n: Node2D, f: float, back: bool) -> void:
	var th := _theta(f)
	if th < 0:
		return
	var L := 1.6   # ความยาวหาง (เรเดียน)
	var fade := 1.0 if th < 1.7 * PI else maxf(0.0, (2 * PI - th) / (0.3 * PI))
	var steps := 160
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
		for k in steps + 1:
			var u := float(k) / steps   # 0 = ปลายหาง · 1 = หัวคม
			var a := th - L * (1 - u)
			if a < 0:
				continue
			var on_back := fmod(a, 2 * PI) > PI
			if on_back != back:
				continue
			# หนา/สว่างสุดกลางครึ่งหน้า (เร็วสุด) · ครึ่งหลังบางลง
			var spd := sin(clampf(a, 0.0, PI)) if a <= PI else 0.45
			var w: float = (1.5 + 4.5 * spd) * pow(u, 0.7) + layer[1]
			if w < 1:
				continue
			var p := _arc_pt(a)
			var col: Color = layer[0]
			col.a = fade * (0.55 if on_back else 1.0) * (0.35 + 0.65 * u)
			px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w) + 1)
	if not back and th <= PI and th > 0.05:   # หัวคม: แสงเรือง 3 ชั้น
		var hp := _arc_pt(th)
		disc(n, hp.x, hp.y, 4, Color(0.6, 0.9, 1, 0.35 * fade))
		disc(n, hp.x, hp.y, 2, Color(1, 1, 1, 0.95 * fade))
	if not back and th <= PI:   # เศษลม/เถ้าปลิวตามแนวสัมผัสหลังหัวคม
		var hp := _arc_pt(th)
		for i in 7:
			var r := fb_hash(i, floor(f), 3)
			px(n, hp.x + 6 + i * 5 + r * 4, hp.y - 3 + fb_hash(i, 5, 7) * 7, Color(0.85, 0.8, 0.74, 0.7 - i * 0.08), 3 + int(r * 3), 1)

func draw_back(n: Node2D) -> void:
	_band(n, t / SEC, true)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var st := geo(f)
	# ม้วนเก็บ: วงแสงจางรอบลำตัววนหนึ่งรอบ + เถ้าวนตาม (ไม่มีประกายดูดเข้าแบบเวท)
	var c := F - (HIT - COIL)
	if c >= 0 and c < COIL + 1:
		var u := (f - (HIT - COIL)) / COIL
		var ctr := Vector2(st.cx - 2, G - st.lift - 40)
		for k in 40:   # หางวงแสงไล่ตามหัว (วนหนึ่งรอบใน 8 เฟรม)
			var a := -PI / 2 + TAU * (u - 0.7 * k / 40.0)
			var al := 0.7 * (1 - k / 40.0) * (1.0 if u < 0.85 else maxf(0.0, (1 - u) / 0.15))
			var w := 2.0 if k < 14 else 1.0
			px(n, ctr.x + cos(a) * 17, ctr.y + sin(a) * 7, Color(0.62, 0.92, 1, al), w, w)
		for k in 8:   # เถ้าวนตามเกลียว
			var a := TAU * (u * 1.3 + k / 8.0)
			px(n, ctr.x + cos(a) * (20 + k % 3 * 2), ctr.y + 6 + sin(a) * 9, Color(0.86, 0.8, 0.72, 0.8), 2 if k % 3 == 0 else 1, 1)
	_band(n, f, false)
	# แผลแนวนอนระดับเอวบนตัวมอนแต่ละตัว (ร่างแข็ง = รอยขูดตื้นสั้นกว่า)
	for i in mons.size():
		var d := F - _hit_f(i)
		if d >= 0 and d < 12:
			var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 6.0)
			var half := mw * (0.18 if hard_body() else 0.24)
			var x0 := cxs[i] + _slide(d)
			var wy := _arc_pt(_theta_at(i)).y - 3   # แผลอยู่ระดับที่คมผ่านตัวนั้นจริง
			slash_line(n, x0 + half, wy - 1, x0 - half, wy + 1, 2, minf(1.0, (d + 1) / 2.0), al)
	if st.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - st.lift / 40.0):
				px(n, st.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	var d0 := F - HIT
	if d0 >= 0 and d0 < 8:   # รอยไถลเท้า
		for i in 6:
			px(n, st.cx - 30 + i * 4 + d0, G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)

func sounds(F0: int) -> void:
	var F := F0
	if F < HIT - COIL or F >= HOP0 + EX:   # ฝีเท้า · กระโดดถอย = เครื่องฟันเดิม
		var bf := F if F < HIT else F - EX
		if bf < HIT - 6 or bf >= HOP0:
			super.sounds(bf)
		return
	if F < HIT and (F - IDLE) % STEP == 0:
		var pk := snappedf(0.35 + 0.25 * (F - IDLE) / RUN, 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == HIT - COIL:   # ม้วนเก็บ: ลมพันตัวโทนต่ำ ยังไม่มีเสียงคม
		play_sfx("sw_coil", [N(0.45, "bandpass", 260, 620, 0.32, 2.5, 0, {"attack": 0.2})])
	if F == HIT - 1:   # คลายเกลียว: หวีดไต่ระดับตามความเร็ววง (~800 → 2,400 Hz) แล้วลง
		play_sfx("sw_sweep", [N(0.42, "bandpass", 800, 2400, 0.85, 2.5, 0, {"attack": 0.08}), N(0.5, "bandpass", 2400, 900, 0.4, 2, 0.4), N(0.25, "highpass", 3200, 8000, 0.35, 6, 0.05)])
	for i in mons.size():
		if F == _hit_f(i):
			if i == 0:
				sfx_hit(false)
			else:   # ตัวถัดไป: กระทบเบา ไม่ตูมซ้ำ (คมไม่หยุด)
				play_sfx("sw_tick", [N(0.07, "highpass", 3000, 6000, 0.55, 2), N(0.18, "bandpass", 4200, 2600, 0.3, 12, 0.01), T(0.2, "sine", 160, 60, 0.35, 0, 0.002)])
			sfx_mon(false, 0.6 if foe == "B1" else 1.0 + i * 0.06)
	if F == _hit_f(mons.size() - 1) + 3:   # วนอ้อมหลังแถว: ลมจางลง
		play_sfx("sw_wrap", [N(0.5, "bandpass", 1600, 500, 0.3, 2)])
	if F == HIT + 2:
		play_sfx("brake", [N(0.18, "lowpass", 1600, 400, 0.35, 2)])
