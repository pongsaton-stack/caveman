# core/Battle.gd
# ★★ ลูปเทิร์นเดียวของทั้งโปรเจกต์ ★★
# ทั้งเกมจริง ตัวทดสอบ และตัวจำลอง ต้องเรียกคลาสนี้เท่านั้น
# ห้ามเขียนลูปเทิร์นที่อื่นเด็ดขาด (GDD บทเรียน 11.15)
class_name Battle
extends RefCounted

const SEIZE_SCHOOL := "ยึด"   # สายของท่าที่ยึดจากมอน (GDD 5.2) — ไม่อยู่ในต้นไม้ท่า ไม่ประกาย

var actors: Array[Actor] = []
var techs: TechDb
var verbose := false
var max_rounds := 300
var allow_glimmer := true
var ambush := ""   # "" ปกติ · "ally" ลอบตีสำเร็จ · "foe" ถูกลอบตี (GDD 3.10)

# ผลลัพธ์
var rounds := 0
var time_elapsed := 0.0   # เวลาจริงในหน่วย AV — ตัวชี้วัดที่ถูกในระบบนี้
var won := false
var dealt := 0
var taken := 0
var downs := 0
var kills := 0
var hits_on_kill := 0
var glimmers := 0
var glimmers_from_fill := 0   # ประกายที่มาจาก Insight เต็ม (ไม่ใช่การสุ่ม)
var fills := 0                # จำนวนครั้งที่ Insight เต็ม
var glimmer_log: Array[String] = []
var counter_glimmers := 0     # ประกายสวนกลับ (ตั้งรับแล้วโดนตี · ไม่นับใน glimmers เพื่อให้อัตราประกายต่อการใช้ท่าเทียบกับของเดิมได้)
var read_glimmers := 0        # ประกายหลบ — เริ่มอ่านทางท่าเด่นมอนใหม่
var dodges := 0               # หลบท่าเด่นได้ด้วยการอ่านทาง
var tech_uses := 0
var statuses_applied := 0
var guards := 0
var status_deaths := 0
var combos := 0
var telegraphs := 0
var interrupts := 0
# ความเข้าใจท่าเด่นของศัตรู (GDD 5.2) — นับต่อสายพันธุ์ · บันทึกอย่างเดียว ไม่แตะการสุ่ม
var understanding := {}          # monster_id → แต้ม
var _understand_need := {}       # monster_id → แต้มที่ต้องได้
var _understand_boss := {}       # monster_id → true ถ้าเป็นบอส
var _understand_viewers := {}    # monster_id → Array[Actor] ผู้ที่เห็นท่า (บอสต้องมีคนเห็นยืนอยู่ตอนจบ)

func _log(s: String) -> void:
	if verbose: print(s)
	if capture: log_lines.append(s)

func allies() -> Array:
	return actors.filter(func(a): return a.side == "ally" and not a.down)

func foes() -> Array:
	return actors.filter(func(a): return a.side == "foe" and not a.down)

func hero() -> Actor:
	for a in actors:
		if a.is_hero: return a
	return null

## ท่าที่ตัวละครตัวนี้ใช้ได้ตอนนี้
func usable(a: Actor) -> Array[Tech]:
	var out: Array[Tech] = []
	if techs == null: return out
	for n in a.learned:
		var t: Tech = techs.get_tech(n)
		if t != null: out.append(t)
	for n in a.seized:   # ท่าที่ยึดมา (GDD 5.2) — อยู่ใน TechDb แต่ไม่อยู่ในต้นไม้ท่า
		var t: Tech = techs.get_tech(n)
		if t != null: out.append(t)
	return out

## ดูคิวล่วงหน้า n ช่องโดยไม่แตะค่าจริง (UI แถบคิวก็ใช้ฟังก์ชันนี้)
func preview(n: int) -> Array:
	var sim := []
	for a in actors:
		if not a.down:
			sim.append({"a": a, "av": a.av})
	var out := []
	for _i in n:
		if sim.is_empty():
			break
		sim.sort_custom(func(x, y): return x["av"] < y["av"])
		var t: Dictionary = sim[0]
		out.append(t["a"])
		t["av"] += Formulas.av(t["a"].spd)
	return out

# ── Insight ────────────────────────────────────────────────
## สะสม Insight ให้ตัวเอก — ทุกแหล่งคือสถานการณ์ที่กำลังแย่
func _gain_insight(a: Actor, amount: float, why: String) -> void:
	if a == null or a.down or not a.is_hero: return
	if a.insight_lock > 0: return
	if Insight.FIRST_GLIMMER_SURE and a.first_glimmer_pending:
		amount = maxf(amount, Insight.THRESHOLD - a.insight)
		why += " · ประกายครั้งแรก"
	a.insight += amount
	if a.insight >= Insight.THRESHOLD:
		fills += 1
		a.insight = Insight.THRESHOLD + (a.insight - Insight.THRESHOLD) * Insight.CARRY
		_log("    ◆ Insight เต็ม (%s) — ท่าถัดไปประกายแน่นอน" % why)

