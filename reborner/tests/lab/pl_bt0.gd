extends "res://tests/lab/lab_stage.gd"
## ทุบ bt0 ไม้เบสบอล — ภาพ PixelLab ตามรายงานวิจัย (kwan 25 ต.ค. "ใช้ pixellab ปรับให้ตรงกับรายงาน ... สีหน้ามีอารมณ์มากกว่า flow")
## ง้างหลังไหล่ (pls_bat_0) → ง้างสุดไม้นอนหลัง (bat2_1) → ไม้ขึ้นหลังหัว (bat2_2) → ไม้ตั้งเหนือหัว ตะโกน (bat2_0) → กระทบลงเฉียง ตัวตั้งตรง (State BT_bat_impact)
## วิ่งเข้า pls_bat_run (run_bat) · ยืนหายใจ pls_bat_breath (idle_bat 0–1 วนสลับ) · ถอยด้วย pls_bat_hop (hop_bat2 · เฟรม 4 ขาซีดจาก clean() → ลอยใช้เฟรม 5) · ภาพแต่ละคลิปจัดวางคนละกรอบ → shift_x ดึงหมวกให้ตรงภาพยืน (วัดจากจุดกลางหมวก)
## (kwan 28 ต.ค. เอาท่าภาพ Flow ออกจากแลป → รวมฉาก flw_bt0 เดิมเข้าไฟล์นี้)
## จังหวะตามรายงานวิจัย bt0 (โดนเฟรม 22 · ง้าง ~10 เฟรม · ฟาดสั้น 4 เฟรม · ไม้จมค้าง 23–29): วิ่งเข้าแบกไม้บนไหล่แบบท่าฟัน bl0 (RUN 18 เฟรม = ช่วง load)
## → ฟาดต่อเนื่องตอนถึงตัว (ไม่ยืนง้างนิ่ง · รสนิยม 10 ต.ค.) → ไถลนิด → ไม้จมค้าง → กระโดดถอย 2 ครั้ง + ไถลแบบท่าฟัน → ยืนหายใจ
## (kwan 25 ต.ค. "หลังโจมตีให้ถอยแบบฟัน" · 26 ต.ค. "วิ่งไปโจมตีแบบฟัน เสร็จแล้วทำท่ายืนหายใจ")

const MX := 74
const END := 80
const IDLE := 4
const RUN := 18   # = HIT - IDLE (เท่า blc_bl0)
const HIT := 22
const FOLLOW := 25
const RET := 29   # เริ่มถอย
## กระโดดถอยแบบ HOPS ของ blc_bl0: ระยะ (สัดส่วน) · ย่อ · ลอย · ลง · สูง · skid = ไถลตั้งหลัก
const HOPS := [{"d": 0.5, "c": 2, "a": 9, "l": 2, "h": 16}, {"d": 0.3, "c": 2, "a": 7, "l": 2, "h": 12}, {"d": 0.2, "skid": 10}]
const POWER := 100   # techs.csv bt0
## ท่า → ภาพ · ปลายไม้ในภาพ (วัดจากพิกเซลเทา) · เลื่อนภาพแนวนอน (ชุดภาพที่จัดวางคนละกรอบ)
## ค่าเป็นรายการ = วนตาม idx (วิ่ง: ทีละเฟรม · หายใจ: ทุก 4 เฟรม)
func keys() -> Dictionary: return {"ready": ["pls_bat_breath_0", "pls_bat_breath_1"], "run": ["pls_bat_run_0", "pls_bat_run_1", "pls_bat_run_2", "pls_bat_run_3", "pls_bat_run_4", "pls_bat_run_5", "pls_bat_run_6", "pls_bat_run_7"], "lift": "pls_bat_0", "wind": "pls_bat2_1", "whip": "pls_bat2_2", "mid": "pls_bat2_0",
	"hit": "pls_bat_imp_0", "follow": "pls_bat_imp_0", "crouch": "pls_bat_hop_2", "air": "pls_bat_hop_5", "fall": "pls_bat_hop_5", "land": "pls_bat_hop_1"}
func tips() -> Dictionary: return {"wind": Vector2(116, 38), "mid": Vector2(84, 28), "hit": Vector2(31, 98)}
const SHIFT := {"run": -2.0, "lift": -20.0, "wind": -17.0, "whip": -20.0, "mid": -12.0, "hit": -15.0, "follow": -15.0, "crouch": 3.0, "air": 2.0, "fall": 2.0, "land": 1.0}
func shift_x(pose: String) -> float: return SHIFT.get(pose, 0.0)
func src_name() -> String: return "ภาพ PixelLab"
func skinnable() -> bool: return true

var near := 0.0
var cell := {}
var fe := {}

