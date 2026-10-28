extends "res://tests/lab/row_base.gd"
## กวาด bl3 — รอบ 2 (kwan 28 ต.ค. "วงล้อกับกวาด ลงไปกลางดงมอนเลย" · "ท่าดูไม่ลื่น เจนเพิ่มให้ไหลลื่นได้")
## วิ่ง → กระโดดข้ามตัวหน้าลงกลางแถว (ท่ากลาง PixelLab bl14_leap) → ลงคุกเข่าข้างเดียว ตัวหน้า 2 ตัวผงะเปิดทาง
## → กวาดต่ำระดับเข่าหมุนรอบตัว 1 รอบ (State BL3_kneel_sweep + rot8 = ภาพคุกเข่ากางแขน 8 มุม pls_kneel_0–7)
## → คมผ่านซ้าย (โดนตัวซ้าย) → หน้า → ขวา (โดนตัวขวา) → หลัง (โดนตัวกลางแถวหลัง) → จบหันซ้าย → ลุกกระโดดถอย
## ต่างจากวงล้อ bl4 (ยืนกางแขน T หมุน 2 รอบ ปล่อยคมลม) และพายุเถ้า bl12 (ลมหมุนพุ่งทะลุแถว): ท่านี้คุกเข่า รอบเดียว วงคมแนบพื้น
## มุมภาพ pls_kneel_k: 0 ซ้าย · 2 หน้า · 4 ขวา · 6 หลัง · มีด (แขนขวา) อยู่ที่มุม θ = 3π/2 − k·π/4 บนวงรีรอบตัว (π = ซ้าย · π/2 = หน้า)

const RUN0 := 18
const LEAP0 := 26
const LAND := 34      # ลงคุกเข่ากลางแถว
const SW0 := 36       # เริ่มกวาด
const SW1 := 48       # กวาดครบรอบ (หันซ้าย)
const HOLD1 := 54     # ค้างท่าคุกเข่าแล้วเข้ากระโดดถอยของเครื่องฟัน
const KNEE := 12      # ระดับคมเหนือพื้น
const ROOM_PX := 8.0

var x_home := 0.0
var x_spin := 0.0
var x_jump := 0.0
var mid := false
var RR := Vector2(34, 7)          # วงรีของคม
var hits_f: Array[float] = []

func mv() -> Dictionary:
	return {"id": "bl3", "slide": 0, "reach": 0, "kb": 6, "shk": 1.5, "sfx": "ซวบ!!", "what": "กวาด (bl3)"}

func end_frame() -> int: return HOLD1 + END - HOP0
func stops() -> Array: return [[int(ceil(hits_f.min())), 0.06]] if not hits_f.is_empty() else []
func caption() -> String: return "วิ่ง → กระโดดลงกลางดงมอน → คุกเข่ากวาดต่ำรอบตัว 1 รอบ → ลุกกระโดดถอย"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 6)
	x_home = start + 60
	mid = cxs.size() == 3
	x_spin = cxs[1] if mid else cxs[0] + mw * 0.5 + 12
	x_jump = cxs[0] + mw * 0.5 + 30 if mid else x_spin + 20
	near = x_spin + 2 - 60
	RR = Vector2(maxf(32.0, (cxs[0] - cxs[1] + 10) if mid else mw * 0.5 + 16), 8)
	hits_f.clear()
	for i in cxs.size():   # มุมภาพที่คมผ่านตัว i: ซ้าย v 2 · ขวา v 6 · หลัง (ตัวกลาง) v 8
		var v := 8.0 if mid and i == 1 else (6.0 if mid and i == 0 else 2.0)
		hits_f.append(_f_of_v(v - 0.2))

# ── มุมหมุน (หน่วย = มุมภาพ · 8 ต่อรอบ) ─────────────
func _v(f: float) -> float:
	if f < SW0:
		return 0.0
	var u := minf(1.0, (f - SW0) / (SW1 - SW0))
	return 8.0 * (u * u * (3 - 2 * u)) * 0.6 + 8.0 * u * 0.4   # เร่งกลางรอบ ช้าตอนจบ

func _f_of_v(v: float) -> float:
	var lo := float(SW0)
	var hi := float(SW1)
	for i in 30:
		var m := (lo + hi) * 0.5
		if _v(m) < v:
			lo = m
		else:
			hi = m
	return lo

func _theta(v: float) -> float:
	return 1.5 * PI - v * PI / 4.0

func _dir(i: int) -> float:
	if not mid or i == 1:
		return -1.0 if not mid else -0.4
	return signf(cxs[i] - x_spin)

func _room(i: int, f: float) -> float:
	if not mid or i == 1 or f < LAND - 2:
		return 0.0
	var u := minf(1.0, (f - LAND + 2) / 4.0)
	return _dir(i) * ROOM_PX * (1 - pow(1 - u, 2))

