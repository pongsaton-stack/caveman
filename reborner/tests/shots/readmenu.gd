extends SceneTree
# เมนูท่าหลบ (kwan 7 ต.ค. 2026): ภาพ 0 = นอกจุดพัก · 1 = ที่จุดพัก (มีปุ่มฝากคลัง) · 2 = หลังฝากคลัง
var ow; var n := 0
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _m():
	for c in ow.get_children():
		if c is MenuScreen: return c
func _open_reads() -> void:
	for c in _m()._menu.get_children():
		if c is Button and c.text.begins_with("ท่าหลบ"): c.pressed.emit()
func _process(_d: float) -> bool:
	n += 1
	if n == 20:
		ow.enemy_clock = -999.0
		ow.ps.reads = {"M06": {"name": "ผลุบผลับ", "p": 5, "need": 5, "on": true},
			"M15": {"name": "เขี้ยวพุ่ง", "p": 2, "need": 5, "on": false}}
		ow.ps.cell = ow.ps.rest_cell + Vector2i(1, 0)
		ow._open_menu()
	if n == 26: _open_reads()
	if n == 32:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
		_m()._show_actions()
		ow.ps.cell = ow.ps.rest_cell
		_open_reads()
	if n == 38:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 1)
		for c in _m()._menu.get_children():
			if c is Button and c.text.begins_with("ฝากคลัง"): c.pressed.emit()
	if n == 44:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 2)
		print("reads: ", ow.ps.reads); quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/readmenu_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/readmenu_%d.png")
