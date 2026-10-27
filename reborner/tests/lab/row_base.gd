extends "res://tests/lab/blc_bl0.gd"
## ฐานท่าตีหลายตัว (กวาด bl3 · ทะลวงแนว bl10 · มีดบินวกกลับ bl11): มอนชนิดเดียวกัน 3 ตัวเรียงแถว · บอสยืนตัวเดียว
## cxs[0] = ตัวใกล้ Rion ที่สุด (ขวาสุด) · ตัวอื่นไล่ไปทางซ้าย · ใช้เครื่องวิ่ง/กระโดดถอยของ blc_bl0 ต่อได้

var mons: Array[Sprite2D] = []
var cxs: Array[float] = []   # กลางตัวมอนแต่ละตัว

func _count() -> int:
	return 1 if foe.begins_with("B") else 3

const ROOM := 65.0   # ระยะว่างขั้นต่ำระหว่างขอบมอนตัวใกล้สุดกับกลางตัว Rion ตอนยืน (kwan 27 ต.ค. "มอนอยู่ใกล้ตัวเอกไป")

## วางแถว: ตัวไกลสุดที่ left_cx · ระยะห่าง gap × ความกว้างมอน (ซ้อนกันเล็กน้อย) · เป้าเดียว = ที่ single_cx (ไม่ระบุ = MX)
## แถวล้นเข้าหา Rion → บีบระยะห่าง (ไม่ต่ำกว่า 0.45 เท่าตัว) ก่อน แล้วค่อยเลื่อนทั้งแถวไปทางซ้าย
func setup_row(left_cx: float, gap := 0.62, single_cx := -1.0) -> void:
	var sp := roundf(mw * gap)
	var c0 := left_cx + sp * (_count() - 1) if _count() > 1 else (single_cx if single_cx > 0 else float(MX))
	var lim := start + 60.0 - ROOM - mw * 0.5   # กลางตัวมอนตัวใกล้สุดห้ามเกินนี้
	if _count() > 1 and c0 > lim:
		sp = maxf(roundf(mw * 0.45), floorf((lim - left_cx) / (_count() - 1)))
		c0 = minf(left_cx + sp * (_count() - 1), lim)
	elif c0 > lim:
		c0 = lim
	place_monster(int(c0))
	cxs.clear()
	for i in _count():
		cxs.append(c0 - sp * i)
	mons.clear()
	mons.append(mon)
	for i in range(1, _count()):
		var s := Sprite2D.new()
		s.centered = false
		s.material = fx_mat()
		s.z_index = 1
		add_child(s)
		mons.append(s)

## ภาพมอนตัวที่ i (แบบ show_mon) · dx = เลื่อน · amt = วาบขาว · lift = ยกจากพื้น · sy = ยุบ/ยืดรอบเท้า
func _show(i: int, key: String, dx: float, amt: float, lift := 0.0, sy := 1.0) -> void:
	var s: Sprite2D = mons[i]
	var mt := tx(key)
	s.visible = true
	s.texture = mt
	s.offset = Vector2(-mt.get_width() / 2.0, -mt.get_height())
	s.position = Vector2(roundf(cxs[i] - mw / 2.0) + roundf(dx) + roundf((mw - mt.get_width()) / 2.0) + mt.get_width() / 2.0, G - roundf(lift))
	s.scale = Vector2(1.0, sy)
	s.material.set_shader_parameter("tint", Color.WHITE)
	s.material.set_shader_parameter("amount", amt)
