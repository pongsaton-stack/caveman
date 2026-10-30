extends SceneTree
# แผนที่จริง: ยึดท่าหลังเข้าใจท่าเด่น · มอนขอเข้าทีมหลังชนะ · มอนอันตรายหลับจนมีพวก (kwan 30 ต.ค.)
var ow
var fails := 0
func ok(c: bool, msg: String) -> void:
	print(("OK   " if c else "FAIL ") + msg)
	if not c: fails += 1
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _scr():
	for c in ow.get_children():
		if c is RecruitScreen and not c.is_queued_for_deletion(): return c
	return null
func _sleepers() -> Dictionary:
	var out := {}
	for e in ow.enemies:
		out[e.label_text] = e.asleep
	return out
func _run() -> void:
	await process_frame
	ok(ow.ps.party.is_empty(), "เกมใหม่: Rion คนเดียว")
	var sl := _sleepers()
	print("  หลับ: ", sl)
	ok(sl.get("ค้างคาวเงา x2", false) and sl.get("หมาป่าคู่", false) and sl.get("ราชาหนอนเถ้า", false), "ค้างคาว/หมาป่า/บอสหลับตอนยังไม่มีพวก")
	ok(not sl.get("สไลม์เถ้า", true) and not sl.get("หนอนหิน", true), "สไลม์/หนอนหินตื่น")
	# ── ยึดท่า: เสนอเฉพาะมอนที่มีท่ายึด ──
	ow.call_deferred("_offer_recruits", ["M01", "M03", "M02"])
	await process_frame
	await process_frame
	var scr = _scr()
	ok(scr != null and scr.seize_cost > 0 and scr.cost < 0 and not scr.asking, "M03 เสนอยึดท่าอย่างเดียว (ไม่มีรับเข้าทีมในกล่องนี้)")
	if scr: scr._done("seize")
	await process_frame
	await process_frame
	ok(_scr() == null, "M01/M02 ไม่มีท่ายึด ไม่เสนอ")
	# ── ขอเข้าทีม: ยังไม่มีพวก หนอนหินขอแน่นอน ──
	ow.call_deferred("_offer_allies", ["M03", "M01"], false)
	await process_frame
	await process_frame
	scr = _scr()
	ok(scr != null and scr.asking and scr.mon_name == "หนอนหิน", "หนอนหินขอเข้าทีม (การันตีพวกตัวแรก)")
	if scr: scr._done("")
	await process_frame
	await process_frame
	scr = _scr()
	ok(scr != null and scr.asking and scr.mon_name == "สไลม์เถ้า", "ไม่รับ → ตรวจชนิดถัดไปต่อ (สไลม์)")
	if scr: scr._done("recruit")
	await process_frame
	await process_frame
	ok(_scr() == null and ow.ps.party.size() == 1, "รับแล้วจบการตรวจของศึกนั้น")
	ow._refresh_enemy_colors()
	sl = _sleepers()
	ok(not sl.get("ค้างคาวเงา x2", true) and not sl.get("หมาป่าคู่", true) and sl.get("ราชาหนอนเถ้า", false), "มีพวก 1 ตัว: ค้างคาว/หมาป่าตื่น · บอสยังหลับ (ต้อง 2 ตัว)")
	# ── ศึกบอสไม่ตรวจ ──
	ow.call_deferred("_offer_allies", ["M15"], true)
	await process_frame
	await process_frame
	ok(_scr() == null, "ศึกบอสไม่มีการขอเข้าทีม")
	print("FAILS %d" % fails)
	quit(1 if fails > 0 else 0)
