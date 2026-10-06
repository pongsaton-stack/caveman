extends SceneTree
# tools/web/ui_battle_record.gd — บันทึกศึก B1 จาก Battle.gd ตัวจริง (seed คงที่) ให้หน้า UI Kit เล่นภาพตาม
# หน้าเว็บไม่คิดผลศึกเอง (กฎ: ลูปเทิร์นมีที่เดียวคือ Battle) — แค่เล่นภาพตามบันทึกนี้
# เลือก seed แรกที่ชนะ + มีประกาย + มีขัดจังหวะ + บอสใช้ท่าเด่นลงมือจริง · พิมพ์ JSON: บรรทัดเดียวขึ้นต้น REC:
func setup(td: TechDb, by_id: Dictionary) -> Battle:
	var ps := PlayerState.new(); ps.prof = 20
	ps.init_new(td, Vector2i.ZERO); ps.sync_weapon(td)
	ps.learned.append("เขี้ยวพุ่ง"); ps.learned.append("กวาด")
	ps.equip(PlayerState.weapon_row("W23"), td, 28)
	ps.learned.append("หักเกราะ")
	ps.insight = 14.0
	ps.seed_party(CsvDb.load_csv("res://data/companions.csv"))
	var b := Battle.new(); b.techs = td; b.capture = true
	b.actors.append(ps.make_hero())
	for m in ps.make_companions(by_id, 2): b.actors.append(m)
	b.actors.append(Actor.from_csv(by_id["B1"]))
	return b

func snap(b: Battle) -> Array:
	var out := []
	for a in b.actors:
		out.append({"hp": a.hp, "down": a.down, "tel": str(a.telegraph.get("name", "")) if not a.telegraph.is_empty() else "",
			"telDmg": int(a.telegraph.get("dmg", 0)) if not a.telegraph.is_empty() else 0, "sp": a.sp, "ins": snappedf(a.insight, 0.1)})
	return out

func record(seed_n: int, td: TechDb, by_id: Dictionary) -> Dictionary:
	seed(seed_n)
	var b := setup(td, by_id)
	var idx := {}
	var roster := []
	for i in b.actors.size():
		var a: Actor = b.actors[i]; idx[a] = i
		roster.append({"id": a.id, "name": a.name, "side": a.side, "hero": a.is_hero, "max_hp": a.max_hp, "max_sp": a.max_sp,
			"lp": a.lp, "loyalty": a.loyalty, "tier": a.tier, "body": a.body, "sig": a.signature})
	var turns := []
	b.begin()
	var start := snap(b)
	var sig_hit := false
	while not b.is_over():
		var cur := b.next_turn()
		if cur == null:
			continue
		var usable := []
		if cur.is_hero:
			for t in b.usable(cur): usable.append({"name": t.name, "sp": t.sp, "scope": t.scope, "power": t.power})
		var e0 := b.events.size(); var l0 := b.log_lines.size()
		var queue := []
		for a in b.preview(8): queue.append(idx[a])
		b.auto_act(cur)
		var evs := []
		for e in b.events.slice(e0):
			var d := {"src": idx[e["src"]], "tgt": idx[e["tgt"]], "tech": e["tech"], "dmg": e["dmg"], "weak": e.get("weak", false),
				"glimmer": e.get("glimmer", false), "body": e.get("body", 0), "dodge": e.get("dodge", false), "buff": e.get("buff", ""), "dot": e.get("dot", "")}
			if e["tech"] == by_id["B1"]["signature_tech"]: sig_hit = true
			evs.append(d)
		turns.append({"cur": idx[cur], "queue": queue, "usable": usable, "events": evs, "after": snap(b), "log": b.log_lines.slice(l0)})
	var res := b.result()
	return {"seed": seed_n, "won": res["won"], "glimmers": res["glimmers"] + res["counters"], "interrupts": res["interrupts"], "sig_hit": sig_hit,
		"roster": roster, "start": start, "turns": turns, "glimmer_log": res["glimmer_log"], "prof_gain": Formulas.prof_gain(20, 20),
		"loot": int(by_id["B1"]["tier"]), "time": res["time"]}

func _initialize() -> void:
	var td := TechDb.new(); td.load_from("res://data/techs.csv"); td.load_seize("res://data/seize_techs.csv")
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	for s in range(1, 400):
		var r := record(s, td, by_id)
		if r["won"] and r["glimmers"] >= 1 and r["interrupts"] >= 1 and r["sig_hit"] and r["turns"].size() <= 40:
			print("REC:" + JSON.stringify(r))
			quit()
			return
	print("ไม่เจอ seed ที่เข้าเงื่อนไข")
	quit()
