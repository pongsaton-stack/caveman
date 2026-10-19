# tools/web/anim_test_build.py — สร้างหน้า "animation test" จากข้อมูลเกมปัจจุบัน
# อ่านสไปรต์จาก assets/ + techs.csv + monsters.csv + ค่าคงที่จาก Formulas.gd / BattleScreen.gd / Overworld.gd
# ข้อมูลฝังในไฟล์ HTML · ภาพแยกเป็นก้อน JSON ข้างหน้าเว็บ (อัปโหลดเป็นไฟล์ประกอบของ Artifact) · รัน: python3 tools/web/anim_test_build.py <out.html>
import glob, base64, csv, json, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPR = os.path.join(ROOT, 'assets/sprites')

CHUNK_BYTES = 12_000_000     # ต่อก้อนภาพ (Artifact รับไฟล์ละ ≤ 16 MB)
FILE_LIMIT = 15_500_000      # ทุกไฟล์ (หน้าเว็บ + แต่ละก้อน)
TOTAL_LIMIT = 100_000_000    # รวมทั้งชุด (kwan กำหนด 100 MB · Artifact รับได้ถึง 256 MB ต่อเวอร์ชัน)
V2_AT = 0.85                 # ใช้เกิน 85% ของ TOTAL_LIMIT → หยุด ให้งานใหม่แยกไปหน้า "animation test V2" (kwan 6 ต.ค.: "แยกเป็นเทส V2 หากใกล้เต็มลิมิต")

def webp(path, q=80):
	"""ภาพที่ไม่ใช่พิกเซลอาร์ต (เอฟเฟกต์เรืองแสง · ช่องจากชีต jpg) → webp เล็กกว่า png หลายเท่า หน้าไม่เกิน 16 MB"""
	import io
	from PIL import Image
	b = io.BytesIO(); Image.open(path).save(b, 'WEBP', quality=q, method=6)
	return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def astra_vfx():
	"""ชีต VFX จาก Astra (index ของ astra_vfx_cut.py) + เสียง wav ฝังเป็น data URI · เวลาเสียงดังสุด (วิ) ใช้วางเสียงให้ตรงจังหวะกระทบ"""
	p = os.path.join(SPR, 'astra_vfx_draft/index.json')
	if not os.path.isfile(p):
		return {}
	import wave
	import numpy as np
	sheets = json.load(open(p, encoding='utf-8'))['sheets']
	for name, sh in sheets.items():
		wp = os.path.join(ROOT, 'docs/art-bible/vfx/astra', sh['sound'])
		if os.path.isfile(wp):
			w = wave.open(wp); a = np.abs(np.frombuffer(w.readframes(w.getnframes()), np.int16)); sr = w.getframerate()
			sh['peak'] = round(int(np.argmax([a[i:i + 441].max() for i in range(0, len(a), 441)])) * 441 / sr, 2)
			sh['wav'] = 'data:audio/wav;base64,' + base64.b64encode(open(wp, 'rb').read()).decode()
	return sheets


def rion_pack_clips():
	"""คลิปชุดครบ (rion_pack_px) · คลิป PixelLab แทรกต่อท้ายกลุ่มเดินหลัก ให้อยู่ติดชีต B"""
	def clips(p):
		return json.load(open(p, encoding='utf-8'))['clips'] if os.path.isfile(p) else []
	rp = clips(os.path.join(SPR, 'rion_pack_px/index.json'))
	pl = clips(os.path.join(SPR, 'pixellab_draft/px/index.json'))
	n = max((i + 1 for i, c in enumerate(rp) if pl and c['group'] == pl[0]['group']), default=len(rp))
	# PixelLab ฟันมีดรอบ 2 พลิกหันขวา (ภาพสร้างใน sprites()) → ตัว Rion ในแท็บสกิล ชุดใหม่ แบบ PixelLab · ไม่ลงแท็บท่าขยับ (hidden)
	extra = [{'group': '', 'id': 'pl_slash2', 'label': 'PixelLab ฟันมีดรอบ 2 (พลิกหันขวา)', 'frames': ['pl_slash2_%d' % i for i in range(8)], 'ms': 110, 'loop': False, 'w': 104, 'travel': 0, 'hidden': True}] if pl else []
	extra += [{'group': '', 'id': cid, 'label': 'PixelLab จาก State (พลิกหันขวา)', 'frames': ['%s_%d' % (cid, i) for i in range(len(fs))], 'ms': 90, 'loop': False, 'w': 120, 'travel': 0, 'hidden': True}
		for cid, fs in PL_STATE_CLIPS.items() if all(os.path.isfile(f) for f in fs)]
	# ชุด Rion ในเกมแบบ PixelLab (tools/sprites/pixellab_rion_set.py · kwan 19 ต.ค. "เปลี่ยนเป็น PixelLab ทั้งชุด" · ร่าง ยังไม่เข้าเกม) · หันซ้ายตามภาพดิบ
	ps = clips(os.path.join(SPR, 'pixellab_draft/px_set/index.json'))
	return ps + rp[:n] + pl + rp[n:] + extra


