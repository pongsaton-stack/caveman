extends "res://tests/lab/flw_bt0.gd"
## ทุบ bt0 ไม้เบสบอล — ภาพ PixelLab ตามรายงานวิจัย (kwan 25 ต.ค. "ใช้ pixellab ปรับให้ตรงกับรายงาน ... สีหน้ามีอารมณ์มากกว่า flow")
## ง้างหลังไหล่ (pls_bat_0) → ง้างสุดไม้นอนหลัง (bat2_1) → ไม้ขึ้นหลังหัว (bat2_2) → ไม้ตั้งเหนือหัว ตะโกน (bat2_0) → กระทบลงเฉียง ตัวตั้งตรง (State BT_bat_impact)
## วิ่งเข้า pls_bat_run (run_bat) · ยืนหายใจ pls_bat_breath (idle_bat 0–1 วนสลับ) · ถอยด้วย pls_bat_hop (hop_bat2 · เฟรม 4 ขาซีดจาก clean() → ลอยใช้เฟรม 5) · ภาพแต่ละคลิปจัดวางคนละกรอบ → shift_x ดึงหมวกให้ตรงภาพยืน (วัดจากจุดกลางหมวก)

func keys() -> Dictionary: return {"ready": ["pls_bat_breath_0", "pls_bat_breath_1"], "run": ["pls_bat_run_0", "pls_bat_run_1", "pls_bat_run_2", "pls_bat_run_3", "pls_bat_run_4", "pls_bat_run_5", "pls_bat_run_6", "pls_bat_run_7"], "lift": "pls_bat_0", "wind": "pls_bat2_1", "whip": "pls_bat2_2", "mid": "pls_bat2_0",
	"hit": "pls_bat_imp_0", "follow": "pls_bat_imp_0", "crouch": "pls_bat_hop_2", "air": "pls_bat_hop_5", "fall": "pls_bat_hop_5", "land": "pls_bat_hop_1"}
func tips() -> Dictionary: return {"wind": Vector2(116, 38), "mid": Vector2(84, 28), "hit": Vector2(31, 98)}
const SHIFT := {"run": -2.0, "lift": -20.0, "wind": -17.0, "whip": -20.0, "mid": -12.0, "hit": -15.0, "follow": -15.0, "crouch": 3.0, "air": 2.0, "fall": 2.0, "land": 1.0}
func shift_x(pose: String) -> float: return SHIFT.get(pose, 0.0)
func src_name() -> String: return "ภาพ PixelLab"
func skinnable() -> bool: return true
