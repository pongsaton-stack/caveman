# REBORNER — คู่มือโปรเจกต์สำหรับ Claude Code

JRPG ทำคนเดียวตอนเย็น · Godot 4.7.1 · GDScript · Compatibility renderer · พิกเซล 2D โทนจิบลิ
เจ้าของ: Pongsaton (kwan) — **สื่อสารภาษาไทย** · ชอบเห็นตัวเลขจริง · ต้องการความตรงไปตรงมาเรื่องความไม่แน่นอน

> ไฟล์นี้เก็บเฉพาะกฎ โครงสร้าง วิธีตรวจ และงานค้าง (ย่อเมื่อ 25 ต.ค. 2026 ตามที่ kwan สั่ง)
> **ประวัติงานทั้งหมดถึง 23 ต.ค. 2026** (ทำอะไร วันไหน Version เท่าไหร่ เหตุผล บทเรียน) อยู่ที่ `docs/archive/CLAUDE_HISTORY_2026-10.md`
> ต้องการรายละเอียดเรื่องไหน → `grep -n "คำค้น" docs/archive/CLAUDE_HISTORY_2026-10.md` แล้วอ่านเฉพาะช่วงนั้น · บันทึกงานใหม่ต่อท้ายไฟล์นั้น ไม่ใช่ที่นี่

## กฎการทำงานกับ kwan (ห้ามลืม)
- **ทุกครั้งที่ต้องถาม ให้ถามเป็นข้อๆ แบบมีตัวเลือกให้กด** (ไม่ถามปนในย่อหน้า)
- **เทสต์แล้วเจออะไรไม่ถูกต้อง → แก้ให้ถูกได้เลย ไม่ต้องถาม** แล้วรายงานว่าเจออะไร แก้อย่างไร · ถามเฉพาะเรื่องที่โค้ดแก้ไม่ได้
- **หลักเหล็ก: งานที่พิสูจน์ไม่ได้ยังไม่นับว่าเสร็จ** — แนบหลักฐาน (ผลเทสต์ · Sim ก่อน/หลัง · seed md5 · ภาพ · ลิงก์หน้าเทส) และบอกตรงๆ ว่าอะไรยังไม่ได้ทำ/ไม่ได้ตรวจ
- **ประกาย + ท่าต่อสู้ = ไฮไลต์หลักของเกม** (kwan 21 ต.ค.) → ตรวจละเอียดที่สุด: ซูมทุกเฟรม · ลองทุกมอน (อย่างน้อย B1 M01 M15) · เปิดเสียงเล่นจริง · แก้จนเนียนก่อนส่ง
- **ฉากต่อสู้/ท่าใหม่ทำใน Godot ที่เดียว (kwan 25 ต.ค. เลือก "1")**: ห้องทดลอง `tests/lab/` + หน้าเว็บ lab · **ไม่แก้ฉากต่อสู้บนเว็บอีก** (ฉากที่ย้ายแล้วติดป้าย "เวอร์ชันเก่า" · `GODOT_PORTED` ใน anim_test.tpl.html) · ไม่ต้องถ่ายเทียบกับเว็บสำหรับท่าใหม่
  หน้า animation test ยังใช้ดูภาพ PixelLab ที่เจนใหม่/ท่าเดิน/มอน ก่อนเอาเข้าฉาก Godot
- **ท่า/เอฟเฟกต์/อนิเมชันใหม่ต้องลองได้ในหน้าเทสก่อนเสมอ** (ฉากต่อสู้ = หน้าเว็บ lab Godot) · เข้าเกมเมื่อ kwan อนุมัติเท่านั้น · ของร่างอยู่ในโฟลเดอร์ `*_draft/` (มี `.gdignore`)
- kwan = ผู้ตัดสินคนเดียว · ไม่ใช้ชื่อคน/บริษัทจริงเป็นบทบาท · เกมอื่น (RS3 = Romancing SaGa 3 ฯลฯ) = แรงบันดาลใจ ไม่ใช่เกณฑ์ให้เหมือน
- **Google Drive: อัปโหลดเฉพาะเมื่อ kwan สั่งเป็นครั้งๆ** (ยกเลิกซิงก์อัตโนมัติ 4 ต.ค.) · id โฟลเดอร์และวิธีอัปอยู่ในไฟล์ประวัติ หัวข้อ "สำเนาใน Google Drive"
- **คีย์ลับห้ามอยู่ใน repo/แชท**: PixelLab = env `PIXELLAB_API_KEY` · night-forge = env `NIGHTFORGE_API_KEY` · Claude แก้ `.mcp.json` เองไม่ได้ (kwan แก้บน GitHub)
- ไม่สร้าง PR เว้นแต่ kwan สั่ง · commit ไม่ใส่ชื่อรุ่นโมเดล
- **แบ่งงานเจน (25 ต.ค.)**: Claude สั่ง PixelLab คนเดียว · Muse สั่ง Flow คนเดียว (Muse = ผู้ทำรายงานวิจัยท่า · ไม่ส่งงานเจน PixelLab ให้ Muse)
  ภาพนิ่ง Flow **ฟรี** → ท่าหลักให้ Muse เจนใน Flow ก่อน (ทีละภาพ · แนบ `docs/art-bible/flow_test/rion_ref_x8.png` + ภาพท่าก่อนหน้า · พื้นเทาเรียบ) · แปลงเข้าเกม `tools/sprites/flow_to_px.py` (ตาราง ~11.75 จุด/พิกเซล ตัวสูง 71 · จัดตำแหน่งร่วมทั้งชุด) · PixelLab เก็บไว้ทำสิ่งที่ Flow ทำไม่ได้
  ทดลองสายทุบไม้เบสบอล 25 ต.ค.: ง้าง 1/2 ผ่าน · ฟาด 2/2 ผ่าน หน้าตา/ตำแหน่งคงที่ข้ามเฟรม (ต่างจากรอบชีตหลายช่อง 15–18 ต.ค. ที่ของในมือหาย)