## มอนไถลออกจากตัว Rion ตามทิศกวาด แล้วค่อยกลับ
func _slide(d: float) -> float:
	if d < 0:
		return 0.0
	if d < 6:
		return BM.kb * (1 - pow(1 - d / 6.0, 2))
	return BM.kb * maxf(0.0, 1 - (d - 6) / 10.0)

func _mx(i: int, f: float) -> float:
	return _room(i, f) + _slide(f - hits_f[i]) * _dir(i)

# ── ตำแหน่ง Rion ─────────────────────────────────
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < RUN0:
		return super.geo(f)
	if F >= HOLD1:
		return super.geo(f - HOLD1 + HOP0)
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_run_bl_0", "flip": false}
	if F < LEAP0:
		var u := (f - RUN0) / (LEAP0 - RUN0)
		b.cx = x_home + (x_jump - x_home) * (u * u * 0.5 + u * 0.5)
		b.lean = -0.07 * minf(1.0, u * 2)
		b.key = "pls_run_bl_%d" % ((F - RUN0) % 6)
		return b
	if F < LAND:   # กระโดดโค้งข้ามตัวหน้า
		var u := (f - LEAP0) / (LAND - LEAP0)
		b.cx = x_jump + (x_spin - x_jump) * u
		b.lift = (38.0 if mid else 16.0) * sin(PI * u)
		b.key = "pls_hop_bl_1" if u < 0.12 else ("pls_lair_0" if u < 0.72 else "pls_leap_4")
		return b
	b.cx = x_spin
	b.key = "pls_kneel_%d" % posmod(int(floor(_v(f) + 0.5)), 8)
	if F < SW0 + 1:   # ลงคุกเข่า: ยุบรับแรง
		b.sy = 0.92
		b.sx = 1.05
	return b

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var d0 := F - int(ceil(hits_f.min()))
	var dl := F - LAND
	shake(F, BM.shk * (1 - d0 / 4.0) if d0 >= 0 and d0 < 4 else (1.2 * (1 - dl / 3.0) if dl >= 0 and dl < 3 else 0.0))
	var g := geo(f)
	for i in mons.size():
		var d := f - hits_f[i]
		var dF := F - int(ceil(hits_f[i]))
		var flinch := _room(i, f) != 0.0 and f < LAND + 4
		_show(i, hurt_key() if (d >= 0 and d < 10) or flinch else idle_key(f + i * 3), _mx(i, f), (0.25 if foe.begins_with("B") else 0.5) if dF == 0 else 0.0)
	set_rion(rion, g)
	if F >= LEAP0 and F < LAND:   # ร่างติดตาตอนกระโดด
		ghost(geo(f - 1.5), 0.18)
		ghost(geo(f - 3), 0.1)
	if F >= SW0 and F < SW1 + 2:   # ร่างติดตาตอนหมุน (มุมก่อนหน้า)
		var gg := g.duplicate()
		gg.key = "pls_kneel_%d" % posmod(int(floor(_v(f - 1) + 0.5)), 8)
		ghost(gg, 0.22, Color("#9ae6ff"), 0.4)
	if fresh:
		if F >= RUN0 and F < LEAP0 and (F - RUN0) % 3 == 0:
			dust_at(g.cx + 6, 1.0, 0.6)
		if F == LEAP0:
			dust_at(g.cx + 6, 1.0, 1.1)
		if F == LAND:
			dust_at(g.cx, 1.0, 1.4)
			dust_at(g.cx, -1.0, 1.4)
		if F >= SW0 and F < SW1 and F % 2 == 0:   # ฝุ่นตามคมแนบพื้น
			var a := _theta(_v(f))
			dust_at(x_spin + cos(a) * RR.x, -signf(sin(a) + 0.01), 0.7)
		for i in mons.size():
			if F == int(ceil(hits_f[i])):
				debris_at(Vector2(cxs[i] + _mx(i, f), gy(i) - KNEE - 6), "คม", F, 0.8)
				if i == 0 or not mid:
					burst(Vector2(cxs[i] + _mx(i, f) - _dir(i) * mw * 0.2, G - KNEE - 4), F, Color("#9ae6ff"))
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
	var b0 := RUN0 - 2
	show_bubble("กวาด!", g.cx, maxf(14.0, G - g.lift - 74), F - b0, (1.0 if F < LEAP0 + 4 else (LEAP0 + 8 - f) / 4.0) if F >= b0 and F < LEAP0 + 8 else 0.0)
	if d0 >= 0 and d0 < 16:   # เหนือหัว Rion (ตัวเลขอยู่เหนือมอน)
		word(BM.sfx, clampf(x_spin - 28, 4, W - 60), G - 70 - mini(5, d0), Color.WHITE)
	for i in mons.size():
		pop(dmg, maxf(16, cxs[i] + _mx(i, f)), my + roundf(mh * 0.25) - (i % 2) * 18 - dep[i], F - int(ceil(hits_f[i])), Color.WHITE, aff_tag(), aff_col())