func tech_id() -> String: return "bt0"
func end_frame() -> int: return END
func stops() -> Array: return [[HIT, int(fe.get("hitstop_frames", 2)) * SEC]]
func caption() -> String: return "ทุบ (%s): วิ่ง → ฟาด → ถอย" % src_name()

func setup() -> void:
	place_monster(MX)
	cell = react("ทุบ")
	fe = feel(POWER)
	var tp: Vector2 = tips().hit
	var row := clampi(mh - (108 - int(tp.y)), 0, mh - 1)   # ระดับปลายไม้ตอนกระทบบนตัวมอน
	var edge := mx0 + roundf(mw * 0.8)
	for x in range(mw - 1, -1, -1):
		if solid(x, row):
			edge = mx0 + x
			break
	near = edge + (60 - tp.x - shift_x("hit")) - 4   # ไม้จมเข้าเนื้อ 4 จุด

func geo(f: float) -> Dictionary:
	var r := _geo(f)
	var pose: String = r.key
	var k: Variant = keys()[pose]
	r.key = k[int(r.get("idx", 0)) % k.size()] if k is Array else k
	r.cx += shift_x(pose)
	return r

func _geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "ready", "sx": 1.0, "sy": 1.0}
	if F < IDLE:   # ยืนหายใจ
		r.idx = F / 4
		return r
	if F < HIT:   # วิ่งเร่งเข้าแบบ blc_bl0 แบกไม้ (load) → ถึงตัวแล้วฟาดต่อเนื่องไม่หยุด
		var u := (f - IDLE) / RUN
		r.cx = home + (near - home) * (u * u * 0.4 + u * 0.6)
		r.lean = -0.04 * minf(1.0, u * 3)
		r.key = "run" if F < HIT - 4 else ("wind" if F < HIT - 3 else ("whip" if F < HIT - 1 else "mid"))
		r.idx = F - IDLE
		return r
	var slide := 3.0 * (1 - pow(1 - minf(1.0, (f - HIT) / 6.0), 2))   # ไถลนิดตามแรงส่ง (รายงาน: เท้าหน้ายันพื้น ตัวไม่เซ)
	if F < FOLLOW:
		r.cx = near - slide
		r.key = "hit"
		r.sy = 0.94 if F < HIT + 2 else 1.0
		return r
	if F < RET:   # ไม้จมค้างที่เป้า
		r.cx = near - slide
		r.key = "follow"
		return r
	var x0 := near - 3.0
	var at := RET
	var done := 0.0
	for h in HOPS:
		var span: int = h.skid if h.has("skid") else h.c + h.a + h.l
		if F < at + span:
			var q: float = f - at
			var xa: float = x0 + (home - x0) * done
			var xb: float = x0 + (home - x0) * (done + h.d)
			if h.has("skid"):   # ไถลตั้งหลัก: เร็วแล้วเบรก
				var u: float = minf(1.0, (q + 1) / (h.skid - 2.0))
				r.cx = xa + (xb - xa) * (1 - (1 - u) * (1 - u))
				r.key = "land" if q < 3 else ("crouch" if q < h.skid - 3 else "ready")
				return r
			if q < h.c:   # ย่อ
				r.cx = xa
				r.key = "crouch"
				r.sy = 0.96
				return r
			if q < h.c + h.a:   # ลอยถอยหลัง
				var u: float = (q - h.c + 1) / float(h.a)
				r.cx = xa + (xb - xa) * u
				r.lift = roundf(4 * float(h.h) * u * (1 - u))
				r.key = "air" if u < 0.5 else "fall"
				return r
			r.cx = xb   # ลง
			r.key = "land"
			r.sy = 0.94
			return r
		at += span
		done += h.d
	r.idx = F / 4   # กลับที่แล้วยืนหายใจ
	return r

## เฟรมที่กระโดดถอยแต่ละครั้งออกตัว / แตะพื้น (ฝุ่น + เสียง)
func hop_events() -> Dictionary:
	var ev := {}
	var at := RET
	for h in HOPS:
		if h.has("skid"):
			ev[at] = "skid"
			break
		ev[at + int(h.c)] = "hop"
		ev[at + int(h.c) + int(h.a)] = "land"
		at += int(h.c) + int(h.a) + int(h.l)
	return ev

## ตำแหน่งปลายไม้บนเวที
func tip(g: Dictionary, k: String) -> Vector2:
	var tp: Vector2 = tips()[k]
	return Vector2(g.cx + tp.x - 60, G - g.lift - (108 - tp.y))