## รสนิยมที่ kwan ล็อกไว้ (ใช้เป็นฐานงานต่อไปทุกครั้ง)
- **จังหวะโจมตี (10 ต.ค.)**: เคลื่อนเข้าหาเป้าแล้ว**ตีทันทีตอนถึงตัว ไม่หยุดตั้งท่า** · ง้างระหว่างเคลื่อน (กลางอากาศ) · กระทบ = แตะพื้น · หลังกระทบไถลตามแรงส่ง · ห้ามยืนง้างนิ่งหลังถึงตัว เว้นแต่ kwan สั่ง/ท่านั้นตั้งใจค้าง (เช่น จิเง็นริว)
- **เพลงต่อสู้ (5 ต.ค.)**: แนวรอบ 4 ใน `BGM` (anim_test.tpl.html · ฟัง `docs/art-bible/audio/battle_bgm_preview.mp3`) — SNES JRPG + ร็อกหนักแนว Linkin Park/Nirvana · 168 BPM D minor · ริฟนูเมทัล Drop D · กระเดื่องคู่ · โซโล่ · เบรกดาวน์ · เพลงหลบตอนกระแทก · **แต่งใหม่เสมอ ห้ามยืมทำนอง/ริฟจริง**
- **ไม่ใช้เสียงพูด/พากย์** (5 ต.ค.) · เสียงสกิลต้องหนัก ไม่ "มุ้งมิ้ง" (ไม่มีกริ๊ง/ระฆัง) · ชื่อท่าใช้บับเบิล (`rs3Bubble`)
- **VFX ใหญ่ทำด้วยโค้ด** ไม่เจนใน PixelLab (18 ต.ค.) · PixelLab ใช้ทำตัวละคร/ท่าเท่านั้น
- **ท่าต้องต่างจากฟันปกติชัดเจน**: ตัดเอ็นแบบกาลีถูกตีตก ("ดูไม่แตกต่างกับฟันปกติ") → ทุกท่าใหม่ต้องมีภาพจำเฉพาะ

## ตัวเอก Rion · MASTER (kwan 18 ต.ค. "นี่คือ master ของ rion")
- ภาพหลัก `docs/art-bible/rion_hires/rion_master_v2.png` (**ไม่มีนาฬิกา**) + prompt ต้นฉบับ `docs/art-bible/rion_hires/RION_MASTER.md` (บล็อก CHARACTER + STYLE ใช้ตามตัวอักษร)
- หมวกน้ำเงิน (ปุ่มบน) + แว่นทองเหลืองเลนส์น้ำเงิน · ผมน้ำตาลชี้ · เสื้อขาวแขนสั้นคอปก เนคไทน้ำเงิน · เข็มขัดน้ำตาลหัวทอง · เป้น้ำตาล · ขาสั้นน้ำเงินพับขา · ถุงเท้าขาว · บูทน้ำตาล
- **ทิศ**: ท่าในศึกหันซ้ายทุกท่า (ยกเว้นท่าหันหลัง) · ท่าเดินแผนที่ทิศไหนก็ได้ อีกทิศพลิกด้วยโค้ด
- **ถืออาวุธมือเดียว = มือขวา** (หันซ้ายแล้วเป็นแขนฝั่งไกล) · ซูม ≥ 4 เท่าตรวจทุกเฟรมว่าของอยู่มือเดิม มือว่างไม่บังหน้า ไม่มีชิ้นเกิน (kwan ตำหนิ 19 ต.ค.)
  วิธีดู: หันซ้ายมุมข้าง แขนใกล้ (ซ้าย) ต้องเห็นเสมอ · เห็นแขนเดียวพาดหน้าอก = มือซ้ายถือ = ผิด
