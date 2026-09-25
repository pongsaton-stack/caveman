# core/Ai.gd — การตัดสินใจของตัวจำลอง แยกออกจาก Battle โดยตั้งใจ
#
# ⚠️ GDD บทเรียน 11.19: AI นี้เล่นแย่กว่าคนจริงมาก (ทดสอบแล้วต่างกันถึง 51 จุด)
#    ตัวเลขที่ได้จากมันคือ "ขอบล่าง" ไม่ใช่ความยากจริง
#    อย่าปรับสมดุลเกมให้ AI ชนะ — ใช้มันเปรียบเทียบระหว่างเวอร์ชันเท่านั้น
class_name Ai
extends RefCounted

## ตั้งรับควรเป็นเครื่องมือตามสถานการณ์ ไม่ใช่ท่าที่กดตลอด (GDD บทเรียน 11.3)
## เงื่อนไขแคบไว้ก่อน — บทเรียน 11.18 บอกว่าเงื่อนไขกว้างเกินทำให้ AI กลายเป็นบอตซัพพอร์ต
static func should_guard(a: Actor, _party: Array, _enemies: Array) -> bool:
	if a.windup:
		return false
	# HP วิกฤต — ตั้งรับซื้อเวลาและสะสม Insight
	if float(a.hp) / float(a.max_hp) < 0.3 and randf() < 0.45:
		return true
	# ติดสถานะหนัก 2 อย่างขึ้นไป — ตั้งรับสลัดออกได้ 1 เทิร์น
	if a.statuses.size() >= 2 and randf() < 0.4:
		return true
	return false

## คอมโบ — ยิงเสมอถ้าเป้าหมายกำลังเปิดท่า (แข่งขัดจังหวะ) ไม่งั้น 60%
static func should_combo(target: Actor) -> bool:
	if not target.telegraph.is_empty():
		return true
	return randf() < 0.6

## เลือกท่าที่ให้ดาเมจต่อน้ำหนักแอ็กชันสูงสุด
## หารด้วย weight เพราะในระบบ AV ท่าที่หนักกว่าคือท่าที่ "ยืมเวลา" มาใช้
static func choose(attacker: Actor, target: Actor, pool: Array[Tech], foe_count: int = 1) -> Tech:
	var best: Tech = null
	var best_score := -1.0
	for t in pool:
		if not t.is_attack():
			continue
		if t.sp > attacker.sp and t.sp > 0:
			continue
		var elem: float = target.elem_mult(t.element)
		var pos := 1.0
		if target.row == "หลัง" and not (t.ignore_pos or t.free_row):
			pos = 0.7
		var d: float = attacker.atk * t.power / 100.0 \
			* Formulas.mitigation(target.def_val, t.ignore_def) * elem * pos * t.hits
		# ท่า AoE คุ้มเมื่อมีเป้าหมายหลายตัว
		if t.scope == "all" or t.scope == "row" or t.scope == "column":
			d *= float(foe_count)
		var score := d / maxf(t.weight, 0.1)
		if score > best_score:
			best_score = score
			best = t
	return best
