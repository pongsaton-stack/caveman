extends SceneTree
var ow; var n := 0
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _m():
	for c in ow.get_children():
		if c is MenuScreen: return c
func _process(_d: float) -> bool:
	n += 1
	if n == 20:
		ow.enemy_clock = -999.0
		ow.ps.seize(ow.techs.seize_for("M03")); ow.ps.seize(ow.techs.seize_for("M06"))
		ow._open_menu()
	if n == 30:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
		for c in _m()._menu.get_children():
			if c is Button and c.text.begins_with("ท่าที่ยึด"): c.pressed.emit()
	if n == 36:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 1)
		_m()._menu.get_child(0).pressed.emit()
	if n == 42:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 2)
		print("left: ", ow.ps.seized); quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/seizemenu_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/seizemenu_%d.png")