## วงคมแนบพื้นรอบตัว: หางไล่หลังหัวคม · back = ครึ่งหลังตัว (วาดใต้มอน/Rion)
func _ring(n: Node2D, f: float, back: bool) -> void:
	if f < SW0 - 0.5 or f >= SW1 + 6:
		return
	var v := _v(f)
	var head := _theta(v)
	var fade := 1.0 if f < SW1 else maxf(0.0, 1 - (f - SW1) / 6.0)
	var L := minf(2.0 * PI * 0.95, v * PI / 4.0 + 0.4)   # หางยาวตามที่กวาดมาแล้ว (ครบรอบ = วงเกือบเต็ม)
	var c := Vector2(x_spin - 2, G - KNEE)
	for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
		for k in 140:
			var u := float(k) / 139   # 0 หาง · 1 หัว
			var a := head + L * (1 - u)
			var front := sin(a) > 0
			if front == back:
				continue
			var w: float = (1.2 + 3.6 * pow(u, 0.6)) * (1.2 if front else 0.8) + layer[1]
			if w < 1:
				continue
			var p := c + Vector2(cos(a) * RR.x, sin(a) * RR.y)
			var col: Color = layer[0]
			col.a = fade * (0.2 + 0.8 * pow(u, 1.5)) * (1.0 if front else 0.6)
			px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))
	if not back and f < SW1 + 1:   # หัวคมเรือง + เศษหิมะ/ฝุ่นปลิวตามแนวสัมผัส
		var hp := c + Vector2(cos(head) * RR.x, sin(head) * RR.y)
		disc(n, hp.x, hp.y, 4, Color(0.6, 0.9, 1, 0.35 * fade))
		disc(n, hp.x, hp.y, 2, Color(1, 1, 1, 0.9 * fade))
		for i in 6:
			var r := fb_hash(i, floor(f), 3)
			px(n, hp.x + (r - 0.5) * 10, hp.y - 2 - fb_hash(i, 5, 7) * 8, Color(0.88, 0.85, 0.8, 0.7 - i * 0.1), 2, 1)

func draw_back(n: Node2D) -> void:
	_ring(n, t / SEC, true)

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var st := geo(f)
	_ring(n, f, false)
	for i in mons.size():   # แผลแนวนอนต่ำระดับเข่า
		var d := f - hits_f[i]
		if d >= 0 and d < 12:
			var al := 1.0 if d < 6 else maxf(0.0, 1 - (d - 6) / 6.0)
			var half := mw * (0.18 if hard_body() else 0.24)
			var x0 := cxs[i] + _mx(i, f)
			var wy := gy(i) - KNEE - 4
			slash_line(n, x0 + half, wy - 1, x0 - half, wy + 1, 2, minf(1.0, (d + 1) / 2.0), al)
	if st.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - st.lift / 40.0):
				px(n, st.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	if F >= SW0 and F < SW1 + 10:   # รอยวงบนพื้น (ค่อยจาง)
		var al := 0.45 * (1.0 if F < SW1 else maxf(0.0, 1 - (f - SW1) / 10.0))
		for k in 48:
			var a := TAU * k / 48.0
			if a / TAU * 8.0 > _v(f) + 0.5 and F < SW1:
				continue
			px(n, x_spin - 2 + cos(_theta(0) - a) * RR.x, G - 1 + sin(_theta(0) - a) * 2, Color(0.82, 0.86, 0.95, al), 2, 1)

func sounds(F: int) -> void:
	if F < RUN0 or F >= HOLD1:
		var bf := F if F < RUN0 else F - HOLD1 + HOP0
		if bf < RUN0 or bf >= HOP0:
			super.sounds(bf)
		return
	if F < LEAP0 and (F - RUN0) % 3 == 0:
		var pk := snappedf(0.4 + 0.3 * (F - RUN0) / (LEAP0 - RUN0), 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == LEAP0:
		play_sfx("sw_jump", [N(0.2, "bandpass", 300, 900, 0.35, 2), T(0.18, "sine", 160, 320, 0.25, 0, 0.004)])
	if F == LAND:   # ลงคุกเข่า
		play_sfx("sw_land", [N(0.16, "lowpass", 900, 150, 0.75, 1), T(0.2, "sine", 90, 40, 0.5, 0, 0.003)])
	if F == SW0:   # กวาด: หวีดวนรอบตัว
		play_sfx("sw_sweep", [N(0.62, "bandpass", 700, 2400, 0.85, 2.5, 0, {"attack": 0.08}), N(0.5, "bandpass", 2400, 900, 0.4, 2, 0.45), N(0.25, "highpass", 3200, 8000, 0.35, 6, 0.05)])
	for i in mons.size():
		if F == int(ceil(hits_f[i])):
			if i == 0 or not mid:
				sfx_hit(false)
			else:
				play_sfx("sw_tick%d" % i, [N(0.07, "highpass", 3000, 6000, 0.55, 2), N(0.18, "bandpass", 4200 - i * 300, 2600, 0.3, 12, 0.01), T(0.2, "sine", 160, 60, 0.35, 0, 0.002)])
			sfx_mon(false, 0.6 if foe == "B1" else 1.0 + i * 0.06)
