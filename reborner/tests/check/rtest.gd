extends SceneTree
var fails := 0
func ok(c: bool, msg: String) -> void:
	print(("OK   " if c else "FAIL ") + msg)
	if not c: fails += 1
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var rec := CsvDb.index_by(CsvDb.load_csv("res://data/recruits.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	ok(rec.size() == 3 and rec.has("M01") and rec.has("M15") and rec.has("B1"), "recruits.csv มี 3 สายพันธุ์ตามกฎ 5.3")
	# ── PlayerState ──
	var ps := PlayerState.new()
	ps.init_new(techs, Vector2i.ZERO)
	ps.seed_party(CsvDb.load_csv("res://data/companions.csv"))
	ok(ps.active_members(2).size() == 2, "เริ่มเกม 2 ตัวลงสนาม")
	var n1 := ps.recruit(rec["M01"])
	ok(ps.party.size() == 3 and n1 == "สไลม์เถ้า", "รับสไลม์ได้ แม้ทีมเต็ม")
	ok(not ps.active_members(2).has(ps._member(n1)), "ตัวเกินช่องไปสำรอง")
	var n2 := ps.recruit(rec["M01"])
	ok(n2 == "สไลม์เถ้า 2", "ชื่อซ้ำได้เลขต่อท้าย")
	var nb := ps.recruit(rec["B1"])
	ok(PlayerState.slot_cost(ps._member(nb)) == 2, "บอสกิน 2 ช่อง")
	ps.move_to_front(nb)
	var act := ps.active_members(2)
	ok(act.size() == 1 and str(act[0]["name"]) == nb, "บอสหัวทีม + 2 ช่อง = ลงสนามตัวเดียว")
	ok(ps.make_companions(by_id, 2).size() == 1, "make_companions เคารพช่องของบอส")
	ok(ps.active_members(3).size() == 2, "3 ช่อง = บอส + อีก 1")
	var d := ps.to_dict()
	var ps2 := PlayerState.new(); ps2.from_dict(d)
	ok(PlayerState.slot_cost(ps2._member(nb)) == 2 and ps2.party.size() == ps.party.size(), "เซฟ/โหลดจำช่องบอสได้")
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