# ── ลูปเทิร์น (แตกเป็นขั้น) ─────────────────────────────────
# run() = begin() + วนลูป is_over() → next_turn() → auto_act()
# หน้าจอต่อสู้ใช้ขั้นเดียวกันทุกตัว ต่างแค่เทิร์นตัวเอกเรียก player_act() แทน auto_act()
# ห้ามเขียนลูปเทิร์นที่อื่น (GDD 11.15) — Sim กับหน้าจอต่อสู้ต้องเดินผ่านโค้ดชุดนี้เท่านั้น

var current: Actor = null   # ตัวที่ถึงคิวอยู่ตอนนี้ (หลัง next_turn)
var capture := false        # เก็บบรรทัดบันทึกไว้ให้ UI อ่าน
## เหตุการณ์ให้หน้าจอวาดเอฟเฟกต์ (เก็บเฉพาะตอน capture · ไม่แตะการสุ่ม → ผลศึกเหมือนเดิมทุกไบต์)
## {src, tgt, tech, school, dmg, weak, glimmer, dot}
var events: Array = []
var _fx_glimmer := false    # ท่าที่กำลังตีเป็นท่าประกายไหม (คอมโบก็ส่ง bonus > 1 จึงแยกธงไว้)
var log_lines: Array[String] = []

func run() -> Dictionary:
	begin()
	while not is_over():
		var cur := next_turn()
		if cur == null:
			continue
		auto_act(cur)
	return _result()

## เตรียมศึก — ตั้ง AV เริ่มต้นและผลของการลอบตี
func begin() -> void:
	for a in actors:
		a.reset_av()
	# ลอบตี — ฝ่ายที่ได้เปรียบเริ่มด้วย AV x0.4 (ได้เปรียบ แต่ไม่ใช่คำพิพากษา)
	if ambush == "ally" or ambush == "foe":
		for a in actors:
			if a.side == ambush:
				a.av *= Formulas.AMBUSH_MULT
		_log("  ◆ %s" % ("ลอบตีสำเร็จ — AV ฝ่ายเรา x0.4" if ambush == "ally" else "ถูกลอบตี — AV ศัตรู x0.4"))

## จบศึกหรือยัง — ตั้งค่า won ตอนจบ
func is_over() -> bool:
	if rounds >= max_rounds:
		return true
	if foes().is_empty():
		won = true; _log("  → ชนะใน %d รอบ" % rounds); return true
	var h := hero()
	if h != null and h.down:
		won = false; _log("  → แพ้ (ตัวเอกล้ม)"); return true
	if allies().is_empty():
		won = false; _log("  → แพ้"); return true
	return false

## เดินเวลาไปถึงตัวถัดไป คืนตัวที่ต้องทำแอ็กชัน
## คืน null ถ้าเทิร์นนี้ถูกข้าม (ล้มจากสถานะ / ไม่มีเป้าหมาย) — ให้เรียก is_over() แล้วเดินต่อ
func next_turn() -> Actor:
	current = null
	var h := hero()
	var alive := actors.filter(func(a): return not a.down)
	var min_av: float = alive.map(func(a): return a.av).min()
	time_elapsed += min_av
	for a in alive:
		a.av -= min_av
	alive.sort_custom(func(x, y): return x.av < y.av)
	var cur: Actor = alive[0]
	rounds += 1

	# ศัตรูที่กำลังจะถึงคิว (ช่อง 2-4) มีโอกาสเปิดเผยท่าเด่น
	_set_telegraphs()

	# นับถอยหลังล็อก Insight ตอนถึงเทิร์นของตัวเอก
	if cur.is_hero and cur.insight_lock > 0:
		cur.insight_lock -= 1

	# อยู่ในอันตราย = สะสม Insight (นับที่เทิร์นของศัตรู)
	if cur.side == "foe" and h != null:
		# บอสนับจากธง is_boss — ราชาหนอนเถ้า tier 20 ก็เป็นบอส (บทเรียน 11.28)
		if cur.is_boss or cur.tier >= Insight.BOSS_TIER:
			_gain_insight(h, Insight.FIGHTING_BOSS, "สู้บอส")
		elif cur.tier >= h.tier:
			_gain_insight(h, Insight.STRONGER_FOE, "ศัตรูแข็งกว่า")

	# บัฟ (เกราะแข็ง) หมดอายุตามเทิร์นของตัวเอง — ไม่ใช้การสุ่ม
	for k in cur.tick_buffs():
		_log("    %s หมดบัฟ %s" % [cur.name, k])
	# สถานะทำงานตอนเริ่มเทิร์นของตัวที่ติด ไม่ใช่ทุกรอบ
	if _tick_status_damage(cur):
		return null
	var pool := foes() if cur.side == "ally" else allies()
	if pool.is_empty():
		return null
	current = cur
	return cur

## ให้ AI ทำแอ็กชันแทน (ศัตรู มอนร่วมทีม และตัวเอกใน Sim)
func auto_act(cur: Actor) -> void:
	var pool := foes() if cur.side == "ally" else allies()
	var target: Actor = _pick_target(cur, pool)
	_take_turn(cur, target)

