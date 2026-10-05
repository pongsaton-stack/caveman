extends SceneTree
func _check(cond: bool, what: String) -> void:
	print(("OK   " if cond else "FAIL ") + what)

func _init() -> void:
	var by_id := CsvDb.index_by(CsvDb.load_csv("res://data/monsters.csv"), "monster_id")
	var techs := TechDb.new(); techs.load_from("res://data/techs.csv")
	var comp_rows := CsvDb.load_csv("res://data/companions.csv")
	var slot_rows := CsvDb.load_csv("res://data/party_slots.csv")
	var item_rows := CsvDb.load_csv("res://data/items.csv")
	var ps := PlayerState.new()
	ps.init_new(techs, Vector2i(3, 3))
	ps.seed_party(comp_rows)
	_check(ps.party.size() == 2, "seed 2 companions")
	ps.seed_party(comp_rows)
	_check(ps.party.size() == 2, "seed only once")
	_check(PlayerState.monster_slots_for(0, slot_rows) == 2 and PlayerState.monster_slots_for(6, slot_rows) == 3 and PlayerState.monster_slots_for(12, slot_rows) == 4, "slots 2/3/4 at EC 0/6/11+")
	var comps := ps.make_companions(by_id, 2)
	_check(comps.size() == 2 and comps[0].lp == 3 and comps[0].loyalty == 3 and comps[0].max_hp == int(int(by_id["M03"]["hp"]) * 1.6), "companion actors built")
	comps[0].down = true
	var notes := ps.after_battle(comps)
	_check(int(ps.party[0]["lp"]) == 2, "down -> LP 2  " + str(notes))
	_check(int(ps.party[1]["loyalty"]) == 4, "clean win -> trust +1 (bat)")
	# rest regen: needs fighting between rests
	var msgs := []
	for i in 3:
		ps.fought_since_rest = true
		msgs.append(ps.rest())
	_check(int(ps.party[0]["lp"]) == 3, "LP regen after 3 counted rests " + str(msgs))
	ps.rest(); ps.rest(); ps.rest()
	_check(ps.rest_count == 0, "rest spam without fighting does not count")
	# permadeath
	for i in 3:
		var c := ps.make_companions(by_id, 2)
		c[0].down = true
		ps.after_battle(c)
	_check(ps.party.size() == 1 and ps.lost.size() == 1, "LP 0 -> gone forever " + str(ps.lost))
	_check(ps.make_companions(by_id, 2).size() == 1, "lost monster no longer fights")
	# items
	ps.add_item("I01", 2); ps.add_item("L01", 1)
	ps.hp = 10
	var herb: Dictionary = item_rows[0]
	var lpot: Dictionary = item_rows[1]
	var msg := ps.use_item(herb)
	_check(ps.hp > 10 and ps.item_count("I01") == 1, "herb heals: " + msg)
	_check(ps.use_item(lpot, str(ps.party[0]["name"])) == "" and ps.item_count("L01") == 1, "LP potion refused at full LP")
	ps.party[0]["lp"] = 1
	_check(ps.use_item(lpot, str(ps.party[0]["name"])) != "" and int(ps.party[0]["lp"]) == 2, "LP potion restores 1")
	_check(ps.use_item(lpot, ps.lost[0]) == "", "cannot revive lost monster")
	# save roundtrip
	ps.shop_stock = {"I01": 5, "L01": 2}
	var d := ps.to_dict()
	var ps2 := PlayerState.new()
	ps2.from_dict(JSON.parse_string(JSON.stringify(d)))
	_check(ps2.party.size() == ps.party.size() and int(ps2.party[0]["lp"]) == 2 and ps2.lost == ps.lost and ps2.item_count("I01") == 1 and int(ps2.shop_stock["L01"]) == 2 and ps2.party_seeded, "save/load roundtrip")
	# old v1 save (no party) gets seeded
	var ps3 := PlayerState.new()
	ps3.from_dict({"prof": 12})
	ps3.seed_party(comp_rows)
	_check(ps3.party.size() == 2, "v1 save seeds party on load")
	quit()
