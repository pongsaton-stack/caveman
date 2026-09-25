# REBORNER — คู่มือโปรเจกต์สำหรับ Claude Code

JRPG ทำคนเดียวตอนเย็น · Godot 4.7.1 · GDScript · Compatibility renderer · พิกเซล 2D โทนจิบลิ
เจ้าของ: Pongsaton — **สื่อสารภาษาไทย** · ชอบเห็นตัวเลขจริง · ต้องการความตรงไปตรงมาเรื่องความไม่แน่นอน

## แหล่งความจริง
- `docs/GDD.md` — ดีไซน์ทั้งหมด ตัวเลขที่จูนแล้ว (หมวด 10) และ **บทเรียน 29 ข้อ (หมวด 11) อ่านก่อนแก้อะไรก็ตาม**
- `docs/STORY_DRAFT.md` — ร่างเรื่อง: ตัวตน Riona · ฉากเปิดเรื่อง · ผู้ที่นับเหตุการณ์ (**ร่าง** ขัดกับ GDD เมื่อไหร่ให้เชื่อ GDD)
- `data/*.csv` + `data/map_ashfield.txt` — ข้อมูลเกมทั้งหมด (`monsters_workbook.xlsx` เป็นเอกสารออกแบบ ค่าอาจเก่ากว่า CSV)

## โครงสร้าง
```
core/   ตรรกะต่อสู้ล้วน ไม่มี node · ทดสอบ headless ได้
  Battle.gd   ★ ลูปเทิร์นเดียวของทั้งโปรเจกต์
  Formulas.gd ค่าคงที่และสูตรทั้งหมด · Insight.gd แหล่งสะสมประกาย
  Actor Ai CsvDb Status Tech TechDb
  Sim.gd (ติด node) รัน 200 ศึก/สถานการณ์ แล้วพิมพ์ตาราง
  BattleTest.gd (ติด node) ศึกเดียวแบบเห็นทุกบรรทัด
world/  ฉากแผนที่
  Overworld.gd (ติด node) · MapData PlayerState SaveGame WorldEnemy
data/   monsters.csv techs.csv encounters.csv chests.csv map_ashfield.txt
assets/sprites/hero/  เฟรมตัวเอก 48x48 30 ไฟล์
```

## กฎที่ห้ามละเมิด
1. **ลูปเทิร์นมีที่เดียว คือ `Battle`** — Sim, BattleTest, Overworld และหน้าจอต่อสู้ในอนาคตต้องเรียก Battle ห้ามเขียนลูปซ้ำ (GDD 11.15)
2. **`class_name`**: คลาสที่ new() ในโค้ดมีได้ · สคริปต์ที่ติด node ในฉาก (Sim, BattleTest, Overworld) **ห้ามมี** · ซ้ำกันเมื่อไหร่ทะเบียนคลาสพังทั้งโปรเจกต์ (11.24)
3. **ห้าม hardcode ค่าเกม** — ตัวเลขอยู่ใน CSV หรือ Formulas/Insight เท่านั้น
4. **typed array** (`Array[String]` ฯลฯ) ห้าม assign ด้วย literal — ใช้ `.clear()` แล้ว `.append()`
5. **เยื้องด้วย tab เท่านั้น** · หารจำนวนเต็มให้เขียน `int(x / 10.0)` กันคำเตือน
6. CSV ต้องมีไฟล์ `.import` แบบ `importer="keep"` ไม่งั้น Godot แปลงเป็น translation
7. **แก้ core/ หรือ data/ แล้วต้องรัน Sim เทียบก่อนสรุปเสมอ** — ห้ามเชื่อเลขที่คำนวณบนกระดาษ (11.2, 11.20, 11.22)
8. ให้เครื่องมือใหม่กับผู้เล่น → ชดเชยที่ศัตรู ไม่ใช่ที่เครื่องมือ (11.16, 11.27)

