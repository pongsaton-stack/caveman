extends SceneTree
# เปิดจอสู้จริง (มีจอเสมือน) แล้วบันทึกภาพหน้าจอ → $SHOT
var screen: BattleScreen
var n := 0
func _initialize() -> void:
	var by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	var ps := PlayerState.new(); ps.prof = 20; ps.weapon_base = 28
	ps.init_new(techs, Vector2i.ZERO)
	var b := Battle.new(); b.techs = techs
	b.actors.append(ps.make_hero())
	for mid in ["M03", "M06"]:
		var m := Actor.from_csv(by_id[mid]); m.side = "ally"; b.actors.append(m)
	for mid in (OS.get_environment("FOES") if OS.has_environment("FOES") else "M01,M02").split(","): b.actors.append(Actor.from_csv(by_id[mid]))
	screen = BattleScreen.new(); screen.step_delay = 0.4
	screen.setup(b, "ทดสอบภาพ", true)
	root.add_child(screen)

func _process(_d: float) -> bool:
	n += 1
	if n >= 20 and n % 4 == 0 and n <= 140:
		root.get_viewport().get_texture().get_image().save_png(_shot() % n)
		if n >= 140: quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/fxshot_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/fxshot_%d.png")
