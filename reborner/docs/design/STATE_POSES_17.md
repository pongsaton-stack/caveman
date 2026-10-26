# รายการ State ท่าตัว · ต้นไม้ 17 ท่า × 6 สาย (ร่างให้ kwan ตรวจ · 19 ต.ค. 2026)

สร้างจาก `tools/sprites/pixellab_states17.py` · 77 State (ทำแล้ว 1: SL_A_stance = fight_knife) · prio 1 = 65 · prio 2 = 12
ราคา: 15 gen/State (หักจริง 19 ต.ค.) → ทั้งหมด ≈ 1140 gen · เฉพาะ prio 1 ≈ 960 gen · ท่าขยับจาก State อีกท่าละ 2–3 gen (102 ท่า ≈ 300 gen)
ตรวจอัตโนมัติ: ทุกท่าในต้นไม้มี State รองรับ ครบ · คำสั่งยาวเกิน 1000 ตัวอักษร 0 รายการ

ของในมือ = อาวุธตัวแทนกิ่ง (A/B/C) จาก `REP` · ท่าที่ต้องใช้ของเฉพาะ (โบลา หน้าไม้กล สว่าน ขาตั้ง ถุงผง สายพ่น ตะขอ) ระบุแยก

## คม

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `SL_A_stance` | A | 1 | ยืนสู้ถือมีด (ทำแล้ว = fight_knife) | bl0 bl1 bl2 bl7 bl8 bl9 bl16 |
| `SL_B_stance` | B | 1 | ยืนสู้ถือเคียว | bl3 bl4 bl10 bl11 bl12 |
| `SL_C_stance` | C | 1 | ยืนสู้ถือคัตเตอร์ | bl5 bl6 bl13 bl14 bl15 |
| `SL_A_overhead` | A | 2 | ง้างมีดเหนือไหล่ | bl0 bl2 |
| `SL_A_lunge` | A | 1 | พุ่งทั้งตัวเอนหน้า | bl1 bl16 |
| `SL_A_low` | A | 1 | ย่อต่ำฟันข้อเท้า | bl7 |
| `SL_A_twohand` | A | 1 | จับมีดสองมือเหนือหัว | bl8 |
| `SL_A_coiled` | A | 2 | เกร็งตัวรวมแรง (ฟันเดียวสุดแรง) | bl9 |
| `SL_B_sweep` | B | 1 | บิดเอวกวาดเคียวแนวนอน | bl3 bl4 bl12 |
| `SL_B_run` | B | 2 | วิ่งพุ่งถือเคียวต่ำ | bl10 |
| `SL_B_throw` | B | 1 | ขว้างเคียวแล้ว (มือว่าง) | bl11 |
| `SL_C_draw` | C | 1 | มือวางที่ด้าม พร้อมชัก (ไออิโด) | bl5 |
| `SL_C_slither` | C | 1 | ย่อต่ำก้าวไขว้ขา | bl13 |
| `SL_C_guard` | C | 1 | คัตเตอร์ขวางตัวรอสวน | bl15 |

## ทุบ

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `BT_A_stance` | A | 1 | ยืนสู้ถือค้อน | bt0 bt1 bt2 bt7 bt8 bt9 bt16 |
| `BT_B_stance` | B | 1 | ยืนสู้ถือไม้กวาด | bt3 bt4 bt10 bt11 bt12 |
| `BT_C_stance` | C | 1 | ยืนสู้ถือกระทะ | bt5 bt6 bt13 bt14 bt15 |
| `BT_A_overhead` | A | 1 | ยกค้อนเหนือหัวสองมือ | bt0 bt2 bt16 |
| `BT_A_windback` | A | 1 | ง้างค้อนไปหลังเต็มแขน | bt1 bt9 |
| `BT_A_lowsweep` | A | 1 | ย่อต่ำเหวี่ยงเลียดพื้น | bt7 |
| `BT_A_reverse` | A | 2 | กลับด้านค้อน สับด้วยด้านเขี้ยว | bt8 |
| `BT_B_sumo` | B | 1 | ยกเข่าสูงแบบซูโม่ | bt3 |
| `BT_B_overhead` | B | 2 | ยกไม้กวาดเหนือหัวสองมือ | bt4 |
| `BT_B_swing` | B | 1 | เหวี่ยงไม้กวาดแนวนอน | bt10 bt11 bt12 |
| `BT_C_bind` | C | 2 | ใช้กระทะขัดล็อกอาวุธ | bt13 |
| `BT_C_forearm` | C | 1 | กระทะแนบแขน ก้าวลึก (ไม้ศอก) | bt14 |
| `BT_C_guard` | C | 1 | กระทะทแยงหน้าตัวรอสวน | bt15 |

