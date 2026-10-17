# world/ShopScreen.gd — ร้านค้า (ช่อง S บนแผนที่) · ของและสต๊อกจาก data/shops.csv · ราคาผ่าน Economy เท่านั้น
# สต๊อกจำกัดต่อร้าน (GDD 9.2: "เพดานที่มาจากจำนวนของ ทะลุไม่ได้") · เติมเมื่อ EC เพิ่ม (ชนะบอส = checkpoint ตอนนี้)
class_name ShopScreen
extends CanvasLayer

signal closed

const TABS := ["ซื้อยา", "ซื้ออาวุธ", "ซื้อตำรา", "ขายวัตถุดิบ", "ขายอาวุธ"]
const KINDS := ["item", "weapon", "tome"]

var ps: PlayerState
var region := ""
var tab := 0

var _root: Control
var _gold: Label
var _info: Label
var _tabs: HBoxContainer
var _scroll: ScrollContainer
var _menu: VBoxContainer

func setup(state: PlayerState, shop_region: String) -> void:
	ps = state
	region = shop_region
	Economy.restock_if_due(ps)

func _ready() -> void:
	layer = 10
	_root = UiKit.screen(self, "ร้านค้า — พ่อค้าเร่")
	_gold = UiKit.label("", 7, UiKit.C_TEXT)
	_gold.position = Vector2(4, 13)
	_root.add_child(_gold)
	_tabs = HBoxContainer.new()
	_tabs.position = Vector2(4, 26)
	_tabs.add_theme_constant_override("separation", 2)
	_root.add_child(_tabs)
	for i in TABS.size():
		var b := UiKit.button(TABS[i], 73)
		b.pressed.connect(_set_tab.bind(i))
		_tabs.add_child(b)
	_scroll = ScrollContainer.new()
	_scroll.position = Vector2(4, 42)
	_scroll.size = Vector2(376, 140)
	_scroll.follow_focus = true
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_root.add_child(_scroll)
	_menu = VBoxContainer.new()
	_menu.add_theme_constant_override("separation", 3)
	_menu.custom_minimum_size = Vector2(370, 0)
	_scroll.add_child(_menu)
	_info = UiKit.label("", 7, UiKit.C_GOLD)
	_info.position = Vector2(4, 186)
	_info.size = Vector2(376, 26)
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_info.max_lines_visible = 2
	_root.add_child(_info)
	_render(0)

func _set_tab(i: int) -> void:
	tab = i
	_info.text = ""
	_render(0)

func _render(focus_index: int) -> void:
	for c in _menu.get_children():
		_menu.remove_child(c)
		c.queue_free()
	_gold.text = "เงิน %d · ราคาช่วงนี้ ×%.2f (EC %d)" % [ps.gold, Economy.price_mult(ps.ec), ps.ec]
	for i in _tabs.get_child_count():
		var t: Button = _tabs.get_child(i)
		t.add_theme_stylebox_override("normal", UiKit.box(UiKit.C_LINE if i == tab else UiKit.C_PANEL, UiKit.C_GOLD if i == tab else UiKit.C_LINE))
	var buttons: Array[Button] = []
	if tab < KINDS.size():
		_buy_list(buttons)
	elif tab == 3:
		_material_list(buttons)
	else:
		_weapon_sell_list(buttons)
	if buttons.is_empty():
		_menu.add_child(UiKit.label(_empty_text(), 7, UiKit.C_MUTED))
	var out := UiKit.button("ออกจากร้าน", 370)
	out.pressed.connect(_close)
	_menu.add_child(out)
	buttons.append(out)
	var idx := clampi(focus_index, 0, buttons.size() - 1)
	while idx < buttons.size() - 1 and buttons[idx].disabled:
		idx += 1
	buttons[idx].grab_focus()

