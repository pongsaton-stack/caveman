extends "res://tests/lab/lab_stage.gd"
## เขี้ยวผ่าเกราะ bl8 แบบคาบูโตะวาริใน Godot — ย้ายจากหน้าเว็บ kw_bl8 (kwGeo/kwCracks/kwView/kwSound)
## วิ่งกระโดดจามระดับหัว มีดฝังเกราะ ปล่อยมือ → กระโดดส้นเท้ากระทืบด้ามมีดตอกเป็นลิ่ม → ร้าวทั่วตัว → เกราะแตกกระจาย → ดึงมีดตีลังกากลับ
## ภาพมือเปล่า pls_nk_* (มีดค้างในเกราะวาดด้วยโค้ด) · มอนยืนที่ x 74 (PKV.MX)

const MX := 74
const END := 96
const RUN := 14
const JUMP := 22
const WIND := 24
const CHOP := 29
const LET := 31
const LANDA := 35
const UP := 38
const PEAK := 42
const DROP := 44
const DRIVE := 46
const BREAK := 54
const LAND := 70
const BY_MIN := 70   # ด้ามมีดสูงกว่านี้ = กระโดดกระทืบแล้วหัวหลุดขอบบน
const HARD := ["เกราะ", "หิน", "กระดูก", "กลไก"]   # ร่างแข็ง = เกราะแตกเป็นเศษ · ที่เหลือ = ก้อนเนื้อกระเซ็น

var bx := 0.0
var by := 0.0
var near := 0.0
var chop_lift := 0.0
var tip_up := 0.0
var u := Vector2.ZERO
var hard := false
var cracks: Array = []

func tech_id() -> String: return "bl8"
func end_frame() -> int: return END
func stops() -> Array: return [[CHOP, 0.08], [DRIVE, 0.1], [BREAK, 0.1]]
func caption() -> String: return "ผ่าเกราะ: จามระดับหัว มีดฝังเป็นลิ่ม → กระทืบด้าม → ร้าว → แตก → ตีลังกากลับ"

func setup() -> void:
	place_monster(MX)
	hard = body in HARD
	var sw := swing_pt(SWING.A[1])
	tip_up = 108 - roundf(sw.y)
	by = maxf(BY_MIN, minf(G - tip_up, roundf(G - bh + maxf(6, bh * 0.22))))   # จุดจาม = หน้าผาก/หมวก
	var edge := mx0 + roundf(mw * 0.8)
	var row := clampi(int(by - (G - mh)), 0, mh - 1)
	for x in range(mw - 1, -1, -1):   # ขอบหน้าตัวมอนที่ระดับจุดจาม
		if solid(x, row):
			edge = mx0 + x
			break
	bx = edge - 3
	near = roundf(bx - (sw.x - 60))
	chop_lift = maxf(0, G - tip_up - by)
	var a := deg_to_rad(SWING.A[1])
	u = Vector2(cos(a), sin(a))   # ทิศมีดชี้เข้าตัว
	for b in 6:   # รอยร้าว 6 กิ่งเดินสุ่ม (seed คงที่) จากปลายมีด
		var x := 0.0
		var y := 0.0
		var an := PI * (0.55 + b * 0.27) + (fb_hash(b, 3, 1) - 0.5) * 0.5
		var pts := [[0.0, 0.0, 0]]
		for s in 26:
			an += (fb_hash(b, s, 2) - 0.5) * 0.9
			x += cos(an) * 2
			y += sin(an) * 2
			pts.append([x, y, 0])
			if s == 8 + (b % 3) * 3:
				var x2 := x
				var y2 := y
				var a2 := an + (0.9 if fb_hash(b, s, 5) > 0.5 else -0.9)
				for k in 7:
					a2 += (fb_hash(b, k, 6) - 0.5) * 0.6
					x2 += cos(a2) * 2
					y2 += sin(a2) * 2
					pts.append([x2, y2, 1])
		cracks.append(pts)

