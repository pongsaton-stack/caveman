# Prompt สำหรับให้อีกค่ายเจนงาน (3 ต.ค. 2026)

บทเรียนจากแพ็ก grok รอบแรก: ท่าโจมตีมอน 214 ไฟล์ใช้ไม่ได้ เพราะย่อจากภาพใหญ่ มีพื้นกระดาษ ป้ายชื่อ และช่องเหลื่อม
ส่วน Rion/หมาเปลี่ยนดีไซน์ไปจากที่อนุมัติ ทุก prompt ด้านล่างจึงขึ้นต้นด้วย **กฎกลาง** (วางทุกครั้ง)

## ไฟล์อ้างอิงที่ต้องแนบไปด้วย (อยู่ใน repo)
- Rion: `assets/sprites/rion_lastlight_draft/west.png` + `docs/art-bible/previews/walk_sheet.png`
- หมา: `assets/sprites/dog_lastlight_draft/east.png` + `docs/art-bible/previews/dog_walk_sheet.png`
- มอน: `assets/sprites/monsters_ll/{M01,M03,M06,M15,B1}.png`
- ฉาก/สไตล์: `docs/art-bible/lastlight_01.png` · ภาพจอสู้ `docs/art-bible/previews/battle_boss.png`

## กฎกลาง (วางหัวทุก prompt) — ฉบับแก้ 3 ต.ค. หลังรอบ 2
รอบ 2 ได้รูปทรงเรขาคณิตล้วน (placeholder) เพราะ (1) กฎเดิมบังคับ "พิกเซล 1:1 ขนาดเป๊ะ" ตัวเจนภาพทำไม่ได้ เลยหันไปเขียนโค้ดวาดกล่อง (2) ไม่ได้แนบรูปอ้างอิง
ฉบับนี้: **ให้วาดภาพใหญ่สวยเต็มที่** แล้วฝั่งเรา (Claude) ตัด/ย่อ/ลดสีเอง — แบบเดียวกับที่ทำจากชีต Last Light ได้ผลแล้ว
ขนาดในแต่ละ prompt ด้านล่าง = ขนาดปลายทางในเกม (ใช้บอกสัดส่วน) ไม่ต้องส่งมาขนาดนั้น

```
OUTPUT RULES — follow exactly:
1. Draw real illustrated pixel-art sprites (modern 16-bit JRPG look). Do NOT draw placeholder shapes, boxes or code-generated geometry.
   Large canvas is fine and preferred (e.g. 1024–2048 px). Chunky visible pixels, crisp edges, no blur.
2. Background: flat solid magenta #FF00FF everywhere outside the sprites. NO parchment, NO paper texture, NO decorative frame,
   NO labels, NO text, NO title, NO watermark, NO ground shadow blobs that touch other sprites.
3. Layout: a clear grid in the order listed. Leave a wide empty gap (at least 1/4 cell) between every sprite. Nothing touches or overlaps.
   All sprites in one sheet share ONE scale (same pixel size), and the same baseline per row.
4. Outline: dark, hue-shifted toward each object's shadow color. NEVER a white or light halo/rim/glow around a sprite.
5. Light from the top-left. 2–3 flat shading steps per material.
6. Mood: cute, warm, Studio-Ghibli, post-apocalyptic world being reclaimed by nature. Earthy muted colors
   (reference palette: 653A21 9A6038 B37A55 D4B08A 4D2A17 714022 523624 6F4B33 A2927B 6C5947 8A7460 A7B5A0 D2BD9A 146E77 383A37 21160F).
7. If reference images are attached, copy those designs EXACTLY (shape, colors, outfit). Never redesign an attached character.
8. One PNG per sheet. Keep each file under 10 MB.
```

**ต้องแนบรูปอ้างอิงในแชตเดียวกับ prompt ทุกครั้ง** (prompt 4, 5, 7 ห้ามส่งถ้าไม่มีรูปแนบ)

## 1) ไทล์แผนที่ 24x24 (สำคัญสุด — แมพตอนนี้ยังเป็นช่องสีเรียบ)
```
[OUTPUT RULES]
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
[OUTPUT RULES]
Top-down 3/4 overworld objects, same style as the attached reference sheet. Sheet 8 columns x 2 rows of 24x48 px cells = 192x96 px.
Each object stands at the BOTTOM-CENTER of its cell (its base touches the cell's bottom edge).
Row 1: pine tree, round bush with berries, mossy boulder, wooden fence horizontal, wooden fence vertical, street lamp (lit), wooden crate, barrel.
Row 2: treasure chest closed, treasure chest open, campfire rest point frame 1, campfire frame 2, small cloth gift-sack drop, signpost, broken car wreck (fits 24x48), stump.
```

## 3) อาคาร
```
[OUTPUT RULES]
Top-down 3/4 buildings for the overworld, base on a 24px tile grid. Sheet 4 columns x 2 rows of 72x72 px cells = 288x144 px.
Each building's footprint is 3x2 tiles (72x48) at the bottom of its cell; roof may use the upper space.
Row 1: patchwork-awning shop stall (counter with jars and herbs), small house with lit window, repair workshop with wrench sign, clinic with red cross.
Row 2: canvas tent, wooden water tower, rusty generator with sparks, collapsed ruined house.
```

