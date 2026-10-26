extends SceneTree
func _init() -> void:
	print("table ", Actor.sig_table())
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var a := Actor.from_csv(by_id["M03"])
	print("M03 fx ", a.sig_effect)
	quit()
