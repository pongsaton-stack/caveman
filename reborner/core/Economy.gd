# core/Economy.gd — เงินทั้งเกมผ่านที่นี่ที่เดียว (GDD 9) · ไม่มี node
# ค่าทั้งหมดอยู่ใน data/economy.csv · inflation.csv · shops.csv · materials.csv · tomes.csv · items.csv · weapons.csv
# ราคา = ฐาน × PRICE_MULT × ตัวคูณตาม EC (inflation.csv) · รายได้ = สูตรเดิม × INCOME_MULT · ที่อื่นห้ามคูณราคาเอง
class_name Economy
extends RefCounted

static var _kv := {}
static var _infl: Array[Dictionary] = []
static var _shops: Array[Dictionary] = []
static var _mats := {}      # ชื่อของดรอป → แถว materials.csv (ps.materials เก็บตามชื่อ)
static var _tomes := {}     # spell_id → แถว tomes.csv
static var _items := {}     # item_id → แถว items.csv

## โหลดใหม่จาก data/ — เทสต์เรียกเพื่อล้างค่าที่ set_value ไว้
static func reload() -> void:
	_kv.clear()
	for r in CsvDb.load_csv("res://data/economy.csv"):
		_kv[str(r["key"])] = float(r["value"])
	_infl.clear()
	for r in CsvDb.load_csv("res://data/inflation.csv"):
		_infl.append(r)
	_infl.sort_custom(func(a, b): return int(a["ec"]) < int(b["ec"]))
	_shops = CsvDb.load_csv("res://data/shops.csv")
	_mats = CsvDb.index_by(CsvDb.load_csv("res://data/materials.csv"), "name")
	_tomes = CsvDb.index_by(CsvDb.load_csv("res://data/tomes.csv"), "spell_id")
	_items = CsvDb.index_by(CsvDb.load_csv("res://data/items.csv"), "item_id")

static func _ensure() -> void:
	if _kv.is_empty():
		reload()

static func num(key: String) -> float:
	_ensure()
	if not _kv.has(key):
		push_error("economy.csv ไม่มี %s" % key)
		return 0.0
	return _kv[key]

## ใช้ในเทสต์/เครื่องวัดเท่านั้น — เกมอ่านจาก CSV
static func set_value(key: String, v: float) -> void:
	_ensure()
	_kv[key] = v

# ── ราคา ──────────────────────────────────────────────────────
static func ec_mult(ec: int) -> float:
	_ensure()
	var m := 1.0
	for r in _infl:
		if ec >= int(r["ec"]):
			m = float(r["price_mult"])
	return m

static func price_mult(ec: int) -> float:
	return num("PRICE_MULT") * ec_mult(ec)

static func buy_price(base: float, ec: int) -> int:
	return roundi(base * price_mult(ec))

## ขายของที่ฐานคือราคาขายอยู่แล้ว (วัตถุดิบ)
static func sell_price(base: float, ec: int) -> int:
	return roundi(base * price_mult(ec))

## ขายคืนของที่ฐานคือราคาซื้อ (อาวุธ) — ได้ SELL_RATIO ของราคาซื้อช่วงนี้
static func resale_price(buy_base: float, ec: int) -> int:
	return roundi(buy_base * num("SELL_RATIO") * price_mult(ec))

# ── รายได้ ────────────────────────────────────────────────────
static func start_gold() -> int:
	return int(num("START_GOLD"))

static func win_gold(max_tier: int, foes: int) -> int:
	return roundi(max_tier * foes * num("WIN_GOLD_PER_TIER") * num("INCOME_MULT"))

static func swat_gold(foes: int) -> int:
	return roundi(num("SWAT_GOLD_PER_FOE") * foes * num("INCOME_MULT"))

static func dup_weapon_gold() -> int:
	return roundi(num("DUP_WEAPON_GOLD") * num("INCOME_MULT"))

## เงินที่เสียตอนแพ้ — ปัดลงแบบ int(gold / 2.0) เดิม
static func death_loss(gold: int) -> int:
	return int(gold * (1.0 - num("DEATH_KEEP")))

# ── ร้าน (data/shops.csv) ────────────────────────────────────
## แถวที่ร้านของภูมิภาคนี้วางขายตอน EC นี้ · อาวุธที่ไม่มี weapon_base ไม่ขึ้นร้าน (ใช้ในศึกไม่ได้)
static func shop_rows(region: String, ec: int, kind: String) -> Array[Dictionary]:
	_ensure()
	var out: Array[Dictionary] = []
	for r in _shops:
		if str(r["region"]) != region or int(r["ec_min"]) > ec or str(r["kind"]) != kind:
			continue
		if kind == "weapon" and str(PlayerState.weapon_row(str(r["ref_id"])).get("weapon_base", "")) == "":
			continue
		out.append(r)
	return out

