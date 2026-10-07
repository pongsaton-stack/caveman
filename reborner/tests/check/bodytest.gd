extends SceneTree
# ความเข้ากับร่างกาย (kwan เลือก 6 ต.ค. 2026): ข้อมูลครบ · ตารางถูกสาย · ไม่นับเป็นจุดอ่อน (ไม่ดันคิว)
var fails := 0

func check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if not ok: fails += 1

func _initialize() -> void:
	var td := TechDb.new()
	td.load_from("res://data/techs.csv")
	var bodies := ["เกราะ", "กระดูก", "หิน", "นุ่ม", "เนื้อ", "ปีก", "ไม้", "วิญญาณ", "กลไก"]
	var missing := []; var bad := []
	for r in CsvDb.load_csv("res://data/monsters.csv"):
		var b := Actor.body_of(str(r["monster_id"]))
		if b == "": missing.append(r["monster_id"])
		elif not bodies.has(b): bad.append(r["monster_id"])
	check(missing.is_empty() and bad.is_empty(), "มอนทุกตัวมีร่างกายที่รู้จัก (ขาด %s · ผิด %s)" % [missing, bad])
	var schools := td.schools()
	var badrow := []
	for r in CsvDb.load_csv("res://data/body_affinity.csv"):
		if not schools.has(str(r["school"])) or not bodies.has(str(r["body"])) or not [1, -1].has(int(r["sign"])):
			badrow.append("%s/%s" % [r["school"], r["body"]])
	check(badrow.is_empty(), "ตาราง body_affinity ใช้สาย/ร่างกาย/เครื่องหมายที่มีจริง %s" % [badrow])
	check(Actor.body_sign("ทุบ", "เกราะ") == 1 and Actor.body_sign("ทุบ", "นุ่ม") == -1 and Actor.body_sign("คม", "นุ่ม") == 0,
		"ทุบเข้าเกราะ · ทุบไม่เข้าของนุ่ม · คมกับของนุ่มปกติ")
	check(Actor.body_sign("", "เกราะ") == 0 and Actor.body_sign(Battle.SEIZE_SCHOOL, "เกราะ") == 0, "ตีธรรมดา/ท่ายึด ไม่มีผลร่างกาย")
	check(Formulas.body_mult(1) == Formulas.BODY_GOOD and Formulas.body_mult(-1) == Formulas.BODY_BAD and Formulas.body_mult(0) == 1.0, "body_mult ตามเครื่องหมาย")
	# ตีของที่เข้าทางไม่ดันคิว (ต่างจากจุดอ่อนธาตุ) · มอนสร้างเองให้ไม่มีจุดอ่อนธาตุมาปน
	var b := Battle.new(); b.techs = td
	var h := Actor.new(); h.id = "hero"; h.side = "ally"; h.is_hero = true; h.atk = 50; h.av = 100.0; h.max_hp = 100; h.hp = 100
	var f := Actor.new(); f.id = "X"; f.side = "foe"; f.body = "เกราะ"; f.max_hp = 9999; f.hp = 9999; f.def_val = 10
	b.actors.append(h); b.actors.append(f)
	b._strike(h, f, td.get_tech("ทุบ"), 1.0)
	check(is_equal_approx(h.av, 100.0), "ตีเข้าทางร่างกายไม่ดันคิว (AV %.1f)" % h.av)
	# ป้ายจอศึก อ่อนแอ/ต้านทาน (kwan 7 ต.ค. 2026): ธาตุ + ร่างกายรวมกัน · หักล้างกันได้
	var W := Formulas.WEAK_MULT; var R := Formulas.RESIST_MULT
	check(Battle._affinity(1.0, 1) == 1 and Battle._affinity(W, 0) == 1 and Battle._affinity(W, 1) == 1, "ร่างกายเข้าทาง/จุดอ่อนธาตุ = อ่อนแอ")
	check(Battle._affinity(1.0, -1) == -1 and Battle._affinity(R, 0) == -1 and Battle._affinity(0.0, 0) == -1, "ร่างกายไม่เข้า/ต้านธาตุ/ไม่ระคาย = ต้านทาน")
	check(Battle._affinity(W, -1) == 0 and Battle._affinity(R, 1) == 0 and Battle._affinity(1.0, 0) == 0, "ดีหนึ่งเสียหนึ่ง/ปกติ = ไม่ขึ้นป้าย")
	b.capture = true; b.events.clear()
	b._strike(h, f, td.get_tech("ทุบ"), 1.0)
	check(int(b.events[-1]["aff"]) == 1, "event ศึกส่ง aff ให้จอศึก (ทุบ×เกราะ = อ่อนแอ)")
	print("FAILS ", fails)
	quit()
