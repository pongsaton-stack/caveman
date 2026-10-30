extends SceneTree
# รอบแบบ "ทุกตัวได้คิวครบ" (COMBO_TECH_SPEC ส่วน 2 · kwan 30 ต.ค.) + ความเชื่อใจสเกล 1–10 + แปลงเซฟเก่า
var fails := 0
func ok(c: bool, msg: String) -> void:
	print(("OK   " if c else "FAIL ") + msg)
	if not c: fails += 1

func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	# ── รอบ: ตัวเร็วได้ 2 คิวในรอบเดียว รอบยังไม่ปิดจนตัวช้าได้คิว ──
	var b := Battle.new()
	b.techs = techs
	var fast := Actor.from_csv(by_id["M06"]); fast.side = "foe"; fast.spd = 300
	var slow := Actor.from_csv(by_id["M03"]); slow.side = "ally"; slow.spd = 100
	for a in [fast, slow]:
		a.max_hp = 999999; a.hp = a.max_hp   # ไม่ให้ศึกจบก่อนครบรอบ
	b.actors.append(fast); b.actors.append(slow)
	var seen := []
	for i in 6:
		var cur := b.next_turn()
		seen.append([cur.name if cur != null else "-", b.cycle])
		if cur != null:
			b.auto_act(cur)
		if b.is_over():
			break
	print("  ", seen)
	ok(b.cycle >= 2, "รอบปิดได้ (cycle %d)" % b.cycle)
	var c1 := 0
	for s in seen:
		if s[1] == 1: c1 += 1
	ok(c1 >= 2, "ตัว SPD สูงได้หลายคิวในรอบแรก ยังเป็นรอบเดิม (%d แอ็กชันในรอบ 1)" % c1)
	ok(b.rounds == seen.size(), "rounds ยังนับทุกแอ็กชันเหมือนเดิม")
	# ── ตัวที่ล้มกลางรอบไม่ค้างรอบ ──
	var b2 := Battle.new()
	b2.techs = techs
	var a1 := Actor.from_csv(by_id["M01"]); a1.side = "foe"; a1.spd = 100
	var a2 := Actor.from_csv(by_id["M01"]); a2.side = "foe"; a2.spd = 100; a2.av += 5
	var h := Actor.from_csv(by_id["M03"]); h.side = "ally"; h.spd = 100; h.av += 10
	b2.actors.append(a1); b2.actors.append(a2); b2.actors.append(h)
	var t1 := b2.next_turn(); t1.av += 1000   # a1 ได้คิว (ไม่ทำแอ็กชันจริง เลื่อนคิวเอง)
	a2.down = true
	var t2 := b2.next_turn(); t2.av += 1000   # h ได้คิว → สมาชิกที่ยืนอยู่ครบ
	var cyc := b2.cycle
	b2.next_turn()
	ok(b2.cycle == cyc + 1, "ตัวล้มกลางรอบไม่ต้องรอ → รอบถัดไปเริ่ม (cycle %d → %d)" % [cyc, b2.cycle])
	# ── ความเชื่อใจ 1–10 ──
	ok(Formulas.TRUST_MIN == 1 and Formulas.TRUST_MAX == 10 and Formulas.COMBO_LOYALTY == 5, "สเกล 1–10 · คอมโบ rank 5")
	var ps := PlayerState.new()
	ps.init_new(techs, Vector2i.ZERO)
	var rec := CsvDb.index_by(CsvDb.load_csv("res://data/recruits.csv"), "monster_id")
	var nm := ps.recruit(rec["M01"])
	ok(int(ps._member(nm)["loyalty"]) == 1, "มอนใหม่เริ่ม rank 1")
	var reach5 := 0
	var reach10 := 0
	var mon := Actor.from_csv(by_id["M01"]); mon.name = nm
	for n in range(1, 13):
		ps.after_battle([mon])
		var l := int(ps._member(nm)["loyalty"])
		if l >= 5 and reach5 == 0: reach5 = n
		if l >= 10 and reach10 == 0: reach10 = n
	ok(reach5 == 4 and reach10 == 8, "ชนะไม่ล้มทุกศึก: rank 5 ที่ศึก %d (เดิมถึง 3 ที่ศึก 4) · rank 10 ที่ศึก %d (เดิมถึง 5 ที่ศึก 8)" % [reach5, reach10])
	# ── เซฟเก่า (version 2) แปลง x → 1 + 2x ──
	var d := ps.to_dict()
	d["version"] = 2
	d["party"] = [{"id": "M03", "name": "a", "lp": 3, "loyalty": 0}, {"id": "M06", "name": "b", "lp": 3, "loyalty": 3}, {"id": "M01", "name": "c", "lp": 3, "loyalty": 5}]
	var ps2 := PlayerState.new()
	ps2.from_dict(d)
	ok(int(ps2.party[0]["loyalty"]) == 1 and int(ps2.party[1]["loyalty"]) == 7 and int(ps2.party[2]["loyalty"]) == 10, "เซฟเก่า 0/3/5 → 1/7/10")
	d["version"] = 3
	var ps3 := PlayerState.new()
	ps3.from_dict(d)
	ok(int(ps3.party[1]["loyalty"]) == 3, "เซฟใหม่ไม่แปลงซ้ำ")
	print("FAILS %d" % fails)
	quit(1 if fails > 0 else 0)
