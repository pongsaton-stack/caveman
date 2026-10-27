# core/WeaponDrop.gd — ดรอปอาวุธจากมอนปกติ + pity (docs/design/team_r3/PITY_SPEC.md · kwan 26 ต.ค. 2026) · ไม่มี node
# ตาราง = data/weapon_drops.csv (tools/data/weapon_drops_csv.py) · ตัวเลข = data/economy.csv PITY_*
# ตัวนับอยู่ใน PlayerState.pity: monster_id -> {misses, kills} · แยกตามชนิดมอน · ไม่รีเซ็ตตอน NG+ (ข้อ 6)
# บอส/มินิบอสไม่อยู่ในตารางนี้ (ดรอปการันตีของตัวเอง) · วัตถุดิบ/ตำรายังใช้ drop/drop_rate ใน monsters.csv
class_name WeaponDrop
extends RefCounted

static var _rows := {}

static func table() -> Dictionary:
	if _rows.is_empty() and FileAccess.file_exists("res://data/weapon_drops.csv"):
		_rows = CsvDb.index_by(CsvDb.load_csv("res://data/weapon_drops.csv"), "monster_id")
	return _rows

## อาวุธที่มอนชนิดนี้ดรอป · ไม่มี = ""
static func weapon_of(monster_id: String) -> String:
	return str(table().get(monster_id, {}).get("weapon_id", ""))

static func base_rate(monster_id: String) -> float:
	return float(table().get(monster_id, {}).get("base_rate", 0))

static func _entry(ps: PlayerState, monster_id: String) -> Dictionary:
	return ps.pity.get(monster_id, {"misses": 0, "kills": 0})

static func misses(ps: PlayerState, monster_id: String) -> int:
	return int(_entry(ps, monster_id).get("misses", 0))

static func kills(ps: PlayerState, monster_id: String) -> int:
	return int(_entry(ps, monster_id).get("kills", 0))

## ฆ่าครั้งถัดไปของชนิดนี้ได้ครั้งที่ 40 แล้ว (นับจากดรอปครั้งก่อน) → การันตี
static func guaranteed(ps: PlayerState, monster_id: String) -> bool:
	return misses(ps, monster_id) + 1 >= int(Economy.num("PITY_GUARANTEE"))

## เรตของการฆ่าครั้งถัดไป (เปอร์เซ็นต์) = เรตฐาน + PITY_STEP × พลาดติดกัน · การันตี = 100
static func rate(ps: PlayerState, monster_id: String) -> float:
	if weapon_of(monster_id) == "":
		return 0.0
	if guaranteed(ps, monster_id):
		return 100.0
	return minf(100.0, base_rate(monster_id) + Economy.num("PITY_STEP") * misses(ps, monster_id))

## ฆ่ามอนชนิดนี้ 1 ตัว → คืนรหัสอาวุธที่ดรอป หรือ "" · อัปเดตตัวนับ (ดรอป = รีเซ็ต · รวมครั้งการันตี)
static func roll(ps: PlayerState, monster_id: String, rng: RandomNumberGenerator) -> String:
	var wid := weapon_of(monster_id)
	if wid == "":
		return ""
	var r := rate(ps, monster_id)
	var e := _entry(ps, monster_id)
	var hit := guaranteed(ps, monster_id) or rng.randf() * 100.0 < r
	ps.pity[monster_id] = {"misses": 0 if hit else int(e.get("misses", 0)) + 1, "kills": int(e.get("kills", 0)) + 1}
	return wid if hit else ""

## เงินเมื่อได้ชิ้นซ้ำ = ราคา × PITY_DUP_RATIO (= ค่าอาวุธ × 5) × INCOME_MULT
static func dup_gold(weapon_id: String) -> int:
	var price := float(PlayerState.weapon_row(weapon_id).get("price", 0))
	return roundi(price * Economy.num("PITY_DUP_RATIO") * Economy.num("INCOME_MULT"))

## เก็บอาวุธที่ดรอป · ชิ้นใหม่ = เข้าคลัง คืน 0 · ชิ้นซ้ำ = แปลงเป็นเงินอัตโนมัติ คืนจำนวนเงิน (ข้อ 7)
static func claim(ps: PlayerState, weapon_id: String) -> int:
	if not ps.weapons_owned.has(weapon_id):
		ps.weapons_owned.append(weapon_id)
		return 0
	var g := dup_gold(weapon_id)
	ps.gold += g
	return g

## บรรทัดแสดงผล (ข้อ 8 ห้ามซ่อนตัวเลข) — สมุดบันทึกยังไม่มี ใช้ในสรุปศึกก่อน
static func status_line(ps: PlayerState, monster_id: String, monster_name: String) -> String:
	var wid := weapon_of(monster_id)
	if wid == "":
		return ""
	var wname := str(PlayerState.weapon_row(wid).get("name", wid))
	return "%s → %s · เรต %.1f%% · ฆ่า %d · การันตี %d/%d" % [monster_name, wname, rate(ps, monster_id), kills(ps, monster_id),
		misses(ps, monster_id), int(Economy.num("PITY_GUARANTEE"))]
