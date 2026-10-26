extends SceneTree
# แผนที่จริง (จอเสมือน): วางตัวเอกแถวบนสุดที่เดินได้ แล้วถ่ายภาพ → $SHOT
var ow
var n := 0
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)

func _process(_d: float) -> bool:
	n += 1
	if n == 5:
		for y in ow.map.h:
			var hit := false
			for x in ow.map.w:
				var c := Vector2i(x, y)
				if ow.map.walkable(c) and ow._enemy_at(c) == null:
					ow.ps.cell = c
					ow.hero_node.position = ow._cell_center(c)
					ow._dog_snap()
					hit = true
					break
			if hit:
				break
		print("hero cell ", ow.ps.cell)
	if n == 60:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
		quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/owshot_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/owshot_%d.png")
