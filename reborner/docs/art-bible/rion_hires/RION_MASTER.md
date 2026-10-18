# Rion · MASTER (kwan 18 ต.ค. 2026: "ตั้งแต่นี้ นี่คือ master ของ rion การออกแบบ และ prompt ทุกอย่างต้องเข้ากับคอนเซปนี้")

ภาพ master: **`rion_master_v2.png`** (1438x2576 · พื้นเขียว chroma-key · หน้าตรงยืนนิ่ง · พิกเซล 32-bit · **ไม่มีนาฬิกา**)
**18 ต.ค. 2026 kwan เลือก "1": Rion ไม่มีนาฬิกา** (Flow วาดนาฬิกาสลับแขนทุกชีตท่าเดิน · นาฬิกาไม่อยู่ในเรื่อง) · v2 = v1 ที่ลบนาฬิกาด้วยโค้ด `tools/sprites/rion_master_nowatch.py` · `rion_master_v1.jpg` เก็บไว้เทียบ ห้ามแนบให้ Flow
แทนที่ `rion_flow_ref.png` เป็นภาพอ้างอิงหลัก · ภาพ/ชีตเดิมที่ตรงแบบนี้ (หมวกน้ำเงินทั้งใบ แว่นทองเหลือง) ยังใช้ได้

## Prompt ต้นฉบับ (ใช้คำตามนี้ทุกตัวอักษรเมื่อต้องบรรยายตัว Rion)

### ตัวละคร (CHARACTER)
```
Chibi boy hero.
Messy medium-brown hair with side-swept bangs, ears visible. Blue cap with a small button on top, brass-gold rimmed goggles with blue lenses resting on the front of the cap. Big round dark-brown eyes, tiny dot nose, small gentle smile, light pink blush on both cheeks.
White short-sleeve collared shirt, blue necktie, blue knee-length shorts with cuffed hems, brown belt with a square gold buckle. Brown backpack with two side pouches and gold buckles on the shoulder straps. Bare wrists, no wristwatch. White socks, brown lace-up boots with tan toe caps and thick tan soles.
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

### การจัดชีต (SHEET LAYOUT) — ใส่ทุกชีตท่าขยับ
แก้ 18 ต.ค. รอบ 2: รอบแรกสั่ง "ตัวสูงเกือบเต็มภาพ" + 6 ภาพแถวเดียวบน 16:9 = ขัดกันเอง (ช่องละ ~230 จุด ตัวกว้าง ~250) Flow จึงทิ้งช่องว่าง → ใช้ 2 แถว × 4 ภาพ ตัวสูงราว 1/3 ของภาพ
```
8 frames arranged in a grid of 2 rows x 4 columns, read left to right, top row first. Each character is about one third of the image height, centered in its own cell. Wide empty green space around every character: no body part, shadow or effect touches or crosses into another cell. Same character size and same head-to-body proportions in every frame, feet on the same baseline within each row.
```

### ทิศ (DIRECTION)
แก้ 18 ต.ค. รอบ 3: เคยสรุปว่า "Flow วาดหันขวาเสมอ" = **ผิด** · ชีตเวทย์ของ Muse 4 ชีต + เดินซ้ายของ Muse หันซ้ายถูกทุกภาพ
ที่ต่าง: ชีตของ Muse มี "สิ่งที่ตัวละครหันไปหา" อยู่ทางซ้าย (เวทย์พุ่งไปทางซ้าย) และเป็นภาพแนวตั้ง · prompt ท่าเดินของ Claude ไม่มีเป้าหมายในภาพ → Flow ใช้ทิศตั้งต้น (หันขวา)
**กฎท่าในศึก (kwan 18 ต.ค.): ทุกท่าหันซ้าย ยกเว้นท่าที่ต้องหันหลัง** — มอนอยู่ซ้าย Rion หันซ้ายเข้าหามอน
- ท่าปกติใช้บล็อก LEFT · ถ้า Flow วาดหันขวามา โค้ดพลิกให้ (มือถือมีดสลับข้างตามภาพพลิก)
- ท่าที่ต้องหันหลังใช้บล็อก BACK · ต้องเขียนใน prompt ของท่านั้นว่าหันหลัง ไม่งั้นถือว่าหันซ้าย
**ท่าเดินบนแผนที่ ไม่ต้องสั่งทิศ (kwan 18 ต.ค.)** — Flow วาดทิศไหนมาก็ใช้ได้ · โค้ดพลิกภาพให้ได้อีกทิศ (คำสั่ง `flip` ในตัวตัด ไม่เสียเครดิตเจน ไม่เสียโทเคน) · ไม่ต้องเจนซ้ำเพื่อแก้ทิศ
```
LEFT:  Side view facing LEFT, toward an enemy off-screen on the left: nose, cap brim and toes point to the LEFT edge of the image; the backpack is on the RIGHT side of the body.
BACK:  Back view, seen from behind: the backpack faces the viewer and covers the upper back, the face is not visible, only the back of the cap and hair.
RIGHT: Side view facing RIGHT: nose, cap brim and toes point to the RIGHT edge of the image; the backpack is on the LEFT side of the body.
```

## กฎสำหรับ prompt ใหม่ทุกชิ้น
1. แนบ `rion_master_v2.png` เป็นภาพอ้างอิงตัวละคร (ภาพ 1)
2. ใช้บล็อก CHARACTER + STYLE ข้างบนตามตัวอักษร · เปลี่ยนเฉพาะส่วนท่า/มุม/จำนวนช่อง
3. พื้นหลังเขียว chroma-key ตามบล็อก BACKGROUND (ตัวตัดพื้น `rion_pack_cut.py` ใช้คีย์เขียวอยู่แล้ว)
4. ท่าในศึกหันซ้ายทุกท่า (บล็อก LEFT · บอกว่าหันไปหาศัตรูทางซ้าย) ยกเว้นท่าที่ต้องหันหลัง (บล็อก BACK) · ท่าเดินแผนที่ไม่ใส่บล็อก DIRECTION (ทิศไหนก็ได้ โค้ดพลิกให้อีกทิศ)
5. มอน/NPC/เอฟเฟกต์ใช้บล็อก STYLE เดียวกัน (พิกเซล 32-bit ขอบแข็ง ไม่ไล่สี) ให้เข้ากับ Rion
