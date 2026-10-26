extends SceneTree
# เริ่มเกมใหม่จากจอจบเดโม → ลบเซฟ + โหลดฉากใหม่ (ตัวเอกกลับจุดเริ่ม ไม่มี EC)
var ow
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	current_scene = ow
	_run.call_deferred()
func _run() -> void:
	await process_frame
	ow.ps.ec = 1; ow.ps.prof = 30; SaveGame.save(ow.ps)
	ow._demo_end()
	await process_frame
	for c in ow.get_children():
		if c is DemoEndScreen: c._done("new_game")
	for i in 10: await process_frame
	var now = current_scene
	print("OK   ฉากใหม่ " if now != ow and now != null else "FAIL ไม่ได้โหลดใหม่ ", " ec=", now.ps.ec if now else -1, " prof=", now.ps.prof if now else -1)
	quit()
