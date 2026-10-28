"""Rion master v2 → PixelLab (API v2) → ท่าเดิน 4 ทิศ · kwan 18 ต.ค. 2026 "ถ้าใช้ pixellab จบไหม" → เลือก "1" ใส่คีย์ทดลอง

คีย์อ่านจาก env PIXELLAB_API_KEY เท่านั้น (ห้ามใส่ใน repo/แชท) · ทุกคำสั่งที่เสียเครดิตพิมพ์ยอดคงเหลือก่อน-หลัง
ขั้น:
  python3 tools/sprites/pixellab_walk.py ref          ทำภาพอ้างอิงหันหน้า (ไม่ต่อเน็ต · ไม่เสียเครดิต)
  python3 tools/sprites/pixellab_walk.py balance      ดูยอดคงเหลือ
  python3 tools/sprites/pixellab_walk.py character    สร้างตัวละครจากภาพอ้างอิง 4 ทิศ (/create-character-v3 · ~ceil(w*h*4/65536) gen)
  python3 tools/sprites/pixellab_walk.py walk [ทิศ…]  ท่าเดินของตัวละครที่สร้างแล้ว (ค่าเริ่ม east · /characters/animations)
  python3 tools/sprites/pixellab_walk.py prompt <ท่า> [ทิศ]  พิมพ์คำสั่งเต็มก่อนเสียเครดิต (ท่าใน MOVES)
  python3 tools/sprites/pixellab_walk.py anim <ท่า> [ทิศ…]   **ท่าใหม่ใช้คำสั่งนี้เท่านั้น** (คำสั่งละเอียด 8 ส่วน · docs/art-bible/rion_hires/PIXELLAB_PROMPTS.md)
  python3 tools/sprites/pixellab_walk.py slash/slash2 [ทิศ]  คำสั่งแบบเก่าที่ใช้ไปแล้ว (เก็บไว้รันซ้ำตามบันทึก)
  python3 tools/sprites/pixellab_walk.py fetch        ดึง ZIP ของตัวละคร แตกภาพลง OUT
  python3 tools/sprites/pixellab_walk.py vfx <ชื่อ>    เอฟเฟกต์จาก VFX_SPECS (/vfx · lite ~1 gen · พิมพ์คำสั่งเต็ม + ราคาที่ PixelLab เสนอ) → OUT/vfx/<ชื่อ>/
  python3 tools/sprites/pixellab_walk.py state [ชื่อ]     สร้าง State จาก STATES (/create-character-state · ตัวเดิมเปลี่ยนท่า/ของในมือ ครบทุกทิศ) · fetch_state [ชื่อ] ดึงภาพ
  python3 tools/sprites/pixellab_walk.py rot8 <State>   State 4 ทิศ → v3 เติมมุมเฉียง = ภาพหมุน 8 มุม (rotations8/ · 2–9 gen)
  python3 tools/sprites/pixellab_walk.py page         ท่าเดินจาก ZIP → px/ (ผืนเดียวกับ rion_pack_px) ให้หน้า animation test
ผลทั้งหมดอยู่ใน assets/sprites/pixellab_draft/ (.gdignore · ร่าง ยังไม่เข้าเกม) · state.json เก็บ character_id / job id
"""
import base64
import io
import shutil
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
MASTER = os.path.join(ROOT, "docs/art-bible/rion_hires/rion_master_v2.png")
OUT = os.path.join(ROOT, "assets/sprites/pixellab_draft")
STATE = os.path.join(OUT, "state.json")
API = "https://api.pixellab.ai/v2"
REF_H, CANVAS = 72, 96   # ตัวสูงเท่า Rion ในเกม (rion_pack_px PX_H) · ผืนจัตุรัส เท้าชิดล่างเว้น 4
DESC = ("chibi boy hero, blue cap with brass goggles, messy brown hair, white short-sleeve collared shirt, blue necktie, "
	"blue knee-length shorts, brown backpack, white socks, brown boots, no wristwatch, 32-bit pixel art")
# ---- คำสั่งที่ใช้ไปแล้ว (เก็บไว้ให้รันซ้ำได้ตรงตามบันทึก · ห้ามใช้แบบนี้กับท่าใหม่) ----
# kwan 18 ต.ค.: "คุณต้องใส่คำสั่งให้ละเอียดที่สุด" → ท่าใหม่ใช้ MOVES + build_action() (กฎใน docs/art-bible/rion_hires/PIXELLAB_PROMPTS.md)
WALK_ACTION = "walking at a steady pace, arms swinging opposite to the legs, legs pass each other mid-step, body bobs slightly"
SEEDS = {"slash2": 27}
ACTIONS = {"walk": WALK_ACTION,
	"slash": "slashing with a small kitchen knife held in the front hand in every frame: raise the knife behind the shoulder, "
		"step forward and swing it down fast in an arc toward an enemy on the left, follow through, then recover to a ready stance",
	# รอบ 2 (kwan 18 ต.ค. "ลองอีกรอบ"): รอบแรกเฟรม 5–7 หมุนหันเข้ากล้อง + แทงตรง + ใบมีดยาว
	"slash2": "side view, the body stays facing LEFT in every frame and never turns toward the camera: nose, cap brim and toes point left, "
		"backpack on the right. A short small kitchen knife (blade about the length of the hand) stays in the front hand in every frame. "
		"Raise the knife up behind the shoulder, step forward with the front foot and slash it down in a curved arc in front of the body "
		"toward an enemy on the left, follow through low, then return to a ready stance still facing left"}

# ---- คำสั่งละเอียด 8 ส่วน (PIXELLAB_PROMPTS.md) ----
MASTER_MD = os.path.join(ROOT, "docs/art-bible/rion_hires/RION_MASTER.md")
DIR_BLOCK = {"west": "LEFT", "east": "RIGHT", "north": "BACK"}   # south = หน้าตรง (บล็อก "ภาพหน้าตรง" ไม่ใช้ เพราะบอกให้ยืนนิ่ง)
# ส่วนที่ต้องคงที่ทุกเฟรม (ข้อ 5) และสิ่งที่ห้ามทุกท่า (ข้อ 6) · ท่าเพิ่มของตัวเองได้ใน MOVES[ท่า]["not"]
KEEP = ("Keep identical in every frame: the whole cap is blue with the brass-gold goggles resting on its front, the brown backpack stays on the back, "
	"the blue necktie, the same head size and body height, the same proportions as the reference. Bare wrists, no wristwatch.")
NOT_ALWAYS = ["turning the body toward the camera unless this move says so", "a wristwatch", "extra characters", "ground, shadow, text or background",
	"large glowing effects, energy trails or speed lines (effects are added later in code)"]
MOMENTUM = ("Follow momentum: wind up while still moving, land the hit at the moment the weight comes down, "
	"let the follow-through carry forward, then settle. Never freeze in a held wind-up pose.")
# ท่า: dir = ทิศตั้งต้น · held = ของในมือ (None = มือว่าง) · beats = จังหวะ (≈ จำนวนเฟรม) · attack = ใส่หลักโมเมนตัม · not = ห้ามเพิ่ม · frames · seed
MOVES = {
	"walk": {"dir": "east", "held": None, "attack": False, "frames": 8, "seed": 18,
		"beats": [
			"contact: front heel touches the ground, back leg straight behind, arms swing opposite to the legs",
			"down: weight drops onto the front leg, knee bends slightly, body lowest",
			"passing: back leg swings forward past the standing leg, body rises, arms near the sides",
			"up: pushing off the toes of the standing leg, body highest",
			"contact with the other foot forward, arms swapped",
			"down on the other leg",
			"passing with the other leg",
			"up, ready to loop back to the first frame"],
		"not": ["both feet off the ground", "sliding feet"]},
	"slash": {"dir": "west", "attack": True, "frames": 8, "seed": 27,
		"held": "a short small kitchen knife, blade about the length of the hand, held by the handle in the front hand (the hand nearest the viewer)",
		"beats": [
			"ready stance facing left, knees slightly bent, knife held low in front",
			"step forward with the front foot while raising the knife back over the shoulder, blade pointing up and back",
			"wind-up at its peak behind the shoulder, body twisting back, weight on the back foot",
			"swing begins: arm comes forward over the head toward the left",
			"the knife slashes down in a curved arc in front of the body, front foot lands, weight shifts forward",
			"follow-through: knife low near the front knee, body leaning forward",
			"recover: pull the knife back up toward the chest",
			"back to the ready stance facing left, same as the first frame"],
		"not": ["the knife disappearing in any frame", "a second knife", "a long sword or dagger", "the knife sticking straight up above the cap"]},
}

# ท่ายากจาก State (kwan 19 ต.ค. "ลองท่ายากก่อน 2 ท่า ทุ่มข้ามไหล่กับเตะหมุนกลางอากาศ") · ไม่วาดศัตรู (โค้ดขยับมอนเอง)
WRAPS = "white cloth hand wraps wound around both hands and wrists (part of the hands, not a weapon)"
NO_FOE = ["an opponent or any second figure (the enemy is added later in code)", "a front view facing the camera"]
MOVES.update({
	"fs10_s": {"dir": "west", "held": WRAPS, "attack": True, "frames": 10, "seed": 31,
		"facing": ("It starts and ends facing LEFT. In frames 4-7 the body pivots half a turn so the back and the backpack face LEFT toward the enemy "
			"while the head looks back over the shoulder; it turns through a side view only and never shows a front view."),
		"beats": [
			"low fighting stance facing left, knees bent, wrapped fists up in front of the chest, same as the start image",
			"step the front foot forward to the left and reach both open hands forward at chest height, as if grabbing an enemy's collar and sleeve",
			"both hands close into gripping fists and pull back toward the chest, weight shifting onto the front foot",
			"pivot on the front foot: the body turns half a turn so the back and backpack now face LEFT, knees bent low, fists still gripping in front of the shoulder, head looking back over the shoulder",
			"hips drop low and push back to the left, both fists pulled down over the shoulder in front of the chest, loading the throw",
			"explosive throw: the legs straighten, the upper body bends forward and down toward the RIGHT, both arms whip down from over the shoulder to the knees",
			"follow-through: body bent forward deeply, both fists low near the ground on the right side, as if the enemy just slammed into the floor",
			"pivot back: the body turns half a turn back to face LEFT while rising",
			"settle into the low fighting stance facing left, knees bent",
			"low fighting stance facing left, same as the first frame"],
		"not": NO_FOE + ["the hand wraps disappearing", "a weapon"]},
	"fs12_s": {"dir": "west", "held": WRAPS, "attack": True, "frames": 12, "seed": 31,
		"facing": ("It starts and ends facing LEFT. In the air the body spins through a back view (back and backpack toward the camera) "
			"to face RIGHT for the kick, then unwinds through the back view to face LEFT again; it never shows a front view."),
		"beats": [
			"low fighting stance facing left, wrapped fists up, same as the start image",
			"crouch deeper, arms tucked to the chest, weight on both feet, ready to jump",
			"jump straight up off both feet, knees tucked under the body",
			"rising in the air and spinning: back and backpack toward the camera, arms pulled in tight",
			"top of the jump: the body now faces RIGHT, head looking back over the shoulder at the enemy on the left, kicking leg chambered with the knee bent",
			"spinning back kick: the leg shoots out straight to the LEFT at head height, heel first, body leaning away to the right, arms out for balance",
			"kick fully extended to the left at head height, body almost horizontal",
			"the leg pulls back in and the body unwinds through the back view",
			"facing LEFT again, dropping down, knees bent under the body",
			"landing on both feet, knees bending deep to absorb the fall",
			"rising out of the landing",
			"low fighting stance facing left, same as the first frame"],
		"not": NO_FOE + ["the hand wraps disappearing", "a weapon", "both legs kicking at once"]},
})

