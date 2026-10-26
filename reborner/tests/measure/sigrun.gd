extends SceneTree
# ศึกเดี่ยวแบบเห็นทุกบรรทัด: หาศึกที่มอนได้ใช้ท่าเด่นที่มีผลจริง
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	for foe_id in ["M03", "M06"]:
		var shown := false
		for s in 200:
			seed(s)
			var b := Battle.new(); b.techs = techs; b.capture = true
			var h := Actor.new(); h.id = "hero"; h.name = "Rion"; h.side = "ally"; h.is_hero = true
			h.tier = 8; h.max_hp = Formulas.hero_hp(8); h.hp = h.max_hp; h.max_sp = Formulas.hero_sp(8, 0); h.sp = h.max_sp
			h.atk = Formulas.hero_atk(8, 14); h.def_val = Formulas.hero_def(8); h.spd = 120; h.school = "คม"
			h.learned.append(techs.root_of("คม").name)
			b.actors.append(h)
			for j in 2: b.actors.append(Actor.from_csv(by_id[foe_id]))
			b.run()
			var txt := "\n".join(b.log_lines)
			if txt.find("DEF +") >= 0 or txt.find("ผลุบผลับ — AV") >= 0:
				print("=== %s seed %d ===" % [foe_id, s]); print(txt); shown = true; break
		if not shown: print("=== %s: ไม่เคยใช้ท่าเด่นใน 200 ศึก ===" % foe_id)
	quit()
