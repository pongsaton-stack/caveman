extends SceneTree
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	seed(777)
	for spec in [["M01", 8, 1, 14], ["M01", 12, 1, 14], ["M15", 12, 2, 14], ["M15", 20, 2, 28], ["B1", 16, 1, 28], ["B1", 20, 1, 28]]:
		var n := 300; var wins := 0; var und := 0; var pts := 0.0; var tels := 0
		for i in n:
			var b := Battle.new(); b.techs = techs
			var h := Actor.new()
			h.id = "hero"; h.name = "Rion"; h.side = "ally"; h.is_hero = true
			h.tier = spec[1]; h.max_hp = Formulas.hero_hp(spec[1]); h.hp = h.max_hp
			h.max_sp = Formulas.hero_sp(spec[1], 0); h.sp = h.max_sp
			h.atk = Formulas.hero_atk(spec[1], spec[3]); h.def_val = Formulas.hero_def(spec[1]); h.spd = 120
			h.school = "คม"; h.steer_branch = "เขี้ยว"; h.learned.append(techs.root_of("คม").name)
			b.actors.append(h)
			for mid in ["M03", "M06"]:
				var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * Formulas.COMPANION_HP_MULT); m.hp = m.max_hp
				b.actors.append(m)
			for j in spec[2]:
				b.actors.append(Actor.from_csv(by_id[spec[0]]))
			var r := b.run()
			tels += int(r["telegraphs"])
			pts += float(r["understanding"].get(spec[0], 0))
			if r["won"]:
				wins += 1
				if r["understood"].has(spec[0]): und += 1
		print("%s x%d prof%d w%d | ชนะ %d%% | เข้าใจครบ(ของที่ชนะ) %d%% | ของทั้งหมด %d%% | แต้มเฉลี่ย %.2f/%s | เปิดท่า/ศึก %.2f" % [spec[0], spec[2], spec[1], spec[3], wins*100/n, (und*100/maxi(1,wins)), und*100/n, pts/n, by_id[spec[0]]["comprehension"], float(tels)/n])
	quit()
