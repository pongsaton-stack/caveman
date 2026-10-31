extends SceneTree
# ขั้น D ระบบพวก (MONSTER_ALLY_SYSTEM_SPEC 2.0 + ส่วนที่ 13 ชุดที่ 6) — วัด pacing ช่วงเปิดเกมด้วยตรรกะเกมจริง
# ส่วน 1: Rion + พวก 1 ตัว (rank เริ่ม 1) vs ค้างคาว ×2 / หมาป่าคู่ · Rion + พวก 2 ตัว vs บอส B1 (HP เต็ม · 200 ศึก/ช่อง)
# ส่วน 2: เส้นทางจริงภูมิภาค 1 — เริ่มคนเดียว → สู้ตามจุดเกิดที่ตื่น → พักเมื่อ HP < ครึ่ง/แพ้/ครบรอบ (พัก = ศัตรูเกิดใหม่)
#   ขอเข้าทีมผ่าน PlayerState.ally_check / join_ally · ความเชื่อใจ/LP ผ่าน after_battle · ไปบอสเมื่อมีพวก 2 ตัวหลังพักครั้งถัดไป
#   กวาด ALLY_RATE × ALLY_OPENING_PITY ด้วยสำเนาของ ally_check (ค่าจริงใน Formulas = แถว [จริง])
# รัน: <godot> --headless --path . -s res://tests/measure/allies_pace.gd [-- --part=1|2] [--runs=N]
var ow
var RUNS := 300
const PROFS := [8, 10, 12, 16, 20]
# ลำดับจุดเกิดตามระยะจากจุดเริ่ม H (2,3) ใน map_ashfield.txt · หีบไม้เบสบอล a (37,8) อยู่หลังหมาป่า (34,6)
const LAP := [["M01"], ["M03"], ["M01"], ["M01"], ["M03"], ["M06", "M06"], ["M06", "M06"], ["M15", "M15"], ["M03"], ["M15", "M15"]]
const NEEDS := {"M06": 1, "M15": 1}
const CHEST_AFTER := 7   # หยิบหีบได้หลังผ่านจุดเกิดที่ 8 ของรอบ (หมาป่าที่ (34,6)) — หลับ = เดินผ่านได้
const MAX_BATTLES := 120

func _initialize() -> void:
	SaveGame.clear()
	ow = load("res://scenes/overworld.tscn").instantiate()
	root.add_child(ow)
	_run.call_deferred()

func _arg(k: String, d: String) -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--%s=" % k):
			return a.split("=")[1]
	return d

func _run() -> void:
	await process_frame
	RUNS = int(_arg("runs", "300"))
	var part := _arg("part", "all")
	print("ALLY_RATE ", Formulas.ALLY_RATE, " · ALLY_OPENING_PITY ", Formulas.ALLY_OPENING_PITY, " · FIRST ", Formulas.ALLY_OPENING_FIRST,
		" · TRUST_STEP ", Formulas.TRUST_STEP, " · COMPANION_HP_MULT ", Formulas.COMPANION_HP_MULT, " · มีดเริ่ม ", ow.ps.weapon_base)
	if part in ["all", "1"]:
		_winrates()
	if part in ["all", "2"]:
		_route_table()
	quit()

func _new_ps(prof: int, base: int) -> PlayerState:
	var ps := PlayerState.new()
	ps.school = ow.ps.school; ps.weapon_base = ow.ps.weapon_base; ps.weapon_id = ow.ps.weapon_id; ps.weapon_name = ow.ps.weapon_name
	ps.prof = prof
	ps.init_new(ow.techs, ow.ps.cell)
	if base > ps.weapon_base:
		_take_bat(ps)
	ps.hp = ps.max_hp(); ps.sp = ps.max_sp()
	return ps

func _take_bat(ps: PlayerState) -> void:
	var wrow := PlayerState.weapon_row("W23")
	if wrow.is_empty():
		ps.weapon_base = 28
	else:
		ps.equip(wrow, ow.techs, 28)