# ท่ายากจาก State (kwan 19 ต.ค. "ลองท่ายากก่อน 2 ท่า" → ไม่ผ่านทั้งคู่ → "1" ประกอบด้วยโค้ดจากช่วงที่ผ่าน) · ใช้เฉพาะเฟรมที่ไม่หันเข้ากล้อง
# ทุ่ม fs10_s: 0–5 ยื่นมือจับ · 6 หันหน้า (ใช้แค่ตอนหมุนตัว 1 เฟรม) · 7–9 หันขวาย่อ (= หันหลังให้มอน) · เตะ fs12_s: 0–7 ยืน ย่อ กระโดด หันหลัง + ภาพนิ่ง State เตะ 4 มุม (ซ้าย หลัง ขวา หน้า)
_ST = os.path.join(SPR, 'pixellab_draft/states')
PL_STATE_CLIPS = {
	'pl_fs10': [os.path.join(_ST, 'FS_B_throw/FS_B_throw/animations/fs10_s_v/west/frame_%03d.png' % i) for i in range(10)],
	'pl_fs12': [os.path.join(_ST, 'FS_B_spinkick/FS_B_spinkick/animations/fs12_s_v/west/frame_%03d.png' % i) for i in range(8)]
		+ [os.path.join(_ST, 'FS_B_spinkick/FS_B_spinkick/rotations/%s.png' % d) for d in ('west', 'north', 'east', 'south')]}   # 8–11 = ท่าเตะ 4 มุม (หมุนตัวด้วยการสลับมุมจริง ไม่บีบภาพ)


def pl_state_frames():
	"""ผืน 120x112 เท้าแถว 108 (แบบ rion_pack_px) · เท้าแต่ละเฟรมลงพื้น (การลอยใส่ด้วยคีย์เฟรมในหน้า) · แนวนอนใช้ขอบซ้ายรวมของคลิป
	ภาพนิ่ง State (ผืนต่างขนาด) วางกลางกรอบให้ตรงกลางกรอบเฟรมแรก · พลิกหันขวาแบบชุดครบ (หน้าเทสพลิกกลับหันซ้าย)"""
	import io
	from PIL import Image, ImageOps
	out = {}
	for cid, files in PL_STATE_CLIPS.items():
		if not all(os.path.isfile(f) for f in files):
			continue
		ims = [Image.open(f).convert('RGBA') for f in files]
		bb = [im.getchannel('A').getbbox() for im in ims]
		same = [b for im, b in zip(ims, bb) if im.size == ims[0].size]
		x0 = min(b[0] for b in same)
		cx0 = (bb[0][0] + bb[0][2]) / 2 - x0
		for i, (im, b) in enumerate(zip(ims, bb)):
			c = Image.new('RGBA', (120, 112))
			ox = 30 - x0 if im.size == ims[0].size else round(30 + cx0 - (b[0] + b[2]) / 2)
			c.alpha_composite(im, (ox, 108 - b[3]))
			buf = io.BytesIO(); ImageOps.mirror(c).save(buf, 'PNG')
			out['rpk/%s_%d' % (cid, i)] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
	return out


def png(path):
	with open(path, 'rb') as f:
		return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

def const(file, name):
	"""อ่านค่าคงที่ตัวเลขจากไฟล์ .gd — หน้าเว็บไม่มีเลขที่พิมพ์เอง"""
	src = open(os.path.join(ROOT, file), encoding='utf-8').read()
	m = re.search(r'const %s\s*:?=\s*([0-9.]+)' % name, src)
	if not m:
		raise SystemExit('ไม่เจอ %s ใน %s' % (name, file))
	return float(m.group(1))

