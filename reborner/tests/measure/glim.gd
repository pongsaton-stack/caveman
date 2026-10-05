extends SceneTree
# วัดประกายตามเส้นทางเล่นจริง: เกมใหม่ → สู้ตามจุดเกิดบนแมพ (ไม่รวมบอส) · สู้อัตโนมัติ
var ow
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _run() -> void:
	await process_frame
	var order := [["M01"],["M03"],["M01"],["M03"],["M06","M06"],["M01"],["M06","M06"],["M03"],["M15","M15"],["M15","M15"],["M03"]]
	var runs := 300
	var tot_g := 0; var tot_uses := 0; var tot_b := 0; var any_g := 0; var tot_fill := 0
	var by_fight := []
	for i in order.size(): by_fight.append([0,0,0.0])
	for r in runs:
		seed(1000 + r)
		var ps := PlayerState.new()
		ps.school = ow.ps.school; ps.weapon_base = ow.ps.weapon_base; ps.prof = 8
		ps.init_new(ow.techs, ow.ps.cell)
		ps.party = ow.ps.party.duplicate(true)
		var got := 0
		for i in order.size():
			var b := Battle.new(); b.techs = ow.techs
			var hero := ps.make_hero(); b.actors.append(hero)
			for m in ps.make_companions(ow.by_id, ow._monster_slots()): b.actors.append(m)
			var mt := 0
			for id in order[i]:
				var f := Actor.from_csv(ow.by_id[id]); b.actors.append(f); mt = maxi(mt, f.tier)
			var res := b.run()
			tot_b += 1; tot_g += res["glimmers"]; tot_uses += res["tech_uses"]; tot_fill += res["fills"]
			by_fight[i][0] += res["glimmers"]; by_fight[i][1] += res["tech_uses"]
			by_fight[i][2] += Formulas.glimmer_chance(mt, ps.prof, float(hero.learned.size())/7.0, 0)
			got += res["glimmers"]
			if res["won"]:
				ps.absorb(hero); ps.prof += Formulas.prof_gain(mt, ps.prof)
			ps.rest()
		if got > 0: any_g += 1
		if r == 0: print("รอบแรก จบที่ prof ", ps.prof, " learned ", ps.learned)
	print("ศึก ", tot_b, " · ใช้ท่า ", tot_uses, " · ประกาย ", tot_g, " (", "%.2f%%" % (100.0*tot_g/max(tot_uses,1)), " ต่อท่า) · Insight เต็ม ", tot_fill)
	print("เล่นครบ ", order.size(), " ศึก แล้วได้ประกายอย่างน้อย 1 ครั้ง: ", any_g, "/", runs)
	for i in order.size():
		print("  ศึก ", i+1, " ", order[i], "  ใช้ท่า/ศึก %.1f  ประกาย/ศึก %.3f  โอกาสต่อท่าจากสูตร %.2f%%" % [by_fight[i][1]/float(runs), by_fight[i][0]/float(runs), 100.0*by_fight[i][2]/runs])
	quit()
