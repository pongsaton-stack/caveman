# ชุดคำสั่งเจนท่า Rion (kwan 16 ต.ค. 2026 เลือก "1 หน้าเดียวรวมทุกชีต")

แหล่งความจริงของ prompt ท่าตัวเอกทุกชีตที่ยังขาด · หน้าเว็บสร้างจากไฟล์นี้ด้วย `python3 tools/web/prompt_pack_build.py <out.html>`
แนบทุกชีต 2 ภาพ ตามลำดับ: ภาพ 1 = `flow_trial_v14b_3.jpg` · ภาพ 2 = `rion_flow_ref.png` · ไม่แนบภาพอื่น (บทเรียน 15-1: ภาพหน้าตรงเป็นภาพ 1 หรือแนบไอคอนอาวุธ = หน้าตาเพี้ยน)
14-1 = prompt เดิม (หมวกน้ำเงินทั้งใบ) เปลี่ยนสองย่อหน้าแรกเป็นแบบ 15-1 แก้ไข + ระบุมีดทำครัว · 15-2…15-5 = "แก้ไข" เดิมทุกตัวอักษร · 15-6 = แถวเดิม หัวแบบ 15-1 แก้ไข · 16-1…16-5 = ใหม่

## 14-1 · ท่าศึก
<!-- note: ยืนศึก · ฟัน · โดนตี · ล้ม · วิ่ง · ร่ายพนมมือ · คุกเข่า · ตั้งรับ — เกมใช้ท่าแทนจาก 14-2 อยู่ ได้ชีตนี้แล้วเปลี่ยนเป็นท่าจริงทั้งหมด | cells: 48 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses of image 1; draw only the poses written below. The only weapon in this sheet is a small KITCHEN KNIFE with a wooden handle.

Layout: 8 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell (except jumps). No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

Every frame faces RIGHT (he looks and moves toward the right edge).

Row 1 – battle idle holding the kitchen knife low in his front hand, loop: breathing in and out, slight bob.
Row 2 – knife attack with momentum: 1 stance, 2 run forward, 3 still running, raising the knife, 4 raised high mid-step, 5 arriving: slash downward with a white arc, 6 recover to stance. The knife stays in his hand in every frame.
Row 3 – hurt: 1 hit (eyes shut, body jolts back), 2 stagger back, 3 stagger, 4 catch balance, 5 straighten, 6 back to stance holding the knife.
Row 4 – defeated: 1 staggering, 2 knees buckle, 3 falling forward, 4 hits the ground, 5 lying face down, 6 lying still (knife on the ground beside him).
Row 5 – run cycle holding the knife low, 6 frames, clear alternating legs, both feet off the ground in frames 2 and 5.
Row 6 – cast a spell, no knife: 1 stand, 2 press palms together at the chest, eyes closed, 3 small glow appears at his hands, 4 glow grows, 5 push both palms forward releasing a small ball of light, 6 recover.
Row 7 – kneel, no knife: 1 stand, 2 bend down, 3 one knee down, 4 one knee down with one hand touching the ground, 5 hold, 6 stand back up. Never crawling on all fours.
Row 8 – guard, no knife: 1 stand, 2 cross both forearms in front of the face, 3 hold guard, 4 hit on the guard with a small white spark, 5 hold, 6 lower arms.

Keep his look identical to image 1 in all 48 frames. Output PNG only.
```

## 15-6 · ท่าร่ายเวทย์ 4 สาย
<!-- note: ขาว · ดำ (พนมมือ → ผลักฝ่ามือ) · แดง · อัญเชิญ — เปิดแท็บเวทย์มนต์ในหน้าเทสคืน | cells: 24 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet.

Layout: 4 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell. Keep magic effects SMALL and close to his hands (no big beams or explosions, no effect touching the cell edges).

Every frame faces RIGHT (he looks and casts toward the right edge).

Row 1 – WHITE magic (protective light), a small open brown spell book held in his back hand at the chest. 1 stand. 2 lift the front hand diagonally upward (not straight up, his face must stay visible). 3 small soft white-gold glow at the raised palm. 4 a thin glowing dome line appears in front of him. 5 hold, glow pulses. 6 lower the hand back to stance.
Row 2 – BLACK magic (elemental attack). 1 stand, the spell book floating open beside his shoulder. 2 press both palms together at the chest, eyes closed. 3 a small orange glow between the palms. 4 glow grows, knees bend slightly. 5 push both palms forward, releasing a small fireball flying right. 6 recover, arms lowering.
Row 3 – RED magic (tricks with time and marks), a small open brown spell book held in his back hand. 1 stand. 2 pull the front hand back, holding a red marker pen. 3 swing forward, drawing a small red X mark in the air. 4 the red X glows. 5 push the front palm forward and the X flies right. 6 recover to stance.
Row 4 – SUMMON (calls a guardian from the ash stove), a small open brown spell book held in his back hand. 1 stand. 2 raise the front hand diagonally upward (face still visible). 3 a small circle of orange runes appears on the ground at his feet. 4 the runes glow brighter, small embers rise. 5 sweep the raised hand forward toward the right. 6 recover to stance, embers fading.

Keep his look identical to image 1 in all 24 frames. Output PNG only.
```

## 15-2 · ถืออาวุธระดับ 2
<!-- note: มีดอีโต้ · ไม้อลูมิเนียม · ดินสอคู่ตอกตะปู · หนังสติ๊กท่อเหล็ก · แม็กยิงบอร์ด · ถุงมือหนังน็อต | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. No weapon images are attached — follow the text descriptions.

