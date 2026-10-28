extends "res://tests/lab/fl_base.gd"
## พันคมดับเถ้า bl16 ไม้ตายสายคม (kwan 28 ต.ค. "ฟันคมดับเถ้า เอฟเฟคเป็นพายุไฟไฟลูกก่อนแล้วกลายเป็นพายุเถ้า")
## โครงตามรายงานทีม R2 (รวมศาสตร์ของสาย · 5 ครั้ง "อ่านต่างกัน" · รอยฟันเป็นรูปดาวบนตัวเป้า · ฮิต 5 มีช่องว่างครึ่งจังหวะ):
## ก้าวเข้า 1 ก้าว → ชาร์จ (State BL16_charge จับมีดกลับด้าน · มีดร้อนแดง ถ่านลอย พื้นร้อน)
## → พุ่งทะลุ 4 ครั้งจากขวาไปซ้าย หายเป็นถ่านแล้วโผล่ขวาใหม่: 1 พุ่งตรงแบบ bl1 · 2 ไขว้มีดเงาแบบ bl6 · 3 ปาดต่ำแบบ bl13 · 4 หมุนแบบ bl4
## → ค้างกลางอากาศเหนือเป้า (ครึ่งจังหวะ) → 5 ฟันตัดสินลงแนวดิ่ง (State BL16_finish)
## → รอยดาว 5 แฉกลุกเป็นพายุไฟหมุน → ไฟมอดกลายเป็นพายุเถ้าสีเทา (ล้มสลายถ้าดาเมจรวม ≥ HP) → zanshin → กระโดดถอย

const STEP1 := 22    # ก้าวเข้า 1 ก้าว
const CHG1 := 36     # ชาร์จจบ
const DASH := 6      # เฟรมต่อการพุ่ง 1 ครั้ง (โดนกลางทาง)
const HANG0 := 60    # โผล่ค้างเหนือเป้า
const DROP := 66     # ฟันตัดสินลง
const LAND := 70
const FIRE0 := 71    # รอยดาวลุก → พายุไฟ
const ASH0 := 86     # ไฟมอด → พายุเถ้า
const ASH1 := 104
const RISE := 98     # ลุกจากท่าฟันตัดสิน
const HOLDF := 108

var x_r := 0.0       # จุดโผล่ขวา
var x_l := 0.0       # ปลายทางซ้าย
var x_fin := 0.0     # จุดลงฟันตัดสิน
var x_c := 0.0       # จุดชาร์จ
var star_pts: Array[Vector2] = []   # ปลายแฉกดาว 5 จุด (บนตัวเป้า)
var total := 0
var kill16 := false

func mv() -> Dictionary:
	return {"id": "bl16", "slide": 0, "reach": 0, "kb": 3, "shk": 2.0, "sfx": "ฉัวะ!", "what": "พันคมดับเถ้า (bl16)"}

func caption() -> String: return "★ ไม้ตาย: ชาร์จถ่านร้อน → พุ่ง 4 ทิศ (ตรง · ไขว้ · ต่ำ · หมุน) → ค้างฟ้า → ฟันตัดสิน → ดาวไฟ → พายุไฟ → พายุเถ้า"
func stops() -> Array: return [[39, 0.04], [45, 0.04], [51, 0.04], [57, 0.04], [69, 0.14]]

func setup() -> void:
	super.setup()
	hold1 = HOLDF
	hit_f.clear()
	for k in 4:
		hit_f.append(36.0 + k * DASH + 3)
	hit_f.append(float(LAND - 1))
	total = dmg * hit_f.size()
	kill16 = total >= hp
	x_c = x_home - 16
	x_r = vis.end.x + 34
	x_l = maxf(20.0, vis.position.x - 26)
	x_fin = vis.end.x + 40   # ห่างพอไม่ให้พายุกลืนตัว Rion
	set_end(x_fin)
	bubble_name = "พันคมดับเถ้า"
	bubble_at = Vector2(STEP1, CHG1)
	var c := vis.get_center()
	var r := minf(vis.size.x, vis.size.y) * 0.44
	star_pts.clear()
	for j in 5:   # ลำดับจุดตามเส้นดาว (ข้ามทีละ 2) → ฟันครบ 5 ครั้ง = ดาวปิดวง
		var a := TAU * ((j * 2) % 5) / 5.0
		star_pts.append(c + Vector2(sin(a) * r, -cos(a) * r))

