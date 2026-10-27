extends "res://tests/lab/row_base.gd"
## วงล้อ bl4 ★ (kwan 27 ต.ค. "ทำ วงล้อต่อ ขออลังการหน่อย") — ตามรายงานวิจัยท่า R2 (กระบี่กระบอง ดาบหมุนรอบตัว) ขยายเป็นไม้ตาย
## วิ่งเข้า (จอมืด · แถบภาพยนตร์ · ออร่า · ง้างระหว่างวิ่ง) → กระโดดขึ้นเหนือแถวแล้วหมุนตัวกลางอากาศ = ดุมล้อ
## → ใบคม 6 ใบเป็นขอบล้อวนรอบทั้งแถว มีซี่แสงต่อจากดุม · ใบผ่านตัวไหนบาดตัวนั้น (ยังไม่ขึ้นตัวเลข) · ลมยกมอนลอยเล็กน้อย
## → ดิ่งฟาดลงพื้น: วงล้อแตก ใบคมกระเด็นออก คลื่นกระแทกบนพื้น เสาแสงผ่าทุกตัว ตัวเลขขึ้นพร้อมกัน → ค้างท่า → กระโดดถอยแบบท่าฟัน
## ภาพ Rion ประกอบจากภาพที่มีอยู่ (ยังไม่เจนใหม่): วิ่ง pls_run_bl · ง้าง pls_atk_bl_1–4 · หมุน pls_spin_bl_0–3 · ดิ่ง pls_bl9_2 + pls_atk_bl_4–7

const RUN0 := 18     # เริ่มวิ่ง
const LEAP := 30     # ถึงหน้าแถว กระโดด
const RING0 := 34    # ใบคมกางออกจากตัว
const RING1 := 40    # วงล้อกางเต็ม
const RISE := 58     # หยุดหมุน ยกมีดเหนือหัว
const SLAM := 64     # ฟาดถึงพื้น = วงล้อแตก (ดาเมจ)
const HOLD1 := 76    # ค้างท่าถึงเฟรมนี้ แล้วเข้ากระโดดถอยของเครื่องฟัน
const WAIST := 22    # ระดับวงล้อเหนือพื้น
const BLADES := 6

var x_home := 0.0
var x_jump := 0.0
var x_land := 0.0
var hub := Vector2.ZERO      # จุดหมุน Rion (กลางผืน · ยกจากพื้น)
var ring_c := Vector2.ZERO
var ring_r := Vector2.ZERO
var cuts: Array = []         # cuts[i] = เฟรมที่ใบคมผ่านหน้ามอนตัว i
var lift_m := false          # ลมยกมอนได้ไหม (ไม่ใช่บอส/ร่างแข็ง)

func mv() -> Dictionary:
	return {"id": "bl4", "slide": 0, "reach": 0, "kb": 6, "shk": 4.0, "sfx": "ฉัวะ!!!", "what": "วงล้อ (bl4)"}

func end_frame() -> int: return HOLD1 + END - HOP0
func stops() -> Array: return [[SLAM, 0.14]]
func caption() -> String: return "★ วิ่งเข้า → หมุนกลางอากาศ วงล้อคม 6 ใบพันทั้งแถว → ดิ่งฟาด วงล้อแตก → กระโดดถอย"

func setup() -> void:
	super.setup()
	var vis := float(mh - top0)   # ความสูงที่เห็นจริงของมอน
	if _count() == 1:
		setup_row(mw * 0.5 + 40, 0.62, mw * 0.5 + 40)
		ring_r = Vector2(mw * 0.5 + 16, 20)
		hub = Vector2(cxs[0] + mw * 0.5 + 6, 36)   # บอส: หมุนหน้าตัวบอส ไม่ลอยข้ามหัว
	else:
		setup_row(mw * 0.5 + 14)
		ring_r = Vector2((cxs[0] - cxs[2]) * 0.5 + mw * 0.5 + 10, 0)
		ring_r.y = clampf(ring_r.x * 0.2, 14, 22)
		hub = Vector2((cxs[0] + cxs[2]) * 0.5, clampf(vis + 8, 40, 72))   # ลอยเหนือหัวกลางแถว
	ring_c = Vector2((cxs[0] + cxs[cxs.size() - 1]) * 0.5, G - WAIST)
	lift_m = _count() > 1 and not hard_body()
	x_home = start + 60
	x_jump = cxs[0] + mw * 0.5 + 10
	x_land = cxs[0] + mw * 0.5 + 20
	near = x_land + 6 - 60   # จุดเริ่มกระโดดถอยของเครื่องฟัน = หลังไถลจากจุดลง
	cuts.clear()
	for i in cxs.size():
		cuts.append([])
		for F in range(RING1, SLAM):
			for k in BLADES:
				var ai := _front_angle(i, float(F))
				var a0 := _rot(F - 1.0) + k * TAU / BLADES - ai
				var a1 := _rot(float(F)) + k * TAU / BLADES - ai
				if floor(a1 / TAU) > floor(a0 / TAU) and not cuts[i].has(F):
					cuts[i].append(F)

