"""คำสั่ง PixelLab ท่าในต้นไม้ 17 ท่า × 6 สาย (102 ท่า · kwan 18 ต.ค. 2026 เลือก "3 แล้ว 1": ตัดชีตอาวุธก่อน แล้วเขียนคำสั่งครบ)
ใช้ผ่าน pixellab_walk.py: `python3 tools/sprites/pixellab_walk.py prompt bl3` ดูคำสั่งเต็ม · `anim bl3` เจนจริง (เสียเครดิต)
กฎ PIXELLAB_PROMPTS.md: ทิศล็อก (ท่าในศึก = west) · ของในมือ · จังหวะทีละเฟรม (จำนวนจังหวะ = จำนวนเฟรม) · โมเมนตัม · คงที่ · ห้าม · CHARACTER + STYLE
ของในมือ = อาวุธตัวแทนของกิ่ง (ชิ้นแรกในรายการ skill17_content.WEAPONS) · ราก/ไม้ตาย = ตัวแทนกิ่ง A
สายกล: อุปกรณ์ที่บิน/วาง/ลอย (โดรน ฝูงกล หนาม กับดัก ป้อม) PixelLab วาดได้ไม่แน่นอน → ตัวละครถือรีโมตทำท่าสั่ง · ตัวอุปกรณ์/กระสุนทำด้วยโค้ด
แสง/เอฟเฟกต์ใหญ่ทำด้วยโค้ดทุกท่า (kwan 18 ต.ค. ข้อ 3)
"""

# อาวุธมือเดียวอยู่มือขวาเสมอ = มือเดียวกับภาพเริ่ม (State) · kwan 19 ต.ค. จับได้ว่าท่าฟัน bl0 สลับมือกลางท่า เพราะคำเดิม "front hand" (= มือซ้ายเมื่อหันซ้าย) ขัดกับภาพ State ที่ถือมือขวา
ONE_HAND = ("held in the RIGHT hand, the same hand that holds it in the start image, in every frame; it never passes to the other hand; "
	"the left hand stays empty, low near the chest, and never covers the face")
ONE_HAND_NOT = ["the held item switching to the other hand", "the empty left hand raised in front of the face"]

# อาวุธตัวแทน (อังกฤษ · ขนาดเทียบตัว · มือไหน)
REP = {
	("คม", "A"): "a short kitchen knife, blade about the length of the hand, " + ONE_HAND,
	("คม", "B"): "a farm sickle with a short wooden handle and a curved steel blade, " + ONE_HAND,
	("คม", "C"): "a small yellow box cutter (utility knife) with a short slim blade, " + ONE_HAND,
	("ทุบ", "A"): "a claw hammer with a wooden handle about forearm length, " + ONE_HAND,
	("ทุบ", "B"): "a straw broom about as tall as the character, held with both hands near the middle of the handle",
	("ทุบ", "C"): "a black cast-iron frying pan, by its handle, " + ONE_HAND,
	("แทง", "A"): "a screwdriver with a red handle, shaft about hand length, like a dagger, " + ONE_HAND,
	("แทง", "B"): "a bamboo spear about as tall as the character, sharpened tip, held with both hands",
	("แทง", "C"): "a large silver dinner fork, " + ONE_HAND,
	("ยิง", "A"): "a simple wooden short bow with arrows; the bow is held in the front hand and the string is drawn with the back hand",
	("ยิง", "B"): "a toy confetti popper gun held with both hands",
	("ยิง", "C"): "a green and blue plastic water pistol " + ONE_HAND,
	("กล", "A"): "a small handheld remote control box with a short antenna, " + ONE_HAND,
	("กล", "B"): "a small car battery with two jumper-cable clamps, battery carried in the back hand, a clamp in the front hand",
	("กล", "C"): "a pair of steel pliers " + ONE_HAND,
	("มือเปล่า", "A"): "red boxing gloves worn on both hands",
	("มือเปล่า", "B"): "white cloth hand wraps on both hands",
	("มือเปล่า", "C"): "brown fingerless leather gloves on both hands",
}