# ท่าต้นไม้ 17 ท่า × 6 สาย (102 ท่า · tools/sprites/pixellab_skills.py) — ใช้คำสั่งเดียวกัน: prompt <รหัสท่า> · anim <รหัสท่า>
try:
	import csv as _csv
	import pixellab_skills as _sk
	MOVES.update(_sk.skill_moves(list(_csv.DictReader(open(os.path.join(ROOT, "docs/design/skill_trees_17.csv"), encoding="utf-8")))))
except (ImportError, FileNotFoundError):
	pass


# ชุด Rion ในเกม (kwan 19 ต.ค. เลือก "เปลี่ยนเป็น PixelLab ทั้งชุด" · docs/art-bible/pixellab_test/ASSET_LIBRARY_PLAN.md ลำดับ 1)
# ยืนในศึก 6 สาย = State ท่าสู้ (fight_knife · <สาย>_A_stance) + ท่าหายใจ 4 เฟรม · โดนตี/ล้ม = จาก fight_knife · โจมตีพื้นฐาน = ท่าราก bl0 bt0 pt0 rg0 dv0 fs0 จาก State สายนั้น
GAME_STATE = {"bl0": "fight_knife", "bt0": "BT_A_stance", "pt0": "PT_A_stance", "rg0": "RG_A_stance", "dv0": "DV_A_stance", "fs0": "FS_A_stance"}
KNIFE = "a short small kitchen knife, blade about the length of the hand, held by the handle in the RIGHT hand (the same hand as in the start image) in every frame; it never passes to the other hand"   # เดิม "front hand" = มือซ้ายเมื่อหันซ้าย ขัดกับภาพ State (kwan 19 ต.ค.)
MOVES.update({
	"hurt_k": {"dir": "west", "held": KNIFE, "attack": False, "frames": 6, "seed": 33,
		"beats": ["struck from the front (the enemy is on the left): the body jerks back to the RIGHT, eyes squeezed shut, the knife still gripped",
			"the biggest recoil: leaning back to the right, knees bending, arms flung back a little",
			"stagger one small step back to the right",
			"regain balance, body upright again",
			"raise the knife back to the ready position",
			"fighting stance facing left, same as the start image"],
		"not": ["dropping the knife", "falling down", "blood"]},
	# ตั้งรับ (kwan 21 ต.ค. "ให้มอนโจมตีกลับ (Rion โดนตี ตั้งรับ)") · ศัตรูอยู่ทางซ้าย · แรงกระแทกจากซ้าย ดันตัวถอยขวาเล็กน้อย การ์ดไม่หลุด
	"guard_k": {"dir": "west", "held": KNIFE, "attack": False, "frames": 8, "seed": 33,
		"beats": ["fighting stance facing left, same as the start image",
			"seeing the attack coming from the LEFT: the near left forearm rises in front of the face, the knife in the far right hand comes up across the chest, blade pointing up-left",
			"full guard: knees bent low, weight on the front foot, near left forearm shielding the face, knife held across in front of the chest, chin tucked down",
			"holding the braced guard, same pose as the previous frame, eyes narrowed",
			"absorbing the impact: the whole body is pushed back to the RIGHT a few pixels, feet sliding, the guard stays up, teeth gritted",
			"still braced after the push, knees deep, guard up",
			"lowering the near forearm, the knife coming back to the ready position",
			"fighting stance facing left, same as the first frame"],
		"not": ["turning toward the camera", "turning the back to the enemy", "dropping the knife", "a second knife", "a shield", "swinging or stabbing with the knife", "slash trails or motion lines", "sparks or impact effects", "falling down"]},
	# รอบ 2 (guard_k รอบแรก: เฟรม 2–3 วาดประกายกระแทก · 4–7 หันขวา/มีดหาย) → ท่าค้างสั้น 4 เฟรม ไม่มีจังหวะโดน (แรงกระแทก/ถอยทำด้วยโค้ด)
	"guard2_k": {"dir": "west", "held": KNIFE, "attack": False, "frames": 4, "seed": 41,
		"beats": ["fighting stance facing left, same as the start image",
			"dropping into a low guard: knees bend deep, hips low, the knife in the far right hand raised vertically in front of the face with the blade pointing UP, the near left fist pressed against the chest, head tucked behind the blade, eyes looking LEFT",
			"holding the same low guard pose as the previous frame, a little more crouched, jaw clenched",
			"holding the same low guard pose, identical to the previous frame"],
		"not": ["turning toward the camera", "turning the back to the enemy", "facing right", "dropping the knife", "a second knife", "a shield", "swinging or stabbing with the knife", "slash trails or motion lines", "sparks, stars or impact effects", "white flashes"]},
	"run_k": {"dir": "west", "held": KNIFE, "attack": False, "frames": 8, "seed": 33,
		"beats": ["running to the LEFT, right foot (far leg) planted under the body, left knee (near leg) driving forward, body leaning forward, knife held low at guard in front of the chest",
			"push off: the far leg pushes back, the near foot reaching forward, both feet almost off the ground, knife still at guard",
			"airborne moment of the run: both feet off the ground, near leg forward, far leg back, body leaning forward",
			"near foot (left) lands under the body, knee bending to absorb, body dips one pixel, knife steady",
			"far knee (right) drives forward past the planted leg, body upright-forward",
			"push off from the near leg, far foot reaching forward",
			"airborne moment again: far leg forward, near leg back",
			"far foot lands under the body, knee bending, same as the first frame (ready to loop)"],
		"not": ["turning toward the camera", "a second knife", "slash trails or motion lines", "swinging the knife", "dust clouds"]},
	# ฟันมือเปล่ากำหมัด (kwan 20 ต.ค. "1 มาครับ ขอดูฝีมือ"): search_help ของ PixelLab แนะนำเจนมือเปล่าแล้ววางอาวุธด้วยโค้ด (คำสั่งข้อความคุมมือไม่ได้แน่นอน)
	# ท่าเดียวกับ bl0 รอบ 2 · กำปั้นขวา (แขนไกล) ต้องเห็นทุกเฟรม = จุดวางด้ามอาวุธ · ทดลองวางมีดครัว SL01 · มีดสับ SL02 · เคียว SL08
	"slash_fist": {"dir": "west", "held": ("nothing: both hands are bare and empty, no weapon, no glove, no tool; the RIGHT hand (the far arm) is a tight closed fist "
			"as if gripping a short handle, the knuckles facing forward, and that fist stays closed and clearly visible in every frame; "
			"the near LEFT arm stays bent with its empty fist low at the chest and never covers the face"), "attack": True, "frames": 8, "seed": 27,
		"beats": ["ready stance facing left, knees bent, the far right fist held low in front of the belly, the near left fist at the chest",
			"step forward with the front foot, the far right arm lifts the closed fist back over the right shoulder, the near left fist stays at the chest",
			"wind-up peak: the far right fist is high behind the right shoulder above the cap, elbow bent, still a closed fist",
			"the far right arm swings the closed fist forward over the head and down toward the left",
			"the far right fist chops diagonally down in front of the body at chest height as the front foot lands, arm extended toward the left",
			"follow-through: the far right fist low beside the front knee, body leaning forward, near left fist still at the chest",
			"pull the far right fist back up toward the belly, rising",
			"ready stance again facing left, same as the first frame"],
		"not": ["any weapon, knife, stick or tool in either hand", "gloves or wraps on the hands", "an open hand or spread fingers on the right hand",
			"the fist switching to the other arm", "the empty left hand raised in front of the face", "slash trails, motion lines, sparkles or glowing effects",
			"turning toward the camera"]},
	# ท่ากลางของการเกิดประกาย (kwan 21 ต.ค. "1 เจนภาพท่ากลาง"): ภาพเริ่ม = bl0_v2 เฟรม 4 (ง้างมีดข้ามไหล่ขวาสุด) · ภาพจบ = bl1_v2 เฟรม 3 (ย่อต่ำ มีดต่ำข้างสะโพก)
	#   PL_STATE=fight_knife PL_START_IMG=<bl0_v2/west/frame_004> PL_END_IMG=<bl1_v2/west/frame_003> anim glim_shift west
	"glim_shift": {"dir": "west", "held": KNIFE, "attack": False, "frames": 4, "seed": 27,
		"beats": ["same as the start image: wind-up with the knife raised over the right shoulder in the far right hand, the near left fist at the chest; he changes his mind and the far right arm starts to lower the knife down behind the body, knees start to bend",
			"the far right hand brings the knife down past the right side of the chest toward the hip, the blade still visible, the near left fist stays at the chest in front of the shirt, knees bending deeper, weight shifting onto the back foot",
			"crouching lower, the far right hand holds the knife low beside the right hip pointing forward, the near left fist at the chest, body leaning forward ready to spring",
			"same as the end image: deep crouch, knife low beside the hip in the far right hand pointing forward, near left fist at the chest, ready to lunge"],
		"not": ["switching the knife to the near left hand", "the near left arm covering the face", "turning toward the camera", "a second knife", "slash trails, motion lines, sparkles or glow"]},
	# ตัดเอ็น bl7 ช่วงถอยแบบกาลี (kwan 21 ต.ค.): bl7_v เฟรม 5–7 ยังเดินหน้า ไม่ถอย → เจนแยกด้วย end_frame: ภาพเริ่ม bl7_v เฟรม 5 (ปาดสุด) → ภาพจบ bl7_v เฟรม 0 (ตั้งการ์ด)
	#   PL_STATE=fight_knife PL_START_IMG=<bl7_v/west/frame_005> PL_END_IMG=<bl7_v/west/frame_000> anim bl7_back west
	"bl7_back": {"dir": "west", "held": KNIFE, "attack": False, "frames": 4, "seed": 27,
		"beats": ["same as the start image: the far right arm extended forward with the knife after the slash, the near left fist at the chest; the back foot starts to step backward, body still facing left",
			"first short step back: the back foot lands behind, weight shifts back, the far right hand circles the knife back toward the chest, the near left fist at the chest, still facing left toward the enemy",
			"second short step back: the front foot slides back, knees bent, the knife at guard in front of the chest in the far right hand, near left fist at the chest",
			"same as the end image: low fighting stance facing left, knife at guard in the far right hand"],
		"not": ["walking forward", "turning around or showing the back", "switching the knife to the near left hand", "a second knife", "sparkles, slash trails, motion lines or glow"]},
	"hop_k": {"dir": "west", "held": KNIFE, "attack": False, "frames": 8, "seed": 33,
		"beats": ["fighting stance facing left, knife held at guard in front of the chest, same as the start image",
			"crouch to jump backward: both knees bend deep, hips drop, upper body leans slightly back to the RIGHT, knife still at guard",
			"push off backward: the legs straighten and drive the body up and to the RIGHT, toes leaving the ground last, body leaning back to the right",
			"in the air moving backward to the right: knees tucked up under the body, feet off the ground, head and knife still facing LEFT toward the enemy",
			"falling: the legs reach down toward the ground, the far foot slightly behind, knife at guard",
			"landing: feet touch the ground, knees bend deep to absorb the fall, body dips, the free hand out a little for balance",
			"rising out of the landing, knees still a little bent, knife at guard",
			"fighting stance facing left, same as the first frame"],
		"not": ["turning toward the camera", "turning the back to the enemy", "a second knife", "slash trails or motion lines", "dust clouds", "swinging the knife"]},
	"ko_k": {"dir": "west", "held": "the same short kitchen knife; it slips out of the right hand in frame 4 and then lies on the ground beside the body", "attack": False, "frames": 8, "seed": 33,
		"beats": ["struck hard from the front: body jerks back to the RIGHT, eyes squeezed shut",
			"knees buckle, body sagging",
			"dropping onto both knees, head lolling",
			"falling backward to the RIGHT, the knife slipping out of the hand",
			"landing flat on the back, lying on the ground with the head to the right and feet to the left",
			"a small bounce of the body on the ground",
			"lying still on the back, eyes closed (swirly dizzy eyes are fine)",
			"lying still, same as the previous frame"],
		"not": ["blood", "the body turning to face the camera before landing"]},
})
for _r, _st in GAME_STATE.items():
	MOVES["idle_" + _r[:2]] = {"dir": "west", "held": MOVES[_r]["held"] if _r in MOVES else KNIFE, "attack": False, "frames": 4, "seed": 33,
		"beats": ["fighting stance facing left, same as the start image",
			"breathe in: chest rises one pixel, shoulders lift slightly, the held item bobs up slightly",
			"breathe out: chest and shoulders come back down",
			"fighting stance, same as the first frame (ready to loop)"],
		"not": ["stepping", "turning", "swinging the held item"]}