func _fight(ps: PlayerState, foes: Array) -> Dictionary:
	var b := Battle.new(); b.techs = ow.techs
	var hero := ps.make_hero(); b.actors.append(hero)
	var comps: Array = ps.make_companions(ow.by_id, ow._monster_slots())
	for m in comps: b.actors.append(m)
	var mt := 0
	for id in foes:
		var f := Actor.from_csv(ow.by_id[id]); b.actors.append(f); mt = maxi(mt, f.tier)
	var res := b.run()
	res["hero"] = hero; res["comps"] = comps; res["mt"] = mt
	return res

# ── ส่วน 1 ──────────────────────────────────────────────
func _winrates() -> void:
	print("\n── ส่วน 1: อัตราชนะ (200 ศึก/ช่อง · HP เต็ม · พวก rank 1 HP ×1.6) ──")
	var sets := [
		[["M01"], [["M06", "M06"], ["M15", "M15"]]],
		[["M03"], [["M06", "M06"], ["M15", "M15"]]],
		[["M01", "M03"], [["M06", "M06"], ["M15", "M15"], ["B1"]]],
		[["M01", "M06"], [["B1"]]], [["M03", "M06"], [["B1"]]],
		[["M01", "M15"], [["B1"]]], [["M03", "M15"], [["B1"]]],
	]
	for st in sets:
		for foes in st[1]:
			for base in [14, 28]:
				for rank in ([Formulas.TRUST_MIN, 7] if foes[0] == "B1" else [Formulas.TRUST_MIN]):
					var line := "  Rion+%s vs %s · อาวุธ %d · rank %d:" % ["+".join(st[0]), "+".join(foes), base, rank]
					for prof in PROFS:
						var wins := 0
						for i in 200:
							var ps := _new_ps(prof, base)
							for id in st[0]: ps.join_ally(id, str(ow.by_id[id]["name_th"]) + id)
							for m in ps.party: m["loyalty"] = rank
							if _fight(ps, foes)["won"]: wins += 1
						line += "  p%d %3d%%" % [prof, int(wins / 2.0)]
					print(line)

# ── ส่วน 2 ──────────────────────────────────────────────
## สำเนา PlayerState.ally_check ที่เปลี่ยนค่าได้ (rate/pity) · real = ใช้ฟังก์ชันจริง
func _check(ps: PlayerState, sid: String, rate: float, pity: int, real: bool) -> bool:
	if real:
		return ps.ally_check(sid, randf())
	ps.ally_checks[sid] = int(ps.ally_checks.get(sid, 0)) + 1
	var n := ps.ally_count()
	if n == 0 and Formulas.ALLY_OPENING_FIRST.has(sid):
		return true
	if n == 1:
		ps.opening_checks += 1
		if ps.opening_checks > pity:
			return true
	return randf() < rate