func _dash_k(f: float) -> int:
	return int(floor((f - CHG1) / DASH)) if f >= CHG1 and f < HANG0 else -1

func _move(f: float) -> Dictionary:
	var F := int(floor(f))
	if F < STEP1:   # ก้าวเข้า 1 ก้าว
		var u := (f - IDLE) / (STEP1 - IDLE)
		return {"cx": x_home + (x_c - x_home) * u, "key": "pls_run_bl_%d" % ((F - IDLE) % 6), "lean": -0.04}
	if F < CHG1:   # ชาร์จ: ทรุดลง ตัวสั่นช่วงท้าย
		var u := (f - STEP1) / (CHG1 - STEP1)
		var tr := 0.7 * maxf(0.0, u - 0.5) * 2 * (1.0 if F % 2 == 0 else -1.0)
		return {"cx": x_c + tr, "key": "pls_u_charge_0", "sy": 1.0 - 0.05 * u, "sx": 1.0 + 0.03 * u}
	var k := _dash_k(f)
	if k >= 0:   # พุ่งทะลุขวา → ซ้าย (เร็วกลางทาง)
		var u := (f - CHG1 - k * DASH) / DASH
		var e := u * u * (3 - 2 * u)
		var b := {"cx": x_r + (x_l - x_r) * e, "lean": -0.1}
		match k:
			0: b.key = "pls_bl1_5" if u < 0.5 else "pls_bl1_6"
			1: b.key = "pls_sd_x_0" if u < 0.5 else "pls_sd_x_2"
			2:
				b.key = "pls_sh_cut_1" if u < 0.5 else "pls_sh_cut_3"
				b.sy = 0.94
			3:
				b.key = "pls_wheel_%d" % posmod(int(floor(u * 8.0)), 8)
				b.lean = 0.0
		return b
	if F < DROP:   # ค้างกลางอากาศเหนือเป้า (ครึ่งจังหวะ ก่อนฟันตัดสิน)
		var u := (f - HANG0) / (DROP - HANG0)
		return {"cx": vis.get_center().x + 14, "lift": 58 + 6 * sin(PI * u), "key": "pls_lair_0"}
	if F < LAND:   # ฟันตัดสินลงแนวดิ่ง
		var u := (f - DROP) / (LAND - DROP)
		return {"cx": vis.get_center().x + 14 + (x_fin - vis.get_center().x - 14) * u, "lift": 64 * (1 - u * u), "key": "pls_lair_0" if u < 0.3 else ("pls_leap_5" if u < 0.75 else "pls_u_finish_0")}
	if F < RISE:   # ค้างท่าฟันตัดสิน (zanshin) ระหว่างไฟ → เถ้า
		return {"cx": x_fin, "key": "pls_u_finish_0", "sy": 0.95 if F < LAND + 2 else 1.0, "sx": 1.04 if F < LAND + 2 else 1.0}
	return {"cx": x_fin, "key": "pls_atk_bl_0" if F < RISE + 4 else "pls_idle_bl_%d" % posmod(F / 4, 4)}

## ความโปร่งของ Rion: หายเป็นถ่านท้ายการพุ่ง โผล่ใหม่ต้นการพุ่ง
func _alpha(f: float) -> float:
	var k := _dash_k(f)
	if k < 0:
		return 1.0
	var u := (f - CHG1 - k * DASH) / DASH
	return minf(1.0, minf(u * 4.0 + 0.2, (1 - u) * 4.0 + 0.1))

## ไฟ 0–1 · เถ้า 0–1
func _fire(f: float) -> float:
	if f < FIRE0:
		return 0.0
	return minf(1.0, (f - FIRE0) / 4.0) * (1.0 - clampf((f - ASH0) / 8.0, 0.0, 1.0))

func _ash(f: float) -> float:
	if f < ASH0 - 2:
		return 0.0
	return minf(1.0, (f - ASH0 + 2) / 8.0) * (1.0 - clampf((f - ASH1) / 6.0, 0.0, 1.0))