def sprites():
	out = {}
	for folder, key in (('rion_lastlight_draft', 'rion'), ('dog_lastlight_draft', 'dog'), ('monsters_ll', 'mon')):
		d = os.path.join(SPR, folder)
		for f in sorted(os.listdir(d)):
			if f.endswith('.png'):
				out['%s/%s' % (key, f[:-4])] = png(os.path.join(d, f))
	# Rion พิกเซล 32-bit ที่เกมใช้ (tools/sprites/rion_px_game.py · kwan 16 ต.ค. 2026)
	xd = os.path.join(SPR, 'rion_px')
	for f in sorted(os.listdir(xd)):
		if f.endswith('.png'):
			out['px/' + f[:-4]] = png(os.path.join(xd, f))
	# Rion พิกเซลถืออาวุธ 6 สาย (tools/sprites/rion_px_weapons.py · ชีต Flow 15-1 หมวกน้ำเงิน · ร่าง · kwan 16 ต.ค. เลือก "ลงหน้าเทสก่อน")
	wd = os.path.join(SPR, 'rion_px_weapons_draft')
	if os.path.isdir(wd):
		for f in sorted(os.listdir(wd)):
			if f.endswith('.png'):
				out['pxw/' + f[:-4]] = png(os.path.join(wd, f))
	# Rion ชุดท่าครบจาก prompt pack (tools/sprites/rion_pack_px.py · ชีต Flow 14-1…17-4b · ร่าง · kwan 16 ต.ค. เลือก "1")
	rp = os.path.join(SPR, 'rion_pack_px')
	if os.path.isdir(rp):
		for f in sorted(os.listdir(rp)):
			if f.endswith('.png'):
				out['rpk/' + f[:-4]] = png(os.path.join(rp, f))
	# PixelLab ท่าเดินจาก master v2 (tools/sprites/pixellab_walk.py page · ร่าง · 18 ต.ค.) → คลิปเดียวกับชุดครบ วางคู่ชีต B
	pl = os.path.join(SPR, 'pixellab_draft/px')
	if os.path.isdir(pl):
		for f in sorted(os.listdir(pl)):
			if f.endswith('.png'):
				out['rpk/' + f[:-4]] = png(os.path.join(pl, f))
				if f.startswith('pixellab_slash2_west_'):   # พลิกหันขวาแบบชุดครบ (หน้าเทสพลิกกลับหันซ้ายเอง) · ใช้ในแท็บสกิล ชุดใหม่ (kwan 18 ต.ค. "ขอดูเทียบ")
					import io
					from PIL import Image, ImageOps
					b = io.BytesIO(); ImageOps.mirror(Image.open(os.path.join(pl, f))).save(b, 'PNG')
					out['rpk/pl_slash2_' + f.rsplit('_', 1)[1][:-4]] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
	out.update(pl_state_frames())
	# VFX จาก Astra ย่อเป็นพิกเซล (tools/sprites/astra_vfx_cut.py · kwan 19 ต.ค. เลือก "1" ลองแบบผสม BK-1 BK-4 · ร่าง)
	av = os.path.join(SPR, 'astra_vfx_draft')
	if os.path.isdir(av):
		for f in sorted(os.listdir(av)):
			if f.endswith('.png'):
				out['avx/' + f[:-4]] = png(os.path.join(av, f))
	ps = os.path.join(SPR, 'pixellab_draft/px_set')
	if os.path.isdir(ps):
		for f in sorted(os.listdir(ps)):
			if f.endswith('.png'):
				out['rpk/' + f[:-4]] = png(os.path.join(ps, f))
	# มอนภูมิภาค 1 พิกเซล (tools/sprites/monsters_px.py · ชีตรอบ 10 · ร่าง)
	md = os.path.join(SPR, 'monsters_px_draft')
	if os.path.isdir(md):
		for f in sorted(os.listdir(md)):
			if f.endswith('.png'):
				out['mpx/' + f[:-4]] = png(os.path.join(md, f))
	# มอนเทสร่างกาย 9 แบบ จาก PixelLab (tools/sprites/pixellab_monsters.py page · M07 M08 M09 M17 M29 · ร่าง) · คีย์เดียวกับชุดเดิม (mpx/) → ใช้ปุ่มเลือกมอนชุดเดียวกัน
	pm = os.path.join(SPR, 'pixellab_draft/monsters/px')
	if os.path.isdir(pm):
		for f in sorted(os.listdir(pm)):
			if f.endswith('.png'):
				out['mpx/' + f[:-4]] = png(os.path.join(pm, f))
	# ไอคอนอาวุธ 30 ชิ้น พิกเซล (tools/sprites/weapons_icons_px.py · ชีตรอบ 12 · ร่าง)
	wi = os.path.join(SPR, 'weapons_icons_draft')
	if os.path.isdir(wi):
		for f in sorted(os.listdir(wi)):
			if f.endswith('.png'):
				out['wic/' + f[:-4]] = png(os.path.join(wi, f))
	# ร่างศัตรูจากชีต Last Light (tools/sprites/ll_enemies.py) — แสดงในหน้านี้อย่างเดียว ยังไม่เข้าเกม
	dd = os.path.join(SPR, 'monsters_ll_draft')
	if os.path.isdir(dd):
		for f in sorted(os.listdir(dd)):
			if f.endswith('.png'):
				out['draft/' + f[:-4]] = png(os.path.join(dd, f))
	# ร่างมอนจาก Monster Compendium (tools/sprites/compendium_cut.py) — ตัวหลัก + ท่าหายใจ (ไม่ฝังภาพการ์ดรวม)
	# 64px + 4 ท่า (tools/sprites/compendium_animate.py) แทนชุด 48px เดิม
	cd = os.path.join(SPR, 'compendium_anim')
	if os.path.isdir(cd):
		for f in sorted(os.listdir(cd)):
			if f.endswith('.png'):
				out['cmp/' + f[:-4]] = png(os.path.join(cd, f))
	# ตัวอย่างมอนที่เจนรายตัว (แปลงกลับเป็นพิกเซลจริงแล้ว) — ร่างทดลอง
	sd = os.path.join(SPR, 'compendium_samples')
	if os.path.isdir(sd):
		for f in sorted(os.listdir(sd)):
			if f.endswith('.png'):
				out['smp/' + f[:-4]] = png(os.path.join(sd, f))
	# อาวุธ (tools/sprites/weapons.py) — ร่าง 30 ชิ้น
	wd = os.path.join(SPR, 'weapons_draft')
	if os.path.isdir(wd):
		for f in sorted(os.listdir(wd)):
			if f.endswith('.png'):
				out['wpn/' + f[:-4]] = png(os.path.join(wd, f))
	# Rion ถืออาวุธ (tools/sprites/weapons_held.py) — ยืน + ฟัน 4 เฟรม ต่ออาวุธ
	hd = os.path.join(SPR, 'weapons_held')
	if os.path.isdir(hd):
		for f in sorted(os.listdir(hd)):
			if f.endswith('.png'):
				out['held/' + f[:-4]] = png(os.path.join(hd, f))
	# ท่าร่ายเวทย์ + เอฟเฟกต์ (tools/sprites/spells_anim.py) — ร่าง 16 คาถา
	sp = os.path.join(SPR, 'spells_draft')
	if os.path.isdir(sp):
		for f in sorted(os.listdir(sp)):
			if f.endswith('.png'):
				out['spl/' + f[:-4]] = png(os.path.join(sp, f))
	# ทุกคลิปในแท็บท่าขยับแบบ 64 เฟรม (tools/sprites/poses64.py) — เก็บเฉพาะภาพไม่ซ้ำ
	pd = os.path.join(SPR, 'poses64_draft')
	if os.path.isdir(pd):
		for f in sorted(os.listdir(pd)):
			if f.endswith('.png'):
				out['p64/' + f[:-4]] = png(os.path.join(pd, f))
	# ผลจากเครื่องตัดชีต (tools/sprites/sheet_cut.py) — ไม่เอาชีตขยายที่ไว้ดูตรวจ
	cd = os.path.join(SPR, 'sheet_cut_draft')
	if os.path.isdir(cd):
		for f in sorted(os.listdir(cd)):
			if f.endswith('.png') and not f.endswith('_sheet.png'):
				out['cut/' + f[:-4]] = png(os.path.join(cd, f))
	# อาวุธที่ตัดจากชีต Weapon Collection 210 (tools/sprites/weapons_sheet_cut.py) — 32px + ขนาดชีต
	wd = os.path.join(SPR, 'weapons_sheet_draft')
	if os.path.isdir(wd):
		for f in sorted(os.listdir(wd)):
			if f.endswith('.png'):
				out['wsh/' + f[:-4]] = png(os.path.join(wd, f))
	# sprite stack ของอาวุธชุดเดียวกัน (tools/sprites/weapons_stack.py) — แถบชั้นล่าง→บน
	sd = os.path.join(SPR, 'weapons_stack_draft')
	if os.path.isdir(sd):
		for f in sorted(os.listdir(sd)):
			if f.endswith('.png'):
				out['wst/' + f[:-4]] = png(os.path.join(sd, f))
	# อาวุธ render จาก Blender (tools/sprites/weapons_3d.py) — 48px หมุน 16 มุม
	bd = os.path.join(SPR, 'weapons_3d_draft')
	if os.path.isdir(bd):
		for f in sorted(os.listdir(bd)):
			if f.endswith('.png'):
				out['w3d/' + f[:-4]] = png(os.path.join(bd, f))
	# ท่า Rion ตามการจับ (rion_grips.py) — ใช้กับอนิเมชันสกิลจากชีต
	gd = os.path.join(SPR, 'rion_lastlight_draft/grips')
	if os.path.isdir(gd):
		for f in sorted(os.listdir(gd)):
			if f.endswith('.png'):
				out['rion/grips/' + f[:-4]] = png(os.path.join(gd, f))
	# สกิลจากชีต 173 ท่า (tools/sprites/skill_sheet_cut.py) — เอฟเฟกต์ + ช่องต้นฉบับ (webp)
	kd = os.path.join(SPR, 'skills_sheet_draft')
	if os.path.isdir(kd):
		for f in sorted(os.listdir(kd)):
			if f.endswith('_fx.png'): out['skf/' + f[:-7]] = webp(os.path.join(kd, f))
			elif f.endswith('_cell.png'): out['skc/' + f[:-9]] = webp(os.path.join(kd, f), 60)
	# ชีต VFX Protagonist (tools/sprites/vfx_sheet_cut.py) — ชีตทั้งแผ่น (หน้าเทสครอปเอง) + ชั้นแสงต่อแผงท่า (webp มีโปร่งใส)
	vd = os.path.join(SPR, 'vfx_sheet_draft')
	if os.path.isdir(vd):
		out['vxs/sheet'] = webp(os.path.join(ROOT, 'docs/art-bible/vfx/vfx_protagonist_sheet.png'), 85)
		for f in sorted(os.listdir(vd)):
			if f.startswith('atlas_') and f.endswith('.png'): out['vxs/' + f[:-4]] = webp(os.path.join(vd, f), 85)
	# แสงจากชีต VFX ขนาดเกม (tools/sprites/vfx_game_fx.py) — พิกเซลอาร์ต png
	gd2 = os.path.join(SPR, 'vfx_fx_draft')
	if os.path.isdir(gd2):
		for f in sorted(os.listdir(gd2)):
			if f.endswith('.png'): out['vfg/' + f[:-4]] = png(os.path.join(gd2, f))
	# ริก Rion + อาวุธจากชีต (tools/sprites/rion_rig.py) — เฟรมที่อบแล้ว 64x64
	rd = os.path.join(SPR, 'rion_rig_draft')
	if os.path.isdir(rd):
		for f in sorted(os.listdir(rd)):
			if f.endswith('.png'): out['rig/' + f[:-4]] = png(os.path.join(rd, f))
	# ไอเท็ม / สิ่งก่อสร้าง / ยานพาหนะ / NPC ร่าง (tools/sprites/items_icons.py · world_props.py · npc_sprites.py)
	for folder, pre in (('items_draft', 'itm'), ('structures_draft', 'stc'), ('vehicles_draft', 'veh'), ('npcs_draft', 'npc'), ('env_sheet_draft', 'env')):
		d = os.path.join(SPR, folder)
		if os.path.isdir(d):
			for f in sorted(os.listdir(d)):
				if f.endswith('.png'):
					out[pre + '/' + f[:-4]] = png(os.path.join(d, f))
	# ไทล์ฉากหลังสำหรับจอศึกแบบ SaGa (พื้น + ของประดับ · เฉพาะชิ้นฐาน ไม่เอาชิ้นขอบ mask)
	td = os.path.join(ROOT, 'assets/tiles_ll')
	for n in ['ash_0', 'ash_1', 'ash_2', 'ash_3', 'grass_0', 'grass_1', 'grass_2', 'grass_3', 'stone_0', 'stone_1', 'stone_2', 'stone_3',
			'ruins', 'rock', 'pine', 'bush', 'ruin_house', 'flowers', 'house', 'shop', 'tent', 'lamp', 'crate', 'barrel']:
		f = os.path.join(td, n + '.png')
		if os.path.exists(f):
			out['tile/' + n] = png(f)
	# kwan 16 ต.ค. "หน้า rion ที่ไม่ตรงกับที่บอก ให้เอาออกจากทุกอาติแฟค" — Rion ยึดแบบ Flow หมวกน้ำเงินทั้งใบเท่านั้น
	# ไม่ฝังภาพ Rion แบบเก่า: Last Light (rion/ grips) · ถืออาวุธเก่า (held/) · ริก (rig/) · poses64 ของ Rion · ตัดชีตจำลอง (cut/) · ท่าร่าย (spl/) ·
	# ช่องชีตสกิล (skc/ มีตัวเอกของชีต) · ชีต VFX ตัวเอก (vxs/) · NPC (ทาสีจาก Rion เก่า)
	# ฉากที่ยังเรียกชื่อภาพเก่า → pxMap() ในเทมเพลตแทนด้วยภาพ px/ (Flow) ทุกจุด
	for k in [k for k in out if OLD_RION.match(k)]: del out[k]
	out.update(px_extra())
	return out


