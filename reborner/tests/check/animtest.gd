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
	screen = BattleScreen.new(); screen.step_delay = 0.08; screen.end_delay = 0.0; screen.cutins = false   # ตรวจท่าฟันเฟรมเดิม (ฉากห้องทดลองตรวจแยก)
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
	# Rion พิกเซล 32-bit (kwan 16 ต.ค. 2026): ถือมีดในภาพเอง · ภาพ weapons_held (วาดบน Rion เก่า) ไม่ใช้แล้ว
	var wid: String = screen.hero.weapon_id
	ok(wid != "", "ตัวเอกรู้อาวุธที่ถือ (%s)" % wid)
	ok(screen._hero_tex.texture.resource_path.begins_with(BattleScreen.SPRITE_DIR), "ภาพมาจาก " + BattleScreen.SPRITE_DIR)
	for i in screen._tex_attack.size():
		ok(seen.has("west_a%d.png" % i), "ท่าฟันครบทุกเฟรม: west_a%d" % i)
	ok(screen._tex_attack.size() >= 4, "ท่าฟัน %d เฟรม" % screen._tex_attack.size())
	ok(seen.has("west_h0.png"), "เห็น west_h0.png")
	ok(not seen.has("%s_0.png" % wid), "ไม่ปนภาพ Rion เก่าถืออาวุธ")
	ok(screen._tex_idle_loop.size() >= 2 and screen._tex_idle == screen._tex_idle_loop[0], "ยืนหายใจวน %d เฟรม" % screen._tex_idle_loop.size())
	if hero_down_ever:
		var last := "west_k%d.png" % (screen._tex_ko.size() - 1)
		ok(seen.has(last), "ตัวเอกล้ม → ท่านอน " + last)
	print("FAILS ", fails)
	quit()
