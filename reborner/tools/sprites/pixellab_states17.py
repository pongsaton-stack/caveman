#!/usr/bin/env python3
"""State ท่าตัวสำหรับต้นไม้ 17 ท่า × 6 สาย (kwan 19 ต.ค. 2026 "รองรับท่าที่ต้องใช้ศาสตร์การต่อสู้ทุกแขนงแล้วใช่ไหม" → เลือก "1" ทำรายการให้ตรวจก่อนเจน)

State = ตัว Rion เดิมเปลี่ยนท่า/ของในมือ ครบ 4 ทิศ (/create-character-state · ผืน 96 · 15 gen ต่อ State ตามที่หักจริง 19 ต.ค.)
ใช้เป็นภาพเริ่ม (keep_first_frame / custom_start_frame) หรือภาพจบ (end_frame) ของท่าขยับ — แทนการให้ PixelLab คิดท่าตัวเองจากภาพยืนมือเปล่า
ของในมือ = อาวุธตัวแทนกิ่ง (REP ใน pixellab_skills.py) · prio 1 = ท่าตัวที่โค้ดทำไม่ได้แน่นอน · prio 2 = ใช้ State อื่นแล้วขยับด้วยโค้ดแทนได้ถ้าต้องประหยัด
ใช้: python3 tools/sprites/pixellab_states17.py <out.md>  → รายการให้ kwan ตรวจ · pixellab_walk.py โหลด STATES17 เข้า STATES เอง (state <ชื่อ>)
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixellab_skills import REP  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCHOOL = {"SL": "คม", "BT": "ทุบ", "PT": "แทง", "RG": "ยิง", "DV": "กล", "FS": "มือเปล่า"}
STANCE = "Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack."

# (ชื่อ State, กิ่งอาวุธ A/B/C, prio, ชื่อไทย, ท่าที่ใช้, ท่าตัว (อังกฤษ) · held=None = ใช้อาวุธของกิ่ง · held="..." = ของเฉพาะท่า)
P = [
	# ── คม ──
	("SL_A_stance", "A", 1, "ยืนสู้ถือมีด (ทำแล้ว = fight_knife)", "bl0 bl1 bl2 bl7 bl8 bl9 bl16", STANCE),
	("SL_B_stance", "B", 1, "ยืนสู้ถือเคียว", "bl3 bl4 bl10 bl11 bl12", STANCE),
	("SL_C_stance", "C", 1, "ยืนสู้ถือคัตเตอร์", "bl5 bl6 bl13 bl14 bl15", STANCE),
	("SL_A_overhead", "A", 2, "ง้างมีดเหนือไหล่", "bl0 bl2", "Wind-up: the knife is raised high above and behind the front shoulder, elbow up, ready to slash diagonally downward; one step forward."),
	("SL_A_lunge", "A", 1, "พุ่งทั้งตัวเอนหน้า", "bl1 bl16", "Long forward lunge: front knee deeply bent, back leg straight, whole body leaning far forward, knife arm fully extended forward at chest height."),
	("SL_A_low", "A", 1, "ย่อต่ำฟันข้อเท้า", "bl7", "Very low crouch, one knee almost touching the ground, body bent forward, knife swept low near the ground in front."),
	("SL_A_twohand", "A", 1, "จับมีดสองมือเหนือหัว", "bl8", "Both hands grip the knife handle together, raised straight above the cap, ready to chop straight down; feet apart."),
	("SL_A_coiled", "A", 2, "เกร็งตัวรวมแรง (ฟันเดียวสุดแรง)", "bl9", "Coiled, tense stance before one all-out slash: deep stance, torso twisted back, knife drawn back at the rear hip, eyes fixed forward."),
	("SL_B_sweep", "B", 1, "บิดเอวกวาดเคียวแนวนอน", "bl3 bl4 bl12", "Mid horizontal sweep at waist height: torso twisted, sickle arm stretched straight out to the side, back arm out for balance."),
	("SL_B_run", "B", 2, "วิ่งพุ่งถือเคียวต่ำ", "bl10", "Running forward fast, body leaning forward, mid-stride with one foot off the ground, sickle held low and back ready to cut while passing."),
	("SL_B_throw", "B", 1, "ขว้างเคียวแล้ว (มือว่าง)", "bl11", "Follow-through after a sidearm throw: throwing arm extended forward with an open empty hand, body turned into the throw.", "nothing in the hands (the sickle has just been thrown)"),
	("SL_C_draw", "C", 1, "มือวางที่ด้าม พร้อมชัก (ไออิโด)", "bl5", "Iaido-like ready pose: body leaned slightly forward, front hand resting on the box cutter held at the rear hip, ready to draw and cut in one motion."),
	("SL_C_slither", "C", 1, "ย่อต่ำก้าวไขว้ขา", "bl13", "Low sneaking crouch with crossed legs mid-step, body close to the ground, cutter held low and close to the body."),
	("SL_C_guard", "C", 1, "คัตเตอร์ขวางตัวรอสวน", "bl15", "Defensive wait pose for a counter: cutter held horizontally across the chest, back hand near the chest, knees bent, still facing forward in side view."),
	# ── ทุบ ──
	("BT_A_stance", "A", 1, "ยืนสู้ถือค้อน", "bt0 bt1 bt2 bt7 bt8 bt9 bt16", STANCE),
	("BT_B_stance", "B", 1, "ยืนสู้ถือไม้กวาด", "bt3 bt4 bt10 bt11 bt12", STANCE),
	("BT_C_stance", "C", 1, "ยืนสู้ถือกระทะ", "bt5 bt6 bt13 bt14 bt15", STANCE),
	("BT_A_overhead", "A", 1, "ยกค้อนเหนือหัวสองมือ", "bt0 bt2 bt16", "Both hands raised high above the head holding the hammer, back slightly arched, ready to smash straight down."),
	("BT_A_windback", "A", 1, "ง้างค้อนไปหลังเต็มแขน", "bt1 bt9", "Full wind-up: hammer swung far back behind the body at shoulder height, torso twisted away from the target, front arm reaching forward."),
	("BT_A_lowsweep", "A", 1, "ย่อต่ำเหวี่ยงเลียดพื้น", "bt7", "Deep low crouch, hammer swinging horizontally just above the ground at knee height."),
	("BT_A_reverse", "A", 2, "กลับด้านค้อน สับด้วยด้านเขี้ยว", "bt8", "Hammer flipped so the claw side points down, raised above the shoulder ready to hack down."),
	("BT_B_sumo", "B", 1, "ยกเข่าสูงแบบซูโม่", "bt3", "Sumo shiko stomp: one leg lifted high to the side with the knee bent, standing on the other leg, broom held upright in both hands planted beside the body."),
	("BT_B_overhead", "B", 2, "ยกไม้กวาดเหนือหัวสองมือ", "bt4", "Broom raised high above the head with both hands, about to slam down on the ground."),
	("BT_B_swing", "B", 1, "เหวี่ยงไม้กวาดแนวนอน", "bt10 bt11 bt12", "Broom held horizontally with both hands mid swing at waist height, torso twisted, like a staff sweep."),
	("BT_C_bind", "C", 2, "ใช้กระทะขัดล็อกอาวุธ", "bt13", "Frying pan pushed forward at chest height with the flat side out, as if pressing against and locking an enemy weapon; back hand bracing the handle."),
	("BT_C_forearm", "C", 1, "กระทะแนบแขน ก้าวลึก (ไม้ศอก)", "bt14", "Deep forward step, frying pan held flat along the forearm like a shield, shoulder driving forward."),
	("BT_C_guard", "C", 1, "กระทะทแยงหน้าตัวรอสวน", "bt15", "Defensive wait pose for a counter: frying pan held diagonally in front of the body, knees bent, still in side view."),
	# ── แทง ──
	("PT_A_stance", "A", 1, "ยืนสู้ถือไขควง", "pt0 pt1 pt2 pt7 pt8 pt9 pt16", STANCE),
	("PT_B_stance", "B", 1, "ยืนสู้ถือหอกไม้ไผ่", "pt3 pt4 pt10 pt11 pt12", STANCE),
	("PT_C_stance", "C", 1, "ยืนสู้ถือส้อม", "pt5 pt6 pt13 pt14 pt15", STANCE),
	("PT_A_lunge", "A", 1, "ลันจ์ฟันดาบ แขนเหยียดสุด", "pt1 pt2 pt16", "Fencing lunge: front knee deeply bent, back leg straight, rear arm extended back for balance, front arm fully extended forward thrusting the screwdriver."),
	("PT_A_lowstab", "A", 1, "ก้มต่ำแทงข้อพับ", "pt7", "Crouched very low, stabbing forward at knee height, head kept low."),
	("PT_A_halfgrip", "A", 2, "จับสองมือแทงสั้นแม่น", "pt8", "Both hands grip the screwdriver close to the chest, short precise stab forward, elbows tucked."),
	("PT_B_spin", "B", 1, "หมุนหอกเหนือหัว", "pt4 pt9", "Bamboo spear held horizontally above the head with both hands, mid spin, body upright and braced."),
	("PT_B_reach", "B", 1, "แทงหอกยืดสุด", "pt3 pt11 pt12", "Long spear thrust: both hands at the rear of the shaft, arms fully extended forward, front foot stepped forward, spear level at chest height."),
	("PT_B_sweep", "B", 1, "จับปลายด้ามกวาดครึ่งวง", "pt10", "Holding the very end of the spear shaft with both hands, spear swung wide horizontally to the front side."),
	("PT_C_feint", "C", 2, "ทำท่าแทงสูง (หลอก)", "pt13", "Feint: fork raised high at head level as if about to stab high, weight on the back foot."),
	("PT_C_guard", "C", 1, "ชี้ปลายส้อมรอสวน", "pt15", "Fencing guard waiting to counter: front arm extended, fork point aimed at the target, back hand raised behind, knees bent, side view."),
	# ── ยิง ──
	("RG_A_stance", "A", 1, "ยืนถือธนูพร้อมยิง", "rg0 rg1 rg2 rg6 rg7 rg8 rg9 rg16", STANCE),
	("RG_B_stance", "B", 1, "ยืนถือปืนกระดาษสองมือ", "rg3 rg4 rg11 rg12", STANCE),
	("RG_C_stance", "C", 1, "ยืนถือปืนฉีดน้ำ", "rg5 rg13 rg14 rg15", STANCE),
	("RG_A_draw", "A", 1, "ง้างธนูเต็มเล็งตรง", "rg1 rg2 rg6 rg8", "Kyudo full draw: bow arm extended straight forward, string pulled back to the cheek with the back hand, arrow level, body upright and still."),
	("RG_A_kneel", "A", 1, "คุกเข่าข้างเดียวยิงต่ำ", "rg7", "Kneeling on one knee, bow drawn and aimed low at an enemy's legs."),
	("RG_A_sky", "A", 1, "เอนหลังยิงขึ้นฟ้า", "rg4 rg9 rg12", "Leaning back, bow drawn and aimed steeply up at the sky at about 60 degrees."),
	("RG_B_bolas", "B", 1, "หมุนโบลาเหนือหัว", "rg10", "One arm raised above the head swinging a cord with two weights (improvised bolas) in a circle, other arm out for balance.", "a cord with a small weight tied to each end, swung above the head"),
	("RG_B_backjump", "B", 1, "กระโดดถอยหันกลับยิง", "rg11", "In mid-air jumping backward, torso twisted to aim the confetti gun back toward the target, legs tucked."),
	("RG_C_underarm", "C", 2, "เหวี่ยงแขนจากล่างยิงโค้ง", "rg14", "Underhand swing: shooting arm swung low to high in front, aiming upward to lob a shot over the front row."),
	("RG_C_hip", "C", 2, "ยิงเร็วจากเอว", "rg13", "Quick draw from the hip: water pistol held at waist height pointed forward, body turned sideways."),
	("RG_C_lowready", "C", 1, "ถือปืนต่ำรอยิงสวน", "rg15", "Ready-to-counter pose: water pistol held low pointing at the ground in front, knees bent, eyes on the target, side view."),
	# ── กล ──
	("DV_A_stance", "A", 1, "ยืนถือรีโมต", "dv0 dv1 dv2 dv7 dv8 dv9 dv16", STANCE),
	("DV_B_stance", "B", 1, "ยืนถือแบต+คีมคีบ", "dv3 dv4 dv10 dv11 dv12", STANCE),
	("DV_C_stance", "C", 1, "ยืนถือคีม", "dv5 dv6 dv13 dv14 dv15", STANCE),
	("DV_A_point", "A", 1, "ชี้นิ้ว/กดรีโมตสั่งการ", "dv0 dv1 dv6", "Commanding pose: front arm extended toward the target pressing the remote's button with the thumb, other hand pointing forward."),
	("DV_A_release", "A", 1, "ชูสองมือปล่อยอุปกรณ์", "dv2 dv16", "Both arms raised forward and up as if releasing small devices into the air, remote still in the front hand."),
	("DV_A_crank", "A", 1, "ง้างคันโยกหน้าไม้กล", "dv7", "Holding a small boxy repeating crossbow at the hip with the back hand pulling its top lever back.", "a small wooden repeating crossbow with a lever on top"),
	("DV_A_drill", "A", 1, "ดันสว่านเจาะไปหน้า", "dv8", "Leaning forward pushing a handheld electric drill with both hands toward the target.", "a handheld electric drill held with both hands"),
	("DV_A_tripod", "A", 1, "คุกเข่าตั้งขาตั้งเครื่องยิง", "dv9", "Kneeling beside a small tripod launcher, one hand pulling back its large bolt, the other steadying it.", "a small tripod launcher on the ground with a large bolt"),
	("DV_B_poles", "B", 1, "แตะสองขั้วไฟฟ้า", "dv3", "Both arms forward touching the two jumper-cable clamps together in front of the chest, small sparks only between the clamps."),
	("DV_B_throw", "B", 1, "ปาถุงผง", "dv10", "Overhand throw follow-through: front arm extended forward, small cloth pouch just leaving the hand.", "a small cloth pouch"),
	("DV_B_hose", "B", 1, "ถือหัวสายพ่น กวาดหน้า", "dv12", "Holding a hose nozzle in both hands pointed forward and sweeping, battery on the ground behind.", "a hose nozzle connected by a hose to the battery"),
	("DV_C_place", "C", 1, "คุกเข่าวางของบนพื้น", "dv4 dv11 dv13 dv15", "Kneeling on one knee, placing a small device on the ground in front with the pliers, back hand on the knee."),
	("DV_C_hook", "C", 1, "เหวี่ยงตะขอเชือกเหนือหัว", "dv14", "Swinging a rope with a metal hook in a circle above the head with the front arm.", "a rope with a small metal grappling hook"),
	# ── มือเปล่า ──
	("FS_A_stance", "A", 1, "การ์ดมวยใส่นวม", "fs0 fs1 fs2 fs7 fs8 fs9 fs16", "Boxing guard: both gloved fists raised in front of the chin, elbows in, knees bent, light on the feet."),
	("FS_B_stance", "B", 1, "ยืนพร้อมผ้าพันมือ", "fs3 fs4 fs10 fs11 fs12", STANCE),
	("FS_C_stance", "C", 1, "ยืนพร้อมถุงมือหนัง", "fs5 fs6 fs13 fs14 fs15", STANCE),
	("FS_A_jab", "A", 1, "แย็บ แขนหน้าเหยียด", "fs0 fs1 fs2", "Jab: front arm fully extended straight forward at face height, rear fist guarding the chin."),
	("FS_A_lowkick", "A", 1, "เตะตัดขามวยไทย", "fs7", "Muay Thai low roundhouse kick: hips rotated, rear shin swinging into the opponent's thigh, arms guarding the face."),
	("FS_A_elbow", "A", 1, "หมุนตัวศอกกลับ", "fs8", "Spinning back elbow: body turned with the back partly toward the target, rear elbow swinging horizontally at head height."),
	("FS_A_knee", "A", 1, "เข่าโดด ล็อกคอ", "fs16", "Muay Thai knee strike: one knee driven up high to chest level, both hands reaching forward as if clinching."),
	("FS_A_bigpunch", "A", 2, "หมัดตรงเต็มแรงพร้อมตะโกน", "fs9", "All-out straight punch: deep stance, rear arm fully extended forward, mouth open shouting."),
	("FS_B_throw", "B", 1, "ทุ่มข้ามไหล่ (ยูโด)", "fs10", "Judo shoulder throw entry: back turned to the target, knees bent low, both hands gripping forward over the shoulder as if pulling an opponent across the back."),
	("FS_B_capoeira", "B", 1, "ย่อมือแตะพื้นกวาดขา", "fs11", "Capoeira leg sweep: crouched very low, one hand on the ground, one leg extended straight sweeping along the ground."),
	("FS_B_spinkick", "B", 1, "เตะหมุนกลางอากาศ", "fs12", "Taekwondo jumping spin kick: in mid-air, body horizontal-turning, one leg extended straight out at head height."),
	("FS_B_palm", "B", 1, "ผลักฝ่ามือไทเก๊ก", "fs3 fs4", "Tai chi push: both palms pushed forward at chest height, fingers up, weight shifted onto the front leg."),
	("FS_C_punch", "C", 2, "หมัดตรงคาราเต้", "fs5 fs6", "Karate straight punch: rear fist fully extended forward at chest height, other fist pulled back to the hip."),
	("FS_C_slip", "C", 1, "ส่ายหัวหลบ", "fs13", "Boxing slip: upper body bent sideways and down, head moved off-line, fists still up."),
	("FS_C_lock", "C", 1, "จับบิดข้อ / ไอคิโด", "fs14 fs15", "Joint lock grip: both hands forward at chest height gripping and twisting an invisible wrist, body turning into the lock."),
]

BASE = ("Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, "
	"messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. "
	"In side views stay in a true side view facing the same direction as the source rotation. ")
NO = "No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text."


def edit_text(s):
	name, br, prio, th, techs, pose = s[:6]
	held = s[6] if len(s) > 6 else REP[(SCHOOL[name[:2]], br)]
	return BASE + f"Held item: {held}. Pose: {pose} " + NO


STATES17 = {s[0]: {"seed": 27, "frame": None, "edit": edit_text(s), "th": s[3], "techs": s[4].split(), "prio": s[2]} for s in P}


def check():
	rows = list(csv.DictReader(open(os.path.join(ROOT, "docs/design/skill_trees_17.csv"), encoding="utf-8")))
	ids = {r["tech_id"] for r in rows}
	used = {t for s in STATES17.values() for t in s["techs"]}
	bad = [(k, len(v["edit"])) for k, v in STATES17.items() if len(v["edit"]) > 1000]
	return sorted(ids - used), sorted(used - ids), bad


def write_md(out):
	missing, extra, bad = check()
	n1 = sum(1 for s in P if s[2] == 1)
	L = ["# รายการ State ท่าตัว · ต้นไม้ 17 ท่า × 6 สาย (ร่างให้ kwan ตรวจ · 19 ต.ค. 2026)", "",
		f"สร้างจาก `tools/sprites/pixellab_states17.py` · {len(P)} State (ทำแล้ว 1: SL_A_stance = fight_knife) · prio 1 = {n1} · prio 2 = {len(P) - n1}",
		f"ราคา: 15 gen/State (หักจริง 19 ต.ค.) → ทั้งหมด ≈ {(len(P) - 1) * 15} gen · เฉพาะ prio 1 ≈ {(n1 - 1) * 15} gen · ท่าขยับจาก State อีกท่าละ 2–3 gen (102 ท่า ≈ 300 gen)",
		f"ตรวจอัตโนมัติ: ทุกท่าในต้นไม้มี State รองรับ {'ครบ' if not missing else 'ขาด ' + ' '.join(missing)} · คำสั่งยาวเกิน 1000 ตัวอักษร {len(bad)} รายการ",
		"", "ของในมือ = อาวุธตัวแทนกิ่ง (A/B/C) จาก `REP` · ท่าที่ต้องใช้ของเฉพาะ (โบลา หน้าไม้กล สว่าน ขาตั้ง ถุงผง สายพ่น ตะขอ) ระบุแยก", ""]
	for code, sch in SCHOOL.items():
		L += [f"## {sch}", "", "| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |", "|---|---|---|---|---|"]
		for s in P:
			if s[0][:2] == code:
				L.append(f"| `{s[0]}` | {s[1]} | {s[2]} | {s[3]} | {s[4]} |")
		L.append("")
	L += ["## คำสั่ง PixelLab เต็มของแต่ละ State", ""]
	for k, v in STATES17.items():
		L += [f"**{k}** · {v['th']} ({len(v['edit'])} ตัวอักษร)", "", "```", v["edit"], "```", ""]
	open(out, "w", encoding="utf-8").write("\n".join(L))
	return missing, extra, bad


if __name__ == "__main__":
	print(write_md(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs/design/STATE_POSES_17.md")), len(P), "states")
