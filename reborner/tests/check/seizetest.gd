extends SceneTree
func _initialize() -> void:
	var td := TechDb.new()
	td.load_from("res://data/techs.csv")
	td.load_seize("res://data/seize_techs.csv")
	var ps := PlayerState.new()
	print("slots prof0 ", ps.memory_slots())
	ps.prof = 150
	print("slots prof150 ", ps.memory_slots())
	ps.prof = 0
	var a := td.seize_for("M03"); var b := td.seize_for("M06")
	print("techs ", a.name, " ", a.sp, " ", a.effect, " / ", b.name, " ", b.power, " ", b.effect, " once ", b.once)
	print("not in all: ", not td.all.has(a), " by_name: ", td.get_tech(a.name) == a)
	print("seize ", ps.seize(a), ps.seize(b), " dup ", ps.seize(a), " used ", ps.used_memory())
	var d := ps.to_dict()
	var ps2 := PlayerState.new(); ps2.from_dict(d)
	print("roundtrip ", ps2.seized.size(), " ", ps2.used_memory())
	ps2.forget("M03")
	print("after forget ", ps2.seized.size(), " ", ps2.used_memory())
	quit()