func _empty_text() -> String:
	match tab:
		0: return "ร้านนี้ไม่มียาขาย"
		1: return "ร้านภูมิภาคนี้ยังไม่มีอาวุธที่ใช้ได้ขาย"
		2: return "ร้านนี้ไม่มีตำราขาย"
		3: return "ยังไม่มีวัตถุดิบที่ร้านรับซื้อ — เก็บ 🎁 จากมอนที่ชนะ"
	return ""

func _add(text: String, why: String, info: String, cb: Callable, buttons: Array[Button]) -> void:
	var btn := UiKit.button(text + ("  · " + why if why != "" else ""), 370)
	btn.disabled = why != ""
	var idx := buttons.size()
	btn.pressed.connect(func(): cb.call(idx))   # cb มี payload ผูกไว้แล้ว → เรียกเป็น (idx, payload)
	btn.focus_entered.connect(func(): _info.text = info)
	_menu.add_child(btn)
	buttons.append(btn)

func _buy_list(buttons: Array[Button]) -> void:
	for r in Economy.shop_rows(region, ps.ec, KINDS[tab]):
		var ref := Economy.ref_row(r)
		var price := Economy.buy_price(Economy.base_price(r), ps.ec)
		var why := Economy.why_not_buy(ps, r)
		var text := ""
		var info := ""
		match str(r["kind"]):
			"item":
				text = "%s  %dg · ร้านเหลือ %d · มี %d" % [ref["name"], price, Economy.stock_left(ps, r), ps.item_count(str(r["ref_id"]))]
				info = str(ref.get("note", "")).split("·")[0].strip_edges()
				if str(ref.get("kind", "")) == "restore_lp":
					info += " · ชุบมอนที่หายถาวรไม่ได้"
			"weapon":
				text = "%s  %dg · สาย%s ค่า %s" % [ref["name"], price, ref["school"], ref["weapon_base"]]
				info = "ซื้อแล้วสลับใช้ได้ที่เมนู > อาวุธ"
			"tome":
				text = "ตำรา %s (%s)  %dg" % [ref["name"], ref["school"], price]
				info = "ยังอ่านไม่ได้ — สายเวทย์ยังไม่เข้าเกม (เก็บไว้ก่อนได้)"
		_add(text, why, info, _buy.bind(r), buttons)

func _material_list(buttons: Array[Button]) -> void:
	for n in Economy.sellable_materials(ps):
		var g := Economy.sell_price(float(Economy.material_row(n)["sell_base"]), ps.ec)
		_add("ขาย %s ×%d  · %dg/ชิ้น" % [n, int(ps.materials[n]), g], "", "ขายทีละชิ้น · ราคารับซื้อขึ้นตามช่วงเวลาเหมือนราคาขาย", _sell_material.bind(n), buttons)

func _weapon_sell_list(buttons: Array[Button]) -> void:
	for id in ps.weapons_owned:
		var row := PlayerState.weapon_row(id)
		var why := Economy.why_not_sell_weapon(ps, id)
		var info := "ขายแล้วหายจากกระเป๋า · ร้านภูมิภาคนี้อาจไม่มีขายคืน" if why == "" else "ขายไม่ได้: " + why
		_add("ขาย %s  %dg" % [row.get("name", id), Economy.weapon_resale(id, ps.ec)], why, info, _sell_weapon.bind(id), buttons)

func _buy(idx: int, r: Dictionary) -> void:
	if not Economy.buy(ps, r):
		return
	_render(idx)
	_info.text = "ซื้อ %s แล้ว" % Economy.ref_row(r)["name"]

func _sell_material(idx: int, n: String) -> void:
	var g := Economy.sell_material(ps, n)
	if g <= 0:
		return
	_render(idx)
	_info.text = "ขาย %s ได้ %d เงิน" % [n, g]

func _sell_weapon(idx: int, id: String) -> void:
	var g := Economy.sell_weapon(ps, id)
	if g <= 0:
		return
	_render(idx)
	_info.text = "ขาย %s ได้ %d เงิน" % [PlayerState.weapon_row(id).get("name", id), g]

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_close()

func _close() -> void:
	closed.emit()
	queue_free()
