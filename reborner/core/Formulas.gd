# core/Formulas.gd — สูตรทั้งหมดของเกม อยู่ที่เดียว ไม่มี node ไม่มี UI ทดสอบได้เดี่ยวๆ
class_name Formulas
extends RefCounted

# ค่าคงที่ — ตรงกับ GDD หมวด 10
const MIT_K        := 100.0   # Mitigation = K / (K + DEF)
const AV_NUM       := 10000.0 # AV = AV_NUM / SPD
const WEAK_MULT    := 1.5
const RESIST_MULT  := 0.5
const PUSH_MULT    := 0.75    # ตีจุดอ่อน -> AV ถัดไปคูณค่านี้
const GLIM_BASE    := 0.032
const INSIGHT_MAX  := 40.0
const THREAT_SLOPE := 0.08
const THREAT_MIN   := 0.2
const THREAT_MAX   := 2.5
const SWAT_GAP     := 10      # tier <= prof - 10 -> ตบทิ้งบนแมพ
const INTERRUPT_PCT := 0.15   # ขัดจังหวะเมื่อดาเมจสะสมถึง % ของ maxHP
const SP_RESTORE   := 0.30

# ── สัปดาห์ 4: คอมโบ · เปิดท่าล่วงหน้า · ขัดจังหวะ (GDD 3.5 / 3.8) ──
const COMBO_LOYALTY := 3       # ความเชื่อใจขั้นต่ำที่ยิงคอมโบได้
const COMBO_SP      := 10      # SP ที่ทั้งคู่ต้องจ่าย
const COMBO_POWER   := 160.0
const COMBO_MULT    := 1.5
const COMBO_WEIGHT  := 1.4     # ทั้งคู่เสียน้ำหนักนี้
const TEL_CHANCE    := 0.6     # โอกาสเปิดท่าเมื่อเข้าคิวช่อง 2-4
const TEL_POWER     := 140.0   # พลังท่าเด่นที่เปิดไว้
const TEL_STATUS_BONUS := 1.5  # ท่าเด่นลงสถานะแรงกว่าปกติ
const INTERRUPT_AV  := 1.4     # ขัดสำเร็จ -> AV ศัตรู x ค่านี้
const AMBUSH_MULT   := 0.4     # ลอบตี: AV ฝ่ายที่ได้เปรียบ x ค่านี้ (ห้าม 0 — บทเรียน 11.17)

# ── ขั้น 4 สัปดาห์ 3: มอนร่วมทีม · LP · ความเชื่อใจ (GDD 3.6 / 5.4 / 9.3) ──
const COMPANION_HP_MULT := 1.6 # มอนร่วมทีมแข็งกว่าตัวป่าเล็กน้อย ไม่สเกลตามตัวเอก (GDD 5.1)
const LP_MAX        := 3       # LP 3 → 2 → 1 → หายถาวร
const LP_REGEN_RESTS := 3      # LP ฟื้น 1 ทุก 3 จุดพัก (GDD 9.3 "2-3" · 11.8 ห้ามฟื้นทุกจุดพัก)
const TRUST_BATTLES := 4       # ความเชื่อใจ +1 ทุก 4 ศึกที่อยู่ในทีม
const TRUST_CLEAN_COOLDOWN := 3 # +1 เมื่อจบศึกไม่ล้ม ได้ครั้งเดียวต่อ 3 ศึก
const TRUST_MAX     := 5       # rank 5 = วิวัฒนาการ (v2)

static func av(spd: float) -> float:
	return AV_NUM / maxf(spd, 1.0)

static func mitigation(def_val: float, ignore_def: float = 0.0) -> float:
	return MIT_K / (MIT_K + def_val * (1.0 - ignore_def))

static func threat(enemy_tier: float, prof: float) -> float:
	return clampf(1.0 + (enemy_tier - prof) * THREAT_SLOPE, THREAT_MIN, THREAT_MAX)

## ตบทิ้งบนแมพ — ไม่เข้าฉากต่อสู้ ไม่ได้ความชำนาญ/ความเข้าใจ
static func is_swat(enemy_tier: float, prof: float) -> bool:
	return enemy_tier <= prof - SWAT_GAP

## ความชำนาญที่ได้ต่อศึก — ห้ามใช้ ceil (GDD 4.1)
static func prof_gain(enemy_tier: float, prof: float) -> int:
	if is_swat(enemy_tier, prof):
		return 0
	var t := threat(enemy_tier, prof)
	if t <= 0.4:
		return 0
	return int(roundf(3.0 * t / (1.0 + prof / 40.0)))

## โอกาสประกายจากการสุ่ม
static func glimmer_chance(enemy_tier: float, prof: float, learned_ratio: float, luck: int) -> float:
	return GLIM_BASE * threat(enemy_tier, prof) * (1.0 - learned_ratio) * (1.0 + luck * 0.015)

## สูตรความเสียหาย — GDD 3.2
## elem: 1.5 จุดอ่อน / 1.0 ปกติ / 0.5 ต้านทาน / 0.0 ภูมิคุ้มกัน
static func damage(atk: float, power: float, def_val: float, elem: float,
		pos: float = 1.0, combo: float = 1.0, ignore_def: float = 0.0) -> int:
	var base := atk * power / 100.0
	var mit := mitigation(def_val, ignore_def)
	var variance := randf_range(0.95, 1.05)
	var d := base * mit * elem * pos * combo * variance
	return int(maxf(1.0 if elem > 0.0 else 0.0, roundf(d)))

# ── สเตตัสตัวเอก (GDD 4.1) ──
static func hero_atk(prof: int, weapon_base: int) -> int:
	return int(roundf(20 + prof * 1.6 + weapon_base))

static func hero_mag(magic_prof: int, staff_base: int) -> int:
	return int(roundf(20 + magic_prof * 1.6 + staff_base))

static func hero_hp(prof: int) -> int:
	return int(roundf(100 + prof * 1.4))

static func hero_sp(prof: int, magic_prof: int) -> int:
	return 34 + prof + magic_prof

static func hero_def(prof: int) -> int:
	return int(roundf(20 + prof * 0.5))

static func tech_slots(total_prof: int) -> int:
	return 4 + total_prof / 150