func frame(f0: float, F0: int, fresh: bool) -> void:
	var f := f0
	var F := F0
	world_stop(F >= HANG0 and F < DROP)
	# จอ: ชาร์จแดงเข้ม → พุ่งมืด → ไฟส้ม → เถ้าเทา
	var tint := Color("#2a0800")
	var dm := 0.0
	if F >= STEP1 and F < FIRE0:
		dm = 0.45 * minf(1.0, (f - STEP1) / 8.0)
	elif F >= FIRE0:
		dm = 0.45 * clampf(1 - maxf(0.0, f - ASH1) / 8.0, 0.0, 1.0)
		tint = Color("#3a1400").lerp(Color("#1a1a1e"), clampf((f - ASH0) / 8.0, 0.0, 1.0))
	dim_to(dm, tint)
	var dl := -1
	for h in hit_f:
		if F >= int(ceil(h)):
			dl = F - int(ceil(h))
	var shk: float = BM.shk * (1 - dl / 5.0) if dl >= 0 and dl < 5 else 0.0
	if F == LAND - 1 or (F >= LAND - 1 and F < LAND + 6):
		shk = maxf(shk, 4.0 * (1 - (f - LAND + 1) / 7.0))
	if F >= FIRE0 and F < ASH0:
		shk = maxf(shk, 1.0 * _fire(f))
	if F >= STEP1 + 6 and F < CHG1:
		shk = maxf(shk, 0.5)
	shake(F, shk)
	# มอน: ผงะทุกครั้ง · ไฟ = ย้อมส้มเต้น · เถ้า = ย้อมเทา + ล้มสลายถ้าตาย
	var hurt := F >= int(ceil(hit_f[0])) and F < ASH1
	var flash := 0.0
	for h in hit_f:
		if F == int(ceil(h)):
			flash = 0.25 if foe.begins_with("B") else 0.45
	var mt := Color.WHITE
	var amt := flash
	if F >= FIRE0 and F < ASH0 + 4:
		mt = Color("#ff7a20")
		amt = maxf(amt, 0.35 * _fire(f) * (0.75 + 0.25 * sin(f * 1.7)))
	elif F >= ASH0 + 4:
		mt = Color("#8a8680")
		amt = 0.55 * clampf((f - ASH0 - 4) / 6.0, 0.0, 1.0) * (1.0 if kill16 else maxf(0.0, 1 - (f - ASH1) / 6.0))
	show_mon(hurt_key() if hurt else idle_key(f), mon_kb(f), amt, mt)
	mon.modulate.a = 1.0
	mon.material.set_shader_parameter("dissolve", 0.0)
	if kill16 and F >= ASH0 + 4:   # ทรุดตามแนวแผลแล้วสลายเป็นเถ้า
		var k := f - ASH0 - 4
		mon.scale.y = maxf(0.7, 1 - k * 0.015)
		mon.material.set_shader_parameter("dissolve", clampf(k / 14.0, 0.0, 1.0))
	var g := geo(f)
	set_rion(rion, g, _alpha(f))
	rion_ghosts(f, F)
	if fresh:
		if F == STEP1:
			dust_at(x_c + 6, 1.0, 1.0)
		for k in 4:   # โผล่/หายเป็นถ่าน
			var s := CHG1 + k * DASH
			if F == s:
				burst(Vector2(x_r - 16, G - 36), F, Color("#ff9a40"))
				dust_at(x_r - 8, 1.0, 0.8)
			if F == s + DASH - 1:
				puff(Vector2(x_l - 6, G - 30))
		for i in hit_f.size():
			if F == int(ceil(hit_f[i])):
				var p := (star_pts[i] + star_pts[(i + 1) % 5]) * 0.5
				debris_at(p, "คม", F, 0.7 if i < 4 else 1.3)
				burst(p, F, Color("#ffb060") if i < 4 else Color.WHITE)
		if F == LAND:
			dust_at(x_fin, 1.0, 1.6)
			dust_at(x_fin, -1.0, 1.6)
		if F >= FIRE0 and F < ASH0 and (F - FIRE0) % 3 == 0:
			burst(vis.get_center() + Vector2(fb_hash(F, 2, 1) * 30 - 15, fb_hash(F, 3, 1) * 30 - 15), F, Color("#ff7a20"))
		var bf := F - hold1 + HOP0
		if F >= hold1:   # ฝุ่นกระโดดถอยของเครื่องฟัน
			var t0 := HOP0
			for h in HOPS:
				if h.has("skid"):
					for kk in range(0, h.skid - 2, 2):
						if bf == t0 + kk:
							dust_at(g.cx + 6, 1.0, 0.9 - kk * 0.08)
					t0 += h.skid
					continue
				if bf == t0 + 1:
					dust_at(g.cx - 6, -1.0, 0.4 + h.d)
				t0 += h.c + h.a
				if bf == t0:
					dust_at(g.cx + 6, 1.0, 0.4 + h.d * 1.4)
				t0 += h.l
	# ตัวหนังสือ
	var b0 := int(bubble_at.x)
	var b1 := int(bubble_at.y)
	show_bubble(bubble_name + "!", g.cx, maxf(14.0, G - g.lift - 74), F - b0, (1.0 if F < b1 - 3 else (b1 - f) / 3.0) if F >= b0 and F < b1 else 0.0)
	var cx := vis.get_center().x
	var ty := maxf(26.0, vis.position.y - 6)
	var words := ["ฉัวะ!", "แคว้ง!", "แฉ่บ!", "ซวบ!", "ขาด!!" if kill16 else "ฉับ!!"]
	for i in hit_f.size():   # ตัวเลขทีละครั้ง: ครั้งถัดไปขึ้นแทนที่ (ไม่กองซ้อน 5 ตัว)
		var d := F - int(ceil(hit_f[i]))
		var nxt := (F - int(ceil(hit_f[i + 1]))) if i < hit_f.size() - 1 else -1
		if nxt < 0 and d >= 0 and d < 12:
			word(words[i], maxf(4, cx - 64), maxf(14, vis.position.y - 30 - mini(4, d)), Color("#ffe0b0") if i < 4 else Color.WHITE, 12 if i < 4 else 15)
		pop(dmg, maxf(16, cx - 4 + (i % 2) * 6), ty - (i % 2) * 4, d if nxt < 0 and F < FIRE0 else -1, Color("#ffd0a0"), "%d/5" % (i + 1), Color("#ffb070"))
	var dt := F - FIRE0
	if dt >= 0 and dt < 30:   # ยอดรวมตอนดาวลุก
		pop(total, maxf(16, cx - 4), ty - 4, mini(dt, 14) if dt < 22 else dt - 8, Color("#ffb040"), "รวม 5 ครั้ง" + (" · " + aff_tag() if aff_tag() != "" else ""), Color("#ffd27a"))
	if F >= FIRE0 and F < FIRE0 + 14:
		word("พรึ่บ!!", clampf(cx + 22, 4, W - 70), maxf(14, vis.position.y - 34 - mini(5, F - FIRE0)), Color("#ffb040"), 18, 4)

