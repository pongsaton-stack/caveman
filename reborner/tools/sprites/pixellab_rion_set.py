"""ชุด Rion ในเกมจาก PixelLab (kwan 19 ต.ค. "เปลี่ยนเป็น PixelLab ทั้งชุด") → ภาพสะอาด + คลิปให้หน้า animation test

ภาพดิบ: assets/sprites/pixellab_draft/states/<State>/<State>/animations/<ท่า>_v/west · เดินขึ้น/ลง zip/Idle/animations/walk_v*/{north,south}
PixelLab วาดเส้นฟาด/แสง/ประกายติดมาทั้งที่ห้าม (19 ต.ค.) → ลบด้วยโค้ด:
  สีที่ห่างจากสีของภาพยืน (rotation ทิศเดียวกัน) > 40 หรือสว่างกว่าจุดสว่างสุดของตัว · แล้วเก็บก้อนใหญ่สุด + ก้อนที่แตะก้อนใหญ่ (อาวุธที่ติดมือ)
เฟรมที่ใช้ไม่ได้ (ท่าหายใจกลายเป็นเหวี่ยง · เดินขึ้นหันกลับมาหน้า) ตัดด้วย KEEP · ผืน 120x112 เท้าแถว 108 แบบ rion_pack_px · หันซ้ายตามภาพดิบ
  python3 tools/sprites/pixellab_rion_set.py → assets/sprites/pixellab_draft/px_set/<คลิป>_<i>.png + index.json (หน้า animation test อ่านเอง · ร่าง ยังไม่เข้าเกม)
"""
import glob
import json
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PL = os.path.join(ROOT, "assets/sprites/pixellab_draft")
OUT = os.path.join(PL, "px_set")
G = "★ Rion PixelLab · ชุดในเกม (ร่าง 19 ต.ค.)"
SCHOOL = {"bl": ("fight_knife", "คม · มีด"), "bt": ("BT_A_stance", "ทุบ · ค้อน"), "pt": ("PT_A_stance", "แทง · ไขควง"),
	"rg": ("RG_A_stance", "ยิง · ธนู"), "dv": ("DV_A_stance", "กล · รีโมต"), "fs": ("FS_A_stance", "มือเปล่า · นวม")}
# (คลิป, ชื่อ, State, โฟลเดอร์ท่า, ทิศ, เฟรมที่ใช้ (None = ทั้งหมด), ms, วน)
CLIPS = []
# เฟรมที่ตัด (ตรวจด้วยตา 19 ต.ค.): run_k เฟรม 6–7 ซีดขาว+ประกายวาดติด · fs0 เฟรม 1–2 เส้นลมขาวพาดทับอก ลบแล้วหัวขาด · pt0 เฟรม 5 วงลมขาวพันรอบตัว
# bl0 รอบ 2 (kwan 19 ต.ค.): รอบแรกสลับมือกลางท่า (ง้างมือขวา ฟันมือซ้าย) → เจนใหม่ระบุมือขวาทุกเฟรม
ATK_ANIM = {"bl": "bl0_v2"}
KEEP = {"pls_atk_fs": [0, 3, 4, 5, 6, 7], "pls_atk_pt": [0, 1, 2, 3, 4, 6, 7]}
for s, (st, th) in SCHOOL.items():
	CLIPS.append((f"pls_idle_{s}", f"ยืนในศึก · {th}", st, f"idle_{s}_v", "west", None, 180, True))
	CLIPS.append((f"pls_atk_{s}", f"โจมตีพื้นฐาน {s}0 · {th}", st, ATK_ANIM.get(s, f"{s}0_v"), "west", KEEP.get(f"pls_atk_{s}"), 90, False))