## วิธีตรวจ — รัน Godot เองได้
ใช้ตัว **console** ของ Godot (บน Windows คือไฟล์ `..._console.exe` ไม่งั้นไม่มี output):
```
<godot_console> --headless --path . res://scenes/sim.tscn
```
ฉากอยู่ใน `scenes/`: `sim.tscn` · `battle_test.tscn` · `overworld.tscn` (main scene) · โปรเจกต์นี้อยู่ใน `reborner/` ของ repo caveman
Sim ปิดตัวเองเมื่อรัน headless · บรรทัดแรกต้องขึ้น `เวอร์ชัน:` ตรงกับ `VERSION` ใน Sim.gd
ถ้าเจอ "Could not find type X" ท่วม → รัน `<godot_console> --headless --path . --import` ก่อน แล้วตรวจ class_name ซ้ำ

## เป้าสมดุล (ตัวเลขจาก AI จำลอง = ขอบล่าง ผู้เล่นจริงง่ายกว่า — 11.19)
| สถานการณ์ | ชนะ | Insight เต็ม/ศึก | อื่นๆ |
|---|---|---|---|
| หนอนหิน M03 | 100% | 0.00 | ขัดจังหวะ 0 |
| หมาป่าคู่ M15 x2 prof 20-25 | 70-85% | ~0.1-0.27 | คอมโบ ~1.3 |
| โกลเลม M29 prof 25 / 30 | ~71% / ~81% | ~0.45 | ขัด ~1 · ~450-600 AV |
| บอส B1 + อาวุธ 28 prof 16/20/22 | ~55/84/91% | ~2.0→0.7 | มีดทำครัว (14) ~5-10 / ~20 / ~30-40% = ตั้งใจ (ประตูอาวุธ · GDD 11.29) |
ยืนยันใน Godot 4.7.1 จริงแล้ว 25 ก.ย. 2026 รวมบอส B1 (`boss_sweep()` ใน Sim) — ดู `docs/SIM_REPORT_2026-09-25.md`

## สถานะ
- ✅ ขั้น 1-3: ดีไซน์ · เอนจิน+ข้อมูล · พอร์ตระบบต่อสู้ครบ (ต้นไม้ท่า ประกาย สถานะ ตั้งรับ Insight คอมโบ เปิดท่า ขัดจังหวะ)
- ✅ ขั้น 4 สัปดาห์ 1: แผนที่ ศัตรูบนแมพ ลอบตี ตบทิ้ง จุดพัก เซฟ/โหลด หีบ บอส — **ศึกบนแมพยังให้ AI เล่นแทน**
- ⬜ ขั้น 4 สัปดาห์ 2: **หน้าจอต่อสู้ที่ผู้เล่นกดเอง**
- ⬜ สัปดาห์ 3: เมนู ร้านค้า ความเชื่อใจ/LP มอน ช่องปาร์ตี้ตาม EC · สัปดาห์ 4: สมุดบันทึก → vertical slice

## งานถัดไปตามลำดับ
1. ✅ รัน Sim headless → เทียบตารางเป้า (`docs/SIM_REPORT_2026-09-25.md`) · ✅ เพิ่มบอส B1 เข้า Sim แล้ว · ✅ ยอมรับเป้ามีดทำครัวใหม่ (GDD 11.29)
2. ให้ Pongsaton กด F5 เล่นแผนที่เอง (ความรู้สึกต้องมาจากมือคน ไม่ใช่ตัวเลข)
3. สัปดาห์ 2 — **ข้อจำกัดสถาปัตยกรรมสำคัญ**: `Battle.run()` ตอนนี้เป็นลูปปิดที่ให้ Ai ตัดสินใจแทนตัวเอก
   ต้องแตกเป็น API ทีละขั้น (เช่น `begin()` / `advance_to_next_actor()` / `player_act(action)`)
   แล้วให้ `run()` = ลูปของขั้นเหล่านั้น + Ai — **หน้าจอต่อสู้กับ Sim ต้องใช้โค้ดขั้นตอนเดียวกัน**
   แถบคิวใช้ `Battle.preview(8)` · ตรวจว่า Sim ให้ตัวเลขเท่าเดิมหลัง refactor ทุกครั้ง

