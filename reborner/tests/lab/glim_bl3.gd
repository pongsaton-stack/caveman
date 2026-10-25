extends "res://tests/lab/blc_bl0.gd"
## ★ การเกิดประกาย: ฟัน → bl3 · ยังไม่มีภาพท่านี้ → ร่างจำลองจากภาพฟัน + รอยฟันเสี้ยวแนวนอน (ขอบเขตทั้งแถว)
## วิ่งเข้าง้างฟันธรรมดา → กลางง้างเวลาหยุด 34 เฟรม (หลอดไฟติด · เห็นท่าใหม่ล่วงหน้า · แถบชื่อ) → ใช้ท่าใหม่แทนทันที

func mv() -> Dictionary:
	var m := super.mv()
	m.merge({"glim": true, "to": "bl3", "P": 34, "sfx": "กวาด!!", "what": "★ ประกาย! ฟัน → กวาด", "FZ": 30, "generic": true, "ghost": ["pls_atk_bl_4", "pls_atk_bl_5", "pls_atk_bl_6"]}, true)
	return m
