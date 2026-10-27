extends "res://tests/lab/row_base.gd"
## ทะลวงแนว bl10 (kwan 27 ต.ค. "ต่อด้วย bl10 bl11 · ขอดูฝีมือ") — ตามรายงานวิจัยท่า R2 (ดาบสองมือเยอรมัน Doppelsöldner ตัดผ่านแนวหอก)
## วิ่งเข้า → วิ่งทะลุแถวโดยไม่หยุด คมเหวี่ยงเลขแปดนอนต่อเนื่อง (ริบบิ้นเส้นเดียวไม่ขาด) โดนทีละตัวตอนผ่าน
## → เบรกไถลหลังแถว → หันกลับตั้งการ์ด (ผลรวมทั้งแถวให้ผู้เล่นเห็น) → กระโดดข้ามแถวกลับ → วิ่งกลับที่
## กฎของท่า: ไม่หยุดภาพ · ไม่มีดาว/วาบขาวรายฮิต · จอสั่นครั้งเดียวตอนเบรก · ตัวหลังเบากว่าตัวแรก (แผล/เศษ/ระยะแหวก/เสียง)
## ภาพ Rion ประกอบจากภาพที่มีอยู่ (ยังไม่เจนใหม่): วิ่ง pls_run_bl · ทะลุ pls_atk_bl_4–5 + pls_bl1_4–5 · เบรก pls_bl1_7 · การ์ด pls_guard (พลิก) · กระโดด pls_hop_bl

const RUN0 := 18     # เริ่มวิ่ง
const PASS0 := 26    # เข้าแถว
const PASS1 := 54    # ออกจากแถว
const BRAKE1 := 62
const GUARD1 := 72
const JUMP1 := 86
const BACK1 := 98
const END10 := 106

var x_home := 0.0
var x_in := 0.0
var x_out := 0.0
var x_land := 0.0
var hits_f: Array[int] = []

func mv() -> Dictionary:
	return {"id": "bl10", "slide": 0, "reach": 0, "kb": 0, "shk": 1.5, "sfx": "ฉึบ!", "what": "ทะลวงแนว (bl10)"}

func end_frame() -> int: return END10
func stops() -> Array: return []   # ไม่หยุดภาพเลย (หยุด = ทิ้งโมเมนตัมของใบ)
func caption() -> String: return "ยืนในศึก → วิ่งทะลุแถว เหวี่ยงไม่หยุด → เบรก ตั้งการ์ด → กระโดดกลับ"

func setup() -> void:
	super.setup()
	setup_row(mw * 0.5 + 72, 0.62, mw * 0.5 + 72)   # เว้นที่ซ้ายให้ Rion ทะลุออกไปเบรก/ตั้งการ์ดหลังแถวในจอ
	x_home = start + 60
	x_in = cxs[0] + mw * 0.5 + 12
	x_out = maxf(26.0, cxs[cxs.size() - 1] - mw * 0.5 - 14)   # แถวถูกเลื่อนซ้าย (มอนตัวใหญ่) → เบรกในจอ
	x_land = cxs[0] + mw * 0.5 + 28
	hits_f.clear()
	for c in cxs:   # โดนตอนกลางตัว Rion ผ่านกลางตัวมอน
		hits_f.append(PASS0 + int(round((x_in - c) / (x_in - x_out) * (PASS1 - PASS0))))

## ตำแหน่ง Rion · cx = กลางผืนบนจอ
func geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var b := {"cx": x_home, "lift": 0.0, "lean": 0.0, "sx": 1.0, "sy": 1.0, "key": "pls_idle_bl_%d" % posmod(F / 4, 4), "flip": false}
	if F < RUN0:
		b.sy = 1 - 0.015 * posmod(F / 4, 2)
	elif F < PASS0:   # ออกตัวแรง เร่งเข้าแถว
		var u := (f - RUN0) / (PASS0 - RUN0)
		b.cx = x_home + (x_in - x_home) * (u * u * 0.6 + u * 0.4)
		b.lean = -0.06 * u
		b.key = "pls_run_bl_%d" % ((F - RUN0) % 6)
	elif F < PASS1:   # ทะลุแถวความเร็วคงที่ · คมเหวี่ยงวน 8 เฟรม/รอบ
		var u := (f - PASS0) / (PASS1 - PASS0)
		b.cx = x_in + (x_out - x_in) * u
		b.lean = -0.1
		b.key = ["pls_atk_bl_4", "pls_atk_bl_5", "pls_bl1_5", "pls_bl1_4"][posmod((F - PASS0) / 2, 4)]
	elif F < BRAKE1:   # เบรก 2–3 ก้าว ไถลต่อ ไม่หยุดกึก
		var q := (f - PASS1) / (BRAKE1 - PASS1)
		b.cx = x_out - 10 * (1 - pow(1 - q, 2))
		b.lean = -0.14 * (1 - q)
		b.key = "pls_bl1_7" if q < 0.6 else "pls_bl1_0"
		b.sy = 0.96
	elif F < GUARD1:   # หันกลับตั้งการ์ด มองผลรวมของแถว
		b.cx = x_out - 10
		b.flip = true
		b.key = "pls_guard_%d" % mini(3, (F - BRAKE1) / 2)
	elif F < JUMP1:   # กระโดดข้ามแถวกลับฝั่ง (หันขวา)
		var u := (f - GUARD1) / (JUMP1 - GUARD1)
		b.flip = true
		if u < 0.15:
			b.cx = x_out - 10
			b.key = "pls_hop_bl_1"
			b.sy = 0.92
		else:
			var v := (u - 0.15) / 0.85
			b.cx = (x_out - 10) + (x_land - (x_out - 10)) * v
			b.lift = 4 * maxf(46.0, mh * 0.8) * v * (1 - v)   # ข้ามบอสตัวสูงได้
			b.key = "pls_hop_bl_2" if v < 0.3 else ("pls_hop_bl_4" if v < 0.8 else "pls_hop_bl_3")
			b.lean = 0.08 * (0.5 - v)
	elif F < BACK1:   # ลงพื้นแล้ววิ่งกลับที่
		var u := (f - JUMP1) / (BACK1 - JUMP1)
		b.flip = true
		b.cx = x_land + (x_home - x_land) * (1 - pow(1 - u, 2))
		b.key = "pls_hop_bl_0" if F - JUMP1 < 2 else "pls_run_bl_%d" % ((F - JUMP1) % 6)
	else:
		b.key = "pls_idle_bl_%d" % posmod((F - BACK1) / 4, 4)
	return b

