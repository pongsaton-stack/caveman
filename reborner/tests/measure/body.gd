extends SceneTree
# วัดความเข้ากับร่างกาย: ตัวเอกแต่ละสาย (รู้ท่ารากกับท่าที่ความชำนาญถึง) สู้มอนตัวแทนแต่ละร่างกาย ที่ความชำนาญ = tier มอน
# ใช้ค่า Formulas.BODY_GOOD/BAD ปัจจุบัน — สคริปต์กวาดค่าแก้ค่าคงที่แล้วรันซ้ำ เทียบส่วนต่างกับค่า 1.0
#   godot --headless --path . -s tests/measure/body.gd
const REPS := {"เกราะ": "M20", "กระดูก": "M18", "หิน": "M29", "นุ่ม": "M25", "เนื้อ": "M19", "ปีก": "M26", "ไม้": "M22", "วิญญาณ": "M21", "กลไก": "M17"}
const N := 300
func _initialize() -> void:
	var sim = load("res://core/Sim.gd").new()
	sim.by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	sim.techs.load_from("res://data/techs.csv")
	print("BODY_GOOD %.2f · BODY_BAD %.2f · %d ศึก/ช่อง · ชนะ%% (เวลา AV)" % [Formulas.BODY_GOOD, Formulas.BODY_BAD, N])
	var head := "สาย      "
	for k in REPS: head += "| %s " % k
	print(head)
	seed(4242)
	for school in sim.techs.schools():
		var line := "%-8s " % school
		for body in REPS:
			var f0 := Actor.from_csv(sim.by_id[REPS[body]])
			var wins := 0; var t := 0.0
			for i in N:
				var b := Battle.new(); b.techs = sim.techs
				var h: Actor = sim.make_hero(f0.tier, sim.WEAPON_BASE, school, "")
				for tt in sim.techs.all:   # ท่าที่ความชำนาญถึงในสายนั้น — ให้แต่ละสายใช้ท่าครบตามระดับ ไม่ใช่แค่ราก
					if tt.school == school and tt.req_prof <= f0.tier and not h.learned.has(tt.name): h.learned.append(tt.name)
				b.allow_glimmer = false
				b.actors.append(h)
				for m in sim.make_party(): b.actors.append(m)
				b.actors.append(Actor.from_csv(sim.by_id[REPS[body]]))
				var res := b.run()
				if res["won"]: wins += 1
				t += res["time"]
			line += "| %3d%% (%3.0f) " % [int(100.0 * wins / N), t / N]
		print(line)
	sim.free()
	quit()