def master_blocks():
	"""อ่านบล็อกจาก RION_MASTER.md ตามตัวอักษร: CHARACTER · STYLE · LEFT/RIGHT/BACK"""
	t = open(MASTER_MD, encoding="utf-8").read()
	def code_after(head):
		i = t.index(head)
		a = t.index("```", i) + 3
		return " ".join(t[a:t.index("```", a)].split())
	out = {"CHARACTER": code_after("### ตัวละคร (CHARACTER)"), "STYLE": code_after("### สไตล์ (STYLE)")}
	for line in t.splitlines():
		for k in ("LEFT", "RIGHT", "BACK"):
			if line.startswith(k + ":"):
				out[k] = line[len(k) + 1:].strip()
	return out


def build_action(move, d):
	"""ประกอบ action_description 8 ส่วน · ส่วน 7–8 (CHARACTER + STYLE) ส่งเป็น description แยก (ดู build_description)"""
	m, mb = MOVES[move], master_blocks()
	parts = []
	if m.get("facing"):   # ท่าที่ต้องหันหลังให้เป้ากลางท่า (ทุ่ม/เตะหมุน) เขียนทิศเอง
		parts.append(mb[DIR_BLOCK[d]] + " " + m["facing"])
	elif d in DIR_BLOCK:
		parts.append(mb[DIR_BLOCK[d]] + " The body keeps this exact facing in every frame and never turns toward the camera.")
	else:
		parts.append("Front view facing the viewer in every frame.")
	if m.get("held_free"):   # ของในมือเปลี่ยนกลางท่า (เช่น เสกมีดเล่มที่สอง) → เขียนเองทั้งประโยค
		parts.append("Held items: " + m["held"])
	elif m["held"]:
		where = "both hands" if "BOTH hands" in m["held"] else "that same hand"   # ไม้เบสบอลจับสองมือ
		parts.append("Held item: " + m["held"] + ". It stays in " + where + " in every frame, never disappears, and there is never a second one.")
	else:
		parts.append("Both hands are empty in every frame.")
	parts.append(f"The animation is {m['frames']} frames, one beat per frame: "
		+ " ".join(f"{i + 1}) {b}." for i, b in enumerate(m["beats"])))
	if m["attack"]:
		parts.append(MOMENTUM)
	parts.append(KEEP)
	parts.append("Do NOT draw: " + "; ".join(NOT_ALWAYS + m.get("not", [])) + ".")
	return " ".join(parts)


def build_description():
	mb = master_blocks()
	return mb["CHARACTER"] + " " + mb["STYLE"]


def show_prompt(move, d=None):
	d = d or MOVES[move]["dir"]
	a, desc = build_action(move, d), build_description()
	print(f"ท่า {move} · ทิศ {d} · seed {MOVES[move]['seed']} · เฟรม {MOVES[move]['frames']}")
	print(f"\n[description {len(desc)} ตัวอักษร]\n{desc}\n\n[action_description {len(a)} ตัวอักษร]\n{a}")
	if len(desc) > 2000:
		sys.exit("description เกิน 2000 ตัวอักษร (ขีดจำกัด API)")


def key_green(rgb):
	r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
	return ~((g > 140) & (g > r + 60) & (g > b + 60))


