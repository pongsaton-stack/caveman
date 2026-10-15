# Rion แนวพิกเซล — คำสั่ง Google Flow (ทดลอง · kwan 15 ต.ค. 2026 เลือก "อยากลอง 2")

**สถานะ: ทดลองเท่านั้น** — แนวภาพหลักยังเป็นของ 14 ต.ค. (chibi เส้นขอบเข้ม สีเรียบ ไม่ใช่พิกเซล · ต้นฉบับ `rion_front_src.png`)
ถ้าชุดนี้ออกมาดีและ kwan เลือกเปลี่ยน ค่อยบันทึกเป็นการตัดสินใหม่ใน CLAUDE.md

ที่มา: ชีตรอบแรกจากอีกค่าย (prompt "16-bit pixel art" · 10 ท่า) — ปัญหาที่เจอและแก้ในคำสั่งชุดนี้:
| ปัญหาในรอบแรก | แก้ในคำสั่งนี้ |
|---|---|
| เดินซ้าย: แถวบนหันขวา แถวล่างหันซ้าย | กฎกลางข้อ "ทุกช่องหันทิศเดียว" + ระบุทิศในทุกคำสั่ง |
| ฟันดาบ: แถวบนหันหน้า แถวล่างหันซ้าย · เป็นดาบยาว | หันซ้ายทุกช่อง · อาวุธ = มีดทำครัว (อาวุธเริ่มเกม) |
| สกิล: 2 ช่องมีแต่คลื่น ไม่มีตัว | "Rion must be visible in every cell" |
| ชื่อ crouch ซ้ำ 2 ชุด | แยกเป็น kneel (ล้มคุกเข่า) กับ idle_battle (ยืนในศึก) |
| หมวกเทาหม่น ไม่ใช่น้ำเงินต้นฉบับ | ให้ค่าสีน้ำเงินตรง: วัดจาก `rion_front_alpha.png` (k-means 3 กลุ่มบนพิกเซลน้ำเงิน 94,976 จุด) = #4184C9 สว่าง 7% · #2A70BE หลัก 87% · #21508A เงา 6% |
| ได้เป็น JPG ชีตรวม | เจนทีละท่า 1 ไฟล์ · ดาวน์โหลดเป็น PNG |

ทิศในเกม: **จอสู้ศัตรูอยู่ซ้าย ปาร์ตี้ขวา → Rion ในศึกหันซ้ายทุกท่า** · เดิน 4 ทิศใช้บนแผนที่

## วิธีใช้
1. เจนทีละท่า (1 ท่า = 1 ภาพชีต) · แนบภาพ:
   - **ภาพ 1** = `rion_front_src.png` (หน้าตา/ชุด/สี — ภาพหลัก)
   - **ภาพ 2** (ถ้ามี) = ภาพที่ได้จากท่า 1 ที่ผ่านแล้ว (ให้แนวพิกเซลตรงกันทุกท่า)
   - ท่า #8 คุกเข่า / #10 ต้นท่าสกิล แนบ `pose_refs/pose_refs_v1.png` เพิ่มได้ (หุ่นท่าอ้างอิง)
2. วาง **คำสั่งของท่านั้น** แล้วต่อด้วย **กฎกลาง** ท้ายสุด (ก้อนเดียวกัน)
3. ดาวน์โหลดเป็น PNG ตั้งชื่อตามหัวข้อ (เช่น `rion_px_walk_left.png`) ส่งมา → ผมตัดช่อง/ลบเขียว/จัดเท้า/ลงหน้าเทสให้