## แทง

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `PT_A_stance` | A | 1 | ยืนสู้ถือไขควง | pt0 pt1 pt2 pt7 pt8 pt9 pt16 |
| `PT_B_stance` | B | 1 | ยืนสู้ถือหอกไม้ไผ่ | pt3 pt4 pt10 pt11 pt12 |
| `PT_C_stance` | C | 1 | ยืนสู้ถือส้อม | pt5 pt6 pt13 pt14 pt15 |
| `PT_A_lunge` | A | 1 | ลันจ์ฟันดาบ แขนเหยียดสุด | pt1 pt2 pt16 |
| `PT_A_lowstab` | A | 1 | ก้มต่ำแทงข้อพับ | pt7 |
| `PT_A_halfgrip` | A | 2 | จับสองมือแทงสั้นแม่น | pt8 |
| `PT_B_spin` | B | 1 | หมุนหอกเหนือหัว | pt4 pt9 |
| `PT_B_reach` | B | 1 | แทงหอกยืดสุด | pt3 pt11 pt12 |
| `PT_B_sweep` | B | 1 | จับปลายด้ามกวาดครึ่งวง | pt10 |
| `PT_C_feint` | C | 2 | ทำท่าแทงสูง (หลอก) | pt13 |
| `PT_C_guard` | C | 1 | ชี้ปลายส้อมรอสวน | pt15 |

## ยิง

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `RG_A_stance` | A | 1 | ยืนถือธนูพร้อมยิง | rg0 rg1 rg2 rg6 rg7 rg8 rg9 rg16 |
| `RG_B_stance` | B | 1 | ยืนถือปืนกระดาษสองมือ | rg3 rg4 rg11 rg12 |
| `RG_C_stance` | C | 1 | ยืนถือปืนฉีดน้ำ | rg5 rg13 rg14 rg15 |
| `RG_A_draw` | A | 1 | ง้างธนูเต็มเล็งตรง | rg1 rg2 rg6 rg8 |
| `RG_A_kneel` | A | 1 | คุกเข่าข้างเดียวยิงต่ำ | rg7 |
| `RG_A_sky` | A | 1 | เอนหลังยิงขึ้นฟ้า | rg4 rg9 rg12 |
| `RG_B_bolas` | B | 1 | หมุนโบลาเหนือหัว | rg10 |
| `RG_B_backjump` | B | 1 | กระโดดถอยหันกลับยิง | rg11 |
| `RG_C_underarm` | C | 2 | เหวี่ยงแขนจากล่างยิงโค้ง | rg14 |
| `RG_C_hip` | C | 2 | ยิงเร็วจากเอว | rg13 |
| `RG_C_lowready` | C | 1 | ถือปืนต่ำรอยิงสวน | rg15 |

