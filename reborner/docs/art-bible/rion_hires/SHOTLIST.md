# Rion ภาพใหญ่ — รายการภาพที่ต้องเจน (ขั้น 1 · kwan 14 ต.ค. 2026)

ต้นแบบ = `rion_front_src.png` (หันหน้า · Version 86 = ภาพที่ kwan เจนใหม่ หมวกน้ำเงินทั้งใบ · ภาพเดิม = `rion_front_src_v1.png` ไม่ใช้อ้างอิงแล้ว) · **แนบภาพนี้เป็นภาพอ้างอิงทุกครั้ง**
ได้ภาพแล้ววางในโฟลเดอร์นี้ตามชื่อไฟล์ในตาราง (หรือส่งในแชทพร้อมบอกเลขภาพ)

## กฎกลาง (ใส่ท้ายคำสั่งทุกภาพ)

```
Same character as the reference image, identical design: ALL-BLUE baseball cap (no cream or white panel),
brass goggles resting on the cap, brown messy hair, brown eyes, white short-sleeve collared shirt,
blue necktie, blue shorts with brown belt, brown backpack with two shoulder straps and side pouches,
blue wristwatch on his left wrist, white socks, brown lace-up boots. Same chibi proportions (big head).
Clean bold dark outlines, flat cel-shaded colors, no gradients, no texture, NOT pixel art.
Full body, feet fully visible, arms and legs clearly separated from the body where the pose allows.
Solid pure green background (#00B140), no shadow, no text, no props unless stated.
Canvas 1145x1374, character about 1210 px tall (cap top to boot soles), feet at the same height as the reference.
```

> แก้ 14 ต.ค.: เดิมเขียน "about 1130 px tall" แต่ต้นฉบับวัดจริงได้ตัวสูง 1211 (y106–1316 · ยอดปุ่มหมวกถึงพื้นรองเท้า) · เท้าล่างสุดแถว 1316 · กลางตัว x571 → แก้เป็น 1210 ให้ตรงต้นฉบับ

## ตรวจภาพที่เจนก่อนใช้ (เครื่องตรวจ)
`python3 tools/sprites/rion_ref.py check <ภาพ.png> [...]` — ขนาดผืน · พื้นเขียว · ตัวสูง ±5% · แถวเท้า ±15 · กลางตัว ±60 · ตัวไม่ชนขอบ ·
สีแปลกปลอม ≤ 1% (ต้นฉบับเอง 0.3% · บอกสีที่เกินมา) · แถบครีม/ขาวบนหมวก ≤ 2% · เงาใต้เท้า ≤ 1%
ผ่านทุกข้อ = ไม่มีปัญหาที่วัดได้เท่านั้น · หน้าตา (ตา ผม ทรงหน้า) ต้องดูด้วยตาเทียบภาพ 1 เสมอ

## รายการ (เรียงตามความสำคัญ)

| # | ไฟล์ | ใช้ในเกม | คำสั่งเฉพาะภาพ |
|---|---|---|---|
| 1 | rion_front_src.png | เดินหน้า | ✅ มีแล้ว (Version 86) |
| 2 | rion_back.png | เดินขึ้น | Back view, facing away from the camera, standing straight, arms slightly away from the body. |
| 3 | rion_left.png | เดินซ้าย · ยืนในจอสู้ | Side view facing LEFT (profile), standing straight, arms relaxed at the sides. |
| 4 | rion_right.png | เดินขวา | Side view facing RIGHT (profile), standing straight, arms relaxed at the sides. (เจนแยก ห้ามพลิกภาพ — เป้/นาฬิกาอยู่คนละข้าง) |
| 5 | rion_left_windup.png | ฟัน: ง้าง | Facing LEFT, holding a kitchen knife in his front hand, arm pulled back behind the shoulder ready to strike, knees slightly bent. |
| 6 | rion_left_strike.png | ฟัน: ฟาด | Facing LEFT, lunging forward and slashing the kitchen knife forward and down, front foot stepping forward. |
| 7 | rion_left_hurt.png | โดนตี | Facing LEFT, recoiling backwards from a hit, body leaning back, eyes squeezed shut, arms flung out. |
| 8 | rion_left_kneel.png | ล้ม (ทรุดเข่า) | Facing LEFT, collapsed down on one knee, exhausted, head lowered, one hand on the ground. |
| 9 | rion_left_down.png | ล้ม (นอน) | Lying face down on the ground, knocked out, head toward the LEFT. |
| 10 | rion_left_pray.png | ร่ายเวทย์ (พนมมือ) | Facing LEFT, palms pressed together in front of the chest (prayer pose), eyes closed, focused. |
| 11 | rion_left_cast.png | ร่ายเวทย์ (ผลักปล่อย) | Facing LEFT, both palms pushed forward toward the left at chest height, releasing magic, front foot forward. |
| 12 | rion_left_run.png | วิ่ง | Facing LEFT, running mid-stride, one leg forward one leg back, arms swinging. (ไม่บังคับ) |
| 13 | battle_bg_act1.png | ฉากหลังจอต่อสู้ (ไม่ต้องแนบภาพ Rion · ไม่ใช้กฎกลาง) | **คำสั่งแยก** ดูหัวข้อ "ภาพ 13" ข้างล่าง |

