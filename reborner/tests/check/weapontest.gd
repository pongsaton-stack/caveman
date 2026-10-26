extends SceneTree
# อาวุธชี้ทางตามสาย (kwan 6 ต.ค. 2026): ถืออาวุธ = สายท่า + กิ่งชี้ทาง · ศึกใช้ได้เฉพาะท่าสายที่ถือ · ประกายในสายนั้น
var fails := 0

func check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if not ok: fails += 1

func _initialize() -> void:
	var td := TechDb.new()
	td.load_from("res://data/techs.csv")
	var table := PlayerState.weapon_table()
	check(table.size() == 30, "weapons.csv 30 ชิ้น (%d)" % table.size())
	# ทุกกิ่งที่ชี้ต้องเป็นกิ่งจริงของสายอาวุธนั้น และกิ่งละ 1 ชิ้น (GDD 6.3)
	var seen := {}; var bad := []
	for id in table:
		var r: Dictionary = table[id]
		var st := str(r["steer"])
		if st == "": continue
		var found := false
		for t in td.all:
			if t.school == str(r["school"]) and t.branch == st: found = true
		if not found: bad.append(id)
		var k := str(r["school"]) + "/" + st
		if seen.has(k): bad.append(k)
		seen[k] = id
	check(bad.is_empty() and seen.size() == 18, "ชี้ทาง 18 กิ่ง กิ่งละ 1 ชิ้น ตรงสาย %s" % [bad])

	# เกมใหม่ = มีดทำครัว สาย คม ชี้ เขี้ยว
	var ps := PlayerState.new()
	ps.init_new(td, Vector2i.ZERO)
	ps.sync_weapon(td)
	check(ps.school == "คม" and ps.steer == "เขี้ยว" and ps.learned == ["ฟัน"], "เริ่มเกม: มีดทำครัว คม/เขี้ยว รู้ ฟัน")
	check(ps.make_hero().first_glimmer_pending, "เริ่มเกม: ยังไม่เคยประกาย")
	ps.learned.append("เขี้ยวพุ่ง")

	# เก็บไม้เบสบอล (หีบใช้รหัสเดิม W23) → สาย ทุบ ได้ท่าราก ทุบ · ไม่ชี้ทาง · ท่าคมไม่หาย
	ps.equip(PlayerState.weapon_row("W23"), td, 28)
	check(ps.school == "ทุบ" and ps.steer == "" and ps.weapon_base == 28 and ps.learned.has("ทุบ") and ps.learned.has("เขี้ยวพุ่ง"),
		"ไม้เบสบอล: สาย ทุบ · ได้ท่า ทุบ · ท่าคมยังอยู่ · %s" % [ps.learned])
	var h := ps.make_hero()
	check(not h.first_glimmer_pending, "เคยประกายในสายอื่นแล้ว ไม่นับเป็นครั้งแรก")
	var b := Battle.new(); b.techs = td; b.actors.append(h)
	var names := []
	for t in b.usable(h): names.append(t.name)
	check(names == ["ทุบ"], "ถือไม้เบสบอล ใช้ได้แค่ท่าสาย ทุบ (%s)" % [names])
	var cand := []
	for t in td.candidates(h.learned, h.school, 30): cand.append(t.school)
	check(not cand.is_empty() and cand.all(func(s): return s == "ทุบ"), "ประกายได้แต่ท่าสาย ทุบ (%d ท่า)" % cand.size())

	# สลับกลับมีด → ท่าคมกลับมา
	ps.equip(PlayerState.weapon_row("SL-1"), td)
	h = ps.make_hero(); b = Battle.new(); b.techs = td; b.actors.append(h)
	names = []
	for t in b.usable(h): names.append(t.name)
	check(ps.weapon_base == 14 and names == ["ฟัน", "เขี้ยวพุ่ง"], "สลับกลับมีด: ค่า 14 · ใช้ ฟัน/เขี้ยวพุ่ง ได้อีก (%s)" % [names])
	check(ps.weapons_owned == ["SL-1", "CR-2"], "เก็บอาวุธทั้งสองชิ้นไว้สลับ")

	# ชี้ทาง ×2 ไปกิ่งของอาวุธ: ถือไม้เบสบอลไม้ร้าว (ชี้ สั่นสะเทือน) รู้แค่ราก ใช้ ทุบ → กระแทกพื้น หนัก 8 จาก 4+4+8 = 50%
	ps.equip(PlayerState.weapon_row("CR-1"), td)
	var tub := td.get_tech("ทุบ")
	var hit := 0
	seed(42)
	for i in 4000:
		var g := td.roll_glimmer(["ทุบ"], "ทุบ", 30, tub, ps.steer)
		if g.branch == "สั่นสะเทือน": hit += 1
	check(absf(hit / 4000.0 - 0.5) < 0.03, "ไม้ร้าวชี้ทาง สั่นสะเทือน: ได้กิ่งนั้น %.1f%% (คาด 50%%)" % (100.0 * hit / 4000.0))

	# เซฟเก่า: ถือไม้เบสบอลแต่สายยังเป็น คม และไม่มี weapon_id → โหลดแล้วสายถูก
	var old := {"weapon_name": "ไม้เบสบอลอลูมิเนียม", "weapon_base": 28, "school": "คม", "steer": "เขี้ยว", "learned": ["ฟัน", "ปาดไว"]}
	var ps2 := PlayerState.new(); ps2.from_dict(old); ps2.sync_weapon(td)
	check(ps2.school == "ทุบ" and ps2.weapon_id == "CR-2" and ps2.learned.has("ทุบ") and ps2.learned.has("ปาดไว") and ps2.weapons_owned.has("SL-1"),
		"เซฟเก่าไม้เบสบอล: สาย ทุบ · มีดยังอยู่ให้สลับ · ท่าเดิมไม่หาย")
	var ps3 := PlayerState.new(); ps3.from_dict(ps.to_dict()); ps3.sync_weapon(td)
	check(ps3.weapon_id == "CR-1" and ps3.steer == "สั่นสะเทือน" and ps3.weapons_owned == ps.weapons_owned, "เซฟ/โหลดอาวุธครบ")
	print("FAILS ", fails)
	quit()
