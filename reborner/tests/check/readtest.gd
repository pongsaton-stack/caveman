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
	ps.reads = {"M1": {"name": "x", "p": 1, "need": 4, "on": true}, "M2": {"name": "y", "p": 4, "need": 4, "on": true}}
	check(not ps.toggle_read("M1"), "ยังไม่ครบ ถอดไม่ได้")
	check(ps.toggle_read("M2") and not bool(ps.reads["M2"]["on"]), "ครบแล้ว ถอดได้")
	ps.reads["M3"] = {"name": "z", "p": 2, "need": 2, "on": true}
	check(not ps.toggle_read("M2"), "ช่องเต็ม (%d/%d) ติดตั้งเพิ่มไม่ได้" % [ps.reads_on(), ps.read_slots()])
	var ps2 := PlayerState.new(); ps2.from_dict(ps.to_dict())
	check(ps2.reads.size() == 3 and int(ps2.reads["M1"]["p"]) == 1 and not bool(ps2.reads["M2"]["on"]), "เซฟ/โหลดท่าหลบครบ")
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
	h.reads["M99"] = {"name": f.signature, "p": 0, "need": 3, "on": false}
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 1, "โดนท่าเด่น แต้มอ่าน +1")
	h.guarding = true; h.counter_used = true
	b._strike(f, h, b._signature_tech(f), 1.0)
	b._strike(f, h, b._signature_tech(f), 1.0)
	check(int(h.reads["M99"]["p"]) == 3, "ตั้งรับ +2 และไม่เกินที่ต้องครบ")

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