def B(s):
	return [x.strip() for x in s.split(";") if x.strip()]

# จังหวะทีละเฟรม (หันซ้าย) · จำนวน = จำนวนเฟรม (คู่ 8/12/16)
BEATS = {
	# ---------------- คม ----------------
	"bl0": B("ready stance facing left, knife low in front; step forward with the front foot, the right hand raises the knife back over the right shoulder, the left hand stays low at the chest; wind-up peak, knife still in the right hand, blade pointing up and back behind the shoulder; the right arm swings the knife forward and down toward the left; the right hand cuts diagonally down in front of the body as the front foot lands; follow-through low by the front knee; pull back toward the chest; ready stance again"),
	"bl1": B("ready stance facing left, knees bent low, knife in the right hand (the far arm, behind the chest), the near left arm bent with the empty fist at the chest; crouch deeper, weight on the back foot, the far right hand pulls the knife back low beside the hip, the near left fist stays at the chest in front of the shirt; explode forward, body leaning far forward, back leg pushing, the knife still in the far right hand low at the hip and visible, near left fist at the chest; mid-lunge, both feet off the ground, the far right arm starts reaching the knife forward below the chin, the blade clearly visible, the near left fist still at the chest; front foot lands far ahead, the far right arm extends the knife straight forward at chest height, its shoulder hidden behind the chest, while the near left arm stays bent with the fist visible in front of the shirt; follow-through, the knife sweeps further left past the front of the body in the far right hand, the near left fist still visible at the chest; push back off the front foot, knife returns low in front in the far right hand; ready stance"),
	# ตัดเอ็น · กาลี (kwan 21 ต.ค. ส่งข้อมูลกาลี/เอสคริมา → เลือก "1"): ฟันที่อาวุธ/แขนขาที่ศัตรูใช้โจมตี (ตัดเขี้ยวงู) · ก้าวเข้าเป็นมุมต่ำ · มีดหมุนวงต่อเนื่อง (เรดอนดา) ไม่ค้าง · ถอยด้วยก้าวสั้นหันหน้าหาเป้า ไม่กระโดด
	#   ทุกจังหวะระบุ มีด = แขนขวาฝั่งไกล ไหล่ซ่อนหลังอก · กำปั้นซ้ายใกล้อยู่หน้าอกเห็นชัด (บทเรียน bl1 รอบ 1 ฟันมือซ้าย)
	"bl7": B("low Kali fighting stance facing left, knees bent, the knife held at chest height in the far right hand, the near left fist guarding in front of the chest; "
		"a quick short step forward and down, body dropping low, the far right hand circles the knife up and back beside the right shoulder, the near left fist stays in front of the chest; "
		"front knee bends deep, body very low and leaning forward, the far right hand brings the knife down in a small circle in front of the body, blade visible; "
		"the front foot lands: the far right arm slashes the knife across low in front of the front knee, at the height of an enemy's paw or wrist, the blade horizontal and clearly visible, the near left fist still at the chest; "
		"follow-through: the far right hand keeps the knife moving, circling it up past the front of the body toward the chest, weight starting to shift back; "
		"a short step back with the back foot, still facing left, the knife back at guard in front of the chest in the far right hand, near left fist at the chest; "
		"a second short step back, still facing left, knees bent, knife at guard; "
		"low Kali fighting stance again, same as the first frame"),
	"bl8": B("ready stance facing left; grip the knife with both hands and raise it straight above the head; small hop forward, body stretched tall; at the top of the hop, knife high; drop down chopping straight down in front of the face; land with knees bent, knife low in front; rise up; ready stance"),
	"bl2": B("ready stance facing left; slash from upper right down to lower left; wrist turns, slash from lower left up to upper right; wrist turns again, raise the knife high; third slash straight down; knife low, body leaning forward; pull back; ready stance"),
	"bl9": B("ready stance facing left; slowly raise the knife high above the head with both hands; hold, whole body tense, knees bent deep, mouth shouting; still tense, leaning back slightly; sudden full-power downward cut, body lunging forward; blade at the bottom, front knee deeply bent; hold the finish for a moment; straighten up into ready stance"),
	"bl3": B("ready stance facing left; twist the waist back, knife held out to the right side at waist height; start the swing, hips turning; knife sweeps horizontally across the front at waist height toward the left; sweep continues past the left side; body fully turned, arm extended; unwind back; ready stance"),
	"bl10": B("ready stance facing left; lean forward and start running left, knife held low behind; running, knife coming forward; slash forward at chest height while still running, not stopping; keep running past, knife trailing behind; skid to a stop, feet sliding; turn the upper body back slightly; ready stance facing left"),
	"bl11": B("ready stance facing left; draw the knife back behind the head; throw the knife forward with a flick, the hand now empty and extended; the empty hand stays open waiting, body leaning forward; hand still waiting, eyes forward; hand closes catching the returning knife; pull it back to the chest; ready stance holding the knife"),
	"bl4": B("ready stance facing left; arms spread wide, knife held out to the side; start spinning on the spot, body turning away; back toward the viewer for a moment, knife sweeping around; turning back toward the left side; knife sweeps past the front; spin finishes, arms still wide; ready stance"),
	"bl12": B("ready stance facing left; crouch low, knife out to the side; jump up while starting to spin; spinning in the air, knife wide; still spinning in the air, back toward the viewer; second rotation in the air; knife sweeping past the front at the top; begin to come down; land spinning, knife low; spin slows; arms wide finishing; stand up; ready stance"),
	"bl5": B("relaxed stance facing left, knife held low at the hip like a sheathed blade; hand tightens on the handle; one fast draw-and-cut forward at waist height; blade fully extended forward, body still; snap the knife back to the hip; return to the relaxed stance; small breath; ready stance"),
	"bl13": B("ready stance facing left; drop very low, knees deeply bent; cross-step forward low, legs crossing; second low step, body close to the ground; short quick slash forward; step back low; rise up slightly; ready stance"),
	"bl14": B("ready stance facing left; quick step diagonally forward and slightly up-screen; step around, body still facing left; slash forward at a far target; step back diagonally; return to the original spot; settle; ready stance"),
	"bl6": B("ready stance facing left, knife in the right hand, left hand open as a guard; raise the knife up to the right; slash diagonally down to the left; raise the knife up to the left; slash diagonally down to the right, crossing the first cut; follow-through low; pull back; ready stance"),
	"bl15": B("side view facing left, knees bent low, box cutter held close in front of the chest, blade pointing left, waiting; same side view, waiting, eyes on the left; same side view, the box cutter flicks up to the left to knock an incoming hit aside; same side view, cutter arm pushed up and out to the left after the parry; same side view, step forward with the front foot and slash down to the left; same side view, follow-through low near the front knee; same side view, pull the cutter back to the chest; side view facing left, knees bent, cutter in front of the chest, same as the first frame"),
	"bl16": B("same side view facing left, standing on one spot, knife held low in front, knees bent; same side view on the same spot, crouch lower gathering strength, knife pulled back to the hip; same side view on the same spot, slash 1: knife cuts high from upper right to the left at head height; same side view on the same spot, slash 2: knife cuts low across the knees toward the left; same side view on the same spot, raise the knife high above the head with the right hand; same side view on the same spot, slash 3: knife cuts straight down in front of the face; same side view on the same spot, slash 4: knife cuts horizontally at chest height toward the left, front foot steps forward; same side view on the same spot, pull the knife far back over the shoulder for the last cut, body coiled; same side view on the same spot, slash 5, the strongest: full diagonal cut down to the left, body leaning forward, front knee deeply bent; same side view on the same spot, hold the finish, knife low near the front foot; same side view on the same spot, slowly straighten up, knife lowered; same side view facing left on the same spot, ready stance, knife held low in front, same as the first frame"),
	# ---------------- ทุบ ----------------
	"bt0": B("ready stance facing left, hammer held low; raise the hammer above the head; peak of the raise, body leaning back slightly; swing straight down to the left; hammer hits at waist height in front, front knee bent; recoil bounce; lift back; ready stance"),
	"bt1": B("ready stance facing left; swing the hammer far back behind the body, full arm; twist the hips back, weight on the back foot; swing diagonally forward with the whole body; hammer impacts at chest height in front; follow-through across the body; recover; ready stance"),
	"bt7": B("ready stance facing left; crouch low; swing the hammer low and flat toward the left at knee height; impact low in front; follow-through low; rise; step back; ready stance"),
	"bt8": B("ready stance facing left; flip the hammer around in the hand so the claw side faces forward; raise it high; chop down with the claw side; claw impact in front at chest height; wrench it back out; flip the hammer back; ready stance"),
	"bt2": B("ready stance facing left; crouch deep; jump high, hammer raised with both hands; at the top of the jump, body arched back; fall forward swinging down; land and smash the ground in front with both hands; hammer stuck on the ground, knees deeply bent; lift it back; ready stance"),
	"bt9": B("ready stance facing left; swing the hammer out to the side; spin one full turn with the hammer swinging around, back toward the viewer; turning back toward the left; spin gives momentum, hammer high; smash down in front with full force; ground impact, body low; hold the impact; lift the hammer; step back; settle; ready stance"),
	"bt3": B("ready stance facing left, broom held with both hands; lift the front knee high like a sumo stomp; stomp down hard while slamming the broom head on the ground; impact, body low and wide; hold; lift the broom; stand; ready stance"),
	"bt10": B("ready stance facing left; swing the broom up and to the right; sweep it down in a wide figure-eight in front; second loop sweeping to the left; finish the loop high; bring it down; recover; ready stance"),
	"bt11": B("ready stance facing left, broom held with both hands; sweep the broom low across the ground toward the left; low sweep passes; reverse and swing it up high; smash back down from above; impact; recover; ready stance"),
	"bt4": B("ready stance facing left; crouch deep with the broom; jump high, broom raised over the head; top of the jump; come down fast; slam the broom head into the ground with full force; huge impact pose, knees deeply bent; hold; rise; ready stance"),
	"bt12": B("ready stance facing left, broom held at the end of the handle; start spinning, broom swinging out wide; spinning, back toward the viewer; still spinning faster; release the spin into a downward slam; first ground impact; lift and spin half a turn; second ground slam; hold low; rise; settle; ready stance"),
	"bt5": B("ready stance facing left, frying pan held up; short step forward; quick short swing at shoulder height; pan hits; small bounce back; step back; ready stance; small breath"),
	"bt13": B("ready stance facing left, pan held out; push the pan forward as if catching an enemy weapon; twist the pan to lock it; hold the lock, leaning in; jab forward with the pan handle end; push away; step back; ready stance"),
	"bt14": B("ready stance facing left, pan held close along the forearm; step deep forward, body low, slipping past the front; drive the elbow and pan forward at a far target; impact; withdraw; step back; settle; ready stance"),
	"bt6": B("ready stance facing left; raise the pan high; smash it down hard at foot level in front; impact on the ground, body bent; press down; lift the pan; step back; ready stance"),
	"bt15": B("side view facing left, knees bent low, frying pan held up in front of the chest like a small shield, waiting; same side view, waiting, eyes on the left; same side view, the pan flicks up to the left to knock an incoming hit aside; same side view, pan pushed up and out to the left after the parry; same side view, step forward and swing the pan down to the left; same side view, pan low after the hit; same side view, pull the pan back to the chest; side view facing left, pan in front of the chest, same as the first frame"),
	"bt16": B("ready stance facing left, hammer raised; smash to the left side; lift; smash to the right side; lift high with both hands; jump slightly; smash straight down with full force; ground impact, knees bent deep; press the hammer down; hold; lift; step back; settle; ready stance; small breath; ready stance"),
	# ---------------- แทง ----------------
	"pt0": B("ready stance facing left, screwdriver held like a dagger at the waist; step forward; stab straight forward at chest height; arm fully extended; pull back; step back; ready stance; small breath"),
	"pt1": B("ready stance facing left; sink back onto the back leg; long lunge forward, front knee deeply bent, back leg straight; arm fully extended, screwdriver at the far tip of the reach; hold the lunge; push back; recover; ready stance"),
	"pt7": B("ready stance facing left; duck low; stab low at knee height; tip pushes in; pull back; hop back; rise; ready stance"),
	"pt8": B("ready stance facing left, screwdriver gripped with both hands near the tip; step close; short precise stab at chest height; push and twist; pull out; step back; ready stance; small breath"),
	"pt2": B("ready stance facing left; lunge forward stabbing; push through, arm fully extended; keep pushing forward a step further; body leaning far forward; pull back hard; step back; ready stance"),
	"pt9": B("ready stance facing left, bamboo spear held with both hands; spin the spear around the body once; spinning, spear behind; bring the spear forward, gathering power; huge lunge thrust forward with the whole body; spear fully extended, body nearly horizontal; hold; pull back; step back; settle; ready stance; small breath"),
	"pt3": B("ready stance facing left, spear held long with both hands; stand far back; thrust the spear forward to its full length without stepping in; spear fully extended; hold; pull back; settle; ready stance"),
	"pt10": B("ready stance facing left, spear held at the end of the shaft; swing the spear back to the right; sweep it in a wide half-circle in front at chest height; sweep past the left; arms extended; bring it back; ready stance"),
	"pt11": B("ready stance facing left, spear held with both hands; first quick thrust forward; pull back half way; second quick thrust forward, deeper; fully extended; pull back; step back; ready stance"),
	"pt4": B("ready stance facing left; circle the spear tip in front; small fast stab; another stab slightly higher; another stab lower; final stab forward; pull back; ready stance"),
	"pt12": B("ready stance facing left, spear held with both hands; step forward and stab; stab again; stab again, faster; small step; second wave, stab; stab; stab hardest, fully extended; hold; pull back; step back; settle; ready stance"),
	"pt5": B("ready stance facing left, fork held at the waist; quick short stab forward from the hip; arm extended; snap back; ready stance; tiny bounce; ready stance; small breath"),
	"pt13": B("ready stance facing left; fake a high stab, fork raised; stop halfway; drop and stab low instead; fork extended low; pull back; rise; ready stance"),
	"pt14": B("ready stance facing left; step in a curve diagonally forward; circle around, still facing left; stab forward at a far target; pull back; step back along the curve; settle; ready stance"),
	"pt6": B("ready stance facing left; stab; pull; stab; pull; stab; pull; stab hardest; recover; small step back; ready stance; small breath; ready stance"),
	"pt15": B("side view facing left, knees bent low, fork held forward at chest height pointing left, waiting; same side view, waiting, eyes on the left; same side view, small flick of the fork to the left side to push an incoming hit aside; same side view, fork pushed out to the side after the parry; same side view, lunge forward and stab straight to the left; same side view, arm fully extended; same side view, pull the fork back; side view facing left, fork forward at chest height, same as the first frame"),
	"pt16": B("ready stance facing left, spear held with both hands; crouch; dash forward and stab; pass through; turn and dash back stabbing; dash forward again stabbing; turn and dash back once more; final huge thrust forward; hold the thrust; pull back; skid to a stop; settle; spear upright; lower the spear; small breath; ready stance"),
	# ---------------- ยิง ----------------
	"rg0": B("ready stance facing left, bow held low; raise the bow, nock an arrow; draw quickly; release, the string snaps forward; small recoil; lower the bow; ready stance; small breath"),
	"rg1": B("ready stance facing left; raise the bow and nock an arrow; slow full draw, string at the cheek; hold perfectly still, aiming; still holding, eyes narrowed; release; follow-through, bow arm steady; lower the bow"),
	"rg7": B("ready stance facing left; drop to one knee; nock and draw aiming low; release low; follow-through; stand up; ready stance; small breath"),
	"rg8": B("ready stance facing left; reach back for a heavier arrow; nock it; full deep draw, leaning back slightly; hold; release with force; recoil step back; ready stance"),
	"rg2": B("ready stance facing left; nock an arrow; draw very slowly to the maximum; hold, arms trembling with strain; still holding; release powerfully; body pushed back by the recoil; recover; ready stance"),
	"rg9": B("ready stance facing left; nock an arrow; lean back and aim high into the sky; full draw upward; hold; release upward; watch the sky; lower the bow; ready stance"),
	"rg3": B("ready stance facing left, popper gun held with both hands; aim right side of the enemy line; fire while sweeping the aim to the left; keep firing while sweeping; finish the sweep on the far left; lower the gun; recoil settle; ready stance"),
	"rg10": B("ready stance facing left; swing a cord over the head in a circle; swing faster; release and throw it forward low; arm extended after the throw; pull the arm back; settle; ready stance"),
	"rg11": B("ready stance facing left, popper gun ready; jump backward away from the enemy; turn the upper body in the air and fire; fire again in the air; land backward; recover; ready stance"),
	"rg4": B("ready stance facing left; aim the popper gun high into the sky; fire upward; fire upward again; fire upward a third time; lower the gun; watch; ready stance"),
	"rg12": B("ready stance facing left; aim high into the sky; fire upward; fire again; fire again; reload quickly; aim high again; fire; fire; fire; lower the gun; watch the sky; ready stance"),
	"rg5": B("ready stance facing left; raise the water pistol and aim; hold still aiming; breathe; hold; lower slightly; aim again; ready stance"),
	"rg13": B("ready stance facing left; quick flick from the hip, firing the water pistol without raising it; recoil small; snap back; ready stance; tiny bounce; ready stance; breath"),
	"rg14": B("ready stance facing left; swing the arm from low to high, lobbing the shot upward in an arc; arm high after the throw; watch the arc; lower the arm; settle; ready stance; breath"),
	"rg6": B("ready stance facing left; raise the water pistol with both hands; aim perfectly still; hold; fire one precise shot; recoil; lower; ready stance"),
	"rg15": B("side view facing left, knees bent low, water pistol held low in front pointing at the ground on the left, waiting; same side view, waiting, eyes on the left; same side view, snap the pistol up to point left at chest height; same side view, fire, small recoil; same side view, fire again; same side view, hold the aim to the left; same side view, lower the pistol; side view facing left, pistol held low, same as the first frame"),
	"rg16": B("ready stance facing left, bow ready; nock and shoot; turn slightly and shoot; turn back and shoot; jump and shoot in the air; land and shoot; draw the last arrow fully; hold; release the final shot; recoil; lower the bow; turn; settle; small breath; ready stance; ready stance"),
	# ---------------- กล (อุปกรณ์/กระสุนทำด้วยโค้ด) ----------------
	"dv0": B("ready stance facing left, remote held in the right hand; raise the remote and point it at the enemy; press the button firmly; hold the pose pointing; lower the remote; ready stance; small breath; ready stance"),
	"dv1": B("ready stance facing left; hold the remote up; press and swipe forward as if sending something flying; arm extended forward; watch; lower; ready stance; breath"),
	"dv7": B("ready stance facing left; point the remote forward; press the button; press again quickly; hold pointing; lower; ready stance; breath"),
	"dv8": B("ready stance facing left; brace the legs; push both arms forward as if driving a heavy machine forward; push harder, leaning in; hold; release; step back; ready stance"),
	"dv2": B("ready stance facing left; raise the remote high; circle the remote in the air directing many things; point forward; keep pointing; lower; nod; ready stance"),
	"dv9": B("ready stance facing left; kneel and pretend to set up a heavy launcher; pull a lever back with both hands; strain; release the lever; recoil, leaning back; stand up; settle; ready stance; breath; ready stance; ready stance"),
	"dv3": B("ready stance facing left, clamp in the right hand; touch the clamp to the battery terminal; spark, flinch slightly; thrust the clamp forward at the enemy; hold; pull back; ready stance; breath"),
	"dv10": B("ready stance facing left; pull out a small pouch with the back hand; throw it forward; arm extended; cover the face with the arm; lower the arm; ready stance; breath"),
	"dv11": B("ready stance facing left; reach into the pocket; scatter something forward low across the ground in a wide sweep; second scatter; arm low; stand up; ready stance; breath"),
	"dv4": B("ready stance facing left; crouch and place something on the ground in front; press it; stand up and step back; hold a hand out; lower; ready stance; breath"),
	"dv12": B("ready stance facing left; hold the clamp forward like a nozzle; sweep it across from right to left; sweep back from left to right; hold forward; lower; step back; settle; ready stance; breath; ready stance; ready stance"),
	"dv5": B("ready stance facing left; raise the pliers up to the eyes like a scope; look; look closely; lower; nod; ready stance; breath"),
	"dv13": B("ready stance facing left; crouch and lay something on the ground; step back; yank the hand back hard as if pulling a rope; hold the pull; release; ready stance; breath"),
	"dv14": B("ready stance facing left; swing a hook on a rope over the head; throw it forward high over the front; pull the rope back hard with both hands; lean back pulling; release; ready stance; breath"),
	"dv6": B("ready stance facing left; point the pliers at the enemy; hold pointing; nod; lower; ready stance; breath; ready stance"),
	"dv15": B("side view facing left, crouching, pressing the pliers down onto the ground in front; same side view, stand up with knees bent, pliers held in front of the chest, waiting; same side view, waiting, eyes on the left; same side view, jerk the pliers upward to the left as if springing a trap; same side view, thrust the pliers forward to the left; same side view, arm extended; same side view, pull the pliers back; side view facing left, knees bent, pliers in front of the chest"),
	"dv16": B("ready stance facing left, remote ready; crouch and assemble something in front; stand and press the remote; point high; press again; point high again; watch; nod; lower; step back; settle; breath; ready stance; ready stance; ready stance; ready stance"),
	# ---------------- มือเปล่า ----------------
	"fs0": B("boxing stance facing left, gloves up; quick jab forward with the front hand; arm extended; snap back; guard; tiny bounce; boxing stance; breath"),
	"fs1": B("boxing stance facing left; straight punch with the front hand; straight punch with the back hand; straight punch with the front hand again; fist extended; pull back; guard; boxing stance"),
	"fs7": B("boxing stance facing left; turn the hips; low roundhouse kick with the back leg to the thigh; impact; leg returns; stance; guard; boxing stance"),
	"fs8": B("boxing stance facing left; step forward; spin the body around, back toward the viewer; swing the back elbow around into the face; elbow impact; finish the turn; guard; boxing stance"),
	"fs2": B("boxing stance facing left; punch; punch; punch; punch; punch; final punch hardest; arm extended; pull back; guard; tiny bounce; boxing stance"),
	"fs9": B("stance facing left, fists at the hips; breathe in deeply; tense the whole body; one straight punch with full power, shouting; fist fully extended; hold the finish; pull back; stance"),
	"fs3": B("guard stance facing left, arms raised blocking; brace; hold; brace; hold; lower; guard; stance"),
	"fs10": B("stance facing left; grab forward with both hands; pull the enemy in; turn the back toward the enemy, bending low; throw over the shoulder forward; throw finishes, arms down; stand up; stance"),
	"fs11": B("stance facing left; drop low with one hand on the ground; sweep the leg around in a wide low circle; sweep continues; second sweep circle; rise; step; stance"),
	"fs4": B("guard stance facing left; absorb, pushed back slightly; plant the feet; push both palms forward hard; palms extended; hold; pull back; guard"),
	"fs12": B("stance facing left; crouch; jump and spin in the air; spinning kick in the air; second spin; second kick; land; stance"),
	"fs5": B("stance facing left; very fast straight punch; fist extended; snap back; stance; tiny bounce; stance; breath"),
	"fs13": B("boxing stance facing left; slip the head to the side dodging; come back and jab; arm extended; snap back; guard; bounce; boxing stance"),
	"fs14": B("stance facing left; grab forward with both hands at wrist height; twist the grabbed arm; hold the lock, leaning; push down; release; step back; stance"),
	"fs6": B("stance facing left; tiny lean forward; extremely fast punch; fist extended; snap back; stance; bounce; stance"),
	"fs15": B("side view facing left, knees bent, both open hands raised in front at chest height, waiting; same side view, waiting, eyes on the left; same side view, both hands catch an incoming push and sweep it down and back to the right; same side view, body turns slightly with the motion but still faces left; same side view, both hands push forward hard to the left; same side view, arms fully extended to the left; same side view, pull the hands back; side view facing left, hands raised in front, same as the first frame"),
	"fs16": B("muay thai stance facing left; jab; cross; front knee strike; elbow strike; roundhouse kick; high knee jump strike; land; elbow down; push kick; guard; bounce; stance; breath; stance; stance"),
}


