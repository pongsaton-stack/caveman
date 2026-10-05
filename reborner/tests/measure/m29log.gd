extends SceneTree
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv"); techs.load_seize("res://data/seize_techs.csv")
	for ws in [false]:
		seed(777)
		var ps := PlayerState.new(); ps.prof = 20; ps.hp = 9999; ps.sp = 9999
		ps.learned.append(techs.root_of(ps.school).name)
		if ws: ps.seize(techs.seize_for("M03")); ps.seize(techs.seize_for("M06"))
		var b := Battle.new(); b.techs = techs; b.capture = true
		var h := ps.make_hero(); b.actors.append(h); for j in 2: b.actors.append(Actor.from_csv(by_id["M15"]))
		print("=== seize ", ws, " hp ", h.hp, " def ", h.def_val); b.run(); print("\n".join(b.log_lines))
	quit()