OLD_RION = re.compile(r'^(rion/|held/|rig/|cut/|spl/|skc/|vxs/|npc/|p64/rion_)')
PX_EXTRA = {'dodge': 'dodge', 'watch': 'watch', 'roll': 'jump_roll', 'victory': 'victory'}   # ท่าแบบ Flow 14-2 ที่เกมยังไม่ใช้ → ผืนเดียวกับ rion_px (96x112 เท้าแถว 110)


# ทางปลายอาวุธของท่าฟันในฉากต่อสู้ (รอยมีดตามปลายจริง · BLC_SWING ในเทมเพลต) — วัดจากภาพทุกครั้งที่สร้างหน้า ด้วย tools/sprites/blade_tip.py
# clip: (จุดหมุน = ไหล่ขวา, เฟรมเริ่มเหวี่ยง = ง้างสุด, เฟรมสุดท้าย, ทิศ −1 = มุมลดลง = ฟันข้ามหัวลงหน้าเมื่อหันซ้าย)
SWINGS = {'pls_atk_bl': ((62, 68), 4, 7, -1)}
# ท่าพุ่ง: ปลายอาวุธทุกเฟรม → รอยตามทางปลายในฉาก (ตัวเคลื่อนเร็ว ทางปลายเป็นเส้นตรงตามตัว) · ค่า = เฟรมที่ฉากใช้ (ต้องหาเจน)
TIPS = {'pls_bl1': [3, 5, 6, 7]}