- ชุดที่ใช้ในฉากต่อสู้ตอนนี้ = PixelLab `px_set` (`assets/sprites/pixellab_draft/px_set/` ผืน 120x112 เท้าแถว 108) · ยังไม่เข้าเกม
- แนวภาพตัวละครที่ kwan ชอบ (14 ต.ค.): chibi หัวโต เส้นขอบเข้มหนา สีเรียบลงเงาการ์ตูน · เอฟเฟกต์วาดเองใช้เส้นขอบ `#2a1a14`

## PixelLab (Tier 1 · 2,000 gen/เดือน · ยอดล่าสุด **1,736** ณ 26 ต.ค.)
- สคริปต์ `tools/sprites/pixellab_walk.py` (API v2 · พิมพ์ยอดก่อน/หลังทุกคำสั่งที่เสียเครดิต) · ท่าในต้นไม้ = `tools/sprites/pixellab_skills.py` (BEATS · HELD/HELD_NOT · HOLD_STILL · IN_PLACE)
- **คำสั่งต้องละเอียดที่สุด** (kwan 18 ต.ค.): ทิศล็อก · ของในมือ (ขนาด/มือไหน/ทุกเฟรม) · จังหวะทีละเฟรม · โมเมนตัม · ส่วนที่คงที่ · สิ่งที่ห้าม · CHARACTER + STYLE
  ใช้ `ONE_HAND` / `KNIFE` เท่านั้น ห้ามคำว่า "front hand" · ดูคำสั่งเต็มก่อนจ่าย: `python3 tools/sprites/pixellab_walk.py prompt <ท่า>` · เจน: `PL_STATE=fight_knife ... anim <ท่า> west`
- ขั้นต่อ: `fetch` → **ตรวจที่อยู่ไฟล์**: ZIP มักแตกไป `zip/fight_knife/animations/` แทน `states/fight_knife/fight_knife/animations/` → คัดลอกไป states แล้ว
  `git clean -fdq assets/sprites/pixellab_draft/zip/fight_knife/animations` + `git checkout assets/sprites/pixellab_draft/zip/metadata.json` (**ห้าม rm -r** มีไฟล์ track อยู่)
  → เพิ่มแถวใน `tools/sprites/pixellab_rion_set.py` CLIPS → รัน (~3 นาที) → px_set
- ทุกท่าที่เจน: เพิ่มแถวใน `docs/art-bible/pixellab_test/catalog.json` + `docs/art-bible/rion_hires/PIXELLAB_PROMPTS.md` แล้วสร้างหน้ามาสเตอร์ใหม่
- บทเรียน: เชื่อได้กับท่าสั้น 8 เฟรม/ท่าค้าง · ท่าเหวี่ยงแรง/หมุน/ทุ่ม มักวาดเส้นฟาดทั้งที่ห้าม + หันเข้ากล้อง + มีดหาย → ใช้เฟรมที่ผ่าน แล้วประกอบด้วยโค้ด
  `clean()` ใน pixellab_rion_set.py ลบเส้นฟาด/ประกาย · `weapon_swap.py` ลบ/วางอาวุธ · `blade_tip.py` วัดปลายมีดอัตโนมัติ · คู่มือ `docs/art-bible/rion_hires/PIXELLAB_TECHNIQUES.md`

## ลิงก์หน้าเว็บ (Artifact ส่วนตัว · เผยแพร่ทับลิงก์เดิมเสมอ)
| หน้า | ลิงก์ | สร้าง |
|---|---|---|
| เกมบนเว็บ | https://claude.ai/artifact/G2xSXyKupn1WSNnu96uHan | `tools/export_web.sh <out>` (ดู "เล่นผ่านเว็บ") |
| animation test | https://claude.ai/artifact/MoNVTd5ckQLmb4tsfqsikw (V155) | `python3 tools/web/anim_test_build.py <out.html>` + files `anim_test_sprites_0.json` |
| ฉากต่อสู้ | https://claude.ai/artifact/6XRNGR6WCWih5zwD9yB7uV (V14) | `anim_test_build.py --combat <out.html>` + files `combat_sprites_0.json` |
| มาสเตอร์ PixelLab | https://claude.ai/artifact/DD4suCKoCB1guFvkM3MW5y (V17) | `python3 tools/web/pixellab_test_build.py <out.html>` · ใส่**เฉพาะภาพที่ PixelLab เจน** |
| สมุดรวม | https://claude.ai/artifact/SfXaREU5hLSHJvgFqWS1h4 | `python3 tools/web/codex_build.py <out.html>` |
| UI Kit | https://claude.ai/artifact/EoUPzxnzW3hswZKMYsaqkz | `GODOT=<godot> python3 tools/web/ui_mock_build.py <out.html>` |
| ต้นไม้ท่า 6 สาย | https://claude.ai/artifact/MEug5zmpASHwnp26RqBi35 | `python3 tools/web/skill17_page_build.py <out.html>` |
- หน้า animation test กับฉากต่อสู้ใช้**เทมเพลตเดียวกัน** `tools/web/anim_test.tpl.html` → แก้ฉากต่อสู้แล้วสร้างทั้งสองหน้า · เปิดทดสอบในเครื่องต้องผ่าน http server (utf-8) ไม่ใช่ file://
- ไฟล์เดี่ยวใน Artifact ≤ 16 MB → สไปรต์แยกเป็นก้อน JSON ส่งผ่าน `files` ทุกก้อน · ใช้เกิน 85% ให้แยกหน้า V2

