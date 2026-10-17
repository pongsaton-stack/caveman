extends SceneTree
# วัดเศรษฐกิจ (GDD 9 · 12.4): รายได้ต่อศึก · เงินสะสมที่ศึก 10/30/60 · ยาเติมชีวิตและอาวุธแต่ละระดับ = กี่ศึก
#   godot --headless --path . -s tests/measure/econ.gd
# ภูมิภาค 1 = สู้จริงด้วย Battle 100 รอบ × 60 ศึก · ลำดับศึก = จุดเกิดบน map_ashfield.txt วนสุ่มทีละรอบแผนที่
#   เริ่ม prof 8 มีดทำครัว (ค่าเริ่ม PlayerState) → หีบไม้เบสบอล CR-2 หลังศึก 5 → บอส B1 ที่ศึก 20 · ทีมมอน 2 ตัวเต็มทุกศึก · HP เต็มทุกศึก
#   แพ้ = เสียเงินตาม Economy.death_loss · ของดรอปสุ่มตาม drop_rate แล้วขายทันทีที่ราคา EC ตอนนั้น
# ภูมิภาค 2/3 = ประมาณจาก tier ใน monsters.csv × จำนวนศัตรูเฉลี่ยของภูมิภาค 1 (ยังไม่มีแผนที่ ไม่ได้สู้จริง)
const RUNS := 100
const BATTLES := 60
const CHEST_AT := 5
const BOSS_AT := 20

