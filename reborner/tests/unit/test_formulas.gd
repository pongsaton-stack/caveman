# tests/unit/test_formulas.gd — gdUnit4: กฎของสูตรใน core/Formulas.gd
# ตัวเลขที่คาดหวังคำนวณจากค่าคงที่ในไฟล์เดียวกัน (MIT_K, THREAT_*, SWAT_GAP …) ไม่พิมพ์เลขเอง
# เปลี่ยนค่าคงที่ได้โดยเทสต์ยังผ่าน · พังเมื่อ "รูปร่าง" ของสูตรเปลี่ยน (เช่น DEF ไม่ลดดาเมจ · threat ไม่ถูกตัดขอบ)
extends GdUnitTestSuite


func test_mitigation_no_def_takes_full_damage() -> void:
	assert_float(Formulas.mitigation(0.0)).is_equal_approx(1.0, 0.000001)


func test_mitigation_def_equal_to_k_halves_damage() -> void:
	assert_float(Formulas.mitigation(Formulas.MIT_K)).is_equal_approx(0.5, 0.000001)


func test_mitigation_falls_as_def_rises() -> void:
	assert_float(Formulas.mitigation(80.0)).is_less(Formulas.mitigation(40.0))


func test_full_armor_pierce_ignores_def() -> void:
	assert_float(Formulas.mitigation(500.0, 1.0)).is_equal_approx(1.0, 0.000001)


func test_av_is_inverse_of_speed() -> void:
	assert_float(Formulas.av(100.0) / Formulas.av(200.0)).is_equal_approx(2.0, 0.000001)


func test_av_survives_zero_speed() -> void:
	assert_float(Formulas.av(0.0)).is_equal_approx(Formulas.AV_NUM, 0.000001)


func test_threat_is_one_at_equal_level() -> void:
	assert_float(Formulas.threat(20.0, 20.0)).is_equal_approx(1.0, 0.000001)


func test_threat_is_clamped_both_ways() -> void:
	assert_float(Formulas.threat(0.0, 999.0)).is_equal_approx(Formulas.THREAT_MIN, 0.000001)
	assert_float(Formulas.threat(999.0, 0.0)).is_equal_approx(Formulas.THREAT_MAX, 0.000001)


func test_swat_boundary_is_prof_minus_gap() -> void:
	var prof := 30.0
	assert_bool(Formulas.is_swat(prof - Formulas.SWAT_GAP, prof)).is_true()
	assert_bool(Formulas.is_swat(prof - Formulas.SWAT_GAP + 1, prof)).is_false()


func test_ambush_never_freezes_a_side() -> void:
	# บทเรียน GDD 11.17: AMBUSH_MULT = 0 ทำให้อีกฝ่ายไม่ได้เล่นเลย
	assert_float(Formulas.AMBUSH_MULT).is_greater(0.0)