## ฉากต่อสู้ในหน้าเทส (ยังเป็น JavaScript บนเว็บ · ยังไม่อยู่ใน Godot)
- เครื่องฉากใน `anim_test.tpl.html`: `blc*` (bl0 · bl1 · ประกาย) · `aot*` ตัดเอ็น bl7 · `kw*` ผ่าเกราะ bl8 · `wr*` เขี้ยวพัน bl2 · `jg*` จันทร์เสี้ยว bl9 · `ma*` มอนโจมตีกลับ M01 · `bgAmbient` ฉากขยับ
  เพิ่มฉากใหม่ = ฟังก์ชัน geo/view/sound + `addClip(..., { <ธง>: true })` + บรรทัดส่งต่อใน `clipView` และใน tick (เสียง)
- ตัวเลขดาเมจใช้สูตรเกม (`csHit` · ATK × พลัง/100 × MIT_K/(MIT_K+DEF) × ธาตุ × ร่างกาย · ignore_def) · HP จาก monsters.csv · Rion ในฉาก prof 20 + มีดครัว 14
- **กับดักที่เกิดซ้ำ 3 ครั้งแล้ว: คอมเมนต์ `//` ท้ายบรรทัดกลืนโค้ดที่ตามมาในบรรทัดเดียวกัน** → ทุกครั้งที่แก้ด้วยสคริปต์: ดึง `<script>` ใหญ่สุดออกมาแล้ว `node --check`
- เครื่องมือตรวจใน scratchpad (`at/`): `kw.cjs <เฟรม> <มอน> <ชื่อ>` ภาพ 2 เท่า · `snd.cjs <คลิป>` เปิดเสียงเล่นวน · `swap.cjs` จอ 400px · `err2.cjs` error ตอนโหลด · `dmg.cjs` ปุ่มตัวเลข (หายเมื่อเครื่องใหม่ → เขียนใหม่ได้จาก playwright)
- ⚠ **ข้อสังเกต 24 ต.ค. (ยังไม่ตัดสิน)**: ฉากเหล่านี้ต้องเขียนใหม่เป็น GDScript ตอนเข้าเกม · ทางเลือกที่เสนอ = ทำฉากใน Godot (AnimationPlayer/Tween/Particles) แล้ว export เว็บให้ดู
- **ฉากต่อสู้ใน Godot (kwan 25 ต.ค. เลือกไปทาง Godot · ท่าใหม่ทำที่นี่)**: `tests/lab/` (ไม่ถูก export กับเกม) · ย้ายครบทุกฉากแล้ว 11 ฉาก + ท่าใหม่ทุบ bt0: bl0 `blc_bl0` · bl1 `blc_bl1` · bl2 `wr_bl2` · bl7 `aot_bl7` · bl8 `kw_bl8` · bl9 `jg_bl9` · ประกาย `glim_bl1/bl3/bl5` (เครื่อง blc · mv()) · มอนตีกลับ `ma_hit` `ma_guard` (เลือกมอนได้ 5 ตัว · ดาเมจคิดจาก ATK ใน monsters.csv)
  `lab_stage.gd` = ฐานใช้ร่วม: ฉากหลัง 3 ฉาก + ของขยับ · เพลง (mp3 อัดจากเว็บ วนซ้ำ หลบตอนกระแทก) · Rion/มอน · บับเบิล/ตัวเลข/คำเสียง/ร่างติดตา (เป็นพูลต่อเฟรม) · อนุภาค · หยุดภาพ · เสียงสังเคราะห์สูตรเดียวกับเว็บ · เมนูเลือกท่า/มอน/ฉาก
  ท่าใหม่ = `extends "res://tests/lab/lab_stage.gd"` + `.tscn` · เขียน tech_id/end_frame/stops/setup/frame/sounds/draw_back/draw_mid/draw_fx · พิกเซลแบบ fbPx = `px()` `star_px()` `slash_line()` `disc()` · ห้าม class_name
  ตารางวิจัยรอบ 2 ของ Muse (25 ต.ค.) = `tests/lab/r2_tables.gd` (สร้างจาก R2SYS ห้ามแก้มือ): `feel(พลัง)` หยุดภาพ/จอสั่น/กระเด็นตามระดับท่า (ใช้กับท่าใหม่ · ฉากเดิมยังใช้ค่าที่ kwan อนุมัติ) · `react(สาย)` ปฏิกิริยาร่าง 9×6 · `debris_at()` เศษตามวัสดุ · ร้าวเฉพาะร่างแข็ง (`HARD_BODIES`)
  เทียบ PixelLab `pl_bt0` (kwan 25 ต.ค. "Flow ทื่อมาก ลองเจน pixellab มาเทียบ"): State `BT_bat_stance` + ท่า `bt0_bat` → `px_set/pls_bat_*` (18 gen · ยอด **1,764**) · ฉากเดียวกันแทนแค่ภาพ (`keys()/tips()/shift_x()`) · ปุ่มความเร็ว ×0.25–×2 ในเมนู (`lab_speed` · `--speed=`)
  **ทุบ bt0 ใช้ PixelLab (kwan 25 ต.ค. "ชอบมากกว่า สีหน้ามีอารมณ์มากกว่า flow")** `pl_bt0` ตามรายงาน: ง้าง ~10 เฟรมกลางอากาศ → ฟาด 4 เฟรม → โดน 22 → ไม้จมค้างถึง 29 → กระโดดถอย 2 ครั้ง + ไถลแบบท่าฟัน (HOPS) · ภาพ pls_bat_0 / pls_bat2_* / pls_bat_imp (State) / pls_bat_hop · บทเรียน: ท่ากระทบทำเป็น State แล้วเจนท่ากลาง (PL_START_IMG + PL_END_IMG)
  bt0 (26 ต.ค. kwan "วิ่งไปโจมตีแบบฟัน เสร็จแล้วทำท่ายืนหายใจ และเพิ่มปุ่มให้เลือกอาวุธ"): วิ่งเข้า `pls_bat_run` แบบ blc_bl0 (RUN 18) · ยืนหายใจ `pls_bat_breath` 0–1 วน · ปุ่มอาวุธ Lv.1–10 ของสายท่า (weapons.csv ชุด 60 ชิ้น · meta `lab_weapon_<bl/bt>` · `--weapon=`) · ไม้เบสบอล CR-1/4/6/9/10 เปลี่ยนสกินด้วยโค้ด `tools/sprites/bat_tiers.py` (TIERS ต้องตรง BAT_SKINS ใน lab_stage) → `pixellab_draft/weapon_skin/` (รันใหม่หลัง pixellab_rion_set) · ชิ้นที่ยังไม่มีภาพใช้ภาพชิ้นตั้งต้น + แถบล่างบอก · ดาเมจเปลี่ยนเฉพาะอาวุธที่มี weapon_base
  อาวุธชุด 60 ชิ้น (kwan เลือก 26 ต.ค.): เอกสาร Muse + ภาพท่าถือ 35 ภาพ `docs/design/weapons60/` (grips/grip_<id>.webp · GRIP_REVIEW.md = ตำหนิ + ไอคอนที่ผิดชิ้น) → `weapons_full.json` (level · grip A/B/C · grip_pose · grip_ref · tier = ceil(level/2) ข้อเสนอ) → econ_csv.py → weapons_csv.py · weapontest คาด 60 ชิ้น
  ท่าทุบ bt0 `flw_bt0` (25 ต.ค. kwan "1 ถ้าออกมาไม่ดี กลับไปใช้ pixellab"): ภาพ Rion จาก Flow 7 ท่า `assets/sprites/flow_draft/bt/flw_bt_*` (ready lift wind mid hit follow back · `tx()` อ่าน prefix `flw_` จาก FPX) · ใช้ feel(100) + react("ทุบ") + ล้มสลายเมื่อดาเมจ ≥ HP · DMG ไม้อลูมิเนียม CR-2
  แก้แสงวาบตามตรวจรอบ 2 (kwan 25 ต.ค. "3"): bl8 ตัดวาบตัวมอนตอนตอก + จอวาบ 0.22→0.15 + ร่างไม่แข็งเป็นรอยแผลแทนร้าว · ประกายจอวาบ 0.6→0.3
  สัญลักษณ์บนจอต้องอยู่ใน subset ฟอนต์ (✦ ขึ้นกล่องบนเว็บ → ใช้ ★) · GDScript: `var x := round(...)`/max/min = พังตอน parse → ใช้ roundf/maxf/minf หรือระบุชนิด · ลำดับชั้น: back_fx (หลังมอน) → มอน z1 → mid_fx z2 → Rion z4 → front_fx z5
  ตรวจเร็ว (ไม่กี่วิ): `xvfb-run -a <godot> --path . --rendering-driver opengl3 --fixed-fps 60 res://tests/lab/<ท่า>.tscn -- --foe=M01 [--bg=ash_village] --snap=30,36 --snapdir=<dir>` → เทียบกับเว็บ `websnap.cjs` (scratchpad)
  อัดวิดีโอ (600x336 + f.wav): ตัด `--snap` ใส่ `--write-movie <dir>/f.png` · หน้าเว็บ: `GODOT=<godot> tests/lab/build_web.sh <out>` → https://claude.ai/artifact/5JNZaykSQiY9ghpD1V7BPp (V8) · ดาเมจ = ตาราง DMG ใน lab_stage.gd (ค่าจาก csHit ของเว็บ)

