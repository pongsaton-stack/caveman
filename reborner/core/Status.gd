# core/Status.gd — นิยามสถานะ 6 แบบ (GDD 3.11)
# ทุกสถานะต้องโจมตีระบบที่มีอยู่แล้ว ห้ามเป็นแค่ "ลด HP เฉยๆ"
class_name Status
extends RefCounted

const DURATION := 3          # เทิร์นของตัวที่ติด ไม่ใช่รอบรวม
const RESIST_K := 120.0      # โอกาสติด = ฐาน x (1 - DEF/(DEF+K)) — ใช้ DEF ที่มีอยู่ ไม่สร้างสเตตัสใหม่

const POISON   := "พิษ"
const BLEED    := "เลือดไหล"
const SLOWED   := "หน่วง"
const BOUND    := "ตรึง"
const SEALED   := "ผนึก"
const CONFUSED := "สับสน"

const ALL := [POISON, BLEED, SLOWED, BOUND, SEALED, CONFUSED]

const INFO := {
	POISON:   {"dot": 0.06, "note": "เสีย HP 6% maxHP ต่อเทิร์นของตัวเอง"},
	BLEED:    {"bleed": 0.25, "note": "เสีย HP 25% ของดาเมจที่รับล่าสุด"},
	SLOWED:   {"av_mult": 1.3, "note": "AV ถัดไป x1.3"},
	BOUND:    {"note": "ห้ามสลับตำแหน่ง ห้ามหนี"},
	SEALED:   {"note": "ใช้ได้เฉพาะท่าที่ไม่เสีย SP"},
	CONFUSED: {"self_hit": 0.35, "note": "35% โจมตีพวกเดียวกัน"},
}

## โอกาสติดจริง — DEF สูงต้านได้ดีกว่า ทำให้บิลด์สาย DEF มีเหตุผล
static func chance(base: float, target_def: int) -> float:
	return base * (1.0 - float(target_def) / (float(target_def) + RESIST_K))

static func dot_of(key: String) -> float:
	return float(INFO.get(key, {}).get("dot", 0.0))

static func bleed_of(key: String) -> float:
	return float(INFO.get(key, {}).get("bleed", 0.0))

static func av_mult_of(key: String) -> float:
	return float(INFO.get(key, {}).get("av_mult", 1.0))