def make_ref():
	"""master (พื้นเขียว 1438x2576) → ตัดพื้น → ย่อ BOX ให้ตัวสูง REF_H → ผืน CANVAS พื้นโปร่ง"""
	rgb = np.array(Image.open(MASTER).convert("RGB")).astype(int)
	m = key_green(rgb)
	ys, xs = np.nonzero(m)
	crop = np.dstack([rgb, m * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
	k = REF_H / crop.shape[0]
	im = Image.fromarray(crop, "RGBA")
	pre = np.array(im).astype(float)
	pre[..., :3] *= pre[..., 3:] / 255
	w = max(1, round(crop.shape[1] * k))
	sm = np.array(Image.fromarray(pre.astype(np.uint8), "RGBA").resize((w, REF_H), Image.BOX)).astype(float)
	A = sm[..., 3] / 255
	rgb2 = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	out = np.zeros((CANVAS, CANVAS, 4), np.uint8)
	x0, y0 = (CANVAS - w) // 2, CANVAS - 4 - REF_H
	out[y0:y0 + REF_H, x0:x0 + w, :3] = rgb2
	out[y0:y0 + REF_H, x0:x0 + w, 3] = np.where(A > .5, 255, 0)
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	p = os.path.join(OUT, "ref_south.png")
	Image.fromarray(out, "RGBA").save(p)
	print("ภาพอ้างอิง", p, out.shape[1], "x", out.shape[0], "ตัวสูง", REF_H)
	return p


def key():
	k = os.environ.get("PIXELLAB_API_KEY", "")
	if not k:
		sys.exit("ไม่มี PIXELLAB_API_KEY ใน session นี้ (ตั้งในหน้าตั้งค่า environment แล้วเปิด session ใหม่)")
	return k


def call(method, path, body=None, raw=False):
	req = urllib.request.Request(API + path, method=method,
		data=json.dumps(body).encode() if body is not None else None,
		headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json"})
	# proxy ของ session ตัดการเชื่อมต่อบ่อย · URLError = หลุดก่อนส่งคำขอครบ ลองใหม่ได้ไม่เสียเครดิตซ้ำ
	for i in range(5):
		try:
			with urllib.request.urlopen(req, timeout=120) as r:
				data = r.read()
			break
		except urllib.error.HTTPError as e:
			sys.exit(f"{method} {path} → HTTP {e.code}: {e.read().decode()[:2000]}")
		except urllib.error.URLError as e:
			print(f"  เน็ตหลุด ({e.reason}) ลองใหม่ครั้งที่ {i + 1}", flush=True)
			time.sleep(2 ** (i + 1))
	else:
		sys.exit(f"{method} {path} → เชื่อมต่อไม่ได้ 5 ครั้ง")
	return data if raw else json.loads(data)


def state():
	return json.load(open(STATE)) if os.path.isfile(STATE) else {}


def save_state(s):
	json.dump(s, open(STATE, "w"), indent=1, ensure_ascii=False)


def balance():
	b = call("GET", "/balance")
	print("ยอดคงเหลือ", json.dumps(b, ensure_ascii=False))
	return b


def wait(job_id, label):
	t0 = time.time()
	while True:
		j = call("GET", f"/background-jobs/{job_id}")
		st = j.get("status")
		print(f"  {label} {st} {int(time.time() - t0)} วิ", flush=True)
		if st in ("completed", "failed"):
			return j
		time.sleep(10)


def b64(path):
	return {"type": "base64", "base64": base64.b64encode(open(path, "rb").read()).decode(), "format": "png"}


def character():
	ref = os.path.join(OUT, "ref_south.png")
	if not os.path.isfile(ref):
		make_ref()
	balance()
	r = call("POST", "/create-character-v3", {"description": DESC, "name": "Rion master v2", "reference_image": b64(ref),
		"n_directions": 4, "view": "low top-down", "no_background": True, "seed": 18})
	s = state()
	s.update(character_id=r["character_id"], character_job=r.get("background_job_id"), character_usage=r.get("usage"))
	save_state(s)
	print("character_id", r["character_id"], "ค่าใช้", r.get("usage"))
	if r.get("background_job_id"):
		j = wait(r["background_job_id"], "สร้างตัวละคร")
		s["character_status"] = j.get("status")
		save_state(s)
	balance()


def walk(dirs, name="walk"):
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	balance()
	r = call("POST", "/characters/animations", {"character_id": s["character_id"], "animation_name": name,
		"mode": "v3", "action_description": ACTIONS[name], "frame_count": 8, "keep_first_frame": False, "directions": dirs, "seed": SEEDS.get(name, 18)})
	s.setdefault(name, []).append(r)
	save_state(s)
	print(json.dumps(r, ensure_ascii=False)[:800])
	for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
		j = wait(jid, name)
		s.setdefault(name + "_jobs", {})[jid] = j.get("status")
		save_state(s)
	balance()


def anim(move, dirs=None):
	"""ท่าใหม่ทุกท่าใช้ทางนี้: คำสั่ง 8 ส่วนจาก MOVES · description = CHARACTER + STYLE ของ RION_MASTER ตามตัวอักษร"""
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	m = MOVES[move]
	dirs = dirs or [m["dir"]]
	# PL_STATE=<ชื่อ State> = ท่าขยับของตัว State (ภาพเริ่ม = ท่าของ State) · PL_START=<ชื่อ State> = ใช้ภาพทิศเดียวกันของ State นั้นเป็นภาพเริ่ม
	cid = s["states"][os.environ["PL_STATE"]]["response"]["character_id"] if os.environ.get("PL_STATE") else s["character_id"]
	balance()
	for d in dirs:
		show_prompt(move, d)
		body = {"character_id": cid, "animation_name": f"{move}_v" + os.environ.get("PL_SUFFIX", ""), "mode": "v3",
			"description": build_description(), "action_description": build_action(move, d),
			"frame_count": m["frames"], "keep_first_frame": False, "directions": [d], "seed": m["seed"]}
		if os.environ.get("PL_START"):
			n = os.environ["PL_START"]
			body["custom_start_frame"] = b64(os.path.join(OUT, "states", n, n, "rotations", d + ".png"))
		# ท่ากลางระหว่างสองภาพ (interpolation · kwan 21 ต.ค. "เจนภาพท่ากลาง"): PL_START_IMG / PL_END_IMG = ไฟล์ภาพดิบขนาดเดียวกัน (ภาพจบเปิดโหมด end_frame)
		if os.environ.get("PL_START_IMG"):
			body["custom_start_frame"] = b64(os.environ["PL_START_IMG"])
		if os.environ.get("PL_END_IMG"):
			body["end_frame"] = b64(os.environ["PL_END_IMG"])
		r = call("POST", "/characters/animations", body)
		s.setdefault("anim", []).append({"move": move, "dir": d, "seed": m["seed"], "state": os.environ.get("PL_STATE"),
			"start": os.environ.get("PL_START"), "response": r})
		save_state(s)
		for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
			j = wait(jid, f"{move} {d}")
			s.setdefault("anim_jobs", {})[jid] = j.get("status")
			save_state(s)
	balance()


def fetch():
	s = state()
	data = call("GET", f"/characters/{s['character_id']}/zip", raw=True)
	z = zipfile.ZipFile(io.BytesIO(data))
	dst = os.path.join(OUT, "zip")
	os.makedirs(dst, exist_ok=True)
	z.extractall(dst)
	names = [n for n in z.namelist() if n.lower().endswith(".png")]
	print("แตก", len(names), "ภาพ →", dst)
	for n in sorted(names)[:40]:
		print(" ", n, Image.open(os.path.join(dst, n)).size)


# ---- State (kwan 18 ต.ค. คลิป "PixelLab Character States" → เลือก "2" สร้าง State อย่างเดียวก่อน) ----
# State = ตัวละครเดิมเปลี่ยนท่า/ของในมือ ครบทุกทิศ (/create-character-state) · ใช้เป็นภาพเริ่มของท่าถัดไป (keep_first_frame) แทนภาพยืนมือเปล่า
# ซึ่งเป็นต้นเหตุที่มีดหาย/ตัวหันเข้ากล้องในท่ายาว · ผลเป็น character_id ใหม่ (กลุ่มเดียวกับตัวเดิม) เก็บใน state.json["states"][ชื่อ]
STATES = {
	"fight_knife": {"seed": 27, "frame": None, "edit": (   # ผืน 112 = อย่างน้อย 15 gen (402 · 18 ต.ค.) → ผืนเดิม 96
		"Same character, same design, same proportions and same colors; only the pose changes. "
		"Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, both feet flat on the ground. "
		"The FRONT hand holds ONE small kitchen knife: short dark wooden handle in the fist, short silver blade about as long as the hand, "
		"blade pointing forward and slightly up, held at chest height in front of the body. The back hand is a loose fist near the chest. "
		"Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack with two side pockets "
		"on the back, blue shorts, white socks and brown boots exactly as in the source. "
		"In side views the character stays in a true side view facing the same direction as the source rotation, never turned toward the camera. "
		"No second knife, no sword, no glow, no slash trail, no motion lines, no shadow, no ground, no background, no text.")},
}

try:   # State ท่าตัวของต้นไม้ 17 ท่า × 6 สาย (pixellab_states17.py · รายการให้ kwan ตรวจ docs/design/STATE_POSES_17.md) · SL_A_stance = fight_knife ที่ทำแล้ว
	from pixellab_states17 import STATES17 as _S17
	STATES.update({k: v for k, v in _S17.items() if k != "SL_A_stance"})
except ImportError:
	pass


# สายทุบ = ไม้เบสบอล (weapons.csv CR-1..5 · ภาพเดิม BT_A_stance ถือค้อนไม่ตรงอาวุธในเกม) · kwan 25 ต.ค. "ทื่อมาก ลองเจน pixellab มาเทียบ" (เทียบกับภาพ Flow ใน tests/lab/flw_bt0)
BAT = ("an aluminum baseball bat, silver-gray metal with a dark grip tape handle and a small knob at the end, about as long as the character's arm and shoulder together, "
	"gripped with BOTH hands together on the handle near the knob, the RIGHT hand above the LEFT hand, in every frame; it is never held with one hand, never thrown, never disappears")
STATES["BT_bat_stance"] = {"seed": 27, "frame": None, "edit": (   # edit_description ≤ 1000 ตัวอักษร (API)
	"Same character, same design, proportions and colors; only the pose and the held item change. "
	"Keep the blue cap with brass goggles, brown hair, white shirt, blue necktie, brown belt, brown backpack, blue shorts, white socks, brown boots. "
	"True side view facing the same direction as the source rotation, never turned toward the camera. "
	"Held item: an aluminum baseball bat, silver-gray with a dark grip handle, about as long as the arm, gripped with BOTH hands together on the handle. "
	"Pose: battle-ready stance, knees slightly bent, feet apart; both hands hold the handle at chest height and the bat rests back on the shoulder, "
	"pointing up and back at 45 degrees behind the head. "
	"No other weapon, no hammer, no glow, no motion lines, no shadow, no ground, no background, no text.")}
MOVES["bt0_bat"] = {"dir": "west", "held": BAT, "attack": True, "frames": 10, "seed": 27,
	"beats": [
		"ready stance facing left, both hands on the bat handle at chest height, the bat resting back on the shoulder pointing up and back, same as the start image",
		"small step forward with the front foot while both hands lift the bat off the shoulder, bat pointing straight up behind the head",
		"wind-up peak: both hands high behind the head, the bat pointing up and back, body leaning back, weight on the back foot",
		"the swing starts: both arms pull forward over the head, the bat vertical above the cap",
		"the bat swings down in front of the body, pointing forward and up at 45 degrees, the front foot stepping forward to the left",
		"impact: both arms extended forward to the left, the bat level and pointing LEFT at waist height, front knee bent, body leaning into the hit",
		"follow-through: the bat keeps going down, its tip near the ground in front of the front foot, body bent forward from the force",
		"recover: straighten up, both hands pulling the bat back toward the chest, bat diagonal across the front of the body",
		"lift the bat back up onto the shoulder with both hands",
		"ready stance facing left, same as the first frame"],
	"not": ["a hammer", "a sword or knife", "holding the bat with one hand", "letting go of the bat", "a second bat", "the bat bending or changing length",
		"swing trails, motion arcs or speed lines", "impact stars or sparks", "an opponent or any second figure"]}

# รอบ 2 (kwan 25 ต.ค. "ใช้ pixellab ปรับให้ตรงกับรายงาน ... สีหน้ามีอารมณ์มากกว่า flow หลังโจมตีให้ถอยแบบฟัน"): bt0_bat ได้หวดแนวนอนระดับอก + ตัวหันเข้ากล้อง
# → ตามรายงานวิจัย bt0: load หลังไหล่ขวา ข้อศอกสูง → ก้าวสั้น → ฟาดลงเฉียง 60–70° → กระทบลำตัวตั้งตรงไม่ก้ม → ไม้จมค้าง (ถอยใช้ hop_bat แบบท่าฟัน bl0)
MOVES["bt0_bat2"] = {"dir": "west", "held": BAT, "attack": True, "frames": 8, "seed": 31,
	"beats": [
		"ready stance facing left, both hands on the bat handle at chest height, the bat resting back on the shoulder, same as the start image",
		"load: weight shifts onto the back foot, both hands lift the bat higher behind the right shoulder, the bat pointing straight UP and slightly back, both elbows raised high, eyes narrowed at the enemy",
		"load peak: hips coiled, both hands high beside the back of the head, the bat pointing UP behind the head, the front foot lifting a little off the ground, jaw clenched",
		"stride: the front foot steps forward to the LEFT and lands, the bat still held high above the head, pointing straight up",
		"the downswing begins: both arms pull forward over the cap, the bat tilting forward, its tip pointing up and to the LEFT at 45 degrees, mouth open shouting",
		"impact: the bat comes DOWN at a steep diagonal, both arms extended forward and down, the bat barrel pointing DOWN-LEFT about 60 degrees below horizontal toward a target at waist height in front, front foot planted flat, torso upright and tense, not bending forward, mouth open shouting",
		"hold the impact pose: the bat stays sunk at the same down-left angle, torso upright, teeth gritted, eyes fierce",
		"same impact pose held, breathing hard, still facing left"],
	"not": ["a hammer", "a sword or knife", "holding the bat with one hand", "letting go of the bat", "a second bat", "the bat bending or changing length",
		"a level horizontal swing at chest height", "the torso bending forward", "turning the chest or the necktie toward the camera", "a front view",
		"swing trails, motion arcs or speed lines", "impact stars or sparks", "an opponent or any second figure"]}
MOVES["hop_bat"] = {"dir": "west", "held": BAT, "attack": False, "frames": 8, "seed": 33,
	"beats": [b.replace("knife held at guard in front of the chest", "both hands holding the bat at guard, the bat diagonal in front of the chest pointing up").replace("knife still at guard", "the bat still held at guard with both hands").replace("head and knife still facing LEFT", "head and bat still facing LEFT").replace("knife at guard", "the bat at guard with both hands")
		for b in MOVES["hop_k"]["beats"]],
	"not": ["turning toward the camera", "turning the back to the enemy", "a second bat", "holding the bat with one hand", "swinging the bat", "slash trails or motion lines", "dust clouds"]}

# รอบ 3: เริ่มจากภาพ hop_bat เฟรม 6 (ไม้ตั้งเหนือหัว ก้าวเท้าหน้า หันซ้าย · PL_START_IMG) → ฟาดลงอย่างเดียว 4 เฟรม (ท่าสั้นได้ผลกว่าท่าเหวี่ยงยาว)
# hop_bat2: hop_bat รอบแรกกลายเป็นพุ่งไปหน้า → เน้นตัวเคลื่อนไปทางขวา (ถอยหลัง) เท่านั้น
MOVES["chop_bat"] = {"dir": "west", "held": BAT, "attack": True, "frames": 4, "seed": 31,
	"beats": [
		"same pose as the start image: the bat raised straight up above the head with both hands, front foot forward, facing left",
		"the bat chops forward and down: both arms swing down in front of the face, the bat pointing forward and up to the LEFT at 45 degrees, mouth open shouting",
		"impact: both arms extended forward and down, the bat barrel pointing DOWN-LEFT about 60 degrees below horizontal toward a target at waist height in front of the front foot, torso upright and tense, eyes fierce, mouth open shouting",
		"hold the impact pose: the bat stays at the same down-left angle, torso upright, teeth gritted"],
	"not": ["a hammer", "holding the bat with one hand", "letting go of the bat", "a second bat", "a level horizontal swing", "the torso bending forward",
		"turning toward the camera", "facing right", "a front view", "swing trails, motion arcs or speed lines", "impact stars or sparks", "an opponent or any second figure"]}
MOVES["hop_bat2"] = {"dir": "west", "held": BAT, "attack": False, "frames": 6, "seed": 41,
	"beats": [
		"standing facing left, both hands holding the bat resting back on the shoulder, same as the start image",
		"crouch: knees bend deep, hips drop, body leaning back to the RIGHT, still facing left",
		"jump BACKWARD: both feet leave the ground and the whole body moves to the RIGHT, away from the enemy, knees tucked, still facing left",
		"in the air further to the RIGHT, knees tucked, the bat still on the shoulder, still facing left",
		"landing to the RIGHT of where it started: knees bend deep to absorb the fall, still facing left",
		"standing facing left, bat on the shoulder, same as the first frame"],
	"not": ["moving or stepping to the LEFT", "running forward", "lunging", "raising or swinging the bat", "turning toward the camera", "turning the back to the enemy",
		"a second bat", "holding the bat with one hand", "motion lines", "dust clouds"]}

# รอบ 4: ท่าฟาดลงไม่ผ่าน 3 รอบ (หวดแนวนอน · หันขวา/เข้ากล้อง) แต่ State ผ่านทุกครั้ง → ท่ากระทบเป็น State แล้วเจนท่ากลาง (PL_START_IMG ไม้เหนือหัว → PL_END_IMG กระทบ)
STATES["BT_bat_impact"] = {"seed": 27, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. Keep the blue cap with brass goggles, brown hair, white shirt, blue necktie, "
	"brown backpack, blue shorts, white socks, brown boots. True side view facing the same direction as the source rotation, never turned toward the camera. "
	"Held item: the same aluminum baseball bat gripped with BOTH hands together on the handle. "
	"Pose: the impact of a downward two-handed chop: both arms extended forward and down, the bat barrel pointing forward and DOWN at a steep 60-degree angle "
	"toward a target at waist height in front; front foot stepped forward and planted, back leg straight, torso upright and tense, mouth open shouting, fierce eyes. "
	"No glow, no motion lines, no shadow, no ground, no background, no text.")}
MOVES["chop_bat2"] = {"dir": "west", "held": BAT, "attack": True, "frames": 4, "seed": 31,
	"beats": ["the bat raised straight up above the head with both hands, same as the start image",
		"both arms swing forward over the face, the bat pointing forward and up at 45 degrees",
		"both arms coming down in front, the bat nearly level pointing forward",
		"impact, same as the end image: the bat pointing down-forward at 60 degrees, torso upright, shouting"],
	"not": ["turning toward the camera", "facing right", "a front view", "a level horizontal swing at chest height", "holding the bat with one hand",
		"a second bat", "swing trails, motion arcs or speed lines", "impact stars or sparks"]}

# วิ่งเข้า + ยืนหายใจถือไม้ (kwan 26 ต.ค. "วิ่งไปโจมตีแบบฟัน เสร็จแล้วทำท่ายืนหายใจ") · วิ่งแบกไม้บนไหล่ = ช่วง load ของรายงาน bt0
MOVES["run_bat"] = {"dir": "west", "held": BAT, "attack": False, "frames": 8, "seed": 33,
	"beats": [b.replace("knife held low at guard in front of the chest", "the bat resting back on the shoulder with both hands on the handle at the chest")
		.replace("knife still at guard", "the bat still on the shoulder").replace("knife steady", "the bat steady on the shoulder") for b in MOVES["run_k"]["beats"]],
	"not": ["turning toward the camera", "a second bat", "holding the bat with one hand", "swinging or raising the bat", "slash trails or motion lines", "dust clouds"]}
MOVES["idle_bat"] = {"dir": "west", "held": BAT, "attack": False, "frames": 4, "seed": 33,
	"beats": ["battle-ready stance facing left, the bat resting back on the shoulder with both hands on the handle, same as the start image",
		"breathe in: chest rises one pixel, shoulders lift slightly, the bat bobs up one pixel",
		"breathe out: chest and shoulders come back down",
		"same stance as the first frame (ready to loop)"],
	"not": ["stepping", "turning", "swinging or raising the bat", "holding the bat with one hand", "motion lines"]}


# ---- สายกวาด ท่าหมุน (kwan 27 ต.ค. "หมุนตัวครบรอบ แขนกางมีดออก ใบมีดกวาดทุกตัว ใช้งาน pixellab ได้เลย เอาให้สุด · ต่อด้วย พายุเถ้าใบมีด") ----
# ท่าหมุนสั่งเจนตรงๆ พังทุกครั้ง (หันเข้ากล้อง · มีดหาย) → ทำเป็น State ท่านิ่ง (ได้ 4 ทิศ) แล้ว rot8 ให้ v3 เติมมุมเฉียงจากภาพเดิม = ภาพหมุน 8 มุมของท่าเดียวกันจริง
SPIN_KEEP = ("Keep the blue cap with brass goggles, brown hair, white shirt, blue necktie, brown belt, brown backpack, "
	"blue shorts, white socks and brown boots. ")
SPIN_KNIFE = ("The RIGHT hand grips ONE small kitchen knife: short dark wooden handle in the fist, short silver blade about as long as the hand, "
	"the blade pointing straight OUTWARD away from the body, continuing the line of the right arm. ")
SPIN_NOT = "No second knife, no sword, no glow, no trails, no motion lines, no shadow, no ground, no background."
STATES["BL4_spin_T"] = {"seed": 41, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Spinning-top blade attack pose: standing upright, feet planted wide apart, knees slightly bent. BOTH arms stretched straight out "
	"horizontally to the left and right of the body at shoulder height, elbows straight, like a letter T. "
	+ SPIN_KNIFE + "The left hand is open and flat, fingers together. Torso upright, chin level, eyes narrowed, mouth set in a determined line. "
	"The arms stay straight out to the sides in every rotation. " + SPIN_KEEP + SPIN_NOT)}
STATES["BL12_low_sweep"] = {"seed": 43, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Low sweeping spin pose: a deep wide crouch, knees bent low, feet wide apart and flat, torso leaning slightly forward. "
	"BOTH arms stretched straight out horizontally to the left and right of the body at waist height, elbows straight. "
	+ SPIN_KNIFE + "The left hand is open and flat. Eyes fierce, mouth open shouting. "
	"The arms stay straight out to the sides in every rotation. " + SPIN_KEEP + SPIN_NOT)}