## ท่าที่ตัวเอกกดได้ตอนนี้ — ผนึกเหลือเฉพาะท่าที่ไม่เสีย SP · SP ไม่พอก็กดไม่ได้
func hero_options(cur: Actor) -> Array[Tech]:
	var pool := _hero_pool(cur)
	var out: Array[Tech] = []
	for t in pool:
		if t.is_usable() and (t.sp == 0 or t.sp <= cur.sp) and not (t.once and cur.once_used.has(t.name)):
			out.append(t)
	return out

## คู่คอมโบที่ใช้ได้ตอนนี้ (null = ยิงคอมโบไม่ได้)
func combo_partner_for(cur: Actor) -> Actor:
	if cur.has_status(Status.SEALED):
		return null
	return _combo_partner(cur)

## ผู้เล่นสั่งตัวเอก — action = {"kind": "tech"|"guard"|"combo"|"watch", "tech": Tech, "target": Actor}
## กฎเดียวกับ AI ทุกข้อ ต่างแค่ใครเป็นคนเลือก
func player_act(action: Dictionary) -> void:
	var cur := current
	if cur == null or not cur.is_hero:
		return
	var kind := str(action.get("kind", "tech"))
	if kind == "guard":
		cur.guarding = false
		_do_guard(cur)
		return
	if kind == "watch":
		cur.guarding = false
		_do_watch(cur, action.get("target"))
		return
	var target: Actor = action.get("target")
	if target == null or target.down:
		var pool := foes()
		if pool.is_empty():
			return
		target = _pick_target(cur, pool)
	cur.guarding = false
	target = _confuse_retarget(cur, target)
	if kind == "combo":
		var partner := combo_partner_for(cur)
		if partner != null:
			var tech0: Tech = action.get("tech")
			_do_combo(cur, partner, target, tech0.element if tech0 != null else "ฟัน")
			return
	_execute(cur, target, action.get("tech"))

## ฝ่ายเราเล็งศัตรูที่เปิดท่าไว้ก่อน (แข่งขัดจังหวะ) ไม่งั้นเล็ง HP ต่ำสุด
func _pick_target(cur: Actor, pool: Array) -> Actor:
	if cur.side == "ally":
		var threat_tgt: Actor = null
		for p in pool:
			if not p.telegraph.is_empty():
				var need: float = p.max_hp * Formulas.INTERRUPT_PCT
				if float(p.telegraph["dmg"]) < need:
					if threat_tgt == null or p.hp < threat_tgt.hp:
						threat_tgt = p
		if threat_tgt != null:
			return threat_tgt
	var target: Actor = pool[0]
	for p in pool:
		if p.hp < target.hp: target = p
	return target

# ── เปิดท่าล่วงหน้า + ขัดจังหวะ (GDD 3.8) ────────────────────
func _set_telegraphs() -> void:
	var q := preview(4)
	# ข้ามช่องแรก — ตัวที่กำลังจะทำอยู่แล้วเปิดท่าไม่ทัน (บทเรียน 11.14)
	for i in range(1, q.size()):
		var a: Actor = q[i]
		if a.side == "foe" and a.telegraph.is_empty() and not _sig_spent(a) and randf() < Formulas.TEL_CHANCE:
			a.telegraph = {"name": a.signature, "dmg": 0}
			telegraphs += 1
			_log("    ▼ %s กำลังจะใช้ %s" % [a.name, a.signature])

## คืน true ถ้าถูกขัดจังหวะ (ข้ามเทิร์น)
func _check_interrupt(f: Actor) -> bool:
	if f.telegraph.is_empty():
		return false
	var need: float = f.max_hp * Formulas.INTERRUPT_PCT
	if float(f.telegraph["dmg"]) >= need:
		interrupts += 1
		_log("  ✂ ขัดจังหวะสำเร็จ! %s เสีย %d/%d → ยกเลิก %s · AV x%.1f"
			% [f.name, int(f.telegraph["dmg"]), int(need), f.telegraph["name"], Formulas.INTERRUPT_AV])
		f.telegraph = {}
		f.av += Formulas.av(f.spd) * Formulas.INTERRUPT_AV
		return true
	return false

# ── คอมโบ (GDD 3.5) ─────────────────────────────────────────
## คู่คอมโบ = ตัวที่อยู่ติดตัวเอกในคิว ต้องเป็นมอนร่วมทีม ไม่มีศัตรูคั่น
func _combo_partner(h: Actor) -> Actor:
	var q := preview(2)
	if q.size() < 2: return null
	var p: Actor = q[1]
	if p.side != "ally" or p.is_hero: return null
	if p.loyalty < Formulas.COMBO_LOYALTY: return null
	if h.sp < Formulas.COMBO_SP or p.sp < Formulas.COMBO_SP: return null
	return p