func rion_ghosts(f: float, F: int) -> void:
	var k := _dash_k(f)
	if k >= 0:   # ร่างติดตาสีถ่าน
		for j in [3, 2, 1]:
			var gg := geo(f - j * 0.8)
			if _dash_k(f - j * 0.8) == k:
				ghost(gg, 0.16 * (4 - j), Color("#ff6a20"), 0.6)
	if F >= DROP and F < LAND:
		ghost(geo(f - 1), 0.3, Color("#ffd0a0"), 0.5)
		ghost(geo(f - 2), 0.15, Color("#ffd0a0"), 0.5)

# ── วาด ───────────────────────────────────────────
func _ember(n: Node2D, x: float, y: float, a: float, s := 1.0) -> void:
	px(n, x, y, Color(1, 0.55 + 0.4 * s * 0.5, 0.15, a), 2 if s > 0.7 else 1, 2 if s > 0.7 else 1)

## พายุไฟ/เถ้าหมุนรอบตัวเป้า (กรวยเกลียวสูงถึงขอบจอบน) · back = ครึ่งหลัง (วาดหลังมอน)
func _storm(n: Node2D, f: float, back: bool) -> void:
	var fi := _fire(f)
	var as_ := _ash(f)
	if fi <= 0.0 and as_ <= 0.0:
		return
	var c := Vector2(vis.get_center().x, G - 2)
	var hgt := 140.0
	var ash_mix := clampf((f - ASH0 + 2) / 8.0, 0.0, 1.0)
	var grow := minf(1.0, (f - FIRE0) / 5.0)   # กรวยพุ่งขึ้นจากพื้นตอนลุก
	var spin := f * (0.5 - 0.3 * ash_mix)
	var wide := vis.size.x * 0.5 + 10
	# ริบบิ้นเกลียว 5 เส้น (อ่านเป็นพายุหมุน)
	for bnd in 5:
		for k in 70:
			var ph := k / 69.0
			if ph > grow:
				break
			var a := spin * 1.3 + bnd * TAU / 5.0 + ph * 7.0
			var front := sin(a) > 0
			if front == back:
				continue
			var r := 8 + pow(ph, 1.1) * (wide + 34) + ash_mix * 14 * ph
			var x := c.x + cos(a) * r
			var y := c.y - ph * hgt + sin(a) * (3 + r * 0.14)
			var heat := 1 - ph
			var fire_col := Color(1, 0.35 + 0.55 * heat, 0.08 + 0.35 * heat * heat)
			var ash_col := Color(0.8, 0.78, 0.74).lerp(Color(0.3, 0.29, 0.3), float(bnd % 2))
			var col := fire_col.lerp(ash_col, ash_mix)
			col.a = clampf((fi * 0.95 + as_ * 1.0) * (0.45 + 0.65 * sin(PI * minf(1.0, ph * 1.15))) * (1.0 if front else 0.5), 0.0, 1.0)
			var sz := 3.0 + 2.0 * heat * (1 - ash_mix)
			px(n, x - sz / 2, y - sz / 2, col, ceil(sz), ceil(sz))
	# เปลวเม็ดหมุนตามกรวย
	for k in 220:
		var ph := fmod(f * (0.03 - 0.015 * ash_mix) + fb_hash(k, 1, 1), 1.0) * grow
		var a := spin * (1.6 - ph * 0.7) + k * 2.399
		var front := sin(a) > 0
		if front == back:
			continue
		var r := 6 + pow(ph, 1.1) * (wide + 30) * (0.6 + 0.4 * fb_hash(k, 2, 2)) + ash_mix * 12 * ph
		var x := c.x + cos(a) * r
		var y := c.y - ph * hgt + sin(a) * (3 + r * 0.14)
		var heat := 1 - ph
		var col := Color(1, 0.3 + 0.65 * heat * heat, 0.06 + 0.4 * heat * heat * heat).lerp(Color(0.82, 0.8, 0.76).lerp(Color(0.28, 0.27, 0.28), fb_hash(k, 2, 3)), ash_mix)
		col.a = clampf((fi + as_ * 1.1) * sin(PI * minf(1.0, ph * 1.1 + 0.05)) * (1.0 if front else 0.55), 0.0, 1.0)
		var sz := 2.0 + 3.0 * heat * (1 - ash_mix) + fb_hash(k, 3, 2) * 2.0 + ash_mix
		px(n, x - sz / 2, y - sz / 2, col, ceil(sz), ceil(sz * (1.4 - 0.5 * ash_mix)))
	if not back and fi > 0.05:   # แกนร้อนกลางกรวย + ลิ้นไฟจากพื้น
		for j in 10:
			var y := c.y - 6 - j * 12 * grow
			disc(n, c.x + sin(f * 0.7 + j) * 2, y, 12 - j * 0.6, Color(1, 0.85, 0.4, 0.16 * fi))
		for k in 14:
			var x := c.x - wide - 10 + k * (wide * 2 + 20) / 13.0
			var h := (16 + fb_hash(k, floor(f / 2), 4) * 30) * fi
			for j in int(h / 2):
				var u := j / maxf(1.0, h / 2)
				var w := maxf(1.0, 5 * (1 - u))
				var col := Color(1, 0.88 - 0.6 * u, 0.3 - 0.25 * u, 0.9 * (1 - u) * fi)
				px(n, x + sin(f * 0.8 + k + u * 3) * 2.5 * u - w / 2, c.y - j * 2, col, w, 2)
	if not back and as_ > 0.05:   # ก้อนเถ้าฟุ้งรอบฐาน
		for k in 10:
			var a := spin * 0.6 + k * 0.63
			var r := wide + 10 + k % 3 * 6
			disc(n, c.x + cos(a) * r, c.y - 10 - fb_hash(k, 4, 4) * 50 * as_, 7 + fb_hash(k, 5, 5) * 7, Color(0.55, 0.54, 0.52, 0.32 * as_))