func _route(rate: float, pity: int, real: bool, chest: bool, lap: Array = LAP) -> Dictionary:
	var ps := _new_ps(8, 14)
	var r := {"a1": -1, "a2": -1, "sp1": "", "sp2": "", "falls_pre1": 0, "falls_1": 0, "falls_boss": 0, "boss_try": 0,
		"boss_won": -1, "prof_boss": 0, "ally_downs": 0, "lost_perm": 0, "f1": [0, 0, 0, 0], "pity_used": false,
		"rank_boss": 0, "chest_at": -1, "checks_1": 0}
	var n := 0
	var boss_ready := false
	while n < MAX_BATTLES and r["boss_won"] < 0:
		# พักแล้ว: บอสก่อนถ้ามีพวก 2 ตัวตั้งแต่ก่อนพัก (ผู้เล่นทั่วไปไปลองบอสทันทีที่ตื่น)
		if boss_ready and ps.ally_count() >= 2:
			n += 1; r["boss_try"] += 1
			if r["boss_try"] == 1:
				r["prof_boss"] = ps.prof
				for m in ps.party: r["rank_boss"] += int(m["loyalty"])
			var bres := _fight(ps, ["B1"])
			_after(ps, bres, r, true)
			if bres["won"]:
				r["boss_won"] = n
				break
			r["falls_boss"] += 1
			ps.rest()
			continue
		var rested := false
		for i in lap.size():
			if chest and r["chest_at"] < 0 and i == CHEST_AFTER + 1:
				_take_bat(ps); r["chest_at"] = n
			var foes: Array = lap[i]
			if ps.ally_count() < int(NEEDS.get(foes[0], 0)):
				continue   # หลับ · เดินผ่าน
			n += 1
			var one := ps.ally_count() == 1
			var res := _fight(ps, foes)
			if one and foes[0] in ["M06", "M15"]:
				var k := 0 if foes[0] == "M06" else 2
				r["f1"][k] += 1
				if res["won"]: r["f1"][k + 1] += 1
			var before := ps.ally_count()
			var pc := ps.opening_checks
			_after(ps, res, r, false, rate, pity, real)
			if before == 1 and ps.opening_checks > pc: r["checks_1"] += ps.opening_checks - pc
			if before == 0 and ps.ally_count() == 1 and r["a1"] < 0:
				r["a1"] = n; r["sp1"] = str(ps.party[-1]["id"])
			if before == 1 and ps.ally_count() == 2 and r["a2"] < 0:
				r["a2"] = n; r["sp2"] = str(ps.party[-1]["id"]); r["pity_used"] = ps.opening_checks > pity
				boss_ready = true
			if not res["won"]:
				if ps.ally_count() == 0: r["falls_pre1"] += 1
				elif ps.ally_count() == 1: r["falls_1"] += 1
				rested = true
				break   # กลับจุดพักแล้ว (after_battle ทำ rest ใน _after)
			if ps.hp < ps.max_hp() / 2.0:
				ps.rest(); rested = true
				break
			if n >= MAX_BATTLES: break
		if not rested:
			ps.rest()
	return r

func _after(ps: PlayerState, res: Dictionary, r: Dictionary, boss: bool, rate := 0.0, pity := 0, real := true) -> void:
	if res["won"]:
		ps.absorb(res["hero"], res["mt"])
		ps.prof += Formulas.prof_gain(res["mt"], ps.prof)
		ps.sp = mini(ps.max_sp(), ps.sp + int(ps.max_sp() * Formulas.SP_RESTORE))
	else:
		ps.rest()
	var lost_before := ps.lost.size()
	for a in res["comps"]:
		if a.down: r["ally_downs"] += 1
	ps.after_battle(res["comps"])
	r["lost_perm"] += ps.lost.size() - lost_before
	if res["won"] and not boss:
		for sid in ps.ally_candidates(res.get("defeated", []), ow.by_id):
			if _check(ps, sid, rate, pity, real):
				ps.join_ally(sid, str(ow.by_id[sid]["name_th"]))
				break