CLIPS += [("pls_hurt", "โดนตี · ถือมีด", "fight_knife", "hurt_k_v", "west", None, 90, False),
	("pls_guard", "ตั้งรับ · ถือมีด", "fight_knife", "guard2_k_v", "west", None, 90, False),   # kwan 21 ต.ค. "ให้มอนโจมตีกลับ (Rion โดนตี ตั้งรับ)" · guard_k รอบแรกไม่ผ่าน (ประกายวาดติด · หันขวา · มีดหาย) → guard2_k 4 เฟรม · แรงกระแทก/ถอยทำด้วยโค้ด
	("pls_ko", "ล้ม · มีดหลุดมือ", "fight_knife", "ko_k_v", "west", None, 110, False),
	("pls_run_bl", "วิ่งถือมีด", "fight_knife", "run_k_v", "west", [0, 1, 2, 3, 4, 5], 60, True),
	("pls_hop_bl", "กระโดดถอยถือมีด", "fight_knife", "hop_k_v", "west", [0, 1, 2, 3, 4], 60, False),   # hop_k เฟรม 5–7 กลายเป็นพุ่งไปหน้า + ประกาย/เส้นลม → ตัดทิ้ง · ลงพื้นใช้ภาพย่อ (1) ด้วยโค้ด
	("pls_bl1", "เขี้ยวพุ่ง bl1 · มีด", "fight_knife", "bl1_v2", "west", None, 90, False),   # รอบ 2 (kwan 19 ต.ค. "ขอลองเขี้ยวพุ่ง"): รอบแรกเฟรม 5–6 ฟันมือซ้าย + เฟรม 3 มีดหาย → เจนใหม่ระบุแขนไกล/ใกล้ทุกจังหวะ
	("pls_glim_shift", "ท่ากลางประกาย · ง้าง → ย่อ (มีด)", "fight_knife", "glim_shift_v2", "west", None, 90, False),   # รอบแรกเซิร์ฟเวอร์ PixelLab หมดเวลา (ไม่หักเครดิต) · kwan 21 ต.ค. "เจนภาพท่ากลาง": end_frame จาก bl0_v2 เฟรม 4 → bl1_v2 เฟรม 3
	("pls_bl7", "ตัดเอ็น bl7 (กาลี) · มีด", "fight_knife", "bl7_v", "west", [0, 1, 4, 5], 90, False),   # kwan 21 ต.ค.: ใช้ 0 ตั้งการ์ด · 1 ก้าวเข้ามีดวนขึ้น · 4 มีดวนลงหน้า · 5 ปาด (2–3 มีดชิดหน้า · 6 ประกายวาดติด · 7 มีดหาย · 5–7 เดินหน้าไม่ถอย)
	("pls_bl7_back", "ตัดเอ็น · ก้าวถอยแบบกาลี (end_frame)", "fight_knife", "bl7_back_v", "west", None, 90, False),
	("pls_bl9", "จันทร์เสี้ยว bl9 · ท่าทมโบะ (มีด)", "fight_knife", "bl9_v", "west", [0, 1, 2, 3, 4], 90, False),   # kwan 23 ต.ค. เลือก "2" เจนท่าทมโบะ (จิเง็นริว) · 2 gen · เฟรม 5–7 วาดเส้นฟาดใหญ่ + มีดหาย ตัดทิ้ง → ช่วงฟันใช้ pls_atk_bl 5–7
	("pls_spin_bl", "หมุนตัว 4 มุมจริง · ถือมีด (State)", "fight_knife", "__rot__", "west", None, 60, True),   # ตัดเอ็นแบบ Attack on Titan (kwan 21 ต.ค.): หมุนสว่านผ่านใต้ขามอน
	("pls_bat", "ทุบ bt0 · ไม้เบสบอลสองมือ (State BT_bat_stance)", "BT_bat_stance", "bt0_bat_v", "west", None, 90, False),   # kwan 25 ต.ค. "ทื่อมาก ลองเจน pixellab มาเทียบ" กับภาพ Flow · 18 gen (State 15 + ท่า 3)
	("pls_wheel", "วงล้อ bl4 · หมุน 8 มุม แขนกาง T มีดมือขวา (State BL4_spin_T + rot8)", "BL4_spin_T", "__rot8__", "west", None, 60, True),   # kwan 27 ต.ค. "หมุนตัวครบรอบ แขนกางมีดออก ... ใช้งาน pixellab ได้เลย" · 17 gen
	("pls_storm_low", "พายุเถ้าใบมีด bl12 · ย่อกวาดหมุน 8 มุม (State BL12_low_sweep + rot8)", "BL12_low_sweep", "__rot8__", "west", None, 60, True),   # kwan 27 ต.ค. "ต่อด้วย พายุเถ้าใบมีด ขอแบบจัดเต็ม"
	("pls_storm_air", "พายุเถ้าใบมีด bl12 · กระโดดหมุนกลางอากาศ 8 มุม (State BL12_air_spin + rot8)", "BL12_air_spin", "__rot8__", "west", None, 60, True),
	("pls_storm_coil", "พายุเถ้าใบมีด bl12 · ง้างย่อข้าง (ภาพข้างของ State BL12_low_sweep)", "BL12_low_sweep", "__rot__", "west", [0], 90, False),
	# กิ่งลื่นไหล (kwan 28 ต.ค. "2" แบบผสม · key pose ตามรายงานทีม R2 เป็น State ภาพนิ่ง ทิศซ้าย)
	("pls_iai_crouch", "ปาดไว bl5 · ย่อ iaigoshi มือแตะด้ามในซอง (State BL5_iai_crouch)", "BL5_iai_crouch", "__rot__", "west", [0], 90, False),
	("pls_iai_cut", "ปาดไว bl5 · ปลายจังหวะชักฟัน (State BL5_iai_cut)", "BL5_iai_cut", "__rot__", "west", [0], 90, False),
	("pls_enso", "เงาสองคม bl6 · ตั้งท่าสองมีด (State BL6_enso)", "BL6_enso", "__rot__", "west", [0], 90, False),
	("pls_tcut", "เงาสองคม bl6 · ฟันมีดขวา (State BL6_cut1)", "BL6_cut1", "__rot__", "west", [0], 90, False),
	("pls_cross", "เงาสองคม bl6 · มีดซ้ายไขว้เป็น X (State BL6_cross)", "BL6_cross", "__rot__", "west", [0], 90, False),
	("pls_slither", "ก้าวเงา bl13 · ก้าวไขว้เลื้อยต่ำ (State BL13_slither)", "BL13_slither", "__rot__", "west", [0], 90, False),
	("pls_stride", "ปาดข้ามแถว bl14 · ก้าวเฉียง 45° (State BL14_stride)", "BL14_stride", "__rot__", "west", [0], 90, False),
	("pls_roll", "คมสวน bl15 · พลิกข้อมือปัดคม (State BL15_roll)", "BL15_roll", "__rot__", "west", [0], 90, False),
	# ท่ากลางให้ลื่น (kwan 28 ต.ค. "ท่าดูไม่ลื่นเลย เจนเพิ่มให้ไหลลื่นได้") · ภาพเริ่ม/จบ = key pose เดิม (end_frame) · จัดวางด้วย ALIGN_MATCH
	("pls_iai_draw", "ปาดไว bl5 · ชักฟันออกจากซอง (ท่ากลาง ย่อ → ปลายจังหวะ)", "BL5_iai_crouch", "bl5_draw_v", "west", None, 60, False),
	("pls_iai_noto", "ปาดไว bl5 · สะบัดคม + เก็บเข้าซอง (ท่ากลาง ปลายจังหวะ → ย่อ)", "BL5_iai_crouch", "bl5_noto_v", "west", None, 90, False),
	("pls_sd_summon", "เงาสองคม bl6 · เสกมีดเงามือซ้าย (ท่ากลาง ยืนสู้ → ตั้งท่าสองมีด)", "fight_knife", "bl6_summon_v", "west", [0, 1, 4, 5], 90, False),   # เฟรม 2 เส้นโค้งสีผิววาดติด (clean ลบไม่ได้) · 3 ตัวซีดขาวทั้งตัว
	("pls_sd_cut", "เงาสองคม bl6 · ฟันมีดขวา (ท่ากลาง ตั้งท่า → ฟัน)", "BL6_enso", "bl6_cut_v", "west", [0, 2, 3], 60, False),   # เฟรม 1 วงขาววาดติดตัว
	("pls_sd_x", "เงาสองคม bl6 · ไขว้มีดเงาเป็น X (ท่ากลาง ฟัน → ไขว้)", "BL6_enso", "bl6_x_v", "west", [1, 2, 3], 60, False),   # เฟรม 0 วงขาวพันตัว ลบแล้วตัวขาด
	("pls_sh_glide", "ก้าวเงา bl13 · เลื้อยก้าวไขว้ (วน 6 เฟรม)", "BL13_slither", "bl13_glide_v", "west", None, 60, True),
	("pls_sh_cut", "ก้าวเงา bl13 · ดีดตัวปาดต่ำ (ท่ากลาง เลื้อย → ปาด)", "fight_knife", "bl13_cut_v", "west", None, 60, False),
	("pls_leap", "ปาดข้ามแถว bl14 · กระโดดสูงข้ามแนวหน้า ฟันลง (8 เฟรม · ใช้ร่วมวงล้อ/กวาด/ไม้ตาย)", "fight_knife", "bl14_leap_v", "west", None, 60, False),
	("pls_cs_counter", "คมสวน bl15 · พลิกข้อมือ → ฟันสวน (ท่ากลาง)", "fight_knife", "bl15_counter_v", "west", None, 60, False),
	("pls_lair", "กระโดดสูงลอยง้างมีดเหนือหัว (State BL14_air · ใช้ร่วม bl14 bl4 bl3 bl16)", "BL14_air", "__rot__", "west", [0], 90, False),
	("pls_wm_dive", "วงล้อ bl4 · ทิ้งตัวจากกลางอากาศลง windmill (ท่ากลาง BL14_air → BL4_windmill)", "BL4_windmill", "bl4_dive_v", "west", None, 60, False),   # kwan 28 ต.ค. "ท่า windmill ของ b boy ฟันหมุน"
	("pls_windmill", "วงล้อ bl4 · windmill b-boy กลับหัวยันบ่า ขากาง V มีดมือขวา 8 มุม (State BL4_windmill + rot8)", "BL4_windmill", "__rot8__", "west", None, 60, True),
	("pls_wm_kip", "วงล้อ bl4 · สะบัดขาดีดตัวลุกจาก windmill (ท่ากลาง BL4_windmill → ยืนสู้)", "BL4_windmill", "bl4_kip_v", "west", [2, 3], 90, False),   # เฟรม 0–1 วงแสงเหลืองวาดติดตัว (clean ลบไม่ได้)
	("pls_kneel", "กวาด bl3 · คุกเข่ากางแขนมีด 8 มุม (State BL3_kneel_sweep + rot8)", "BL3_kneel_sweep", "__rot8__", "west", None, 60, True),
	("pls_u_charge", "พันคมดับเถ้า bl16 · ชาร์จจับมีดกลับด้าน (State BL16_charge)", "BL16_charge", "__rot__", "west", [0], 90, False),
	("pls_u_finish", "พันคมดับเถ้า bl16 · ลงฟันตัดสิน (State BL16_finish)", "BL16_finish", "__rot__", "west", [0], 90, False),
	("pls_bat_idle", "ยืนถือไม้เบสบอล (State)", "BT_bat_stance", "__rot__", "west", [0], 180, True),
	("pls_bat2", "ทุบ bt0 รอบ 4 · ง้าง → ฟาดลงเฉียง (ท่ากลาง ไม้หลังไหล่ → State กระทบ)", "BT_bat_stance", "chop_bat2_v", "west", None, 90, False),   # kwan 25 ต.ค. "ใช้ pixellab ปรับให้ตรงกับรายงาน" · PL_START_IMG hop_bat 6 + PL_END_IMG BT_bat_impact
	("pls_bat_imp", "ทุบ · กระทบลงเฉียง ตัวตั้งตรง (State BT_bat_impact)", "BT_bat_impact", "__rot__", "west", [0], 90, False),
	("pls_bat_hop", "กระโดดถอยถือไม้เบสบอล (hop_bat2)", "BT_bat_stance", "hop_bat2_v", "west", None, 60, False),   # hop_bat รอบแรกพุ่งไปหน้า → hop_bat2 เน้นถอยขวา
	("pls_bat_run", "วิ่งแบกไม้เบสบอล (run_bat)", "BT_bat_stance", "run_bat_v", "west", None, 60, True),   # kwan 26 ต.ค. "วิ่งไปโจมตีแบบฟัน เสร็จแล้วทำท่ายืนหายใจ"
	("pls_bat_breath", "ยืนหายใจถือไม้เบสบอล (idle_bat 0–1)", "BT_bat_stance", "idle_bat_v", "west", [0, 1], 180, True),   # เฟรม 2–3 ยกไม้ขึ้น + วาดแสง → ตัดทิ้ง วน 0-1 ด้วยโค้ด
	("pls_walk_s", "เดินลง (หันหน้า)", None, "walk_v-eb599d32", "south", None, 90, True),
	("pls_walk_n", "เดินขึ้น (หันหลัง)", None, "walk_v", "north", None, 90, True)]