## แหล่งความจริง
- `docs/GDD.md` — ดีไซน์ทั้งหมด ตัวเลขที่จูนแล้ว (หมวด 10) · **บทเรียนหมวด 11 อ่านก่อนแก้อะไรก็ตาม**
- `docs/PENDING_DECISIONS.md` — เรื่องที่ kwan ยังไม่ตัดสิน · ตัดสินข้อไหนแล้วอัปเดตไฟล์นั้น
- `docs/STORY_DRAFT.md` — ร่างเรื่อง (ขัดกับ GDD เมื่อไหร่ให้เชื่อ GDD)
- `data/*.csv` + `data/map_ashfield.txt` — ข้อมูลเกมทั้งหมด · `docs/design/skill_trees_17.csv` = ร่างต้นไม้ 17 ท่า × 6 สาย (ยังไม่แตะ techs.csv ยกเว้นสายคม)

## โครงสร้าง
```
core/    ตรรกะต่อสู้ล้วน ไม่มี node · ทดสอบ headless ได้
  Battle.gd ★ ลูปเทิร์นเดียวของทั้งโปรเจกต์ (begin → is_over → next_turn → auto_act/player_act)
  Formulas.gd ค่าคงที่และสูตร · Insight.gd แหล่งสะสมประกาย · Economy.gd ราคา/เงิน
  Actor Ai CsvDb Status Tech TechDb · Sim.gd (ติด node) · BattleTest.gd (ติด node)
world/   Overworld.gd (ติด node) · MapData PlayerState SaveGame WorldEnemy
         BattleScreen.gd · MenuScreen · ShopScreen · RecruitScreen · DemoEndScreen · UiKit
data/    monsters techs encounters chests party_slots companions items recruits weapons
         monster_body body_affinity sig_effects seize_techs economy inflation shops materials tomes dialogue (.csv)
scenes/  sim.tscn · battle_test.tscn · overworld.tscn (main)
tests/   check/ (ผ่าน/ไม่ผ่าน) · measure/ (วัดค่า) · shots/ (ถ่ายภาพ) · unit/ (gdUnit4) · seed.md5
tools/   run_tests.sh · get_godot.sh · export_web.sh · sprites/ (ภาพ/PixelLab) · web/ (หน้าเว็บ) · data/ (สร้าง CSV) · blender/
assets/sprites/  ของเกม + *_draft/ (ร่าง · .gdignore) · addons/ dialogic (ยังไม่ใช้ในเกม) · gdUnit4
docs/    GDD · art-bible/ · design/ · archive/ (ประวัติ) · .gdignore (Godot ไม่นำเข้า)
```
- skill ที่ราก repo `.claude/skills/`: `reborner-verify` (ขั้นตอนตรวจ) · `aseprite` · `ffmpeg-skill` · ใน `reborner/.claude/skills/` = BMAD 29 ตัว (ตัวช่วยวางแผน · กฎในไฟล์นี้มาก่อน)