func _do_combo(h: Actor, p: Actor, target: Actor, element: String) -> void:
	combos += 1
	h.sp -= Formulas.COMBO_SP
	p.sp -= Formulas.COMBO_SP
	var t := Tech.new()
	t.id = "combo"
	t.name = "คอมโบ %s+%s" % [h.name, p.name]
	t.power = Formulas.COMBO_POWER
	t.weight = Formulas.COMBO_WEIGHT
	t.element = element
	t.scope = "single"
	_log("  ◆ คอมโบ! %s + %s" % [h.name, p.name])
	_strike(h, target, t, Formulas.COMBO_MULT)
	h.av += Formulas.av(h.spd) * Formulas.COMBO_WEIGHT
	p.av += Formulas.av(p.spd) * Formulas.COMBO_WEIGHT

## คืน true ถ้าตัวนั้นล้มจากสถานะ (ข้ามเทิร์น)
func _tick_status_damage(a: Actor) -> bool:
	if a.statuses.is_empty():
		return false
	if a.has_status(Status.POISON):
		var d := int(round(float(a.max_hp) * Status.dot_of(Status.POISON)))
		a.hp = maxi(0, a.hp - d)
		_log("    %s เสีย %d จากพิษ" % [a.name, d])
		if capture: events.append({"tgt": a, "dmg": d, "dot": "พิษ"})
	if a.has_status(Status.BLEED) and a.last_hit > 0:
		var d := int(round(float(a.last_hit) * Status.bleed_of(Status.BLEED)))
		a.hp = maxi(0, a.hp - d)
		_log("    %s เสีย %d จากเลือดไหล" % [a.name, d])
		if capture: events.append({"tgt": a, "dmg": d, "dot": "เลือดไหล"})
	for k in a.tick_statuses(1):
		_log("    %s หายจาก%s" % [a.name, k])
	if a.hp <= 0:
		a.down = true
		status_deaths += 1
		if a.side == "foe":
			kills += 1
		else:
			downs += 1
			if not a.is_hero:
				_gain_insight(hero(), Insight.ALLY_DOWN, "เพื่อนล้ม")
		_log("    %s ล้มจากสถานะ" % a.name)
		return true
	return false

func _apply_status(tgt: Actor, key: String, base: float) -> void:
	if tgt.down or key == "": return
	if randf() > Status.chance(base, tgt.def_val):
		_log("    %s ต้านทาน%sไว้ได้" % [tgt.name, key])
		return
	tgt.add_status(key)
	statuses_applied += 1
	_log("    %s ติด%s %d เทิร์น" % [tgt.name, key, Status.DURATION])
	if tgt.is_hero:
		_gain_insight(tgt, Insight.GOT_STATUS, "ติดสถานะ")

## จับตา — เสียเทิร์นจ้องท่าเด่นของศัตรู ได้ความเข้าใจ +2 ให้ทีม (GDD 5.2)
func _do_watch(a: Actor, target: Actor) -> void:
	if target == null or target.down or target.side != "foe":
		var pool := foes()
		if pool.is_empty():
			return
		target = pool[0]
	_add_understanding(target, a, Formulas.WATCH_POINTS)
	a.av += Formulas.av(a.spd) * Formulas.WATCH_WEIGHT
	_log("  รอบ %2d  %s จับตา %s — อ่านท่า %s (%d/%d)" % [rounds, a.name, target.name, target.signature,
		understanding[target.id], _understand_need[target.id]])

## ความเข้าใจตอนนี้ของสายพันธุ์นี้ — [แต้ม, ที่ต้องได้]
func understanding_of(f: Actor) -> Array[int]:
	var out: Array[int] = [int(understanding.get(f.id, 0)), maxi(1, f.comprehension)]
	return out

## ตั้งรับ — 4 หน้าที่ในแอ็กชันเดียว แต่เสมอตัวทางเทมโป (GDD 3.3)
func _do_guard(a: Actor) -> void:
	a.guarding = true
	a.windup = true
	a.counter_used = false
	guards += 1
	for k in a.tick_statuses(1):
		_log("    ตั้งรับสลัด%sออกได้" % k)
	a.av += Formulas.av(a.spd) * 0.5
	_log("  รอบ %2d  %s ตั้งรับ — ลดดาเมจ 50%% · ท่าถัดไปเบาลงครึ่ง" % [rounds, a.name])

func _take_turn(cur: Actor, target: Actor) -> void:
	cur.guarding = false

	# ศัตรูที่เปิดท่าไว้ — ถ้าโดนตีถึงเกณฑ์ก่อนถึงคิว ท่าถูกยกเลิก
	if cur.side == "foe" and _check_interrupt(cur):
		return

	target = _confuse_retarget(cur, target)

	var tech: Tech = null
	if cur.is_hero and techs != null:
		var pool := _hero_pool(cur)
		var insight_full := cur.insight >= Insight.THRESHOLD
		# Insight เต็มแล้วห้ามตั้งรับ — ต้องยิงท่าออกไปเพื่อให้ประกายเกิด
		if not insight_full and Ai.should_guard(cur, allies(), foes()):
			_do_guard(cur)
			return
		# ท่าเสริมตัวเอง (ท่ายึด เช่น เกราะแข็ง) — Insight เต็มแล้วไม่ใช้ เพราะท่าเสริมไม่ประกาย
		var buff := Ai.choose_buff(cur, pool, _attack_threats(cur)) if not insight_full else null
		if buff != null:
			_execute(cur, cur, buff)
			return
		tech = Ai.choose(cur, target, pool, foes().size())
		# คอมโบ — Insight เต็มแล้วไม่ยิงคอมโบ เพราะคอมโบไม่ประกาย
		if not insight_full and not cur.has_status(Status.SEALED):
			var partner := _combo_partner(cur)
			if partner != null and Ai.should_combo(target):
				var el := tech.element if tech != null else "ฟัน"
				_do_combo(cur, partner, target, el)
				return
	_execute(cur, target, tech)

