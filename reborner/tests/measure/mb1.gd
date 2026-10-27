extends SceneTree
# MB-1 หมาป่าคู่จ่าฝูง (data/monsters.csv MB01 + กลไกโกรธ data/enrage.csv) เทียบคู่ M15 ปกติ — ใช้ Battle จริง
# ทีมเริ่มเกม (Rion + M03 + M06 แบบ Sim/Overworld) · เป้า (kwan 27 ต.ค.): มีดครัว w14 ชนะ ~70%
#   <godot> --headless --path . -s res://tests/measure/mb1.gd [-- --n=400 --grid --hp=180,200 --atk=50,55]
#   ไม่ใส่ --grid = M15 ปกติ + MB01 ตาม CSV (ไม่โกรธ / โกรธ) · --grid = ไล่ HP × ATK ของ MB01 (โกรธ) เฉพาะ w14
var N := 400

func _init() -> void:
	randomize()
	var grid := false
	var hps := [160, 180, 200]
	var atks := [40, 45, 50, 55]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--n="): N = int(a.substr(4))
		if a == "--grid": grid = true
		if a.begins_with("--hp="): hps = Array(a.substr(5).split(",")).map(func(x): return int(x))
		if a.begins_with("--atk="): atks = Array(a.substr(6).split(",")).map(func(x): return int(x))
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	var mb: Dictionary = by_id["MB01"]
	var cases := []
	if grid:
		for hp in hps:
			for atk in atks:
				cases.append(["MB01 %d/%d โกรธ" % [hp, atk], "MB01", hp, atk, true, [14]])
	else:
		cases.append(["M15 ปกติ", "M15", -1, -1, false, [14, 22, 28]])
		cases.append(["MB01 %s/%s ไม่โกรธ" % [mb["hp"], mb["atk"]], "MB01", -1, -1, false, [14, 22, 28]])
		cases.append(["MB01 %s/%s โกรธ" % [mb["hp"], mb["atk"]], "MB01", -1, -1, true, [14, 22, 28]])
	for c in cases:
		var line := "%s:" % c[0]
		var enr := 0
		var total := 0
		for w in c[5]:
			for prof in [12, 16, 20]:
				var wins := 0
				for i in N:
					var b := Battle.new()
					b.techs = techs
					var ps := PlayerState.new()
					ps.prof = prof; ps.weapon_base = w
					ps.init_new(techs, Vector2i.ZERO)
					b.actors.append(ps.make_hero())
					for mid in ["M03", "M06"]:
						var m := Actor.from_csv(by_id[mid]); m.side = "ally"; m.loyalty = 3; m.max_hp = int(m.max_hp * 1.6); m.hp = m.max_hp; m.telegraph = {}
						b.actors.append(m)
					for j in 2:
						var e := Actor.from_csv(by_id[c[1]])
						if c[2] > 0: e.max_hp = c[2]; e.hp = c[2]
						if c[3] > 0: e.atk = c[3]
						if not c[4]: e.enrage = {}
						b.actors.append(e)
					var r := b.run()
					if r["won"]: wins += 1
					enr += int(r["enrages"]); total += 1
				line += "  w%d p%d %d%%" % [w, prof, int(100.0 * wins / N)]
		print(line + "  · โกรธ %.2f/ศึก" % (float(enr) / total))
	quit()
