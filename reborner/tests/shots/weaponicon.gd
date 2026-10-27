extends SceneTree
# ไอคอนอาวุธในเมนู (ชุด 60 ชิ้น · tools/sprites/weapon_icons60.py): ภาพ 0 = มีดครัว SL-1 · 1 = สารานุกรม CR-8 · 2 = ถุงมือจักรวาล BD-10
var ow; var n := 0
const IDS := ["SL-1", "CR-8", "BD-10"]
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _process(_d: float) -> bool:
	n += 1
	var k := int((n - 20) / 10.0)
	if n >= 20 and (n - 20) % 10 == 0 and k < IDS.size():
		ow.enemy_clock = -999.0
		var r: Dictionary = PlayerState.weapon_row(IDS[k])
		ow.ps.weapon_id = IDS[k]; ow.ps.weapon_name = str(r["name"])
		ow._open_menu()
	if n >= 26 and (n - 26) % 10 == 0 and int((n - 26) / 10.0) < IDS.size():
		root.get_viewport().get_texture().get_image().save_png(_shot() % int((n - 26) / 10.0))
		for c in ow.get_children():
			if c is MenuScreen: c.queue_free()
	return n > 20 + IDS.size() * 10 + 4
func _shot() -> String:
	return OS.get_environment("SHOT_DIR") + "/weaponicon_%d.png" if OS.has_environment("SHOT_DIR") else "user://weaponicon_%d.png"
