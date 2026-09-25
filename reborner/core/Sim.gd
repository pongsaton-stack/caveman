# core/Sim.gd — รันศึกจำลองหลายร้อยครั้งแล้วสรุปสถิติ
# วิธีรัน: Node เปล่า + สคริปต์นี้ + F6
# นี่คือความสามารถที่ใช้ตัดสินทุกอย่างมาตลอดโปรเจกต์ ห้ามทำหาย
# ⚠ ไฟล์นี้ต้องไม่มี class_name — เป็นสคริปต์ติด Node ไม่ใช่คลาส
extends Node

const BATTLES := 200
const WEAPON_BASE := 30
const SCHOOL := "คม"          # สายอาวุธของตัวเอกในการทดสอบ
const STEER := "เขี้ยว"        # กิ่งที่อาวุธชี้ทาง
const VERSION := "ขั้น 4 สัปดาห์ 1 · + บอส B1 ใน Sim"
const BOSS_PROFS := [16, 20, 22]   # จุดที่เส้นทางแผนที่ออกแบบให้ถึงบอส (README)

var by_id: Dictionary = {}
var techs := TechDb.new()

func _ready() -> void:
	randomize()
	var rows := CsvDb.load_csv("res://data/monsters.csv")
	if rows.is_empty():
		push_error("ไม่พบ res://data/monsters.csv")
		return
	by_id = CsvDb.index_by(rows, "monster_id")
	techs.load_from("res://data/techs.csv")
	if techs.all.is_empty():
		push_error("ไม่พบ res://data/techs.csv")
		return

	# บรรทัดนี้บอกว่ากำลังรันไฟล์เวอร์ชันไหนอยู่ — กันสับสนเวลาไฟล์ไม่ถูกทับ
	print("เวอร์ชัน: %s" % VERSION)
	print("Insight: สู้บอส %.0f · เพื่อนล้ม %.0f · เพื่อนเจ็บ %.0f · เกณฑ์ %.0f"
		% [Insight.FIGHTING_BOSS, Insight.ALLY_DOWN, Insight.ALLY_HURT, Insight.THRESHOLD])
	print("มอนสเตอร์ %d ตัว · ท่า %d ท่า · %d สาย · จำลองศึกละ %d ครั้ง\n"
		% [rows.size(), techs.all.size(), techs.schools().size(), BATTLES])

	sweep("M03", "หนอนหิน",    [10, 15, 20])
	sweep("M15", "หมาป่าคู่",  [15, 20, 25], 2)
	sweep("M29", "โกลเลมสลัก", [25, 30, 35, 45])
	boss_sweep()

	tech_progression()

	print("เป้าหมายสมดุล (GDD หมวด 10):")
	print("  ศึกปกติ 150-300 AV · มินิบอส 450-600 AV · ชนะ 70-85%")
	print("  Insight เต็ม: มอนขยะ 0 · ศึกอันตราย ~0.11/ศึก · มินิบอส ~0.42/ศึก")
	print("  คอมโบ ~1/ศึก · ขัดจังหวะ ~1/มินิบอส แทบไม่เกิดกับมอนขยะ")
	print("  ⚠ ตัวเลขจาก AI จำลอง = ขอบล่าง ผู้เล่นจริงจะง่ายกว่านี้มาก (GDD 11.19)")

	# รันแบบ headless (จาก Claude Code / command line) — ปิดเองเมื่อเสร็จ
	if DisplayServer.get_name() == "headless":
		get_tree().quit()

