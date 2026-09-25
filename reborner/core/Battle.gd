# core/Battle.gd
# ★★ ลูปเทิร์นเดียวของทั้งโปรเจกต์ ★★
# ทั้งเกมจริง ตัวทดสอบ และตัวจำลอง ต้องเรียกคลาสนี้เท่านั้น
# ห้ามเขียนลูปเทิร์นที่อื่นเด็ดขาด (GDD บทเรียน 11.15)
class_name Battle
extends RefCounted

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
var tech_uses := 0
var statuses_applied := 0
var guards := 0
var status_deaths := 0
var combos := 0
var telegraphs := 0
var interrupts := 0

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
		if t.is_attack() and (t.sp == 0 or t.sp <= cur.sp):
			out.append(t)
	return out

## คู่คอมโบที่ใช้ได้ตอนนี้ (null = ยิงคอมโบไม่ได้)
func combo_partner_for(cur: Actor) -> Actor:
	if cur.has_status(Status.SEALED):
		return null
	return _combo_partner(cur)

## ผู้เล่นสั่งตัวเอก — action = {"kind": "tech"|"guard"|"combo", "tech": Tech, "target": Actor}
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
		if a.side == "foe" and a.telegraph.is_empty() and randf() < Formulas.TEL_CHANCE:
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
	if a.has_status(Status.BLEED) and a.last_hit > 0:
		var d := int(round(float(a.last_hit) * Status.bleed_of(Status.BLEED)))
		a.hp = maxi(0, a.hp - d)
		_log("    %s เสีย %d จากเลือดไหล" % [a.name, d])
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

## ตั้งรับ — 4 หน้าที่ในแอ็กชันเดียว แต่เสมอตัวทางเทมโป (GDD 3.3)
func _do_guard(a: Actor) -> void:
	a.guarding = true
	a.windup = true
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
	var pool := usable(cur)
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
	if allow_glimmer and cur.is_hero and techs != null and tech.is_attack():
		tech_uses += 1
		if target.tier > cur.tier:
			_gain_insight(cur, Insight.TECH_ON_STRONG, "ใช้ท่ากับศัตรูแข็งกว่า")
		var guaranteed := cur.insight >= Insight.THRESHOLD
		var learned_ratio: float = float(cur.learned.size()) / maxf(float(_school_size(cur)), 1.0)
		var p := Formulas.glimmer_chance(target.tier, cur.tier, learned_ratio, cur.luck)
		if guaranteed or randf() < p:
			var g: Tech = techs.roll_glimmer(cur.learned, cur.school, cur.tier, tech, cur.steer_branch)
			if g != null:
				cur.learned.append(g.name)
				glimmers += 1
				glimmer_log.append(g.name)
				if guaranteed:
					glimmers_from_fill += 1
					cur.insight = 0.0
					cur.insight_lock = Insight.LOCK_ROUNDS
					_log("    ★★ ประกาย! %s เรียนรู้ %s (Insight เต็ม)" % [cur.name, g.name])
				else:
					_log("    ★ ประกาย! %s เรียนรู้ %s (สุ่มติด %.1f%%)" % [cur.name, g.name, p * 100.0])
				tech = g
				free = true
			elif guaranteed:
				# ไม่มีท่าให้เรียนแล้ว — ห้ามทิ้ง Insight เปล่า (GDD 4.3 กฎกันความหงุดหงิด)
				cur.insight = 0.0
				cur.tier += 2
				_log("    Insight เต็มแต่ไม่มีท่าให้เรียน → แปลงเป็นโบนัสความชำนาญ +2")

	if not free and tech.sp > 0:
		cur.sp -= tech.sp

	var targets := _resolve_scope(tech, target)
	var bonus := 1.5 if free else 1.0
	for _i in tech.hits:
		for t in targets:
			if not t.down:
				_strike(cur, t, tech, bonus)

	var wm := 1.0
	if cur.windup:
		wm = 0.5
		cur.windup = false
		_log("    (ท่วงท่าจากการตั้งรับ: น้ำหนัก x0.5)")
	if cur.has_status(Status.SLOWED):
		wm *= Status.av_mult_of(Status.SLOWED)
	cur.av += Formulas.av(cur.spd) * tech.weight * tech.self_av_mult * wm
	if tech.target_av_mult != 1.0 and not target.down:
		target.av *= tech.target_av_mult

func _strike(src: Actor, tgt: Actor, tech: Tech, bonus: float) -> void:
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
	return t

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
		"statuses": statuses_applied, "guards": guards, "status_deaths": status_deaths,
		"combos": combos, "telegraphs": telegraphs, "interrupts": interrupts,
		"ambush": ambush,
	}