func draw_back(n: Node2D) -> void:
	_storm(n, t / SEC, true)

func fx(n: Node2D, f: float) -> void:
	var F := int(floor(f))
	var g := geo(f)
	# ชาร์จ: พื้นร้อน · ถ่านลอยขึ้นรอบตัว · มีดร้อนแดง
	if F >= STEP1 and F < CHG1 + 2:
		var u := clampf((f - STEP1) / (CHG1 - STEP1), 0.0, 1.0)
		var out := 1.0 if F < CHG1 else 1 - (f - CHG1) / 2.0
		for i in range(-24, 25, 2):
			var k := 1 - absf(i) / 24.0
			px(n, x_c + i - 2, G - 1, Color(1, 0.35, 0.05, 0.45 * k * u * out * (0.8 + 0.2 * sin(f + i))), 2, 1)
		for k in 18:
			var ph := fmod(f * 0.05 + fb_hash(k, 4, 1), 1.0)
			var r := 10 + fb_hash(k, 5, 2) * 18
			_ember(n, x_c - 2 + sin(k * 1.7 + f * 0.1) * r, G - 2 - ph * 70, sin(PI * ph) * u * out, fb_hash(k, 6, 3))
		var hand := Vector2(g.cx - 4, G - 30)   # มีดกลับด้านหลังสะโพก
		disc(n, hand.x, hand.y, 3 + 3 * u, Color(1, 0.4, 0.1, 0.35 * u * out))
		disc(n, hand.x, hand.y, 1.5 + u, Color(1, 0.85, 0.5, 0.8 * u * out))
	# เส้นทางพุ่ง: เส้นถ่านระดับกลางตัวเป้า
	var k := _dash_k(f)
	for j in 4:
		var s := CHG1 + j * DASH
		var q := f - s
		if q >= 1 and q < DASH + 4:
			var al := minf(1.0, q / 2.0) * (1.0 if q < DASH else maxf(0.0, 1 - (q - DASH) / 4.0))
			var y: float = vis.get_center().y + [-6.0, 0.0, 12.0, -2.0][j]
			var x0 := x_r - 10
			var x1 := x_r - 10 + (x_l - x_r) * minf(1.0, q / DASH)
			for i in int(absf(x1 - x0) / 2):
				var xx := x0 - i * 2
				px(n, xx, y + sin(i * 0.5) * 0.5, Color(1, 0.6, 0.25, al * 0.7 * (0.4 + 0.6 * i * 2 / maxf(1.0, absf(x1 - x0)))), 2, 1)
	# รอยดาวบนตัวเป้า: เกิดทีละเส้นตามครั้งที่โดน · ไฟ = ลุกสว่าง · เถ้า = ดำมอด
	var fi := _fire(f)
	var ash_mix := clampf((f - ASH0) / 8.0, 0.0, 1.0)
	for i in hit_f.size():
		var d := f - hit_f[i]
		if d < 0:
			continue
		var a: Vector2 = star_pts[i] + Vector2(mon_kb(f), 0)
		var b: Vector2 = star_pts[(i + 1) % 5] + Vector2(mon_kb(f), 0)
		var al := minf(1.0, (d + 1) / 2.0) * (1.0 if f < ASH1 else maxf(0.0, 1 - (f - ASH1) / 6.0))
		if al <= 0:
			continue
		var th := 2.0 + (2.0 if i == 4 else 0.0) + 2.0 * fi
		var glow := Color(1, 0.55, 0.15, 0.4 * al * (0.4 + fi)).lerp(Color(0.2, 0.2, 0.22, 0.5 * al), ash_mix)
		var core := Color(1, 0.95, 0.8, al).lerp(Color(0.1, 0.1, 0.12, al), ash_mix)
		for s in 24:
			var u := s / 23.0
			var p := a + (b - a) * u
			px(n, p.x - th, p.y - th, glow, th * 2, th * 2)
			px(n, p.x - 1, p.y - 1, core, 2, 2)
	if F >= DROP - 1 and F < LAND + 3:   # ฟันตัดสิน: เส้นดิ่งสว่างทั้งจอ
		var q := f - (LAND - 1)
		var al := 1.0 if q < 1 else maxf(0.0, 1 - q / 3.0)
		if q >= -1:
			px(n, vis.get_center().x - 2, 0, Color(1, 0.95, 0.85, al * 0.9), 4, G)
			px(n, vis.get_center().x - 6, 0, Color(1, 0.6, 0.2, al * 0.35), 12, G)
	_storm(n, f, false)
	# เถ้าร่วงทั้งจอ
	var as_ := _ash(f)
	if as_ > 0:
		for k2 in 60:
			var x := fmod(fb_hash(k2, 7, 1) * W + sin(f * 0.07 + k2) * 10 + f * 0.6, W + 20) - 10
			var y := fmod(fb_hash(k2, 8, 1) * H + f * (0.9 + fb_hash(k2, 9, 1) * 0.8), H)
			px(n, x, y, Color(0.75, 0.73, 0.7, 0.7 * as_), 2 if k2 % 4 == 0 else 1, 1)
	if F >= FIRE0 and F < FIRE0 + 3:   # จอวาบส้มตอนดาวลุก (เบา)
		px(n, -8, -8, Color(1, 0.6, 0.2, 0.18 * (1 - (f - FIRE0) / 3.0)), W + 16, H + 16)