func sweep(mid: String, label: String, profs: Array, count: int = 1) -> void:
	if not by_id.has(mid):
		push_warning("ไม่พบ %s" % mid)
		return
	var tier := int(by_id[mid]["tier"])
	print("── %s (%s tier %d) x%d ──" % [label, mid, tier, count])
	print("  prof   ชนะ  เวลา AV  ออก/เข้า  ประกาย%  Insight เต็ม  คอมโบ  เปิดท่า  ขัด  สถานะ  ตั้งรับ%")
	for p in profs:
		if Formulas.is_swat(tier, p):
			print("  %4d   —      —        —        —          —         —       —      —     —       —   ตบทิ้งบนแมพ" % p)
			continue
		var r := batch(mid, p, count)
		print("  %4d  %3d%%  %6.0f   %6.2f   %6.2f%%     %5.2f     %5.2f   %5.2f  %5.2f  %5.2f   %5.1f%%"
			% [p, int(r["win"] * 100.0), r["time"], r["ratio"], r["glim_rate"] * 100.0,
			   r["fills"], r["combos"], r["tels"], r["ints"], r["status"], r["guard_rate"] * 100.0])
	print("")

func batch(mid: String, prof: int, count: int, weapon: int = WEAPON_BASE) -> Dictionary:
	var wins := 0
	var tot := {"rounds": 0, "time": 0.0, "dealt": 0, "taken": 0, "glimmers": 0,
		"tech_uses": 0, "statuses": 0, "guards": 0, "fills": 0,
		"combos": 0, "telegraphs": 0, "interrupts": 0}
	for i in BATTLES:
		var b := Battle.new()
		b.techs = techs
		b.actors.append(make_hero(prof, weapon))
		for m in make_party():
			b.actors.append(m)
		for j in count:
			var f := Actor.from_csv(by_id[mid])
			if count > 1:
				f.name = "%s %d" % [f.name, j + 1]
			b.actors.append(f)
		var res := b.run()
		if res["won"]:
			wins += 1
		for k in tot.keys():
			tot[k] += res[k]
	var n := float(BATTLES)
	return {
		"win": wins / n,
		"time": tot["time"] / n,
		"ratio": float(tot["dealt"]) / maxf(float(tot["taken"]), 1.0),
		"glim_rate": float(tot["glimmers"]) / maxf(float(tot["tech_uses"]), 1.0),
		"fills": tot["fills"] / n,
		"combos": tot["combos"] / n,
		"tels": tot["telegraphs"] / n,
		"ints": tot["interrupts"] / n,
		"status": tot["statuses"] / n,
		"guard_rate": float(tot["guards"]) / maxf(float(tot["rounds"]), 1.0),
	}

## บอสบนแมพ — ตัวบอสมาจาก encounters.csv (boss=1) · อาวุธมาจากของที่ผู้เล่นมีจริงบนแมพ
## มีดทำครัว = อาวุธเริ่มต้นใน PlayerState · อาวุธใหม่ = ของในหีบ chests.csv
## บอสไม่ถูกตบทิ้งเด็ดขาด จึงไม่เช็ค is_swat (GDD 11.28)
func boss_sweep() -> void:
	var boss_ids: Array[String] = []
	for r in CsvDb.load_csv("res://data/encounters.csv"):
		if str(r.get("boss", "0")) == "1":
			boss_ids.append(str(r["monster_ids"]))
	var weapons: Array[Dictionary] = []
	var start := PlayerState.new()
	weapons.append({"name": start.weapon_name, "base": start.weapon_base})
	for r in CsvDb.load_csv("res://data/chests.csv"):
		weapons.append({"name": str(r["label"]), "base": int(r["weapon_base"])})
	for mid in boss_ids:
		if not by_id.has(mid):
			push_warning("ไม่พบ %s" % mid)
			continue
		print("── บอส %s (%s tier %d) x1 ──" % [by_id[mid]["name_th"], mid, int(by_id[mid]["tier"])])
		for w in weapons:
			print("  อาวุธ: %s (ค่า %d)" % [w["name"], w["base"]])
			print("  prof   ชนะ  เวลา AV  ออก/เข้า  ประกาย%  Insight เต็ม  คอมโบ  เปิดท่า  ขัด  สถานะ  ตั้งรับ%")
			for p in BOSS_PROFS:
				var r := batch(mid, p, 1, int(w["base"]))
				print("  %4d  %3d%%  %6.0f   %6.2f   %6.2f%%     %5.2f     %5.2f   %5.2f  %5.2f  %5.2f   %5.1f%%"
					% [p, int(r["win"] * 100.0), r["time"], r["ratio"], r["glim_rate"] * 100.0,
					   r["fills"], r["combos"], r["tels"], r["ints"], r["status"], r["guard_rate"] * 100.0])
		print("  เป้า: อาวุธ 28 prof 16/20/22 ~55/84/91% · มีดทำครัว ~5-10/20/30-40% (ประตูอาวุธ · GDD 11.29)\n")

