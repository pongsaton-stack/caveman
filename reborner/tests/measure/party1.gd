extends SceneTree
# hero + N companions (same companion build as Sim/Overworld) vs region-1 encounters
func _init() -> void:
	randomize()
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	for comp in [["M03"], ["M06"], ["M03", "M06"]]:
		print("== hero + ", comp)
		for spec in [["M06",2],["M15",2],["B1",1]]:
			var line := "  %s x%d:" % [spec[0], spec[1]]
			for w in [14, 28]:
				for prof in [8, 12, 16, 20]:
					var wins := 0
					for i in 200:
						var b := Battle.new()
						b.techs = techs
						var ps := PlayerState.new()
						ps.prof = prof; ps.weapon_base = w
						ps.init_new(techs, Vector2i.ZERO)
						b.actors.append(ps.make_hero())
						for mid in comp:
							var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * 1.6); m.hp = m.max_hp; m.telegraph = {}
							b.actors.append(m)
						for j in spec[1]:
							b.actors.append(Actor.from_csv(by_id[spec[0]]))
						if b.run()["won"]: wins += 1
					line += "  w%d p%d %d%%" % [w, prof, int(wins / 2.0)]
			print(line)
	quit()
