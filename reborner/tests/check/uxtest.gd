extends SceneTree
var ow
var fails := 0
func ok(c: bool, m: String) -> void:
	print(("OK   " if c else "FAIL ") + m)
	if not c: fails += 1
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()
func _run() -> void:
	await process_frame
	ok(ow.ps.auto_battle == true, "เกมใหม่ สู้อัตโนมัติเปิด (UX ข้อ 1)")
	# drop: fake enemy at the cell right of hero, force roll
	var e := WorldEnemy.new()
	e.cell = ow.ps.cell + Vector2i.RIGHT
	ow.rng.seed = 1
	var rows: Array = [{"drop": "เมือกเถ้า", "drop_rate": 100}, {"drop": "ไม่ดรอป", "drop_rate": 0}]
	ow._drop_loot(e, rows)
	var key := PlayerState.key_of(e.cell)
	ok(ow.ps.ground_drops.get(key, []) == ["เมือกเถ้า"], "ดรอปตามโอกาส 100% ได้ · 0% ไม่ได้")
	ok(ow.drop_nodes.has(key), "ไอคอนดรอปขึ้นตรงจุดทันที (UX ข้อ 3)")
	var d: Dictionary = ow.ps.to_dict()
	var p2 := PlayerState.new(); p2.from_dict(d)
	ok(p2.ground_drops.has(key) and p2.auto_battle == true, "เซฟ/โหลดจำของบนพื้น + สวิตช์อัตโนมัติ")
	var before := int(ow.ps.materials.get("เมือกเถ้า", 0))
	ow.ps.cell = e.cell
	ok(ow._pick_up_drops(), "เดินทับ = เก็บ")
	ok(int(ow.ps.materials.get("เมือกเถ้า", 0)) == before + 1 and not ow.ps.ground_drops.has(key), "ได้วัสดุ · หายจากพื้น")
	# paging
	ow._show("1\n2\n3\n4\n5", 3.0)
	ok(ow.panel_label.text == "1\n2" and ow._pages.size() == 2, "ข้อความ 5 บรรทัด = 3 หน้า หน้าละ ≤2 (UX ข้อ 5)")
	print("FAILS ", fails)
	quit()
