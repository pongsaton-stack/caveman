extends "res://tests/lab/lab_stage.gd"
## เครื่องฉาก "วิ่งเข้าฟัน" ใน Godot — ย้ายจากหน้าเว็บ blc_* (blcKey/blcState/blcView/blcSound/glimFx/glimSound ใน tools/web/anim_test.tpl.html)
## ไฟล์นี้ = ฟัน bl0 · ท่าอื่นที่ใช้เครื่องเดียวกัน extends ไฟล์นี้แล้วเขียนทับ mv(): เขี้ยวพุ่ง bl1 (blc_bl1.gd) · ประกาย (glim_bl1/bl3/bl5.gd)
## ยืนในศึก → วิ่งเข้า (ฝุ่น) ง้างระหว่างวิ่ง → ฟันตอนถึงตัว (หยุดภาพ) → ไถลตามแรง → กระโดดถอย 2 สเตป + ไถลตั้งหลัก → ยืนในศึก
## ประกาย: กลางง้างเวลาหยุด P เฟรม (หลอดไฟติด · เห็นท่าใหม่ล่วงหน้า · แถบชื่อท่า) แล้วใช้ท่าใหม่แทน · มอนยืนที่ x 74 (PKV.MX) · Rion เริ่มที่ W−100

const MX := 74
const IDLE := 18
const RUN := 18
const HIT := 36
const HOP0 := 44
const END := 100
const STEP := 3
## สเตปกระโดดถอย: ระยะ (สัดส่วน) · ย่อ · ลอย · ลง · สูง · skid = ไถลถอยตั้งหลัก
const HOPS := [{"d": 0.5, "c": 2, "a": 9, "l": 2, "h": 16}, {"d": 0.3, "c": 2, "a": 7, "l": 0, "h": 12}, {"d": 0.2, "skid": 10}]
## ปลายมีดของภาพ pls_bl1_0–7 (DATA.swing.tips.pls_bl1)
const TIPS_BL1 := [[46, 64], [46, 70], [50, 70], [55, 66], [54, 64], [39, 69], [31, 67], [34, 67]]
## ข้อมูลท่าในต้นไม้ 17 ท่า (glimRow) สำหรับแถบชื่อท่าใหม่
const ROWS := {"bl1": {"name_th": "เขี้ยวพุ่ง", "school": "คม", "branch": "เขี้ยว", "scope": "single", "power": 145, "hits": 1},
	"bl3": {"name_th": "กวาด", "school": "คม", "branch": "กวาด", "scope": "row", "power": 90, "hits": 1},
	"bl5": {"name_th": "ปาดไว", "school": "คม", "branch": "ลื่นไหล", "scope": "single", "power": 80, "hits": 1}}
const BL1 := {"id": "bl1", "slide": 10, "reach": 31, "kb": 9, "shk": 3.5, "sfx": "ฉึก!!", "what": "เขี้ยวพุ่ง (bl1)", "CROUCH": 27, "LAUNCH": 30, "lunge": 64, "lift": 5}

var BM := {}
var P := 0
var start := 0.0
var near := 0.0
var art_lift := {}
var glim_dark: ColorRect

## ค่าท่า (BLC_MV ของหน้าเว็บ)
func mv() -> Dictionary:
	return {"id": "bl0", "slide": 7, "reach": 25, "kb": 6, "shk": 2.5, "sfx": "ฉัวะ!", "what": "ฟัน (bl0)"}

func tech_id() -> String: return mv().get("to", mv().id)
func end_frame() -> int: return END + mv().get("P", 0)
func stops() -> Array: return [[HIT + mv().get("P", 0), 0.12]]
func caption() -> String: return "ยืนในศึก → วิ่ง → %s → กระโดดถอย" % mv().what

func setup() -> void:
	BM = mv()
	P = BM.get("P", 0)
	place_monster(MX)
	start = W - 100
	near = mx0 + mw - 17 - BM.reach
	if BM.has("glim"):   # เวลาหยุด: ทั้งฉากมืดคราม (ใต้ Rion ที่สว่างขอบทอง)
		glim_dark = ColorRect.new()
		glim_dark.color = Color("#120c2e")
		glim_dark.position = Vector2(-8, -8)
		glim_dark.size = Vector2(W + 16, H + 16)
		glim_dark.z_index = 3
		glim_dark.modulate.a = 0.0
		add_child(glim_dark)

func _bl1() -> bool:
	return BM.id == "bl1"

## เฟรมฉาก F0 → [เฟรมท่า, เฟรมในเวลาหยุด (−1 = ไม่หยุด)] (glimMap)
func _map(f0: float) -> Array:
	if not BM.has("glim") or f0 < BM.FZ:
		return [f0, -1]
	if f0 < BM.FZ + P:
		return [float(BM.FZ), int(floor(f0 - BM.FZ))]
	return [f0 - P, -1]

func _n(h: Dictionary) -> int:
	return h.skid if h.has("skid") else h.c + h.a + h.l

func _hop_end() -> int:
	var e := HOP0
	for h in HOPS:
		e += _n(h)
	return e

