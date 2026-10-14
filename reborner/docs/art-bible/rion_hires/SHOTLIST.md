# Rion ภาพใหญ่ — รายการภาพที่ต้องเจน (ขั้น 1 · kwan 14 ต.ค. 2026)

ต้นแบบ = `rion_front_src.png` (หันหน้า · ทำแล้ว Version 85) · **แนบภาพนี้เป็นภาพอ้างอิงทุกครั้ง**
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
Canvas 1145x1374, character about 1130 px tall, feet at the same height as the reference.
```

## รายการ (เรียงตามความสำคัญ)

| # | ไฟล์ | ใช้ในเกม | คำสั่งเฉพาะภาพ |
|---|---|---|---|
| 1 | rion_front_src.png | เดินหน้า | ✅ มีแล้ว |
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

## ตรวจก่อนส่ง (ดูด้วยตา)
- หมวกน้ำเงินทั้งใบ · นาฬิกาข้อมือซ้าย · เป้มีสายสองข้าง · ไม่มีของเกินมา (เข็มขัดเพิ่ม/กระเป๋าใหม่)
- หน้าเหมือนภาพ 1 (ตา ผม ทรงหน้า) · ไม่มีเงาบนพื้นเขียว · เท้าไม่ถูกตัดขอบภาพ
- ถ้าผิดข้อไหน เจนใหม่ภาพนั้น หรือส่งมาได้ ผมแก้สีเล็กน้อยได้ (แบบหน้าหมวกครีม) แต่แก้รูปทรง/หน้าไม่ได้

## ฝั่ง Claude เมื่อได้ภาพ
แยกชิ้น (หัว ตัว แขน ขา) ด้วยพิกัดต่อภาพ → ขยับด้วยโค้ดชุด rion_smooth / rion_hd → ย่อ 64 + ล็อกสี Rion → ทับไฟล์ชื่อเดิมใน `rion_lastlight_draft` (ร่าง) → หน้า animation test → kwan ดู → เข้าเกม