def swing_paths():
	import importlib.util
	spec = importlib.util.spec_from_file_location('blade_tip', os.path.join(ROOT, 'tools/sprites/blade_tip.py')); bt = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt)
	out = {}
	for clip, (pivot, f0, f1, sign) in SWINGS.items():
		paths = [os.path.join(SPR, 'pixellab_draft/px_set', '%s_%d.png' % (clip, i)) for i in range(f0, f1 + 1)]
		if not all(os.path.isfile(p) for p in paths): continue
		res = bt.swing(paths, pivot, sign)
		miss = [f0 + i for i, r in enumerate(res) if r is None]
		if miss: sys.exit('blade_tip: หาปลายอาวุธ %s เฟรม %s ไม่เจอ — ดูภาพด้วย --check แล้วแก้ค่าใน blade_tip.py ก่อน' % (clip, miss))
		out[clip] = {'P': list(pivot), 'f0': f0, 'A': [round(r[1], 1) for r in res], 'R': [round(r[2], 1) for r in res], 'tip': [list(r[0]) for r in res]}
		print('ทางปลายอาวุธ', clip, 'มุม', out[clip]['A'], 'รัศมี', out[clip]['R'])
	for clip, need in TIPS.items():   # ปลายอาวุธทุกเฟรมของคลิป (รอยตามทางปลายจริงในฉาก · ท่าพุ่ง) · เฟรมที่ฉากใช้ต้องหาเจน
		paths = sorted(glob.glob(os.path.join(SPR, 'pixellab_draft/px_set', clip + '_*.png')), key=lambda p: int(re.search(r'_(\d+)\.png$', p).group(1)))
		if not paths: continue
		tips = [(lambda b: list(b[0]) if b else None)(bt.find_tip(p)) for p in paths]
		miss = [i for i in need if i >= len(tips) or tips[i] is None]
		if miss: sys.exit('blade_tip: หาปลายอาวุธ %s เฟรม %s ไม่เจอ' % (clip, miss))
		out.setdefault('tips', {})[clip] = tips
		print('ปลายอาวุธทุกเฟรม', clip, tips)
	return out


