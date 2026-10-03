# Prompt สำหรับให้อีกค่ายเจนงาน (3 ต.ค. 2026)

บทเรียนจากแพ็ก grok รอบแรก: ท่าโจมตีมอน 214 ไฟล์ใช้ไม่ได้ เพราะย่อจากภาพใหญ่ มีพื้นกระดาษ ป้ายชื่อ และช่องเหลื่อม
ส่วน Rion/หมาเปลี่ยนดีไซน์ไปจากที่อนุมัติ ทุก prompt ด้านล่างจึงขึ้นต้นด้วย **กฎกลาง** (วางทุกครั้ง)

## ไฟล์อ้างอิงที่ต้องแนบไปด้วย (อยู่ใน repo)
- Rion: `assets/sprites/rion_lastlight_draft/west.png` + `docs/art-bible/previews/walk_sheet.png`
- หมา: `assets/sprites/dog_lastlight_draft/east.png` + `docs/art-bible/previews/dog_walk_sheet.png`
- มอน: `assets/sprites/monsters_ll/{M01,M03,M06,M15,B1}.png`
- ฉาก/สไตล์: `docs/art-bible/lastlight_01.png` · ภาพจอสู้ `docs/art-bible/previews/battle_boss.png`

## กฎกลาง (วางหัวทุก prompt)
```
STRICT OUTPUT RULES — follow exactly:
1. True native pixel art. 1 art pixel = 1 image pixel. No anti-aliasing, no blur, no painterly or noisy texture, no upscaling.
2. Background: flat solid magenta #FF00FF. NO parchment, NO paper texture, NO decorative frame, NO labels, NO text, NO title, NO watermark.
3. Fixed grid: every asset sits alone inside its own cell of the stated size. Nothing may cross a cell border. No gap lines between cells.
4. Outline: 1px dark, hue-shifted toward the object's own shadow color. NEVER a white or light halo/rim/glow around the sprite.
5. Light comes from the top-left. Shading in 2–3 flat steps per material.
6. Style: modern 16-bit JRPG, cute, warm, Studio-Ghibli mood, post-apocalyptic world being reclaimed by nature.
7. Palette — use only these hex colors (plus #FF00FF background):
   653A21 9A6038 B37A55 D6966A D4B08A 2F1B10 4D2A17 714022 92552D 342013 523624 6F4B33 825335 A2927B
   412C1E 6C5947 8A7460 A7B5A0 D2BD9A 050708 13545C 146E77 306E76 3C5253 000000 150F0D 21160F 383A37 3E2214
   Blue 395472 4C6880 507895 7A8993 = Rion only. Orange B25F3C DA7B42 E39253 E1B684 = dog only. Teal = allies/UI only.
8. Export one PNG per sheet, exactly the pixel size stated. Do not resize after drawing.
```

## 1) ไทล์แผนที่ 24x24 (สำคัญสุด — แมพตอนนี้ยังเป็นช่องสีเรียบ)
```
[STRICT OUTPUT RULES]
Top-down 3/4 RPG overworld tileset. Cell size 24x24 px. Sheet 8 columns x 6 rows = 192x144 px.
Row 1: grass A, grass B, grass C (small variations), tall grass, flowers, dirt A, dirt B, ash ground (grey-brown, cracked).
Row 2: road straight horizontal, straight vertical, cross, T-north, T-south, T-east, T-west, road end.
Row 3: road corners (NE, NW, SE, SW), stone floor A, stone floor B, mossy stone, rubble.
Row 4: water center, water edges against grass (N, S, E, W), water outer corners (NE, NW).
Row 5: water outer corners (SE, SW), water inner corners (NE, NW, SE, SW), lily pads on water, shallow water.
Row 6: ruin wall top, ruin wall front face, ruin wall corner, ruin wall broken, cliff edge top, cliff face, void/dark ground, bridge planks.
Every tile must tile seamlessly with its neighbours of the same type.
```

## 2) ของบนแผนที่ (ต้นไม้ หิน หีบ จุดพัก ของดรอป)
```
[STRICT OUTPUT RULES]
Top-down 3/4 overworld objects, same style as the attached reference sheet. Sheet 8 columns x 2 rows of 24x48 px cells = 192x96 px.
Each object stands at the BOTTOM-CENTER of its cell (its base touches the cell's bottom edge).
Row 1: pine tree, round bush with berries, mossy boulder, wooden fence horizontal, wooden fence vertical, street lamp (lit), wooden crate, barrel.
Row 2: treasure chest closed, treasure chest open, campfire rest point frame 1, campfire frame 2, small cloth gift-sack drop, signpost, broken car wreck (fits 24x48), stump.
```