## สับสน — มีโอกาสตีพวกเดียวกัน
func _confuse_retarget(cur: Actor, target: Actor) -> Actor:
	if cur.has_status(Status.CONFUSED) and randf() < 0.35:
		var own := allies() if cur.side == "ally" else foes()
		own = own.filter(func(a): return a != cur)
		if not own.is_empty():
			target = own[randi() % own.size()]
			_log("    %s สับสน — ตีพวกเดียวกัน" % cur.name)
	return target

## ท่าที่ตัวเอกมีสิทธิ์ใช้ตอนนี้ — ผนึกเหลือเฉพาะท่าไม่เสีย SP
func _hero_pool(cur: Actor) -> Array[Tech]:
	# ผนึก — ใช้ได้เฉพาะท่าที่ไม่เสีย SP
	var pool := usable(cur).filter(func(t): return not (t.once and cur.once_used.has(t.name)))
	if cur.has_status(Status.SEALED):
		var free_pool := pool.filter(func(t): return t.sp == 0)
		# ถ้าผนึกจนไม่เหลือท่าเลย ต้องเหลือท่ารากไว้เสมอ
		# ไม่งั้น Ai.choose คืน null แล้วตกไปใช้ท่าพื้นฐานซึ่งไม่โรลประกาย
		if not free_pool.is_empty():
			pool = free_pool
	return pool

## ลงมือจริง — ท่าเด่นที่เปิดไว้ · ประกาย · SP · ดาเมจ · AV (AI และผู้เล่นใช้ร่วมกัน)
func _execute(cur: Actor, target: Actor, tech: Tech) -> void:
	if tech == null:
		tech = _basic_tech(cur)

	# ศัตรูที่เปิดท่าไว้แล้วรอดมาถึงคิว — ใช้ท่าเด่นจริง ห้ามสุ่มใหม่
	# (ไม่งั้น UI โกหกผู้เล่น — GDD 3.8)
	if cur.side == "foe" and not cur.telegraph.is_empty():
		tech = _signature_tech(cur)
		cur.telegraph = {}

	# ── ประกาย (GDD 4.3) ──
	# สองทาง: Insight เต็ม = แน่นอน · ไม่งั้นโรลตามโอกาส
	var free := false
	if allow_glimmer and cur.is_hero and techs != null and tech.is_attack() and tech.school != SEIZE_SCHOOL:
		tech_uses += 1
		if target.tier > cur.tier:
			_gain_insight(cur, Insight.TECH_ON_STRONG, "ใช้ท่ากับศัตรูแข็งกว่า")
		var guaranteed := cur.insight >= Insight.THRESHOLD
		var learned_ratio: float = float(cur.learned.size()) / maxf(float(_school_size(cur)), 1.0)
		var p := Formulas.glimmer_chance(target.tier, cur.tier, learned_ratio, cur.luck)
		if guaranteed or randf() < p:
			var g: Tech = techs.roll_glimmer(cur.learned, cur.school, cur.tier, tech, cur.steer_branch)
			if g != null:
				glimmers += 1
				_learn_glimmer(cur, g, guaranteed, p, "")
				tech = g
				free = true
			elif guaranteed:
				# ไม่มีท่าให้เรียนแล้ว — ห้ามทิ้ง Insight เปล่า (GDD 4.3 กฎกันความหงุดหงิด)
				cur.insight = 0.0
				cur.tier += 2
				_log("    Insight เต็มแต่ไม่มีท่าให้เรียน → แปลงเป็นโบนัสความชำนาญ +2")

	if not free and tech.sp > 0:
		cur.sp -= tech.sp

	if tech.once:
		cur.once_used.append(tech.name)
	if tech.effect == "def_up":
		cur.apply_def_up(tech.effect_value, tech.effect_turns)
		_log("  รอบ %2d  %s ใช้ %s — DEF +%d%% %d เทิร์น (%d)" % [rounds, cur.name, tech.name,
			int(round(tech.effect_value * 100.0)), tech.effect_turns, cur.def_val])
		if capture:
			events.append({"src": cur, "tgt": cur, "tech": tech.name, "school": tech.school, "dmg": 0,
				"weak": false, "glimmer": false, "buff": "DEF+%d%%" % int(round(tech.effect_value * 100.0))})
	# ท่าเด่นที่ไม่ใช่การโจมตี ไม่มีใคร "โดน" — นับเป็นตัวเอกเห็นท่า (+1 · ตั้งรับอยู่ +2) ให้ยังสะสมความเข้าใจได้
	if cur.side == "foe" and tech.id == "signature" and not tech.is_attack():
		var h := hero()
		if h != null and not h.down:
			_note_understanding(cur, h)

	if tech.is_attack():
		var targets := _resolve_scope(tech, target)
		var bonus := 1.5 if free else 1.0
		_fx_glimmer = free
		for _i in tech.hits:
			for t in targets:
				if not t.down:
					_strike(cur, t, tech, bonus)
		_fx_glimmer = false

	var wm := 1.0
	if cur.windup:
		wm = 0.5
		cur.windup = false
		_log("    (ท่วงท่าจากการตั้งรับ: น้ำหนัก x0.5)")
	if cur.has_status(Status.SLOWED):
		wm *= Status.av_mult_of(Status.SLOWED)
	cur.av += Formulas.av(cur.spd) * tech.weight * tech.self_av_mult * wm
	if tech.effect == "av_cut":
		cur.av *= 1.0 - tech.effect_value
		_log("    %s ผลุบผลับ — AV x%.2f" % [cur.name, 1.0 - tech.effect_value])
	if tech.target_av_mult != 1.0 and not target.down:
		target.av *= tech.target_av_mult

