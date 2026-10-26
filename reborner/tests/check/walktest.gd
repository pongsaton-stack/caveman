extends SceneTree
# กดค้างเดินบนแมพจริง → เฟรมก้าวต้องโผล่ · ปล่อยปุ่ม → ยืน (เฟรม 0 ไม่เล่น) · ชนกำแพง → ไม่ย่ำ
var ow
var fails := 0
func ok(c, m): print(("OK   " if c else "FAIL ") + m); fails += 0 if c else 1
func _initialize() -> void:
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()

func _hold(action: String, ms: int) -> Dictionary:
	var hf := {}; var df := {}
	Input.action_press(action)
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < ms:
		await process_frame
		hf[ow.hero_sprite.frame] = true
		if ow.dog_sprite != null: df[ow.dog_sprite.frame] = true
	Input.action_release(action)
	return {"hero": hf.keys(), "dog": df.keys()}

func _run() -> void:
	await process_frame
	for e in ow.enemies: e.queue_free()
	ow.enemies.clear()
	var dirs := {"ui_left": Vector2i.LEFT, "ui_right": Vector2i.RIGHT, "ui_up": Vector2i.UP, "ui_down": Vector2i.DOWN}
	var best := ""; var run := 0
	for a in dirs:
		var n := 0; var c: Vector2i = ow.ps.cell
		while ow.map.walkable(c + dirs[a]) and n < 6:
			c += dirs[a]; n += 1
		if n > run: run = n; best = a
	print("เดิน ", best, " ได้ ", run, " ช่อง")
	while ow.busy: await process_frame   # ข้อความเปิดเกม 1.2 วิ
	ok(ow.dog_cell.y == ow.ps.cell.y or ow.dog_sprite.offset.x > 0.0, "เริ่มเกม: หมาไม่ซ่อนหลังตัวเอก")
	var start: Vector2i = ow.ps.cell
	var r: Dictionary = await _hold(best, 450)   # ~3 ช่อง
	var moved: int = (ow.ps.cell - start).length()
	print("ฮีโร่เฟรม ", r["hero"], " หมาเฟรม ", r["dog"], " เดินไป ", moved, " ช่อง")
	ok(moved >= 2, "กดค้างแล้วเดินหลายช่อง")
	ok(r["hero"].size() >= 3, "ฮีโร่ก้าวขาจริง (เห็น ≥3 เฟรม)")
	ok(r["dog"].size() >= 3, "หมาก้าวขาจริง (เห็น ≥3 เฟรม)")
	for i in 20: await process_frame
	ok(not ow.hero_sprite.is_playing() and ow.hero_sprite.frame == 0, "ปล่อยปุ่ม → ฮีโร่ยืน")
	ok(not ow.dog_sprite.is_playing() and ow.dog_sprite.frame == 0, "ปล่อยปุ่ม → หมายืน")
	# เดินต่อจนชนกำแพง แล้วกดค้างอีกรอบ
	while ow.map.walkable(ow.ps.cell + dirs[best]):
		await _hold(best, 160)
		while ow.busy: await process_frame
	for i in 5: await process_frame
	var w: Dictionary = await _hold(best, 300)
	ok(w["hero"] == [0] and not ow.hero_sprite.is_playing(), "ชนกำแพง = หันหน้า ไม่ย่ำ")
	# เดินขึ้น/ลง: หมาอยู่ช่องล่าง = วาดทับ Rion · อยู่ช่องบน = โดน Rion ทับ
	for a in ["ui_up", "ui_down"]:
		var c: Vector2i = ow.ps.cell
		if ow.map.walkable(c + dirs[a]) and ow.map.walkable(c + dirs[a] * 2):
			await _hold(a, 330)
			while ow.busy: await process_frame
			await process_frame
			var dog_below: bool = ow.dog_node.position.y > ow.hero_node.position.y
			ok((ow.dog_node.z_index > ow.hero_node.z_index) == dog_below, "%s: หมา%s → %s" % [a, "อยู่ล่าง" if dog_below else "อยู่บน", "ทับ Rion" if dog_below else "อยู่หลัง Rion"])
			ok(is_equal_approx(ow.dog_sprite.offset.x, ow.DOG_SIDE_PX), "%s: หมาเยื้องข้าง ไม่หายหลังตัว" % a)
	print("FAILS ", fails)
	quit()
