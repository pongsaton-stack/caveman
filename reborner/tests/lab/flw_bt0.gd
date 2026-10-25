extends "res://tests/lab/lab_stage.gd"
## ทุบ bt0 ไม้เบสบอล — ท่าแรกที่ใช้ภาพ Rion จาก Flow (Muse เจน 25 ต.ค. · tools/sprites/flow_to_px.py) + ตาราง feel/ปฏิกิริยารอบ 2
## จังหวะตามรายงานวิจัย bt0 (โดนเฟรม 22 · ง้าง ~10 เฟรม · ฟาดสั้น 4 เฟรม · ไม้จมค้าง 23–29): ย่อ → กระโดดเข้าพร้อมง้างกลางอากาศ (ไม่ยืนง้างนิ่ง · รสนิยม 10 ต.ค.)
## → ฟาดลงตอนเท้าแตะพื้น → ไถลนิด → ไม้จมค้าง → กระโดดถอย 2 ครั้ง + ไถลตั้งหลักแบบท่าฟัน bl0 (kwan 25 ต.ค. "หลังโจมตีให้ถอยแบบฟัน")
## ภาพ flw_bt_*: ready lift wind mid hit follow back (ผืน 120x112 เท้าแถว 108) · ถ้าภาพ Flow ไม่ผ่าน kwan → กลับไปเจน PixelLab (kwan 25 ต.ค.)

const MX := 74
const END := 70
const CROUCH := 6
const JUMP := 9
const HIT := 22
const FOLLOW := 25
const RET := 29   # เริ่มถอย
## กระโดดถอยแบบ HOPS ของ blc_bl0: ระยะ (สัดส่วน) · ย่อ · ลอย · ลง · สูง · skid = ไถลตั้งหลัก
const HOPS := [{"d": 0.5, "c": 2, "a": 9, "l": 2, "h": 16}, {"d": 0.3, "c": 2, "a": 7, "l": 2, "h": 12}, {"d": 0.2, "skid": 10}]
const POWER := 100   # techs.csv bt0
## ท่า → ภาพ · ปลายไม้ในภาพ (วัดจากพิกเซลเทา) · เลื่อนภาพแนวนอน (ชุดภาพที่จัดวางคนละกรอบ) — ฉาก PixelLab (pl_bt0.gd) แทนที่ฟังก์ชันเหล่านี้
func keys() -> Dictionary: return {"ready": "flw_bt_ready", "lift": "flw_bt_lift", "wind": "flw_bt_wind", "whip": "flw_bt_mid", "mid": "flw_bt_mid",
	"hit": "flw_bt_hit", "follow": "flw_bt_follow", "crouch": "flw_bt_ready", "air": "flw_bt_back", "fall": "flw_bt_back", "land": "flw_bt_ready"}
func tips() -> Dictionary: return {"wind": Vector2(80, 43), "mid": Vector2(17, 46), "hit": Vector2(15, 91)}
func shift_x(_pose: String) -> float: return 0.0
func src_name() -> String: return "ภาพ Flow"

var near := 0.0
var cell := {}
var fe := {}

func tech_id() -> String: return "bt0"
func end_frame() -> int: return END
func stops() -> Array: return [[HIT, int(fe.get("hitstop_frames", 2)) * SEC]]
func caption() -> String: return "ทุบ (%s): กระโดดง้างกลางอากาศ → ฟาดตอนแตะพื้น → ไถลตามแรง · ปฏิกิริยา%s|ทุบ" % [src_name(), body]

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
	r.key = keys()[pose]
	r.cx += shift_x(pose)
	return r

func _geo(f: float) -> Dictionary:
	var F := int(floor(f))
	var r := {"cx": float(home), "lift": 0.0, "key": "ready", "sx": 1.0, "sy": 1.0}
	if F < CROUCH:   # ยืนหายใจ (ยุบ 1 จุดทุก 4 เฟรม)
		r.sy = 0.985 if (F / 4) % 2 == 1 else 1.0
		return r
	if F < JUMP:   # ย่อสะสมแรง
		r.sy = 0.92
		r.sx = 1.04
		return r
	if F < HIT:   # กระโดดโค้งเข้า ยกไม้ → ง้างที่ยอด → เริ่มฟาดขาลง
		var tt := (f - JUMP + 1) / (HIT - JUMP)
		r.cx = home + (near - home) * (tt * tt * 0.35 + tt * 0.65)
		r.lift = roundf(4 * 24 * tt * (1 - tt))
		r.key = "lift" if F < JUMP + 3 else ("wind" if F < HIT - 3 else ("whip" if F < HIT - 1 else "mid"))
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
	var fl := 1.0 if d >= 0 and d < int(fe.flash_frames) else 0.0
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
		if F == JUMP:
			dust_at(home - 4, 1.0, 1.1)
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
		var wy := minf(hp_pt.y - 30, G - roundf(mh * 0.75) - 30)   # เหนือตัวเลขดาเมจ ไม่ทับ
		word("เปรี้ยง!!" if hard_body() else "ปึ้ก!!", maxf(4, mx0 + mw * 0.5 - 4), maxf(18, wy - mini(4, d)), Color("#ffd24a") if hard_body() else Color.WHITE)
	show_bubble("ทุบ!", g.cx, maxf(14, G - g.lift - 74), F - JUMP, (1.0 if F < HIT else (HIT + 3 - f) / 3.0) if F >= JUMP and F < HIT + 3 else 0.0)
	pop(dmg, maxf(52, mx0 + 8), G - roundf(mh * 0.75), d, Color.WHITE, aff_tag(), aff_col())

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
	if F == CROUCH:
		play_sfx("crouch", [N(0.06, "lowpass", 700, 150, 0.2, 1)])
	if F == JUMP:
		play_sfx("jump", [N(0.08, "lowpass", 700, 150, 0.35, 1)])
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