## กฎที่ห้ามละเมิด
1. **ลูปเทิร์นมีที่เดียว คือ `Battle`** — Sim, BattleTest, Overworld, หน้าจอต่อสู้ ต้องเรียก Battle ห้ามเขียนลูปซ้ำ (GDD 11.15)
2. **`class_name`**: คลาสที่ new() มีได้ · สคริปต์ที่ติด node ในฉาก (Sim, BattleTest, Overworld) **ห้ามมี** · ซ้ำกัน = ทะเบียนคลาสพังทั้งโปรเจกต์ (11.24)
3. **ห้าม hardcode ค่าเกม** — ตัวเลขอยู่ใน CSV หรือ Formulas/Insight/Economy เท่านั้น · ค่าที่ Claude เสนอใส่ `[เสนอ]` ใน note จนกว่า kwan ยืนยัน
4. **typed array** ห้าม assign ด้วย literal — ใช้ `.clear()` แล้ว `.append()`
5. **เยื้องด้วย tab เท่านั้น** · หารจำนวนเต็มเขียน `int(x / 10.0)`
6. CSV ต้องมีไฟล์ `.import` แบบ `importer="keep"` ไม่งั้น Godot แปลงเป็น translation · weapons.csv สร้างจาก `tools/data/weapons_csv.py` ห้ามแก้ตรง
7. **แก้ core/ หรือ data/ แล้วต้องรัน Sim เทียบก่อน/หลังเสมอ** — ห้ามเชื่อเลขบนกระดาษ (11.2, 11.20, 11.22)
8. ให้เครื่องมือใหม่กับผู้เล่น → ชดเชยที่ศัตรู ไม่ใช่ที่เครื่องมือ (11.16, 11.27)