## เรียนท่าจากประกาย — ใช้ร่วมกันระหว่างประกายตอนใช้ท่ากับประกายสวนกลับ
func _learn_glimmer(cur: Actor, g: Tech, guaranteed: bool, p: float, kind: String) -> void:
	cur.learned.append(g.name)
	cur.first_glimmer_pending = false
	glimmer_log.append(g.name)
	if guaranteed:
		glimmers_from_fill += 1
		cur.insight = 0.0
		cur.insight_lock = Insight.LOCK_ROUNDS
		_log("    ★★ ประกาย%s! %s เรียนรู้ %s (Insight เต็ม)" % [kind, cur.name, g.name])
	else:
		_log("    ★ ประกาย%s! %s เรียนรู้ %s (สุ่มติด %.1f%%)" % [kind, cur.name, g.name, p * 100.0])

# ── อ่านทางหลบ (kwan 6 ต.ค. 2026) ─────────────────────────
## ท่าเด่นมอนกำลังจะลงตัวเอก — คืน true ถ้าหลบได้ (ไม่โดนดาเมจ)
## ลำดับ: หลบด้วยแต้มก่อนหน้า → ยังไม่เคยอ่าน = โรลสูตรประกาย → โดน/เห็นท่าอีกครั้ง = แต้ม +1 (ตั้งรับ +2)
func _read_signature(src: Actor, tgt: Actor) -> bool:
	if not allow_glimmer or techs == null:
		return false
	var dodged := false
	var ch := tgt.dodge_chance(src.id)
	if ch > 0.0 and (ch >= 1.0 or randf() < ch):
		dodged = true
	if not tgt.reads.has(src.id):
		var p := Formulas.glimmer_chance(src.tier, tgt.tier, 0.0, tgt.luck)
		if randf() >= p:
			return false
		var on := tgt.reads_on() < tgt.read_slots
		tgt.reads[src.id] = {"name": src.signature, "p": 0, "need": maxi(1, src.comprehension), "on": on}
		read_glimmers += 1
		_log("    ★ ประกายหลบ! %s เริ่มอ่านทาง %s ของ %s (สุ่มติด %.1f%%)%s" % [tgt.name, src.signature, src.name,
			p * 100.0, "" if on else " · ช่องเต็ม ยังไม่ติดตั้ง"])
	var r: Dictionary = tgt.reads[src.id]
	var need := int(r["need"])
	if int(r["p"]) < need:
		r["p"] = mini(need, int(r["p"]) + (2 if tgt.guarding else 1))
		_log("    ◇ อ่านทาง %s %d/%d (หลบได้ %d%%)" % [src.signature, r["p"], need,
			int(round(100.0 * float(r["p"]) / float(need)))])
	return dodged

# ── ประกายสวนกลับ (kwan 6 ต.ค. 2026) ──────────────────────
## ตั้งรับแล้วโดนตี → โรลสูตรประกาย (Insight เต็ม = แน่นอน) → ติด = เรียนท่าใหม่แล้วสวนทันที นอกคิว
## ไม่เสีย SP · แรง x1.5 เหมือนประกายปกติ · ครั้งเดียวต่อการตั้งรับหนึ่งครั้ง
func _counter_glimmer(src: Actor, h: Actor) -> void:
	if not allow_glimmer or techs == null or h.counter_used or src.down or h.down:
		return
	h.counter_used = true
	var guaranteed := h.insight >= Insight.THRESHOLD
	var learned_ratio: float = float(h.learned.size()) / maxf(float(_school_size(h)), 1.0)
	var p := Formulas.glimmer_chance(src.tier, h.tier, learned_ratio, h.luck)
	if not guaranteed and randf() >= p:
		return
	var g: Tech = techs.roll_glimmer(h.learned, h.school, h.tier, null, h.steer_branch)
	if g == null:
		return
	counter_glimmers += 1
	_learn_glimmer(h, g, guaranteed, p, "สวนกลับ")
	var prev := _fx_glimmer
	_fx_glimmer = true
	for _i in g.hits:
		for t in _resolve_scope(g, src):
			if not t.down:
				_strike(h, t, g, 1.5)
	_fx_glimmer = prev