# ใบมีดที่ clean() ลบไปพร้อมเส้นฟาดฟ้า (ใบมีดเรืองขาวฟ้าทับเส้นฟาด) → วาดคืนตามแนวด้ามที่เหลือ · พิกัดในผืน 120x112 หลังจัดวาง
# bl0 รอบ 2 เฟรม 5 (จังหวะฟาด): ด้ามชี้ลงซ้ายจบที่ (32, 75) · สีใบมีด/ขอบจากเฟรม 6 (ใบมีดเดียวกันที่ไม่ถูกลบ)
BLADE = {("pls_atk_bl", 5): ((32, 75), (-1, 1), 7, "pls_atk_bl", 6)}
# ใบมีดที่ clean() ลบไส้ขาวเหลือแต่โครงขาด → ล้างโครงในกรอบ clear แล้วคัดลอกใบมีด (พร้อมขอบ) จากเฟรมอ้างอิงในกรอบ src เลื่อนตาม shift
# bl1 รอบ 2 เฟรม 6 (จังหวะแทง): กำปั้นอยู่ซ้ายของเฟรม 7 พอดี 3 จุด ความสูงเท่ากัน · ใบมีดเฟรม 7 ชี้ซ้ายแนวนอนเหมือนกัน
BLADE_COPY = {("pls_bl1", 6): (7, (-3, 0), (26, 64, 36, 73), (30, 64, 39, 73))}