def px_extra():
	import importlib.util
	spec = importlib.util.spec_from_file_location('rpg', os.path.join(ROOT, 'tools/sprites/rion_px_game.py')); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
	out = {}
	for name, row in PX_EXTRA.items():
		i = 0
		while os.path.exists(os.path.join(g.SRC, '%s_%d.png' % (row, i))):
			im = g._frame(row, i); c = Image.new('RGBA', (g.W, g.H)); c.paste(im, (g.W // 2 - im.width // 2, g.FEET - im.height), im)
			import io as _io; b = _io.BytesIO(); c.save(b, 'PNG'); out['px/%s_%d' % (name, i)] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
			i += 1
	# หน้าคัตอิน = ภาพอ้างอิง Flow (rion_flow_ref_cut.png 512) ครอปหน้าผากถึงคาง ย่อ 44 จุด
	ref = Image.open(os.path.join(ROOT, 'docs/art-bible/rion_hires/rion_flow_ref_cut.png')).convert('RGBA').crop((150, 110, 370, 330)).resize((44, 44), Image.BOX)
	import io as _io; b = _io.BytesIO(); ref.save(b, 'PNG'); out['ref/face'] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
	return out

def sheet_cut():
	cd = os.path.join(SPR, 'sheet_cut_draft')
	return [dict(json.load(open(p, encoding='utf-8')), name=os.path.basename(p)[:-5]) for p in sorted(glob.glob(os.path.join(cd, '*.json')))]

def techs():
	rows = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/techs.csv'), encoding='utf-8')):
		rows.append({k: r[k] for k in ('tech_id', 'name_th', 'school', 'branch', 'parent', 'req_prof', 'power',
			'weight', 'sp', 'element', 'scope', 'hits', 'ignore_def', 'note', 'status', 'status_chance', 'effect') if k in r})
	# ท่ายึด (GDD 5.2) — สาย "ยึด" ในหน้าทดลอง · ค่าจาก seize_techs.csv ตรง ๆ
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/seize_techs.csv'), encoding='utf-8')):
		eff = {'def_up': 'DEF ตัวเอง +%d%% %s เทิร์น' % (round(float(r['value']) * 100), r['turns']),
			'av_cut': 'ลด AV ตัวเอง %d%%' % round(float(r['value']) * 100)}.get(r['effect'], r['effect'])
		rows.append({'tech_id': 'seize_' + r['monster_id'], 'name_th': r['name_th'], 'school': 'ยึด', 'branch': 'จาก ' + r['monster_id'],
			'parent': '', 'req_prof': '0', 'power': r['power'], 'weight': r['weight'], 'sp': r['sp'], 'element': r['element'],
			'scope': r['scope'], 'hits': '1', 'ignore_def': '0', 'status': '', 'status_chance': '',
			'note': eff + (' · ครั้งเดียวต่อศึก' if r['once'] == '1' else '') + ' · ความจำ %s ช่อง · %s' % (r['slots'], r['status']),
			'effect': r['effect'], 'value': float(r['value'])})
	return rows

def monsters(ids):
	out = []
	for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8')):
		if r['monster_id'] in ids:
			out.append({k: r[k] for k in ('monster_id', 'name_th', 'name_en', 'tier', 'hp', 'atk', 'def', 'spd',
				'weak', 'resist', 'immune', 'signature_tech')})
	return out

def bosses():
	"""บอสทุกตัวใน monsters.csv (is_boss = 1) — มีภาพหรือไม่ก็แสดง"""
	return [{k: r[k] for k in ('monster_id', 'name_th', 'name_en', 'tier', 'ec_min', 'ec_max', 'hp', 'atk', 'def', 'spd',
		'weak', 'resist', 'immune', 'signature_tech', 'tech_effect')}
		for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8')) if r['is_boss'] == '1']

def compendium():
	f = os.path.join(SPR, 'compendium_draft/index.json')
	return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []

def skill_ref():
	"""ชีตสกิล 173 ท่า แบ่งเป็นภาพละสาย (tools/sprites/skill_panels.py) — ภาพอ้างอิงเท่านั้น"""
	d = os.path.join(ROOT, 'docs/art-bible/compendium/skill_panels'); out = []
	for code, th in (('SL', 'คม'), ('PC', 'แทง'), ('CR', 'ทุบ'), ('BD', 'มือเปล่า'), ('ST', 'ยิง'), ('DV', 'กล')):
		f = os.path.join(d, code + '.jpg')
		if os.path.exists(f):
			out.append({'code': code, 'school': th, 'img': 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()})
	return out

def draft_map():
	"""ร่างแต่ละแบบ → มอนในเกมที่ MASTER ให้ใช้แบบนั้น (lastlight_archetype)"""
	names = {r['monster_id']: r['name_th'] for r in csv.DictReader(open(os.path.join(ROOT, 'data/monsters.csv'), encoding='utf-8'))}
	out = {}
	for e in json.load(open(os.path.join(ROOT, 'docs/art-bible/monster_visual_master.json'), encoding='utf-8'))['entries']:
		if e['id'] in names:
			out.setdefault(e['lastlight_archetype'], []).append('%s %s' % (e['id'], names[e['id']]))
	return out

def main(out_path):
	spr = sprites()
	mon_ids = sorted({k.split('/')[1].split('_')[0] for k in spr if k.startswith('mon/') and not k.split('/')[1].startswith('COMP')})
	data = {
		'sprites': spr,
		'techs': techs(),
		'fx': {k: v for k, v in json.load(open(os.path.join(ROOT, 'data/fx/ultimates.json'), encoding='utf-8')).items() if k != '_doc'},
		'monsters': monsters(mon_ids),
		'bosses': bosses(),
		'items': json.load(open(os.path.join(SPR, 'items_draft/index.json'), encoding='utf-8'))['items'],
		'env_sheet': json.load(open(os.path.join(SPR, 'env_sheet_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'env_sheet_draft/index.json')) else None,
		'structures': json.load(open(os.path.join(ROOT, 'docs/art-bible/world/structures.json'), encoding='utf-8')),
		'vehicles': json.load(open(os.path.join(ROOT, 'docs/art-bible/world/vehicles.json'), encoding='utf-8')),
		'npcs': json.load(open(os.path.join(ROOT, 'docs/art-bible/world/npcs.json'), encoding='utf-8')),
		# Rion พิกเซล: แถวล่างสุดของตัวต่อภาพ (ฉาก VFX วางเท้าลงพื้นเสมอ · ภาพวิ่ง/ง้างในชีตลอยอยู่ 17–21 จุด)
		'px_feet': {f[:-4]: Image.open(os.path.join(SPR, 'rion_px', f)).getchannel('A').getbbox()[3] for f in sorted(os.listdir(os.path.join(SPR, 'rion_px'))) if f.endswith('.png')},
		'px_extra': {k: sum(1 for x in os.listdir(os.path.join(SPR, 'rion_flow_draft/main_px')) if re.fullmatch(v + r'_\d+\.png', x)) for k, v in PX_EXTRA.items()},
		'astra_vfx': astra_vfx(),
		'monsters_px': sum((json.load(open(p, encoding='utf-8'))['monsters'] for p in (os.path.join(SPR, 'monsters_px_draft/index.json'), os.path.join(SPR, 'pixellab_draft/monsters/px/index.json')) if os.path.isfile(p)), []),
		'swing': swing_paths(),   # ทางปลายอาวุธ (blade_tip.py)
		'rion_pack': rion_pack_clips(),   # ชุดท่าครบ (prompt pack) + PixelLab
		# ต้นไม้ท่า 17 ท่า (ร่าง · tools/data/skill17_proposal.py + skill17_content.py) → ชื่อ/จำนวนครั้ง/เลือดไหล/ท่าทาง ของคลิปสายคม 17 ท่า (kwan 18 ต.ค. "ปรับชื่อและท่าทางให้ตรงกับรายละเอียดในต้นไม้ท่า")
		'tree17': list(csv.DictReader(open(os.path.join(ROOT, 'docs/design/skill_trees_17.csv'), encoding='utf-8'))),
		'motion17': json.load(open(os.path.join(ROOT, 'docs/design/skill_trees_17_content.json'), encoding='utf-8'))['motion'],
		'px_weapons': json.load(open(os.path.join(SPR, 'rion_px_weapons_draft/index.json'), encoding='utf-8'))['clips'] if os.path.isfile(os.path.join(SPR, 'rion_px_weapons_draft/index.json')) else [],   # ชีต 15-1 (แบบ Flow)
		'poses64': json.load(open(os.path.join(SPR, 'poses64_draft/index.json'), encoding='utf-8'))['poses'],
		'draft_map': draft_map(),
		'sheet_cut': sheet_cut(),
		'skill_sheet': json.load(open(os.path.join(SPR, 'skills_sheet_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'skills_sheet_draft/index.json')) else None,
		'vfx_sheet': json.load(open(os.path.join(SPR, 'vfx_sheet_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'vfx_sheet_draft/index.json')) else None,
		'vfx_fx': json.load(open(os.path.join(SPR, 'vfx_fx_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'vfx_fx_draft/index.json')) else None,
		'rion_rig': json.load(open(os.path.join(SPR, 'rion_rig_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'rion_rig_draft/index.json')) else None,
		'weapon_3d': json.load(open(os.path.join(SPR, 'weapons_3d_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'weapons_3d_draft/index.json')) else None,
		'weapon_stack': json.load(open(os.path.join(SPR, 'weapons_stack_draft/index.json'), encoding='utf-8')) if os.path.exists(os.path.join(SPR, 'weapons_stack_draft/index.json')) else None,
		'weapon_sheet': json.load(open(os.path.join(SPR, 'weapons_sheet_draft/index.json'), encoding='utf-8'))['items'] if os.path.exists(os.path.join(SPR, 'weapons_sheet_draft/index.json')) else [],
		'compendium': compendium(),
		'weapons': [dict(w, school=f['school']) for f in json.load(open(os.path.join(ROOT, 'docs/art-bible/weapons/weapons_full.json'), encoding='utf-8'))['families'] for w in f['weapons']],
		'spells': json.load(open(os.path.join(ROOT, 'docs/art-bible/spells/spells_full.json'), encoding='utf-8'))['schools'],
		'skill_ref': skill_ref(),
		# ความเข้ากับร่างกาย (data/monster_body.csv · body_affinity.csv) — แท็บสกิลคิดดาเมจ + ป้าย อ่อนแอ/ต้านทาน แบบเดียวกับเกม
		'body': {r['monster_id']: r['body'] for r in csv.DictReader(open(os.path.join(ROOT, 'data/monster_body.csv'), encoding='utf-8'))},
		'body_aff': {r['school'] + '|' + r['body']: int(r['sign']) for r in csv.DictReader(open(os.path.join(ROOT, 'data/body_affinity.csv'), encoding='utf-8'))},
		# preset จาก night-forge-vfx-lab (kwan ส่ง 10 ต.ค. · Drive LAB) — ทุกไฟล์ *.nightforge.json · ฟันดวงดาว = ประกาย ★ สายคม
		'lab': [{'file': os.path.basename(f)[:-len('.nightforge.json')], 'comp': json.load(open(f, encoding='utf-8'))['comp']} for f in sorted(glob.glob(os.path.join(ROOT, 'docs/art-bible/vfx/*.nightforge.json')))],
		'k': {
			'MIT_K': const('core/Formulas.gd', 'MIT_K'),
			'WEAK_MULT': const('core/Formulas.gd', 'WEAK_MULT'),
			'RESIST_MULT': const('core/Formulas.gd', 'RESIST_MULT'),
			'BODY_GOOD': const('core/Formulas.gd', 'BODY_GOOD'),
			'BODY_BAD': const('core/Formulas.gd', 'BODY_BAD'),
			'ATTACK_FRAME_SEC': const('world/BattleScreen.gd', 'ATTACK_FRAME_SEC'),
			'HERO_IDLE_SEC': const('world/BattleScreen.gd', 'HERO_IDLE_SEC'),
			'FOE_IDLE_SEC': const('world/BattleScreen.gd', 'FOE_IDLE_SEC'),
			'MOVE_TIME': const('world/Overworld.gd', 'MOVE_TIME'),
			'FX_SEC': const('world/BattleScreen.gd', 'FX_SEC'),
			'ULT_PROF': const('world/BattleScreen.gd', 'ULT_PROF'),
			'HERO_X': const('world/BattleScreen.gd', 'HERO_X'),
			'STAGE_FEET_Y': const('world/BattleScreen.gd', 'STAGE_FEET_Y'),
			'FOE_AREA': [float(v) for v in re.search(r'const FOE_AREA\s*:?=\s*Vector2\(([0-9.]+),\s*([0-9.]+)\)', open(os.path.join(ROOT, 'world/BattleScreen.gd'), encoding='utf-8').read()).groups()],
		},
	}
	# ภาพสไปรต์แยกเป็นไฟล์ก้อน <ชื่อหน้า>_sprites_<i>.json ข้างหน้าเว็บ (kwan 6 ต.ค. "เพิ่มลิมิตหน้าเทสเป็น 100 MB")
	# Artifact รับไฟล์ละ ≤ 16 MB แต่หลายไฟล์ต่อหน้าได้ → หน้าเว็บเก็บแค่ชื่อภาพ แล้วโหลดก้อนภาพด้วย fetch ก่อนเริ่ม
	# อัปโหลด: Artifact publish ด้วย files = {ชื่อก้อน: path} ทุกก้อน (พิมพ์รายชื่อไว้ท้ายผล) · เปิดในเครื่องต้องผ่าน http server (file:// โหลด fetch ไม่ได้)
	stem = os.path.splitext(os.path.basename(out_path))[0]; out_dir = os.path.dirname(os.path.abspath(out_path))
	for old in glob.glob(os.path.join(out_dir, stem + '_sprites_*.json')): os.remove(old)
	chunks, cur, size = [], {}, 0
	for k, v in spr.items():
		if cur and size + len(v) > CHUNK_BYTES: chunks.append(cur); cur, size = {}, 0
		cur[k] = v; size += len(v) + len(k) + 6
	if cur: chunks.append(cur)
	names = []
	for i, c in enumerate(chunks):
		n = f'{stem}_sprites_{i}.json'; open(os.path.join(out_dir, n), 'w', encoding='utf-8').write(json.dumps(c, separators=(',', ':'))); names.append(n)
	data['sprites'] = {k: 1 for k in spr}; data['sprite_chunks'] = names
	tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anim_test.tpl.html'), encoding='utf-8').read()
	html = tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
	open(out_path, 'w', encoding='utf-8').write(html)
	sizes = [len(html)] + [os.path.getsize(os.path.join(out_dir, n)) for n in names]
	if max(sizes) > FILE_LIMIT or sum(sizes) > TOTAL_LIMIT:
		raise SystemExit(f'เกินลิมิต: ไฟล์ใหญ่สุด {max(sizes)} (≤ {FILE_LIMIT}) · รวม {sum(sizes)} (≤ {TOTAL_LIMIT})')
	if sum(sizes) > TOTAL_LIMIT * V2_AT:
		raise SystemExit(f'ใกล้เต็มลิมิต ({sum(sizes)} / {TOTAL_LIMIT} = {sum(sizes) / TOTAL_LIMIT:.0%}) → แยกงานใหม่ไปหน้า animation test V2 (Artifact ลิงก์ใหม่) แทนการเพิ่มในหน้านี้')
	print(out_path, len(html), 'bytes + ภาพ', len(names), 'ก้อน', sum(sizes[1:]), 'bytes · รวม', sum(sizes), '/', TOTAL_LIMIT, f'({sum(sizes) / TOTAL_LIMIT:.0%} · แยก V2 ที่ {V2_AT:.0%})', '·', len(spr), 'sprites ·', len(data['techs']), 'techs ·', len(data['monsters']), 'monsters')
	print('ก้อนภาพ:', ' '.join(names))

if __name__ == '__main__':
	main(sys.argv[1] if len(sys.argv) > 1 else 'anim_test.html')
