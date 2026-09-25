# world/ShopScreen.gd — ร้านค้า (ช่อง S บนแผนที่) · ราคาและสต๊อกจาก data/items.csv
# สต๊อกจำกัดต่อภูมิภาค (GDD 9.2: "เพดานที่มาจากจำนวนของ ทะลุไม่ได้") · เติมเมื่อผ่าน checkpoint (ยังไม่มี)
class_name ShopScreen
extends CanvasLayer

signal closed

var ps: PlayerState
var items_rows: Array = []

var _root: Control
var _gold: Label
var _info: Label
var _menu: GridContainer

func setup(state: PlayerState, item_rows: Array) -> void:
	ps = state
	items_rows = item_rows

func _ready() -> void:
	layer = 10
	_root = UiKit.screen(self, "ร้านค้า — พ่อค้าเร่")
	_gold = UiKit.label("", 8, UiKit.C_TEXT)
	_gold.position = Vector2(4, 16)
	_root.add_child(_gold)
	var hint := UiKit.label("ของมีจำกัดต่อภูมิภาค · ยาเติมชีวิตคืน LP ได้ แต่ชุบมอนที่หายถาวรไม่ได้", 6, UiKit.C_MUTED)
	hint.position = Vector2(4, 30)
	_root.add_child(hint)
	_info = UiKit.label("", 7, UiKit.C_GOLD)
	_info.position = Vector2(4, 132)
	_info.size = Vector2(376, 10)
	_info.clip_text = true
	_root.add_child(_info)
	_menu = GridContainer.new()
	_menu.columns = 1
	_menu.position = Vector2(4, 46)
	_menu.add_theme_constant_override("v_separation", 3)
	_root.add_child(_menu)
	_render(0)

func _render(focus_index: int) -> void:
	for c in _menu.get_children():
		_menu.remove_child(c)
		c.queue_free()
	_gold.text = "เงิน %d" % ps.gold
	var buttons: Array[Button] = []
	for r in items_rows:
		var id := str(r["item_id"])
		var left := int(ps.shop_stock.get(id, 0))
		var price := int(r["price"])
		var btn := UiKit.button("ซื้อ %s  %dg  · ร้านเหลือ %d · มีอยู่ %d" % [r["name"], price, left, ps.item_count(id)], 376)
		btn.disabled = left <= 0 or ps.gold < price
		btn.pressed.connect(_buy.bind(r, buttons.size()))
		btn.focus_entered.connect(func(): _info.text = str(r["note"]).split("·")[0].strip_edges())
		_menu.add_child(btn)
		buttons.append(btn)
	var out := UiKit.button("ออกจากร้าน", 376)
	out.pressed.connect(_close)
	_menu.add_child(out)
	buttons.append(out)
	var idx := clampi(focus_index, 0, buttons.size() - 1)
	while idx < buttons.size() - 1 and buttons[idx].disabled:
		idx += 1
	buttons[idx].grab_focus()

func _buy(r: Dictionary, idx: int) -> void:
	var id := str(r["item_id"])
	var price := int(r["price"])
	if int(ps.shop_stock.get(id, 0)) <= 0 or ps.gold < price:
		return
	ps.gold -= price
	ps.shop_stock[id] = int(ps.shop_stock[id]) - 1
	ps.add_item(id)
	_info.text = "ซื้อ %s แล้ว" % r["name"]
	_render(idx)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_close()

func _close() -> void:
	closed.emit()
	queue_free()