## ปฏิกิริยามอนตามตาราง: ถอยตามแรงทุบ (shift) ใน cell.frames เฟรม · ร่างนุ่มยุบลึกแล้วเด้ง 3 รอบ · ปีกโดนทุบ = ร่วงลง
func _kb(F: int) -> float:
	var d := F - HIT
	if d < 0:
		return 0.0
	var fr := float(cell.get("frames", 8))
	return -roundf(float(cell.get("shift", 5)) * maxf(0.0, 1 - maxf(0.0, d - 2) / fr))

func frame(f: float, F: int, fresh: bool) -> void:
	var d := F - HIT
	shake(F, float(fe.shake_px) * (1 - d / float(fe.shake_frames)) if d >= 0 and d < int(fe.shake_frames) else 0.0)
	var fr := int(cell.get("frames", 8))
	var hurt := d >= 0 and d < fr + 4
	var fl := (0.6 if d == 0 else 0.3) if d >= 0 and d < int(fe.flash_frames) else 0.0   # จำนวนเฟรมตามตาราง feel · ไม่ขาวทึบทั้งตัว (ตรวจท่าเก่า 28 ต.ค.)
	var sy := 1.0
	var sx := 1.0
	if d >= 0 and d < fr:
		if body == "นุ่ม":   # แบนยุบรับแรงแล้วสั่นดีดคืน 3 รอบ (นุ่ม|ทุบ)
			var a := 0.22 * (1 - float(d) / fr)
			sy = 1 - a * cos(d * PI * 3 / fr) if d > 0 else 0.75
			sx = 1 + (1 - sy) * 0.6
		else:
			sy = 0.94 if d < 2 else 1.0
	show_mon(hurt_key() if hurt else idle_key(f), _kb(F), fl, Color.WHITE, sx, sy)
	mon.modulate.a = 1.0
	if kill and d > fr:   # ล้ม: ทรุดค้าง แล้วสลายเป็นผงเถ้า (KO beats ของตาราง · ไม่มีกองศพค้างจอ)
		var k := float(d - fr)
		mon.scale.y = maxf(0.6, 1 - k * 0.02)
		mon.modulate.a = maxf(0.0, 1 - maxf(0.0, k - 6) / 14.0)
	if body == "ปีก" and d >= 0:   # ปีกโดนทุบ = ร่วงลงพื้นเสมอ แล้วค่อยบินคืน (special.winged_fall)
		mon.position.y += roundf(10 * minf(1.0, d / 3.0) * maxf(0.0, 1 - maxf(0.0, d - 12) / 16.0))
	var g := geo(f)
	set_rion(rion, g)
	if F >= HIT - 3 and F <= HIT:
		for k in [2, 1]:
			ghost(geo(f - k), 0.14 * (3 - k))
	if F > RET and F < RET + 22 and geo(f).lift > 2:
		ghost(geo(f - 1), 0.12)
	var hp_pt := tip(geo(HIT), "hit")
	if fresh:
		if F >= IDLE + 2 and F < HIT - 4 and (F - IDLE - 2) % 3 == 0:   # ฝุ่นเท้าวิ่ง (แบบ blc_bl0)
			dust_at(g.cx + 6, 1.0, 0.45 + 0.4 * (F - IDLE) / RUN)
		if F == HIT:
			dust_at(near, -1.0, 1.0)
			burst(hp_pt, F, Color("#ffd27a") if hard_body() else Color("#fff0d0"))
			debris_at(hp_pt, "ทุบ", F)
		var ev: String = hop_events().get(F, "")
		if ev != "":
			dust_at(g.cx, 1.0, 0.8 if ev == "hop" else 1.0)
		if kill and F == HIT + int(cell.get("frames", 8)) + 8:
			puff(Vector2(mcx, G - mh * 0.4))
	if d >= 0 and d < 12:
		word("เปรี้ยง!!" if hard_body() else "ปึ้ก!!", maxf(4, mon_rect().get_center().x + _kb(F) - 64), maxf(14, mon_rect().position.y - 30 - mini(4, d)), Color("#ffd24a") if hard_body() else Color.WHITE)   # ซ้ายของตัวเลข
	show_bubble("ทุบ!", g.cx, maxf(14, G - g.lift - 74), F - (HIT - 8), (1.0 if F < HIT else (HIT + 3 - f) / 3.0) if F >= HIT - 8 and F < HIT + 3 else 0.0)
	pop(dmg, maxf(16, mon_rect().get_center().x + _kb(F) - 4), maxf(26.0, mon_rect().position.y - 6), d, Color.WHITE, aff_tag(), aff_col())   # เหนือตัวมอนจริง (ตรวจท่าเก่า 28 ต.ค.)