STATES["BL12_air_spin"] = {"seed": 47, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Airborne spinning jump pose: both feet off the ground, knees bent and tucked up under the body, toes pointing down, "
	"BOTH arms stretched straight out horizontally to the left and right of the body at shoulder height, elbows straight. "
	+ SPIN_KNIFE + "The left hand is open and flat. Hair and shirt hem blown upward by the jump. Eyes fierce, teeth gritted. "
	"The arms stay straight out to the sides in every rotation. " + SPIN_KEEP + SPIN_NOT)}

# ---- กิ่งลื่นไหล สายคม (kwan 27–28 ต.ค. เลือก "2" = แบบผสม: key pose ที่ตาจำได้เป็น State · ที่เหลือใช้ภาพเดิม + โค้ด) ----
# ท่าตาม key pose ใหม่ในรายงานทีม R2 (SPRITES ใน docs/design/moves/MOVES_RESEARCH_102_R2.html) · bl6 = ข้อยกเว้นถือสองมีด (นิเท็นอิจิริว · ทีมแนะนำ)
SIDE = "In side views stay in a true side view facing the same direction as the source rotation, never turned toward the camera. "
FLOW_NOT = "No sword, no glow, no trails, no motion lines, no shadow, no ground, no background."
STATES["BL5_iai_crouch"] = {"seed": 51, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes and a plain brown leather knife sheath is added at the LEFT side of the belt. "
	"Iaido ready crouch: knees deeply bent, feet wide, body coiled low and perfectly still. The kitchen knife is SHEATHED: only its short dark wooden handle "
	"sticks out of the sheath at the left hip; the RIGHT hand rests on that handle and the LEFT hand holds the sheath. No blade visible. Eyes narrowed, mouth closed, calm. "
	+ SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}
STATES["BL5_iai_cut"] = {"seed": 52, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes and a plain brown leather knife sheath is added at the LEFT side of the belt. "
	"Finish of a lightning-fast draw cut: body lunged forward low, front knee bent deep, back leg stretched straight. The RIGHT arm is fully extended forward at temple height "
	"holding ONE small kitchen knife (short dark wooden handle, short silver blade about as long as the hand) with the blade horizontal and pointing forward. "
	"The LEFT hand still holds the empty sheath back at the left hip. Head lowered slightly, eyes fierce. " + SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}
TWO = ("Exactly TWO knives, one in each hand, in every rotation: the RIGHT hand holds a small kitchen knife (dark wooden handle, short silver blade about as long as the hand) "
	"and the LEFT hand holds a SHORTER small knife (blade about half as long). ")
