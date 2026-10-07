extends SceneTree
# ศึกอัตโนมัติจริง step_delay สั้น → เก็บชื่อไฟล์ภาพตัวเอกที่โผล่ทุกเฟรม
var screen: BattleScreen
var seen := {}
var hero_down_ever := false
var fails := 0
func ok(c, m): print(("OK   " if c else "FAIL ") + m); fails += 0 if c else 1

func _initialize() -> void:
	var by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	var ps := PlayerState.new(); ps.prof = 8; ps.weapon_base = 14
	ps.init_new(techs, Vector2i.ZERO)
	var b := Battle.new(); b.techs = techs
	b.actors.append(ps.make_hero())
	for j in 2: b.actors.append(Actor.from_csv(by_id["B1"]))
	screen = BattleScreen.new(); screen.step_delay = 0.08; screen.end_delay = 0.0
	screen.setup(b, "anim", true)
	screen.finished.connect(_done)
	root.add_child(screen)

func _process(_d: float) -> bool:
	if screen != null and is_instance_valid(screen) and screen._hero_tex != null and screen._hero_tex.texture != null:
		seen[screen._hero_tex.texture.resource_path.get_file()] = true
		if screen.hero != null and screen.hero.down: hero_down_ever = true
	return false

func _done(r: Dictionary) -> void:
	print("seen ", seen.keys(), " won=", r["won"])
	# ถืออาวุธที่ติดตั้ง (kwan 7 ต.ค. 2026): เริ่มเกม = มีดทำครัว → ภาพ weapons_held/<id>_0–4 แทน west/west_a
	var wid: String = screen.hero.weapon_id
	ok(wid != "", "ตัวเอกรู้อาวุธที่ถือ (%s)" % wid)
	for n in ["%s_0.png" % wid, "%s_1.png" % wid, "%s_3.png" % wid, "west_h0.png"]:
		ok(seen.has(n), "เห็น " + n)
	ok(not seen.has("west_a0.png"), "ไม่ใช้ท่าฟันมีดเดิมเมื่อมีภาพถืออาวุธ")
	if hero_down_ever:
		ok(seen.has("west_k1.png"), "ตัวเอกล้ม → ท่านอน")
	print("FAILS ", fails)
	quit()