## กฎกลาง (ต่อท้ายทุกคำสั่ง)
```
CHARACTER: same boy as Image 1 — ALL-BLUE baseball cap with brass goggles resting on it, brown messy hair, brown eyes,
white short-sleeve collared shirt, blue necktie, blue shorts with brown belt, brown backpack with two shoulder straps,
blue wristwatch on his LEFT wrist only, white socks, brown lace-up boots. Blues must match Image 1: cap/shorts
#2A70BE with highlight #4184C9 and shade #21508A, tie #2A70BE. Never grey-blue, never slate, never teal.
STYLE: clean 16-bit pixel art sprite, chibi 3-head proportion (head = 1/3 of height), crisp pixels, dark brown outline
#150F0D, 3-4 hard shade steps per material, light from upper-left, no gradients, no blur, no anti-aliased halo.
SHEET RULES: one sprite sheet, cells in a strict grid with equal cell size, the character centered in every cell,
same height and same scale in every cell, feet on the same ground line in every cell (except where the pose is airborne
or lying down), the character fully inside the cell — never cropped. EVERY cell faces the SAME direction stated above;
never flip or turn around between cells. Rion must be visible in EVERY cell. Effects (slash arcs, energy) stay inside
the same cell as Rion and never replace him. No labels, no text, no numbers, no borders, no grid lines.
Flat solid green background #00FF00 in every cell, no shadow on the ground, no other characters, no scenery.
```

## 1 · ยืนในศึก (idle_battle) — 4 เฟรม วน · ทำท่านี้ก่อน (ใช้เป็นภาพ 2 ของท่าอื่น)
```
Draw Rion from Image 1 as a 4-frame looping battle idle, 1 row x 4 cells, side view facing LEFT (true profile).
Ready stance: feet apart, knees slightly bent, empty hands loose in front at waist height. F1 neutral, F2 body sinks
1-2 pixels (breathing in), F3 lowest, F4 rising back. Only the body moves up and down a little; feet stay planted.
Backpack and hair move one frame later than the body.
```

## 2 · เดินหน้า (walk_front) — 8 เฟรม วน
```
Draw Rion from Image 1 as an 8-frame looping walk cycle, 2 rows x 4 cells, FRONT view (facing the viewer) in every cell.
F1 contact left foot forward, F2 down, F3 passing, F4 up, F5 contact right foot forward, F6 down, F7 passing, F8 up.
Arms swing opposite to the legs, body bobs down on contact and up on passing. Knees bend.
```

## 3 · เดินหลัง (walk_back) — 8 เฟรม วน
```
Draw Rion from Image 1 as an 8-frame looping walk cycle, 2 rows x 4 cells, BACK view (we see his back and backpack,
no face, no eyes) in every cell. Same 8 phases as a standard walk: contact, down, passing, up, then the other foot.
Arms swing opposite to the legs, backpack bounces one frame behind the body.
```

## 4 · เดินซ้าย (walk_left) — 8 เฟรม วน
```
Draw Rion from Image 1 as an 8-frame looping walk cycle, 2 rows x 4 cells, side view facing LEFT (nose points to the
left edge) in EVERY one of the 8 cells. F1 contact, F2 down, F3 passing, F4 up, F5 contact other foot, F6 down,
F7 passing, F8 up. His left side faces the viewer, so the wristwatch is visible on the near wrist.
Arms swing opposite to the legs, backpack bounces one frame behind.
```

## 5 · เดินขวา (walk_right) — 8 เฟรม วน
```
Draw Rion from Image 1 as an 8-frame looping walk cycle, 2 rows x 4 cells, side view facing RIGHT (nose points to the
right edge) in EVERY one of the 8 cells. Same 8 walk phases. Draw this view directly — do NOT mirror a left-facing walk:
his right side faces the viewer, so the wristwatch is on the FAR wrist and mostly hidden.
Arms swing opposite to the legs, backpack bounces one frame behind.
```

## 6 · ฟันมีด (attack_knife) — 8 เฟรม เล่นครั้งเดียว
```
Draw Rion from Image 1 as an 8-frame one-shot melee attack, 2 rows x 4 cells, side view facing LEFT in EVERY cell.
He holds a small KITCHEN KNIFE (short blade, wooden handle) in his front hand — not a sword.
F1 ready stance, F2 wind-up: knife pulled back behind the shoulder, knees bent, weight on the back foot,
F3 lunge starts: front foot steps forward, F4 strike: knife slashes forward and down with a short white slash arc
in front of him, F5 follow-through: arm across the body, F6 hold, F7 recover, F8 back to ready stance.
The slash arc appears only in F4-F5 and stays inside the cell.
```