## ขนาดงาน → ขั้นตอน
| ขนาด | ตัวอย่าง | ขั้นตอน |
|---|---|---|
| เล็ก | แก้บั๊ก · ปรับค่า · แก้ข้อความ | สร้าง → ตรวจด้วยหลักฐาน → รายงาน |
| กลาง | ระบบใหม่ · อาร์ต/ท่าใหม่ · หน้าจอใหม่ | เสนอเป็นข้อให้ kwan เลือก → สร้าง → ตรวจ → หน้าเทส → kwan อนุมัติก่อนเข้าเกม |
| ใหญ่ | ภูมิภาคใหม่ · เปลี่ยนรายชื่อมอน · เปลี่ยนสูตร | ค้นคว้า → แผนให้เลือก → สร้าง → ตรวจรอบแยกโดยตัวช่วยอิสระ 1 ตัว → kwan เล่นจริง |

## วิธีตรวจ
- เครื่องใหม่: `tools/get_godot.sh [dir] [--web]` (Godot 4.7.1 + template เว็บ) · ffmpeg: `sudo apt-get install -y ffmpeg`
- **เทสต์ทั้งชุด**: `GODOT=<godot> tools/run_tests.sh [--sim] [--shots]` → ผ่าน = exit 0 · ไม่มี SCRIPT ERROR · ไม่มี `FAIL` · seed md5 ตรง `tests/seed.md5` (ล่าสุด 7d2078bf…)
  เซฟเทสต์แยกไฟล์ด้วย env `REBORNER_SAVE` · ไฟล์ class ใหม่ต้อง `<godot> --headless --path . --import` ก่อน ไม่งั้น "X not declared"
- Sim: `<godot> --headless --path . res://scenes/sim.tscn` · บรรทัดแรก `เวอร์ชัน:` ตรง `VERSION` · Sim ไม่ล็อก seed: รันเดิมซ้ำต่างได้ ~21–33 บรรทัด = ระดับสุ่ม
- ภาพจากเกมจริง: `xvfb-run -a <godot> --path . --rendering-driver opengl3 -s <script>` · สคริปต์ใน `tests/shots/`
- รายการตรวจตามด้าน: ระบบต่อสู้ = Sim ก่อน/หลัง + seed + เทสต์ · อาร์ต = ขนาดช่อง (มอน M 48 · L 96) หันถูกทิศ (ศัตรูหันขวา) พื้นโปร่งสะอาด ·
  ท่าขยับ = หน้าเทสก่อน · UI ไทย = กล่อง ≤ 2 บรรทัด ไม่ล้นที่ 384x216 สัญลักษณ์อยู่ใน subset ฟอนต์ · เนื้อเรื่อง = ตรง GDD/STORY_DRAFT บทพูดใน `data/dialogue.csv` · เว็บ = `fileSizes.index.pck` ตรง
- รายละเอียดทีละขั้น: skill `reborner-verify`

## เป้าสมดุล (AI จำลอง = ขอบล่าง ผู้เล่นจริงง่ายกว่า — 11.19)
| สถานการณ์ | ชนะ | Insight เต็ม/ศึก | อื่นๆ |
|---|---|---|---|
| หนอนหิน M03 | 100% | 0.00 | ขัดจังหวะ 0 |
| หมาป่าคู่ M15 x2 prof 20-25 | 70-85% | ~0.1-0.27 | คอมโบ ~1.3 |
| โกลเลม M29 prof 25 / 30 | ~71% / ~81% | ~0.45 | ขัด ~1 · ~450-600 AV |
| บอส B1 + อาวุธ 28 prof 16/20/22 | ~55/84/91% | ~2.0→0.7 | มีดครัว (14) ต่ำโดยตั้งใจ (ประตูอาวุธ · GDD 11.29) · หลังระบบร่างกาย มีดเหลือ 3/6/15% (ยอมรับแล้ว) |

## สถานะเกม (สรุป · รายละเอียดในไฟล์ประวัติ)
- ✅ ระบบต่อสู้ครบ: ต้นไม้ท่า (คม 17 ท่า · สายอื่น 7) · ประกาย (+สวนกลับ · อ่านทางหลบ · Insight ค้างข้ามศึก) · สถานะ · ตั้งรับ · คอมโบ · ขัดจังหวะ · คมสวน · ความเข้ากับร่างกาย
- ✅ แผนที่ · ศัตรูบนแมพ · ลอบตี · จุดพัก · เซฟ/โหลด · หีบ · บอส · จอสู้กดเอง · ปาร์ตี้มอน/LP · รับมอน/ยึดท่า · ร้าน+เศรษฐกิจ+เงินเฟ้อ · ฉากจบเดโม · ห้องทดลองท่า
- ⬜ ยังไม่มี: หนี (GDD 3.7) · ใช้ไอเท็มในศึก · สมุดบันทึก · บทพูดฉากเปิด (ฉาก 0–6) · ระบบเควส · สายเวทย์ (ร่างในหน้าเทสเท่านั้น)
- ตบทิ้งบนแมพปิดชั่วคราว (`Formulas.MAP_SWAT := false`) ตามที่สั่ง