# ท่าสวน: bl15 รอบแรก (18 ต.ค.) ท่ายืนรอทำให้ตัวหันเข้ากล้อง 3 เฟรม + วาดวงแสงใหญ่ → ทุกจังหวะขึ้นต้น "same side view" · ห้ามแบบระบุของ
COUNTER_NOT = ["a front-facing guard pose", "the chest or face turned toward the viewer", "a glowing ring, circle or shield around the body",
	"speed lines, wind lines or energy streaks", "a defensive stance with both arms crossed in front of the face"]


# ไม้ตายแบบแยกงาน (kwan 18 ต.ค. "ทำเลย"): PixelLab เจนท่าฟันอยู่กับที่ หันซ้ายตลอด · การพุ่ง/พลิกทิศ/ร่างติดตา/รอยฟัน ทำด้วยโค้ด
IN_PLACE = {"bl16"}
IN_PLACE_NOT = ["turning around or facing right", "spinning the body", "jumping off the ground", "moving away from the starting spot",
	"the knife turning into a white streak of light (it stays a solid steel kitchen knife with a dark handle)", "afterimages or duplicate bodies",
	"a glowing ring, circle or arc of light"]


def frames_for(n):
	return n if n % 2 == 0 else n + 1


def skill_moves(rows):
	"""rows = แถวจาก docs/design/skill_trees_17.csv → dict ท่า → spec แบบ MOVES"""
	out = {}
	for r in rows:
		slot = r["slot"]
		if not slot:
			continue
		br = slot[0] if slot[0] in "ABC" else "A"
		beats = BEATS[r["tech_id"]]
		if len(beats) % 2:
			beats = beats + [beats[-1]]
		out[r["tech_id"]] = {"dir": "west", "attack": True, "frames": len(beats), "seed": 27,
			"held": REP[(r["school"], br)], "beats": beats,
			"not": ["the held item disappearing in any frame", "a second copy of the held item", "a sword"]
				+ (ONE_HAND_NOT if ONE_HAND in REP[(r["school"], br)] else [])
				+ (COUNTER_NOT if r.get("effect") == "counter" else [])
				+ (IN_PLACE_NOT if r["tech_id"] in IN_PLACE else []),
			"name": r["name_th"]}
	return out
