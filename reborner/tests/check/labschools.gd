extends SceneTree
# ทุกสายในห้องทดลอง: เมนู → ทดลองท่า → ปุ่มสาย · ใช้ท่า req_prof สูงสุดของสาย 1 ครั้ง → ภาพ → ให้ AI เล่นจบ → สายถัดไป
var ow
var n := 0
var fails := 0
var schools := []
var si := -1
var phase := "wait_free"
var used := -1
var before := ""
func ok(c: bool, m: String) -> void:
	print("OK   " if c else "FAIL ", m)
	if not c: fails += 1
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _find(cls: String) -> Node:
	for c in ow.get_children():
		if c.get_script() != null and c.get_script().get_global_name() == cls: return c
	return null
func _process(_d: float) -> bool:
	n += 1
	if n > 20000: print("TIMEOUT"); quit()
	match phase:
		"wait_free":
			if n > 10 and not ow.busy:
				ow.enemy_clock = -99999.0
				if schools.is_empty():
					schools = ow.techs.schools()
					before = str([ow.ps.prof, ow.ps.learned, ow.ps.gold, ow.ps.hp, ow.ps.sp, ow.ps.school])
				si += 1
				if si >= schools.size():
					ok(str([ow.ps.prof, ow.ps.learned, ow.ps.gold, ow.ps.hp, ow.ps.sp, ow.ps.school]) == before, "ทดลองครบทุกสายแล้ว สถานะตัวเอกเหมือนเดิม")
					print("FAILS ", fails); quit(); return false
				ow._open_menu(); phase = "menu"; used = n
		"menu":
			if n - used == 5:
				var m = _find("MenuScreen")
				for c in m._menu.get_children():
					if c is Button and c.text == "ทดลองท่า": c.pressed.emit()
			if n - used == 10:
				var m = _find("MenuScreen")
				var hit := false
				for c in m._menu.get_children():
					if c is Button and c.text.begins_with(schools[si] + " ("):
						hit = true; c.pressed.emit(); break
				ok(hit, "มีปุ่มสาย " + schools[si])
				phase = "battle"
		"battle":
			var bs = _find("BattleScreen")
			if bs != null and bs._waiting_player and used >= 0 and phase == "battle":
				var h: Actor = bs.hero
				var top: Tech = null
				for t in bs.b.hero_options(h):
					if top == null or t.req_prof > top.req_prof: top = t
				ok(h.school == schools[si] and h.learned.size() == 7, "สาย %s รู้ %d ท่า · ตัวเลือกตอนนี้ %d" % [schools[si], h.learned.size(), bs.b.hero_options(h).size()])
				var foe: Actor
				for a in bs.b.actors:
					if a.side == "foe" and not a.down: foe = a; break
				print("     ใช้ ", top.name if top else "-", " (req ", top.req_prof if top else 0, ")")
				bs._commit({"kind": "tech", "tech": top, "target": foe})
				used = -1; phase = "shot"; set_meta("t", n)
		"shot":
			if n - int(get_meta("t")) == int(OS.get_environment("AT")):
				root.get_viewport().get_texture().get_image().save_png(_shot() % si)
			if n - int(get_meta("t")) == 40:
				var bs = _find("BattleScreen")
				if bs != null:
					bs.auto = true; bs.step_delay = 0.01; bs.end_delay = 0.01
					if bs._waiting_player: bs._commit({"kind": "guard"})
				phase = "end"
		"end":
			if _find("BattleScreen") == null:
				phase = "wait_free"
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/labschools_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/labschools_%d.png")