# ── เวลาและรูปทรงของวงล้อ ─────────────────────────
## มุมหมุนของวงล้อ (เร่งขึ้นเรื่อยๆ ~2.7 รอบ) · มุม 0 = ขวา · เพิ่มขึ้น = ผ่านหน้าแถวจากขวาไปซ้าย
func _rot(f: float) -> float:
	var q := clampf(f, RING0, SLAM + 6.0) - RING0
	return 0.16 * q + 0.016 * q * q

## ขนาดวงล้อ 0–1: กางออก (ease out) → เต็ม → บีบแน่นขึ้นก่อนฟาด
func _scale(f: float) -> float:
	if f < RING0:
		return 0.0
	if f < RING1:
		var u := (f - RING0) / (RING1 - RING0)
		return 0.15 + 0.85 * (1 - pow(1 - u, 3))
	if f < RISE:
		return 1.0
	return 1.0 - 0.12 * minf(1.0, (f - RISE) / (SLAM - RISE))

## ศูนย์กลางวงล้อ: เริ่มที่ดุม (ตัว Rion) แล้วลงไปรอบเอวแถว
func _center(f: float) -> Vector2:
	var hc := Vector2(hub.x, G - hub.y - 36)
	if f >= RING1:
		return ring_c
	var u := clampf((f - RING0) / (RING1 - RING0), 0.0, 1.0)
	return hc.lerp(ring_c, 1 - pow(1 - u, 2))

func _pt(a: float, f: float) -> Vector2:
	var s := _scale(f)
	return _center(f) + Vector2(cos(a) * ring_r.x * s, sin(a) * ring_r.y * s)

## มุมหน้าแถว (ครึ่งหน้า 0–π) ที่ตรงกลางตัวมอน i
func _front_angle(i: int, f: float) -> float:
	var rx := ring_r.x * maxf(0.2, _scale(f))
	return acos(clampf((cxs[i] - ring_c.x) / rx, -1.0, 1.0))

## เฟรมนับจากใบคมผ่านตัว i ล่าสุด (−1 = ยังไม่ผ่าน)
func _cut_d(i: int, F: int) -> int:
	var last := -1
	for c in cuts[i]:
		if c <= F:
			last = c
	return F - last if last >= 0 else -1

## มุมหมุนตัว Rion (รอบ) · 4 ภาพ: ซ้าย หลัง ขวา หน้า
func _spin(f: float) -> float:
	var q := f - (LEAP + 2)
	return 0.11 * q + 0.006 * q * q