func _initialize() -> void:
	Economy.reload()
	var sim = load("res://core/Sim.gd").new()
	sim.by_id = CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	sim.techs.load_from("res://data/techs.csv")
	var enc := {}
	for r in CsvDb.load_csv("res://data/encounters.csv"): enc[str(r["symbol"])] = r
	var map := MapData.load_map("res://data/map_ashfield.txt")
	var spawns: Array = []
	var boss: Array = []
	for s in map.spawns:
		if not enc.has(s["sym"]): continue
		var g := Array(str(enc[s["sym"]]["monster_ids"]).split("|"))
		if int(enc[s["sym"]]["boss"]) == 1: boss = g
		else: spawns.append(g)

	# ── ตารางรายได้ต่อศึกที่ชนะ (ไม่สุ่ม) ──
	print("== ภูมิภาค 1: เงินต่อศึกที่ชนะ (Economy.win_gold) + ค่าคาดหวังขายของดรอป ที่ EC 0")
	var mix_gold := 0.0; var mix_mat := 0.0; var mix_foes := 0.0
	var groups := spawns.duplicate(); groups.append(boss)
	for g in groups:
		var t := 0; var mat := 0.0
		for id in g:
			t = maxi(t, int(sim.by_id[id]["tier"]))
			mat += _mat_ev(sim.by_id[id], 0)
		var w := Economy.win_gold(t, g.size())
		print("  %-14s ×%d  tier %2d  เงิน %3d  ของดรอป ~%.1f" % [sim.by_id[g[0]]["name_th"], g.size(), t, w, mat])
		if g != boss:
			mix_gold += w; mix_mat += mat; mix_foes += g.size()
	var n_sp := float(spawns.size())
	print("  เฉลี่ยตามจุดเกิด %d จุด: เงิน %.1f + ดรอป %.1f = %.1f ต่อศึกที่ชนะ · ศัตรูเฉลี่ย %.1f ตัว/ศึก"
		% [spawns.size(), mix_gold / n_sp, mix_mat / n_sp, (mix_gold + mix_mat) / n_sp, mix_foes / n_sp])

	# ── สู้จริง ──
	var at := {10: 0.0, 30: 0.0, 60: 0.0}
	var at_mat := {10: 0.0, 30: 0.0, 60: 0.0}
	var wins := 0; var losses := 0; var lost_gold := 0.0; var boss_wins := 0; var gross := 0.0
	for run in RUNS:
		seed(9100 + run)
		var hero: Actor = sim.make_hero(8, 14, "คม", "เขี้ยว")
		var weapon := 14; var school := "คม"; var steer := "เขี้ยว"
		var gold := 0; var mat_gold := 0; var ec := 0
		var order: Array = []
		for i in BATTLES:
			if i == CHEST_AT:
				weapon = 28; school = "ทุบ"; steer = ""
				hero = _rebuild(sim, hero, weapon, school, steer)
			var group: Array
			if i + 1 == BOSS_AT:
				group = boss
			else:
				if order.is_empty():
					order = spawns.duplicate(); order.shuffle()
				group = order.pop_back()
			var b := Battle.new(); b.techs = sim.techs
			hero.hp = hero.max_hp; hero.sp = hero.max_sp; hero.down = false; hero.statuses.clear()
			b.actors.append(hero)
			for m in sim.make_party(): b.actors.append(m)
			var t := 0
			for id in group:
				var f := Actor.from_csv(sim.by_id[id]); b.actors.append(f); t = maxi(t, f.tier)
			var ins0 := hero.insight
			var res := b.run()
			if res["won"]:
				wins += 1
				gold += Economy.win_gold(t, group.size())
				gross += Economy.win_gold(t, group.size())
				for id in group:
					var row: Dictionary = sim.by_id[id]
					if randf() * 100.0 < float(row["drop_rate"]):
						var mr := Economy.material_row(str(row["drop"]))
						if not mr.is_empty(): mat_gold += Economy.sell_price(float(mr["sell_base"]), ec)
				if group == boss:
					boss_wins += 1; ec += 1
				hero.insight = Insight.carry(ins0, hero.insight, t, hero.tier); hero.insight_lock = 0
				hero.tier += Formulas.prof_gain(t, hero.tier)
				hero = _rebuild(sim, hero, weapon, school, steer)
			else:
				losses += 1
				var l := Economy.death_loss(Economy.start_gold() + gold + mat_gold)
				lost_gold += l
				gold -= l
			for k in at.keys():
				if i + 1 == k:
					at[k] += gold; at_mat[k] += gold + mat_gold
	var played := float(RUNS * BATTLES)
	print("== ภูมิภาค 1 สู้จริง %d รอบ × %d ศึก · ชนะ %.1f%% · แพ้ %.2f ครั้ง/รอบ (เสียเฉลี่ย %.0f/ครั้ง) · ชนะบอส %d/%d"
		% [RUNS, BATTLES, 100.0 * wins / played, losses / float(RUNS), lost_gold / maxf(losses, 1), boss_wins, RUNS])
	print("  เงินสะสม (ไม่นับเงินเริ่ม 600 · หักแพ้แล้ว)  ศึก10 %.0f · ศึก30 %.0f · ศึก60 %.0f" % [at[10] / RUNS, at[30] / RUNS, at[60] / RUNS])
	print("  + ขายของดรอปทั้งหมด                    ศึก10 %.0f · ศึก30 %.0f · ศึก60 %.0f" % [at_mat[10] / RUNS, at_mat[30] / RUNS, at_mat[60] / RUNS])
	var per: float = at[60] / RUNS / BATTLES
	var per_mat: float = at_mat[60] / RUNS / BATTLES
	print("  รายได้เฉลี่ยต่อศึก (60 ศึก) หักแพ้แล้ว: %.1f · รวมขายของ %.1f · ก่อนหักแพ้ (เงินชนะล้วน) %.1f" % [per, per_mat, gross / played])

	# ── ราคาเป็นจำนวนศึก ──
	var items := CsvDb.index_by(CsvDb.load_csv("res://data/items.csv"), "item_id")
	var l01 := float(items["L01"]["price"])
	print("== ราคาเป็นจำนวนศึก (ภูมิภาค 1 · EC 0 · รายได้ %.1f/ศึก · รวมขายของ %.1f)" % [per, per_mat])
	print("  ยาเติมชีวิต L01 %dg = %.1f ศึก (%.1f ถ้าขายของ)" % [Economy.buy_price(l01, 0), Economy.buy_price(l01, 0) / per, Economy.buy_price(l01, 0) / per_mat])
	var tier_price := {}
	for id in PlayerState.weapon_table():
		var w: Dictionary = PlayerState.weapon_table()[id]
		tier_price[int(w["tier"])] = tier_price.get(int(w["tier"]), []) + [int(w["price"])]
	var tiers := tier_price.keys(); tiers.sort()
	for t in tiers:
		var ps: Array = tier_price[t]; ps.sort()
		print("  อาวุธระดับ %d  %d–%dg = %.1f–%.1f ศึก" % [t, ps[0], ps[-1], ps[0] / per, ps[-1] / per])

	# ── ภูมิภาค 2/3 ประมาณ ──
	var foes := mix_foes / n_sp
	print("== ภูมิภาคถัดไป (ประมาณ: tier เฉลี่ยของภูมิภาค × ศัตรู %.1f ตัว · ไม่ได้สู้จริง · ไม่หักแพ้)" % foes)
	for reg in [["ที่ราบเถ้า", 0], ["เมืองใต้ซาก", 5], ["ยอดเขาคำสาป", 13]]:
		var ts := 0.0; var mats := 0.0; var c := 0
		for id in sim.by_id:
			var row: Dictionary = sim.by_id[id]
			if str(row["region"]) != reg[0]: continue
			ts += int(row["tier"]); mats += _mat_ev(row, reg[1]); c += 1
		var inc := Economy.win_gold(roundi(ts / c), 1) * foes
		var mat_ev := mats / c * foes
		var lp := Economy.buy_price(l01, reg[1])
		var line := "  %s EC %d (×%.2f): tier เฉลี่ย %.1f · เงิน ~%.0f/ศึก (+ดรอป ~%.0f) · L01 %dg = %.1f ศึก" % [reg[0], reg[1], Economy.price_mult(reg[1]), ts / c, inc, mat_ev, lp, lp / inc]
		for t in tiers:
			line += " · อาวุธ%d %.0f ศึก" % [t, Economy.buy_price(tier_price[t][0], reg[1]) / inc]
		print(line)

	print("== เทียบ GDD")
	print("  9.2  ยาเติม LP ≈ รายได้ 2 ศึก → ต้องได้ ~%.0f/ศึก · วัดได้ %.1f ศึก" % [l01 / 2.0, l01 / per])
	print("  12.4 130g = 13 ศึกภูมิภาค 1 → ต้องได้ ~%.0f/ศึก · วัดได้ %.1f ศึก" % [130.0 / 13.0, 130.0 / per])
	print("  9.2 กับ 12.4 ขัดกันเอง: รายได้ที่ต้องการต่างกัน %.1f เท่า" % [(l01 / 2.0) / (130.0 / 13.0)])
	sim.free()
	quit()

## ค่าคาดหวังเงินขายของดรอปต่อมอน 1 ตัว ที่ EC นี้ (ของที่ร้านไม่รับ = 0)
func _mat_ev(row: Dictionary, ec: int) -> float:
	var mr := Economy.material_row(str(row["drop"]))
	if mr.is_empty(): return 0.0
	return float(row["drop_rate"]) / 100.0 * Economy.sell_price(float(mr["sell_base"]), ec)

func _rebuild(sim, hero: Actor, weapon: int, school: String, steer: String) -> Actor:
	hero.atk = Formulas.hero_atk(hero.tier, weapon)
	hero.max_hp = Formulas.hero_hp(hero.tier); hero.max_sp = Formulas.hero_sp(hero.tier, 0)
	hero.def_val = Formulas.hero_def(hero.tier)
	hero.read_slots = Formulas.tech_slots(hero.tier) / 2
	if hero.school != school:
		hero.school = school; hero.steer_branch = steer
		var root: Tech = sim.techs.root_of(school)
		if root != null and not hero.learned.has(root.name): hero.learned.append(root.name)
	return hero