STATES["BL6_enso"] = {"seed": 53, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose and the held items change. Two-knife stance: " + TWO +
	"The right knife is raised forward with its blade angled up and forward; the left short knife is held low behind the hip with its blade angled down and back; "
	"arms spread wide apart. Knees bent, feet apart, eyes forward and calm. " + SIDE + SPIN_KEEP + FLOW_NOT)}
STATES["BL6_cut1"] = {"seed": 54, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose and the held items change. Two-knife attack: " + TWO +
	"The right knife slashes diagonally downward and forward, arm extended; the left short knife is held back near the chest as a guard. "
	"Torso leaning into the cut, front foot stepped in, knees bent, mouth shouting. " + SIDE + SPIN_KEEP + FLOW_NOT)}
STATES["BL6_cross"] = {"seed": 55, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose and the held items change. Crossing two-knife strike: " + TWO +
	"The LEFT arm is extended forward at chest height with the short knife; the RIGHT hand kitchen knife is lowered across the waist; "
	"the two blades cross in an X shape in front of the body. Torso twisted, knees bent deep, teeth gritted. " + SIDE + SPIN_KEEP + FLOW_NOT)}
STATES["BL13_slither"] = {"seed": 56, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. Very low slithering cross-step: the front leg crossed over the back leg, "
	"body crouched close to the ground, ONE small kitchen knife held in the RIGHT hand low beside the knee, the LEFT hand reaching low for balance without covering the face, "
	"head up, eyes sharp. " + SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}
STATES["BL14_stride"] = {"seed": 57, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. Long diagonal stride: the front leg reaching far forward, the back leg pushing off, "
	"torso leaned into the step, ONE small kitchen knife held ready in the RIGHT hand at the side, the LEFT arm swung back for balance, eyes forward. "
	+ SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}
STATES["BL15_roll"] = {"seed": 58, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. Deflecting an unseen blade: ONE small kitchen knife in the RIGHT hand is rolled over "
	"to the far side of the wrist, the blade angled diagonally across the body pointing down and forward, the wrist turned outward, the body half-stepped back and turned slightly; "
	"the LEFT hand raised open near the chest. Eyes sharp, mouth tight. " + SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}

# ---- ท่ากลางให้ลื่น (kwan 28 ต.ค. "ท่าดูไม่ลื่นเลย เจนเพิ่มให้ไหลลื่นได้") ----
# ภาพ State เป็นท่านิ่งภาพเดียว → สลับภาพแล้วกระตุก · เจนท่ากลางระหว่างสอง key pose (PL_START_IMG → PL_END_IMG · ~2 gen/ท่า)
# ภาพ State 96x96 · ภาพท่าจาก fight_knife 128x128 (ขนาดตัวเท่ากัน) → ผสมกันต้องเติมขอบ State เป็น 128 ก่อน (scratch)
SHEATH = "a plain brown leather knife sheath stays at the LEFT side of the belt in every frame"
MOVES.update({
	"bl5_draw": {"dir": "west", "attack": True, "frames": 6, "seed": 61,
		"held": KNIFE + "; in the first frame the knife is still inside the sheath at the left hip with only the handle showing, then the RIGHT hand draws it out; " + SHEATH,
		"beats": ["same as the start image: iaido crouch, perfectly still, the RIGHT hand on the knife handle at the left hip, the LEFT hand holding the sheath",
			"the RIGHT hand starts pulling the knife out of the sheath, the blade sliding out across the belly, knees still deep",
			"the blade clears the sheath and sweeps forward horizontally at waist height, the front foot steps forward",
			"lunging forward low, the RIGHT arm sweeping the knife horizontally forward, the LEFT hand pulling the empty sheath back",
			"the RIGHT arm almost fully extended forward at temple height, blade horizontal, back leg stretching",
			"same as the end image: finish of the draw cut, RIGHT arm fully extended forward, LEFT hand holding the sheath back at the hip"],
		"not": ["a second knife", "a sword or long blade", "the knife in the left hand", "slash trails, glow or motion lines"]},
	"bl5_noto": {"dir": "west", "attack": False, "frames": 6, "seed": 62,
		"held": KNIFE + "; it ends back inside the sheath at the left hip; " + SHEATH,
		"beats": ["same as the start image: RIGHT arm extended forward with the knife after the cut",
			"chiburi: the RIGHT arm flicks the knife sharply down and out to the side to shake off blood, body still low",
			"the RIGHT hand slowly brings the knife back toward the left hip, blade horizontal, the LEFT hand holding the sheath mouth",
			"the blade tip enters the sheath mouth at the left hip, sliding in slowly, eyes still on the enemy",
			"the knife almost fully sheathed, only the handle and a little blade showing, knees deep",
			"same as the end image: iaido crouch, knife fully sheathed, the RIGHT hand resting on the handle"],
		"not": ["a second knife", "looking down at the sheath", "the knife in the left hand", "slash trails, glow or motion lines"]},
	"bl6_summon": {"dir": "west", "attack": False, "frames": 6, "seed": 63, "held_free": True,
		"held": ("the RIGHT hand holds ONE small kitchen knife (short dark wooden handle, short silver blade about as long as the hand) in every frame; "
			"the LEFT hand starts EMPTY and open, then closes around the handle of a SHORTER second knife that appears in it from frame 4 on, "
			"so the last frame has exactly two knives, one in each hand"),
		"beats": ["same as the start image: fighting stance, the knife in the RIGHT hand, the LEFT hand empty",
			"the LEFT hand opens wide and reaches back low behind the hip, palm open, fingers spread, eyes narrowing",
			"the LEFT fist closes on empty air behind the hip as if gripping a handle, knees bending",
			"a short second knife is now in the LEFT fist, blade angled down and back; the RIGHT knife rises forward",
			"arms spreading wide apart, the RIGHT knife angled up and forward, the LEFT short knife low behind the hip",
			"same as the end image: two-knife stance, arms spread wide, knees bent"],
		"not": ["the right knife switching hands", "a sword", "turning toward the camera", "glow, smoke, trails or motion lines"]},
	"bl6_cut": {"dir": "west", "attack": True, "frames": 4, "seed": 64, "held_free": True,
		"held": "exactly two knives in every frame: a small kitchen knife in the RIGHT hand and a SHORTER knife in the LEFT hand",
		"beats": ["same as the start image: two-knife stance, arms spread",
			"step in with the front foot, the RIGHT arm raising the knife high forward, the LEFT short knife pulled toward the chest",
			"the RIGHT knife slashing diagonally down and forward, torso leaning into the cut",
			"same as the end image: RIGHT arm extended down-forward after the slash, LEFT short knife guarding near the chest"],
		"not": ["a third knife", "knives switching hands", "turning toward the camera", "slash trails, glow or motion lines"]},
	"bl6_x": {"dir": "west", "attack": True, "frames": 4, "seed": 65, "held_free": True,
		"held": "exactly two knives in every frame: a small kitchen knife in the RIGHT hand and a SHORTER knife in the LEFT hand",
		"beats": ["same as the start image: RIGHT arm extended down-forward after the first slash, LEFT short knife near the chest",
			"the torso twists, the LEFT arm drives the short knife forward while the RIGHT knife sweeps back across the waist",
			"the two blades meet crossing in front of the body, knees bending deep",
			"same as the end image: LEFT arm extended forward with the short knife, RIGHT knife low across the waist, the blades forming an X"],
		"not": ["a third knife", "knives switching hands", "turning toward the camera", "slash trails, glow or motion lines"]},
	"bl13_glide": {"dir": "west", "attack": False, "frames": 6, "seed": 66, "held": KNIFE,
		"beats": ["same as the start image: very low cross-step, the front leg crossed over the back leg, knife low beside the knee",
			"the back leg slides out from behind and steps wide forward-left, body staying very low, head level",
			"legs wide apart, body at its lowest, knife low, the LEFT hand reaching low forward for balance",
			"the other leg slides across in front, crossing over again, body still low and level",
			"crossed legs, weight shifting forward onto the front foot, head level",
			"same as the start image, ready to loop"],
		"not": ["standing up tall", "jumping", "turning toward the camera", "a second knife", "slash trails, glow or motion lines"]},
	"bl13_cut": {"dir": "west", "attack": True, "frames": 4, "seed": 67, "held": KNIFE,
		"beats": ["same as the start image: very low cross-step, knife low beside the knee",
			"springing up and forward out of the crouch, the RIGHT arm whipping the knife up from low",
			"the knife slashing forward at knee-to-hip height, front foot landing, body leaning in",
			"same as the end image: low slash finish, RIGHT arm extended forward low"],
		"not": ["a second knife", "the knife in the left hand", "turning toward the camera", "slash trails, glow or motion lines"]},
	"bl14_leap": {"dir": "west", "attack": True, "frames": 8, "seed": 68, "held": KNIFE,
		"beats": ["same as the start image: long diagonal stride, pushing off the back leg, knife ready at the side",
			"both knees bend deep for a big jump, arms swinging back, knife low",
			"launching up and forward to the LEFT, legs extending, arms swinging up, the knife raised",
			"high in the air over the enemies, knees tucked up, the knife held high over the head ready to strike",
			"descending to the LEFT, legs reaching down, the RIGHT arm starting to swing the knife down",
			"landing on the front foot, the knife slashing down diagonally in front of the body",
			"knees bending deep to absorb the landing, the RIGHT arm low after the slash",
			"rising into a low fighting stance facing left, knife at guard"],
		"not": ["turning toward the camera", "flipping upside down", "a second knife", "the knife in the left hand", "slash trails, glow or motion lines"]},
	"bl15_counter": {"dir": "west", "attack": True, "frames": 4, "seed": 69, "held": KNIFE,
		"beats": ["same as the start image: the knife rolled over the wrist deflecting, body half-stepped back",
			"the wrist rolls the knife back over, the blade coming up and around overhead, a diagonal step forward",
			"the RIGHT arm cuts down diagonally in front of the body, weight landing on the front foot",
			"same as the end image: follow-through of the downward slash"],
		"not": ["a second knife", "the knife in the left hand", "turning toward the camera", "slash trails, glow or motion lines"]},
})
MOVES.update({   # วงล้อ bl4 แบบ windmill ของ b-boy (kwan 28 ต.ค.) · ท่ากลางเข้า/ออกจากท่าหมุน
	"bl4_dive": {"dir": "west", "attack": False, "frames": 4, "seed": 76, "held": KNIFE,
		"beats": ["same as the start image: in the air, knees tucked, the knife raised over the head",
			"falling forward and down, the LEFT hand reaching for the ground, legs starting to swing up behind",
			"the LEFT hand and shoulders touch the ground, the body tipping upside down, legs swinging up and apart, the knife arm stretching out along the ground",
			"same as the end image: upside down on the shoulders, legs spread wide in a V in the air, the knife arm stretched out along the ground"],
		"not": ["a second knife", "the knife in the left hand", "slash trails, glow or motion lines", "landing on the feet"]},
	"bl4_kip": {"dir": "west", "attack": False, "frames": 4, "seed": 77, "held": KNIFE,
		"beats": ["same as the start image: upside down on the shoulders, legs spread wide in a V in the air",
			"the legs whip down together toward the ground, the body rolling forward onto the hands",
			"springing up off the hands, feet landing under the body, crouched low, knife coming to guard",
			"same as the end image: fighting stance facing left, knife at guard in the RIGHT hand"],
		"not": ["a second knife", "the knife in the left hand", "slash trails, glow or motion lines", "turning toward the camera"]},
})