## ภาพ 13 — ฉากหลังจอต่อสู้ (ขั้น 1 แนวภาพคม · kwan 14 ต.ค. เลือก "ขั้น 1: Rion + ฉากต่อสู้")
ใช้แทนพื้นสีเรียบ (ฟ้า A7B5A0 + ดิน D4B08A) ในแถบเวทีของจอสู้ · องก์ 1 ตาม GDD = เขียวชอุ่ม ฟ้าใส ทองอุ่น แนวจิบลิ
```
Wide side-view background for a 2D JRPG battle scene, same flat cel-shaded anime style as the character art
(clean dark outlines, flat colors, soft simple shading, NOT pixel art). Peaceful countryside on a sunny afternoon:
clear light-blue sky with a few soft clouds, distant green hills, a few trees far away, warm golden light.
The bottom 30% is flat open ground (short grass and a sandy dirt path) seen from the side, completely empty
where characters will stand. Calm, low detail, muted enough that characters in front stay readable.
No characters, no animals, no text, no UI. Landscape 1920x1080.
```
ผมตัดเป็นแถบเวที (กว้าง:สูง ≈ 4.9:1) เส้นพื้นอยู่ ~73% จากบนของแถบ · ถ้าพื้นในภาพสูง/ต่ำไปผมเลื่อนได้

## ตรวจก่อนส่ง (ดูด้วยตา)
- หมวกน้ำเงินทั้งใบ · นาฬิกาข้อมือซ้าย · เป้มีสายสองข้าง · ไม่มีของเกินมา (เข็มขัดเพิ่ม/กระเป๋าใหม่)
- หน้าเหมือนภาพ 1 (ตา ผม ทรงหน้า) · ไม่มีเงาบนพื้นเขียว · เท้าไม่ถูกตัดขอบภาพ
- ถ้าผิดข้อไหน เจนใหม่ภาพนั้น หรือส่งมาได้ ผมแก้สีเล็กน้อยได้ (แบบหน้าหมวกครีม) แต่แก้รูปทรง/หน้าไม่ได้

## ฝั่ง Claude เมื่อได้ภาพ
แยกชิ้น (หัว ตัว แขน ขา) ด้วยพิกัดต่อภาพ → ขยับด้วยโค้ดชุด rion_smooth / rion_hd → ย่อ 64 + ล็อกสี Rion → ทับไฟล์ชื่อเดิมใน `rion_lastlight_draft` (ร่าง) → หน้า animation test → kwan ดู → เข้าเกม

## ภาพ 4 · 8 · 10 รอบ 2 — แนบภาพอ้างอิงท่าจากหุ่น 3D (kwan 14 ต.ค. ลอง ActionForge → เลือก "1")
รอบแรก (ชีต v1) ใช้ไม่ได้ 3 ท่า: หันขวาได้ภาพพลิก · พนมมือหันหน้าตรง · ทรุดเข่าเป็นคลานสี่ขา → รอบนี้แนบภาพหุ่นจัดท่าให้ด้วย
ภาพหุ่น: `pose_refs/pose_refs_v1.png` (ชีตรวม 3 ท่า) หรือแยก `right_180.png` `pray_0.png` `kneel_0.png` · สร้างซ้ำ `python3 tools/sprites/rion_pose_refs.py <glb>`
**แนบ 2 ภาพ: ภาพ 1 = `rion_front_src.png` (หน้าตา/ชุด) · ภาพ 2 = `pose_refs_v1.png` (ท่า)** แล้ววางคำสั่งนี้ทั้งก้อน:
```
Image 1 is the character (the only source for his face, hair, outfit and colors). Image 2 is a plain 3D mannequin showing POSES ONLY.
Draw the character from Image 1 in each of the three mannequin poses from Image 2, left to right, as one sheet:
1) standing straight, true side profile facing RIGHT, arms relaxed at the sides (draw this view, do NOT mirror the left view:
   his wristwatch stays on his LEFT wrist, which is the far-side arm in this view);
2) true side profile facing LEFT, palms pressed together in front of the chest (prayer pose), eyes closed, calm and focused;
3) facing LEFT, collapsed down on ONE knee: front foot flat on the ground, back knee touching the ground, upper body leaning
   forward and exhausted, head lowered, near hand touching the ground in front, other hand resting on the front knee.
   Only one knee and one hand on the ground, he is NOT crawling on all fours.
Copy only the body angles from the mannequin; keep the character's own chibi proportions (big head, short limbs) from Image 1.
Same character as Image 1, identical design: ALL-BLUE baseball cap (no cream or white panel), brass goggles resting on the cap,
brown messy hair, brown eyes, white short-sleeve collared shirt, blue necktie, blue shorts with brown belt, brown backpack with
two shoulder straps and side pouches, blue wristwatch on his left wrist, white socks, brown lace-up boots.
Clean bold dark outlines, flat cel-shaded colors, no gradients, no texture, NOT pixel art. Full body, feet fully visible.
Solid pure green background (#00B140), no shadow, no text, no mannequin in the output, characters well separated from each other.
```
ได้ภาพแล้วส่งมา → ผมตัด/ย่อด้วย `rion_poses.py` แบบชีต v1 + ตรวจด้วยตาเทียบภาพ 1
