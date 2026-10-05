extends SceneTree
# แผนที่จริง: ย้ายสไลม์/หมาป่ามาใกล้ตัวเอก หันซ้าย-ขวา แล้วถ่ายภาพ → $SHOT
var ow
var n := 0
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)

func _place(e, c: Vector2i, d: Vector2i) -> void:
	e.cell = c; e.home = c; e.position = ow._cell_center(c); e.set_facing(d)

func _process(_d: float) -> bool:
	n += 1
	if n == 5:
		ow.enemy_clock = -999.0   # ห้ามศัตรูเดินระหว่างถ่าย
		var hc: Vector2i = ow.ps.cell
		var got := {}
		for e in ow.enemies:
			var id: String = e.group[0]
			if (id == "M01" or id == "M15") and not got.has(id + str(got.size())):
				got[id + str(got.size())] = e
		var spots := [[hc + Vector2i(2, 0), Vector2i.RIGHT], [hc + Vector2i(4, 0), Vector2i.LEFT], [hc + Vector2i(2, 2), Vector2i.DOWN], [hc + Vector2i(4, 2), Vector2i.LEFT]]
		var i := 0
		for k in got:
			if i < spots.size():
				_place(got[k], spots[i][0], spots[i][1]); print(k, " -> ", spots[i]); i += 1
	if n == 70:
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
		quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/owmon_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/owmon_%d.png")