## กล

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `DV_A_stance` | A | 1 | ยืนถือรีโมต | dv0 dv1 dv2 dv7 dv8 dv9 dv16 |
| `DV_B_stance` | B | 1 | ยืนถือแบต+คีมคีบ | dv3 dv4 dv10 dv11 dv12 |
| `DV_C_stance` | C | 1 | ยืนถือคีม | dv5 dv6 dv13 dv14 dv15 |
| `DV_A_point` | A | 1 | ชี้นิ้ว/กดรีโมตสั่งการ | dv0 dv1 dv6 |
| `DV_A_release` | A | 1 | ชูสองมือปล่อยอุปกรณ์ | dv2 dv16 |
| `DV_A_crank` | A | 1 | ง้างคันโยกหน้าไม้กล | dv7 |
| `DV_A_drill` | A | 1 | ดันสว่านเจาะไปหน้า | dv8 |
| `DV_A_tripod` | A | 1 | คุกเข่าตั้งขาตั้งเครื่องยิง | dv9 |
| `DV_B_poles` | B | 1 | แตะสองขั้วไฟฟ้า | dv3 |
| `DV_B_throw` | B | 1 | ปาถุงผง | dv10 |
| `DV_B_hose` | B | 1 | ถือหัวสายพ่น กวาดหน้า | dv12 |
| `DV_C_place` | C | 1 | คุกเข่าวางของบนพื้น | dv4 dv11 dv13 dv15 |
| `DV_C_hook` | C | 1 | เหวี่ยงตะขอเชือกเหนือหัว | dv14 |

## มือเปล่า

| State | กิ่ง | prio | ท่า | ท่าในต้นไม้ที่ใช้ |
|---|---|---|---|---|
| `FS_A_stance` | A | 1 | การ์ดมวยใส่นวม | fs0 fs1 fs2 fs7 fs8 fs9 fs16 |
| `FS_B_stance` | B | 1 | ยืนพร้อมผ้าพันมือ | fs3 fs4 fs10 fs11 fs12 |
| `FS_C_stance` | C | 1 | ยืนพร้อมถุงมือหนัง | fs5 fs6 fs13 fs14 fs15 |
| `FS_A_jab` | A | 1 | แย็บ แขนหน้าเหยียด | fs0 fs1 fs2 |
| `FS_A_lowkick` | A | 1 | เตะตัดขามวยไทย | fs7 |
| `FS_A_elbow` | A | 1 | หมุนตัวศอกกลับ | fs8 |
| `FS_A_knee` | A | 1 | เข่าโดด ล็อกคอ | fs16 |
| `FS_A_bigpunch` | A | 2 | หมัดตรงเต็มแรงพร้อมตะโกน | fs9 |
| `FS_B_throw` | B | 1 | ทุ่มข้ามไหล่ (ยูโด) | fs10 |
| `FS_B_capoeira` | B | 1 | ย่อมือแตะพื้นกวาดขา | fs11 |
| `FS_B_spinkick` | B | 1 | เตะหมุนกลางอากาศ | fs12 |
| `FS_B_palm` | B | 1 | ผลักฝ่ามือไทเก๊ก | fs3 fs4 |
| `FS_C_punch` | C | 2 | หมัดตรงคาราเต้ | fs5 fs6 |
| `FS_C_slip` | C | 1 | ส่ายหัวหลบ | fs13 |
| `FS_C_lock` | C | 1 | จับบิดข้อ / ไอคิโด | fs14 fs15 |

## คำสั่ง PixelLab เต็มของแต่ละ State

