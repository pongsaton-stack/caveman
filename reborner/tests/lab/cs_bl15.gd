extends "res://tests/lab/ma_hit.gd"
## คมสวน bl15 (kwan 28 ต.ค. "2" แบบผสม · ตามรายงานทีม R2: เคนโด คาเอชิวาซะ — รับให้ไหล พลิกข้อมือ แล้วฟันสวนในจังหวะเดียว ไม่ใช่บล็อกแข็งค้าง)
## ใช้เครื่องมอนโจมตีกลับ (ma_hit): มอนกระดึ๊บ 2 ครั้ง → ถีบพุ่งใส่ Rion
## Rion รอในท่าการ์ดผ่อน (ภาพเดิม pls_guard) → ตอนคมกระทบ พลิกข้อมือปัดให้ไหลออกข้าง (State BL15_roll · ประกายโลหะ)
## → 3 เฟรมต่อมาก้าวเฉียงฟันสวนทันที (ภาพเดิม pls_atk_bl_5 · โดน · ดาเมจของท่า) มอนกระเด็นหมุนกลับที่ → zanshin → ถอยกลับที่
## ห้ามมีเฟรมค้างระหว่างรับกับสวน (ทีม) · Rion ไม่เสีย HP

const CUT := HIT + 3   # สวนตรงจังหวะมอนเด้งกลับ (BACK)

var dmg_tech := 0

func guard() -> bool: return true
func tech_id() -> String: return "bl15"
func stops() -> Array: return [[HIT, 0.05], [CUT, 0.09]]
func caption() -> String: return "รอในการ์ดผ่อน → มอนพุ่งใส่ → พลิกข้อมือปัดให้ไหล → ก้าวเฉียงฟันสวนทันที → zanshin"

func setup() -> void:
	dmg_tech = dmg   # dmg จากตาราง DMG ของ bl15 (ma_hit.setup เขียนทับด้วยดาเมจของมอน)
	super.setup()
	dmg = dmg_tech

## ตำแหน่ง Rion ใหม่ (มอนใช้ของ ma_hit ตั้งรับ: ถูกดีดหมุนกลับที่)
func geo(f: float) -> Dictionary:
	var g := super.geo(f)
	var F := int(floor(f))
	var r := {"x": _home(), "key": "pls_guard_0", "flash": 0.0, "lift": 0.0, "lean": 0.0}
	if F < WAIT:
		r.key = "pls_idle_bl_%d" % posmod(F / 4, 4)
	elif F < GRD:   # การ์ดผ่อน: มีดเฉียงพร้อมรับ (ไม่ใช่กำแพง)
		r.key = "pls_guard_0"
	elif F < HIT:   # เห็นมอนถีบตัว → ย่อรับ
		r.key = "pls_guard_1"
	elif F < CUT:   # รับให้ไหล + พลิกข้อมือ (ถอยครึ่งก้าว)
		r.key = "pls_roll_0"
		r.x = _home() + 3 * minf(1.0, (f - HIT) / 2.0)
	elif F < CUT + 10:   # ฟันสวน ก้าวเฉียงออก (ลงหน้านิด) → zanshin
		var q := f - CUT
		r.key = "pls_atk_bl_5" if q < 4 else "pls_atk_bl_6"
		r.x = _home() + 3 - 12 * (1 - pow(1 - minf(1.0, q / 3.0), 2))
		r.lift = -3 * minf(1.0, q / 3.0)
		r.lean = -0.1 if q < 3 else 0.0
	elif F < CUT + 20:   # ถอยกลับที่
		var u := (f - CUT - 10) / 10.0
		r.key = "pls_atk_bl_7" if u < 0.5 else "pls_guard_0"
		r.x = _home() - 9 + 9 * (u * u * (3 - 2 * u))
		r.lift = -3 * (1 - u)
	else:
		r.key = "pls_idle_bl_%d" % posmod(F / 4, 4)
	g.r = r
	return g