# ── ตำแหน่ง Rion ─────────────────────────────────
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < RUN0:
		return super.geo(f)
	if F >= HOLD1:
		return super.geo(f - HOLD1 + HOP0)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false}
	if F < LEAP:   # วิ่งเร่งเข้า · ง้าง 6 เฟรมท้ายระหว่างวิ่ง
		var u := (f - RUN0) / (LEAP - RUN0)
		b.cx = x_home + (x_jump - x_home) * (u * u * 0.5 + u * 0.5)
		b.lean = -0.07 * minf(1.0, u * 2)
		b.key = "pls_run_bl_%d" % ((F - RUN0) % 6) if F < LEAP - 6 else "pls_atk_bl_%d" % (1 + mini(3, (F - (LEAP - 6)) / 2))
	elif F < LEAP + 2:   # ย่อดีดตัว
		b.cx = x_jump
		b.key = "pls_hop_bl_1"
		b.sy = 0.9
		b.sx = 1.06
	elif F < RISE:   # ลอยขึ้นเหนือแถวแล้วลอยค้างหมุน (ลอยต่ำลงช้าๆ + โยกเบาๆ)
		var u := minf(1.0, (f - LEAP - 2) / 6.0)
		var e := 1 - pow(1 - u, 2)
		b.cx = x_jump + (hub.x - x_jump) * e
		b.lift = (hub.y + 8) * e - 4 * maxf(0.0, (f - LEAP - 8) / (RISE - LEAP - 8)) + 1.5 * sin(f * 0.9)
		b.key = "pls_spin_bl_%d" % posmod(int(floor(_spin(f) * 4)), 4)
		var w := absf(cos(_spin(f) * TAU * 2))   # บีบแกน x ตอนเปลี่ยนมุม = หมุนลื่น
		b.sx = 0.88 + 0.12 * w
	elif F < SLAM:   # ยกมีดเหนือหัว แล้วดิ่งเฉียงลงหน้าแถว
		var q := f - RISE
		if q < 2:
			b.cx = hub.x
			b.lift = hub.y + 4 * q
			b.key = "pls_bl9_2"
		else:
			var u := (q - 2) / (SLAM - RISE - 2)
			b.cx = hub.x + (x_land - hub.x) * u
			b.lift = (hub.y + 8) * (1 - u * u)
			b.key = "pls_atk_bl_4" if u < 0.5 else "pls_atk_bl_5"
			b.lean = -0.25 * u
	else:   # กระแทก ไถลถอย ค้างท่าปลายวงล้อ
		var q := f - SLAM
		b.cx = x_land + 6 * (1 - pow(1 - minf(1.0, q / 6.0), 2))
		b.key = "pls_atk_bl_5" if q < 3 else ("pls_atk_bl_6" if q < 6 else "pls_atk_bl_7")
		b.lean = -0.2 * maxf(0.0, 1 - q / 6.0)
		if q < 2:
			b.sy = 0.88
			b.sx = 1.08
	return b