func _route_table() -> void:
	print("\n── ส่วน 2: เส้นทางภูมิภาค 1 (%d เกม/แถว · เริ่ม prof 8 มีดครัว · ผู้เล่นอัตโนมัติ) ──" % RUNS)
	print("  ศึกที่ = ลำดับศึกนับจากเริ่มเกม · ค่าเฉลี่ย (p90 / สูงสุด)")
	var rows := [[Formulas.ALLY_RATE, Formulas.ALLY_OPENING_PITY, true, "จริง"]]
	for rate in [0.10, 0.20, 0.30]:
		for pity in [3, 5, 8]:
			rows.append([rate, pity, false, ""])
	# หนอนหินก่อน = เดินไปจุด 2 (15,5) ก่อนสไลม์ (8,4) → พวกตัวแรก M03 · ค่าจริงเท่านั้น
	var lap3 := LAP.duplicate()
	lap3[0] = LAP[1]; lap3[1] = LAP[0]
	for sc in [[false, LAP, rows], [true, LAP, rows], [false, lap3, rows.slice(0, 1)], [true, lap3, rows.slice(0, 1)]]:
		var chest: bool = sc[0]
		var lap: Array = sc[1]
		print("\n  %s · %s" % ["หยิบหีบไม้เบสบอลรอบแรกที่เดินผ่าน (ค่า 28)" if chest else "มีดครัวตลอด (ไม่หยิบหีบ)",
			"สู้สไลม์ก่อน (พวกตัวแรก M01)" if lap == LAP else "สู้หนอนหินก่อน (พวกตัวแรก M03)"])
		for row in sc[2]:
			var acc := {"a1": [], "a2": [], "bw": [], "falls1": 0, "fallsb": 0, "pre1": 0, "downs": 0, "perm": 0, "pity": 0,
				"f1": [0, 0, 0, 0], "nob": 0, "prof": 0, "try": 0, "rank": 0, "sp2": {}, "chk": 0}
			for g in RUNS:
				seed(5000 + g)
				var r := _route(row[0], row[1], row[2], chest, lap)
				acc["a1"].append(r["a1"]); acc["a2"].append(r["a2"]); acc["chk"] += r["checks_1"]
				acc["falls1"] += r["falls_1"]; acc["fallsb"] += r["falls_boss"]; acc["pre1"] += r["falls_pre1"]
				acc["downs"] += r["ally_downs"]; acc["perm"] += r["lost_perm"]; acc["pity"] += 1 if r["pity_used"] else 0
				for k in 4: acc["f1"][k] += r["f1"][k]
				acc["prof"] += r["prof_boss"]; acc["try"] += r["boss_try"]; acc["rank"] += r["rank_boss"]
				acc["sp2"][r["sp2"]] = int(acc["sp2"].get(r["sp2"], 0)) + 1
				if r["boss_won"] < 0: acc["nob"] += 1
				else: acc["bw"].append(r["boss_won"])
			var f1: Array = acc["f1"]
			print("  %s rate %.2f pity %d │ พวก1 ศึก %s │ พวก2 ศึก %s · การันตีทำงาน %d%% · ตรวจ %.1f ครั้ง │ ค้างคาว(พวก1) ชนะ %s · หมาป่า(พวก1) ชนะ %s · แพ้ช่วงพวก1 %.2f │ บอส: prof %.1f rank รวม %.1f ลอง %.2f ครั้ง · ชนะที่ศึก %s · ไม่ผ่านใน %d ศึก %d%% │ พวกล้ม %.1f · หายถาวร %.2f · ตัวที่2 %s" % [
				row[3] if row[3] != "" else "    ", row[0], row[1], _stat(acc["a1"]), _stat(acc["a2"]), int(100.0 * acc["pity"] / RUNS),
				acc["chk"] / float(RUNS),
				_pct(f1[1], f1[0]), _pct(f1[3], f1[2]), acc["falls1"] / float(RUNS),
				acc["prof"] / float(RUNS), acc["rank"] / float(RUNS), acc["try"] / float(RUNS), _stat(acc["bw"]), MAX_BATTLES,
				int(100.0 * acc["nob"] / RUNS), acc["downs"] / float(RUNS), acc["perm"] / float(RUNS), _sp(acc["sp2"])])

func _stat(a: Array) -> String:
	var v: Array = a.filter(func(x): return x >= 0)
	if v.is_empty(): return "—"
	v.sort()
	var s := 0.0
	for x in v: s += x
	return "%.1f (%d/%d)" % [s / v.size(), v[int(0.9 * (v.size() - 1))], v[-1]]

func _pct(w: int, n: int) -> String:
	return "—" if n == 0 else "%d%% (%d ศึก)" % [int(100.0 * w / n), n]

func _sp(d: Dictionary) -> String:
	var out := []
	for k in d: out.append("%s %d" % [k if k != "" else "ไม่ได้", d[k]])
	return " ".join(out)