## จุดปลายคมรอบตัว Rion: เลขแปดนอน (forehand/backhand สลับ) ระดับอก
func _blade(f: float) -> Vector2:
	var g := geo(f)
	var w := TAU * (f - PASS0) / 8.0
	return Vector2(g.cx - 26 + sin(w) * 15, G - g.lift - 34 + sin(w) * cos(w) * 22)

## แหวกออก: ตัวแรกเปิดกว้างสุด ตัวหลังแค่เซ (ถูกปัดไปทางขวา = ด้านหลังทางวิ่ง แล้วค่อยกลับ)
func _part(i: int, d: int) -> float:
	if d < 0:
		return 0.0
	var amp: float = [9.0, 6.0, 3.5][mini(i, 2)]
	return amp * (1 - pow(1 - minf(1.0, d / 4.0), 2)) if d < 4 else amp * maxf(0.0, 1 - (d - 4) / 14.0)

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(false)
	var db := F - PASS1
	cam.offset = Vector2(round(-1.5 * sin(db * 1.6) * (1 - db / 5.0)), 0) if db >= 0 and db < 5 else Vector2.ZERO   # สั่นขนานพื้นตอนเบรกเท่านั้น
	var g := geo(f)
	for i in mons.size():
		var d := F - hits_f[i]
		_show(i, hurt_key() if d >= 0 and d < 12 else idle_key(f + i * 3), _part(i, d), 0.0, 0.0, 0.96 if d >= 0 and d < 3 else 1.0)
	set_rion(rion, g)
	if F >= PASS0 - 2 and F < PASS1 + 2:   # ร่างติดตาความเร็ว 3 ร่าง
		for k in [3, 2, 1]:
			ghost(geo(f - k * 1.5), 0.12 * (4 - k))
	if F >= GUARD1 + 3 and F < JUMP1 - 2:
		ghost(geo(f - 2), 0.18)
	if fresh:
		if F >= RUN0 and F < PASS1 and (F - RUN0) % 2 == 0:   # ฝุ่นเท้าเป็นทางยาว
			dust_at(g.cx + 6, 1.0, 1.1 if F == RUN0 else 0.6)
		if F >= PASS1 and F < BRAKE1 and (F - PASS1) % 2 == 0:   # เบรก: ฝุ่นโค้งกว้างหน้าตัว
			dust_at(g.cx - 8, -1.0, 1.2 - (F - PASS1) * 0.1)
		if F == JUMP1 - 1:
			dust_at(g.cx, 1.0, 1.2)
		for i in mons.size():
			if F == hits_f[i]:   # เศษพุ่งออกด้านข้างตามทิศแหวก (ไม่ย้อนเข้าหา Rion) · ลดลงตามลำดับ
				debris_at(Vector2(cxs[i] + 6, G - 30), "คม", F, [1.0, 0.7, 0.45][mini(i, 2)])
	var b0 := RUN0 - 2
	show_bubble("ทะลวงแนว!", g.cx, G - g.lift - 74, F - b0, (1.0 if F < PASS0 + 6 else (PASS0 + 10 - f) / 4.0) if F >= b0 and F < PASS0 + 10 else 0.0)
	for i in mons.size():
		var d := F - hits_f[i]
		pop(dmg, maxf(16, cxs[i] + _part(i, d)), my + roundf(mh * 0.25) - (i % 2) * 18, d, Color.WHITE, aff_tag(), aff_col())

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	# ริบบิ้นคม: เส้นเดียวต่อเนื่อง 3 ชั้น ตั้งแต่ออกวงแรกจนเบรก · กว้าง/สว่างพีคตอนผ่านแต่ละตัว (ตัวหลังบางลง)
	if f >= PASS0 - 1 and f < PASS1 + 8:
		var fade := 1.0 if f < PASS1 else maxf(0.0, 1 - (f - PASS1) / 8.0)
		var L := 7.0   # หางยาวกี่เฟรม
		for layer in [[Color("#1a3a9a"), 2.0], [Color("#9ae6ff"), 0.0], [Color.WHITE, -2.0]]:
			for k in 57:
				var u := float(k) / 56   # 0 หาง · 1 หัว
				var ft := minf(f, PASS1 + 1.0) - L * (1 - u)
				if ft < PASS0 - 1:
					continue
				var peak := 0.0
				for i in hits_f.size():
					peak = maxf(peak, [1.0, 0.75, 0.55][mini(i, 2)] * exp(-pow((ft - hits_f[i]) / 2.2, 2)))
				var w: float = (1.2 + 2.0 * peak) * pow(u, 0.7) * 2 + layer[1]
				if w < 1:
					continue
				var p := _blade(ft)
				var col: Color = layer[0]
				col.a = fade * (0.4 + 0.6 * u)
				px(n, p.x - w / 2, p.y - w / 2, col, ceil(w), ceil(w))
	# แผลเฉียงตามแนววงที่ผ่าน · เล็กลงตามลำดับ
	for i in mons.size():
		var d := F - hits_f[i]
		if d >= 0 and d < 14:
			var s: float = [1.0, 0.8, 0.6][mini(i, 2)]
			var al := 1.0 if d < 7 else maxf(0.0, 1 - (d - 7) / 7.0)
			var x0 := cxs[i] + _part(i, d)
			var dir := 1.0 if i % 2 == 0 else -1.0   # forehand/backhand สลับทิศแผล
			slash_line(n, x0 + 12 * s, G - 30 - 9 * s * dir, x0 - 12 * s, G - 30 + 9 * s * dir, 3 if i == 0 else 2, minf(1.0, (d + 1) / 2.0), al)
	if F >= PASS1 and F < BRAKE1 + 6:   # รอยไถลบนพื้น
		var q := F - PASS1
		for i in 7:
			px(n, x_out + 4 - i * 3 - minf(q, 8) * 1.5, G - 1 - fb_hash(i, 4, 1) * 2, Color(0.85, 0.8, 0.72, maxf(0.0, 0.8 - q * 0.05)), 2, 1)
	if g.lift > 1:   # เงาพื้นตอนลอย
		for i in range(-9, 10):
			if absi(i) < 9 * maxf(0.4, 1 - g.lift / 50.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)