**SL_A_stance** · ยืนสู้ถือมีด (ทำแล้ว = fight_knife) (674 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_B_stance** · ยืนสู้ถือเคียว (668 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a farm sickle with a short wooden handle and a curved steel blade, held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_C_stance** · ยืนสู้ถือคัตเตอร์ (668 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small yellow box cutter (utility knife) with a short slim blade, held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_A_overhead** · ง้างมีดเหนือไหล่ (708 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Wind-up: the knife is raised high above and behind the front shoulder, elbow up, ready to slash diagonally downward; one step forward. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_A_lunge** · พุ่งทั้งตัวเอนหน้า (718 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Long forward lunge: front knee deeply bent, back leg straight, whole body leaning far forward, knife arm fully extended forward at chest height. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_A_low** · ย่อต่ำฟันข้อเท้า (688 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Very low crouch, one knee almost touching the ground, body bent forward, knife swept low near the ground in front. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_A_twohand** · จับมีดสองมือเหนือหัว (688 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Both hands grip the knife handle together, raised straight above the cap, ready to chop straight down; feet apart. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_A_coiled** · เกร็งตัวรวมแรง (ฟันเดียวสุดแรง) (707 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a short kitchen knife, blade about the length of the hand, held by the handle in the front hand. Pose: Coiled, tense stance before one all-out slash: deep stance, torso twisted back, knife drawn back at the rear hip, eyes fixed forward. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_B_sweep** · บิดเอวกวาดเคียวแนวนอน (693 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a farm sickle with a short wooden handle and a curved steel blade, held in the front hand. Pose: Mid horizontal sweep at waist height: torso twisted, sickle arm stretched straight out to the side, back arm out for balance. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_B_run** · วิ่งพุ่งถือเคียวต่ำ (705 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a farm sickle with a short wooden handle and a curved steel blade, held in the front hand. Pose: Running forward fast, body leaning forward, mid-stride with one foot off the ground, sickle held low and back ready to cut while passing. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_B_throw** · ขว้างเคียวแล้ว (มือว่าง) (653 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: nothing in the hands (the sickle has just been thrown). Pose: Follow-through after a sidearm throw: throwing arm extended forward with an open empty hand, body turned into the throw. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_C_draw** · มือวางที่ด้าม พร้อมชัก (ไออิโด) (716 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small yellow box cutter (utility knife) with a short slim blade, held in the front hand. Pose: Iaido-like ready pose: body leaned slightly forward, front hand resting on the box cutter held at the rear hip, ready to draw and cut in one motion. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_C_slither** · ย่อต่ำก้าวไขว้ขา (680 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small yellow box cutter (utility knife) with a short slim blade, held in the front hand. Pose: Low sneaking crouch with crossed legs mid-step, body close to the ground, cutter held low and close to the body. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**SL_C_guard** · คัตเตอร์ขวางตัวรอสวน (718 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small yellow box cutter (utility knife) with a short slim blade, held in the front hand. Pose: Defensive wait pose for a counter: cutter held horizontally across the chest, back hand near the chest, knees bent, still facing forward in side view. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_A_stance** · ยืนสู้ถือค้อน (658 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a claw hammer with a wooden handle about forearm length, held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_B_stance** · ยืนสู้ถือไม้กวาด (675 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a straw broom about as tall as the character, held with both hands near the middle of the handle. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_C_stance** · ยืนสู้ถือกระทะ (645 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a black cast-iron frying pan, held by its handle in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_A_overhead** · ยกค้อนเหนือหัวสองมือ (667 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a claw hammer with a wooden handle about forearm length, held in the front hand. Pose: Both hands raised high above the head holding the hammer, back slightly arched, ready to smash straight down. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_A_windback** · ง้างค้อนไปหลังเต็มแขน (693 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a claw hammer with a wooden handle about forearm length, held in the front hand. Pose: Full wind-up: hammer swung far back behind the body at shoulder height, torso twisted away from the target, front arm reaching forward. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_A_lowsweep** · ย่อต่ำเหวี่ยงเลียดพื้น (641 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a claw hammer with a wooden handle about forearm length, held in the front hand. Pose: Deep low crouch, hammer swinging horizontally just above the ground at knee height. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_A_reverse** · กลับด้านค้อน สับด้วยด้านเขี้ยว (648 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a claw hammer with a wooden handle about forearm length, held in the front hand. Pose: Hammer flipped so the claw side points down, raised above the shoulder ready to hack down. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_B_sumo** · ยกเข่าสูงแบบซูโม่ (729 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a straw broom about as tall as the character, held with both hands near the middle of the handle. Pose: Sumo shiko stomp: one leg lifted high to the side with the knee bent, standing on the other leg, broom held upright in both hands planted beside the body. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_B_overhead** · ยกไม้กวาดเหนือหัวสองมือ (658 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a straw broom about as tall as the character, held with both hands near the middle of the handle. Pose: Broom raised high above the head with both hands, about to slam down on the ground. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_B_swing** · เหวี่ยงไม้กวาดแนวนอน (676 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a straw broom about as tall as the character, held with both hands near the middle of the handle. Pose: Broom held horizontally with both hands mid swing at waist height, torso twisted, like a staff sweep. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_C_bind** · ใช้กระทะขัดล็อกอาวุธ (692 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a black cast-iron frying pan, held by its handle in the front hand. Pose: Frying pan pushed forward at chest height with the flat side out, as if pressing against and locking an enemy weapon; back hand bracing the handle. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_C_forearm** · กระทะแนบแขน ก้าวลึก (ไม้ศอก) (643 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a black cast-iron frying pan, held by its handle in the front hand. Pose: Deep forward step, frying pan held flat along the forearm like a shield, shoulder driving forward. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**BT_C_guard** · กระทะทแยงหน้าตัวรอสวน (660 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a black cast-iron frying pan, held by its handle in the front hand. Pose: Defensive wait pose for a counter: frying pan held diagonally in front of the body, knees bent, still in side view. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_A_stance** · ยืนสู้ถือไขควง (673 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a screwdriver with a red handle, shaft about hand length, held in the front hand like a dagger. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_B_stance** · ยืนสู้ถือหอกไม้ไผ่ (661 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a bamboo spear about as tall as the character, sharpened tip, held with both hands. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_C_stance** · ยืนสู้ถือส้อม (629 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a large silver dinner fork, held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_A_lunge** · ลันจ์ฟันดาบ แขนเหยียดสุด (726 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a screwdriver with a red handle, shaft about hand length, held in the front hand like a dagger. Pose: Fencing lunge: front knee deeply bent, back leg straight, rear arm extended back for balance, front arm fully extended forward thrusting the screwdriver. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_A_lowstab** · ก้มต่ำแทงข้อพับ (639 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a screwdriver with a red handle, shaft about hand length, held in the front hand like a dagger. Pose: Crouched very low, stabbing forward at knee height, head kept low. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_A_halfgrip** · จับสองมือแทงสั้นแม่น (667 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a screwdriver with a red handle, shaft about hand length, held in the front hand like a dagger. Pose: Both hands grip the screwdriver close to the chest, short precise stab forward, elbows tucked. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_B_spin** · หมุนหอกเหนือหัว (658 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a bamboo spear about as tall as the character, sharpened tip, held with both hands. Pose: Bamboo spear held horizontally above the head with both hands, mid spin, body upright and braced. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_B_reach** · แทงหอกยืดสุด (702 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a bamboo spear about as tall as the character, sharpened tip, held with both hands. Pose: Long spear thrust: both hands at the rear of the shaft, arms fully extended forward, front foot stepped forward, spear level at chest height. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_B_sweep** · จับปลายด้ามกวาดครึ่งวง (666 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a bamboo spear about as tall as the character, sharpened tip, held with both hands. Pose: Holding the very end of the spear shaft with both hands, spear swung wide horizontally to the front side. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_C_feint** · ทำท่าแทงสูง (หลอก) (617 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a large silver dinner fork, held in the front hand. Pose: Feint: fork raised high at head level as if about to stab high, weight on the back foot. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**PT_C_guard** · ชี้ปลายส้อมรอสวน (662 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a large silver dinner fork, held in the front hand. Pose: Fencing guard waiting to counter: front arm extended, fork point aimed at the target, back hand raised behind, knees bent, side view. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_A_stance** · ยืนถือธนูพร้อมยิง (694 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a simple wooden short bow with arrows; the bow is held in the front hand and the string is drawn with the back hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_B_stance** · ยืนถือปืนกระดาษสองมือ (625 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a toy confetti popper gun held with both hands. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_C_stance** · ยืนถือปืนฉีดน้ำ (639 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a green and blue plastic water pistol held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_A_draw** · ง้างธนูเต็มเล็งตรง (734 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a simple wooden short bow with arrows; the bow is held in the front hand and the string is drawn with the back hand. Pose: Kyudo full draw: bow arm extended straight forward, string pulled back to the cheek with the back hand, arrow level, body upright and still. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_A_kneel** · คุกเข่าข้างเดียวยิงต่ำ (659 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a simple wooden short bow with arrows; the bow is held in the front hand and the string is drawn with the back hand. Pose: Kneeling on one knee, bow drawn and aimed low at an enemy's legs. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_A_sky** · เอนหลังยิงขึ้นฟ้า (670 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a simple wooden short bow with arrows; the bow is held in the front hand and the string is drawn with the back hand. Pose: Leaning back, bow drawn and aimed steeply up at the sky at about 60 degrees. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_B_bolas** · หมุนโบลาเหนือหัว (665 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a cord with a small weight tied to each end, swung above the head. Pose: One arm raised above the head swinging a cord with two weights (improvised bolas) in a circle, other arm out for balance. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_B_backjump** · กระโดดถอยหันกลับยิง (628 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a toy confetti popper gun held with both hands. Pose: In mid-air jumping backward, torso twisted to aim the confetti gun back toward the target, legs tucked. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_C_underarm** · เหวี่ยงแขนจากล่างยิงโค้ง (644 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a green and blue plastic water pistol held in the front hand. Pose: Underhand swing: shooting arm swung low to high in front, aiming upward to lob a shot over the front row. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_C_hip** · ยิงเร็วจากเอว (636 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a green and blue plastic water pistol held in the front hand. Pose: Quick draw from the hip: water pistol held at waist height pointed forward, body turned sideways. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**RG_C_lowready** · ถือปืนต่ำรอยิงสวน (659 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a green and blue plastic water pistol held in the front hand. Pose: Ready-to-counter pose: water pistol held low pointing at the ground in front, knees bent, eyes on the target, side view. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_stance** · ยืนถือรีโมต (659 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small handheld remote control box with a short antenna, held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_B_stance** · ยืนถือแบต+คีมคีบ (688 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small car battery with two jumper-cable clamps, battery carried in the back hand, a clamp in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_C_stance** · ยืนถือคีม (624 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a pair of steel pliers held in the front hand. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_point** · ชี้นิ้ว/กดรีโมตสั่งการ (686 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small handheld remote control box with a short antenna, held in the front hand. Pose: Commanding pose: front arm extended toward the target pressing the remote's button with the thumb, other hand pointing forward. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_release** · ชูสองมือปล่อยอุปกรณ์ (666 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small handheld remote control box with a short antenna, held in the front hand. Pose: Both arms raised forward and up as if releasing small devices into the air, remote still in the front hand. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_crank** · ง้างคันโยกหน้าไม้กล (629 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small wooden repeating crossbow with a lever on top. Pose: Holding a small boxy repeating crossbow at the hip with the back hand pulling its top lever back. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_drill** · ดันสว่านเจาะไปหน้า (609 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a handheld electric drill held with both hands. Pose: Leaning forward pushing a handheld electric drill with both hands toward the target. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_A_tripod** · คุกเข่าตั้งขาตั้งเครื่องยิง (636 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small tripod launcher on the ground with a large bolt. Pose: Kneeling beside a small tripod launcher, one hand pulling back its large bolt, the other steadying it. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_B_poles** · แตะสองขั้วไฟฟ้า (712 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small car battery with two jumper-cable clamps, battery carried in the back hand, a clamp in the front hand. Pose: Both arms forward touching the two jumper-cable clamps together in front of the chest, small sparks only between the clamps. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_B_throw** · ปาถุงผง (597 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a small cloth pouch. Pose: Overhand throw follow-through: front arm extended forward, small cloth pouch just leaving the hand. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_B_hose** · ถือหัวสายพ่น กวาดหน้า (622 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a hose nozzle connected by a hose to the battery. Pose: Holding a hose nozzle in both hands pointed forward and sweeping, battery on the ground behind. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_C_place** · คุกเข่าวางของบนพื้น (631 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a pair of steel pliers held in the front hand. Pose: Kneeling on one knee, placing a small device on the ground in front with the pliers, back hand on the knee. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**DV_C_hook** · เหวี่ยงตะขอเชือกเหนือหัว (599 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: a rope with a small metal grappling hook. Pose: Swinging a rope with a metal hook in a circle above the head with the front arm. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_stance** · การ์ดมวยใส่นวม (617 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: Boxing guard: both gloved fists raised in front of the chin, elbows in, knees bent, light on the feet. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_B_stance** · ยืนพร้อมผ้าพันมือ (615 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: white cloth hand wraps on both hands. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_C_stance** · ยืนพร้อมถุงมือหนัง (624 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: brown fingerless leather gloves on both hands. Pose: Battle-ready fighting stance: knees slightly bent, feet apart, body weight forward, ready to attack. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_jab** · แย็บ แขนหน้าเหยียด (606 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: Jab: front arm fully extended straight forward at face height, rear fist guarding the chin. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_lowkick** · เตะตัดขามวยไทย (629 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: Muay Thai low roundhouse kick: hips rotated, rear shin swinging into the opponent's thigh, arms guarding the face. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_elbow** · หมุนตัวศอกกลับ (636 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: Spinning back elbow: body turned with the back partly toward the target, rear elbow swinging horizontally at head height. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_knee** · เข่าโดด ล็อกคอ (622 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: Muay Thai knee strike: one knee driven up high to chest level, both hands reaching forward as if clinching. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_A_bigpunch** · หมัดตรงเต็มแรงพร้อมตะโกน (605 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: red boxing gloves worn on both hands. Pose: All-out straight punch: deep stance, rear arm fully extended forward, mouth open shouting. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_B_throw** · ทุ่มข้ามไหล่ (ยูโด) (673 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: white cloth hand wraps on both hands. Pose: Judo shoulder throw entry: back turned to the target, knees bent low, both hands gripping forward over the shoulder as if pulling an opponent across the back. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_B_capoeira** · ย่อมือแตะพื้นกวาดขา (630 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: white cloth hand wraps on both hands. Pose: Capoeira leg sweep: crouched very low, one hand on the ground, one leg extended straight sweeping along the ground. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_B_spinkick** · เตะหมุนกลางอากาศ (626 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: white cloth hand wraps on both hands. Pose: Taekwondo jumping spin kick: in mid-air, body horizontal-turning, one leg extended straight out at head height. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_B_palm** · ผลักฝ่ามือไทเก๊ก (618 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: white cloth hand wraps on both hands. Pose: Tai chi push: both palms pushed forward at chest height, fingers up, weight shifted onto the front leg. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_C_punch** · หมัดตรงคาราเต้ (631 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: brown fingerless leather gloves on both hands. Pose: Karate straight punch: rear fist fully extended forward at chest height, other fist pulled back to the hip. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_C_slip** · ส่ายหัวหลบ (608 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: brown fingerless leather gloves on both hands. Pose: Boxing slip: upper body bent sideways and down, head moved off-line, fists still up. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```

**FS_C_lock** · จับบิดข้อ / ไอคิโด (645 ตัวอักษร)

```
Same character, same design, same proportions and same colors; only the pose and the held item change. Keep the blue cap with brass goggles, messy brown hair, white short-sleeve shirt, blue necktie, brown belt, brown backpack on the back, blue shorts, white socks and brown boots. In side views stay in a true side view facing the same direction as the source rotation. Held item: brown fingerless leather gloves on both hands. Pose: Joint lock grip: both hands forward at chest height gripping and twisting an invisible wrist, body turning into the lock. No extra weapons, no glow, no motion lines, no shadow, no ground, no background, no text.
```
