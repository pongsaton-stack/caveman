extends SceneTree
# MB-1 หมาป่าคู่จ่าฝูง (ข้อเสนอทีมรอบ 3) เทียบคู่ M15 ปกติ — ใช้ Battle จริง · ทีมเริ่มเกม (Rion + M03 + M06 แบบ Sim/Overworld)
# ยังไม่มีกลไก "โกรธเมื่อคู่ตาย" ในเกม → ผลของ MB-1 ที่นี่ = ขอบบน (จริงจะยากกว่า)
#   <godot> --headless --path . -s res://tests/measure/mb1.gd
const N := 400
func _init() -> void:
	randomize()
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	for foe in [["M15 ปกติ", 130, 85], ["MB-1 ทีม (240/85)", 240, 85], ["MB-1 สาย A (180/55)", 180, 55], ["MB-1 (200/55)", 200, 55]]:
		var line := "%s:" % foe[0]
		for w in [14, 22, 28]:
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
						var e := Actor.from_csv(by_id["M15"])
						e.max_hp = foe[1]; e.hp = foe[1]; e.atk = foe[2]
						b.actors.append(e)
					if b.run()["won"]: wins += 1
				line += "  w%d p%d %d%%" % [w, prof, int(100.0 * wins / N)]
		print(line)
	quit()