static func ref_row(r: Dictionary) -> Dictionary:
	_ensure()
	var id := str(r["ref_id"])
	match str(r["kind"]):
		"item": return _items.get(id, {})
		"weapon": return PlayerState.weapon_row(id)
		"tome": return _tomes.get(id, {})
	return {}

static func base_price(r: Dictionary) -> int:
	return int(ref_row(r).get("price", 0))

static func stock_key(r: Dictionary) -> String:
	return "%s/%s" % [r["shop_id"], r["ref_id"]]

## ไม่มีในเซฟ = สต๊อกเต็มตามข้อมูล
static func stock_left(ps: PlayerState, r: Dictionary) -> int:
	return int(ps.shop_stock.get(stock_key(r), int(r["stock"])))

## "" = ซื้อได้ · ไม่งั้นคืนเหตุผลสั้นๆ ให้ UI
static func why_not_buy(ps: PlayerState, r: Dictionary) -> String:
	var id := str(r["ref_id"])
	if str(r["kind"]) == "weapon" and ps.weapons_owned.has(id):
		return "มีแล้ว"
	if str(r["kind"]) == "tome" and ps.tomes.has(id):
		return "มีแล้ว"
	if stock_left(ps, r) <= 0:
		return "หมด"
	if ps.gold < buy_price(base_price(r), ps.ec):
		return "เงินไม่พอ"
	return ""

static func buy(ps: PlayerState, r: Dictionary) -> bool:
	if why_not_buy(ps, r) != "":
		return false
	ps.gold -= buy_price(base_price(r), ps.ec)
	ps.shop_stock[stock_key(r)] = stock_left(ps, r) - 1
	var id := str(r["ref_id"])
	match str(r["kind"]):
		"item": ps.add_item(id)
		"weapon": ps.weapons_owned.append(id)
		"tome": ps.tomes.append(id)
	return true

## เติมสต๊อกเมื่อ EC เพิ่ม (GDD 9.2 "เติมเมื่อผ่าน checkpoint" · ตอนนี้ checkpoint = ชนะบอส) · เรียกซ้ำได้
static func restock_if_due(ps: PlayerState) -> void:
	if ps.ec > ps.stock_ec:
		ps.shop_stock.clear()
		ps.stock_ec = ps.ec

## เซฟก่อนมีหลายร้านเก็บสต๊อกเป็น item_id ล้วน → ย้ายเป็นคีย์ร้านแรกที่ขายของชิ้นนั้น
static func migrate_stock(ps: PlayerState) -> void:
	_ensure()
	for k in ps.shop_stock.keys():
		if str(k).contains("/"):
			continue
		for r in _shops:
			if str(r["ref_id"]) == str(k):
				ps.shop_stock[stock_key(r)] = int(ps.shop_stock[k])
				break
		ps.shop_stock.erase(k)

# ── ขาย ───────────────────────────────────────────────────────
static func material_row(name: String) -> Dictionary:
	_ensure()
	return _mats.get(name, {})

## ของที่ถือและร้านรับซื้อ (ตำรา/ของสำคัญไม่อยู่ใน materials.csv จึงขายไม่ได้)
static func sellable_materials(ps: PlayerState) -> Array[String]:
	var out: Array[String] = []
	for n in ps.materials:
		if int(ps.materials[n]) > 0 and not material_row(str(n)).is_empty():
			out.append(str(n))
	return out

static func sell_material(ps: PlayerState, name: String) -> int:
	var row := material_row(name)
	if row.is_empty() or int(ps.materials.get(name, 0)) <= 0:
		return 0
	var g := sell_price(float(row["sell_base"]), ps.ec)
	ps.materials[name] = int(ps.materials[name]) - 1
	if int(ps.materials[name]) <= 0:
		ps.materials.erase(name)
	ps.gold += g
	return g

static func why_not_sell_weapon(ps: PlayerState, id: String) -> String:
	if id == ps.weapon_id:
		return "กำลังถือ"
	if ps.weapons_owned.size() <= 1:
		return "ชิ้นสุดท้าย"
	if str(PlayerState.weapon_row(id).get("price", "")) == "":
		return "ร้านไม่รับ"
	return ""

static func weapon_resale(id: String, ec: int) -> int:
	return resale_price(float(PlayerState.weapon_row(id).get("price", 0)), ec)

static func sell_weapon(ps: PlayerState, id: String) -> int:
	if not ps.weapons_owned.has(id) or why_not_sell_weapon(ps, id) != "":
		return 0
	var g := weapon_resale(id, ps.ec)
	ps.weapons_owned.erase(id)
	ps.gold += g
	return g
