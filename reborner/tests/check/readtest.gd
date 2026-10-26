extends SceneTree
# อ่านทางหลบ + ประกายสวนกลับ (kwan 6 ต.ค. 2026) — กติกาหลักที่ห้ามพัง
var fails := 0

func check(ok: bool, what: String) -> void:
	if ok:
		print("ok   ", what)
	else:
		print("FAIL ", what)
		fails += 1

func mk(id: String, side: String, hp: int) -> Actor:
	var a := Actor.new()
	a.id = id; a.name = id; a.side = side
	a.tier = 20; a.max_hp = hp; a.hp = hp; a.atk = 40; a.def_val = 10; a.spd = 100
	a.signature = "ท่าทดสอบ"; a.comprehension = 3
	return a

func setup() -> Array:
	var td := TechDb.new()
	td.load_from("res://data/techs.csv")
	var b := Battle.new()
	b.techs = td
	var h := mk("hero", "ally", 500)
	h.is_hero = true; h.school = "คม"
	h.learned.append(td.root_of("คม").name)
	h.read_slots = 2
	var f := mk("M99", "foe", 5000)
	b.actors.append(h); b.actors.append(f)
	return [b, h, f]

func _initialize() -> void:
	# Actor: หลบได้ตาม % · ไม่ติดตั้ง = 0
	var a := Actor.new()
	a.reads = {"M1": {"name": "x", "p": 1, "need": 4, "on": true}, "M2": {"name": "y", "p": 4, "need": 4, "on": false}}
	check(is_equal_approx(a.dodge_chance("M1"), 0.25), "อ่าน 1/4 หลบ 25%")
	check(a.dodge_chance("M2") == 0.0, "ไม่ติดตั้ง หลบ 0%")
	check(a.dodge_chance("M3") == 0.0, "ยังไม่อ่าน หลบ 0%")

	# PlayerState: ช่อง = ช่องความจำ ÷ 2 · ถอด/ติดตั้งได้เมื่อครบ 100% · เซฟกลับมาเหมือนเดิม
	var ps := PlayerState.new()
	check(ps.read_slots() == ps.memory_slots() / 2, "ช่องท่าหลบ = ช่องความจำ ÷ 2 (%d)" % ps.read_slots())
	# kwan 7 ต.ค. 2026: ถอดได้ทุกเมื่อ % ค้าง · ติดตั้งต้องมีช่อง · ครบ 100% ฝาก/ถอนคลังได้เฉพาะที่จุดพัก
	ps.reads = {"M1": {"name": "x", "p": 1, "need": 4, "on": true}, "M2": {"name": "y", "p": 4, "need": 4, "on": true}}
	check(ps.toggle_read("M1") and not bool(ps.reads["M1"]["on"]) and int(ps.reads["M1"]["p"]) == 1, "ยังไม่ครบ ถอดได้ % ค้างไว้")
	check(ps.toggle_read("M1") and bool(ps.reads["M1"]["on"]), "ติดตั้งคืนได้เมื่อมีช่อง")
	ps.reads["M3"] = {"name": "z", "p": 2, "need": 2, "on": false}
	check(not ps.toggle_read("M3"), "ช่องเต็ม (%d/%d) ติดตั้งเพิ่มไม่ได้" % [ps.reads_on(), ps.read_slots()])
	ps.cell = ps.rest_cell + Vector2i(1, 0)
	check(not ps.store_read("M2"), "ไม่อยู่ที่จุดพัก ฝากคลังไม่ได้")
	ps.cell = ps.rest_cell
	check(not ps.store_read("M1"), "ยังไม่ครบ 100% ฝากคลังไม่ได้")
	check(ps.store_read("M2") and bool(ps.reads["M2"]["stored"]) and not bool(ps.reads["M2"]["on"]), "ครบแล้ว ฝากคลังที่จุดพักได้ · ถอดออกจากช่อง")
	check(not ps.toggle_read("M2"), "อยู่ในคลัง ติดตั้งจากเมนูไม่ได้")
	check(ps.toggle_read("M3"), "ฝากคลังแล้วคืนช่องให้ท่าอื่น")
	ps.cell = ps.rest_cell + Vector2i(1, 0)
	check(not ps.retrieve_read("M2"), "ไม่อยู่ที่จุดพัก ถอนคลังไม่ได้")
	ps.cell = ps.rest_cell
	ps.toggle_read("M3")
	check(ps.retrieve_read("M2") and not bool(ps.reads["M2"]["stored"]) and bool(ps.reads["M2"]["on"]), "ถอนคลังที่จุดพัก ติดตั้งเองเมื่อมีช่อง")
	ps.store_read("M2")
	var ps2 := PlayerState.new(); ps2.from_dict(ps.to_dict())
	check(ps2.reads.size() == 3 and int(ps2.reads["M1"]["p"]) == 1 and bool(ps2.reads["M2"]["stored"]) and not bool(ps2.reads["M3"]["on"]), "เซฟ/โหลดท่าหลบ + คลังครบ")
	# Insight ค้างข้ามศึก (Insight.CARRY_BATTLE) · เซฟ/โหลดได้ · เริ่มเกมใหม่ = 0
	var keep := ps2.reads.duplicate(true)
	var ins := Actor.new(); ins.insight = 30.0; ins.tier = ps2.prof
	ps2.absorb(ins, ps2.prof)
	check(is_equal_approx(ps2.insight, 30.0 * Insight.CARRY_BATTLE), "ศึกสูสี Insight ค้างข้ามศึกเต็ม (%.1f)" % ps2.insight)
	# ศัตรูอ่อนกว่ามาก: ส่วนที่ได้ในศึกนั้นค้างแค่บางส่วน · ส่วนที่ค้างมาก่อนไม่ถูกหัก
	ins.insight = 40.0 - 0.001
	ps2.absorb(ins, 0)
	var tf := (Formulas.threat(0, ps2.prof) - Formulas.THREAT_MIN) / (1.0 - Formulas.THREAT_MIN)
	var want := 30.0 + (10.0 - 0.001) * tf
	check(is_equal_approx(ps2.insight, want * Insight.CARRY_BATTLE), "ศัตรูอ่อน: ค้างเฉพาะส่วนน้อย ของเดิมไม่หาย (%.2f · TF %.2f)" % [ps2.insight, tf])
	# ใช้ Insight เต็มไปแล้วในศึก (จบน้อยกว่าตอนเริ่ม) = ที่เหลือได้มาในศึกนี้ทั้งหมด
	var held := ps2.insight
	ins.insight = 5.0
	ps2.absorb(ins, 0)
	check(is_equal_approx(ps2.insight, 5.0 * tf * Insight.CARRY_BATTLE) and held > 5.0, "ใช้ Insight เต็มแล้ว เศษที่เหลือคิดเป็นของศึกนี้")
	var ps3 := PlayerState.new(); ps3.from_dict(ps2.to_dict())
	check(is_equal_approx(ps3.insight, ps2.insight) and is_equal_approx(ps3.make_hero().insight, ps2.insight), "เซฟ/โหลด Insight แล้วเข้าศึกต่อ")
	ps2.reads = keep
	var h0 := ps2.make_hero()
	check(h0.reads.size() == 3 and h0.read_slots == ps2.read_slots(), "make_hero ส่งท่าหลบเข้าศึก")

	# ศึก: ครบ 100% + ติดตั้ง = ท่าเด่นไม่โดนเลย
	var s := setup(); var b: Battle = s[0]; var h: Actor = s[1]; var f: Actor = s[2]
	h.reads["M99"] = {"name": f.signature, "p": 3, "need": 3, "on": true}
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(h.hp == h.max_hp and b.dodges == 1, "อ่านครบ หลบท่าเด่นได้ (HP %d/%d)" % [h.hp, h.max_hp])
	b._strike(f, h, b._basic_tech(f), 1.0)
	check(h.hp < h.max_hp, "ตีธรรมดาไม่ใช่ท่าเด่น หลบไม่ได้")

	# ศึก: ยังไม่ครบ โดนท่าเด่น = แต้ม +1 · ตั้งรับ +2 · ไม่เกินที่ต้องครบ
	s = setup(); b = s[0]; h = s[1]; f = s[2]
	h.reads["M99"] = {"name": f.signature, "p": 0, "need": 3, "on": true}
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 1, "โดนท่าเด่น แต้มอ่าน +1")
	h.guarding = true; h.counter_used = true
	b._strike(f, h, b._signature_tech(f), 1.0)
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 3, "ตั้งรับ +2 และไม่เกินที่ต้องครบ")

	# ไม่ได้ติดตั้ง (ศึกก่อน) = โดนซ้ำก็ไม่ได้แต้ม · อ่านได้ในศึกนี้ (fresh) = สะสมได้แม้ไม่ติดตั้ง
	s = setup(); b = s[0]; h = s[1]; f = s[2]
	h.reads["M99"] = {"name": f.signature, "p": 1, "need": 3, "on": false}
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 1, "ไม่ได้ติดตั้ง โดนท่าเด่นไม่ได้แต้ม")
	h.reads["M99"]["fresh"] = true
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 2, "อ่านได้ในศึกนี้ ไม่ติดตั้งก็สะสมแต้มได้")
	var psf := PlayerState.new(); psf.absorb(h, h.tier)
	check(not psf.reads["M99"].has("fresh"), "จบศึก ป้าย 'อ่านในศึกนี้' หาย")
	h.reads["M99"] = {"name": f.signature, "p": 3, "need": 3, "on": false, "stored": true}
	var hp0 := h.hp
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(h.hp < hp0, "อยู่ในคลัง หลบไม่ได้")

	# ศึก: ไม่เคยอ่าน + โอกาสสูงสุด = เริ่มอ่าน ติดตั้งเองเมื่อมีช่อง
	var learned_any := false
	for i in 400:
		s = setup(); b = s[0]; h = s[1]; f = s[2]
		f.tier = 99
		b._strike(f, h, b._signature_tech(f), 1.0)
		if h.reads.has("M99"):
			learned_any = true
			check(bool(h.reads["M99"]["on"]) and int(h.reads["M99"]["p"]) == 1, "ประกายหลบ: ติดตั้งเอง และนับครั้งที่โดนเป็นแต้มแรก")
			check(b.read_glimmers == 1, "นับประกายหลบ")
			break
	check(learned_any, "ประกายหลบเกิดได้ (400 ครั้ง ศัตรูแข็งกว่ามาก)")

	# ประกายสวนกลับ: ตั้งรับ + Insight เต็ม → เรียนท่าใหม่ แล้วสวนทันที · ครั้งเดียวต่อการตั้งรับ
	s = setup(); b = s[0]; h = s[1]; f = s[2]
	h.guarding = true; h.counter_used = false; h.insight = Insight.THRESHOLD
	var n0 := h.learned.size(); var fhp := f.hp
	b._strike(f, h, b._basic_tech(f), 1.0)
	check(h.learned.size() == n0 + 1 and b.counter_glimmers == 1, "ประกายสวนกลับเรียนท่าใหม่ (%s)" % h.learned[-1])
	check(f.hp < fhp, "สวนกลับโดนศัตรูทันที (%d → %d)" % [fhp, f.hp])
	check(h.sp == 0, "สวนกลับไม่เสีย SP")
	h.insight = Insight.THRESHOLD
	b._strike(f, h, b._basic_tech(f), 1.0)
	check(b.counter_glimmers == 1, "ตั้งรับครั้งเดียว สวนได้ครั้งเดียว")

	# ไม่ตั้งรับ = ไม่มีสวนกลับ
	s = setup(); b = s[0]; h = s[1]; f = s[2]
	h.insight = Insight.THRESHOLD
	b._strike(f, h, b._basic_tech(f), 1.0)
	check(b.counter_glimmers == 0, "ไม่ตั้งรับ ไม่สวนกลับ")
	print("FAILS ", fails)
	quit()
