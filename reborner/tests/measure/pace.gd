extends SceneTree
# วัดจังหวะได้ของใหม่ (ความเบื่อ): เส้นทาง 60 ศึกแบบเดียวกับ Sim.tech_progression · 100 รอบ ต่างกันแค่ seed
# รายงาน: ศึกแรกที่ได้ท่าใหม่ · จำนวนท่าที่ได้ถึงศึกที่ 10/20/30/60 · ท่าหลบที่อ่านได้ · สวนกลับ
#   godot --headless --path . -s tests/measure/pace.gd
func _initialize() -> void:
	var sim = load("res://core/Sim.gd").new()
	sim.by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	sim.techs.load_from("res://data/techs.csv")
	var ladder := ["M15", "M19", "M25", "M29", "M31", "M35"]
	var runs := 100
	var first_sum := 0.0; var never := 0
	var at := {10: 0.0, 20: 0.0, 30: 0.0, 60: 0.0}
	var reads := 0.0; var counters := 0.0; var dodges := 0.0; var gaps := 0.0
	for r in runs:
		seed(7000 + r)
		var hero: Actor = sim.make_hero(20)
		var got := 0; var first := -1; var last := 0; var gap := 0
		for i in 60:
			var b := Battle.new(); b.techs = sim.techs
			hero.hp = hero.max_hp; hero.sp = hero.max_sp; hero.down = false; hero.statuses.clear()
			b.actors.append(hero)
			for m in sim.make_party(): b.actors.append(m)
			var f := Actor.from_csv(sim.by_id[ladder[mini(int(i / 10.0), ladder.size() - 1)]])
			b.actors.append(f)
			var res := b.run()
			var n: int = res["glimmer_log"].size() + int(res["reads"])
			if n > 0:
				if first < 0: first = i + 1
				gap = maxi(gap, i + 1 - last); last = i + 1
			got += res["glimmer_log"].size()
			counters += res["counters"]; dodges += res["dodges"]; reads += res["reads"]
			for k in at.keys():
				if i + 1 == k: at[k] += got
			hero.insight = 0.0; hero.insight_lock = 0
			hero.tier += Formulas.prof_gain(f.tier, hero.tier)
			hero.read_slots = Formulas.tech_slots(hero.tier) / 2
			hero.atk = Formulas.hero_atk(hero.tier, sim.WEAPON_BASE)
			hero.max_hp = Formulas.hero_hp(hero.tier); hero.max_sp = Formulas.hero_sp(hero.tier, 0)
			hero.def_val = Formulas.hero_def(hero.tier)
		gap = maxi(gap, 60 - last)
		gaps += gap
		if first < 0: never += 1
		else: first_sum += first
	print("รอบ %d · ได้ของใหม่ (ท่าหรือท่าหลบ) ครั้งแรกเฉลี่ยศึกที่ %.1f (ไม่ได้เลย %d รอบ) · ช่วงแห้งยาวสุดเฉลี่ย %.1f ศึก"
		% [runs, first_sum / maxf(runs - never, 1), never, gaps / runs])
	print("ท่าโจมตีสะสม: ศึก10 %.2f · ศึก20 %.2f · ศึก30 %.2f · ศึก60 %.2f"
		% [at[10] / runs, at[20] / runs, at[30] / runs, at[60] / runs])
	print("ต่อรอบ 60 ศึก: อ่านทางใหม่ %.2f · หลบได้ %.2f · สวนกลับ %.2f" % [reads / runs, dodges / runs, counters / runs])
	sim.free()
	quit()
