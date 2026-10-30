extends SceneTree
# ศึกจริงตัดเข้าฉากท่าจากห้องทดลอง (kwan 30 ต.ค.): เห็นฉาก · ตัวเลขจริงส่งเข้าไป · ศึกเดินต่อจนจบ
var screen: BattleScreen
var n := 0
var seen := false
var embed_dmg := -1
var done := false
var fails := 0
func ok(c: bool, msg: String) -> void:
	print(("OK   " if c else "FAIL ") + msg)
	if not c: fails += 1
func _initialize() -> void:
	var by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	var ps := PlayerState.new(); ps.prof = 20; ps.weapon_base = 28
	ps.init_new(techs, Vector2i.ZERO)
	var b := Battle.new(); b.techs = techs
	b.actors.append(ps.make_hero())
	b.actors.append(Actor.from_csv(by_id["M01"]))
	screen = BattleScreen.new(); screen.step_delay = 0.05; screen.end_delay = 0.0
	screen.setup(b, "ทดสอบฉากท่า", true)
	root.add_child(screen)
	screen.finished.connect(func(_r): done = true)
func _process(_d: float) -> bool:
	n += 1
	for c in screen.get_children() if is_instance_valid(screen) else []:
		if c is CanvasLayer and c.layer == 20:
			for vp in c.find_children("*", "SubViewport", true, false):
				for st in vp.get_children():
					if not seen and st.get("embed") != null:
						seen = true
						embed_dmg = int(st.dmg)
						st.embed_done.emit.call_deferred()   # ข้ามฉาก (เหมือนกด Enter)
	if done or n > 3000:
		ok(seen, "ตัดเข้าฉากท่าห้องทดลอง")
		ok(embed_dmg > 0, "ตัวเลขดาเมจจริงส่งเข้าฉาก (%d)" % embed_dmg)
		ok(done, "ศึกเดินต่อจนจบหลังฉาก")
		print("FAILS %d" % fails)
		quit(1 if fails > 0 else 0)
	return false