## ยกมอนด้วยลมวงล้อ · ตกกระแทกตอนฟาด
func _mon_lift(i: int, f: float) -> float:
	if not lift_m or f < RING1 - 2 or f >= SLAM:
		return 0.0
	var u := minf(1.0, (f - RING1 + 2) / 8.0)
	return u * (5.0 + i) + 1.5 * sin(f * 0.8 + i * 2.1)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var ds := F - SLAM
	# จอมืด: เริ่มตอนออกวิ่ง · ฟาด = สว่างวาบแล้วค่อยจาง
	var dm := 0.0
	if F >= RUN0 and F < SLAM:
		dm = 0.5 * minf(1.0, (f - RUN0) / 10.0)
	elif ds >= 0:
		dm = maxf(0.0, 0.35 * (1 - ds / 14.0))
	dim_to(dm, Color("#0a0e26"))
	if ds >= 0 and ds < 10:
		shake(F, BM.shk * (1 - ds / 10.0))
	elif F >= RING1 and F < SLAM:
		shake(F, 0.6)   # สั่นเบาตลอดการหมุน
	else:
		cam.offset = Vector2.ZERO
	var g := geo(f)
	for i in mons.size():
		var dc := _cut_d(i, F)
		var dh := F - (SLAM + i * 2)
		var key := hurt_key() if (dh >= 0 and dh < 14) or (dc >= 0 and dc < 2 and F < SLAM) else idle_key(f + i * 3)
		var dx := 0.0
		if dc == 0 and F < SLAM:
			dx = 1.0 if (F + i) % 2 else -1.0
		if ds >= 0:
			dx = -BM.kb * (1 - pow(1 - minf(1.0, ds / 4.0), 2)) if ds < 4 else -BM.kb * maxf(0.0, 1 - (ds - 4) / 12.0)
		var amt := (0.25 if foe.begins_with("B") else 0.5) if dh == 0 else 0.0   # ใบคมผ่าน = สั่น + แผล ไม่วาบ (ตรวจแสงวาบ R2)
		_show(i, key, dx, amt, _mon_lift(i, f), 0.86 if ds >= 0 and ds < 3 and lift_m else 1.0)
	set_rion(rion, g)
	# ร่างติดตา: วิ่งช่วงง้าง · หมุน (ร่างฟ้าจาง) · ดิ่ง
	if F >= LEAP - 6 and F < LEAP:
		for k in [2, 1]:
			ghost(geo(f - k), 0.14 * (3 - k))
	if F >= LEAP + 3 and F < RISE:
		for k in [3, 2, 1]:
			ghost(geo(f - k * 0.5), 0.12 * (4 - k), Color("#9ae6ff"), 0.5)
	if F >= RISE + 2 and F <= SLAM:
		for k in [3, 2, 1]:
			ghost(geo(f - k * 0.7), 0.16 * (4 - k), Color("#9ae6ff"), 0.35)
	if fresh:
		if F >= RUN0 and F < LEAP and (F - RUN0) % 3 == 0:
			dust_at(g.cx + 6, 1.0, 0.5 + 0.5 * (F - RUN0) / (LEAP - RUN0))
		if F == LEAP:
			dust_at(g.cx, 1.0, 1.4)
			dust_at(g.cx, -1.0, 1.0)
		if F == SLAM:
			burst(Vector2(x_land - 22, G - 14), F, Color("#9ae6ff"))
			dust_at(x_land, -1.0, 2.0)
			dust_at(x_land, 1.0, 1.6)
			for i in mons.size():
				debris_at(Vector2(cxs[i] - 4, G - WAIST - 8), "คม", F, 1.0)
		if F >= RING1 and F < SLAM and F % 4 == 0:   # ลมวงล้อพัดฝุ่นที่ขอบล้อ
			dust_at(ring_c.x + ring_r.x * (1 if F % 8 == 0 else -1), -1.0 if F % 8 == 0 else 1.0, 0.7)
		if ds > 0 and ds < 8 and ds % 2 == 0:
			dust_at(g.cx + 6, 1.0, 1.0 - ds * 0.1)
		var bf := F - HOLD1 + HOP0
		if F >= HOLD1:   # ฝุ่นกระโดดถอยของเครื่องฟัน
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
	# ตัวหนังสือ: ชื่อท่าตอนออกวิ่ง · คำเสียงใหญ่กลางแถวตอนแตก · ตัวเลขพร้อมกันเหลื่อม 2 เฟรม
	var b0 := RUN0 - 2
	show_bubble("วงล้อ!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < LEAP + 4 else (LEAP + 8 - f) / 4.0) if F >= b0 and F < LEAP + 8 else 0.0)
	if ds >= 0 and ds < 18:
		var sz := 18 if ds < 2 else 16
		word(BM.sfx, clampf(x_land - 34, 4, W - 72), G - 84 - mini(6, ds), Color("#e8f8ff"), sz, 4)   # เหนือ Rion ไม่ทับตัวเลขของแถว
	for i in mons.size():
		var dh := F - (SLAM + i * 2)
		pop(dmg, maxf(16, cxs[i] - BM.kb), my + roundf(mh * 0.25) - (i % 2) * 18, dh, Color.WHITE, aff_tag(), aff_col())

# ── วาด ───────────────────────────────────────────
## ใบคมหนึ่งใบบนขอบล้อ: หางโค้งตามวง 3 ชั้น · ครึ่งหน้า (ใกล้กล้อง) หนา/สว่าง ครึ่งหลังบาง/จาง
func _blade(n: Node2D, f: float, a_head: float, back: bool, glow: float) -> void:
	var L := 1.1 + 0.5 * minf(1.0, maxf(0.0, f - RING1) / 12.0)   # หางยาวขึ้นตามความเร็ว
	var steps := 44
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
		for k in steps + 1:
			var u := float(k) / steps   # 0 = หาง · 1 = หัว
			var a := a_head - L * (1 - u)
			var on_back := sin(a) < 0
			if on_back != back:
				continue
			var near_cam := (sin(a) + 1) * 0.5   # 0 หลังสุด · 1 หน้าสุด
			var w: float = (1.5 + 3.5 * near_cam) * pow(u, 0.7) * (1 + 0.4 * glow) + layer[1]
			if w < 1:
				continue
			var p := _pt(a, f)
			var col: Color = layer[0]
			col.a = (0.5 if on_back else 1.0) * (0.3 + 0.7 * u)
			px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))
	var hp := _pt(a_head, f)
	if (sin(a_head) < 0) == back:   # หัวคม: แสงเรือง
		disc(n, hp.x, hp.y, 4 + 2 * glow, Color(0.6, 0.9, 1, (0.2 if back else 0.4) * (1 + glow)))
		disc(n, hp.x, hp.y, 2, Color(1, 1, 1, 0.6 if back else 0.95))