func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "rot": 0.0, "sx": 1.0, "sy": 1.0, "flip": false}
	if F < RUN:
		return r
	var x0 := near + 30   # จุดกระโดด (วิ่งเร่งมาถึงแล้วถีบขึ้นเลย)
	if F < JUMP:
		var tt := (f - RUN + 1) / (JUMP - RUN)
		r.cx = home + (x0 - home) * (tt * tt * 0.4 + tt * 0.6)
		r.key = "pls_run_bl_%d" % ((F - RUN) % 6)
		return r
	if F < CHOP:   # โค้งพาราโบลา ยอดเหนือจุดจาม · ง้างกลางอากาศ
		var tt := (f - JUMP + 1) / (CHOP - JUMP)
		var h4 := chop_lift + 34
		r.cx = x0 + (near - x0) * tt
		r.lift = roundf(chop_lift * tt + h4 * tt * (1 - tt))
		r.key = "pls_hop_bl_2" if F < JUMP + 1 else ("pls_hop_bl_3" if F < WIND else "pls_atk_bl_%d" % mini(4, 1 + F - WIND))
		return r
	if F < LET:   # จามฝัง
		r.cx = near
		r.lift = chop_lift
		r.key = "pls_atk_bl_5"
		r.sy = 0.95
		r.sx = 1.04
		return r
	if F < LANDA:   # ปล่อยมือ มีดค้างในเกราะ · ตกลงพื้น
		var tt := (f - LET + 1) / (LANDA - LET)
		r.cx = near + 5 * tt
		r.lift = roundf(chop_lift * (1 - tt * tt))
		r.key = "pls_nk_atk_bl_6" if F < LET + 2 else "pls_nk_atk_bl_7"
		return r
	var sx0 := near + 5
	var hx := bx - u.x * 10
	var hy := by - u.y * 10
	var knee_x := roundf(hx - 12)
	var top_y := G - 12 - roundf(hy) + 2   # ส้นบูทภาพขดตัวลงตรงด้าม
	if F < UP:
		r.cx = sx0
		r.key = "pls_nk_hop_bl_1"
		r.sy = 0.9 if F == LANDA else 0.94
		return r
	var top := minf(86, maxf(top_y + 26, 44))
	if F < DROP:   # ถีบขึ้นสูงเหนือด้าม (ชะลอที่ยอด)
		var tt := (f - UP + 1) / (DROP - UP)
		var e := 1 - (1 - tt) * (1 - tt)
		r.cx = sx0 + (knee_x - sx0) * e
		r.lift = roundf(top * e)
		r.key = "pls_nk_hop_bl_2" if F < UP + 2 else ("pls_nk_hop_bl_3" if F < PEAK else "pls_nk_hop_bl_4")
		return r
	if F < DRIVE:   # ดิ่งลงเร่งเต็มที่
		var tt := (f - DROP + 1) / (DRIVE - DROP + 1)
		r.cx = knee_x
		r.lift = roundf(top + (top_y - top) * tt * tt)
		r.key = "pls_nk_hop_bl_4"
		r.sy = 1.06
		r.sx = 0.96
		return r
	if F < BREAK:   # ส้นกระทืบด้าม · ค้างกดลิ่มจนร้าวทั่ว
		var q := F - DRIVE
		r.cx = knee_x
		r.lift = top_y - (0 if q < 3 else mini(2, q - 2))
		r.key = "pls_nk_hop_bl_4"
		r.sy = 0.88 if q < 3 else 0.92
		r.sx = 1.08 if q < 3 else 1.05
		return r
	if F < LAND:   # ดึงมีดออกตอนเกราะแตก แล้วตีลังกาหลังกลับที่
		var tt := (f - BREAK + 1) / (LAND - BREAK)
		var e := tt * tt * (3 - 2 * tt)
		r.cx = knee_x + (home - knee_x) * tt
		r.lift = roundf(top_y * (1 - tt) + 4 * maxf(10, minf(46, 86 - top_y / 2)) * tt * (1 - tt))
		r.key = "pls_hop_bl_4"
		r.rot = TAU * e
		return r
	r.cx = home
	if F < LAND + 2:
		r.key = "pls_hop_bl_1"
		r.sy = 0.94
	return r

func _kb(F: int) -> float:
	var dd := F - DRIVE
	var db := F - BREAK
	return -roundf(10 * maxf(0.0, 1 - maxf(0.0, db - 2) / 12.0)) if db >= 0 else (-1.0 if dd >= 0 and dd < 4 else 0.0)