# ท่าใหม่ (ท่านิ่ง) · kwan 28 ต.ค.: กวาด bl3 ลงกลางดงมอน · ไม้ตาย bl16 พันคมดับเถ้า
STATES["BL3_kneel_sweep"] = {"seed": 71, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Kneeling sweep pose: the left knee down touching the ground, the right leg bent with the foot flat, torso low and upright. "
	"The RIGHT arm is stretched straight out horizontally to the side at knee height holding ONE small kitchen knife "
	"(short dark wooden handle, short silver blade about as long as the hand) with the blade pointing outward continuing the arm. "
	"The LEFT hand is pressed flat on the ground for balance. Eyes fierce, mouth set. "
	"The pose stays the same in every rotation. " + SPIN_KEEP + SPIN_NOT)}
STATES["BL14_air"] = {"seed": 74, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"High in the air in the middle of a big forward jump: both feet off the ground, knees tucked up under the body, body leaning forward. "
	"The RIGHT arm raised high above and behind the head holding ONE small kitchen knife (short dark wooden handle, short silver blade), "
	"ready to cut down; the LEFT arm stretched forward for balance. Hair and shirt blown upward. Eyes fierce, mouth shouting. "
	+ SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}   # bl14_leap ได้ท่าวิ่ง ไม่ลอย (kwan 28 ต.ค. "กระโดดไปแถวหลังเลย")
STATES["BL4_windmill"] = {"seed": 75, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Breakdance windmill power move frozen mid-spin: the boy lies diagonally on his upper back and shoulders on the ground, "
	"BOTH legs straight and spread wide apart in a big V raised high into the air. The LEFT hand is planted flat on the ground beside the hip for support. "
	"The RIGHT arm is stretched straight out along the ground away from the body holding ONE small kitchen knife "
	"(short dark wooden handle, short silver blade about as long as the hand) with the blade pointing outward continuing the arm. "
	"Cap still on the head, eyes fierce, teeth gritted. The pose stays the same in every rotation. " + SPIN_KEEP + SPIN_NOT)}   # kwan 28 ต.ค. "ท่ากงล้อ ทำท่า windmill ของ b boy ฟันหมุนแทน"
STATES["BL4_windmill_nobag"] = {"seed": 78, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes and the brown backpack is taken OFF and not worn at all, "
	"so the back of the white shirt is visible. "
	"Breakdance windmill power move frozen mid-spin: the boy lies diagonally on his upper back and shoulders on the ground, "
	"BOTH legs straight and spread wide apart in a big V raised high into the air. The LEFT hand is planted flat on the ground beside the hip for support. "
	"The RIGHT arm is stretched straight out along the ground away from the body holding ONE small kitchen knife "
	"(short dark wooden handle, short silver blade about as long as the hand) with the blade pointing outward continuing the arm. "
	"Cap still on the head, eyes fierce, teeth gritted. The pose stays the same in every rotation. "
	"Keep cap, goggles, hair, white shirt, necktie, belt, blue shorts, socks and boots. No backpack, no straps. " + SPIN_NOT)}   # kwan 28 ต.ค. "3": ปลดกระเป๋าก่อนหมุน (กระเป๋าดูกระพริบสลับข้างตอนหมุน)
STATES["ULT_powerup"] = {"seed": 79, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Powering up with a mighty roar: standing with feet wide apart and knees bent, both arms pulled down and back beside the hips with fists clenched hard, "
	"chest pushed forward, head tilted up, mouth wide open screaming, eyes glowing and fierce, hair standing straight up. "
	"The RIGHT fist grips ONE small kitchen knife (short dark wooden handle, short silver blade) pointing down. "
	+ SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}   # kwan 28 ต.ค. ท่าสุดยอดของสาย: ระเบิดพลังแบบซูเปอร์ไซย่าก่อนพูดชื่อท่า
STATES["BL16_charge"] = {"seed": 72, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Charging stance before an ultimate attack: very deep wide crouch, the back knee almost on the ground, body coiled and twisted away from the enemy. "
	"The RIGHT hand holds ONE small kitchen knife in a REVERSE grip low behind the right hip, the blade lying back along the forearm. "
	"The LEFT arm stretched forward toward the enemy with the hand open and fingers spread. Hair standing up, eyes wide and burning, teeth gritted. "
	+ SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}
STATES["BL16_finish"] = {"seed": 73, "frame": None, "edit": (
	"Same character, same design, proportions and colors; only the pose changes. "
	"Landing after a huge decisive downward cut: the front knee bent very deep, the back leg stretched far behind, torso leaned forward low. "
	"The RIGHT arm swung all the way down in front so ONE small kitchen knife (short dark wooden handle, short silver blade) points at the ground near the front foot. "
	"The LEFT arm swept back behind. Head up, eyes fierce, mouth closed. " + SIDE + SPIN_KEEP + "No second knife. " + FLOW_NOT)}

ROT8_KEEP = {}   # State ไหนภาพข้างใช้ได้ ใส่ทิศที่จะส่งไปตามเดิม
ROT8 = ("west", "south-west", "south", "south-east", "east", "north-east", "north", "north-west")   # ลำดับหมุน: หันซ้าย → เข้ากล้อง → ขวา → หลัง


def rot8(name):
	"""State 4 ทิศ → v3 เติมมุมเฉียง 4 มุมจากภาพ south ของ State (ทิศที่มีแล้วส่งไปตามเดิม) → OUT/states/<ชื่อ>/<ชื่อ>/rotations8/"""
	rd = os.path.join(OUT, "states", name, name, "rotations")
	if not os.path.isfile(os.path.join(rd, "south.png")):
		sys.exit("ยังไม่มีภาพ State: รัน state + fetch_state ก่อน")
	balance()
	body = {"description": DESC + ", " + STATES[name]["edit"][:400], "name": "Rion " + name + " rot8", "reference_image": b64(os.path.join(rd, "south.png")),
		"direction_images": {d: b64(os.path.join(rd, d + ".png")) for d in ROT8_KEEP.get(name, ("north",))},   # ภาพข้างของ State มักไม่ได้ท่าเดียวกับหน้า/หลัง → ให้ v3 หมุนเองจากภาพหน้า
		"n_directions": 8, "view": "low top-down", "no_background": True, "seed": STATES[name]["seed"]}
	r = call("POST", "/create-character-v3", body)
	s = state()
	s.setdefault("rot8", {})[name] = r
	save_state(s)
	print(json.dumps(r, ensure_ascii=False)[:600])
	if r.get("background_job_id"):
		wait(r["background_job_id"], "rot8 " + name)
	data = call("GET", f"/characters/{r['character_id']}/zip", raw=True)
	dst = os.path.join(OUT, "states", name, name, "rotations8")
	tmp = dst + "_zip"
	shutil.rmtree(tmp, ignore_errors=True)
	zipfile.ZipFile(io.BytesIO(data)).extractall(tmp)
	os.makedirs(dst, exist_ok=True)
	for f in glob_rot(tmp):
		shutil.copy(f, os.path.join(dst, os.path.basename(f)))
		print(" ", os.path.basename(f), Image.open(f).size)
	shutil.rmtree(tmp, ignore_errors=True)
	balance()


def glob_rot(d):
	out = []
	for root, _, fs in os.walk(d):
		if os.path.basename(root) == "rotations":
			out += [os.path.join(root, f) for f in sorted(fs) if f.endswith(".png")]
	return out


def make_state(name):
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	st = STATES[name]
	print(f"— edit_description ({len(st['edit'])} ตัวอักษร) —\n{st['edit']}\n")
	balance()
	body = {"character_id": s["character_id"], "edit_description": st["edit"], "state_name": name, "seed": st["seed"],
		"no_background": True, "use_color_palette_from_reference": True}
	if st.get("frame"):
		body["override_frame_size"] = {"width": st["frame"][0], "height": st["frame"][1]}
	r = call("POST", "/create-character-state", body)
	s.setdefault("states", {})[name] = {"response": r}
	save_state(s)
	print(json.dumps(r, ensure_ascii=False)[:800])
	jid = r.get("background_job_id") or (r.get("background_job_ids") or [None])[0]
	if jid:
		j = wait(jid, f"state {name}")
		s["states"][name]["status"] = j.get("status")
		save_state(s)
	balance()


def fetch_state(name):
	"""ZIP ของ State → OUT/states/<ชื่อ>/ (ภาพหมุนทุกทิศ)"""
	s = state()
	r = s["states"][name]["response"]
	cid = r.get("character_id") or r.get("state_character_id") or r.get("id")
	if not cid:
		sys.exit("ไม่เจอ character_id ของ State ใน state.json: " + json.dumps(r, ensure_ascii=False)[:400])
	data = call("GET", f"/characters/{cid}/zip", raw=True)
	dst = os.path.join(OUT, "states", name)
	os.makedirs(dst, exist_ok=True)
	zipfile.ZipFile(io.BytesIO(data)).extractall(dst)
	for root, _, fs in os.walk(dst):
		for f in sorted(fs):
			if f.endswith(".png"):
				im = Image.open(os.path.join(root, f))
				print(" ", os.path.relpath(os.path.join(root, f), dst), im.size, im.getbbox())