## วงล้อทั้งชุด (ขอบจาง + ซี่แสงจากดุม + ใบคม 6 ใบ) ชั้นหลังหรือชั้นหน้า
func _wheel(n: Node2D, f: float, back: bool) -> void:
	if f < RING0 or f >= SLAM:
		return
	var rot := _rot(f)
	var glow := maxf(0.0, (f - RISE) / (SLAM - RISE))   # ก่อนฟาด: ล้อสว่างขึ้น
	# ขอบล้อ: เส้นวงรีบางๆ ให้เห็นเป็นวงล้อ
	for k in 96:
		var a := TAU * k / 96.0
		if (sin(a) < 0) != back:
			continue
		var p := _pt(a, f)
		px(n, p.x, p.y, Color(0.6, 0.9, 1, (0.18 if back else 0.32) + 0.4 * glow), 1, 1)
	# ซี่ล้อ: จากดุม (เอว Rion) ไปหัวคมแต่ละใบ
	var g := geo(f)
	var hc := Vector2(g.cx - 4, G - g.lift - 38)
	for b in BLADES:
		var a: float = rot + b * TAU / BLADES
		if (sin(a) < 0) != back:
			continue
		var tip := _pt(a, f)
		var m := int(hc.distance_to(tip) / 3)
		for s in m:
			var u := float(s) / m
			var q := hc.lerp(tip, u)
			var al := (0.14 if back else 0.34) * (0.3 + 0.7 * u) * (1 + glow)
			if (s + int(f * 3)) % 4 < 2:   # ประเป็นช่วงวิ่งออกจากดุม
				px(n, q.x, q.y, Color(0.75, 0.95, 1, al), 1, 1)
	for b in BLADES:
		_blade(n, f, rot + b * TAU / BLADES, back, glow)
	# เถ้าหมุนวนในล้อ (ลอยขึ้นช้าๆ)
	for k in 26:
		var a := rot * 0.7 + k * 2.4
		if (sin(a) < 0) != back:
			continue
		var rr := 0.55 + 0.45 * fb_hash(k, 3, 1)
		var p := _center(f) + Vector2(cos(a) * ring_r.x * _scale(f) * rr, sin(a) * ring_r.y * rr - fmod(f * 1.3 + k * 7, 34))
		px(n, p.x, p.y, Color(0.86, 0.8, 0.72, 0.55 if back else 0.8), 2 if k % 4 == 0 else 1, 1)