func frame(f: float, F: int, fresh: bool) -> void:
	var dc := F - CHOP
	var dd := F - DRIVE
	var db := F - BREAK
	shake(F, 1.5 * (1 - dc / 4.0) if dc >= 0 and dc < 4 else (4.0 * (1 - dd / 7.0) if dd >= 0 and dd < 7 else (3.0 * (1 - db / 6.0) if db >= 0 and db < 6 else 0.0)))
	dim_to(0.2 if dd >= 0 and db < 4 else (0.1 if F >= UP and dd < 0 else 0.0))
	# มอน: ผงะตอนจาม · ตอนตอกยุบรับแรง · เกราะแตกกระเด็นถอย
	var hurt := (dc >= 0 and dc < 6) or (dd >= 0 and dd < 4) or (db >= 0 and db < 10)
	# วาบขาวตัวมอน 2 ครั้ง (จาม/แตก) · ตอนตอกไม่วาบ ใช้ยุบตัว+จอสั่นแทน (ตรวจแสงวาบรอบ 2: เดิม 3 ครั้งใน 17 เฟรม = แตะเพดาน)
	var fl := 1.0 if (dc >= 0 and dc < 2) or db == 0 else 0.0
	var squash := (0.88 if body == "นุ่ม" else 0.94) if dd >= 0 and dd < 3 else 1.0   # ร่างนุ่มยุบลึกกว่า (ตารางปฏิกิริยา)
	show_mon(hurt_key() if hurt else idle_key(f), _kb(F), fl, Color.WHITE, 1.0, squash)
	var g := geo(f)
	set_rion(rion, g)
	if F >= DROP and F <= DRIVE:
		for k in [2, 1]:
			ghost(geo(f - k), 0.18 * (3 - k), Color("#9ae6ff"), 1.0)
	if (F > JUMP and F <= CHOP) or (F > BREAK and F < LAND - 4):
		for k in [2, 1]:
			ghost(geo(f - k), 0.12 * (3 - k))
	if fresh:
		for e in [[JUMP, near + 34, 1.0, 1.1], [LANDA, near + 5, -1.0, 0.9], [UP, near + 6, 1.0, 1.1], [LAND, float(home), 1.0, 1.0]]:
			if F == e[0]:
				dust_at(e[1], e[2], e[3])
		if F >= RUN + 2 and F < JUMP and (F - RUN - 2) % 3 == 0:
			dust_at(g.cx + 4, 1.0, 0.5 + 0.4 * (F - RUN) / 12.0)
		if F == CHOP:   # เศษตามวัสดุ: เกราะ = ประกาย+เปลือก · นุ่ม = เจล · ปีก = ขนนก · เนื้อ = เลือดหยด
			debris_at(Vector2(bx, by), "คม", F)
		if F == DRIVE:
			burst(Vector2(bx + _kb(F) - u.x * 10, by - u.y * 10), F)
		if F == BREAK:
			burst(Vector2(bx + _kb(F), by - 4), F, Color("#ffd24a") if hard else Color("#ff8a7a"))
	if dc >= 0 and dc < 10:
		word("แก๊ง!", minf(W - 40, bx + 8), maxf(18, by - 14 - mini(4, dc)))
	if dd >= 0 and dd < 8:
		word("ตอก!!", maxf(4, bx - 46), maxf(18, by - 30 - mini(4, dd)), Color("#ffd24a"))
	if db >= 0 and db < 16:
		word("เพล้ง!!" if hard else "ปึ้ก!!", maxf(4, mx0 - 4), maxf(18, minf(G - mh - 4, G - roundf(mh * 0.75) - 34) - mini(5, db)))   # มอนตัวเล็ก: อยู่เหนือตัวเลข ไม่ทับ
	show_bubble("เขี้ยวผ่าเกราะ!", g.cx, maxf(14, G - g.lift - 74), F - WIND + 2, (1.0 if F < CHOP else (CHOP + 3 - f) / 3.0) if F >= WIND - 2 and F < CHOP + 3 else 0.0)
	var tag := ("อ่อนแอ! · " if aff > 0 else "ต้านทาน · " if aff < 0 else "") + "เจาะเกราะ 30%"
	pop(dmg, maxf(52, mx0 + 8), G - roundf(mh * 0.75), db, Color.WHITE, tag, Color("#ffe08a") if aff > 0 else Color("#c8e6ff"))

