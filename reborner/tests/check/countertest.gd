extends SceneTree
# ท่าตั้งท่าสวน (คมสวน · effect=counter) + ต้นไม้สายคม 17 ท่า
var fails := 0
var td: TechDb
var by_id: Dictionary

func check(c: bool, what: String) -> void:
	print(("ok   " if c else "FAIL ") + what)
	if not c: fails += 1

func _hero(learned: Array) -> Actor:
	var h := Actor.new()
	h.id = "hero"; h.name = "Rion"; h.side = "ally"; h.is_hero = true
	h.tier = 30; h.max_hp = 9999; h.hp = 9999; h.atk = 60; h.def_val = 30; h.spd = 120
	h.max_sp = 60; h.sp = 60; h.school = "คม"
	for n in learned:
		h.learned.append(n)
	return h

func _battle(h: Actor, foe_ids: Array) -> Battle:
	var b := Battle.new()
	b.techs = td
	b.allow_glimmer = false   # ประกายสุ่มเปลี่ยนท่าที่ใช้ — ปิดเพื่อให้เห็นผลของท่าตั้งท่าสวนตรง ๆ
	b.capture = true
	b.actors.append(h)
	for id in foe_ids:
		b.actors.append(Actor.from_csv(by_id[id]))
	return b

func _count(b: Battle, key: String) -> int:
	var n := 0
	for e in b.events:
		if e.get(key, false): n += 1
	return n