# ท่าเชื่อมระหว่างสองคลิป: แต่ละคลิปจัดวางแยกกัน (ตามกรอบรวมของคลิป) → ภาพดิบตำแหน่งเดียวกันลงผืนต่างกันได้ (atk_bl กับ bl1 ห่าง 11 จุด)
# → ภาพท่าเชื่อมเลื่อนตำแหน่งทีละเฟรมจากตำแหน่งของคลิปต้นทางไปคลิปปลายทาง ไม่กระตุกตอนต่อ (ต้องอยู่หลังทั้งสองคลิปใน CLIPS)
ALIGN_BLEND = {"pls_glim_shift": ("pls_atk_bl", "pls_bl1")}
# วางแนวนอนตามคลิปอื่น แต่เท้าตามกรอบตัวเอง: bl7_back (end_frame จาก bl7_v) PixelLab วาดต่ำกว่าภาพต้นทาง 2 จุด → วางทั้งคลิปเท่า pls_bl7 แล้วเท้าลอย/จม
ALIGN_X = {"pls_bl7_back": "pls_bl7"}
# ท่ากลางที่ผืนภาพดิบขนาดไม่คงที่ (96 · 108x124 · 160x140 …) → จัดวางทั้งคลิปให้เฟรม mine ทับภาพ px_set ของคลิป ref เฟรม ri พอดี (หาเลื่อนที่ทับกันมากสุด)
# = ตัวไม่กระโดดตอนสลับจากภาพท่าเดิมเข้าท่ากลาง (คลิป ref ต้องอยู่ก่อนใน CLIPS)
ALIGN_MATCH = {"pls_iai_draw": ("pls_iai_crouch", 0, 0), "pls_iai_noto": ("pls_iai_draw", -1, 0),
	"pls_sd_summon": ("pls_idle_bl", 0, 0), "pls_sd_cut": ("pls_sd_summon", -1, 0), "pls_sd_x": ("pls_sd_cut", -1, 0),
	"pls_sh_glide": ("pls_slither", 0, 0), "pls_sh_cut": ("pls_slither", 0, 0), "pls_leap": ("pls_stride", 0, 0), "pls_cs_counter": ("pls_roll", 0, 0),
	"pls_wm_dive": ("pls_lair", 0, 0), "pls_windmill": ("pls_wm_dive", -1, 0), "pls_wm_kip": ("pls_idle_bl", 0, -1)}


