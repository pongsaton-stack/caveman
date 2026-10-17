extends SceneTree
# เศรษฐกิจ (GDD 9) — ค่าเริ่มต้นต้องให้เงินเท่าโค้ดเดิมทุกบาท · ปุ่มเงินเฟ้อ/EC คูณทั้งซื้อและขาย · กติการ้าน · เซฟเก่าโหลดได้
var fails := 0

func check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if not ok: fails += 1

func _initialize() -> void:
	Economy.reload()
	var td := TechDb.new()
	td.load_from("res://data/techs.csv")

	# ── ค่าเริ่มต้น = สูตรเดิมใน Overworld/PlayerState ก่อนย้ายเข้า CSV ──
	check(Economy.start_gold() == 600 and PlayerState.new().gold == 600, "เงินเริ่ม 600 เท่าเดิม")
	var bad := []
	for t in [5, 8, 12, 20, 25, 42, 68]:
		for n in [1, 2, 3]:
			if Economy.win_gold(t, n) != t * n: bad.append([t, n])
	check(bad.is_empty(), "เงินชนะศึก = max_tier × จำนวนศัตรู เท่าเดิม %s" % [bad])
	check(Economy.swat_gold(1) == 2 and Economy.swat_gold(3) == 6, "ตบทิ้ง 2 ต่อตัว เท่าเดิม")
	check(Economy.dup_weapon_gold() == 50, "หีบอาวุธซ้ำ +50 เท่าเดิม")
	bad = []
	for g in [0, 1, 7, 99, 600, 601, 1333]:
		if Economy.death_loss(g) != int(g / 2.0): bad.append(g)
	check(bad.is_empty(), "ตายเสีย int(gold / 2.0) เท่าเดิม (รวมเลขคี่) %s" % [bad])

	# ── ตัวคูณ ──
	var infl := {}
	for r in CsvDb.load_csv("res://data/inflation.csv"): infl[int(r["ec"])] = float(r["price_mult"])
	var steps := infl.keys(); steps.sort()
	bad = []
	for ec in [0, 3, 4, 5, 6, 10, 11, 16, 17, 30]:
		var m := 1.0
		for s in steps:
			if ec >= s: m = infl[s]
		if Economy.buy_price(100, ec) != roundi(100 * m) or Economy.sell_price(40, ec) != roundi(40 * m): bad.append(ec)
	check(bad.is_empty() and infl.size() >= 2, "ราคาซื้อ/ขายขึ้นตามขั้น EC ใน inflation.csv %s" % [bad])
	check(Economy.buy_price(130, 0) == 130 and Economy.buy_price(20, 0) == 20, "EC 0 + PRICE_MULT 1 = ราคาร้านเดิม (130 / 20)")
	Economy.set_value("PRICE_MULT", 2.0)
	check(Economy.buy_price(100, 0) == 200 and Economy.sell_price(40, 0) == 80 and Economy.resale_price(140, 0) == roundi(140 * Economy.num("SELL_RATIO") * 2.0),
		"PRICE_MULT 2 คูณทั้งซื้อ ขายวัตถุดิบ และขายอาวุธ")
	check(Economy.buy_price(100, 11) == roundi(100 * 2.0 * Economy.ec_mult(11)), "PRICE_MULT ซ้อนกับเงินเฟ้อตาม EC")
	check(Economy.win_gold(25, 2) == 50 and Economy.death_loss(600) == 300, "PRICE_MULT ไม่แตะรายได้/ค่าปรับตาย")
	Economy.reload()
	Economy.set_value("INCOME_MULT", 2.0)
	check(Economy.win_gold(25, 2) == 100 and Economy.swat_gold(1) == 4 and Economy.dup_weapon_gold() == 100 and Economy.buy_price(100, 0) == 100,
		"INCOME_MULT คูณรายได้ ไม่แตะราคา")
	Economy.reload()
	var ratio := Economy.num("SELL_RATIO")
	check(ratio > 0.0 and ratio < 1.0 and Economy.resale_price(280, 0) == roundi(280 * ratio), "ขายอาวุธคืน = ราคาซื้อ × SELL_RATIO %.2f" % ratio)

	# ── ร้านภูมิภาค 1 ──
	var r1 := "ที่ราบเถ้า"
	var items := CsvDb.index_by(CsvDb.load_csv("res://data/items.csv"), "item_id")
	var stock_same := true
	var item_ids := []
	for r in Economy.shop_rows(r1, 0, "item"):
		item_ids.append(str(r["ref_id"]))
		if int(r["stock"]) != int(items[str(r["ref_id"])]["stock"]) or Economy.base_price(r) != int(items[str(r["ref_id"])]["price"]): stock_same = false
	check(item_ids == ["I01", "L01"] and stock_same, "ร้านภูมิภาค 1 ขาย I01/L01 ราคาและสต๊อกเดิม %s" % [item_ids])
	var cr2 := false
	var no_base := []
	var any_base_less := false
	for row in CsvDb.load_csv("res://data/shops.csv"):
		if str(row["kind"]) == "weapon" and str(PlayerState.weapon_row(str(row["ref_id"])).get("weapon_base", "")) == "": any_base_less = true
	for region in ["ที่ราบเถ้า", "เมืองใต้ซาก", "ยอดเขาคำสาป"]:
		for ec in range(0, 25):
			for r in Economy.shop_rows(region, ec, "weapon"):
				if str(PlayerState.weapon_row(str(r["ref_id"]))["weapon_base"]) == "": no_base.append(r["ref_id"])
				if region == r1 and str(r["ref_id"]) == "CR-2": cr2 = true
	check(any_base_less and no_base.is_empty(), "อาวุธที่ไม่มี weapon_base ไม่ขึ้นร้านเลย (ข้อมูลมีแถวแบบนี้ให้กรองจริง) %s" % [no_base])
	check(not cr2, "ไม้เบสบอลอลูมิเนียม (CR-2 ประตูบอส GDD 11.29) ไม่ขายในภูมิภาค 1 ทุก EC")
	var r2w := []
	for r in Economy.shop_rows("เมืองใต้ซาก", 5, "weapon"): r2w.append(r["ref_id"])
	check(r2w.has("CR-2") and Economy.shop_rows("เมืองใต้ซาก", 4, "weapon").is_empty(), "ร้านภูมิภาค 2 เปิดที่ EC 5 และขาย CR-2 %s" % [r2w])

	# ── ซื้อ / เติมสต๊อก ──
	var ps := PlayerState.new()
	ps.init_new(td, Vector2i.ZERO)
	ps.sync_weapon(td)
	var lp_row: Dictionary = Economy.shop_rows(r1, 0, "item")[1]
	check(Economy.buy(ps, lp_row) and ps.gold == 600 - 130 and Economy.stock_left(ps, lp_row) == 2 and ps.item_count("L01") == 1, "ซื้อยาเติมชีวิต: เงิน -130 · สต๊อก 3 → 2")
	Economy.buy(ps, lp_row); Economy.buy(ps, lp_row)
	check(Economy.stock_left(ps, lp_row) == 0 and Economy.why_not_buy(ps, lp_row) == "หมด" and not Economy.buy(ps, lp_row), "หมดสต๊อกแล้วซื้อไม่ได้")
	Economy.restock_if_due(ps)
	check(Economy.stock_left(ps, lp_row) == 0, "EC เท่าเดิม ไม่เติม")
	ps.ec = 1
	Economy.restock_if_due(ps)
	check(Economy.stock_left(ps, lp_row) == 3 and ps.stock_ec == 1, "EC เพิ่ม (ชนะบอส) → เติมสต๊อกเต็ม")
	Economy.restock_if_due(ps)
	check(Economy.stock_left(ps, lp_row) == 3, "เติมซ้ำไม่มีผล")
	var tome: Dictionary = Economy.shop_rows(r1, 0, "tome")[0]
	var g0 := ps.gold
	check(Economy.buy(ps, tome) and ps.tomes == [str(tome["ref_id"])] and ps.gold == g0 - Economy.buy_price(Economy.base_price(tome), 1), "ซื้อตำรา เก็บใน ps.tomes")
	check(Economy.why_not_buy(ps, tome) == "มีแล้ว" and not Economy.buy(ps, tome), "ตำราซื้อซ้ำไม่ได้")
	ps.gold = 5
	var herb: Dictionary = Economy.shop_rows(r1, 1, "item")[0]
	check(Economy.why_not_buy(ps, herb) == "เงินไม่พอ" and not Economy.buy(ps, herb) and ps.gold == 5, "เงินไม่พอซื้อไม่ได้ ไม่เสียเงิน")

	# ── ขาย ──
	ps.gold = 0
	ps.materials = {"เมือกเถ้า": 2, "ตำรา White \"คืน LP\"": 1}
	check(Economy.sellable_materials(ps) == ["เมือกเถ้า"], "ตำราที่ดรอปไม่อยู่ในรายการขาย")
	var mg := Economy.sell_material(ps, "เมือกเถ้า")
	check(mg == Economy.sell_price(float(Economy.material_row("เมือกเถ้า")["sell_base"]), ps.ec) and ps.gold == mg and int(ps.materials["เมือกเถ้า"]) == 1, "ขายวัตถุดิบ 1 ชิ้นได้ราคาตาม materials.csv × ตัวคูณ")
	Economy.sell_material(ps, "เมือกเถ้า")
	check(not ps.materials.has("เมือกเถ้า") and Economy.sell_material(ps, "เมือกเถ้า") == 0, "ขายหมดแล้วหายจากกระเป๋า")
	check(Economy.why_not_sell_weapon(ps, "SL-1") == "กำลังถือ" and Economy.sell_weapon(ps, "SL-1") == 0, "ขายอาวุธที่ถืออยู่ไม่ได้")
	ps.equip(PlayerState.weapon_row("CR-2"), td)
	ps.gold = 0
	var wg := Economy.sell_weapon(ps, "SL-1")
	check(wg == Economy.resale_price(140, ps.ec) and ps.gold == wg and ps.weapons_owned == ["CR-2"], "ถือ CR-2 แล้วขายมีดได้ %d" % wg)
	check(Economy.why_not_sell_weapon(ps, "CR-2") != "" and Economy.sell_weapon(ps, "CR-2") == 0, "ชิ้นสุดท้าย/ที่ถือ ขายไม่ได้")
	var ps_last := PlayerState.new()
	ps_last.weapons_owned.clear(); ps_last.weapons_owned.append("CR-2"); ps_last.weapon_id = "SL-1"
	check(Economy.why_not_sell_weapon(ps_last, "CR-2") == "ชิ้นสุดท้าย", "อาวุธชิ้นสุดท้ายขายไม่ได้แม้ไม่ได้ถือ")

	# ── เซฟ ──
	ps.gold = 777
	var d := ps.to_dict()
	var ps2 := PlayerState.new()
	ps2.from_dict(JSON.parse_string(JSON.stringify(d)))
	check(ps2.gold == 777 and ps2.tomes == ps.tomes and ps2.stock_ec == 1 and ps2.shop_stock == ps.shop_stock, "เซฟ/โหลด: เงิน ตำรา สต๊อก EC ที่เติม")
	var old := PlayerState.new()
	old.from_dict({"prof": 12, "gold": 321, "ec": 1, "shop_stock": {"I01": 4, "L01": 1}})
	Economy.migrate_stock(old)
	Economy.restock_if_due(old)
	check(old.gold == 321 and old.tomes.is_empty() and old.stock_ec == 1 and Economy.stock_left(old, lp_row) == 1 and Economy.stock_left(old, herb) == 4,
		"เซฟเก่า (ไม่มี tomes/stock_ec · คีย์สต๊อกแบบเก่า) โหลดได้ สต๊อกเดิมไม่หาย ไม่เติมฟรี %s" % [old.shop_stock])
	var bare := PlayerState.new()
	bare.from_dict({"prof": 8})
	check(bare.gold == 600, "เซฟที่ไม่มีเงินเลย = เงินเริ่ม")

	print("FAILS %d" % fails)
	quit()