func _hop(F: int) -> Dictionary:   # สเตปที่ F อยู่
	var t0 := HOP0
	var f0 := 0.0
	for k in HOPS.size():
		var h: Dictionary = HOPS[k]
		var n := _n(h)
		if F >= t0 and F < t0 + n:
			return {"k": k, "q": F - t0, "h": h, "f0": f0, "f1": f0 + h.d, "t": t0}
		t0 += n
		f0 += h.d
	return {}

func _arc(hp: Dictionary) -> float:
	var u: float = (hp.q - hp.h.c + 1.0) / (hp.h.a + 1.0)
	return roundf(4 * hp.h.h * u * (1 - u))

## ภาพกระโดดลอยในผืนเองกี่จุด (เท้าเหนือแถว 108) → หักออกจากโค้ง ไม่ให้ลอยซ้อน (blcArtLift)
func _art_lift(key: String) -> float:
	if not art_lift.has(key):
		var im := tx(key).get_image()
		var bot := 0
		for y in range(im.get_height() - 1, -1, -1):
			for x in im.get_width():
				if im.get_pixel(x, y).a > 0.5:
					bot = y
					break
			if bot:
				break
		art_lift[key] = maxf(0.0, 108.0 - bot)
	return art_lift[key]

func _key(F: int) -> String:
	if F < IDLE:
		return "pls_idle_bl_%d" % (posmod(F / 4, 4))
	if _bl1() and F < HOP0:   # ภาพ bl1: 3 ย่อ · 5 พุ่ง · 6 แทง · 7 ตามแรง
		if BM.has("glim") and BM.has("SHIFT") and F > BM.FZ and F < BM.CROUCH:
			return "pls_glim_shift_%d" % mini(3, F - BM.FZ - 1)   # ท่ากลาง: ลดมีดจากไหล่ลงมาที่อก
		if BM.has("glim") and BM.has("SHIFT") and F >= BM.WIND and F <= BM.FZ:
			return "pls_atk_bl_%d" % [1, 2, 2, 3, 4][F - BM.WIND]
		if F < BM.CROUCH:
			return "pls_run_bl_%d" % ((F - IDLE) % 6)
		if F < BM.LAUNCH:
			return "pls_bl1_3"
		if F < HIT:
			return "pls_bl1_5"
		if F < HIT + 3:
			return "pls_bl1_6"
		return "pls_bl1_7"
	if F < HIT - 8:
		return "pls_run_bl_%d" % ((F - IDLE) % 6)
	if F < HIT:
		return "pls_atk_bl_%d" % (1 + mini(3, (F - (HIT - 8)) / 2))   # ง้างระหว่างวิ่ง
	if F < HIT + 3:
		return "pls_atk_bl_5"   # ฟาด
	if F < HOP0:
		return "pls_atk_bl_%d" % mini(7, 6 + (F - HIT - 3) / 2)
	var hp := _hop(F)
	if not hp.is_empty():
		var q: int = hp.q
		var h: Dictionary = hp.h
		if h.has("skid"):
			return "pls_hop_bl_1" if q < h.skid - 1 else "pls_hop_bl_0"
		if q < h.c:
			return "pls_hop_bl_1"
		if q < h.c + h.a:
			var u: float = (q - h.c + 1.0) / (h.a + 1.0)
			return "pls_hop_bl_4" if _arc(hp) >= _art_lift("pls_hop_bl_4") else ("pls_hop_bl_2" if u <= 0.5 else "pls_hop_bl_3")
		return "pls_hop_bl_0" if hp.k == HOPS.size() - 1 and q == h.c + h.a + h.l - 1 else "pls_hop_bl_1"
	return "pls_idle_bl_%d" % (posmod((F - _hop_end()) / 4, 4))