def match_at(im, ref_path):
	"""ตำแหน่งมุมซ้ายบนของ im บนผืน 120x112 ที่เนื้อทับภาพ ref มากสุด (สหสัมพันธ์ของมาสก์)"""
	from scipy.signal import fftconvolve
	A = (np.array(im)[..., 3] > 127).astype(float)
	B = (np.array(Image.open(ref_path).convert("RGBA"))[..., 3] > 127).astype(float)
	c = fftconvolve(B, A[::-1, ::-1], mode="full")
	i, j = np.unravel_index(int(np.argmax(c)), c.shape)
	return (int(j - (A.shape[1] - 1)), int(i - (A.shape[0] - 1)))


def copy_blade(f, ref, shift, clear, srcbox):
	a = np.array(Image.open(f).convert("RGBA")); r = np.array(Image.open(ref).convert("RGBA"))
	a[clear[1]:clear[3], clear[0]:clear[2]] = 0
	for y in range(srcbox[1], srcbox[3]):
		for x in range(srcbox[0], srcbox[2]):
			if r[y, x, 3] >= 128: a[y + shift[1], x + shift[0]] = r[y, x]
	Image.fromarray(a).save(f)


def draw_blade(c, end, step, n, ref_cid, ref_i):
	"""ใบมีดแนวเฉียง 2 จุด ขอบเข้ม ต่อจากปลายด้าม end ไปทาง step n จุด · ปลายแหลม 1 จุด"""
	ref = np.array(Image.open(os.path.join(OUT, f"{ref_cid}_{ref_i}.png")).convert("RGBA")).astype(int)
	sat = ref[..., :3].max(-1) - ref[..., :3].min(-1); lum = ref[..., :3].mean(-1)
	blade = (ref[..., 3] > 127) & (sat < 40) & (lum > 120)
	light = tuple(np.median(ref[blade][:, :4], axis=0).astype(int))
	edge = tuple(np.median(ref[ndimage.binary_dilation(blade) & ~blade & (ref[..., 3] > 127)][:, :4], axis=0).astype(int))
	a = np.array(c); core = set()
	for k in range(1, n + 1):
		x, y = end[0] + step[0] * k, end[1] + step[1] * k
		core.add((x, y))
		if k < n: core.add((x - step[0], y))   # สองจุดต่อแถว ปลายเหลือจุดเดียว
	for x, y in core: a[y, x] = light
	for x, y in core:
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				u, v = x + dx, y + dy
				if (u, v) not in core and a[v, u, 3] < 128: a[v, u] = edge
	c.paste(Image.fromarray(a.astype(np.uint8), "RGBA"))


