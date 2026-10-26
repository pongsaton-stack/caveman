extends SceneTree
# drives BattleScreen headless: whenever a menu is up, press a button (rotating choices)
var screen: BattleScreen
var results := []
var fights := [["B1", 1, 16, 28], ["M15", 2, 20, 30], ["M01", 1, 8, 14]]
var idx := 0
var presses := 0
var by_id: Dictionary
var techs := TechDb.new()

func _initialize() -> void:
	by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	techs.load_from("res://data/techs.csv")
	_start()

func _start() -> void:
	if idx >= fights.size():
		print("RESULTS ", results, " presses=", presses)
		quit()
		return
	var f = fights[idx]
	var ps := PlayerState.new()
	ps.prof = f[2]; ps.weapon_base = f[3]
	ps.init_new(techs, Vector2i.ZERO)
	var b := Battle.new()
	b.techs = techs
	b.actors.append(ps.make_hero())
	for mid in ["M03", "M06"]:
		var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * 1.6); m.hp = m.max_hp
		b.actors.append(m)
	for j in f[1]:
		b.actors.append(Actor.from_csv(by_id[f[0]]))
	screen = BattleScreen.new()
	screen.step_delay = 0.0
	screen.end_delay = 0.0
	screen.setup(b, "test %s" % f[0])
	screen.finished.connect(_done)
	root.add_child(screen)

func _done(r: Dictionary) -> void:
	results.append("%s won=%s rounds=%d glim=%d combos=%d guards=%d" % [fights[idx][0], r["won"], r["rounds"], r["glimmers"], r["combos"], r["guards"]])
	idx += 1
	_start.call_deferred()

func _process(_d: float) -> bool:
	if screen == null or not is_instance_valid(screen):
		return false
	var m: GridContainer = screen._menu
	var btns := m.get_children().filter(func(c): return c is Button and not c.is_queued_for_deletion())
	if btns.size() > 0:
		presses += 1
		var btn: Button = btns[presses % btns.size()]
		btn.pressed.emit()
	return false
