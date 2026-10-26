extends SceneTree
# ปิดตบทิ้งบนแมพ: ความชำนาญสูงมากชนสไลม์ t5 → ต้องเข้าฉากต่อสู้ ไม่ตบทิ้ง · prof_gain ของมอนอ่อนยังเป็น 0
var ow
var fails := 0
func ok(c, m): print(("OK   " if c else "FAIL ") + m); fails += 0 if c else 1
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _run() -> void:
	await process_frame
	while ow.busy: await process_frame
	ow.ps.prof = 40
	var slime = null
	for e in ow.enemies:
		if e.group[0] == "M01": slime = e
	ok(Formulas.is_swat(5, 40) and not Formulas.map_swat(5, 40), "สไลม์ t5 อ่อนกว่าเกณฑ์ แต่ไม่ตบทิ้งบนแมพ")
	var gold: int = ow.ps.gold
	ow.call_deferred("_encounter", slime, "")
	for i in 5: await process_frame
	var bs = null
	for c in ow.get_children():
		if c is BattleScreen: bs = c
	ok(bs != null, "ชนแล้วเข้าฉากต่อสู้")
	ok(ow.ps.gold == gold, "ไม่ได้เงินตบทิ้ง")
	ok(Formulas.prof_gain(5, 40) == 0, "มอนอ่อนยังให้ความชำนาญ 0 (กันฟาร์ม)")
	slime.set_danger(40)
	ok(slime.body_color != Color("7a7a7a"), "วงสีไม่เป็นสีเทา (ตบได้) แล้ว")
	print("FAILS ", fails)
	quit()