## ตำแหน่ง Rion (blcState) · cx = กลางผืน · f = เฟรมท่า (ทศนิยม = เลื่อนต่อเนื่อง)
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var b := {"cx": start, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": _key(F), "flip": false}
	var slide: float = BM.slide
	var stop := near - slide
	if F < IDLE:
		b.sy = 1 - 0.015 * (posmod(F / 4, 2))
	elif _bl1() and F < HIT:
		var cx: float = near + BM.lunge
		var brake := 3.0
		if F < BM.CROUCH:   # วิ่งเร่งเข้าจุดย่อ
			var u: float = (f - IDLE) / (BM.CROUCH - IDLE)
			b.cx = start + (cx - start) * (u * u * 0.4 + u * 0.6)
			b.lean = -0.04 * minf(1.0, u * 3)
		elif F < BM.LAUNCH:   # เบรกไถลเข้าท่าย่อ
			var q: float = f - BM.CROUCH
			b.cx = cx - brake * (1 - pow(1 - (q + 1) / (BM.LAUNCH - BM.CROUCH), 2))
			b.lean = -0.06
			b.sy = 0.95
			b.sx = 1.03
		else:   # พุ่ง: แนวนอนคงที่ · แนวตั้งพาราโบลาเตี้ย ลงพื้นตรงจังหวะแทง
			var n: float = HIT - BM.LAUNCH
			var u: float = (f - BM.LAUNCH + 1) / (n + 1)
			var x0 := cx - brake
			b.cx = x0 + (near - x0) * u
			b.lift = roundf(4 * BM.lift * u * (1 - u))
			b.lean = -0.1
			if F == BM.LAUNCH:
				b.sx = 1.05
				b.sy = 0.97
	elif F < HIT:
		var u := (f - IDLE) / RUN
		b.cx = start + (near - start) * (u * u * 0.4 + u * 0.6)   # เร่งออกตัว
		b.lean = -0.04 * minf(1.0, u * 3)
	elif F < HOP0:
		var q := f - HIT
		b.cx = near - slide * (1 - pow(1 - minf(1.0, q / 6.0), 2))   # ไถลตามแรง
		b.lean = -0.18 if q < 3 else -0.18 * maxf(0.0, 1 - (q - 3) / 5.0)
		if F - HIT < 2:
			b.sy = 0.93
			b.sx = 1.05
	else:
		var hp := _hop(F)
		if hp.is_empty():
			b.cx = start
			b.sy = 1 - 0.015 * posmod((F - _hop_end()) / 4, 2)
		else:
			var h: Dictionary = hp.h
			var q: float = f - hp.t
			var last: Dictionary = HOPS[HOPS.size() - 1]
			var home_a: float = start - (0.0 if last.has("skid") else last.d * 8)
			var prev_l: bool = hp.k > 0 and HOPS[hp.k - 1].get("l", 0) > 0
			var x0: float = stop + (home_a - stop) * hp.f0 + (HOPS[hp.k - 1].d * 8 if prev_l else 0.0)
			var x1: float = stop + (home_a - stop) * hp.f1
			if h.has("skid"):   # ไถล: เริ่มเร็วเท่าตอนลง แล้วเบรก
				var u := minf(1.0, (q + 1) / (h.skid - 2.0))
				b.cx = x0 + (x1 - x0) * (1 - pow(1 - u, 2))
				b.lean = -0.05 * (1 - u)
			elif q < h.c:
				b.cx = x0
			elif q < h.c + h.a:   # ลอย: แนวนอนคงที่ แนวตั้งพาราโบลา
				var u: float = (q - h.c + 1) / h.a
				b.cx = x0 + (x1 - x0) * minf(1.0, u)
				b.lift = maxf(0.0, _arc(hp) - _art_lift(b.key))
				b.lean = 0.05 * (1 - u)
			else:
				b.cx = x1 + mini(2, int(q) - h.c - h.a + 1) * h.d * 4
	b.cx += 60.0
	return b

func _kb(d: int) -> float:
	return roundf(-BM.kb * maxf(0.0, 1 - maxf(0.0, d - 2) / 10.0)) if d >= 0 else 0.0

func _to_w(s: Dictionary, p: Vector2) -> Vector2:   # จุดในผืน → ฉาก (เอน/ยืดตามตัว)
	var l := Vector2((p.x - 60) * s.sx, (p.y - 108) * s.sy).rotated(s.lean)
	return Vector2(s.cx, G - s.lift) + l

## ปลายมีดในฉากตอนกระทบ: bl1 = ปลายภาพแทง (bl1_6) · bl0 = ทางมีดมุม A[1]
func _tip() -> Vector2:
	var p := Vector2(TIPS_BL1[6][0], TIPS_BL1[6][1]) if _bl1() else swing_pt(SWING.A[1])
	return _to_w(geo(HIT), p)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var mp := _map(f0)
	var f: float = mp[0]
	var gz: int = mp[1]
	var F := int(floor(f))
	var d := F - HIT
	world_stop(gz >= 0)
	shake(F, BM.shk * (1 - d / 5.0) if d >= 0 and d < 5 and gz < 0 else 0.0)
	var g := geo(f)
	# มอน: ยืนหายใจ → วาบขาว 2 · ผงะ 10 · กระเด็นถอย แล้วกลับ
	var kb := _kb(d)
	show_mon(hurt_key() if d >= 0 and d < 10 else idle_key(f), kb, 1.0 if d >= 0 and d < 2 else 0.0)
	set_rion(rion, g)
	# ร่างติดตา: ช่วงง้างวิ่ง (bl1 = ช่วงพุ่ง 3 ร่าง) · สเตปถอยแรก
	if gz < 0 and F > (BM.LAUNCH if _bl1() else HIT - 8) and F < HIT:
		for k in ([3, 2, 1] if _bl1() else [2, 1]):
			ghost(geo(f - k), 0.15 * (4 - k) / (1.5 if _bl1() else 1.0))
	for k in [2, 1]:
		var hp := _hop(F - k)
		if not hp.is_empty() and hp.k == 0 and hp.q >= hp.h.c and hp.q < hp.h.c + hp.h.a:
			ghost(geo(f - k), 0.12 * (3 - k))
	if BM.has("glim"):
		_glim_frame(f0, F0, f, F, gz, g)
	# ฝุ่น
	if fresh and gz < 0:
		var run_end: int = BM.CROUCH if _bl1() else HIT
		if F >= IDLE and F < run_end and (F - IDLE) % STEP == 0:
			dust_at(g.cx + 6, 1.0, 0.45 + 0.4 * (F - IDLE) / RUN)
		if _bl1() and F == BM.CROUCH:
			dust_at(g.cx - 6, -1.0, 0.9)
		if _bl1() and F == BM.LAUNCH:
			dust_at(g.cx + 6, 1.0, 1.7)
		if F == HIT:
			dust_at(g.cx + 6, 1.0, 1.3)
			burst(_tip(), F, Color("#ffd040") if BM.has("glim") else Color("#9ae6ff"))
		var t0 := HOP0
		for h in HOPS:
			if h.has("skid"):
				for i in range(0, h.skid - 2, 2):
					if F == t0 + i:
						dust_at(g.cx + 6, 1.0, 0.9 - i * 0.08)
				t0 += h.skid
				continue
			if F == t0 + 1:
				dust_at(g.cx - 6, -1.0, 0.4 + h.d)
			t0 += h.c + h.a
			if F == t0:
				dust_at(g.cx + 6, 1.0, 0.4 + h.d * 1.4)
			t0 += h.l
	# ตัวหนังสือ: คำเสียง · ตะโกนชื่อท่าตอนเริ่มออกท่า (ประกาย = ชื่อท่าใหม่ หลังเวลาเดิน) · ตัวเลข
	if d >= 0 and d < 14:
		word(BM.sfx, maxf(4, mx0 + kb + mw / 2.0 - 14), maxf(24 if BM.has("glim") else 16, my - 8 - mini(5, d)), Color("#ffe27a") if BM.has("glim") else Color.WHITE)
	var b0: int = BM.FZ + 1 if BM.has("glim") else (BM.CROUCH - 2 if _bl1() else HIT - 10)
	var nm: String = ROWS[BM.to].name_th if BM.has("glim") else ("เขี้ยวพุ่ง" if _bl1() else "ฟัน")
	show_bubble(nm + "!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < HIT + 4 else (HIT + 8 - f) / 4.0) if gz < 0 and F >= b0 and F < HIT + 8 else 0.0)
	if gz < 0:
		pop(dmg, maxf(16, mx0 + kb - 8), my + roundf(mh * 0.25), d, Color("#ffe08a") if BM.has("glim") else Color.WHITE, aff_tag(), aff_col())

# ── ประกาย (glimFx) ──────────────────────────────────
func _glim_frame(f0: float, F0: int, f: float, F: int, gz: int, st: Dictionary) -> void:
	var gold := Color("#ffd24a")
	if gz >= 0:
		var tt: float = f0 - BM.FZ
		var in_a := minf(1.0, (gz + 1) / 3.0)
		var out_a: float = (P - tt) / 5.0 if gz > P - 5 else 1.0
		glim_dark.modulate.a = 0.66 * in_a * out_a
		var ra: float = (0.55 + 0.35 * sin(gz * 0.9)) * out_a   # Rion สว่างกลางความมืด ขอบทอง
		for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
			var gg := st.duplicate()
			gg.cx += o.x
			gg.lift -= o.y
			ghost(gg, ra, gold, 1.0)
		rion.z_index = 4
		if gz >= 13:   # ★ ประกาย!
			var k := minf(1.0, (gz - 12) / 2.0)
			var bx := roundf(st.cx) + 2
			var yb: float = G - st.lift - 74 - 6
			word("★ ประกาย!", minf(W - 70, bx + 14), maxf(14, yb - 14 - (15 - gz if gz < 15 else 0)), Color(1, 226 / 255.0, 122 / 255.0, k * out_a))
		if gz >= 15 and gz < 29:   # ภาพท่าใหม่ล่วงหน้า: ร่างฟ้าพุ่งเข้ามอน
			var u := minf(1.0, (gz - 15) / 7.0)
			var gx: float = (st.cx - 60) + (near - (st.cx - 60)) * (u * u * (3 - 2 * u))
			var ga := 0.55 * (1.0 if gz < 25 else (29 - gz) / 4.0)
			var gk: String = BM.ghost[0 if u < 0.25 else (1 if u < 1 else 2)]
			if u < 1:
				for e in [3, 2, 1]:
					ghost({"cx": gx + 60 + e * 10, "lift": st.lift, "key": gk, "lean": st.lean, "sx": st.sx, "sy": st.sy}, ga * 0.25 * (4 - e) / 3, Color("#7ad0ff"), 1.0)
			ghost({"cx": gx + 60, "lift": st.lift, "key": gk, "lean": st.lean, "sx": st.sx, "sy": st.sy}, ga, Color("#9ae6ff"), 0.75)
		if gz >= 17:   # แถบชื่อท่าใหม่เลื่อนเข้าจากขวา
			var k := minf(1.0, (gz - 17) / 4.0)
			var l0 := 40 + roundf(pow(1 - k, 2) * W * 0.8)
			var r: Dictionary = ROWS[BM.to]
			var sc := {"single": "เดี่ยว", "row": "ทั้งแถว", "column": "ทะลุแนว", "all": "ทั้งหมด"}
			word(r.name_th, l0 + 18, 10 + 19, Color(1, 226 / 255.0, 122 / 255.0, out_a), 15)
			var ix := l0 + 18 + text_w(r.name_th, 15) + 10
			var l1 := "ท่าใหม่ · %s กิ่ง%s" % [r.school, r.branch]
			var l2 := "%s · พลัง %d%s" % [sc.get(r.scope, r.scope), r.power, (" × %d" % r.hits) if r.hits > 1 else ""]
			if text_w(l1 + " · " + l2, 8) <= W - 6 - ix:
				word(l1 + " · " + l2, ix, 10 + 17, Color(1, 1, 1, out_a), 8)
			else:
				word(l1, ix, 10 + 12, Color(1, 1, 1, out_a), 8)
				word(l2, ix, 10 + 22, Color(1, 1, 1, out_a), 8)
	else:
		glim_dark.modulate.a = 0.0
		if F >= BM.FZ and F < HIT + 2:   # หลังเวลาเดิน: ขอบทองจางระหว่างย่อ-พุ่ง
			var ra := 0.5 * maxf(0.0, 1 - (F - BM.FZ) / 12.0)
			for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
				var gg := st.duplicate()
				gg.cx += o.x
				gg.lift -= o.y
				ghost(gg, ra, gold, 1.0)
		if F0 >= 100:   # ป้ายได้ท่าใหม่ตอนท้าย
			var k := minf(1.0, (F0 - 100) / 4.0)
			var y := -22 + 30 * (1 - pow(1 - k, 3))
			var msg: String = "★ ได้ท่าใหม่ · " + ROWS[BM.to].name_th
			var w: float = text_w(msg, 11) + 16
			word(msg, (W - w) / 2 + 8, y + 13, Color("#2a1a14"), 11, 0)

func _bulb(n: Node2D, x: float, y: float, lit: bool) -> void:   # หลอดไฟ (glimBulb): แก้ว 10x10 + ขั้ว
	var O := Color("#2a1a14")
	var g := Color("#fff6a0") if lit else Color("#8a90a8")
	var rects := [[-4, -16, 8, 1], [-6, -15, 12, 1], [-7, -14, 14, 7], [-6, -7, 12, 2], [-4, -5, 8, 1]]
	for r in rects:
		px(n, x + r[0] - 1, y + r[1] - 1, O, r[2] + 2, r[3] + 2)
	for r in rects:
		px(n, x + r[0], y + r[1], g, r[2], r[3])
	px(n, x - 4, y - 13, Color.WHITE, 2, 3)
	var fil := Color("#ff9a20") if lit else Color("#6a3a30")
	px(n, x - 2, y - 10, fil, 1, 4)
	px(n, x + 1, y - 10, fil, 1, 4)
	px(n, x - 2, y - 10, fil, 4, 1)
	px(n, x - 4, y - 4, O, 8, 5)
	px(n, x - 3, y - 4, Color("#b8bcc8"), 6, 1)
	px(n, x - 3, y - 2, Color("#8a8e9a"), 6, 1)
	px(n, x - 1, y, O, 2, 1)
	if lit:
		px(n, x - 6, y - 14, Color("#ffd040"), 1, 6)

func _glim_fx(n: Node2D, f0: float, F0: int, st: Dictionary) -> void:
	var gz := int(floor(f0 - BM.FZ))
	var hx := roundf(st.cx)
	var bx := hx + 2
	var by: float = G - st.lift - 74 - 6
	if gz >= 0 and gz < P:
		var in_a := minf(1.0, (gz + 1) / 3.0)
		var out_a := (P - gz) / 5.0 if gz > P - 5 else 1.0
		for i in 26:   # ฝุ่นในอากาศค้างนิ่ง
			if (gz + i) % 9 < 6:
				px(n, fmod(fb_hash(i, 77, 1) * W + i * 13, W), int(fb_hash(i, 77, 2) * (G - 10)), Color(180 / 255.0, 170 / 255.0, 1, 0.25 * in_a * out_a))
		for i in range(-13, 14):   # แอ่งแสงใต้เท้า
			px(n, hx + i * 1.5, G - 1 - (0 if absi(i) > 9 else 1), Color(1, 214 / 255.0, 90 / 255.0, 0.35 * in_a * out_a), 2, 1)
		if gz < 2:   # จอวาบตอนเวลาหยุด
			px(n, -8, -8, Color(1, 1, 1, 0.6 * (1 - gz / 2.0)), W + 16, H + 16)
		if gz >= 2 and gz < 9:   # ประกายลอยจากอกขึ้นหัว (ส่ายเป็นเกลียว)
			var u := (gz - 2) / 6.0
			var sx := hx - 4 + sin(u * 9) * 3 * (1 - u)
			var sy: float = (G - 44) + (by - 8 - (G - 44)) * (u * u * (3 - 2 * u))
			for k in range(4, -1, -1):
				px(n, sx + (sin((u - k * 0.04) * 9) * 3 * (1 - u) if k else 0.0), sy + k * 3, Color(1, 214 / 255.0, 90 / 255.0, 0.6 - k * 0.1) if k else Color.WHITE, 1 if k else 2, 2)
		if gz >= 9 and gz < 27:   # หลอดโผล่ลอยขึ้น → กะพริบ ติก-ติก → ติด
			var lit := gz >= 13 or gz == 10 or gz == 12
			var yb: float = by - (11 - gz if gz < 11 else 0)
			if lit and gz >= 13:   # รัศมีหมุน
				var L := mini(14, (gz - 12) * 3)
				for i in 12:
					var a := i * TAU / 12 + gz * 0.05
					for k in range(0, L, 2):
						px(n, bx + cos(a) * (13 + k), yb - 10 + sin(a) * (13 + k), Color("#ffd040") if i % 2 else Color("#fff6a0"), 1 if i % 2 else 2, 1 if i % 2 else 2)
			if gz >= 13 and gz < 19:   # วงคลื่นแสงตอนติด
				var r := 8 + (gz - 13) * 6
				for i in 24:
					var a := i * PI / 12
					px(n, bx + cos(a) * r, yb - 10 + sin(a) * r, Color.WHITE if gz < 16 else Color("#ffd040"), 2, 2)
			if gz >= 13 and gz < 15:
				n.draw_set_transform(Vector2(bx, yb) * (1 - 1.3), 0, Vector2(1.3, 1.3))
			_bulb(n, bx, yb, lit)
			n.draw_set_transform(Vector2.ZERO)
		if gz >= 15 and gz < 29:   # เส้นทางพุ่งประ ๆ + ดาวที่ปลาย
			var ga := 0.55 * (1.0 if gz < 25 else (29 - gz) / 4.0)
			var x := roundf(near + 60)
			while x < hx - 6:
				if int(x + gz * 2) % 8 < 4:
					px(n, x, G - 30, Color(154 / 255.0, 230 / 255.0, 1, ga * 0.7), 2, 1)
				x += 4
			if gz >= 22:
				star_px(n, near + 26, G - 41, 4 + (gz - 22), Color(1, 1, 1, 0.8), Color(154 / 255.0, 230 / 255.0, 1, 0.6))
		if gz >= 17:   # พื้นแถบชื่อท่าใหม่
			var k := minf(1.0, (gz - 17) / 4.0)
			var l0 := 40 + roundf(pow(1 - k, 2) * W * 0.8)
			px(n, l0, 10, Color(16 / 255.0, 10 / 255.0, 40 / 255.0, 0.85 * out_a), W - 40, 26)
			px(n, l0, 10, Color(1, 208 / 255.0, 64 / 255.0, out_a), W - 40, 1)
			px(n, l0, 35, Color(1, 208 / 255.0, 64 / 255.0, out_a), W - 40, 1)
			for i in 7:
				px(n, l0 + 6 + ((i * 37 + gz * 9) % (W - 60)), 14 + i * 3, Color(1, 214 / 255.0, 90 / 255.0, 0.35 * out_a), 12, 1)
		if gz >= 27:   # หลอดแตกเป็นเศษทอง วิ่งเข้าปลายมีดที่ง้างค้าง
			var u := minf(1.0, (gz - 27) / float(P - 29))
			var tip := Vector2(st.cx - 60 + 86, G - st.lift - (108 - 62))
			for i in 10:
				var a := i * PI / 5 + 0.3
				var r := 6 + 10 * sin(PI * minf(1.0, u * 1.4))
				var e := u * u
				var x := bx + cos(a) * r * (1 - e) + (tip.x - bx) * e
				var y: float = by - 10 + sin(a) * r * (1 - e) + (tip.y - by + 10) * e
				if u < 1:
					px(n, x, y, Color("#ffd040") if i % 3 else Color.WHITE, 2, 2)
					px(n, x - cos(a) * 2, y - sin(a) * 2, Color(1, 180 / 255.0, 40 / 255.0, 0.5))
			if gz >= P - 3:
				star_px(n, tip.x, tip.y, 3 + (gz - P + 3) * 3, Color.WHITE, Color("#ffd040"))
	if F0 >= 100:   # ป้ายได้ท่าใหม่ (พื้น)
		var k := minf(1.0, (F0 - 100) / 4.0)
		var y := -22 + 30 * (1 - pow(1 - k, 3))
		var w := text_w("★ ได้ท่าใหม่ · " + ROWS[BM.to].name_th, 11) + 16
		var x := (W - w) / 2
		px(n, x - 1, y - 1, Color("#2a1a14"), w + 2, 20)
		px(n, x, y, Color("#fff3c4"), w, 18)
		px(n, x, y + 17, Color("#ffd040"), w, 1)

func draw_fx(n: Node2D) -> void:
	var f0 := t / SEC
	var F0 := int(floor(f0))
	var mp := _map(f0)
	var f: float = mp[0]
	var gz: int = mp[1]
	var F := int(floor(f))
	var d := F - HIT
	var st := geo(f)
	var kb := _kb(d)
	if gz < 0 and d >= 0 and d < 7:   # รอยไถล
		for i in 6:
			px(n, near + 30 + i * 4 + d * 2, G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)
	if st.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - st.lift / 40.0):
				px(n, st.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	if _bl1() and gz < 0 and F >= BM.LAUNCH and F <= HIT + 1:   # เส้นความเร็วแนวนอนหลังตัว
		for i in 6:
			px(n, st.cx + 10 + roundf(fb_hash(i, F, 5) * 8), G - st.lift - 18 - roundf(fb_hash(i, 7, 2) * 30), Color(230 / 255.0, 248 / 255.0, 1, 0.85 if F <= HIT else 0.4), 10 + roundf(fb_hash(i, F, 9) * 18), 1)
	if BM.id == "bl0" and gz < 0 and d >= 0 and d < 7:   # รอยมีดติดตัว (blcTrail 3 ชั้น)
		var A: Array = SWING.A
		var ki := int(str(st.key).get_slice("_", 3)) if str(st.key).begins_with("pls_atk_bl_") else 5
		var hd: float = A[clampi(ki - SWING.f0, 1, A.size() - 1)]
		var t0: float = SWING.TAIL
		var tl: float = t0 + (hd - t0) * maxf(0.0, (d - 1) / 4.0) if d < 3 else A[1] + (hd - A[1]) * minf(1.0, (d - 2) / 3.0)
		var al := 1.0 if d < 3 else 1 - (d - 2) / 5.0
		if tl != hd:
			var cnt := maxi(8, int(roundf(absf(hd - tl) / 2)))
			for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
				var col: Color = layer[0]
				col.a = al
				for i in cnt + 1:
					var u := float(i) / cnt
					var w0 := 5 * pow(u, 0.7)
					var w: float = w0 + layer[1]
					if w0 < 1 or w < 1:
						continue
					var p := _to_w(st, swing_pt(tl + (hd - tl) * u))
					px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))
	if _bl1() and gz < 0 and d >= 0 and d < 4:   # เขี้ยวแสง: โคนซ่อนใต้มือ ปลายแหลมเข้าตัวมอน
		var tp := _tip()
		var L: int = [30, 30, 22, 12][d]
		var hw: int = [4, 4, 3, 2][d]
		for layer in [[Color("#1a3a9a"), 1], [Color("#9ae6ff"), 0], [Color.WHITE, -1]]:
			for k in L + 9:
				var w := maxf(0.0, (hw + layer[1]) * minf(1.0, (L + 8 - k) / (L * 0.8)))
				if w < 0.6:
					continue
				px(n, tp.x + 8 - k, tp.y - w, layer[0], 1, maxi(1, int(roundf(w * 2))))
	if gz < 0 and d >= 3 and d < 12:   # แผล: bl1 = แนวนอนตามทางแทง · bl0 = ช่วงทางมีดที่ผ่านตัว
		var tp := _tip()
		var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 6.0)
		if _bl1():
			slash_line(n, tp.x + 6 + kb, tp.y - 1, tp.x - 9 + kb, tp.y + 1, 3, minf(1.0, (d - 2) / 2.0), al)
		else:
			var w0 := _to_w(geo(HIT), swing_pt(-150))
			var wk := tp + (tp - w0) * 0.25
			slash_line(n, w0.x + kb, w0.y, wk.x + kb, wk.y, 3, minf(1.0, (d - 2) / 2.0), al)
	if BM.get("generic", false) and gz < 0 and d >= 0 and d < 10:   # ท่าที่ยังไม่มีภาพ: รอยฟันตามขอบเขต (ในกรอบตัวมอน)
		var prog := minf(1.0, (d + 1) / 3.0)
		var al := 1.0 if d < 6 else 1 - (d - 5) / 5.0
		var mc := mx0 + mw / 2.0 + kb
		if ROWS[BM.to].scope != "single":   # กวาด: เสี้ยวแนวนอนผ่านกลางตัวจากขวาไปซ้าย + เศษลม
			_crescent(n, mc, my + mh * 0.25, mw * 0.62, 0.42, 25, 155, 6, prog, al)
			for i in 6:
				px(n, mc - mw * 0.55 - d * 4 - i * 5, my + mh * 0.5 + (i % 2) * 3, Color(1, 214 / 255.0, 90 / 255.0, maxf(0.0, 0.8 - d * 0.1)), 5, 1)
		else:   # ปาดไว: ปาดต่ำเฉียงขึ้นเร็ว
			slash_line(n, mc + mw * 0.35, my + mh * 0.82, mc - mw * 0.45, my + mh * 0.58, 4, prog, al)
	if BM.has("glim") and gz < 0 and d >= 0 and d < 8:   # ท่าใหม่ครั้งแรก: ดาวทอง + วงประกายทอง
		var tp := _tip()
		star_px(n, tp.x - 2, tp.y, 10 + d * 5, Color("#fff6a0"), Color("#ffb020"))
		for i in 16:
			var a := i * PI / 8
			var r := 6 + d * 4
			if fb_hash(i, d, 4) > 0.3:
				px(n, tp.x + cos(a) * r, tp.y + sin(a) * r * 0.8, Color("#fff6a0") if d < 4 else Color("#ffb020"), 2, 2)
	if BM.has("glim"):
		_glim_fx(n, f0, F0, st)