## 3) อาคาร
```
[STRICT OUTPUT RULES]
Top-down 3/4 buildings for the overworld, base on a 24px tile grid. Sheet 4 columns x 2 rows of 72x72 px cells = 288x144 px.
Each building's footprint is 3x2 tiles (72x48) at the bottom of its cell; roof may use the upper space.
Row 1: patchwork-awning shop stall (counter with jars and herbs), small house with lit window, repair workshop with wrench sign, clinic with red cross.
Row 2: canvas tent, wooden water tower, rusty generator with sparks, collapsed ruined house.
```

## 4) ท่าต่อสู้ของมอน 5 ตัวที่อยู่ในเกม (แนบรูปอ้างอิงทุกตัว — ห้ามออกแบบใหม่)
```
[STRICT OUTPUT RULES]
Battle animation frames for the 5 attached monster sprites. Keep each design EXACTLY as the reference (same shapes, colors, size). Side view, facing RIGHT (toward the party).
Sheet: 7 columns per row. Columns = idle 1, idle 2, attack wind-up, attack strike, attack recover, hit (recoil + flinch), down (defeated, lying flat).
Row 1 — M01 Ash Slime, 48x48 cells: idle = slow wobble squash-stretch; attack = squash low, then body-slam forward with a stretch, then wobble back; down = melted puddle.
Row 2 — M03 Stone Grub, 48x48 cells: idle = head bobs; attack = curls into its stone shell, rolls forward, uncurls; down = shell cracked, head out flat.
Row 3 — M06 Shade Bat, 48x48 cells: idle = two wing-flap positions; attack = wings up, dive forward with small fangs, pull back; down = wings folded on the ground.
Row 4 — M15 Pair Wolf (two pups together), 48x48 cells: idle = small synchronized hop; attack = back pup crouches, front pup lunges and bites, both reset; down = both pups lying curled.
Row 5 — B1 Ashgrub Sovereign boss, 96x96 cells (row is 672x96): idle = segments ripple in a wave; attack = rears up, crown spikes up, lunges with the twin fangs; hit = armor plates crack; down = collapsed, eyes dim.
Rows 1–4 sheet width 336 px. Deliver rows 1–4 as one 336x192 PNG and row 5 as a separate 672x96 PNG.
```

## 5) หมาคู่หูเข้าศึก (แนบรูปหมา — สีส้ม ไม่มีผ้าพันคอ)
```
[STRICT OUTPUT RULES]
Battle frames for the attached companion dog. Keep the exact design: small orange shiba-like dog, cream muzzle and belly, NO scarf, NO collar.
Side view facing LEFT. Cell 48x48 px, dog about 34 px tall, standing at the bottom-center of each cell.
One row, 8 cells = 384x48 px: idle 1, idle 2 (tail wag), run, attack wind-up (crouch), attack bite lunge, attack recover, hit (yelp recoil), down (lying, eyes closed).
```

## 6) UI kit + ไอคอนของ
```
[STRICT OUTPUT RULES]
JRPG UI kit, warm wood-and-brass frame style matching the attached references, but drawn as clean native pixel art.
Sheet 192x96 px on #FF00FF:
- Window frame for 9-slice: 24x24 px, corners exactly 8x8, edges repeat cleanly, dark fill using palette 150F0D or 21160F.
- Buttons 48x16: normal, focused (thin gold edge), pressed.
- Bar frames 64x6: HP (green fill 6C5947→olive), SP (teal), Insight (gold).
- Icons 16x16 each, one per cell, in a row: herbal medicine bottle, revive tonic, ash slime goo, raw stone chunk, thin bat wing, wolf fang, white skill tome, gold coin, gift sack, understanding diamond ◇, recruit heart.
- Six weapon-school chips 16x16: SL slash (blade), PC pierce (needle), CR crush (hammer), BD body (fist), ST shoot (slingshot), DV device (gear).
```

## 7) ภาพหน้าตัวละครในกล่องบทพูด
```
[STRICT OUTPUT RULES]
Dialogue portraits, bust shot facing slightly right, 64x64 px cells, one row = 448x64 px.
Rion (attached reference: blue cap with goggles, brown hair, beige shirt, blue denim, leather backpack; NOT a brown cap):
neutral, happy, surprised, determined, sad.
Dog (attached reference: orange, no scarf): happy, alert.
```

## 8) เสียง (ถ้าเจนเสียงได้)
```
Game audio for a cozy post-apocalyptic Ghibli-mood JRPG. Seamless loops, no vocals in music.
- bgm_field: 60–90 s loop, acoustic guitar + soft strings + light percussion, hopeful and gentle, ~90 BPM.
- bgm_battle: 60 s loop, same instrumentation but driving, light tension, ~140 BPM.
- bgm_boss: 60 s loop, heavier low strings and drums, ominous but not horror.
- Short SFX (WAV, 0.2–1.0 s, mono): slime squish, stone roll, bat wing flap, wolf bite, boss roar, knife slash, hit thud,
  guard clang, chest open, item pickup, footstep on grass, understanding chime (soft bell), recruit success jingle, menu move tick.
```
