# Rion · MASTER (kwan 18 ต.ค. 2026: "ตั้งแต่นี้ นี่คือ master ของ rion การออกแบบ และ prompt ทุกอย่างต้องเข้ากับคอนเซปนี้")

ภาพ master: `rion_master_v1.jpg` (1438x2576 · พื้นเขียว chroma-key · หน้าตรงยืนนิ่ง · พิกเซล 32-bit)
แทนที่ `rion_flow_ref.png` เป็นภาพอ้างอิงหลัก · ภาพ/ชีตเดิมที่ตรงแบบนี้ (หมวกน้ำเงินทั้งใบ แว่นทองเหลือง) ยังใช้ได้

## Prompt ต้นฉบับ (ใช้คำตามนี้ทุกตัวอักษรเมื่อต้องบรรยายตัว Rion)

### ตัวละคร (CHARACTER)
```
Chibi boy hero.
Messy medium-brown hair with side-swept bangs, ears visible. Blue cap with a small button on top, brass-gold rimmed goggles with blue lenses resting on the front of the cap. Big round dark-brown eyes, tiny dot nose, small gentle smile, light pink blush on both cheeks.
White short-sleeve collared shirt, blue necktie, blue knee-length shorts with cuffed hems, brown belt with a square gold buckle. Brown backpack with two side pouches and gold buckles on the shoulder straps. Blue digital wristwatch on the left wrist. White socks, brown lace-up boots with tan toe caps and thick tan soles.
```

### พื้นหลัง (BACKGROUND)
```
Solid flat pure green chroma-key background, no shadow, no ground line, no text, no watermark, no extra props.
```

### สไตล์ (STYLE) — ต่อท้ายทุก prompt
```
2D pixel art, classic 32-bit era style (16/32-bit JRPG, SNES and PlayStation 1 look), crisp square pixels, limited palette, flat shading with hard edges, no anti-aliasing, no smooth gradients, no 3D rendering.
```

### ภาพหน้าตรง (ท่าของภาพ master)
```
front view, full body, standing still with arms relaxed at his sides, feet planted at the bottom edge, centered, single character.
```

### การจัดชีต (SHEET LAYOUT) — ใส่ทุกชีตท่าขยับ ลดงานตัดภาพ (บทเรียนชีตเดินแรก 18 ต.ค.: ตัวชิดกันจนเศษเท้า/หมวกติดเฟรมข้าง)
```
Exactly 6 frames in ONE horizontal row. Wide empty green gaps between frames: at least half a character width of pure green between any two characters, no body part, shadow or effect may cross into the gap. Same character size and same head-to-body proportions in every frame, feet on one shared baseline, the character fills most of the image height.
```

### ทิศ (DIRECTION) — Flow ชอบวาดหันขวาเสมอ ต้องบอกด้วยส่วนของร่างกาย ไม่ใช่แค่คำว่า left/right
```
LEFT:  Side view facing LEFT: nose, cap brim and toes point to the LEFT edge of the image; the backpack is on the RIGHT side of the body. The left arm with the blue watch is the near arm, fully visible.
RIGHT: Side view facing RIGHT: nose, cap brim and toes point to the RIGHT edge of the image; the backpack is on the LEFT side of the body. The left arm with the blue watch is the far arm, mostly hidden behind the body; never draw the watch on the near arm.
```

## กฎสำหรับ prompt ใหม่ทุกชิ้น
1. แนบ `rion_master_v1.jpg` เป็นภาพอ้างอิงตัวละคร (ภาพ 1)
2. ใช้บล็อก CHARACTER + STYLE ข้างบนตามตัวอักษร · เปลี่ยนเฉพาะส่วนท่า/มุม/จำนวนช่อง
3. พื้นหลังเขียว chroma-key ตามบล็อก BACKGROUND (ตัวตัดพื้น `rion_pack_cut.py` ใช้คีย์เขียวอยู่แล้ว)
4. นาฬิกาอยู่ข้อมือซ้ายของตัวละครเสมอ (หันขวา = แขนไกล · หันซ้าย = แขนใกล้)
5. มอน/NPC/เอฟเฟกต์ใช้บล็อก STYLE เดียวกัน (พิกเซล 32-bit ขอบแข็ง ไม่ไล่สี) ให้เข้ากับ Rion