## ชั้นกลาง (ทับมอน ใต้ Rion): รอยร้าว (เฉพาะร่างแข็ง) / รอยแผลตามแนวมีด (ร่างอื่น) · มีดฝัง
func draw_mid(n: Node2D) -> void:
	var F := int(floor(t / SEC))
	var dc := F - CHOP
	var dd := F - DRIVE
	var db := F - BREAK
	var kb := _kb(F)
	var grow := 0.0 if dc < 0 else (0.12 if dd < 0 else (0.12 + 0.88 * minf(1.0, (dd + 1) / 6.0) if db < 0 else 1.0))
	var fade := 1.0 if db < 6 else maxf(0.0, 1 - (db - 6) / 24.0)
	if grow > 0 and fade > 0 and not hard:   # ร่างนุ่ม/เนื้อ/ปีก ไม่ร้าว: แผลเปิดตามแนวมีด ยาวขึ้นตอนตอก แล้วประกบจาง
		for k in int(roundf(3 + 9 * grow)):
			var p := Vector2(bx + kb, by) + u * k
			var sx := int(roundf(p.x - kb - mx0))
			var sy := int(roundf(p.y - (G - mh)))
			if not solid(sx, sy):
				continue
			var c := rgb(sx, sy).darkened(0.6)
			c.a = 0.9 * fade
			px(n, p.x, p.y, c)
			px(n, p.x, p.y + 1, Color(c, 0.5 * fade))
	if grow > 0 and fade > 0 and hard:
		var ox := bx - mx0
		var oy := by - (G - mh)
		for br in cracks:
			var cnt := int(roundf(br.size() * grow))
			for i in cnt:
				var p: Array = br[i]
				var pxx := int(roundf(ox + p[0]))
				var pyy := int(roundf(oy + p[1]))
				if not solid(pxx, pyy):
					continue
				var lit := db < 0 and dd >= 0 and i > cnt - 4   # ปลายรอยที่กำลังวิ่ง = เส้นแสง
				var col := Color(1, 236 / 255.0, 160 / 255.0, fade) if lit else Color(26 / 255.0, 16 / 255.0, 12 / 255.0, 0.85 * fade)
				px(n, mx0 + kb + pxx, G - mh + pyy, col)
				if i > 0 and (p[2] == 0) == (br[i - 1][2] == 0):
					px(n, mx0 + kb + roundf(ox + (p[0] + br[i - 1][0]) / 2), G - mh + roundf(oy + (p[1] + br[i - 1][1]) / 2), col)
				if p[2] == 0 and i % 3 == 0 and i < cnt - 2:
					px(n, mx0 + kb + pxx + 1, G - mh + pyy, Color(1, 1, 1, 0.25 * fade))
	if F >= LET and F < BREAK:   # มีดฝัง: ใบจม เห็นสัน + ด้าม · ตอกแล้วจมอีก 2 จุด
		var sink := 0 if dd < 0 else mini(2, 1 + (dd >> 1))
		for k in range(1, 15):
			var p := Vector2(bx + kb, by) - u * (k - sink)
			px(n, p.x, p.y - 1, Color("#2a1a14"), 1, 3)
			if k <= 6:
				px(n, p.x, p.y, Color("#c8ced4"))
				px(n, p.x, p.y - 1, Color("#f4f6f8"))
			elif k <= 13:
				px(n, p.x, p.y, Color("#6a3c22"))

## ชั้นหน้า: เงา · เส้นความเร็วดิ่ง · ประกายตอนจาม · วงแรงตอนตอก · เศษเกราะ · จอวาบ
func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var dc := F - CHOP
	var dd := F - DRIVE
	var db := F - BREAK
	var kb := _kb(F)
	var g := geo(f)
	if g.lift > 2:
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.35, 1 - g.lift / 90.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	if F >= DROP and F < DRIVE:
		for i in 5:
			for s in 10 + roundf(fb_hash(i, F, 2) * 10):
				px(n, g.cx - 8 + i * 4, G - g.lift - 70 - s, Color(230 / 255.0, 248 / 255.0, 1, 0.6))
	if dc >= 0 and dc < 5:   # จาม: ประกายเหล็ก + ดาวเล็ก (เกราะรับไว้ ไม่ทะลุ)
		star_px(n, bx, by, 4 + dc * 2, Color.WHITE, Color("#ffd24a"))
		for i in 8:
			var a := PI * (1.1 + fb_hash(i, 1, 1) * 0.9)
			var v := 2 + fb_hash(i, 1, 2) * 2
			px(n, bx + cos(a) * v * dc, by + sin(a) * v * dc + 0.3 * dc * dc, Color.WHITE if dc < 3 else Color("#ffd24a"))
	if dd >= 0 and dd < 6:   # ตอก: วงแรงกระแทกจากด้าม + เส้นแรงลงตามแนวมีด
		var h := Vector2(bx + kb - u.x * 10, by - u.y * 10)
		for i in 20:
			var a := i * PI / 10
			var r := 6 + dd * 5
			if fb_hash(i, dd, 3) > 0.25:
				px(n, h.x + cos(a) * r, h.y + sin(a) * r * 0.6, Color(1, 1, 1, 1 - dd / 6.0), 2, 1)
		for s in 18:
			px(n, bx + kb + u.x * s, by + u.y * s, Color(1, 236 / 255.0, 160 / 255.0, 1 - dd / 6.0), 2, 2)
	if db >= 0 and db < 34:   # แตก: เศษเกราะ (สีจากตัวมอน) กระเด็นไปซ้าย-บน ตกกระดอนพื้น · ร่างนุ่ม = ก้อนกลม
		for i in 36:
			var sx0 := int(roundf(bx - mx0 + (fb_hash(i, 1, 4) - 0.65) * mw * 0.8))
			var sy0 := int(roundf(by - (G - mh) + (fb_hash(i, 2, 4) - 0.7) * mh * 0.8))
			if not solid(sx0, sy0):
				continue
			var col := rgb(sx0, sy0)
			var vx := -(0.8 + fb_hash(i, 3, 4) * 2.6) + (3.0 if fb_hash(i, 5, 4) < 0.2 else 0.0)
			var vy := -(1.4 + fb_hash(i, 4, 4) * 2.8)
			var x := mx0 + kb + sx0 + vx * db * 1.5
			var y := G - mh + sy0 + vy * db * 1.5 + 0.18 * db * db
			if y > G - 2:
				y = G - 2 - absf(sin(db * 0.7)) * maxf(0, 6 - (db - 8)) * 0.5
				x = maxf(4, x)
			var al := maxf(0.0, 1 - maxf(0.0, db - 22) / 12.0)
			var s := 2 + (i % 3)
			col.a = al
			if hard:
				px(n, x, y, Color(42 / 255.0, 26 / 255.0, 20 / 255.0, al), s + 1, s + 1)
				px(n, x, y, col, s, s)
				px(n, x, y, Color(1, 240 / 255.0, 210 / 255.0, 0.8 * al))
			else:
				disc(n, x, y, s * 0.7, col)
	if db >= 0 and db < 2:   # จอวาบ (ลดจาก 0.22 → 0.15 ตามตรวจแสงวาบรอบ 2)
		px(n, -8, -8, Color(1, 1, 1, (1 - db / 2.0) * 0.15), W + 16, H + 16)

