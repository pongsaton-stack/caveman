extends SceneTree
# solo hero vs region-1 encounters (GDD 5.5: EC 0 = 1 slot = hero alone)
func _init() -> void:
	randomize()
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	for spec in [["M01",1],["M03",1],["M06",2],["M15",2],["B1",1]]:
		var line := "%s x%d (t%d):" % [spec[0], spec[1], int(by_id[spec[0]]["tier"])]
		for w in [14, 28]:
			for prof in [8, 12, 16, 20, 22]:
				var wins := 0
				for i in 200:
					var b := Battle.new()
					b.techs = techs
					var ps := PlayerState.new()
					ps.prof = prof; ps.weapon_base = w
					ps.init_new(techs, Vector2i.ZERO)
					b.actors.append(ps.make_hero())
					for j in spec[1]:
						b.actors.append(Actor.from_csv(by_id[spec[0]]))
					if b.run()["won"]: wins += 1
				line += "  w%d p%d %d%%" % [w, prof, int(wins / 2.0)]
		print(line)
	quit()