Layout: 6 rows x 5 columns (exactly 5 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell. EVERY cell must clearly show that row's weapon in his hands — never an empty hand, even during the attack and the follow-through.

Every frame faces RIGHT. Only one weapon per row.

Row 1 – a heavy CLEAVER with a cloth-tape-wrapped handle and a thickened spine (bigger than a kitchen knife), 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc, the weapon still in his hand. 5 recover to stance.
Row 2 – a dented ALUMINUM baseball bat with a cloth-wrapped grip (silver metal, NOT wood), two-handed. 1 stance, held up over the shoulder. 2 run forward with it raised behind the head. 3 cocked far back while still running. 4 arriving: full horizontal swing with a white swing arc. 5 recover to stance.
Row 3 – TWO yellow pencils TAPED together side by side with grey duct tape and a long NAIL sticking out of the tip (NOT a single pencil), held like a short spear in BOTH hands. 1 stance, pointing forward. 2 dash forward, pulled back to the chest. 3 still dashing, lowered. 4 arriving: straight lunge thrust, the weapon clearly visible at the end of his arms, short white thrust line. 5 recover to stance.
Row 4 – a slingshot made of grey STEEL PIPE bent into a Y-fork with a thick black bicycle INNER-TUBE band (NOT a tree-branch slingshot), stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the shot flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 5 – a handheld STAPLE GUN with a tape-wrapped grip (NOT a desktop stapler), held in both hands like a small gun, stands in place. 1 stance at the waist. 2 lift and aim at chest height. 3 brace, lean forward. 4 fire: a shot flies right with a small spark. 5 recover to stance.
Row 6 – brown leather WELDER'S GLOVES with bolts sewn over the knuckles, worn on both hands. 1 boxing guard. 2 dash forward. 3 straight punch with a small white impact star. 4 rising uppercut. 5 recover to guard.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 15-3 · ถืออาวุธระดับ 3
<!-- note: มีดพร้าใบเลื่อย · ไม้ตอกตะปู · ดินสอกดเหล็ก · หนังสติ๊กรั้งแขน · ปืนยิงตะปูลม · ถุงมือพวงกุญแจ | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. No weapon images are attached — follow the text descriptions.

Layout: 6 rows x 5 columns (exactly 5 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell. EVERY cell must clearly show that row's weapon in his hands — never an empty hand, even during the attack and the follow-through.

Every frame faces RIGHT. Only one weapon per row.

Row 1 – a MACHETE with a jagged SAW BLADE welded along its back edge and a grey PVC-pipe handle (long blade, not a small knife), 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc, the weapon still in his hand. 5 recover to stance.
Row 2 – an ALUMINUM baseball bat with many NAILS hammered around the tip, bound with wire, two-handed. 1 stance, held up over the shoulder. 2 run forward with it raised behind the head. 3 cocked far back while still running. 4 arriving: full horizontal swing with a white swing arc. 5 recover to stance.
Row 3 – a long silver METAL MECHANICAL PENCIL as long as a short spear, with a pocket clip and a steel spike tip (NOT a yellow wooden pencil), held like a short spear in BOTH hands. 1 stance, pointing forward. 2 dash forward, pulled back to the chest. 3 still dashing, lowered. 4 arriving: straight lunge thrust, the weapon clearly visible at the end of his arms, short white thrust line. 5 recover to stance.
Row 4 – a WRIST-BRACE slingshot: a metal fork with a brace that rests on the forearm and a wooden RULER mounted on top as a sight (NOT a tree-branch slingshot), stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the shot flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 5 – a red-and-black PNEUMATIC NAIL GUN with a hose connected to a small blue AIR TANK hanging from his side, held in both hands like a small gun, stands in place. 1 stance at the waist. 2 lift and aim at chest height. 3 brace, lean forward. 4 fire: a shot flies right with a small spark. 5 recover to stance.
Row 6 – yellow gloves with a ring of silver CAR KEYS threaded across the knuckles like brass knuckles, worn on both hands. 1 boxing guard. 2 dash forward. 3 straight punch with a small white impact star. 4 rising uppercut. 5 recover to guard.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 15-4 · ถืออาวุธระดับ 4
<!-- note: ใบพัดลมคมกริบ · ไม้เฟืองรถ · ปากกาหมึกซึม · หน้าไม้ร่ม · ที่เย็บต่อแบตเตอรี่ · ถุงมือสปริง | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. No weapon images are attached — follow the text descriptions.

Layout: 6 rows x 5 columns (exactly 5 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell. EVERY cell must clearly show that row's weapon in his hands — never an empty hand, even during the attack and the follow-through.

Every frame faces RIGHT. Only one weapon per row.

Row 1 – a sharpened CEILING-FAN BLADE mounted on a knife handle with a small round motor at the hub, 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc, the weapon still in his hand. 5 recover to stance.
Row 2 – a baseball bat with a heavy round CAR GEAR WHEEL fitted on the end, two-handed. 1 stance, held up over the shoulder. 2 run forward with it raised behind the head. 3 cocked far back while still running. 4 arriving: full horizontal swing with a white swing arc. 5 recover to stance.
Row 3 – a long black FOUNTAIN PEN whose big brass nib is a spearhead, held like a short spear in BOTH hands. 1 stance, pointing forward. 2 dash forward, pulled back to the chest. 3 still dashing, lowered. 4 arriving: straight lunge thrust, the weapon clearly visible at the end of his arms, short white thrust line. 5 recover to stance.
Row 4 – a CROSSBOW built from a broken umbrella's bent steel frame, loaded with an umbrella rib as the bolt, stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the shot flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 5 – a heavy olive-green FIELD STAPLER wired by red and black cables to a car battery worn on his back, held in both hands like a small gun, stands in place. 1 stance at the waist. 2 lift and aim at chest height. 3 brace, lean forward. 4 fire: a shot flies right with a small spark. 5 recover to stance.
Row 6 – gloves with a coiled DOOR-CLOSER SPRING mounted on the back of each hand, worn on both hands. 1 boxing guard. 2 dash forward. 3 straight punch with a small white impact star. 4 rising uppercut. 5 recover to guard.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 15-5 · ถืออาวุธระดับ 5
<!-- note: มีดเชฟเรืองไฟ · ไม้เบสบอลลายเซ็น · ปากกาผู้นับเหตุการณ์ · หนังสติ๊กทองเหลือง · ที่เย็บทองเหลือง · ถุงมือปะเรือง | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. No weapon images are attached — follow the text descriptions.

Layout: 6 rows x 5 columns (exactly 5 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell. EVERY cell must clearly show that row's weapon in his hands — never an empty hand, even during the attack and the follow-through.

Every frame faces RIGHT. Only one weapon per row.

Row 1 – a chef's knife whose blade GLOWS bright ORANGE like a live ember, with small sparks, 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc, the weapon still in his hand. 5 recover to stance.
Row 2 – a baseball bat with a faded autograph and a GLOWING gold band wrapped around it, tiny star sparkles, two-handed. 1 stance, held up over the shoulder. 2 run forward with it raised behind the head. 3 cocked far back while still running. 4 arriving: full horizontal swing with a white swing arc. 5 recover to stance.
Row 3 – a wooden pen covered in carved tally marks with a GLOWING blue nib, held like a short spear in BOTH hands. 1 stance, pointing forward. 2 dash forward, pulled back to the chest. 3 still dashing, lowered. 4 arriving: straight lunge thrust, the weapon clearly visible at the end of his arms, short white thrust line. 5 recover to stance.
Row 4 – a polished BRASS slingshot with a GLOWING band, firing a glass marble with a star inside, stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the shot flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 5 – an antique BRASS stapler firing GLOWING light-blue staples, held in both hands like a small gun, stands in place. 1 stance at the waist. 2 lift and aim at chest height. 3 brace, lean forward. 4 fire: a shot flies right with a small spark. 5 recover to stance.
Row 6 – gardening gloves covered in many sewn patches that GLOW warm orange, worn on both hands. 1 boxing guard. 2 dash forward. 3 straight punch with a small white impact star. 4 rising uppercut. 5 recover to guard.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 16-1 · ท่านอกศึก · ยืนและวิ่ง
<!-- note: ยืนหายใจหน้า/หลัง · วิ่ง 3 ทิศ · กระโดดอยู่กับที่ — ใช้บนแผนที่ | cells: 36 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet. His hands are empty.

Layout: 6 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell (except the jump). No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

The facing direction is written on each row.

Row 1 – facing the viewer (front view), idle breathing loop: 1–6 chest rises and falls slightly, tiny head bob, arms relaxed at his sides.
Row 2 – seen from the BACK (we see his backpack, not his face), idle breathing loop, same subtle motion.
Row 3 – running toward the viewer (front view), 6-frame run cycle, clear alternating legs, arms pumping, both feet off the ground in frames 2 and 5.
Row 4 – running away from the viewer (back view, backpack visible), 6-frame run cycle, same rules.
Row 5 – running toward the RIGHT (side view), 6-frame run cycle, arms pumping, both feet off the ground in frames 2 and 5.
Row 6 – front view, jump in place: 1 stand, 2 crouch, 3 push off, 4 highest point with knees tucked, 5 land with knees bent, 6 stand.

Keep his look identical to image 1 in all 36 frames. Output PNG only.
```

## 16-2 · ท่าทาง · ทักทายและหยิบของ
<!-- note: โบกมือ · พยักหน้า · ส่ายหน้า · มองหา · เก็บของ · ผลักลัง | cells: 36 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet. Only rows 5 and 6 contain an object (a small box and a wooden crate).

Layout: 6 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

The facing direction is written on each row.

Row 1 – front view, wave: 1 stand, 2 raise his front hand to shoulder height (the hand never covers his face), 3–5 wave the open hand side to side with a smile, 6 lower the hand.
Row 2 – front view, nod yes: 1 stand, 2 head tilts down, 3 up, 4 down, 5 up, 6 stand smiling.
Row 3 – front view, shake head no: 1 stand, 2 head turned to his left, 3 to his right, 4 left, 5 right, 6 stand with a small frown.
Row 4 – front view, look around: 1 stand, 2 turn his head to one side, 3 shade his eyes with one hand looking that way, 4 turn to the other side, 5 shade his eyes looking that way, 6 back to front, puzzled.
Row 5 – facing RIGHT, pick up an item: 1 stand, 2 bend his knees and lean forward, 3 crouch reaching to the ground, 4 grab a small brown box, 5 stand up holding it at his chest, 6 hold it happily.
Row 6 – facing RIGHT, push a heavy wooden crate (the crate touches his hands in every frame): 1 hands on the crate, 2 lean in, 3 step and push, 4 strain hard, 5 step and push, 6 lean in.

Keep his look identical to image 1 in all 36 frames. Output PNG only.
```

## 16-3 · พักและอารมณ์
<!-- note: นั่ง · นอนหลับ · ตกใจ · งง · ดีใจ · โกรธ — สัญลักษณ์ ! ? ♪ ผมวาดเพิ่มเองด้วยโค้ด | cells: 36 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet. Do NOT draw speech bubbles, symbols, hearts, music notes, sweat drops or Zzz — facial expression and body only.

Layout: 6 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

Rows 1 and 3–6 face the viewer (front view). Row 2 faces RIGHT.

Row 1 – sit down: 1 stand, 2 bend knees, 3 sit on the ground cross-legged, 4 sitting relaxed, 5 sitting, swaying a little, 6 sitting, looking up.
Row 2 – sleep, facing RIGHT: 1 sitting, yawning, 2 lying down on his side, 3–6 sleeping with eyes closed, slow breathing, mouth slightly open.
Row 3 – surprised: 1 stand, 2 jump back a little with wide eyes and open mouth, 3 both arms up in shock, 4 hold, 5 relax, 6 stand.
Row 4 – confused: 1 stand, 2 tilt his head, 3 scratch the back of his head, 4 hold, 5 shrug, 6 stand.
Row 5 – happy: 1 stand, 2 big smile with happy closed eyes, 3 small hop, 4 both fists up at his chest, 5 small hop, 6 stand smiling.
Row 6 – angry: 1 stand, 2 frown with gritted teeth, 3 stomp one foot, 4 fists clenched, shaking, 5 stomp, 6 stand, still angry.

Keep his look identical to image 1 in all 36 frames. Output PNG only.
```

## 16-4 · ท่าศึกเสริม
<!-- note: ใช้ไอเท็ม · HP ต่ำ · ฟื้น · เชียร์เพื่อน · ประกาย (คิดท่าออก) | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. In this sheet he holds the small KITCHEN KNIFE with a wooden handle in his front hand in every frame (except where written).

Layout: 5 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell (except lying). No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

Every frame faces RIGHT.

Row 1 – use an item: 1 battle stance, knife low, 2 take a small round glass bottle with green liquid from his backpack strap with his back hand, 3 lift the bottle, 4 drink, 5 lower the bottle and wipe his mouth, 6 back to stance.
Row 2 – low HP, loop: hunched over, panting, back hand on his knee, knife lowered, 1–6 heavy breathing, shoulders rise and fall, tired eyes.
Row 3 – revive: 1 lying face down with the knife on the ground beside him, 2 push up on his arms, 3 one knee up, 4 rise, grabbing the knife, 5 stand, shaky, 6 battle stance.
Row 4 – cheer an ally: 1 stance, 2 raise his back fist, 3 pump the fist upward (his face stays visible), 4 shout encouragingly, 5 pump again, 6 stance.
Row 5 – sudden insight: 1 stance, 2 eyes widen, 3 looks up as if getting an idea, 4 a small sparkle in his eyes, determined smile, 5 grips the knife tighter, 6 confident stance.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 16-5 · ภาพหน้าสำหรับบทพูด
<!-- note: 8 อารมณ์ ครึ่งตัวใหญ่ — ใช้ในกล่องบทพูดและคัตอินสกิล | cells: 8 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. This sheet is large portraits, not full-body sprites.

Layout: 2 rows x 4 columns, evenly spaced. Each cell is one large BUST portrait (head and shoulders only, the head fills most of the cell), facing three-quarters to the RIGHT, on the same solid green background #01DA0D. No grid lines, no text, no labels, no numbers, no shadows, no speech bubbles or symbols, only one Rion per cell.

Row 1 – 1 neutral and calm, 2 happy with a big smile, 3 laughing with eyes closed, 4 determined and serious.
Row 2 – 1 surprised with wide eyes, 2 sad with teary eyes, 3 angry frown with gritted teeth, 4 hurt, wincing in pain.

Keep his look identical to image 1 in all 8 portraits. Output PNG only.
```

## 16-1b · แก้ 16-1 แถว 4–6 (ไม่มีหมวก)
<!-- note: ผล 16-1 แถว 4–6 (วิ่งออกห่าง · วิ่งไปทางขวา · กระโดด) วาดไม่ใส่หมวกและแว่น — เจนใหม่เฉพาะ 3 แถวนี้ | cells: 18 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet. His hands are empty.
IMPORTANT: he wears his bright blue baseball cap with the brass goggles on top in EVERY frame — from behind we see the back of the blue cap and its strap, from the side we see the curved blue brim pointing right. Never draw him bare-headed.

Layout: 3 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell (except the jump). No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

The facing direction is written on each row.

Row 1 – running away from the viewer (back view: back of the blue cap, brown backpack visible), 6-frame run cycle, clear alternating legs, both feet off the ground in frames 2 and 5.
Row 2 – running toward the RIGHT (side view, cap brim pointing right), 6-frame run cycle, arms pumping, both feet off the ground in frames 2 and 5.
Row 3 – front view, jump in place, cap on: 1 stand, 2 crouch, 3 push off, 4 highest point with knees tucked, 5 land with knees bent, 6 stand.

Keep his look identical to image 1 in all 18 frames, cap included. Output PNG only.
```

## 17-1 · แก้ถืออาวุธ (15-2 · 15-3 · 15-4)
<!-- note: เจนใหม่เฉพาะแถวที่พลาด: 15-2 แถว 3 ดินสอคู่ · 15-3 แถว 4 หนังสติ๊ก (ไม่มีเป้) + แถว 6 ถุงมือกุญแจ (ไม่มีหมวก) · 15-4 แถว 1 ใบพัดลม · 4 หน้าไม้ร่ม · 5 ที่เย็บต่อแบต · 6 ถุงมือสปริง | cells: 35 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. No weapon images are attached — follow the text descriptions exactly, the special parts of each weapon must be big and clearly visible.
IMPORTANT: in EVERY frame he wears his bright blue baseball cap with the brass goggles on top AND his brown backpack with straps. Never bare-headed, never without the backpack.

Layout: 7 rows x 5 columns (exactly 5 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell. EVERY cell must clearly show that row's weapon in his hands — never an empty hand, even during the attack and the follow-through.

Every frame faces RIGHT. Only one weapon per row.

Row 1 – TWO yellow wooden pencils TAPED together side by side with grey duct tape wrapped around them in three places, and one long silver NAIL sticking straight out of the sharpened tip. It is NOT a single pencil, NOT a pen, NOT a metal spear. Held like a short spear in BOTH hands. 1 stance, pointing forward. 2 dash forward, pulled back to the chest. 3 still dashing, lowered. 4 arriving: straight lunge thrust, the weapon clearly visible at the end of his arms, short white thrust line. 5 recover to stance.
Row 2 – a WRIST-BRACE slingshot: a metal fork with a brace that rests on the forearm and a wooden RULER mounted on top as a sight (NOT a tree-branch slingshot). His brown backpack is clearly visible on his back. Stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the shot flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 3 – yellow work gloves with a ring of silver CAR KEYS threaded across the knuckles like brass knuckles, worn on both hands. He wears his blue cap with goggles and his backpack. 1 boxing guard. 2 dash forward. 3 straight punch with a small white impact star. 4 rising uppercut. 5 recover to guard.
Row 4 – a sharpened white CEILING-FAN BLADE (one long flat curved fan blade, as long as his arm) mounted on a black knife handle, with a small round silver MOTOR as the hilt between blade and handle. NOT a normal knife, NOT a sword. 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc, the fan blade still in his hand. 5 recover to stance.
Row 5 – an UMBRELLA CROSSBOW: a closed black umbrella turned sideways, its handle is the stock, its bent steel ribs spread out as the bow arms with torn black fabric still hanging on them, string across the rib tips, loaded with one long thin umbrella rib as the bolt. It must clearly look like it was made from an umbrella. Stands in place. 1 stance, held low in front. 2 raise to eye level, aiming. 3 pull back fully, aiming. 4 release: the bolt flies right while he STILL HOLDS the weapon up. 5 recover to stance, weapon in hand.
Row 6 – a heavy OLIVE-GREEN metal field stapler held in both hands like a small gun, one RED cable and one BLACK cable run from its back over his shoulder to a rectangular dark-grey CAR BATTERY with red and black terminals strapped onto his backpack. 1 stance at the waist. 2 lift and aim at chest height. 3 brace, lean forward. 4 fire: a staple flies right with a small spark. 5 recover to stance.
Row 7 – brown gloves with a big silver COILED SPRING (a door-closer spring, as long as his hand) mounted on the back of EACH glove, worn on both hands in every frame. 1 boxing guard, both springs visible. 2 dash forward. 3 straight punch, the spring compressed, small white impact star. 4 rising uppercut, spring stretched. 5 recover to guard.

Keep his look identical to image 1 in all 35 frames, cap and backpack included. Output PNG only.
```

## 17-2 · แก้ท่าศึกที่มีดหาย (14-1 · 16-4)
<!-- note: เจนใหม่ทั้งแถว: 14-1 โดนตี (ช่อง 1–4 มีดหาย) · ล้ม (1–2) · วิ่ง (5) · 16-4 ใช้ไอเท็ม (2–4) · เชียร์ (2–5) — มีดต้องอยู่ในมือทุกเฟรม | cells: 30 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses of image 1; draw only the poses written below. The only weapon in this sheet is a small KITCHEN KNIFE with a wooden handle.
IMPORTANT: the kitchen knife stays gripped in his FRONT hand in EVERY frame of this sheet — while hurt, while falling, while running, while drinking and while cheering. He never drops it, never puts it away, never lets go of it, except row 2 frames 5–6 where it lies on the ground beside him. All other actions use his BACK hand only.

Layout: 5 rows x 6 columns (exactly 6 poses per row), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline in every cell (except lying). No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

Every frame faces RIGHT.

Row 1 – hurt, knife in the front hand in all 6 frames: 1 hit (eyes shut, body jolts back, knife still gripped), 2 stagger back, 3 stagger, 4 catch balance, 5 straighten, 6 back to stance holding the knife.
Row 2 – defeated: 1 staggering, knife still gripped, 2 knees buckle, knife still gripped, 3 falling forward, the knife slipping from his fingers, 4 hits the ground, 5 lying face down with the knife on the ground beside his hand, 6 lying still.
Row 3 – run cycle holding the knife low in the front hand in all 6 frames, clear alternating legs, both feet off the ground in frames 2 and 5.
Row 4 – use an item: 1 battle stance, knife low in the front hand, 2 the BACK hand takes a small round glass bottle with green liquid from his backpack strap (knife still in the front hand), 3 lift the bottle with the back hand, 4 drink from it, the knife held low in the front hand, 5 lower the bottle and wipe his mouth with the back of the back hand, 6 back to stance.
Row 5 – cheer an ally: 1 stance, knife in the front hand, 2 raise his BACK fist, 3 pump the back fist upward (his face stays visible) while the front hand still holds the knife low, 4 shout encouragingly, knife still in the front hand, 5 pump the back fist again, 6 stance.

Keep his look identical to image 1 in all 30 frames. Output PNG only.
```

## 17-3 · แก้วิ่งขวา + ผลักลัง (16-1b · 16-2)
<!-- note: 16-1b วิ่งขวาได้ 4 จาก 6 · 16-2 ผลักลังช่อง 4 ไม่มีลัง — เจนใหม่ทั้งสองแถว มือเปล่า | cells: 12 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1. He holds NO weapon in this sheet. He wears his bright blue cap with the brass goggles in every frame.

Layout: 2 rows x 6 columns (exactly 6 poses per row, 12 cells in total), one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never a duplicate Rion overlapping in a cell.

Every frame faces RIGHT (side view, cap brim pointing right).

Row 1 – running toward the RIGHT, a full 6-frame run cycle (exactly SIX different frames, not four): 1 front foot strikes the ground, 2 both feet off the ground, 3 back leg swings forward, 4 the other foot strikes the ground, 5 both feet off the ground, 6 back leg swings forward. Arms pumping, hands empty.
Row 2 – pushing a heavy wooden crate (a brown crate as tall as his chest, drawn in front of him on the right). The crate is in ALL 6 frames and both his hands touch it in every frame: 1 hands on the crate, 2 lean in, 3 step and push, 4 strain hard, eyes squeezed, crate still under his hands, 5 step and push, 6 lean in.

Keep his look identical to image 1 in all 12 frames. Output PNG only.
```

## 17-4 · แก้ใบพัดลม + โดนตี/เชียร์ถือมีด
<!-- note: 17-1b แถว 4 ใบพัดลมถูกแค่ช่อง 2/4 (ที่เหลือถือร่ม) · 17-2 โดนตีช่อง 2–5 และเชียร์ช่อง 2/4/5 มีดหาย — 3 แถว แถวละอาวุธเดียว | cells: 17 -->
```
Image 1 is the ONLY style and character reference: copy this exact sprite sheet's character — same chibi proportions (very big round head, about 40% of his total height, short small body), same big round eyes and young face, same bright royal-blue BASEBALL cap with a curved front brim (bright blue like image 1, NOT dark navy, NOT a flat newsboy cap) with brass goggles with blue lenses on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack and straps, bright blue shorts, blue wristwatch on his LEFT wrist, white socks, brown boots. Same thick dark outline, same flat cel colors, same character size per cell, same solid green background #01DA0D.
Image 2 shows the same character from the front for extra detail. Do NOT change his look, age or proportions in any frame.
Ignore the poses and weapons of image 1; draw only the poses and the weapons written below. He wears his blue cap with goggles and his backpack in every frame.

Layout: 3 rows, one pose per cell, evenly spaced, Rion fully inside each cell, feet on the same baseline. Row 1 has exactly 5 cells, rows 2 and 3 have exactly 6 cells. No grid lines, no text, no labels, no numbers, no shadows, only one Rion per cell, never an extra Rion.

Every frame faces RIGHT. Each row has ONE weapon only, and it is gripped in his FRONT hand in EVERY frame of that row. No umbrella anywhere in this sheet.

Row 1 – a sharpened white CEILING-FAN BLADE (one long flat curved blade, as long as his arm) fixed to a black knife handle, with a small round silver MOTOR as the hilt. It is always attached to his hand, never floating, never an umbrella. 1 battle stance holding it low and forward. 2 run forward with it raised. 3 cocked back over the shoulder while still running. 4 arriving: big slash with a white swing arc. 5 recover to stance holding it.
Row 2 – hurt, holding a small KITCHEN KNIFE with a wooden handle in the front hand in all 6 frames: 1 hit (eyes shut, body jolts back), 2 stagger back, 3 stagger, 4 catch balance, 5 straighten, 6 back to stance. The knife stays in his fist in every frame.
Row 3 – cheer an ally, holding the same small kitchen knife low in the FRONT hand in all 6 frames: 1 stance, 2 raise the BACK fist, 3 pump the back fist upward (face stays visible), 4 shout encouragingly, 5 pump the back fist again, 6 stance. Only ONE knife, never a second knife at his hip.

Keep his look identical to image 1 in all 17 frames. Output PNG only.
```

## 17-4b · แบบสั้น แนบภาพเดียว
<!-- note: ⚠ แนบแค่ rion_flow_ref.png ภาพเดียว (ไม่แนบชีต v14b_3) · 17-4 รอบแรก Flow วาดชีตเก่าซ้ำ (เดิน 4 ทิศ ม้วนฟัน) ไม่มีท่าที่สั่ง | cells: 17 -->
```
The attached image is Rion, the ONLY character reference. Copy him exactly: chibi, very big round head, big round eyes, bright blue baseball cap with brass goggles on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack, blue shorts, blue watch on his LEFT wrist, white socks, brown boots. Thick dark outline, flat cel colors.

Make a NEW sprite sheet with ONLY the 17 poses below. Do not draw walking, running, rolling, jumping or any other pose.

Solid green background #01DA0D. 3 rows. Row 1 has 5 cells, rows 2 and 3 have 6 cells. One full-body Rion per cell, all facing RIGHT, same size, feet on one baseline. No grid lines, no text, no shadows.

Row 1 (5 cells) – he holds a CEILING-FAN BLADE sword: one long white curved fan blade on a black handle, with a small round silver motor between blade and handle. It is in his front hand in all 5 cells. 1 stand ready. 2 step forward, blade raised. 3 blade pulled back over his shoulder. 4 big slash with a white arc. 5 stand ready.
Row 2 (6 cells) – he holds a small kitchen knife in his front hand in all 6 cells. HURT: 1 hit, eyes shut, leaning back. 2 stagger back. 3 stagger. 4 catch balance. 5 straighten up. 6 stand ready.
Row 3 (6 cells) – he holds the small kitchen knife low in his front hand in all 6 cells. CHEER: 1 stand. 2 raise his other fist. 3 pump that fist up. 4 shout with mouth open. 5 pump the fist again. 6 stand.

One weapon per row. No umbrella. Only one knife. Output PNG only.
```

## 18-1 · ท่าสายคม 7 ท่า (มีดทำครัว)
<!-- note: ⚠ แนบแค่ rion_flow_ref.png ภาพเดียว (บทเรียน 17-4) · techs.csv สายคม: ฟัน เขี้ยวพุ่ง เขี้ยวพัน★ กวาด วงล้อ★ ปาดไว เงาสองคม★ · หลักโมเมนตัม (kwan 10 ต.ค.): ฟาดทันทีตอนถึงตัว ไม่ยืนง้างนิ่ง · แสงใหญ่/ร่างแยกใส่ด้วยโค้ด | cells: 42 -->
```
The attached image is Rion, the ONLY character reference. Copy him exactly: chibi, very big round head, big round eyes, bright blue baseball cap with brass goggles on top, brown spiky hair, white short-sleeve shirt, blue tie, brown backpack, blue shorts, blue watch on his LEFT wrist, white socks, brown boots. Thick dark outline, flat cel colors.

Make a NEW sprite sheet with ONLY the 42 poses below: 7 sword techniques with a small KITCHEN KNIFE (short steel blade, wooden handle). The knife is gripped in his front hand in EVERY frame, never dropped, never a second knife.

Solid green background #01DA0D. 7 rows x 6 columns, exactly 6 cells per row, one full-body Rion per cell, all facing RIGHT, same size, feet on one baseline (except jumps). No grid lines, no text, no shadows, no duplicate or ghost Rion. Keep slash trails SMALL: one thin white arc next to the knife only, never covering his body.

Every attack follows momentum: he moves toward the right and the blade hits at the moment he arrives. No standing still to wind up.

Row 1 – BASIC SLASH: 1 ready stance, knife low. 2 step forward, knife rising. 3 knife raised beside his head while still stepping. 4 arriving: diagonal downward slash, thin white arc. 5 follow-through, knife low behind, leaning forward. 6 back to ready stance.
Row 2 – FANG LUNGE: 1 ready stance, crouched low. 2 push off, body low and forward. 3 long lunge, knife pointed forward at chest height. 4 arriving: upward slash from the lunge, thin white arc. 5 sliding to a stop, knife high. 6 ready stance.
Row 3 – TRIPLE FANG (3 fast slashes): 1 ready stance. 2 first slash diagonal down. 3 second slash diagonal up, reversed. 4 third slash, a strong horizontal cut, thin white arc. 5 follow-through, knife far behind. 6 ready stance.
Row 4 – SWEEP (wide horizontal cut across a row of enemies): 1 ready stance. 2 knife pulled back to his far side at waist height, body twisted, stepping forward. 3 swinging across, arm straight. 4 wide horizontal cut fully extended, long thin white arc. 5 body turned by the momentum. 6 ready stance.
Row 5 – WHEEL (spinning attack): 1 crouch low, knife out to the side. 2 jump and start spinning. 3 mid-air spin, seen from the side, knife outward. 4 spin continues, his back toward us. 5 landing with knees bent, knife out wide, thin circular white arc. 6 ready stance.
Row 6 – QUICK SLICE (very fast, light cut): 1 ready stance. 2 small fast step forward, knife low. 3 quick low slice at knee height, thin white line. 4 already passing through, knife behind. 5 small hop back. 6 ready stance.
Row 7 – TWIN SHADOW (two fast slashes): 1 ready stance, eyes narrowed. 2 dash forward, knife low. 3 first slash upward. 4 second slash downward crossing the first, thin white X arc. 5 skidding past, knife behind. 6 ready stance.

Keep his look identical to the attached image in all 42 frames. Output PNG only.
```

## ผลตรวจรอบแรก (kwan ส่ง 7 ชีต 16 ต.ค. · Google Flow · JPG 1438x2576 ทุกชีต) — ยังไม่เข้าเกม/หน้าเทส
ไฟล์ `flow_trial_v14_1.jpg` `v15_6` `v16_1`…`v16_5` · ตัดด้วย `tools/sprites/rion_pack_cut.py` · ภาพตรวจกรอบ+เลข `pack_check/<ชีต>.jpg` · หน้าตาตรงแบบ Flow ทุกชีต (หมวกน้ำเงินสด แว่นทอง chibi)
- 14-1 ศึก 48/48 ✓ · พลาด: โดนตีช่อง 1–4 และล้มช่อง 1–2 มีดหายจากมือ · วิ่งช่อง 5 มือเปล่า
- 15-6 ร่าย 24 ตัว แต่ผัง 6x4 (สั่ง 4x6): ขาว 4 · ดำ 8 (2 แถว) · แดง 4 · อัญเชิญ 8 (2 แถว) · ขาว/แดงไม่มีท่ายกมือลงคืน (ใช้ช่อง 1 แทนได้) · ตำราหายหลังช่อง 1 ทุกสาย · ดำผลักฝ่ามือเดียว
  **แก้ด้วยโค้ดแล้ว**: แถว 2 (ดำ: ตำราลอย · พนมมือ · เรืองส้ม) วาดครึ่งตัวถึงเข็มขัด → ต่อขาจากท่ายืนแถว 3 ช่อง 1 (หัวตรงกัน · ลบมือที่ห้อยข้างสะโพกของท่ายืน)
- 16-1 ยืน/วิ่ง 36/36 · แถว 1–3 ✓ · **แถว 4–6 ไม่มีหมวกและแว่น** (วิ่งออกห่าง · วิ่งขวา · กระโดด) → เจนใหม่ด้วย 16-1b ข้างบน
- 16-2 ท่าทาง 33 (สั่ง 36: โบกมือ/เก็บของ/ผลักลังได้แถวละ 5) · ผลักลังช่อง 4 ไม่มีลัง (ต่อยลม)
- 16-3 พัก/อารมณ์ 30 (แถวละ 5) · หลับหันซ้าย (สั่งขวา · พลิกได้) · วาดเครื่องหมายตกใจ/เงาใต้เท้ามา → ตัวตัดทิ้งก้อนที่ไม่แตะตัวแล้ว
- 16-4 ศึกเสริม 29 (ใช้ไอเท็ม 5) · ใช้ไอเท็มช่อง 2–4 และเชียร์ช่อง 2–5 ไม่มีมีด · ประกายช่อง 5 ถือมีดหน้าปาก · ฟื้นวาดซ้อนกัน → ผ่าที่คอลัมน์โปร่งสุด ขอบหมวกช่อง 2–3 โดนตัดนิดหน่อย
- 16-5 ภาพหน้า 8/8 แต่ผัง 4x2 (สั่ง 2x4) · ตลกกับดีใจหน้าคล้ายกัน

## ผลตรวจรอบ 2 (kwan ส่ง 5 ชีต 16 ต.ค. · Google Flow · JPG) — ยังไม่เข้าเกม/หน้าเทส
ไฟล์ `flow_trial_v16_1b.jpg` `v15_2`…`v15_5` · ตัดด้วย `rion_pack_cut.py` (`ROW_CY` 16-1b · `EXPECT` · `REUSE` = ช่องคืนท่ามือว่างใช้ช่อง 1 ของแถวเดียวกัน) · ภาพตรวจ `pack_check/<ชีต>.jpg`
- 16-1b ยืน/วิ่ง 16 ตัว · หมวก+แว่นครบทุกเฟรม ✓ · วิ่งออกห่าง 6 ✓ · **วิ่งขวาได้ 4 (สั่ง 6)** · กระโดด 6 ช่องแต่วาดเป็น 4+2 สองแถว (รวมเป็นคลิปเดียวได้)
- 15-2 ระดับ 2: 30 ตัว (6x5 · สั่ง 6x6) · **แถว 3 อาวุธแทงผิดแบบ** · ที่เย็บช่อง 3 มือว่าง → ใช้ช่อง 2 แทน
- 15-3 ระดับ 3: 30 ตัว · **แถว 6 ไม่มีหมวก** · แถว 4 และ 6 ไม่มีเป้
- 15-4 ระดับ 4: 30 ตัว · **แถว 1 ไม่มีใบพัดลม · แถว 4 เป็นหน้าไม้ ไม่ใช่ร่ม · แถว 5 แบตเตอรี่/สีผิด · แถว 6 ไม่มีสปริง บางเฟรมมือเปล่า**
- 15-5 ระดับ 5: 30 ตัว · 6 สายถืออาวุธครบ มีแสงเรือง ✓ · ช่อง 5 คืนท่ามือว่าง → ใช้ช่อง 1

## ผลตรวจรอบ 3 (kwan ส่ง 17-1…17-3 · 16 ต.ค.) — ยังไม่เข้าเกม/หน้าเทส
ไฟล์ `flow_trial_v17_{1,2,3}.jpg` · 17-1 พื้นเขียวอ่อนไม่เท่ากันทีละแถบ → ตัวตัดลบพื้นด้วยสีขอบซ้าย/ขวาของแต่ละบรรทัด (`BAND_KEY`) · ตัดได้ 35 / 26 / 48 ตัว
- **ใช้ได้ (แทนของเดิม)**: 17-3 แถว 1 วิ่งขวา 6 เฟรม → แทน 16-1b แถว 2 (4 เฟรม) · 17-2 แถว 2 ล้ม 5 เฟรม มีดในมือจนล้มแล้ววางข้างตัว → แทน 14-1 แถว 4 ·
  17-3 ช่อง 5-4 (ผลักลังเบ่งแรง มีลัง) → แทน 16-2 ผลักลังช่อง 4
- 17-1 ถืออาวุธ: วาดตามสั่งได้แค่ดินสอยาวมีปลายแหลม (แถว 1 · ดูเป็นดินสอแท่งเดียว ไม่เห็นเทป) และสปริงบนถุงมือ (แถว 7 ช่อง 4 เท่านั้น) ·
  หนังสติ๊กเป็นกิ่งไม้ (ไม่ใช่รั้งแขน) · ถุงมือไม่เห็นกุญแจ · ใบพัดลมกลายเป็นดาบ และช่อง 2/5 มือว่าง · หน้าไม้ยังไม่มีร่ม · ที่เย็บไม่มีสาย/แบตเตอรี่ · ช่อง 5 มือว่างเกือบทุกแถว
- 17-2: โดนตีช่อง 2–5 มีดหายอีก · วิ่งมีมีดสองเล่ม (มือหน้า + เล่มที่สองโผล่ข้างสะโพก) · ใช้ไอเท็มมีดเล่มที่สองที่สะโพก · เชียร์ช่อง 2/4/5 มือว่าง
- 17-3 แถมแถวที่ไม่ได้สั่ง (เดินหลัง · เดินซ้าย 2 แถว · ยืนหน้า 2 แถว · ผลักลังแบบสลับฝั่ง) — แถวผลักลังตัวกับลังทับกัน ใช้เป็นคลิปไม่ได้
- **17-3b (kwan เจนใหม่ · PNG 1536x1024 · 2x6) ใช้ได้ทั้งชีต**: วิ่งขวา 6 เฟรม ตัวลอยในช่อง 2 และ 5 (เท้าต่ำสุดยกขึ้น 12 / 18 จุดในชีต) → แทน 17-3 แถว 1 ·
  ผลักลังครบ 6 เฟรม มีลังและมือแตะลังทุกเฟรม ช่อง 4 เบ่งหลับตา → แทน 16-2 แถว 6 ทั้งแถว · PNG ไม่มีรอย JPG · ภาพเทียบ `pack_check/17-3b_vs_17-3.jpg`
  ข้อสังเกต: มีสายรัดฟ้าที่ข้อมือไกลด้วย (ต้นแบบมีนาฬิกาแค่ข้อมือซ้าย = ข้อมือใกล้เมื่อหันขวา · 17-3 เดิมก็เป็น) · ตาเล็กลงนิดหน่อย หมวกกลมโตกว่าชีตอื่นเล็กน้อย
- **17-1b (kwan เจนใหม่ · PNG 1024x1536 · 7 แถว) ใช้ได้เกือบทั้งชีต** · ภาพตรวจ `pack_check/17-1b.jpg` · ตัดได้ [5,5,5,5,5,5,6]
  ✓ แถว 1 ดินสอยาวปลายเหล็กแหลม (แทน 15-2 แถว 3) · ✓ แถว 2 หนังสติ๊กรั้งแขนมีไม้บรรทัด (แทน 15-3 แถว 4) · ✓ แถว 3 ถุงมือเหลือง (แทน 15-3 แถว 6 · มีหมวก+เป้แล้ว · พวงกุญแจเห็นไม่ชัด) ·
  ✓ แถว 5 หน้าไม้จากร่มดำ (แทน 15-4 แถว 4) · ✓ แถว 6 ที่เย็บเขียวมะกอก + แบตเตอรี่บนเป้ + สายแดง (แทน 15-4 แถว 5) · ✓ แถว 7 ถุงมือสปริง (แทน 15-4 แถว 6 · มี 6 ตัว ช่อง 4 เป็นท่าย่อตัวเกินมา → ใช้ช่อง 1 2 3 5 6)
  ✗ แถว 4 ใบพัดลม: ถูกแค่ช่อง 2 (วิ่งชูใบพัด มีมอเตอร์) กับช่อง 4 (ฟัน) · ช่อง 1/3/5 ถือร่มดำแทน (ปนกับแถวหน้าไม้) · ช่อง 3 ใบพัดลอยแยกจากมือ
- **17-4b (แนบภาพเดียว · JPG 4 แถว)**: Flow ทำตาม prompt แล้ว (มีแค่ 3 ท่าที่สั่ง ไม่วาดชีตเก่าซ้ำ) · ตัดได้ 17 ตัว [5,6,5,1] (ช่อง 6 ของเชียร์ปัดลงแถว 4)
  แถว 1: ได้ดาบโค้งสีขาวด้ามดำ **ไม่เห็นเป็นใบพัดลม/ไม่มีมอเตอร์** · ถือครบ 5 ช่อง · แถว 2 โดนตี: มีดช่อง 1–3 · ช่อง 4–6 มือว่าง ·
  แถว 3 เชียร์: มีดช่อง 1 2 4 6 (ช่อง 2 ชูมีดด้วยมือที่ต้องชูกำปั้น) · ช่อง 3 5 มือว่าง · ทุกช่องหันเกือบตรงหน้า (ไม่ได้หันขวาแบบชีตอื่น)