## งานค้าง / รอ kwan
- 📌 เจน PixelLab ท่าฟันย้อนขึ้นมือขวา (~2–4 gen) ให้ฟันครั้งที่ 2/3 ของเขี้ยวพัน `wr_bl2` มีภาพจริง (kwan 23 ต.ค. "จดไว้ก่อน")
- ฉากต่อสู้ที่รอ kwan ดู/ตัดสิน: bl0 bl1 ประกาย ตัดเอ็น (AoT) ผ่าเกราะ (ผ่าหมวก) เขี้ยวพัน จันทร์เสี้ยว มอนตีกลับ M01 · ทั้งหมดเป็นร่าง ยังไม่เข้าเกม
  ข้อเสนอค้างล่าสุด: ซีกที่ขาดของจันทร์เสี้ยวให้หมุนคว่ำ · ย้ายฉากต่อสู้เข้า Godot (ลองท่า bl0 ก่อน)
- ตัวเลขท่าคม bl7–bl16 ใน techs.csv เป็น `[เสนอ]` รอยืนยัน · ต้นไม้ 17 ท่าอีก 5 สายเป็นร่าง ยังไม่รัน Sim
- รายการ State ท่าตัว 77 แบบ (`docs/design/STATE_POSES_17.md`) รอตรวจก่อนเจน · แผนคลังชิ้นส่วน `docs/art-bible/pixellab_test/ASSET_LIBRARY_PLAN.md` รอตัดสิน 2 ข้อท้าย · ยังไม่ได้อ่านข้อตกลงการใช้งาน PixelLab
- ชุด Rion PixelLab ในเกม: ทุบ bt0 สลับมือ · แทง pt0 มือหายช่วงง้าง → ยังไม่แก้ รอ kwan
- ขัดกันที่ยังไม่ตัดสิน: GDD 9.2 vs 12.4 (ราคายา LP) · ชีตสกิล 173 ท่า vs techs.csv · ชีตอาวุธ 210 vs 183 ชิ้น · ภาพแนวไม้ตายของ kwan vs ข้อมูล · ท่าเดิม rg5 dv5 dv6 fs3 พลัง 0
- Dialogic: segfault ตอนปิดเกมถ้าเคยแสดงบรรทัดที่มีชื่อผู้พูด · ยังไม่ใช้ในเกม · pck ใหญ่ขึ้น 1.9 MB

## ช่องโหว่ที่รู้แล้ว
- ท่ายึดมีแค่ M03/M06 · เกราะแข็ง (+40% DEF) คุ้มน้อย AI แทบไม่ใช้ · M03/M06 รับเข้าทีมไม่ได้ตามกฎ 5.3
- ยาสมุนไพร (I01) 40%/20g เป็นค่าชั่วคราว · HP มอนเต็มทุกศึก · EC เพิ่มเมื่อชนะบอส (ไม่มีเควส)
- ธาตุไฟ/น้ำแข็ง/แสง/มืด ยังไม่มีท่าไหนใช้ — อย่าจูนมอนที่อ่อนแอต่อธาตุเหล่านี้ · ศึกภูมิภาค 1 สั้นกว่าเป้า 5–8 รอบ
- `HERO_ANIMS` ใน Overworld.gd อาจจับคู่ทิศผิด · AI แทบไม่ใช้คมสวน/ตั้งรับ (สวนกลับแทบไม่เกิดใน Sim)

## เล่นผ่านเว็บ
- จอฐาน 384x216 ขยาย canvas_items · ฟอนต์ `assets/fonts/game_font.tres` = Sarabun + fallback สัญลักษณ์ (ตัดเฉพาะอักษรที่ใช้) → สัญลักษณ์ใหม่ต้องเพิ่มเข้า subset
- `tools/export_web.sh <out>` = export + gzip wasm (`index.wasm.gz.wasm`) + `index.pck.wasm` + fileSizes · หน้าเว็บ `tools/web/reborner.html` ดัก fetch แปลงชื่อกลับ + ปุ่มสัมผัส
- ต้องมี export template `web_nothreads_release.zip` ของ 4.7.1 · โฮสต์รับไฟล์ละ ≤ 15 MB

## เครื่องมือเสริม (รายละเอียดในไฟล์ประวัติ)
- Blender MCP: `tools/blender/start_blender_mcp.sh` ต้องรันก่อนทุกเครื่องใหม่ · `.mcp.json` ที่ราก repo
- night-forge VFX Lab MCP: endpoint ในไฟล์ประวัติ · คีย์ env เท่านั้น
- Chromium ในเครื่องคลาวด์ใบรับรองว่าง → `certutil` นำเข้า `/root/.ccr/ca-bundle.crt` (หัวข้อ ActionForge ในไฟล์ประวัติ) · Playwright: `NODE_PATH=/opt/node-tools/node_modules`
- คลิปไฮไลต์ 20 วิ: `tools/web/highlight_video.cjs` + ffmpeg (loudnorm −14 · alimiter)
- submodule อ้างอิงใน `third_party/` (aseprite · godot-open-rpg · RPG-JS ฯลฯ) ไม่รวมเข้าเกม · Aseprite เป็น EULA ห้ามคัดลอกซอร์ส