func _strike(src: Actor, tgt: Actor, tech: Tech, bonus: float) -> void:
	var is_sig := src.side == "foe" and tgt.is_hero and tech.name == src.signature and src.id != ""
	if is_sig and _read_signature(src, tgt):
		dodges += 1
		_log("  รอบ %2d  %s → %s [%s] : หลบได้! (อ่านทางออก)" % [rounds, src.name, tgt.name, tech.name])
		if capture:
			events.append({"src": src, "tgt": tgt, "tech": tech.name, "school": tech.school, "dmg": 0,
				"weak": false, "glimmer": false, "dodge": true})
		_note_understanding(src, tgt)
		return
	var elem: float = tgt.elem_mult(tech.element)
	var pos := 1.0
	if tgt.row == "หลัง" and not (tech.ignore_pos or tech.free_row):
		pos = 0.7
	var guard_mult := 0.5 if tgt.guarding else 1.0
	var dmg := Formulas.damage(src.atk, tech.power, tgt.def_val,
		elem, pos, bonus * guard_mult, tech.ignore_def)
	tgt.hp = maxi(0, tgt.hp - dmg)
	tgt.hits += 1
	tgt.last_hit = dmg
	if not tgt.telegraph.is_empty():
		tgt.telegraph["dmg"] = int(tgt.telegraph["dmg"]) + dmg
	if src.side == "ally": dealt += dmg
	else: taken += dmg

	var tag := ""
	if elem == Formulas.WEAK_MULT:
		tag = "  จุดอ่อน! ดันคิว"
		src.av *= Formulas.PUSH_MULT
		if src.is_hero:
			_gain_insight(src, Insight.HIT_WEAKNESS, "ตีจุดอ่อน")
	elif elem == Formulas.RESIST_MULT:
		tag = "  ต้านทาน"
	elif elem == 0.0:
		tag = "  ภูมิคุ้มกัน"
	if tgt.guarding:
		tag += "  (ตั้งรับ -50%)"

	_log("  รอบ %2d  %s → %s [%s] : %d (เหลือ %d/%d)%s"
		% [rounds, src.name, tgt.name, tech.name, dmg, tgt.hp, tgt.max_hp, tag])
	if capture:
		events.append({"src": src, "tgt": tgt, "tech": tech.name, "school": tech.school, "dmg": dmg,
			"weak": elem == Formulas.WEAK_MULT, "glimmer": _fx_glimmer})

	# ฝ่ายเราโดนตี = สะสม Insight
	# ศัตรูเล็งตัวที่ HP น้อยที่สุด มอนร่วมทีมจึงเป็นแท้งก์และตัวเอกแทบไม่โดน
	# Insight ต้องตอบสนองต่อความอันตรายของทั้งทีม ไม่ใช่แค่ตัวเอก
	if tgt.side == "ally" and tgt.hp > 0:
		var ratio := float(tgt.hp) / float(tgt.max_hp)
		if tgt.is_hero:
			if tgt.guarding:
				_gain_insight(tgt, Insight.GUARD_HIT, "ตั้งรับรับท่า")
			if dmg > tgt.max_hp * 0.18:
				_gain_insight(tgt, Insight.HEAVY_HIT, "โดนหนัก")
			if ratio < 0.15:
				_gain_insight(tgt, Insight.HP_CRITICAL, "HP วิกฤต")
			elif ratio < 0.3:
				_gain_insight(tgt, Insight.HP_LOW, "HP ต่ำ")
		elif ratio < Insight.ALLY_HURT_RATIO:
			_gain_insight(hero(), Insight.ALLY_HURT, "เพื่อนเจ็บหนัก")
		if tgt.is_hero and tgt.guarding and src.side == "foe":
			_counter_glimmer(src, tgt)

	if src.side == "foe" and tgt.side == "ally" and tech.name == src.signature and src.id != "":
		_note_understanding(src, tgt)

	if tech.status != "" and tgt.hp > 0:
		_apply_status(tgt, tech.status, tech.status_chance)

	if tgt.hp <= 0:
		tgt.down = true
		if tgt.side == "foe":
			kills += 1; hits_on_kill += tgt.hits
		else:
			downs += 1
			if not tgt.is_hero:
				_gain_insight(hero(), Insight.ALLY_DOWN, "เพื่อนล้ม")
		_log("    %s ล้ม (ถูกตี %d ครั้ง)" % [tgt.name, tgt.hits])

func _resolve_scope(tech: Tech, target: Actor) -> Array:
	var side := "foe" if target.side == "foe" else "ally"
	var pool := foes() if side == "foe" else allies()
	match tech.scope:
		"all":    return pool
		"row":    return pool.filter(func(a): return a.row == target.row)
		"column": return pool
		_:        return [target]

func _school_size(a: Actor) -> int:
	if techs == null: return 6
	var n := 0
	for t in techs.all:
		if t.school == a.school: n += 1
	return n

