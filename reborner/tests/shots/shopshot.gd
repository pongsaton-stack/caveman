extends SceneTree
# ร้านค้า 5 แท็บ (ซื้อยา · ซื้ออาวุธ · ซื้อตำรา · ขายวัตถุดิบ · ขายอาวุธ) ที่ EC 6 (ราคา ×1.25) · ภาพ 0-4 ตามแท็บ
var ow; var n := 0
func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
func _shop():
	for c in ow.get_children():
		if c is ShopScreen: return c
func _process(_d: float) -> bool:
	n += 1
	if n == 20:
		ow.enemy_clock = -999.0
		ow.ps.ec = 6
		ow.ps.stock_ec = 6
		ow.ps.equip(PlayerState.weapon_row("CR-2"), ow.techs, 28)
		ow.ps.materials = {"เมือกเถ้า": 3, "หินดิบ": 1, "ปีกบาง": 2, "เขี้ยวหมาป่า": 4, "ตำรา White \"คืน LP\"": 1}
		ow.ps.tomes.append("WH-1")
		ow._open_shop()
	for t in 5:
		if n == 26 + t * 6: _shop()._set_tab(t)
		if n == 30 + t * 6: root.get_viewport().get_texture().get_image().save_png(_shot() % t)
	if n == 60:
		print("shop shots ok"); quit()
	return false

# ที่เก็บภาพ: $SHOT ถ้ามี ไม่งั้น tests/out/shopshot_<i>.png
func _shot() -> String:
	if OS.has_environment("SHOT"): return OS.get_environment("SHOT")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/out"))
	return ProjectSettings.globalize_path("res://tests/out/shopshot_%d.png")
