extends SceneTree
# ไม้ตาย: ตัวเอก prof 45 ใช้ "วงล้อ" ด้วยมือ แล้วบันทึกภาพทุก 3 เฟรม → $SHOT
var screen: BattleScreen
var b: Battle
var techs: TechDb
var fired := -1
var n := 0
func _initialize() -> void:
	var by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	techs = TechDb.new(); techs.load_from("res://data/techs.csv")
	var ps := PlayerState.new(); ps.prof = 45; ps.weapon_base = 28
	ps.init_new(techs, Vector2i.ZERO)
	b = Battle.new(); b.techs = techs
	var h := ps.make_hero(); h.sp = h.max_sp
	var tn := OS.get_environment("TECH") if OS.has_environment("TECH") else "bl4"; h.school = techs.get_tech(tn).school; h.learned.append(tn)
	b.actors.append(h)
	for mid in ["M03", "M06"]:
		var m := Actor.from_csv(by_id[mid]); m.side = "ally"; b.actors.append(m)
	for mid in (OS.get_environment("FOES") if OS.has_environment("FOES") else "M01,M02").split(","): b.actors.append(Actor.from_csv(by_id[mid]))
	screen = BattleScreen.new(); screen.step_delay = 0.6
	screen.setup(b, "ทดสอบไม้ตาย", false)
	root.add_child(screen)

func _process(_d: float) -> bool:
	n += 1
	if fired < 0 and screen._waiting_player:
		var foe: Actor
		for a in b.actors:
			if a.side == "foe": foe = a; break
		fired = n
		screen._commit({"kind": "tech", "tech": techs.get_tech(OS.get_environment("TECH") if OS.has_environment("TECH") else "bl4"), "target": foe})
	if fired >= 0 and n - fired <= 60 and (n - fired) % 3 == 0:
		root.get_viewport().get_texture().get_image().save_png(_shot() % (n - fired))
	if fired >= 0 and n - fired > 60: quit()
	if n > 2000: quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/ultshot_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/ultshot_%d.png")