func sounds(F: int) -> void:
	if F >= RUN0 and F < PASS1 and (F - RUN0) % 3 == 0:   # ฝีเท้าคงที่ใต้เสียงหวีด
		play_sfx("tl_step", [N(0.06, "lowpass", 900, 200, 0.45, 1)])
	if F == RUN0:   # ออกตัว + พาดคม
		play_sfx("tl_go", [N(0.12, "lowpass", 600, 120, 0.6, 1), T(0.08, "triangle", 1400, 1100, 0.08)])
	if F == PASS0 - 1:   # หวีดลมเส้นเดียวไม่ขาด: คลื่นขึ้นลงตามรอบเหวี่ยง (ยอด = จังหวะผ่านจุดเร็วสุด)
		var v := []
		for k in 4:
			v.append(N(0.5, "bandpass", 700, 2200, 0.55, 2.2, k * 0.48, {"attack": 0.2}))
		v.append(N(1.9, "bandpass", 1200, 900, 0.25, 1.5, 0.0, {"attack": 0.15}))
		play_sfx("tl_whirl", v)
	for i in hits_f.size():   # เสียงตัดสั้น เบาลง/ต่ำลงตามลำดับ ทับเสียงหวีดโดยไม่ตัดมัน
		if F == hits_f[i]:
			var p: float = [1.0, 0.85, 0.72][mini(i, 2)]
			play_sfx("tl_cut%d" % i, [N(0.08, "highpass", 4000 * p, 1500 * p, 0.7 * p, 2), N(0.16, "bandpass", 3600 * p, 2200 * p, 0.3 * p, 10, 0.01)])
			sfx_mon(false, (0.6 if foe == "B1" else 1.0) * (1.0 - i * 0.06))
	if F == PASS1:
		play_sfx("brake", [N(0.32, "lowpass", 1600, 300, 0.45, 2)])
	if F == BRAKE1 + 1:   # ตั้งการ์ด
		play_sfx("tl_guard", [T(0.06, "triangle", 900, 700, 0.12)])
	if F == GUARD1 + 2:
		play_sfx("kick0.5", [N(0.06, "bandpass", 600, 1600, 0.3, 2)])
	if F == JUMP1:
		play_sfx("land0.5", [N(0.09, "lowpass", 700, 150, 0.5, 1)])