func frame(f: float, F: int, fresh: bool) -> void:
	var d := F - HIT
	var dc := F - CUT
	shake(F, (1.2 * (1 - d / 3.0) if d >= 0 and d < 3 else 0.0) + (3.0 * (1 - dc / 5.0) if dc >= 0 and dc < 5 else 0.0))
	var g := geo(f)
	_place(mon, g.s, 1.0, (0.25 if foe.begins_with("B") else 0.6) if dc == 0 else 0.0)
	for k in 2:
		if F > LEAP and F < HIT:
			_place(mon_ghosts[k], geo(f - (k + 1)).s, 0.14 * (2 - k), 0.0)
		else:
			mon_ghosts[k].visible = false
	var r: Dictionary = g.r
	set_rion(rion, {"cx": r.x + 60, "lift": r.lift, "key": r.key, "lean": r.lean})
	if dc >= 0 and dc < 3:   # ร่างติดตาตอนก้าวสวน
		var r0: Dictionary = geo(f - 1).r
		ghost({"cx": r0.x + 60, "lift": r0.lift, "key": r0.key}, 0.2)
	if fresh:
		var xs := [float(MX), MX + (near - MX) * 0.32, MX + (near - MX) * 0.62]
		for e in [[H1, 0, 0.6], [L1, 1, 0.7], [H2, 1, 0.7], [L2, 2, 0.9], [LEAP, 2, 1.1]]:
			if F == e[0]:
				dust_at(xs[e[1]], 1.0, e[2])
				dust_at(xs[e[1]], -1.0, e[2])
		if F == HIT:
			burst(_hit_pt(geo(HIT).r), F, Color("#ffd24a"))
		if F == CUT:
			burst(Vector2(near + 4, G - 40), F, Color("#9ae6ff"))
			debris_at(Vector2(near, G - 36), "คม", F, 0.9)
			dust_at(_home() + 60 - 6, 1.0, 1.0)
	var hp := _hit_pt(r)
	if d >= 0 and d < 8:
		word("แก๊ง!", hp.x - 30, maxf(18, hp.y - 22 - mini(4, d)), Color("#ffe08a"), 10, 3)
	if dc >= 0 and dc < 14:
		word("สวน!", r.x + 60 - 16, G - 96 - mini(5, dc), Color.WHITE)   # เหนือหัว Rion ไม่ทับตัวเลขของมอน
	pop(dmg, maxf(16, near - 6), G - 82, dc, Color.WHITE, aff_tag(), aff_col())
	show_bubble("คมสวน!", _home() + 60, G - 74, F - GRD, (1.0 if F < CUT - 2 else (CUT - f) / 2.0) if F >= GRD and F < CUT else 0.0)   # หายก่อนคำ "สวน!" ขึ้นที่เดียวกัน

func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	var s: Dictionary = g.s
	if s.lift > 2:   # เงาพื้นตอนมอนลอย
		for i in range(-7, 8):
			if absi(i) < 7 * maxf(0.4, 1 - s.lift / 30.0):
				px(n, s.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.35), 2, 1)
	var d := f - HIT
	var hp := _hit_pt(geo(float(HIT)).r)
	if d >= 0 and d < 8:   # ประกายโลหะตอนคมแตะ · ไหลออกด้านข้างตามทางพลิก (ไม่กระเด็นตรง)
		for i in 10:
			var a := PI * (1.05 + fb_hash(i, 5, 1) * 0.4)
			var v := 1.5 + fb_hash(i, 5, 2) * 2.5
			var y := hp.y - 10 + sin(a) * v * d + 0.35 * d * d
			if y < G - 1:
				px(n, hp.x + cos(a) * v * d, y, Color.WHITE if d < 3 else Color("#ffd24a"), 2, 2)
		if d < 3:   # โค้งเบี่ยงทางคม (รับให้ไหล)
			slash_line(n, hp.x + 2, hp.y - 26, hp.x - 14, hp.y + 2, 2, 1.0, 1 - d / 3.0)
	var dc := f - CUT
	if dc >= 0 and dc < 3:   # รอยฟันสวนตามมือ
		var rx: float = g.r.x + 60
		slash_line(n, rx - 6, G - 62, rx - 40, G - 24, 4, minf(1.0, (dc + 1) / 1.5), 1 - dc / 3.0)
	if dc >= 0 and dc < 12:   # แผลเฉียง 45° บนมอน (ตามตัวที่กำลังกระเด็น)
		var cx: float = s.cx
		var cy: float = G - s.lift - mh * 0.45
		var sz := minf(16.0, mw * 0.2)
		var al := 1.0 if dc < 5 else maxf(0.0, 1 - (dc - 5) / 7.0)
		slash_line(n, cx + sz, cy - sz, cx - sz, cy + sz, 3, minf(1.0, (dc + 1) / 2.0), al)

func sounds(F: int) -> void:
	var p := 0.6 if foe == "B1" else 1.0
	if F == WAIT:
		play_sfx("squeeze", [N(0.25, "lowpass", 500, 160, 0.25, 3, 0, {"attack": 0.15})])
	if F == H1 or F == H2:
		play_sfx("boing", [T(0.16, "sine", 160, 420, 0.32, 0, 0.004)])
	if F == LEAP:
		play_sfx("leap", [T(0.2, "sine", 140, 520, 0.4, 0, 0.004), N(0.16, "bandpass", 500, 1800, 0.25, 2)])
	if F == L1 or F == L2:
		play_sfx("splat", [N(0.1, "lowpass", 900, 200, 0.35, 2)])
	if F == HIT:   # คมแตะ: โลหะเบา ไม่ตูม (รับให้ไหล)
		play_sfx("cs_parry", [T(0.14, "square", 2100, 1500, 0.1, 0, 0.002, {"lp": 5000}), N(0.12, "bandpass", 4200, 2800, 0.35, 12)])
	if F == CUT:   # สวน: ฟันหนัก
		sfx_hit(true)
		sfx_mon(false, p)
	if F == CUT + 13:
		play_sfx("splat", [N(0.1, "lowpass", 900, 200, 0.35, 2)])
