extends SceneTree
# tools/web/ui_mock_dump.gd — ค่าจริงจากเกม (สูตร/ข้อมูล) ให้หน้าตัวอย่าง UI · เรียกโดย tools/web/ui_mock_build.py
func _initialize() -> void:
	var td := TechDb.new(); td.load_from("res://data/techs.csv"); td.load_seize("res://data/seize_techs.csv")
	var ps := PlayerState.new(); ps.prof = 20
	ps.init_new(td, Vector2i.ZERO); ps.sync_weapon(td)
	ps.learned.append("เขี้ยวพุ่ง"); ps.learned.append("กวาด")
	ps.equip(PlayerState.weapon_row("W23"), td, 28)
	ps.learned.append("หักเกราะ")
	ps.insight = 14.0
	ps.reads = {"M06": {"name": "ผลุบผลับ", "p": 2, "need": 3, "on": true}}
	var h := ps.make_hero()
	var out := {"prof": ps.prof, "hp": h.max_hp, "sp": h.max_sp, "atk": h.atk, "def": h.def_val, "spd": h.spd,
		"mem": ps.memory_slots(), "read_slots": ps.read_slots(), "school": ps.school, "steer": ps.steer, "weapon": ps.weapon_name,
		"base": ps.weapon_base, "learned": ps.learned, "owned": ps.weapons_owned}
	var mons := {}
	var by := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	for id in ["M01", "M03", "M06", "M15", "B1"]:
		var a := Actor.from_csv(by[id])
		mons[id] = {"name": a.name, "tier": a.tier, "hp": a.max_hp, "weak": a.weak, "resist": a.resist, "body": a.body, "sig": a.signature, "comp": a.comprehension}
	out["mons"] = mons
	out["comp_hp"] = int(Actor.from_csv(by["M03"]).max_hp * Formulas.COMPANION_HP_MULT)
	out["comp_hp6"] = int(Actor.from_csv(by["M06"]).max_hp * Formulas.COMPANION_HP_MULT)
	var techs := []
	for t in td.all:
		techs.append({"name": t.name, "school": t.school, "branch": t.branch, "parent": t.parent, "req": t.req_prof, "sp": t.sp, "power": t.power, "weight": t.weight, "scope": t.scope})
	out["techs"] = techs
	print("JSON:" + JSON.stringify(out))
	quit()
