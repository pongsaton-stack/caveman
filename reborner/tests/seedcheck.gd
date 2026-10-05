extends SceneTree
# fixed-seed fingerprint of Battle.run() across many scenarios
func _init() -> void:
	var rows := CsvDb.load_csv("res://data/monsters.csv")
	var by_id := CsvDb.index_by(rows, "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	seed(12345)
	var out := []
	for spec in [["M03", 10, 1, 30, ""], ["M15", 20, 2, 30, "ally"], ["M29", 25, 1, 30, "foe"], ["B1", 20, 1, 14, ""], ["B1", 16, 1, 28, ""]]:
		for i in 60:
			var b := Battle.new()
			b.techs = techs
			b.ambush = spec[4]
			var h := Actor.new()
			h.id = "hero"; h.name = "Rion"; h.side = "ally"; h.is_hero = true
			h.tier = spec[1]; h.max_hp = Formulas.hero_hp(spec[1]); h.hp = h.max_hp
			h.max_sp = Formulas.hero_sp(spec[1], 0); h.sp = h.max_sp
			h.atk = Formulas.hero_atk(spec[1], spec[3]); h.def_val = Formulas.hero_def(spec[1]); h.spd = 120
			h.school = "คม"; h.steer_branch = "เขี้ยว"
			h.learned.append(techs.root_of("คม").name)
			b.actors.append(h)
			for mid in ["M03", "M06"]:
				var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * 1.6); m.hp = m.max_hp
				b.actors.append(m)
			for j in spec[2]:
				b.actors.append(Actor.from_csv(by_id[spec[0]]))
			var r := b.run()
			out.append("%s|%d|%d|%.1f|%d|%d|%s|%d|%d|%d" % [r["won"], r["rounds"], r["dealt"], r["time"], r["glimmers"], r["combos"], ",".join(r["glimmer_log"]), r["guards"], r["interrupts"], r["fills"]])
	print("\n".join(out))
	quit()
