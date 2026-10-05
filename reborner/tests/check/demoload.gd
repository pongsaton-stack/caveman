extends SceneTree
# เซฟเก่าที่ชนะบอสแล้ว (ec 1 · ยังไม่เห็นฉากจบ) → โหลดแล้วขึ้นจอจบเดโม · เซฟใหม่ไม่ขึ้น
var ow
func _initialize() -> void:
	var ps := PlayerState.new(); ps.ec = 1; ps.prof = 22; ps.learned.append("ฟัน"); ps.learned.append("เขี้ยวพุ่ง")
	SaveGame.save(ps)
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _run() -> void:
	await create_timer(2.0).timeout
	var got := false
	for c in ow.get_children():
		if c is DemoEndScreen: got = true; c._done("continue")
	print("OK   เซฟเก่าชนะบอส → จอจบเดโม" if got else "FAIL ไม่ขึ้นจอจบ")
	await process_frame
	ow.queue_free()
	await process_frame
	var ow2 = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow2)
	await create_timer(2.0).timeout
	var again := false
	for c in ow2.get_children():
		if c is DemoEndScreen: again = true
	print("OK   ไม่ขึ้นซ้ำหลังเห็นแล้ว" if not again else "FAIL ขึ้นซ้ำ")
	SaveGame.clear()
	quit()