func _initialize() -> void:
	td = TechDb.new()
	td.load_from("res://data/techs.csv")
	by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var counter := td.get_tech("คมสวน")

	var blade := td.all.filter(func(t): return t.school == "คม")
	check(blade.size() == 17, "สายคม 17 ท่า (%d)" % blade.size())
	var orphans := blade.filter(func(t): return t.parent != "" and td.get_tech(t.parent) == null)
	check(orphans.is_empty(), "ทุกท่าในสายคมมีท่าแม่อยู่จริง")
	check(counter != null and counter.is_counter() and counter.is_attack() and counter.is_usable(), "คมสวน = counter · นับเป็นท่าโจมตี")
	check(td.all.filter(func(t): return t.is_counter()).size() == 1, "มีท่า counter ท่าเดียว")
	for s in td.schools():
		if s != "คม":
			check(td.all.filter(func(t): return t.school == s).size() == 7, "สาย %s ยังมี 7 ท่า" % s)

	var learned: Array[String] = []
	learned.append(td.root_of("คม").name)
	while true:
		var c := td.candidates(learned, "คม", 99)
		if c.is_empty(): break
		learned.append(c[0].name)
	check(learned.size() == 17, "ไล่ candidates จากรากได้ครบ 17 ท่า (%d)" % learned.size())
	var early: Array[String] = []
	early.append("ฟัน"); early.append("เขี้ยวพุ่ง")
	var names := td.candidates(early, "คม", 20).map(func(t): return t.name)
	check(names.has("ตัดเอ็น") and not names.has("เขี้ยวผ่าเกราะ"), "prof 20: ตัดเอ็นออก · เขี้ยวผ่าเกราะ (28) ยังไม่ออก %s" % [names])

	var h := _hero(["ฟัน", "คมสวน"])
	var b := _battle(h, ["M15"])
	var foe: Actor = b.foes()[0]
	var foe_hp := foe.hp
	var av0 := h.av
	b.current = h
	b.player_act({"kind": "tech", "tech": counter, "target": null})
	check(h.counter_tech == counter, "ใช้คมสวน → ตั้งท่าสวน")
	check(foe.hp == foe_hp and b.dealt == 0, "ใช้คมสวน → ไม่มีดาเมจ")
	check(h.sp == 60 - counter.sp, "เสีย SP %d" % counter.sp)
	check(h.av > av0, "AV เดินตามน้ำหนักท่า")
	check(_count(b, "stance") == 1, "มี event stance")

	b.events.clear()
	var basic := b._basic_tech(foe)
	b._strike(foe, h, basic, 1.0)
	check(foe.hp < foe_hp, "ศัตรูตีตอนตั้งท่า → ผู้ตีโดนสวน (%d → %d)" % [foe_hp, foe.hp])
	check(_count(b, "counter") == 1 and h.counter_tech == null, "สวน 1 ครั้งแล้วท่าหมด")
	var hp_after := foe.hp
	b._strike(foe, h, basic, 1.0)
	check(foe.hp == hp_after and _count(b, "counter") == 1, "โดนครั้งที่ 2 ในตาเดียวกัน → ไม่สวนอีก")

	foe.hp = foe.max_hp
	h.counter_tech = counter
	b.events.clear()
	var multi := b._basic_tech(foe)
	multi.hits = 3
	var hits0 := h.hits
	b._execute(foe, h, multi)
	check(_count(b, "counter") == 1 and h.hits - hits0 == 3, "ศัตรูตี 3 ครั้ง → โดนครบ 3 · สวนครั้งเดียว")

	foe.hp = 1
	h.counter_tech = counter
	hits0 = h.hits
	b._execute(foe, h, multi)
	check(foe.down and h.hits - hits0 == 1, "ผู้ตีล้มจากการสวน → ฮิตที่เหลือไม่ออก (%d)" % (h.hits - hits0))
	foe.down = false
	foe.hp = foe.max_hp

	var ally := Actor.from_csv(by_id["M03"]); ally.side = "ally"
	b.actors.append(ally)
	h.counter_tech = counter
	b.events.clear()
	b._strike(ally, h, b._basic_tech(ally), 1.0)
	check(_count(b, "counter") == 0 and h.counter_tech == counter, "พวกเดียวกันตี → ไม่สวน ท่ายังค้าง")

	b.current = h
	b.player_act({"kind": "guard"})
	check(h.counter_tech == null, "ตาถัดไป (ผู้เล่นกดตั้งรับ) → ท่าสวนหมด")
	h.counter_tech = counter
	foe.telegraph = {}
	b.auto_act(h)
	check(h.counter_tech == null, "ตาถัดไป (AI) → ท่าสวนหมด")

	var pool: Array[Tech] = []
	pool.append(td.get_tech("ฟัน")); pool.append(counter)
	check(Ai.choose(h, foe, pool) == td.get_tech("ฟัน"), "Ai.choose ไม่เลือกคมสวน")
	var only: Array[Tech] = []
	only.append(counter)
	check(Ai.choose(h, foe, only) == null, "Ai.choose มีแต่คมสวน → null")
	h.sp = 60
	var sig := b._signature_tech(foe)
	var big := {"actor": foe, "sig": sig, "gap": 1.0e9, "turns": 1}
	var small := {"actor": foe, "sig": sig, "gap": 1.0, "turns": 1}
	var late := {"actor": foe, "sig": sig, "gap": 1.0e9, "turns": 2}
	check(Ai.choose_counter(h, pool, []) == null, "ไม่มีท่าเด่นกำลังมา → ไม่ตั้งท่า")
	check(Ai.choose_counter(h, pool, [big]) == counter, "ท่าเด่นลงก่อนตาถัดไป + ขัดไม่ทัน → ตั้งท่าสวน")
	check(Ai.choose_counter(h, pool, [small]) == null, "ขัดทัน → ตีดีกว่า")
	check(Ai.choose_counter(h, pool, [late]) == null, "ยังมีตาก่อนมันลงมือ → ไม่ตั้งท่า")
	h.sp = counter.sp - 1
	check(Ai.choose_counter(h, pool, [big]) == null, "SP ไม่พอ → ไม่ตั้งท่า")

	var h2 := _hero(["ฟัน", "คมสวน"])
	h2.atk = 1
	var b2 := _battle(h2, ["M15"])
	var f2: Actor = b2.foes()[0]
	h2.av = 0.0
	f2.av = 1.0
	f2.telegraph = {"name": f2.signature, "dmg": 0}
	var f2_hp := f2.hp
	b2.auto_act(h2)
	check(h2.counter_tech == counter and f2.hp == f2_hp, "AI ในลูป: ท่าเด่นมา ขัดไม่ทัน → ตั้งท่าสวน")
	var h3 := _hero(["ฟัน", "คมสวน"])
	var b3 := _battle(h3, ["M15"])
	b3.auto_act(h3)
	check(h3.counter_tech == null, "AI ในลูป: ไม่มีท่าเด่น → ไม่ตั้งท่า")

	print("FAILS ", fails)
	quit()