func snd(F: int) -> void:
	step_snd(F, IDLE, STEP1)
	if F == STEP1:   # ชาร์จ: เสียงต่ำบวม + ไฟปะทุ
		play_sfx("uk_charge", [T(1.0, "sine", 40, 90, 0.5, 0, 0.5), N(0.9, "bandpass", 300, 1600, 0.3, 1.2, 0, {"attack": 0.6})])
	for k in 4:
		if F == CHG1 + k * DASH:   # พุ่ง: หวีด
			play_sfx("uk_dash%d" % k, [N(0.18, "bandpass", 900 + k * 300, 3200 + k * 200, 0.45, 2.5, 0, {"attack": 0.02})])
	for i in hit_f.size():
		if F == int(ceil(hit_f[i])):
			if i < 4:
				play_sfx("uk_hit%d" % i, [N(0.07, "highpass", 3600 + i * 200, 1800, 0.6, 2), N(0.14, "bandpass", 3000 + i * 250, 2000, 0.3, 10, 0.01), T(0.2, "sine", 150 - i * 15, 50, 0.4, 0, 0.002)])
			else:   # ฟันตัดสิน: หนักสุด
				sfx_hit(true)
				play_sfx("uk_final", [T(0.6, "sine", 70, 28, 0.8, 0, 0.003, {"drive": true}), N(0.4, "lowpass", 2000, 150, 0.6, 1.2)])
	if F == HANG0:   # ค้างฟ้า: เงียบ เหลือลมหวีดบาง
		play_sfx("uk_hang", [N(0.35, "highpass", 5000, 7000, 0.12, 3)])
	if F == FIRE0:   # ดาวลุก → พายุไฟคำราม
		play_sfx("uk_fire", [N(1.0, "lowpass", 400, 1800, 0.7, 1.0, 0, {"attack": 0.05}), N(0.9, "bandpass", 900, 300, 0.4, 1.5, 0.1), T(0.8, "sine", 55, 40, 0.5, 0, 0.01)])
	if F > FIRE0 and F < ASH0 and (F - FIRE0) % 4 == 0:   # ไฟปะทุแตก
		play_sfx("uk_crackle", [N(0.05, "highpass", 2500, 4000, 0.25, 4)])
	if F == ASH0:   # ไฟมอด → ลมเถ้า (ซ่า ค่อยจาง)
		play_sfx("uk_ash", [N(1.4, "bandpass", 1400, 500, 0.4, 0.8, 0, {"attack": 0.3})])
	if F == RISE + 2:   # ลุกตั้งท่า
		play_sfx("uk_set", [T(0.06, "triangle", 900, 700, 0.1)])