## ท่าพื้นฐานสำหรับตัวที่ไม่มีต้นไม้ท่า (มอนในทีม / ศัตรู)
func _basic_tech(a: Actor) -> Tech:
	var t := Tech.new()
	t.id = "basic"; t.name = "โจมตี"; t.power = 100.0; t.weight = 1.0
	t.element = a.basic_element
	t.scope = "single"
	t.status = a.basic_status
	t.status_chance = a.basic_status_chance
	return t

## ท่าเด่นที่ศัตรูเปิดไว้ — แรงกว่าท่าปกติ และลงสถานะแรงกว่า
func _signature_tech(a: Actor) -> Tech:
	var t := _basic_tech(a)
	t.id = "signature"
	t.name = a.signature
	t.power = Formulas.TEL_POWER
	t.status_chance = minf(1.0, a.basic_status_chance * Formulas.TEL_STATUS_BONUS)
	# ท่าเด่นที่มีผลจริง (data/sig_effects.csv · ตัวเลขจากคอลัมน์ tech_effect ของ monsters.csv)
	var fx: Dictionary = a.sig_effect
	if not fx.is_empty():
		t.effect = str(fx.get("effect", ""))
		t.effect_value = float(fx.get("value", 0.0))
		t.effect_turns = int(fx.get("turns", 0))
		t.once = int(fx.get("once", 0)) == 1
		if int(fx.get("strike", 1)) == 0:
			t.power = 0.0
			t.status = ""
	return t

## ศัตรูที่เปิดท่าเด่นแบบโจมตีไว้ (ให้ Ai ตัดสินว่าบัฟหรือตีขัด)
## gap = ดาเมจที่ยังขาดถึงเกณฑ์ขัด · turns = ตาของ cur ก่อนศัตรูตัวนั้นลงมือ (นับตานี้ด้วย ตามคิว preview)
func _attack_threats(cur: Actor) -> Array:
	var out := []
	var q := preview(12)
	for f in foes():
		if f.telegraph.is_empty() or not _signature_tech(f).is_attack():
			continue
		var turns := 0
		for a in q:
			if a == f:
				break
			if a == cur:
				turns += 1
		out.append({"actor": f, "sig": _signature_tech(f), "gap": f.max_hp * Formulas.INTERRUPT_PCT - float(f.telegraph["dmg"]), "turns": maxi(turns, 1)})
	return out

## ท่าเด่นแบบครั้งเดียวต่อการต่อสู้ที่ใช้ไปแล้ว ห้ามเปิดท่าซ้ำ
func _sig_spent(a: Actor) -> bool:
	return int(a.sig_effect.get("once", 0)) == 1 and a.once_used.has(a.signature)

## โดนท่าเด่น +1 · ตั้งรับใส่ท่านั้น +2 (GDD 5.2) — ท่าที่ถูกขัดจังหวะไม่เคยลงมือ จึงไม่ได้ความเข้าใจ
func _note_understanding(src: Actor, viewer: Actor) -> void:
	var pts := 2 if viewer.guarding else 1
	_add_understanding(src, viewer, pts)
	_log("    ◇ เข้าใจท่า %s ของ %s +%d (%d/%d)" % [src.signature, src.name, pts,
		understanding[src.id], _understand_need[src.id]])

func _add_understanding(src: Actor, viewer: Actor, pts: int) -> void:
	understanding[src.id] = int(understanding.get(src.id, 0)) + pts
	_understand_need[src.id] = maxi(1, src.comprehension)
	_understand_boss[src.id] = src.is_boss
	if not _understand_viewers.has(src.id):
		_understand_viewers[src.id] = []
	if not _understand_viewers[src.id].has(viewer):
		_understand_viewers[src.id].append(viewer)

## สายพันธุ์ที่เข้าใจครบแล้ว — บอสต้องมีผู้เห็นท่ายังยืนอยู่ตอนจบศึก
func understood() -> Array[String]:
	var out: Array[String] = []
	for id in understanding.keys():
		if int(understanding[id]) < int(_understand_need.get(id, 1)):
			continue
		if bool(_understand_boss.get(id, false)):
			var standing := false
			for v in _understand_viewers.get(id, []):
				if not v.down:
					standing = true
			if not standing:
				continue
		out.append(str(id))
	return out

## ผลศึก (ใช้หลัง is_over() คืน true)
func result() -> Dictionary:
	return _result()

func _result() -> Dictionary:
	return {
		"won": won, "rounds": rounds, "time": time_elapsed,
		"dealt": dealt, "taken": taken,
		"downs": downs, "kills": kills, "hits_on_kill": hits_on_kill,
		"glimmers": glimmers, "glimmer_log": glimmer_log, "tech_uses": tech_uses,
		"fills": fills, "from_fill": glimmers_from_fill,
		"counters": counter_glimmers, "reads": read_glimmers, "dodges": dodges,
		"statuses": statuses_applied, "guards": guards, "status_deaths": status_deaths,
		"combos": combos, "telegraphs": telegraphs, "interrupts": interrupts,
		"ambush": ambush,
		"understanding": understanding.duplicate(), "understood": understood(),
	}
