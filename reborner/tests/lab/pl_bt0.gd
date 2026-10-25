extends "res://tests/lab/flw_bt0.gd"
## ทุบ bt0 ไม้เบสบอล — ภาพ PixelLab (State BT_bat_stance + ท่า bt0_bat 10 เฟรม · 18 gen · kwan 25 ต.ค. "ทื่อมาก ลองเจน pixellab มาเทียบ")
## จังหวะ/เอฟเฟกต์/ปฏิกิริยาเดียวกับฉาก Flow ทุกอย่าง ต่างแค่ภาพ · PixelLab วาดเป็นหวดแนวนอนระดับอก (ไม่ใช่ฟาดลงจากบน) และเฟรมท้ายตัวหันเฉียงเข้ากล้อง

func keys() -> Dictionary: return {"ready": "pls_bat_idle_0", "lift": "pls_bat_0", "wind": "pls_bat_2", "whip": "pls_bat_6", "mid": "pls_bat_7",
	"hit": "pls_bat_8", "follow": "pls_bat_9", "back": "pls_bat_0"}
func tips() -> Dictionary: return {"wind": Vector2(116, 62), "mid": Vector2(35, 49), "hit": Vector2(31, 64)}
## ชุด pls_bat จัดวางคนละกรอบกับภาพยืน (State ผืน 96) → หมวกเลื่อนขวา 21 จุด · ดึงกลับให้ตัวอยู่ที่เดิม
func shift_x(pose: String) -> float: return 0.0 if pose == "ready" else -21.0
func src_name() -> String: return "ภาพ PixelLab"
