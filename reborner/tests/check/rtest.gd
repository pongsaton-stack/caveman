extends SceneTree
var fails := 0
func ok(c: bool, msg: String) -> void:
	print(("OK   " if c else "FAIL ") + msg)
	if not c: fails += 1
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	# ── ขอเข้าทีมหลังชนะ (MONSTER_ALLY_SYSTEM_SPEC 2 · kwan 29–30 ต.ค.) ──
	var ps := PlayerState.new()
	ps.init_new(techs, Vector2i.ZERO)
	ps.seed_party(CsvDb.load_csv("res://data/companions.csv"))
	ok(ps.party.is_empty(), "เริ่มเกม Rion คนเดียว")
	ok(ps.ally_candidates(["M01", "M01", "B1", "MB01", "M03"], by_id) == ["M01", "M03"], "ตรวจชนิดละครั้ง ตามลำดับที่ปราบ · บอส/มินิบอสไม่ตรวจ")
	ok(not ps.ally_check("M06", 0.99), "ยังไม่มีพวก: ชนิดนอก M01/M03 ใช้เรตปกติ")
	ok(ps.ally_check("M03", 0.99), "ยังไม่มีพวก: หนอนหินขอเข้าทีมแน่นอน (สุ่มได้ 0.99 ก็ผ่าน)")
	ok(ps.ally_check("M01", 0.99), "ไม่รับ = การันตียังอยู่")
	var n1 := ps.join_ally("M01", "สไลม์เถ้า")
	ok(ps.party.size() == 1 and int(ps._member(n1)["loyalty"]) == Formulas.TRUST_MIN and int(ps._member(n1)["lp"]) == Formulas.LP_MAX, "รับแล้ว: rank 1 · LP เต็ม")
	ok(ps.ally_candidates(["M01", "M03"], by_id) == ["M03"], "ชนิดที่มีในคลังแล้วไม่ตรวจซ้ำ")
	var got := 0
	for i in Formulas.ALLY_OPENING_PITY:
		if ps.ally_check("M15", 0.99): got += 1
	ok(got == 0 and ps.opening_checks == Formulas.ALLY_OPENING_PITY, "พวก 1 ตัว: ตรวจ %d ครั้งไม่ได้ (สุ่ม 0.99)" % Formulas.ALLY_OPENING_PITY)
	ok(ps.ally_check("M15", 0.99), "ครั้งถัดไปสำเร็จแน่นอน (การันตีพวกตัวที่สอง)")
	ok(ps.ally_check("M06", 0.99), "ไม่รับ = การันตียังอยู่ (ตัวที่สอง)")
	ps.join_ally("M15", "หมาป่าคู่")
	ok(not ps.ally_check("M06", 0.99) and ps.ally_check("M06", Formulas.ALLY_RATE - 0.01), "พวกครบ 2 ตัว: กลับเป็นสุ่มตามเรต")
	ok(int(ps.ally_checks["M06"]) == 4 and int(ps.ally_checks["M15"]) == 6, "นับครั้งที่ตรวจรายชนิด")
	ps.join_ally("M06", "ค้างคาวเงา")
	ok(ps.active_members(2).size() == 2 and not ps.active_members(2).has(ps._member("ค้างคาวเงา")), "ตัวที่ 3 อยู่ในคลัง")
	var d := ps.to_dict()
	var ps2 := PlayerState.new(); ps2.from_dict(JSON.parse_string(JSON.stringify(d)))
	ok(ps2.party.size() == 3 and int(ps2.ally_checks["M15"]) == 6 and ps2.opening_checks == ps.opening_checks, "เซฟ/โหลดจำคลังพวกและตัวนับ")
	ok(ps.ally_count() == 3, "นับพวกที่ยังมี LP")
	# ── Battle: จับตา ──
	var b := Battle.new(); b.techs = techs
	var h := ps.make_hero(); b.actors.append(h)
	var f := Actor.from_csv(by_id["M01"]); b.actors.append(f)
	b.begin()
	b.current = h
	b.player_act({"kind": "watch", "target": f})
	ok(b.understanding_of(f)[0] == Formulas.WATCH_POINTS, "จับตา +%d" % Formulas.WATCH_POINTS)
	ok(not b.understood().has("M01"), "2/3 ยังไม่ครบ")
	b.current = h
	b.player_act({"kind": "watch", "target": f})
	ok(b.understood().has("M01"), "จับตา 2 ครั้ง = เข้าใจสไลม์ครบ")
	# boss: viewer must be standing
	var bb := Battle.new(); bb.techs = techs
	var h2 := ps.make_hero(); bb.actors.append(h2)
	var boss := Actor.from_csv(by_id["B1"]); bb.actors.append(boss)
	bb.begin(); bb.current = h2
	bb.player_act({"kind": "watch", "target": boss})
	ok(bb.understood().has("B1"), "บอสเกณฑ์ 1 · ผู้เห็นยืนอยู่ = ครบ")
	h2.down = true
	ok(not bb.understood().has("B1"), "ผู้เห็นล้ม = ไม่นับ (GDD 5.2)")
	print("FAILS ", fails)
	quit()
