extends SceneTree
# ศึกเดียวแบบเห็นทุกบรรทัด: เกมใหม่ vs M01 และ M03
var ow
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _run() -> void:
	await process_frame
	print("party: ", ow.ps.party.map(func(p): return p["id"]), " prof ", ow.ps.prof, " learned ", ow.ps.learned)
	for ids in [["M01"], ["M03"]]:
		seed(5)
		var b := Battle.new(); b.techs = ow.techs; b.capture = true
		b.actors.append(ow.ps.make_hero())
		for m in ow.ps.make_companions(ow.by_id, ow._monster_slots()): b.actors.append(m)
		for id in ids: b.actors.append(Actor.from_csv(ow.by_id[id]))
		var res := b.run()
		print("==== ", ids, " rounds ", res.get("rounds"), " tech_uses ", res["tech_uses"])
		for l in b.log_lines: print(l)
	quit()
