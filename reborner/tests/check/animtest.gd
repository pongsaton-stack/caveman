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
		seen[screen._hero_tex.texture] = true   # px_set อ่านไฟล์ตรง (ImageTexture ไม่มี resource_path) → เก็บตัว texture
		if screen.hero != null and screen.hero.down: hero_down_ever = true
	return false

func _done(r: Dictionary) -> void:
	print("seen ", seen.size(), " ภาพ · won=", r["won"])
	# Rion ชุดห้องทดลอง px_set (kwan 30 ต.ค. เอาของห้องทดลองลงเกม) · ไม่มีไฟล์ร่าง = ชุด rion_px เดิม
	var wid: String = screen.hero.weapon_id
	ok(wid != "", "ตัวเอกรู้อาวุธที่ถือ (%s)" % wid)
	var px := screen._px_clip("pls_idle_bl")
	ok(px.size() == 4 and screen._tex_idle_loop.size() == 4, "ยืนหายใจ px_set 4 เฟรม")
	for i in screen._tex_attack.size():
		ok(seen.has(screen._tex_attack[i]), "ท่าฟันครบทุกเฟรม: %d" % i)
	ok(screen._tex_attack.size() >= 4, "ท่าฟัน %d เฟรม" % screen._tex_attack.size())
	ok(screen._tex_hurt.size() > 0 and seen.has(screen._tex_hurt[0]), "เห็นท่าโดนตีเฟรมแรก")
	ok(screen._tex_idle == screen._tex_idle_loop[0], "ภาพยืน = เฟรมแรกของวงหายใจ")
	if hero_down_ever:
		ok(seen.has(screen._tex_ko[screen._tex_ko.size() - 1]), "ตัวเอกล้ม → ท่านอนเฟรมสุดท้าย")
	print("FAILS ", fails)
	quit()