func _crescent(n: Node2D, cx: float, cy: float, R: float, sy: float, a0: float, a1: float, th: float, prog: float, al: float) -> void:   # pkCrescent
	var cnt := maxi(12, int(roundf(absf(a1 - a0) / 3)))
	var m := maxi(1, int(roundf(cnt * prog)))
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
		var col: Color = layer[0]
		col.a = al
		for i in m + 1:
			var u := float(i) / cnt
			var an := deg_to_rad(a0 + (a1 - a0) * u)
			var w: float = maxf(0.0, th * pow(sin(PI * minf(1.0, u / maxf(prog, 0.01) * prog)), 0.6) + layer[1])
			if w < 1:
				continue
			px(n, cx + cos(an) * R - w / 2, cy + sin(an) * R * sy - w / 2, col, ceil(w), ceil(w))

func sounds(F0: int) -> void:
	var mp := _map(F0)
	var gz: int = mp[1]
	if gz >= 0:   # เวลาหยุด = เสียงประกายอย่างเดียว
		_glim_sound(gz)
		return
	var F := int(mp[0])
	if BM.has("glim") and F0 == 100:   # ป้ายได้ท่าใหม่
		play_sfx("newtech", [T(0.18, "triangle", 1318, 1318, 0.1), T(0.3, "triangle", 1760, 1760, 0.08, 0.09)])
	var run_end: int = BM.CROUCH if _bl1() else HIT
	if F >= IDLE and F < run_end and (F - IDLE) % STEP == 0:
		var pk := snappedf(0.35 + 0.25 * (F - IDLE) / RUN, 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])   # ฝีเท้า
	if _bl1() and F == BM.CROUCH:
		play_sfx("brake", [N(0.18, "lowpass", 1600, 400, 0.35, 2)])   # เบรกลากเท้า
	if _bl1() and F == BM.LAUNCH:   # ถีบพื้น + ลมพุ่ง
		play_sfx("launch", [N(0.1, "lowpass", 600, 120, 0.6, 1)])
		sfx_release()
	if not _bl1() and F == HIT - 6:
		sfx_release()
	if F == HIT:
		sfx_hit(false)
		sfx_mon(false, 0.6 if foe == "B1" else 1.0)
	var t0 := HOP0
	for h in HOPS:
		if h.has("skid"):
			if F == t0:
				play_sfx("skid", [N(0.4, "lowpass", 1400, 300, 0.3, 2)])   # ลากเท้า
			t0 += h.skid
			continue
		if F == t0 + h.c:
			play_sfx("kick%s" % h.d, [N(0.06, "bandpass", 600, 1600, 0.15 + h.d * 0.3, 2)])   # ดีดตัว
		t0 += h.c + h.a
		if F == t0:
			play_sfx("land%s" % h.d, [N(0.09, "lowpass", 700, 150, 0.2 + h.d * 0.6, 1)])   # ลงพื้น
		t0 += h.l