## ชั้นกลาง: รอยตามวัสดุตรงจุดทุบ — ร้าวใยแมงมุม (ร่างแข็ง) · รอยช้ำ (เนื้อ/ปีก) · ร่างนุ่มไม่มีรอย
func draw_mid(n: Node2D) -> void:
	var F := int(floor(t / SEC))
	var d := F - HIT
	var life := int(cell.get("mark_life", 0))
	if d < 0 or life <= 0 or d > life:
		return
	var kb := _kb(F)
	var p := tip(geo(HIT), "hit")
	var al := (1.0 - maxf(0.0, d - life * 0.6) / (life * 0.4)) * mon.modulate.a   # มอนสลายแล้ว รอยหายตาม
	var mark: String = cell.get("mark", "none")
	if mark.contains("crack") or mark.contains("dent"):
		for b in 7:
			var an := TAU * b / 7 + (fb_hash(b, 4, 1) - 0.5) * 0.6
			var x := 0.0
			var y := 0.0
			for s in mini(9, 2 + d * 2):
				an += (fb_hash(b, s, 2) - 0.5) * 0.7
				x += cos(an) * 1.5
				y += sin(an) * 1.5
				var sx := int(roundf(p.x - mx0 + x))
				var sy := int(roundf(p.y - (G - mh) + y))
				if solid(sx, sy):
					px(n, mx0 + kb + sx, G - mh + sy, Color(26 / 255.0, 16 / 255.0, 12 / 255.0, 0.85 * al))
	elif mark.contains("bruise"):
		for i in 9:
			var sx := int(roundf(p.x - mx0 - 2 + (i % 3) * 1.5))
			var sy := int(roundf(p.y - (G - mh) - 1 + (i / 3) * 1.5))
			if solid(sx, sy):
				var c := rgb(sx, sy).darkened(0.45)
				c.a = 0.7 * al
				px(n, mx0 + kb + sx, G - mh + sy, c, 2, 2)

## ชั้นหน้า: เงา · รอยวงไม้ (ทึบหนา ไม่ใช่เส้นคม) ช่วงฟาดลง
func draw_fx(n: Node2D) -> void:
	var f := t / SEC
	var F := int(floor(f))
	var g := geo(f)
	if g.lift > 2:
		for i in range(-8, 9):
			if absi(i) < 8 * maxf(0.35, 1 - g.lift / 60.0):
				px(n, g.cx + i * 1.6, G - 1, Color(40 / 255.0, 30 / 255.0, 24 / 255.0, 0.4), 2, 1)
	var d := F - (HIT - 2)
	if d >= 0 and d < 6:   # วงไม้: ปลายไม้ ง้าง → กลางวง → กระทบ (โค้งผ่านเหนือหัว)
		var a := tip(geo(HIT - 3), "wind")
		var b := tip(geo(HIT - 1), "mid")
		var c := tip(geo(HIT), "hit")
		var prog := minf(1.0, (f - (HIT - 2)) / 2.0)
		var al := 0.75 * (1 - maxf(0.0, f - HIT) / 4.0)
		for i in 24:
			var u := float(i) / 23 * prog
			var q := a.lerp(b, u).lerp(b.lerp(c, u), u)
			var w := 1.0 + 3.0 * sin(PI * u)
			px(n, q.x - w / 2, q.y - w / 2, Color(1, 1, 1, al * (0.4 + 0.6 * u)), ceil(w), ceil(w))

func sounds(F: int) -> void:
	var big := foe == "B1"
	if F >= IDLE and F < HIT - 4 and (F - IDLE) % 3 == 0:   # ฝีเท้าวิ่ง ดังขึ้นตามความเร็ว (แบบ blc_bl0)
		var pk := snappedf(0.35 + 0.25 * (F - IDLE) / RUN, 0.05)
		play_sfx("step%s" % pk, [N(0.07, "lowpass", 900, 200, pk, 1)])
	if F == HIT - 3:   # ไม้หวดลม (ทื่อ ต่ำกว่าเสียงมีด)
		play_sfx("whoosh", [N(0.22, "bandpass", 380, 1100, 0.4, 2)])
	if F == HIT:   # ทุบ: กระแทกต่ำ (ไม่มีกริ๊ง) + เสียงมอนตามร่าง
		sfx_hit(big, "CR")
		play_sfx("thud", [T(0.6, "sine", 120, 28, 1.0, 0, 0.002, {"drive": true})])
		sfx_mon(kill, 0.6 if big else 1.0)
		duck()
	match hop_events().get(F, ""):
		"hop":
			play_sfx("hop", [N(0.08, "lowpass", 700, 150, 0.3, 1)])
		"land":
			play_sfx("land", [N(0.09, "lowpass", 700, 150, 0.4, 1)])
		"skid":
			play_sfx("skid", [N(0.4, "lowpass", 1400, 300, 0.3, 2)])
