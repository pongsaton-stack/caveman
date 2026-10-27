extends SceneTree
# กลไกโกรธ (data/enrage.csv · มินิบอส MB-1) — คู่ชนิดเดียวกันล้ม → อีกตัว ATK ×1.5 · AV ×0.7 ถาวร ครั้งเดียว · ตัวอื่นไม่โดน
var fails := 0

func check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if not ok: fails += 1

func _battle(ids: Array, team := false) -> Battle:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	var b := Battle.new()
	b.techs = techs
	var ps := PlayerState.new()
	ps.init_new(techs, Vector2i.ZERO)
	if team:
		ps.prof = 16
	b.actors.append(ps.make_hero())
	if team:   # ทีมเริ่มเกมแบบ tests/measure/mb1.gd
		for mid in ["M03", "M06"]:
			var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * 1.6); m.hp = m.max_hp; m.telegraph = {}
			b.actors.append(m)
	for id in ids:
		b.actors.append(Actor.from_csv(by_id[id]))
	return b

func _initialize() -> void:
	var b := _battle(["MB01", "MB01"])
	var w1: Actor = b.actors[1]
	var w2: Actor = b.actors[2]
	check(not w1.enrage.is_empty() and str(w1.enrage["trigger"]) == "pair_down", "MB01 มีแถวโกรธ pair_down")
	var atk0 := w2.atk
	var spd0 := w2.spd
	w2.av = 1000.0
	w1.hp = 0
	w1.down = true
	b._on_down(w1)
	check(w2.enraged and w2.atk == roundi(atk0 * 1.5), "คู่ล้ม → ATK %d → %d (×1.5)" % [atk0, w2.atk])
	check(absf(Formulas.av(w2.spd) / Formulas.av(spd0) - 0.7) < 0.01, "AV ต่อการกระทำ ×0.7 (SPD %d → %d)" % [spd0, w2.spd])
	check(absf(w2.av - 700.0) < 0.01, "AV ที่ค้างในคิวลดทันที 1000 → %.0f" % w2.av)
	check(b.enrages == 1, "นับโกรธ 1 ครั้ง")
	b._on_down(w1)
	check(w2.atk == roundi(atk0 * 1.5) and b.enrages == 1, "โกรธไม่ซ้อน")

	var bm := _battle(["M15", "M15"])
	var m1: Actor = bm.actors[1]
	var m2: Actor = bm.actors[2]
	var a0 := m2.atk
	m1.down = true
	bm._on_down(m1)
	check(not m2.enraged and m2.atk == a0, "หมาป่าคู่ M15 ปกติไม่โกรธ (สมดุลเดิมไม่ขยับ)")

	# ศึกจริงจนจบ (ทีมเริ่มเกม): ชนะ = ฆ่าครบ 2 ตัว → ตัวที่สองโกรธ เว้นแต่ล้มพร้อมกันในการกระทำเดียว
	var n := 0
	var won := 0
	for i in 50:
		var r := _battle(["MB01", "MB01"], true).run()
		n += int(r["enrages"])
		won += int(r["won"])
	print("     ศึกจริง 50 ศึก ชนะ %d · โกรธ %d ครั้ง" % [won, n])
	check(n >= 35, "ศึกจริงเกิดโกรธ ≥ 35/50")
	print("FAILS %d" % fails)
	quit(1 if fails > 0 else 0)
