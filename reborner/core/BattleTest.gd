# core/BattleTest.gd — ดูศึกเดียวแบบเห็นทุกบรรทัด
# ใช้ Battle ตัวเดียวกับ Sim.gd — ห้ามมีลูปเทิร์นซ้ำ (GDD 11.15)
# ⚠ ไฟล์นี้ต้องไม่มี class_name — เป็นสคริปต์ติด Node ไม่ใช่คลาส
extends Node

const HERO_PROF := 25
const WEAPON_BASE := 30
const ENEMY := "M29"   # เปลี่ยนเป็น M15 / M03 เพื่อดูศึกอื่น

func _ready() -> void:
	randomize()
	var rows := CsvDb.load_csv("res://data/monsters.csv")
	if rows.is_empty():
		push_error("ไม่พบ res://data/monsters.csv")
		return
	var by_id := CsvDb.index_by(rows, "monster_id")
	var techs := TechDb.new()
	techs.load_from("res://data/techs.csv")
	print("มอนสเตอร์ %d ตัว · ท่า %d ท่า" % [rows.size(), techs.all.size()])
	print("สัญลักษณ์ในบันทึก:  ▼ เปิดท่า  ✂ ขัดจังหวะ  ◆ คอมโบ / Insight เต็ม  ★ ประกาย\n")

	var b := Battle.new()
	b.verbose = true
	b.techs = techs

	var hero := Actor.new()
	hero.id = "hero"
	hero.name = "Riona"
	hero.side = "ally"
	hero.is_hero = true
	hero.tier = HERO_PROF
	hero.max_hp = Formulas.hero_hp(HERO_PROF)
	hero.hp = hero.max_hp
	hero.max_sp = Formulas.hero_sp(HERO_PROF, 0)
	hero.sp = hero.max_sp
	hero.atk = Formulas.hero_atk(HERO_PROF, WEAPON_BASE)
	hero.def_val = Formulas.hero_def(HERO_PROF)
	hero.spd = 120
	hero.school = "คม"
	hero.steer_branch = "เขี้ยว"
	hero.learned.clear()
	for n in ["ฟัน", "เขี้ยวพุ่ง", "กวาด"]:
		hero.learned.append(n)
	b.actors.append(hero)

	for spec in [{"n": "หนอนหินร่วมทาง", "id": "M03"}, {"n": "ค้างคาวร่วมทาง", "id": "M06"}]:
		var m := Actor.from_csv(by_id[spec["id"]])
		m.name = str(spec["n"])
		m.side = "ally"
		m.loyalty = 3
		m.max_hp = int(m.max_hp * 1.6)
		m.hp = m.max_hp
		b.actors.append(m)

	var foe := Actor.from_csv(by_id[ENEMY])
	b.actors.append(foe)
	print("%s (ATK %d · HP %d · ท่า %s) vs ปาร์ตี้ 3 ตัว\n" % [foe.name, foe.atk, foe.max_hp, ", ".join(hero.learned)])

	var res := b.run()

	print("\n— สรุป —")
	var verdict := "ชนะ" if res["won"] else "แพ้"
	print("  ผล: %s · %d รอบ · %.0f AV" % [verdict, res["rounds"], res["time"]])
	print("  คอมโบ %d · เปิดท่า %d · ขัดจังหวะ %d" % [res["combos"], res["telegraphs"], res["interrupts"]])
	print("  Insight เต็ม %d ครั้ง · ประกาย %d (จาก Insight %d)"
		% [res["fills"], res["glimmers"], res["from_fill"]])
	print("  สถานะที่ลงได้ %d · ตั้งรับ %d ครั้ง" % [res["statuses"], res["guards"]])