func sounds(F: int) -> void:
	var big := 0.6 if foe == "B1" else 1.0
	if F >= RUN and F < JUMP and (F - RUN) % 3 == 1:
		play_sfx("step", [N(0.05, "lowpass", 900, 200, 0.18, 1)])
	if F == JUMP:
		play_sfx("jump", [N(0.08, "lowpass", 700, 150, 0.35, 1)])
	if F == LANDA:
		play_sfx("landa", [N(0.08, "lowpass", 600, 140, 0.32, 1)])
	if F == WIND + 2:
		sfx_release()
	if F == CHOP:   # แก๊ง: เหล็กกระทบเกราะ ก้อง
		play_sfx("clang", [T(0.18, "square", 2400, 1900, 0.12, 0, 0.002, {"lp": 6000}), T(0.5, "triangle", 3100, 2900, 0.05, 0.01), N(0.05, "highpass", 3000, 6000, 0.4, 2)])
		sfx_mon(false, big)
	if F == UP:
		play_sfx("up", [N(0.08, "lowpass", 700, 150, 0.35, 1), N(0.25, "bandpass", 600, 1800, 0.18, 2, 0.04)])
	if F == DROP:
		play_sfx("drop", [N(0.12, "bandpass", 800, 2600, 0.22, 2)])
	if F == DRIVE:   # ตอก: กระแทกหนัก + เหล็กครวญ
		play_sfx("drive", [N(0.2, "lowpass", 500, 80, 0.8, 1), T(0.12, "sine", 140, 50, 0.4), T(0.6, "triangle", 1800, 1700, 0.06, 0.01)])
		duck()
	if F > DRIVE and F < BREAK and (F - DRIVE) % 2 == 1:   # ร้าวไต่
		play_sfx("crack%d" % F, [N(0.05, "highpass", 2500 + (F - DRIVE) * 300, 5000, 0.16 + 0.03 * (F - DRIVE), 3)])
	if F == BREAK:   # เพล้ง: เกราะแตกกระจาย
		play_sfx("break%s" % hard, [N(0.6, "highpass", 2200 if hard else 900, 6000 if hard else 2000, 0.6, 1), N(0.25, "lowpass", 400, 70, 0.7, 1)])
		sfx_mon(false, big)
		duck()
	if F == BREAK + 2:
		play_sfx("flipwind", [N(0.25, "bandpass", 600, 1800, 0.18, 2)])
	if hard and F > BREAK + 8 and F < BREAK + 20 and (F - BREAK) % 4 == 0:   # เศษตกพื้น
		play_sfx("bit%d" % F, [T(0.04, "square", 1500 + fb_hash(F, 1, 1) * 1500, 900, 0.04)])
	if F == LAND:
		play_sfx("land", [N(0.09, "lowpass", 700, 150, 0.4, 1)])
