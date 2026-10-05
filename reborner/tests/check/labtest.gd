extends SceneTree
# ห้องทดลองท่า: เปิดเมนู → กด "ทดลองท่า" → ภาพเมนูท่า → ใช้ไม้ตาย → ภาพ · ตรวจว่าเซฟ/สถานะไม่เปลี่ยน
var ow
var n := 0
var before := {}
var fails := 0
var shots := 0
var t0 := -1
var t_end := -1
func ok(c: bool, m: String) -> void:
	print("OK   " if c else "FAIL ", m)
	if not c: fails += 1
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _find(node: Node, cls: String) -> Node:
	for c in node.get_children():
		if c.get_class() == cls or (c.get_script() != null and c.get_script().get_global_name() == cls): return c
	return null
func _process(_d: float) -> bool:
	n += 1
	if t0 < 0 and n > 10 and not ow.busy:
		t0 = n
		ow.enemy_clock = -999.0   # หยุดมอนเดินเข้าหาระหว่างเทสต์ (เมนูเปิดแล้ว busy กันเองอยู่แล้ว)
	if t0 < 0:
		return false
	var n0 := n
	n = n - t0 + 40
	_step()
	n = n0
	return false

func _step() -> void:
	if n == 40:
		before = {"prof": ow.ps.prof, "learned": ow.ps.learned.duplicate(), "gold": ow.ps.gold, "hp": ow.ps.hp, "sp": ow.ps.sp, "party": str(ow.ps.party)}
		ow._open_menu()
	if n == 50:
		var m = _find(ow, "MenuScreen")
		ok(m != null, "เปิดเมนูได้")
		var lab: Button
		for c in m._menu.get_children():
			if c is Button and c.text == "ทดลองท่า": lab = c
		ok(lab != null, "มีปุ่ม ทดลองท่า")
		root.get_viewport().get_texture().get_image().save_png(_shot() % 0)
		lab.pressed.emit()
		for c in m._menu.get_children():   # เมนูเลือกสาย (เพิ่มทีหลัง) → เลือกสายของตัวเอก
			if c is Button and c.text.begins_with(ow.ps.school + " ("): c.pressed.emit(); break
	if n > 50:
		var bs = _find(ow, "BattleScreen")
		if bs != null and bs._waiting_player and shots == 0:
			shots = 1
			var h: Actor = bs.hero
			ok(h.learned.has("วงล้อ") and h.learned.has("เขี้ยวพัน"), "ตัวเอกทดลองรู้ไม้ตาย (%d ท่า)" % h.learned.size())
			ok(h.tier == 45, "ความชำนาญชั่วคราว = req_prof สูงสุดของสาย (%d)" % h.tier)
			root.get_viewport().get_texture().get_image().save_png(_shot() % 1)
			bs.auto = true; bs.step_delay = 0.02; bs.end_delay = 0.05
			bs._commit({"kind": "guard"})
		if bs == null and shots == 1 and n > 60:
			shots = 2
			ok(ow.ps.prof == before["prof"] and ow.ps.learned == before["learned"] and ow.ps.gold == before["gold"] and ow.ps.hp == before["hp"] and ow.ps.sp == before["sp"] and str(ow.ps.party) == before["party"], "จบแล้วสถานะตัวเอก/ทีมเหมือนเดิม")
			t_end = n
		if shots == 2 and n == t_end + 200:
			ok(not ow.busy, "ปิดข้อความแล้วกลับมาเดินได้")
			root.get_viewport().get_texture().get_image().save_png(_shot() % 2)
			print("FAILS ", fails); quit()
	if n > 6000: print("TIMEOUT"); quit()

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/labtest_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/labtest_%d.png")
