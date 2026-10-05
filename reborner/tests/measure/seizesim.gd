extends SceneTree
# ตัวเอกมี/ไม่มีท่ายึด เทียบกัน 200 ศึก/แถว (AI เล่นทั้งสองฝั่ง)
const N := 1000
func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv"); techs.load_seize("res://data/seize_techs.csv")
	print("แถว | ท่ายึด | ชนะ% | รอบเฉลี่ย | HP เหลือ% | ใช้เกราะแข็ง/ศึก | ใช้ผลุบผลับ/ศึก")
	for spec in [["M03", 10, 1], ["M15", 20, 2], ["M29", 25, 1], ["B1", 16, 1], ["B1", 20, 1]]:
		for with_seize in [false, true]:
			seed(4242)
			var won := 0; var rounds := 0; var hpleft := 0.0; var u1 := 0; var u2 := 0
			for i in N:
				var ps := PlayerState.new(); ps.prof = spec[1]; ps.hp = 9999; ps.sp = 9999
				ps.learned.append(techs.root_of(ps.school).name)
				if with_seize:
					ps.seize(techs.seize_for("M03")); ps.seize(techs.seize_for("M06"))
				var b := Battle.new(); b.techs = techs; b.capture = true
				var h := ps.make_hero(); b.actors.append(h)
				for j in spec[2]: b.actors.append(Actor.from_csv(by_id[spec[0]]))
				var r := b.run()
				if r["won"]: won += 1
				rounds += int(r["rounds"]); hpleft += float(h.hp) / h.max_hp
				var txt := "\n".join(b.log_lines)
				u1 += txt.count("Rion ใช้ เกราะแข็ง"); u2 += txt.count("[ผลุบผลับ]")
			print("%s prof %d x%d | %s | %d%% | %.1f | %.0f%% | %.2f | %.2f" % [spec[0], spec[1], spec[2], "มี" if with_seize else "ไม่มี", won * 100 / N, rounds / float(N), hpleft * 100.0 / N, u1 / float(N), u2 / float(N)])
	quit()