## เวลาหยุด → ประกายขึ้นหัว → ติก ติก → ติ๊ง! → ภาพล่วงหน้าพุ่ง → แถบชื่อ → หลอดแตกเข้ามีด → พลังขึ้น (glimSound)
func _glim_sound(g: int) -> void:
	if g == 0:
		play_sfx("g0", [N(0.6, "lowpass", 2400, 90, 0.55, 1), T(0.7, "sine", 330, 82, 0.2)])
		duck()
	if g == 2:
		play_sfx("g2", [T(0.4, "triangle", 500, 1600, 0.07)])
	if g == 10 or g == 12:
		play_sfx("tick", [T(0.03, "square", 2600, 2600, 0.05, 0, 0.002, {"lp": 5000})])
	if g == 13:
		play_sfx("g13", [N(0.18, "highpass", 5000, 9000, 0.7, 6), T(0.12, "square", 1046, 2093, 0.12, 0, 0.002, {"lp": 4000}),
			T(0.6, "triangle", 1318, 1318, 0.13), T(0.7, "triangle", 1976, 1976, 0.09, 0.07), T(0.9, "sine", 2637, 2637, 0.05, 0.14)])
	if g == 15:
		play_sfx("g15", [N(0.25, "bandpass", 900, 3200, 0.3, 2)])
		sfx_release()
	if g == 17:
		play_sfx("g17", [N(0.22, "highpass", 1200, 5000, 0.25, 1)])
	if g == 27:
		play_sfx("g27", [N(0.16, "highpass", 4000, 9000, 0.45, 4)])
	if g == P - 3:
		play_sfx("gup", [T(0.35, "sawtooth", 180, 900, 0.07, 0, 0.004, {"lp": 2400})])
