extends SceneTree
# tools/web/ui_map_shot.gd — ภาพแผนที่จริงรอบจุดบอส B1 (ไม่มีตัวละคร/HUD) เป็นฉากหลังศึกบนแผนที่ในหน้า UI Kit
#   xvfb-run -a <godot> --path . --rendering-driver opengl3 -s tools/web/ui_map_shot.gd   (SHOT=<ไฟล์.png>)
var ow
var n := 0
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)

func _process(_d: float) -> bool:
	n += 1
	if n == 5:
		ow.enemy_clock = -999.0
		var boss: Vector2i = Vector2i.ZERO
		for e in ow.enemies:
			if e.group[0] == "B1":
				boss = e.cell
			e.visible = false
		ow.hero_sprite.visible = false
		if ow.dog_node: ow.dog_node.visible = false
		ow.hud.get_parent().visible = false
		var cam: Camera2D = ow.hero_node.get_child(ow.hero_node.get_child_count() - 1)
		cam.position_smoothing_enabled = false
		ow.hero_node.position = ow._cell_center(boss + Vector2i(-1, 0))
		print("boss cell ", boss)
	if n == 40:
		var out := OS.get_environment("SHOT") if OS.has_environment("SHOT") else "user://ui_map.png"
		root.get_viewport().get_texture().get_image().save_png(out)
		quit()
	return false
