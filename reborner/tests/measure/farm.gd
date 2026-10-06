extends SceneTree
# วัด "ฟาร์มมอนอ่อน" — สู้มอนตัวเดิมซ้ำ 100 ศึก ด้วยตัวเอกคนเดิม (Insight ค้างข้ามศึกตาม Insight.CARRY_BATTLE)
# รายงานต่อมอน: ประกายสุ่ม · ประกายจาก Insight เต็ม · ศึกแรกที่ได้ท่าใหม่ · Insight ที่ได้ต่อศึก แยกตามแหล่ง
#   godot --headless --path . -s tests/measure/farm.gd
func _initialize() -> void:
	var sim = load("res://core/Sim.gd").new()
	sim.by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	sim.techs.load_from("res://data/techs.csv")
	var runs := 100; var battles := 100
	for spec in [["M01", 1, 15], ["M03", 1, 15], ["M03", 1, 25], ["M06", 2, 15], ["M06", 2, 25]]:
		var rnd := 0.0; var fill := 0.0; var first_sum := 0.0; var never := 0; var gain := 0.0
		for r in runs:
			seed(9000 + r)
			var hero: Actor = sim.make_hero(spec[2])
			var first := -1
			for i in battles:
				var b := Battle.new(); b.techs = sim.techs
				hero.hp = hero.max_hp; hero.sp = hero.max_sp; hero.down = false; hero.statuses.clear()
				b.actors.append(hero)
				for m in sim.make_party(): b.actors.append(m)
				for j in spec[1]: b.actors.append(Actor.from_csv(sim.by_id[spec[0]]))
				var before := hero.insight
				var res := b.run()
				if res["glimmers"] > 0 and first < 0: first = i + 1
				rnd += res["glimmers"] - res["from_fill"]; fill += res["from_fill"]
				gain += maxf(hero.insight - before, 0.0) if res["from_fill"] == 0 else 0.0
				hero.insight *= Insight.CARRY_BATTLE; hero.insight_lock = 0
				# ความชำนาญไม่โต — ผู้เล่นฟาร์มที่ระดับเดิม (มอนอ่อนให้ prof แทบไม่ได้อยู่แล้ว)
			if first < 0: never += 1
			else: first_sum += first
		print("%s x%d @prof %d · %d ศึก: ประกายสุ่ม %.2f · จาก Insight เต็ม %.2f · ได้ท่าแรกศึกที่ %s (ไม่ได้เลย %d/%d รอบ) · Insight เฉลี่ยต่อศึก %.2f"
			% [spec[0], spec[1], spec[2], battles, rnd / runs, fill / runs,
			   ("%.0f" % (first_sum / (runs - never))) if never < runs else "—", never, runs, gain / (runs * battles)])
	sim.free()
	quit()