## ตัวเอกสู้ต่อเนื่องหลายศึก — ดูว่าต้นไม้ท่าคลี่ออกยังไง
func tech_progression() -> void:
	print("── การคลี่ต้นไม้ท่า (60 ศึกต่อเนื่อง ศัตรูแข็งขึ้นทุก 10 ศึก) ──")
	var hero := make_hero(20)
	var learned_at: Array = []
	# ศัตรูต้องแข็งขึ้นตามตัวเอก ไม่งั้น ThreatFactor ตกจนประกายตาย
	var ladder := ["M15", "M19", "M25", "M29", "M31", "M35"]
	for i in 60:
		var b := Battle.new()
		b.techs = techs
		hero.hp = hero.max_hp
		hero.sp = hero.max_sp
		hero.down = false
		hero.statuses.clear()
		b.actors.append(hero)
		for m in make_party():
			b.actors.append(m)
		var pick: String = ladder[mini(int(i / 10.0), ladder.size() - 1)]
		var f := Actor.from_csv(by_id[pick])
		b.actors.append(f)
		var res := b.run()
		for g in res["glimmer_log"]:
			learned_at.append("ศึกที่ %2d vs %s → %s" % [i + 1, f.name, g])
		hero.insight = 0.0
		hero.insight_lock = 0
		# ความชำนาญโตตามสูตรจริง
		hero.tier += Formulas.prof_gain(f.tier, hero.tier)
		hero.atk = Formulas.hero_atk(hero.tier, WEAPON_BASE)
		hero.max_hp = Formulas.hero_hp(hero.tier)
		hero.max_sp = Formulas.hero_sp(hero.tier, 0)
		hero.def_val = Formulas.hero_def(hero.tier)
	for line in learned_at:
		print("  " + line)
	print("  ท่าที่มีตอนจบ: %s" % ", ".join(hero.learned))
	print("  ความชำนาญตอนจบ: %d\n" % hero.tier)

func make_party() -> Array[Actor]:
	var out: Array[Actor] = []
	for spec in [{"n": "หนอนหินร่วมทาง", "id": "M03"},
			{"n": "ค้างคาวร่วมทาง", "id": "M06"}]:
		if not by_id.has(spec["id"]):
			continue
		var m := Actor.from_csv(by_id[spec["id"]])
		m.name = str(spec["n"])
		m.side = "ally"
		m.is_hero = false
		m.lp = 3
		m.loyalty = 3   # rank 3 = ยิงคอมโบกับตัวเอกได้ (GDD 5.4)
		# มอนร่วมทีมแข็งกว่าตัวป่าเล็กน้อย และ "ไม่" สเกลตามความชำนาญตัวเอก
		# (GDD 5.1 — มอนคือค่าคงที่ ตัวเอกคือตัวแปร)
		m.max_hp = int(m.max_hp * 1.6)
		m.hp = m.max_hp
		m.telegraph = {}
		out.append(m)
	return out

func make_hero(prof: int, weapon: int = WEAPON_BASE) -> Actor:
	var h := Actor.new()
	h.id = "hero"
	h.name = "Rion"
	h.side = "ally"
	h.is_hero = true
	h.tier = prof
	h.max_hp = Formulas.hero_hp(prof)
	h.hp = h.max_hp
	h.max_sp = Formulas.hero_sp(prof, 0)
	h.sp = h.max_sp
	h.atk = Formulas.hero_atk(prof, weapon)
	h.def_val = Formulas.hero_def(prof)
	h.spd = 120
	h.school = SCHOOL
	h.steer_branch = STEER
	var root := techs.root_of(SCHOOL)
	h.learned.clear()
	if root != null:
		h.learned.append(root.name)
	return h