## 7 · โดนตี (hurt) — 6 เฟรม เล่นครั้งเดียว
```
Draw Rion from Image 1 as a 6-frame one-shot hurt reaction, 2 rows x 3 cells, side view facing LEFT in EVERY cell
(the hit comes from the left). F1 impact: head snaps back, eyes squeezed shut, small yellow impact star near the head,
F2 recoil: body leans back, arms flung out, F3 stagger back one step, F4 regain balance, knees bent, F5 straighten,
F6 back to ready stance.
```

## 8 · ล้มคุกเข่า (kneel) — 6 เฟรม เล่นครั้งเดียว ค้างเฟรมสุดท้าย
```
Draw Rion from Image 1 as a 6-frame one-shot collapse to one knee, 2 rows x 3 cells, side view facing LEFT in EVERY cell.
F1 standing hurt, wobbling, F2 knees buckle, F3 back knee drops toward the ground, F4 back knee touches the ground,
front foot flat, F5 near hand reaches down, F6 HOLD: down on ONE knee, upper body leaning forward exhausted,
head lowered, near hand touching the ground, other hand on the front knee. Only one knee and one hand on the ground —
he is NOT crawling on all fours. (Pose reference: the kneeling mannequin in the attached pose sheet, if attached.)
```

## 9 · ล้มนอน (death) — 8 เฟรม เล่นครั้งเดียว ค้างเฟรมสุดท้าย
```
Draw Rion from Image 1 as an 8-frame one-shot knock-out fall, 2 rows x 4 cells, facing LEFT in EVERY cell.
F1 hit and stagger, F2 knees give way, F3 falling forward, F4 hands and knees hit the ground, F5 body slumps down,
F6 lying face down, head toward the LEFT, F7 small bounce settle, F8 HOLD lying still face down, head toward the LEFT.
The lying frames stay fully inside the cell, on the ground line.
```

## 10 · ร่ายเวทย์ พนมมือ → คลื่นพลัง (skill) — 8 เฟรม เล่นครั้งเดียว
```
Draw Rion from Image 1 as an 8-frame one-shot magic cast, 2 rows x 4 cells, side view facing LEFT in EVERY cell.
Rion is visible in ALL 8 cells.
F1 pray: palms pressed together in front of the chest, eyes closed, F2 deeper: knees bend, small blue glow between
the palms, F3 peak charge: lowest crouch, glow strongest, F4 release: both palms push forward to the left, a BLUE energy
wave bursts from the palms in front of him, F5 the wave travels further left and widens while Rion keeps his palms
forward, F6 the wave fades, Rion pulls his hands back, F7 standing, breathing, F8 back to ready stance.
The wave is always in front of him (to the left) and never covers or replaces him.
```

## 11 · วิ่ง (run_left) — 6 เฟรม วน
```
Draw Rion from Image 1 as a 6-frame looping run cycle, 2 rows x 3 cells, side view facing LEFT in EVERY cell.
F1 push-off: rear leg extended behind, front knee driving up, body leaning forward, F2 flight: BOTH feet off the ground,
F3 front foot lands under the body, F4 push-off with the other leg, F5 flight: both feet off the ground,
F6 landing, loops to F1. Strong forward lean, arms pump opposite to the legs, backpack bounces one frame behind.
```

## ตรวจก่อนส่ง (ดูด้วยตา)
- ทุกช่องในชีตเดียวกันหันทิศเดียวกัน · มี Rion ทุกช่อง · ไม่มีตัวหนังสือ/เส้นตาราง
- หมวก/กางเกง/เนคไทน้ำเงินสดแบบภาพ 1 (ไม่ใช่เทาหม่น) · นาฬิกาข้อมือซ้าย · มีดทำครัวไม่ใช่ดาบ
- เท้าไม่โดนตัด · ขนาดตัวเท่ากันทุกช่อง

## แบบรวมก้อนเดียว (kwan 15 ต.ค. "ขอคำสั่งรวมเป็นก้อนเดียว กอปวาง")
ชีตเดียว 11 แถว (แถวละ 1 ท่า · สูงสุด 8 ช่อง) = 76 ภาพในภาพเดียว → แต่ละตัวเล็กกว่าเจนทีละท่ามาก · ถ้าออกมาเล็ก/ทิศเพี้ยน ให้กลับไปใช้แบบทีละท่าข้างบน
แนบภาพ 1 = `rion_front_src.png` (+ `pose_refs/pose_refs_v1.png` ถ้าต้องการ) · วางก้อนเดียวในแชท (ข้อความเต็มอยู่ในคำตอบของ Claude วันที่ 15 ต.ค.)

