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
	# ดรอปอาวุธ (PITY_SPEC): M08 ตัวนับครบ 39 → ตัวถัดไปการันตี CR-1 · บรรทัดสรุปมีตัวเลข · เก็บ = เข้าคลัง · ชิ้นซ้ำ = เงิน
	var m08: Dictionary = ow.by_id["M08"]
	ow.ps.pity["M08"] = {"misses": 39, "kills": 39}
	var wl: Array[String] = ow._drop_loot(e, [m08])
	ok(ow.ps.ground_drops.get(key, []).has(PlayerState.WEAPON_DROP_PREFIX + "CR-1") and ow.drop_nodes.has(key), "ฆ่า M08 ครั้งที่ 40 → CR-1 ลงพื้น + ไอคอน")
	ok(wl.size() == 2 and "ดรอปอาวุธ" in wl[0] and "ฆ่า 40" in wl[1] and "0/40" in wl[1], "สรุปศึกบอกดรอป + เรต/ยอดฆ่า/การันตี %s" % [wl])
	ok(ow._pick_up_drops() and ow.ps.weapons_owned.has("CR-1"), "เดินทับเก็บ → CR-1 เข้าคลังอาวุธ")
	var g0: int = ow.ps.gold
	ow.ps.pity["M08"] = {"misses": 39, "kills": 79}
	ow._drop_loot(e, [m08])
	ow._pick_up_drops()
	ok(ow.ps.gold == g0 + WeaponDrop.dup_gold("CR-1") and ow.ps.weapons_owned.count("CR-1") == 1, "CR-1 ซ้ำ → +%d เงิน ไม่เพิ่มชิ้น" % WeaponDrop.dup_gold("CR-1"))
	# paging
	ow._show("1\n2\n3\n4\n5", 3.0)
	ok(ow.panel_label.text == "1\n2" and ow._pages.size() == 2, "ข้อความ 5 บรรทัด = 3 หน้า หน้าละ ≤2 (UX ข้อ 5)")
	print("FAILS ", fails)
	quit()
