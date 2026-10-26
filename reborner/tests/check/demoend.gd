extends SceneTree
# จบเดโม: บทพูดจาก CSV · ไม่เคยล้ม → มีบรรทัด "อีกแล้ว" · ปุ่มเดินเล่นต่อ = ธงเซฟ · ภาพ → $SHOT
var ow
var fails := 0
func ok(c: bool, m: String) -> void:
	print(("OK   " if c else "FAIL ") + m)
	if not c: fails += 1
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _scr():
	for c in ow.get_children():
		if c is DemoEndScreen: return c
	return null
func _run() -> void:
	await process_frame
	ok(ow._dialogue("boss_win") == ["...หนึ่ง"], "บทพูดชนะบอสจาก CSV")
	ow.ps.ec = 1
	ow._demo_end()
	await process_frame
	var s = _scr()
	ok(s != null, "เปิดจอจบเดโม")
	ok(s.lines.size() == 2 and s.lines[1] == "...อีกแล้วเหรอ", "ไม่เคยล้ม → มีบรรทัด อีกแล้ว")
	s.line_secs = 0.05
	for i in 20: await process_frame
	await create_timer(0.3).timeout
	ok(s._phase == "summary", "บทพูดจบ → การ์ดสรุป")
	ok(ow.busy, "ระหว่างจอจบ เดินไม่ได้")
	for i in 5: await process_frame
	if _shot() != "":
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
	s._done("continue")
	for i in 3: await process_frame
	ok(ow.ps.demo_end_seen, "เดินเล่นต่อ → ไม่แสดงซ้ำ")
	ok(not ow.busy, "กลับมาเดินได้")
	var ps2 := PlayerState.new(); SaveGame.load_into(ps2)
	ok(ps2.demo_end_seen, "ธงอยู่ในเซฟ")
	# เคยล้ม → ไม่มีบรรทัด อีกแล้ว
	ow.ps.falls = 1
	ow._demo_end()
	await process_frame
	s = _scr()
	ok(s.lines.size() == 1, "เคยล้ม → บทพูดเดียว")
	s._done("continue")
	for i in 3: await process_frame
	# message_done ยิงตอนกล่องข้อความหน้าสุดท้ายปิด
	var got := [false]
	ow.message_done.connect(func(): got[0] = true, CONNECT_ONE_SHOT)
	ow._show("ก\nข\nค", 0.1)
	await create_timer(3.0).timeout
	ok(got[0], "message_done หลังข้อความ 2 หน้า")
	print("FAILS ", fails)
	SaveGame.clear()
	quit()

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/demoend_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/demoend_%d.png")
