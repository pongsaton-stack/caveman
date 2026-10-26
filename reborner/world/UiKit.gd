# world/UiKit.gd — ชิ้นส่วน UI ที่หน้าจอเมนู/ร้านค้าใช้ร่วมกัน (พาเลตต์เดียวกับแผนที่องก์ 1)
class_name UiKit
extends RefCounted

const C_BG := Color("15130f")
const C_PANEL := Color("1d1a15")
const C_LINE := Color("3a3329")
const C_TEXT := Color("e8d9b5")
const C_MUTED := Color("a89b80")
const C_GOLD := Color("c9a24a")
const C_GOOD := Color("6b7d4a")
const C_BAD := Color("b5553f")

static func label(text: String, size: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	return l

static func box(fill: Color, border: Color) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fill
	s.border_color = border
	s.set_border_width_all(1)
	s.set_corner_radius_all(2)
	s.content_margin_left = 4
	s.content_margin_right = 4
	s.content_margin_top = 0
	s.content_margin_bottom = 0
	return s

static func button(text: String, min_w: float = 120.0) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(min_w, 12)
	btn.clip_text = true
	btn.focus_mode = Control.FOCUS_ALL
	btn.add_theme_font_size_override("font_size", 7)
	btn.add_theme_color_override("font_color", C_TEXT)
	btn.add_theme_color_override("font_focus_color", C_BG)
	btn.add_theme_color_override("font_hover_color", C_BG)
	btn.add_theme_color_override("font_pressed_color", C_BG)
	btn.add_theme_color_override("font_disabled_color", C_MUTED)
	btn.add_theme_stylebox_override("normal", box(C_PANEL, C_LINE))
	btn.add_theme_stylebox_override("hover", box(C_GOLD, C_GOLD))
	btn.add_theme_stylebox_override("focus", box(C_GOLD, C_TEXT))
	btn.add_theme_stylebox_override("pressed", box(C_TEXT, C_TEXT))
	btn.add_theme_stylebox_override("disabled", box(C_BG, C_LINE))
	return btn

## พื้นหลังเต็มจอ + หัวข้อ — คืน root ให้ใส่ของต่อ
static func screen(layer_node: CanvasLayer, title: String) -> Control:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer_node.add_child(root)
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(bg)
	var head := label(title, 8, C_GOLD)
	head.position = Vector2(4, 1)
	root.add_child(head)
	return root

## LP เป็นจุด ●●○ — อ่านเร็วกว่าตัวเลข
static func lp_dots(lp: int) -> String:
	var s := ""
	for i in Formulas.LP_MAX:
		s += "●" if i < lp else "○"
	return s
