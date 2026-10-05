extends SceneTree
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv"); techs.load_seize("res://data/seize_techs.csv")
	var ps := PlayerState.new(); ps.prof = 8; ps.hp = 999; ps.sp = 999
	ps.learned.append(techs.root_of(ps.school).name)
	ps.seize(techs.seize_for("M03")); ps.seize(techs.seize_for("M06"))
	seed(1)
	var b := Battle.new(); b.techs = techs; b.capture = true
	var h := ps.make_hero()
	b.actors.append(h)
	b.actors.append(Actor.from_csv(by_id["M01"]))
	b.begin()
	var used_def := false; var used_av := false
	for i in 40:
		if b.is_over(): break
		var cur := b.next_turn()
		if cur == null: break
		if not cur.is_hero: b.auto_act(cur); continue
		var names := b.hero_options(cur).map(func(t): return t.name)
		if not used_def:
			print("options: ", names)
			var t: Tech = techs.get_tech("เกราะแข็ง")
			var d0 := cur.def_val
			b.player_act({"kind": "tech", "tech": t})
			print("def ", d0, " -> ", cur.def_val, " sp ", cur.sp, " events ", b.events.map(func(e): return e.get("buff", e["dmg"])))
			b.events.clear(); used_def = true
		elif not used_av:
			var av0 := cur.av
			b.player_act({"kind": "tech", "tech": techs.get_tech("ผลุบผลับ")})
			print("ผลุบผลับ av before ", av0, " after ", cur.av, " dmg ", b.events.map(func(e): return e["dmg"]))
			b.events.clear(); used_av = true
		else:
			print("after once: ผลุบผลับ in options = ", names.has("ผลุบผลับ"), " · เกราะแข็ง = ", names.has("เกราะแข็ง"), " def now ", cur.def_val)
			break
	print("\n".join(b.log_lines.slice(0, 30)))
	quit()