func draw_back(n: Node2D) -> void:
	_wheel(n, t / SEC, true)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	var ds := f - SLAM
	# แถบภาพยนตร์บน/ล่าง: เลื่อนเข้าตอนออกวิ่ง ออกหลังค้างท่า
	var lb := 0.0
	if f >= RUN0 and f < HOLD1:
		lb = 12 * minf(1.0, (f - RUN0) / 5.0)
	elif f >= HOLD1 and f < HOLD1 + 6:
		lb = 12 * (1 - (f - HOLD1) / 6.0)
	if lb > 0:
		px(n, -8, -8, Color("#05060e"), W + 16, 8 + lb)
		px(n, -8, H - lb, Color("#05060e"), W + 16, lb + 8)
	# ออร่าเปลวฟ้ารอบตัวตอนวิ่ง/หมุน
	if F >= RUN0 + 2 and F < SLAM:
		for k in 16:
			var r := fb_hash(k, F, 5)
			var hgt := fmod(f * 4 + k * 9, 60)
			var x: float = g.cx - 14 + fb_hash(k, 1, 2) * 26 + sin(f + k) * 2
			var y: float = G - g.lift - 6 - hgt
			px(n, x, y, Color(0.55, 0.85, 1, 0.55 * (1 - hgt / 60.0)), 2 if r > 0.6 else 1, 2 if r > 0.6 else 1)
	_wheel(n, f, false)
	# รอยบาดตอนใบคมผ่าน (เล็ก · ทิศตามวง) · ยังไม่ขึ้นตัวเลข
	for i in mons.size():
		var dc := _cut_d(i, F)
		if dc >= 0 and dc < 3 and F < SLAM:
			var cx: float = cxs[i]
			var cy := G - WAIST - _mon_lift(i, f) - 6 - fb_hash(i, F, 4) * 16
			var tilt := (fb_hash(i, F, 8) - 0.5) * 10
			slash_line(n, cx + 13, cy - tilt, cx - 13, cy + tilt, 2, minf(1.0, (dc + 1) / 2.0), 1.0 - dc * 0.3)
	# ── วงล้อแตก ──
	if ds >= 0 and ds < 26:
		# จอวาบขาว 3 เฟรม (ไม่ทึบ)
		if ds < 3:
			px(n, -8, -8, Color(0.9, 0.97, 1, 0.2 * (1 - ds / 3.0)), W + 16, H + 16)
		# ใบคม 6 ใบกระเด็นออกตามแนวรัศมีแล้วจาง
		if ds < 8:
			var rot := _rot(SLAM)
			for b in BLADES:
				var a: float = rot + b * TAU / BLADES
				var p0 := _pt(a, SLAM - 0.01)
				var dir := Vector2(cos(a) * ring_r.x, sin(a) * ring_r.y).normalized()
				var p1 := p0 + dir * (10 + ds * 9)
				slash_line(n, p0.x + dir.x * ds * 6, p0.y + dir.y * ds * 6, p1.x, p1.y, 3, 1.0, 1.0 - ds / 8.0)
		# คลื่นกระแทกบนพื้น 2 วง
		for wv in 2:
			var q := ds - wv * 3
			if q < 0 or q > 14:
				continue
			var s := 0.9 + q * 0.09
			var al := 0.9 * (1 - q / 14.0)
			for k in 120:
				var a := TAU * k / 120.0
				var p := Vector2(ring_c.x + cos(a) * ring_r.x * s, G - 3 + sin(a) * ring_r.y * 0.55 * s)
				px(n, p.x, p.y, Color(0.75, 0.93, 1, al * (1.0 if sin(a) > 0 else 0.5)), 2 if wv == 0 and sin(a) > 0 else 1, 1)
		# เสาแสงผ่าทุกตัว (บาง → กว้าง → หาย) + แผลกากบาทใหญ่
		for i in mons.size():
			var dh := ds - i * 2
			if dh < 0 or dh >= 12:
				continue
			var cx: float = cxs[i] - BM.kb * minf(1.0, dh / 4.0)
			if dh < 6:
				var w := 2.0 + 6 * sin(PI * dh / 6.0)
				var top := G - (mh - top0) - 26.0   # เสาสูงเหนือหัวมอนนิดเดียว ปลายบนจาง
				for k in 4:
					var y0 := top + (G - top) * k / 4.0
					var fa := (0.35 + 0.65 * k / 3.0) * (1 - dh / 6.0)
					px(n, cx - w / 2, y0, Color(0.85, 0.96, 1, 0.6 * fa), w, (G - top) / 4.0 + 1)
					px(n, cx - 1, y0, Color(1, 1, 1, 0.85 * fa), 2, (G - top) / 4.0 + 1)
			var al := 1.0 if dh < 6 else 1 - (dh - 6) / 6.0
			var hy := G - (mh - top0) * 0.45
			var sz := minf(18.0, mw * 0.2)
			slash_line(n, cx + sz, hy - sz, cx - sz, hy + sz, 3, minf(1.0, (dh + 1) / 2.0), al)
			slash_line(n, cx - sz, hy - sz, cx + sz, hy + sz, 3, minf(1.0, (dh) / 2.0), al)
		# รอยร้าวบนพื้นตามแนวล้อ (ค้างแล้วจาง)
		var ca := maxf(0.0, 1 - ds / 26.0)
		for k in 22:
			var a := PI * (k + 0.5) / 22.0
			var p := Vector2(ring_c.x + cos(a) * ring_r.x * 0.92, G - 2 + sin(a) * 2)
			var L := 3 + int(fb_hash(k, 2, 9) * 5)
			for j in L:
				px(n, p.x + (fb_hash(k, j, 3) - 0.5) * 3 + j * (1 if k % 2 else -1), p.y - j * 0.4, Color(0.17, 0.1, 0.08, 0.8 * ca), 1, 1)
			px(n, p.x, p.y - 1, Color(0.7, 0.92, 1, 0.6 * ca * (1 if ds < 8 else 0.4)), 2, 1)
	# รอยไถลเท้าหลังลง
	if ds >= 0 and ds < 10:
		for i in 6:
			px(n, x_land - 14 + i * 4 + minf(ds, 6.0), G - 1 - fb_hash(i, 9, 1) * 2, Color("#d8ccb8"), 2, 1)
	if g.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - g.lift / 70.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)