def src(st, anim, d):
	base = os.path.join(PL, "states", st, st) if st else os.path.join(PL, "zip", "Idle")
	if anim == "__rot8__":   # ภาพหมุน 8 มุมของ State (pixellab_walk.py rot8 · ซ้าย → เข้ากล้อง → ขวา → หลัง) · ไม่ผ่าน clean (ภาพนิ่งไม่มีแสงวาดติด)
		order = ("west", "south-west", "south", "south-east", "east", "north-east", "north", "north-west")
		return [os.path.join(base, "rotations8", r + ".png") for r in order], None
	if anim == "__rot__":   # ภาพหมุนตัวจริง 4 มุมของ State (ซ้าย → หลัง → ขวา → หน้า) · ผืน 96 ตัวสูงเท่าภาพท่า (72)
		return [os.path.join(base, "rotations", r + ".png") for r in ("west", "north", "east", "south")], os.path.join(base, "rotations", d + ".png")
	return sorted(glob.glob(os.path.join(base, "animations", anim, d, "*.png"))), os.path.join(base, "rotations", d + ".png")


def clean(im, ref):
	a, r = np.array(im), np.array(ref)
	pal = np.unique(r[r[..., 3] > 127][:, :3], axis=0).astype(int)
	lum = lambda x: x[..., :3].astype(int) @ np.array([299, 587, 114]) // 1000
	hi = np.percentile(lum(r)[r[..., 3] > 127], 99) + 12
	px = a[..., :3].reshape(-1, 1, 3).astype(int)
	d = np.min(((px - pal[None]) ** 2).sum(-1), axis=1).reshape(a.shape[:2])
	body = a[..., 3] > 127
	far = body & ((d > 40 ** 2) | ((lum(a) > hi) & (d > 15 ** 2)))
	keep = body & ~far
	# เส้นฟาด/วงหมัด/ประกายสีขาวเทา สีตรงกับเสื้อขาว ลบด้วยสีไม่ได้ → ก้อนสีซีดที่รอบก้อนเป็นพื้นโปร่งเกินครึ่ง = เอฟเฟกต์ (เสื้อ/ใบมีดจริงมีเส้นขอบเข้มล้อม)
	rgb = a[..., :3].astype(int)
	pale = keep & (rgb.max(-1) - rgb.min(-1) < 40) & (lum(a) > 110)
	plab, pn = ndimage.label(pale)
	for i in range(1, pn + 1):
		comp = plab == i
		ring = ndimage.binary_dilation(comp) & ~comp
		if ring.sum() and (ring & ~keep).sum() / ring.sum() > 0.5:
			keep &= ~comp; far |= comp
	# ขอบน้ำเงินของเส้นฟาดสีฟ้า (สีตรงกับหมวก) → พิกเซลน้ำเงินที่ห่างเส้นฟาดสีฟ้าที่ลบไปแล้วไม่เกิน 2 จุด
	blue = keep & (rgb[..., 2] > rgb[..., 0] + 50) & (rgb[..., 2] > rgb[..., 1] + 20)
	cyan = far & (rgb[..., 1] > 150) & (rgb[..., 2] > 200) & (rgb[..., 0] < 170)   # เฉพาะเส้นฟาดสีฟ้า (แว่นทองที่ถูกลบในเดินขึ้นไม่นับ · ไม่งั้นกินขอบหมวก)
	edge = blue & ndimage.binary_dilation(cyan, iterations=2)
	keep &= ~edge; far |= edge
	lab, n = ndimage.label(keep)
	if n > 1:
		sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
		big = lab == 1 + int(np.argmax(sz))
		near = ndimage.binary_dilation(big, iterations=2)
		ids = {int(i) for i in np.unique(lab[near]) if i}
		keep = np.isin(lab, list(ids))
	out = a.copy(); out[~keep] = 0
	return Image.fromarray(out, "RGBA"), int(far.sum())