## 4) ท่าต่อสู้ของมอน 5 ตัวที่อยู่ในเกม (แนบรูปอ้างอิงทุกตัว — ห้ามออกแบบใหม่)
```
[OUTPUT RULES]
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
[OUTPUT RULES]
Battle frames for the attached companion dog. Keep the exact design: small orange shiba-like dog, cream muzzle and belly, NO scarf, NO collar.
Side view facing LEFT. Cell 48x48 px, dog about 34 px tall, standing at the bottom-center of each cell.
One row, 8 cells = 384x48 px: idle 1, idle 2 (tail wag), run, attack wind-up (crouch), attack bite lunge, attack recover, hit (yelp recoil), down (lying, eyes closed).
```

## 6) UI kit + ไอคอนของ
```
[OUTPUT RULES]
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
[OUTPUT RULES]
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

## 9) เพลงต่อสู้แนว SNES JRPG (kwan ส่งคลิป Romancing SaGa 3 "Battle I" เป็นแนว · 4 ต.ค. 2026)
ห้ามขอให้ "เหมือนเพลงนั้น" หรือใส่ชื่อเกม/ชื่อผู้แต่งใน prompt — บอกแค่ลักษณะดนตรี (กันได้ทำนองซ้ำของเดิม)
```
Original battle music for a 16-bit era JRPG (Super Famicom / SNES sound chip style). Instrumental only, no vocals.
- Tempo ~150–165 BPM, 4/4, driving and heroic with a slightly dark, adventurous edge.
- Instruments as sampled by a 1990s console: punchy slap/synth bass playing fast arpeggiated ostinato,
  brass stabs and a bright brass lead melody, orchestral string runs, timpani + snare + crash, a short harpsichord or
  organ counter-line in the B section.
- Structure: 4-bar intro hit → A section (main melody, 16 bars) → B section (modulates up a step, 16 bars) →
  bridge with bass-only breakdown (8 bars) → back to A. Must loop seamlessly from the end to the start of A.
- Mix: mono-ish, warm, slightly lo-fi (32 kHz sampler feel), light reverb, no modern sub-bass or EDM sound design.
- Length 90–120 s per loop. Deliver WAV + OGG. Also deliver a 3-second victory fanfare and a 2-second "glimmer" sting
  (rising bell arpeggio, bright, like a sudden idea).
```

## 10) มอนจาก Monster Compendium ทีละตัว (4 ต.ค. 2026 · ต้นฉบับคมกว่าตัดจากชีตรวม)
แนบ `docs/art-bible/compendium/monster_compendium.jpg` ทุกครั้ง · ส่งครั้งละ 1 ตัว (ดีสุด) หรือ 4 ตัวในภาพเดียวก็ได้
```
[OUTPUT RULES]
Redraw ONE monster from the attached "Monster Compendium" sheet: <NAME> (row "<REGION>").
Copy its design exactly (shape, colors, proportions). Do not add or remove parts.
- Pixel art, modern 16-bit JRPG look, chunky crisp pixels on a clear pixel grid, NO blur, NO soft painting, NO gradients smoothing.
- Pixel scale: design it on a 64x64 pixel grid (the monster about 44-56 grid pixels wide/tall), then enlarge EVERY pixel to an exact 16x16 block (nearest neighbor) so the file is 1024x1024. Same block size everywhere, no half blocks.
- Side view, facing RIGHT. Full body visible, nothing cropped.
- Background: flat solid magenta #FF00FF only. No ground, no shadow, no text, no name label, no frame, no effects around it.
- Only ONE creature (if the sheet shows several variants, draw the biggest/main one).
- Export PNG (not JPG).
Second image (optional): a 4-frame row, 4096x1024 (four 1024x1024 cells), SAME 16x16 block size and SAME character size as image 1
— copy image 1 exactly and change only the pose: idle 1 (= image 1), idle 2 (body 1 grid pixel lower/squashed), attack (lunge/strike), hit (recoil).
```
ตัวอย่างแรก (สไลม์ 4 ต.ค. · `compendium/samples/`): ไฟล์ถูกรูปแบบทุกข้อ แต่พิกเซลละ ~18px → ภาพจริงแค่ 32x23 จุด · เฟรมท่าขยับคนละสเกล (บล็อก ~10px · ตัวแบนเหลือ 11 จุด) · ตัวมีขา ไม่เหมือนสไลม์ในชีต
→ แก้ prompt ข้างบน: บังคับตาราง 64x64 ขยายบล็อกละ 16 และเฟรมต้องสเกลเดียวกับภาพแรก · ฝั่งเรา `native()` (เก็บสีกลางบล็อก) ได้พิกเซลอาร์ตคมเป๊ะ ไม่ต้องย่อ
ตั้งชื่อไฟล์ตอนอัป: `<region>_<ชื่ออังกฤษ>.png` เช่น `forest_wolf.png` · อัปที่ลิงก์ใน CLAUDE.md หัวข้อ "ลิงก์ที่ปักไว้"