## ช่องโหว่ที่รู้แล้ว
- ช่องปาร์ตี้ตาม EC ยังไม่ทำ — Sim/แผนที่ใช้มอนร่วมทีม 2 ตัวตายตัว (หนอนหิน M03 + ค้างคาว M06 · ความเชื่อใจ 3 · HP x1.6)
- LP/permadeath ของมอนร่วมทีมยังไม่ต่อเนื่องข้ามศึก
- ธาตุไฟ/น้ำแข็ง/แสง/มืด ยังไม่มีท่าไหนใช้ (สายเวทย์ยังไม่พอร์ต) — อย่าจูนมอนที่อ่อนแอต่อธาตุเหล่านี้
- `HERO_ANIMS` ใน Overworld.gd อาจจับคู่ทิศผิด

## เล่นผ่านเว็บ
- ลิงก์: https://claude.ai/artifact/G2xSXyKupn1WSNnu96uHan (Artifact ส่วนตัว · แชร์ผ่านเมนู Share ของหน้า)
- จอฐาน 384x216 ขยาย canvas_items · ฟอนต์ `assets/fonts/game_font.tres` = Sarabun (ไทย+ละติน) + fallback สัญลักษณ์ ★◆▼✂✋⚠ → 🎁 (ตัดเฉพาะอักษรที่ใช้ · OFL)
  ใช้ข้อความสัญลักษณ์ใหม่ในเกม → ต้องเพิ่มอักษรนั้นเข้า subset ไม่งั้นเป็นกล่องบนเว็บ
- สร้างใหม่: ต้องมี export template `web_nothreads_release.zip` ของ 4.7.1 ใน `~/.local/share/godot/export_templates/4.7.1.stable/`
  `<godot> --headless --path . --export-release "Web" <out>/index.html` → `gzip -9 index.wasm` แล้วตั้งชื่อ `index.wasm.gz.wasm` · `index.pck` → `index.pck.wasm`
  (ที่โฮสต์รับแค่ชนิดไฟล์มาตรฐานและไฟล์ละ ≤15MB) · หน้าเว็บคือ `tools/web/reborner.html` ซึ่งดัก fetch แปลงชื่อกลับ + ปุ่มลูกศรบนจอสัมผัส
  เผยแพร่ทับลิงก์เดิมด้วย Artifact `url` ข้างบน

## สำเนาใน Google Drive — ซิงก์ทุกครั้งที่ไฟล์เปลี่ยน
Pongsaton อนุญาตแล้ว: ไฟล์ไหนในโปรเจกต์ถูกแก้ ให้อัปโหลดทับใน Drive ได้เลยไม่ต้องถาม
- โฟลเดอร์ `The Reborner` id `1d3YPhEXP4x86I_VTVzksScbSog-GZDFJ` · โครงเดียวกับ repo
  core `1ivuWP8GZGVi7FPg75dxQl2Adsr0A8pgk` · world `1y7M-SLPV2_urDsoFhyNRei7zoSEd_BWH` · data `1mq4yyiJJMGjAINJJKJSL1Ruotxe6BsVF`
  docs `1atuceU4o6LrYQ8n_kKrVf0VsGKJQBy36` · scenes `1s1sLb00yvq3WhwVY5yQwXrrTEAqOBOYj` · assets/sprites_hero `18ftQRAhD4I9U8DClNAvSavJ03KR1KYdr`
- เครื่องมือ Drive แก้เนื้อหาไฟล์เดิมไม่ได้ → "ทับ" = สร้างไฟล์ใหม่ชื่อเดิมในโฟลเดอร์เดิม แล้ว trash ไฟล์เก่า
- ต้องตั้ง `disableConversionToGoogleType: true` เสมอ (ไม่งั้นกลายเป็น Google Docs) · เทียบ `fileSize` กับ `wc -c` ทุกไฟล์
- ไม่อัปโหลด `.uid` / `.import` ของ PNG / `.godot/` (Godot สร้างใหม่เอง)