def main():
	shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
	clips, report, place, names_of = [], [], {}, {}
	for cid, th, st, anim, d, use, ms, loop in CLIPS:
		files, rot = src(st, anim, d)
		if not files:
			print("ไม่มีภาพ", cid); continue
		ims = [Image.open(f).convert("RGBA") for f in files]
		if use: ims = [ims[i] for i in use]
		if rot is None:
			cl = [(im, 0) for im in ims]
		else:
			ref = Image.open(rot).convert("RGBA")
			cl = [clean(im if im.size == ref.size else im, ref if im.size == ref.size else ref.resize(im.size)) for im in ims]
		ims = [c[0] for c in cl]; removed = sum(c[1] for c in cl)
		bb = [im.getchannel("A").getbbox() for im in ims]
		x0, y1 = min(b[0] for b in bb), max(b[3] for b in bb)
		names = []
		place[cid] = (30 - x0 + max(0, (60 - (max(b[2] for b in bb) - x0)) // 2), 108 - y1)
		if cid in ALIGN_MATCH:
			rc, ri, mi = ALIGN_MATCH[cid]
			rn = names_of[rc][ri]
			place[cid] = match_at(ims[mi], os.path.join(OUT, rn + ".png"))
		for i, im in enumerate(ims):
			at = place[cid]
			if cid in ALIGN_X:
				at = (place[ALIGN_X[cid]][0], at[1])
			if cid in ALIGN_BLEND:
				(ax, ay), (bx, by), u = place[ALIGN_BLEND[cid][0]], place[ALIGN_BLEND[cid][1]], i / max(1, len(ims) - 1)
				at = (round(ax + (bx - ax) * u), round(ay + (by - ay) * u))
			if min(at) < 0 or at[0] + im.width > 120 or at[1] + im.height > 112:   # ผืนดิบใหญ่กว่า 120x112 (ท่ากลาง) → วางบนผืนใหญ่แล้วตัดเฉพาะกรอบ
				big = Image.new("RGBA", (im.width + 400, im.height + 400)); big.alpha_composite(im, (at[0] + 200, at[1] + 200)); c = big.crop((200, 200, 320, 312))
			else:
				c = Image.new("RGBA", (120, 112)); c.alpha_composite(im, at)
			n = f"{cid}_{i}"; c.save(os.path.join(OUT, n + ".png")); names.append(n)
		for (bc, bi), spec in BLADE.items():   # หลังบันทึกครบทั้งคลิป (ใช้สีจากเฟรมอื่นของคลิปเดียวกัน)
			if bc == cid and bi < len(names):
				f = os.path.join(OUT, f"{cid}_{bi}.png"); c = Image.open(f).convert("RGBA"); draw_blade(c, *spec); c.save(f)
		for (bc, bi), (ri, sh, clr, sb) in BLADE_COPY.items():
			if bc == cid and max(bi, ri) < len(names): copy_blade(os.path.join(OUT, f"{cid}_{bi}.png"), os.path.join(OUT, f"{cid}_{ri}.png"), sh, clr, sb)
		clips.append({"group": G, "id": cid, "label": f"{th} · {len(names)} เฟรม (PixelLab · ลบแสงที่วาดติดมา {removed} จุด)", "frames": names, "ms": ms,
			"loop": loop, "w": 120, "travel": 0, "src": [f"pixellab {st or 'base'} {anim} {d}"]})
		report.append((cid, len(names), removed)); names_of[cid] = names
	json.dump({"_doc": "ชุด Rion ในเกมจาก PixelLab · tools/sprites/pixellab_rion_set.py · ร่าง ยังไม่เข้าเกม", "clips": clips},
		open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	for r in report: print(*r)
	import weapon_swap; weapon_swap.main(); weapon_swap.empty_hand()
	import shadow_knife; shadow_knife.main()   # มีดเงา bl6: ย้อมมีดมือซ้ายของท่าสองมีด (ต้องรันกับภาพที่เพิ่งสร้าง ไม่ใช่ภาพที่ย้อมแล้ว)   # คลิปเปลี่ยนอาวุธด้วยโค้ด (ใช้ภาพ pls_atk_bl ที่เพิ่งสร้าง) · ภาพมือเปล่าของผ่าเกราะ bl8


if __name__ == "__main__":
	main()
