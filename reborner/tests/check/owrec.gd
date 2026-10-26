extends SceneTree
var ow
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _scr():
	for c in ow.get_children():
		if c is RecruitScreen: return c
	return null
func _run() -> void:
	await process_frame
	var before: int = ow.ps.party.size()
	ow.call_deferred("_offer_recruits", ["M01", "M03", "M02"])
	await process_frame
	await process_frame
	var scr = _scr()
	print("M01 prompt: ", scr != null and scr.mon_name != "", " seize_cost ", scr.seize_cost, " cost ", scr.cost)
	scr._done("recruit")
	await process_frame
	await process_frame
	print("party ", before, " -> ", ow.ps.party.size(), " last: ", ow.ps.party[-1]["name"])
	scr = _scr()
	print("M03 prompt (ยึดได้ รับไม่ได้): ", scr != null, " seize_cost ", scr.seize_cost if scr else -9, " cost ", scr.cost if scr else -9, " mem ", scr.memory_left if scr else -9)
	scr._done("seize")
	await process_frame
	await process_frame
	print("seized: ", ow.ps.seized, " mem ", ow.ps.used_memory(), "/", ow.ps.memory_slots())
	scr = _scr()
	print("M02 skipped (ไม่มีท่ายึด ไม่อยู่ใน recruits): ", scr == null)
	# ซ้ำ: M03 ยึดแล้ว ห้ามเสนอซ้ำ
	ow.call_deferred("_offer_recruits", ["M03"])
	await process_frame
	await process_frame
	print("M03 again not offered: ", _scr() == null)
	quit()
