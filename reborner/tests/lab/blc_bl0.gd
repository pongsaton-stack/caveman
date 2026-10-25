extends "res://tests/lab/lab_stage.gd"
## ฟัน bl0 ใน Godot — ย้ายจากหน้าเว็บ blc_bl0 (blcKey/blcState/blcView/blcSound ใน tools/web/anim_test.tpl.html)
## ยืนในศึก → วิ่งเข้า (ฝุ่น) ง้างระหว่างวิ่ง → ฟันตอนถึงตัว (หยุดภาพ) → ไถลตามแรง → กระโดดถอย 2 สเตป + ไถลตั้งหลัก → ยืนในศึก
## มอนยืนที่ x 74 (PKV.MX ของหน้าเว็บ) · Rion เริ่มที่ W−100

const MX := 74
const IDLE := 18
const RUN := 18
const HIT := 36
const HOP0 := 44
const END := 100
const STEP := 3
const SLIDE := 7
const REACH := 25
const KB := 6
## สเตปกระโดดถอย: ระยะ (สัดส่วน) · ย่อ · ลอย · ลง · สูง · skid = ไถลถอยตั้งหลัก
const HOPS := [{"d": 0.5, "c": 2, "a": 9, "l": 2, "h": 16}, {"d": 0.3, "c": 2, "a": 7, "l": 0, "h": 12}, {"d": 0.2, "skid": 10}]

var start := 0.0
var near := 0.0
var art_lift := {}

func tech_id() -> String: return "bl0"
func end_frame() -> int: return END
func stops() -> Array: return [[HIT, 0.12]]
func caption() -> String: return "ยืนในศึก → วิ่ง → ฟัน (bl0) → กระโดดถอย"

func setup() -> void:
	place_monster(MX)
	start = W - 100
	near = mx0 + mw - 17 - REACH

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

## ตำแหน่ง Rion (blcState) · cx = กลางผืน · f ทศนิยม = เลื่อนต่อเนื่อง
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var b := {"cx": start, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": _key(F), "flip": false}
	var stop := near - SLIDE
	if F < IDLE:
		b.sy = 1 - 0.015 * (posmod(F / 4, 2))
	elif F < HIT:
		var u := (f - IDLE) / RUN
		b.cx = start + (near - start) * (u * u * 0.4 + u * 0.6)   # เร่งออกตัว
		b.lean = -0.04 * minf(1.0, u * 3)
	elif F < HOP0:
		var q := f - HIT
		b.cx = near - SLIDE * (1 - pow(1 - minf(1.0, q / 6.0), 2))   # ไถลตามแรง
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

func frame(f: float, F: int, fresh: bool) -> void:
	var d := F - HIT
	shake(F, 2.5 * (1 - d / 5.0) if d >= 0 and d < 5 else 0.0)
	var g := geo(f)
	# มอน: ยืนหายใจ → วาบขาว 2 · ผงะ 10 · กระเด็นถอย 6 แล้วกลับ
	var kb := roundf(-KB * maxf(0.0, 1 - maxf(0.0, d - 2) / 10.0)) if d >= 0 else 0.0
	show_mon(hurt_key() if d >= 0 and d < 10 else idle_key(f), kb, 1.0 if d >= 0 and d < 2 else 0.0)
	# Rion + ร่างติดตาตอนวิ่งง้าง / สเตปแรก
	set_rion(rion, g)
	if F > HIT - 8 and F < HIT:
		for k in [2, 1]:
			ghost(geo(f - k), 0.15 * (4 - k))
	for k in [2, 1]:
		var hp := _hop(F - k)
		if not hp.is_empty() and hp.k == 0 and hp.q >= hp.h.c and hp.q < hp.h.c + hp.h.a:
			ghost(geo(f - k), 0.12 * (3 - k))
	# ฝุ่น: ทุกก้าว (ใหญ่ขึ้นตามความเร็ว) · ไถลหลังฟาด · ถีบ/ลงทุกสเตป
	if fresh:
		if F >= IDLE and F < HIT and (F - IDLE) % STEP == 0:
			dust_at(g.cx + 6, 1.0, 0.45 + 0.4 * (F - IDLE) / RUN)
		if F == HIT:
			dust_at(g.cx + 6, 1.0, 1.3)
			burst(_tip(), F, Color("#9ae6ff"))
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
	if d >= 0 and d < 14:
		word("ฉัวะ!", maxf(4, mx0 + kb + mw / 2.0 - 14), maxf(16, my - 8 - mini(5, d)))
	if F >= HIT - 10 and F < HIT + 8:
		show_bubble("ฟัน!", g.cx, G - g.lift - 74, F - (HIT - 10), 1.0 if F < HIT + 4 else (HIT + 8 - f) / 4.0)
	else:
		show_bubble("", 0, 0, 0, 0.0)
	pop(dmg, maxf(16, mx0 + kb - 8), my + roundf(mh * 0.25), d, Color.WHITE, aff_tag(), aff_col())

## ปลายมีดในฉาก ณ ภาพฟาด (มุม A[1]) ของท่าตอนกระทบ
func _tip() -> Vector2:
	return _to_w(geo(HIT), swing_pt(SWING.A[1]))

func _to_w(s: Dictionary, p: Vector2) -> Vector2:   # จุดในผืน → ฉาก (เอน/ยืดตามตัว)
	var l := Vector2((p.x - 60) * s.sx, (p.y - 108) * s.sy).rotated(s.lean)
	return Vector2(s.cx, G - s.lift) + l

func draw_fx(n: Node2D) -> void:
	var F := int(floor(t / SEC))
	var d := F - HIT
	var st := geo(t / SEC)
	var kb := roundf(-KB * maxf(0.0, 1 - maxf(0.0, d - 2) / 10.0)) if d >= 0 else 0.0
	if d >= 0 and d < 7:   # รอยไถล
		for i in 6:
			px(n, near + 30 + i * 4 + d * 2, G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)
	if st.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - st.lift / 40.0):
				px(n, st.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	# รอยมีดติดตัว: หัวรอย = ปลายมีดของภาพที่แสดง · หางเริ่มหน้าหมวกแล้วกินตามหัว · จางใน 7 เฟรม (blcTrail 3 ชั้น)
	if d >= 0 and d < 7:
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
	# แผล = ช่วงทางมีดที่ผ่านตัวมอน ต่อเลยปลายมีดเล็กน้อย
	if d >= 3 and d < 12:
		var sh := geo(HIT)
		var tip := _to_w(sh, swing_pt(SWING.A[1]))
		var w0 := _to_w(sh, swing_pt(-150))
		var wk := tip + (tip - w0) * 0.25
		slash_line(n, w0.x + kb, w0.y, wk.x + kb, wk.y, 3, minf(1.0, (d - 2) / 2.0), 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 6.0))

func sounds(F: int) -> void:
	if F >= IDLE and F < HIT and (F - IDLE) % STEP == 0:
		var pk := snappedf(0.35 + 0.25 * (F - IDLE) / RUN, 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])   # ฝีเท้า
	if F == HIT - 6:
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