func sounds(F: int) -> void:
	if F < RUN0 or F >= HOLD1:   # ยืน · กระโดดถอย = เครื่องฟันเดิม
		var bf := F if F < RUN0 else F - HOLD1 + HOP0
		if bf < RUN0 or bf >= HOP0:
			super.sounds(bf)
		return
	if F == RUN0:   # ไม้ตาย: เสียงต่ำบวมขึ้น + ลมก่อตัว
		play_sfx("wl_charge", [T(1.4, "sine", 50, 85, 0.55, 0, 0.3), N(1.2, "bandpass", 300, 1300, 0.3, 1.5, 0, {"attack": 0.7})])
	if F < LEAP and (F - RUN0) % 3 == 0:
		var pk := snappedf(0.4 + 0.3 * (F - RUN0) / (LEAP - RUN0), 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == LEAP:
		play_sfx("wl_leap", [N(0.12, "lowpass", 900, 150, 0.7, 1), N(0.25, "bandpass", 600, 1800, 0.3, 2, 0.03)])
	if F == RING0:   # ใบคมกางออก: หวีดกว้าง
		play_sfx("wl_open", [N(0.5, "bandpass", 700, 2600, 0.6, 2.2, 0, {"attack": 0.12}), N(0.3, "highpass", 3500, 7000, 0.25, 4, 0.1)])
	if F > LEAP + 2 and F < RISE and floor(_spin(F)) > floor(_spin(F - 1)):   # หวีดต่อรอบหมุน สูงขึ้นตามความเร็ว
		var p := snappedf(1.0 + 0.6 * (F - LEAP) / (RISE - LEAP), 0.1)
		play_sfx("wl_rev%s" % p, [N(0.22, "bandpass", 900 * p, 2000 * p, 0.45, 2.5, 0, {"attack": 0.06})])
	if F >= RING1 and F < SLAM:
		var any := false
		for i in cuts.size():
			if cuts[i].has(F):
				any = true
		if any:   # บาดสั้นๆ ไม่ตูม
			play_sfx("wl_tick%d" % (F % 3), [N(0.05, "highpass", 3800 + 400 * (F % 3), 6000, 0.35, 2), N(0.1, "bandpass", 4200, 2800, 0.15, 12, 0.01)])
	if F == RISE:   # ยกมีด: เสียงไต่ขึ้น
		play_sfx("wl_rise", [N(0.36, "bandpass", 1200, 4200, 0.5, 3, 0, {"attack": 0.2}), T(0.36, "sawtooth", 180, 420, 0.12, 0, 0.1, {"lp": 2000})])
	if F == RISE + 3:   # ดิ่ง
		play_sfx("wl_dive", [N(0.2, "bandpass", 3200, 600, 0.55, 2)])
	if F == SLAM:   # วงล้อแตก: กระแทกใหญ่ + ทุ้มยาว + เศษคมแตกกระจาย
		sfx_hit(true)
		play_sfx("wl_boom", [T(1.6, "sine", 72, 24, 0.9, 0, 0.002, {"drive": true}), N(1.3, "lowpass", 2200, 70, 0.7, 0.8), N(0.5, "highpass", 6000, 2000, 0.4, 3, 0.03), N(0.6, "bandpass", 3000, 900, 0.3, 4, 0.06)])
	for i in mons.size():
		if F == SLAM + i * 2:
			sfx_mon(i == mons.size() - 1, (0.6 if foe == "B1" else 1.0) * (1.0 - i * 0.05))
	if F == SLAM + 1:
		play_sfx("brake", [N(0.18, "lowpass", 1600, 400, 0.35, 2)])