## รอบ 3 — คำสั่งรวมแก้ปัญหาที่ค้าง (kwan 15 ต.ค. "ขอ prompt สั่งใหม่ ที่แก้ปัญหาที่ค้างอยู่ และไฟล์เป็น png")
ปัญหาจากรอบ 2 (`flow_trial_v1.jpg` · ตรวจใน https://claude.ai/artifact/Lijbtbm4Eyz4Xmg1mDPifV) → ข้อที่เพิ่มในคำสั่ง:
| ปัญหารอบ 2 | แก้ด้วย |
|---|---|
| ท่าในศึก 6 ท่าหันขวา/3-4 | บอกทิศด้วยสิ่งที่เห็น: จมูก มีด คลื่น ชี้ขอบซ้าย · เป้อยู่ฝั่งขวาของตัว · ห้ามมุม 3/4 |
| ล้มนอน ช่วงล้มหันขวา นอนหัวซ้าย | ล้มไปข้างหน้าทางซ้ายตลอดคลิป |
| เฟรม 1 ท่าวนต่างจากเฟรมอื่น 31–43% (กระตุก) | เฟรม 1 ต้องเป็นท่าเดียวกับชุด · ตำแหน่ง/ขนาดเท่ากัน · เฟรมสุดท้ายต่อเฟรม 1 |
| เดินหัวไม่ขึ้นลง · เดินหน้าขาขยับน้อย | ตัวลง 3–4 จุดตอนแตะพื้น ขึ้นตอนก้าวผ่าน · ก้าวขาชัด |
| เดินขวานาฬิกาแขนใกล้ | นาฬิกาข้อมือซ้าย = แขนไกล ซ่อน |
| คลื่นสกิลคร่อมเส้นช่อง | ทุกอย่างอยู่ในช่องตัวเอง เว้นขอบ 10% · คลื่นเล็กลงให้พอดีช่อง |
| วิ่งจังหวะลอยไม่ชัด | เฟรม 2 และ 5 เท้าลอยทั้งสองข้าง เห็นช่องใต้เท้า |
| JPG | ดาวน์โหลดจาก Flow เป็น PNG ขนาดเต็ม ไม่ส่งผ่านภาพในแชท (คำสั่งในภาพบังคับชนิดไฟล์ไม่ได้) |
แนบภาพ 1 = `rion_front_src.png` · วางก้อนเดียว (ข้อความเต็มอยู่ในคำตอบของ Claude 15 ต.ค.) · ผมต้องวัดเส้นตาราง (CX/RY ใน rion_flow_cut.py) ใหม่เมื่อได้ภาพ

## รอบ 4 — ยอมให้หันขวา แล้วพลิกด้วยโค้ด (kwan 15 ต.ค. "ขอ promt" หลังรอบ 3)
รอบ 3 (ภาพหน้าจอ Flow บน iPad · ไม่ได้ไฟล์) สั่งหันซ้ายละเอียดแล้ว ท่าในศึกยังหันขวาทุกท่า · เดินขวาออกมาหันซ้าย · สกิล 2 ช่องไม่มีตัว · ตารางแถวล่างกว้างไม่เท่าแถวบน
→ เลิกฝืน: ท่าในศึกสั่งหันขวา (ตามที่ Flow ถนัด) แล้ว `rion_flow_cut.py` พลิกเป็นหันซ้ายตอนตัด · เดินซ้าย = พลิกจากเดินขวา (เหลือ 10 แถว ช่องใหญ่ขึ้น)
ผลที่ต้องรู้: พลิกแล้วนาฬิกาอยู่ผิดข้อมือ (ลบด้วยโค้ดได้แบบท่า #4) · ข้อความคำสั่งเต็มอยู่ในคำตอบของ Claude 15 ต.ค.

## รอบ 5 — ชีตเสริม (kwan 15 ต.ค. "อยากให้อีกค่ายเจนอะไรเพิ่มไหม ขอ prompt เดียว")
ภาพที่ส่งมาพร้อมคำถาม = ชีตรอบ 3 เดิม (md5 ตรงกับ `flow_trial_v3.jpg`) · ชีตเสริมขอเฉพาะสิ่งที่โค้ดแก้/สร้างไม่ได้:
1–3 เดินหน้า/หลัง/ซ้ายใหม่ (เฟรม 1 ต่อเนื่อง + ตัวขึ้นลง) · 4 คุกเข่ามือแตะพื้น (รอบ 3 มีแต่คลานสี่ขา) · 5 ตั้งรับ (คำสั่งตั้งรับในศึก) ·
6 หลบ (ป้าย "หลบ!" ของระบบอ่านทางหลบ) · 7 จับตา (คำสั่งของ Rion) · 8 กระโดดม้วน → ลงคุกเข่าฟันสองมือ (คลิป SL01 ในหน้า animation test) · 9 ชนะ เต้นสามช่า (ท่าชนะที่ kwan สั่ง 10 ต.ค.)
ท่าในศึกสั่งหันขวา (Flow ถนัด) แล้วพลิกตอนตัด · เดินขวาได้จากพลิกเดินซ้าย · ข้อความคำสั่งเต็มอยู่ในคำตอบของ Claude 15 ต.ค.

### ผลรอบ 5 (GPT เจน 2 ชีต PNG · ไม่มีเส้นตาราง) — `flow_trial_v5a.png` 1214x1295 · `flow_trial_v5b.png` 1326x1186
ตัด: `cut_free()` (ก้อนตัว → แถวที่ใกล้สุด · ก้อนสูงเกินแยกที่กลางแถว · เศษเล็กรวมเข้าตัวใกล้สุด) · ท่าในศึกพลิกให้หันซ้าย · หน้าเทส Version 8 ปุ่ม "รอบ 5 ชีต A/B"
ได้: เดิน 3 ทิศวนเรียบทั้งสองชีต (ต่าง 26–56%/เฟรม ไม่มีเฟรม 1 กระโดดแบบรอบ 3) · หัวขึ้นลง 1–4 จุด · ม้วนกลางอากาศ + ลงฟันมีรอยมีด · หลบ · มองไกล · ชนะหันหน้า
**แก้ด้วยโค้ดแล้ว**:
- เดินขวา = พลิกเดินซ้าย + ลบนาฬิกา (`erase_watch_free`: หาแกนหน้าปัดฟ้าอ่อนใต้ท่อนแขนแคบ เอาก้อนบนสุดก้อนเดียว · ทาเฉพาะช่วงแขนด้วยสีผิวใกล้สุด + เส้นขอบ) · ตรวจด้วยตาครบ A 8 / B 6 เฟรม
  วิธีเดิมของรอบ 3 (คัดลอกกรอบ) ใช้ไม่ได้ — ก้อนฟ้าติดเนคไท ลากลายกางเกงมาเป็นแถบ
- ขนาดแถวไม่เท่ากันในชีต (B มองไกลสูงแค่ 56% ของท่าเดิน) → `norm_rows()` ขยายทั้งแถวอัตราเดียว (เฉลี่ยเรขาคณิตของความสูงเฟรมยืนกับความกว้างหมวก เทียบท่าเดิน)
  A: ตั้งรับ ×1.13 หลบ ×1.23 มองไกล ×1.32 ม้วน ×1.30 ชนะ ×1.16 · B: ×1.25 ×1.32 ×1.47 ×1.33 ×1.36 (ภาพที่ขยายนุ่มลงเล็กน้อย)
- คุกเข่าตัดเฟรมคลานสี่ขาท้ายแถว (A เหลือ 4 · B เหลือ 4)
**แก้ด้วยโค้ดไม่ได้ (ต้องเจนใหม่ถ้าต้องการ)**: คุกเข่าไม่มีมือแตะพื้นทั้งสองชีต · A ตั้งรับ = มือกุมหน้า ไม่ใช่การ์ด · ลงฟันมือเดียว ไม่ใช่สองมือ ·
ชนะไม่เป็นสามช่าชัด (ชูมือ/โบก/กระโดด) · B เดินซ้าย 6 เฟรม · B มองไกล 3 เฟรม · B เดินขวาเหลือเศษสายนาฬิกา 1–2 จุดที่ขอบข้อมือ