# ---- เอฟเฟกต์ (/vfx · kwan 18 ต.ค. "vfx ก็ทำใน pixellab ได้หรือเปล่า" → ลอง lite 1 ท่า) ----
# คำสั่งละเอียดแบบเดียวกับท่า: อะไร · สี · ขยับยังไง · จังหวะเทียบเฟรมของสไปรต์ · สิ่งที่ห้าม · สไปรต์ = เฟรมท่าที่ PixelLab เจนแล้ว (เรียงแนวนอน)
VFX_SPECS = {
	"slash2_trail": {"sprite": "zip/Idle/animations/slash2/west", "artist": "lite", "fps": 9,
		"description": (
			"A knife slash trail for a small kitchen knife, in 32-bit pixel art that matches the sprite: hard pixel edges, no anti-aliasing, "
			"no blur, no soft glow gradients, a small palette. The sprite is an 8-frame attack: a chibi boy seen from the side, facing LEFT "
			"in every frame, raises a short kitchen knife behind his shoulder (frames 1-4), slashes it down in a curved arc in front of his body "
			"toward an enemy on the LEFT (frames 5-6), follows through low and recovers (frames 7-8). "
			"Make the effect follow the knife tip exactly: nothing during the wind-up except a 1-2 pixel glint on the blade at frame 4; "
			"at frames 5-6 a thick crescent arc trail swept from above the cap down to knee height on the LEFT side of the body, "
			"3 pixels thick at its middle and tapering to 1 pixel at both ends, colours from the edge inward: dark navy #21508A outline, "
			"blue #4184C9, pale sky blue, and a white core line along the leading edge; 4-6 small white and pale-blue spark pixels fly "
			"off the arc to the left at frame 6; at frames 7-8 the arc breaks into pixel fragments that fade out and drift slightly left and down. "
			"The effect is about as wide as the character and never covers his face. "
			"Do NOT redraw, recolour, move or resize the character; do NOT add a second knife, a big explosion, smoke, a ground, a shadow, "
			"a background, text or numbers. Keep the same timing as the sprite and end with an empty frame so the attack can loop.")},
}


def vfx(name):
	spec = VFX_SPECS[name]
	src = os.path.join(OUT, spec["sprite"])
	files = sorted(f for f in os.listdir(src) if f.startswith("frame_"))
	ims = [Image.open(os.path.join(src, f)).convert("RGBA") for f in files]
	strip = Image.new("RGBA", (ims[0].width * len(ims), ims[0].height), (0, 0, 0, 0))
	for i, im in enumerate(ims):
		strip.paste(im, (i * im.width, 0))
	buf = io.BytesIO()
	strip.save(buf, "PNG")
	print(f"เอฟเฟกต์ {name} · {spec['artist']} · สไปรต์ {len(ims)} เฟรม {ims[0].size} · คำสั่ง {len(spec['description'])} ตัวอักษร")
	print(spec["description"])
	balance()
	r = call("POST", "/vfx", {"description": spec["description"], "artist": spec["artist"], "name": f"Rion {name}",
		"sprite": {"type": "base64", "base64": base64.b64encode(buf.getvalue()).decode(), "format": "png"},
		"sprite_frames": len(ims), "sprite_fps": spec["fps"], "game_pack": True})
	print("ตอบรับ", json.dumps(r, ensure_ascii=False)[:600])
	s = state()
	s.setdefault("vfx", []).append({"name": name, "response": r})
	save_state(s)
	jid = r.get("background_job_id")
	if not jid:
		sys.exit("ไม่มี background_job_id")
	j = wait(jid, "vfx " + name)
	last = j.get("last_response") or {}
	s["vfx"][-1].update(status=j.get("status"), result={k: v for k, v in last.items() if k != "conversation"}, conversation=last.get("conversation"))
	save_state(s)
	dst = os.path.join(OUT, "vfx", name)
	os.makedirs(dst, exist_ok=True)
	fl = last.get("files") or {}
	for fname, url in (fl.items() if isinstance(fl, dict) else [(f.get("name") or os.path.basename(f.get("url", "")), f.get("url")) for f in fl]):
		for i in range(4):
			try:
				data = urllib.request.urlopen(url, timeout=120).read()
				break
			except urllib.error.URLError as e:
				print(f"  โหลด {fname} หลุด ({e.reason}) ลองใหม่", flush=True)
				time.sleep(2 ** (i + 1))
		else:
			continue
		open(os.path.join(dst, os.path.basename(fname)), "wb").write(data)
		print("  ได้", fname, len(data), "ไบต์")
	print("ข้อความศิลปิน:", last.get("message"))
	vfx_frames(name)
	balance()


def vfx_frames(name):
	"""ผล /vfx → เฟรมแยกให้หน้า pixellab animation test: with_sprite/ (ตามที่ PixelLab ทำ) · fx/ (เอฟเฟกต์ล้วน ผืน/จังหวะเท่าสไปรต์ จาก game pack)"""
	dst = os.path.join(OUT, "vfx", name)
	base = [f for f in os.listdir(dst) if f.endswith(".json") and not f.endswith("manifest.json")][0][:-5]
	meta = json.load(open(os.path.join(dst, base + ".json")))
	sheet = Image.open(os.path.join(dst, base + ".png")).convert("RGBA")
	for sub in ("with_sprite", "fx"):
		shutil.rmtree(os.path.join(dst, sub), ignore_errors=True)
		os.makedirs(os.path.join(dst, sub))
	for i, fr in enumerate(meta["frames"]):
		r = fr["frame"]
		sheet.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"])).save(os.path.join(dst, "with_sprite", f"frame_{i:03d}.png"))
	z = zipfile.ZipFile(os.path.join(dst, base + "-game.zip"))
	man = json.loads(z.read("manifest.json"))
	clip = next(c for c in man["clips"] if c["name"] == "whole")
	w, h = man["canvas"]["w"], man["canvas"]["h"]
	ox, oy = man["anchor"]["x"] + clip["offset"]["x"], man["anchor"]["y"] + clip["offset"]["y"]
	cells = {}
	for sh in clip["sheets"]:
		im = Image.open(io.BytesIO(z.read(sh["file"]))).convert("RGBA")
		for k in range(sh["frames"]):
			cx, cy = (k % sh["columns"]) * clip["frame"]["w"], (k // sh["columns"]) * clip["frame"]["h"]
			cells[sh["first_frame"] + k] = im.crop((cx, cy, cx + clip["frame"]["w"], cy + clip["frame"]["h"]))
	for i in range(man["frames"]):
		out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
		k = i - clip["start_frame"]
		if k in cells:
			out.alpha_composite(cells[k], (ox, oy))
		out.save(os.path.join(dst, "fx", f"frame_{i:03d}.png"))
	print("  เฟรมแยก", len(meta["frames"]), "→", dst, "(with_sprite/ fx/)")


PAGE_H, PAGE_FEET = 112, 108   # ผืน/แถวเท้าเดียวกับ rion_pack_px (CANVAS_H · FEET) → เทียบกับชีต B ได้ตรง
G_WALK = "★ Rion master v2 · เดินหลัก (ชีต B · kwan เลือก 18 ต.ค.)"


PAGE_CLIPS = {   # ท่าที่ลงหน้าเทส: (กลุ่ม, ชื่อ, ms ความเร็วดู, ms ในเกมหรือ None, พื้นเลื่อน/รอบ)
	"walk": (G_WALK, "เดิน", 90, 37.5, 48),
	"slash2": ("Rion พิกเซล · ชุดครบ · ท่าศึก", "ฟันมีด (PixelLab รอบ 2 · หันซ้ายทุกเฟรม)", 110, None, 0),
}


def page():
	"""ZIP → OUT/px/<คลิป>_<i>.png + index.json (รูปแบบคลิปเดียวกับ rion_pack_px) ให้หน้า animation test วางคู่ชุดเดิม
	เลื่อนทุกเฟรมของท่าเท่ากัน (เท้าต่ำสุด = แถว PAGE_FEET · กลางกรอบรวม) → คงการขึ้นลง/ส่ายตัวที่ PixelLab วาดมา
	ท่าที่ไม่อยู่ใน PAGE_CLIPS (เช่น slash รอบแรกที่ตัวหมุนเข้ากล้อง) ไม่ลงหน้า"""
	base = os.path.join(OUT, "zip", "Idle/animations")
	dst = os.path.join(OUT, "px")
	shutil.rmtree(dst, ignore_errors=True)
	os.makedirs(dst)
	clips = []
	for anim in sorted(os.listdir(base)):
		if anim not in PAGE_CLIPS:
			continue
		group, th, ms, game_ms, travel = PAGE_CLIPS[anim]
		for d in sorted(os.listdir(os.path.join(base, anim))):
			src = os.path.join(base, anim, d)
			fs = [Image.open(os.path.join(src, f)).convert("RGBA") for f in sorted(os.listdir(src)) if f.endswith(".png")]
			bb = [f.getchannel("A").getbbox() for f in fs]
			x0, y1 = min(b[0] for b in bb), max(b[3] for b in bb)
			W = max(b[2] for b in bb) - x0 + 24
			names = []
			for i, f in enumerate(fs):
				c = Image.new("RGBA", (W, PAGE_H))
				c.alpha_composite(f, (12 - x0, PAGE_FEET - y1))
				n = f"pixellab_{anim}_{d}_{i}"
				c.save(os.path.join(dst, n + ".png"))
				names.append(n)
			sign = {"east": 1, "west": -1}.get(d, 0)
			for cid, label, t in ((f"pixellab_{anim}_{d}", "ความเร็วดู", ms), (f"pixellab_{anim}_{d}_game", "ความเร็วในเกม", game_ms)):
				if t is None:
					continue
				clips.append({"group": group, "id": cid, "label": f"PixelLab · {th} · {d} · {label} (ทดลอง 18 ต.ค. · จาก master v2)",
					"frames": names, "ms": t, "loop": True, "w": W, "travel": travel * sign, "src": [f"pixellab {anim} {d}"]})
	json.dump({"_doc": "PixelLab ท่าจาก master v2 · tools/sprites/pixellab_walk.py page · ร่าง ยังไม่เข้าเกม", "clips": clips},
		open(os.path.join(dst, "index.json"), "w"), ensure_ascii=False, indent=1)
	print("คลิป", [c["id"] for c in clips], "→", dst)


if __name__ == "__main__":
	cmd = sys.argv[1] if len(sys.argv) > 1 else "ref"
	{"ref": make_ref, "balance": balance, "character": character, "fetch": fetch, "page": page,
	 "walk": lambda: walk(sys.argv[2:] or ["east"]),
	 "slash": lambda: walk(sys.argv[2:] or ["west"], "slash"),
	 "slash2": lambda: walk(sys.argv[2:] or ["west"], "slash2"),
	 "prompt": lambda: show_prompt(sys.argv[2], (sys.argv[3:] or [None])[0]),
	 "anim": lambda: anim(sys.argv[2], sys.argv[3:] or None),
	 "vfx_frames": lambda: vfx_frames(sys.argv[2] if len(sys.argv) > 2 else "slash2_trail"),
	 "state": lambda: make_state(sys.argv[2] if len(sys.argv) > 2 else "fight_knife"),
	 "fetch_state": lambda: fetch_state(sys.argv[2] if len(sys.argv) > 2 else "fight_knife"),
	 "rot8": lambda: rot8(sys.argv[2]),
	 "vfx": lambda: vfx(sys.argv[2] if len(sys.argv) > 2 else "slash2_trail")}[cmd]()
