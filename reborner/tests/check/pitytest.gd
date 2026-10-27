extends SceneTree
# ดรอปอาวุธ + pity (docs/design/team_r3/PITY_SPEC.md) — กติกา 8 ข้อ · ตารางตรงชีตแหล่งอาวุธ · เซฟ/โหลด · เรตจริงจากการสุ่ม
var fails := 0

func check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if not ok: fails += 1

func _initialize() -> void:
	Economy.reload()
	var t := WeaponDrop.table()
	check(t.size() == 31, "ตารางดรอปอาวุธ 31 ชนิดมอน (WEAPON_SOURCES_60.xlsx) — ได้ %d" % t.size())
	var mons := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var bad := []
	for mid in t:
		var r: Dictionary = t[mid]
		if PlayerState.weapon_row(str(r["weapon_id"])).is_empty() or not float(r["base_rate"]) in [5.0, 6.0]:
			bad.append(mid)
		if mons.has(mid) and str(mons[mid]["is_boss"]) != "0":
			bad.append(mid + " เป็นบอส")
	check(bad.is_empty(), "ทุกแถว: อาวุธมีจริง · เรตฐาน 5 หรือ 6 · ไม่ใช่บอส (ข้อ 1 + ขอบเขต) %s" % [bad])
	check(WeaponDrop.weapon_of("M08") == "CR-1" and WeaponDrop.base_rate("M08") == 6.0, "M08 → CR-1 เรต 6%")
	check(WeaponDrop.weapon_of("M01") == "" and WeaponDrop.weapon_of("M15") == "", "มอนที่ไม่มีอาวุธในตาราง = ไม่ดรอปอาวุธ")

	# ── ข้อ 3–5: เรตไต่ +0.5 · ครั้งที่ 40 การันตี · ดรอปแล้วรีเซ็ต (ตัวอย่างในสเปก: 5.0 → 24.0 → 100) ──
	var ps := PlayerState.new()
	var never := RandomNumberGenerator.new()
	var rates: Array[float] = []
	var got := ""
	var kill := 0
	while got == "" and kill < 60:
		rates.append(WeaponDrop.rate(ps, "M02"))
		# บังคับพลาดทุกครั้งก่อนถึงการันตี (ตั้งตัวนับเอง) · ครั้งที่ 40 ใช้ roll จริง
		var e: Dictionary = ps.pity.get("M02", {"misses": 0, "kills": 0})
		if WeaponDrop.guaranteed(ps, "M02"):
			got = WeaponDrop.roll(ps, "M02", never)
		else:
			ps.pity["M02"] = {"misses": int(e["misses"]) + 1, "kills": int(e["kills"]) + 1}
		kill += 1
	check(rates[0] == 5.0 and rates[1] == 5.5 and rates[2] == 6.0, "เรต 5.0 → 5.5 → 6.0 (ข้อ 3)")
	check(rates[38] == 24.0, "ฆ่าครั้งที่ 39 เรต 24.0%% — ได้ %.1f" % rates[38])
	check(rates[39] == 100.0 and kill == 40 and got == "PC-1", "ครั้งที่ 40 การันตีดรอป PC-1 (ข้อ 4) — kill %d got %s" % [kill, got])
	check(WeaponDrop.misses(ps, "M02") == 0 and WeaponDrop.rate(ps, "M02") == 5.0, "ดรอปแล้วตัวนับกลับเรตฐาน (ข้อ 5)")
	check(WeaponDrop.kills(ps, "M02") == 40, "ยอดฆ่าสะสมไม่รีเซ็ต = 40 — ได้ %d" % WeaponDrop.kills(ps, "M02"))

	# ── ข้อ 2: ตัวนับแยกตามชนิด ──
	ps.pity["M08"] = {"misses": 10, "kills": 10}
	check(WeaponDrop.rate(ps, "M08") == 11.0 and WeaponDrop.rate(ps, "M13") == 6.0, "M08 พลาด 10 = 11% · M13 ไม่กระทบ = 6% (ข้อ 2)")

	# ── roll ใช้เรตจริง: สุ่ม 20000 ครั้งที่พลาด 0 ต้องได้ ~5% ──
	var rng := RandomNumberGenerator.new()
	rng.seed = 777
	var hits := 0
	var n := 20000
	for i in n:
		ps.pity.erase("M03")
		if WeaponDrop.roll(ps, "M03", rng) != "":
			hits += 1
	var pct := 100.0 * hits / n
	check(absf(pct - 5.0) < 0.5, "สุ่มที่เรตฐาน 5%% ได้ %.2f%%" % pct)
	# ค่าเฉลี่ยฆ่ากี่ตัวถึงได้ (มีบันทึกไว้ให้ดู ไม่ใช่เกณฑ์)
	var total := 0
	var maxk := 0
	var runs := 4000
	for i in runs:
		ps.pity.erase("M02")
		var k := 0
		while true:
			k += 1
			if WeaponDrop.roll(ps, "M02", rng) != "":
				break
		total += k
		maxk = maxi(maxk, k)
	print("     M02 (5%%): ฆ่าเฉลี่ย %.1f ตัวถึงได้ · มากสุด %d" % [float(total) / runs, maxk])
	check(maxk <= 40, "ไม่มีรอบไหนเกิน 40 ตัว (ข้อ 4)")

	# ── ข้อ 7: ชิ้นซ้ำ = ราคา × 0.5 = ค่าอาวุธ × 5 · ยังนับเป็นดรอป ──
	var ps2 := PlayerState.new()
	var g0 := ps2.gold
	check(WeaponDrop.claim(ps2, "CR-1") == 0 and ps2.weapons_owned.has("CR-1") and ps2.gold == g0, "ชิ้นใหม่เข้าคลัง ไม่ได้เงิน")
	var price := int(PlayerState.weapon_row("CR-1")["price"])
	var g := WeaponDrop.claim(ps2, "CR-1")
	check(g == price / 2 and ps2.gold == g0 + g and ps2.weapons_owned.count("CR-1") == 1, "ชิ้นซ้ำ → +%d เงิน (ราคา %d × 0.5 = ค่าอาวุธ × 5)" % [g, price])
	check(WeaponDrop.dup_gold("SL-1") == 70, "มีดครัว ค่า 14 ซ้ำ = 70")

	# ── ข้อ 6 + 8: เซฟ/โหลดเก็บตัวนับ · บรรทัดแสดงผลมีตัวเลขครบ ──
	ps2.pity["M08"] = {"misses": 7, "kills": 23}
	var ps3 := PlayerState.new()
	ps3.from_dict(ps2.to_dict())
	check(WeaponDrop.misses(ps3, "M08") == 7 and WeaponDrop.kills(ps3, "M08") == 23, "เซฟ/โหลดเก็บตัวนับ (ข้อ 6)")
	var old := ps2.to_dict()
	old.erase("pity")
	var ps4 := PlayerState.new()
	ps4.from_dict(old)
	check(ps4.pity.is_empty() and WeaponDrop.rate(ps4, "M08") == 6.0, "เซฟเก่าไม่มี pity โหลดได้ เริ่ม 0")
	var line := WeaponDrop.status_line(ps3, "M08", "โครงกระดูกเดินเวร")
	print("     " + line)
	check("9.5%" in line and "ฆ่า 23" in line and "7/40" in line, "บรรทัดแสดง เรต · ยอดฆ่า · การันตี n/40 (ข้อ 8)")

	print("FAILS %d" % fails)
	quit(1 if fails > 0 else 0)
