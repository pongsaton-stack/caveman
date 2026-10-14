# tools/blender/rion_model.py — รันใน Blender (ผ่าน tools/blender/bl.py): ตัวเอก REBORNER (Rion) แบบ chibi 3D ตามภาพต้นแบบ kwan
# (docs/art-bible/rion3d/rion_ref_2026-10-14.png) · แยกชิ้นตามส่วน + ลบมุม (bevel) + แสงเงาการ์ตูน 2 ระดับ + เส้นขอบเข้ม + โครงกระดูก
#
# ARGS (KEY=VALUE ของ bl.py):
#   OUT=<โฟลเดอร์>        ที่เก็บ PNG
#   BG=green|alpha|both   พื้นเขียว #00B140 (คีย์ออกได้) / พื้นโปร่ง (ทำสไปรต์) / ทั้งสอง (ค่าเริ่ม both)
#   SCALE=1|4             1 = 1145x1374 · 4 = 4580x5496
#   BLEND=<ไฟล์ .blend>   บันทึกไฟล์ Blender ที่แก้ต่อได้ (ไม่ใส่ = ไม่บันทึก)
#   DIRS=0|4|8            เพิ่มภาพพื้นโปร่งรอบตัว ผืน/กล้องเดียวกับภาพหลัก: 4 → front/right/back/left.png (right = หันไปทางขวาของภาพ)
#                         8 → dir_<i>.png (0 หน้า · ทวนเข็ม: 2 = หันขวาของภาพ · 4 หลัง · 6 = หันซ้ายของภาพ)
#   EL=<องศา>             มุมกล้องก้มลง (ค่าเริ่ม 5 = เกือบตรง) · FILL=<สัดส่วน> ตัวสูงกี่ส่วนของภาพ (ค่าเริ่ม 0.86)
#
# พิกัด: ยืนบนพื้น z=0 · หันหน้าไป -Y · ซ้ายของตัวละคร = +X (ชื่อ .L) · ตัวสูง ~1.85 หน่วย
# สัดส่วนวัดจากภาพต้นแบบ (1 หน่วย ≈ 655 จุดในภาพ 1145x1374): ยอดหมวก→คาง 45% ของความสูง · เข็มขัด 0.64 · ชายกางเกง 0.39 · บูทสูง 0.27
import bpy, bmesh, math, os
from mathutils import Matrix, Vector

OUT = ARGS.get("OUT", "/tmp/rion_model"); BG = ARGS.get("BG", "both"); SCALE = int(ARGS.get("SCALE", 1))
BLEND = ARGS.get("BLEND", ""); DIRS = int(ARGS.get("DIRS", 0)); EL = float(ARGS.get("EL", 5)); FILL = float(ARGS.get("FILL", 0.86))
os.makedirs(OUT, exist_ok=True)

sc = bpy.context.scene   # ล้างฉากเอง (read_factory_settings จะปิดปลั๊กอิน MCP ที่ส่งคำสั่งมา)
for o in list(bpy.data.objects):
	bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.armatures, bpy.data.worlds):
	for d in list(coll):
		coll.remove(d)

# ── สี (อ่านจากภาพต้นแบบ) ──
SKIN, HAIR, CAP, GOLD, LENS, SHIRT, TIE, SHORTS, CUFF, BELT, BAG, BAG2, BOOT, TAN, SOCK = (
	"#f9dcc0", "#80482a", "#2f62c6", "#d99a2b", "#3f86e0", "#f7f6f1", "#2c5fc4", "#2f6dd2", "#2a5cb8", "#6e4426", "#8a5530", "#74452a",
	"#8b5a33", "#e3c896", "#f7f6f1")
EYE, DARK, BLUSH, WHITE, LACE, STRAP_G = "#6a3b1c", "#2a1a14", "#f5aea4", "#ffffff", "#efe2c4", "#8a5a2a"
INK = (0.022, 0.011, 0.007, 1)            # เส้นขอบน้ำตาลเกือบดำ (linear)
SHADOW = (0.74, 0.70, 0.86, 1)            # สีคูณด้านเงา อมม่วงฟ้า
FLAT = {EYE, DARK, BLUSH, WHITE}          # ลายหน้า ไม่ลงเงา

MATS = {}
def lin(hexcol):
	"""#rrggbb (sRGB) → ค่าเชิงเส้นที่ Blender ใช้ (สูตร sRGB ตรง ไม่ใช่ประมาณ ^2.2 → สีออกมาตรงไบต์)"""
	def ch(c):
		return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
	return tuple(ch(int(hexcol[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1.0,)

def toon(hexcol):
	"""วัสดุการ์ตูน: Diffuse → Shader to RGB → ไล่สีแบบขั้น (เงา/สว่าง) → คูณสีพื้น → Emission (สีออกตรงตามที่ตั้ง)"""
	if hexcol in MATS:
		return MATS[hexcol]
	m = bpy.data.materials.new("toon_" + hexcol[1:]); m.use_nodes = True; m.diffuse_color = lin(hexcol)
	nt = m.node_tree; nt.nodes.clear()
	dif = nt.nodes.new("ShaderNodeBsdfDiffuse"); s2r = nt.nodes.new("ShaderNodeShaderToRGB")
	ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp; cr.interpolation = "CONSTANT"
	cr.elements[0].color = (1, 1, 1, 1) if hexcol in FLAT else SHADOW; cr.elements[1].position = 0.12; cr.elements[1].color = (1, 1, 1, 1)
	mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1.0
	mix.inputs[6].default_value = lin(hexcol)
	em = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
	for a, b in ((dif.outputs[0], s2r.inputs[0]), (s2r.outputs[0], ramp.inputs[0]), (ramp.outputs[0], mix.inputs[7]),
			(mix.outputs[2], em.inputs[0]), (em.outputs[0], out.inputs["Surface"])):
		nt.links.new(a, b)
	MATS[hexcol] = m
	return m

ink = bpy.data.materials.new("ink"); ink.use_nodes = True; ink.use_backface_culling = True
_nt = ink.node_tree; _nt.nodes.clear(); _em = _nt.nodes.new("ShaderNodeEmission"); _em.inputs["Color"].default_value = INK
_nt.links.new(_em.outputs[0], _nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])

# ── ตัวช่วยปั้น ──
GROUPS = {}   # ชื่อชิ้น → [วัตถุย่อย] (รวมเป็นวัตถุเดียวต่อชื่อทีหลัง)
def part(group, kind, loc, scale, col, rot=(0, 0, 0), cut=None, **kw):
	if kind == "box":
		bpy.ops.mesh.primitive_cube_add(size=1)
	elif kind == "cyl":
		bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("v", 32), radius=0.5, depth=1)
	elif kind == "cone":
		bpy.ops.mesh.primitive_cone_add(vertices=kw.get("v", 12), radius1=kw.get("r1", 0.5), radius2=kw.get("r2", 0.0), depth=1)
	elif kind == "sph":
		bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5)
	elif kind == "torus":
		bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=kw.get("minor", 0.12), major_segments=40, minor_segments=10)
	o = bpy.context.active_object
	o.location = loc; o.scale = scale; o.rotation_euler = [math.radians(a) for a in rot]
	o.data.materials.append(toon(col))
	if cut:   # ลบจุดยอดตามเงื่อนไข (พิกัดก่อนย่อขยาย) — ทำหมวก/ผม/ปีกหมวกเป็นเปลือกบางส่วน
		bm = bmesh.new(); bm.from_mesh(o.data)
		bmesh.ops.delete(bm, geom=[v for v in bm.verts if cut(v.co)], context="VERTS"); bm.to_mesh(o.data); bm.free()
	GROUPS.setdefault(group, []).append(o)
	return o

def both(fn):
	for s, side in ((1, "L"), (-1, "R")):
		fn(s, side)

# ── บูทหนังผูกเชือก + ถุงเท้า + ขา ──  (ขาห่างกันเล็กน้อย ปลายเท้าแบะออก 6°)
FX = 0.17
def leg(s, side):
	x = FX * s; B = "Boot." + side
	part(B, "box", (x, -0.045, 0.035), (0.25, 0.37, 0.07), TAN)                          # พื้นรองเท้าสีทราย
	part(B, "sph", (x, -0.06, 0.09), (0.25, 0.37, 0.15), BOOT)                           # หัวบูทเตี้ย
	part(B, "sph", (x, -0.16, 0.075), (0.2, 0.15, 0.11), TAN)                            # หัวรองเท้าสีทราย
	part(B, "cyl", (x, -0.01, 0.19), (0.21, 0.21, 0.17), BOOT)                           # ข้อบูท (ที่ผูกเชือก)
	part(B, "cyl", (x, -0.01, 0.272), (0.225, 0.225, 0.03), BOOT)                        # ขอบปากบูทพับ
	part(B, "box", (x, -0.105, 0.2), (0.07, 0.02, 0.13), BOOT)                           # ลิ้นรองเท้า
	for z, a in ((0.155, 32), (0.19, -32), (0.225, 32), (0.255, -20)):                   # เชือกผูกไขว้ด้านหน้า
		part(B, "box", (x, -0.118, z), (0.085, 0.014, 0.014), LACE, rot=(0, a, 0))
	for z in (0.155, 0.19, 0.225):
		for e in (-1, 1):
			part(B, "cyl", (x + 0.045 * e, -0.113, z), (0.018, 0.018, 0.01), GOLD, rot=(90, 0, 0), v=12)   # ตาไก่ทอง
	part(B, "box", (x, -0.205, 0.13), (0.11, 0.03, 0.025), GOLD, rot=(30, 0, 0))         # สายรัดทองหลังเท้า
	part("Sock." + side, "cyl", (x, 0.0, 0.29), (0.15, 0.15, 0.06), SOCK)
	part("Leg." + side, "cyl", (x, 0.0, 0.345), (0.11, 0.11, 0.12), SKIN)
	part("Shorts." + side, "cyl", (x * 0.82, 0.0, 0.47), (0.23, 0.24, 0.17), SHORTS)    # ขากางเกง (แยกซ้าย/ขวา ขยับตามต้นขา)
	part("Shorts." + side, "cyl", (x * 0.82, 0.0, 0.395), (0.245, 0.255, 0.04), CUFF)   # ปลายขาพับ
both(leg)
part("Shorts", "box", (0, 0, 0.575), (0.43, 0.27, 0.13), SHORTS)                       # สะโพก
part("Belt", "cyl", (0, 0, 0.645), (0.45, 0.29, 0.05), BELT)
part("Belt", "box", (0, -0.145, 0.645), (0.09, 0.02, 0.05), GOLD)                       # หัวเข็มขัด

# ── ลำตัว: เสื้อเชิ้ตขาวปก + เนคไทน้ำเงิน ──
part("Shirt", "cone", (0, 0, 0.82), (0.42, 0.28, 0.38), SHIRT, r1=0.5, r2=0.43, v=32)
for s in (-1, 1):
	part("Shirt", "cone", (0.055 * s, -0.125, 0.985), (0.11, 0.05, 0.08), SHIRT, rot=(180, 0, -28 * s), v=3)   # ปกแหลม
part("Tie", "box", (0, -0.14, 0.86), (0.06, 0.02, 0.2), TIE, rot=(-3, 0, 0))
part("Tie", "cone", (0, -0.143, 0.745), (0.06, 0.02, 0.05), TIE, rot=(180, 0, 0), r1=0.5, v=4)
part("Tie", "box", (0, -0.14, 0.965), (0.07, 0.035, 0.045), TIE)                       # ปม
part("Head", "cyl", (0, 0, 1.03), (0.11, 0.11, 0.1), SKIN)                             # คอ

# ── แขน: แขนเสื้อสั้น + แขน + กำมือ · กางออกจากตัว 11° ──
SHOULDER = 0.98; ARM_OUT = 11
def arm(s, side):
	part("Sleeve." + side, "sph", (0.215 * s, 0, 0.93), (0.18, 0.18, 0.16), SHIRT)
	part("Arm." + side, "cyl", (0.24 * s, 0, 0.76), (0.09, 0.09, 0.26), SKIN)
	part("Arm." + side, "sph", (0.245 * s, -0.01, 0.6), (0.13, 0.12, 0.13), SKIN)        # กำปั้น
	part("Arm." + side, "sph", (0.215 * s, -0.06, 0.615), (0.05, 0.04, 0.05), SKIN)      # นิ้วโป้ง
both(arm)
part("Watch", "cyl", (0.242, 0, 0.665), (0.105, 0.105, 0.04), "#2f62c6")               # นาฬิกาข้อมือซ้าย (ขวาของภาพ)
part("Watch", "box", (0.245, -0.052, 0.665), (0.045, 0.012, 0.035), "#55a86a")         # หน้าปัด

# ── เป้หลัง + สายสะพาย 2 เส้น + กระเป๋าข้าง ──
part("Backpack", "box", (0, 0.21, 0.82), (0.42, 0.2, 0.36), BAG)
part("Backpack", "box", (0, 0.315, 0.79), (0.3, 0.05, 0.22), BAG2)                    # ช่องหน้าเป้ (ด้านหลังตัว)
part("Backpack", "box", (0, 0.32, 0.88), (0.31, 0.06, 0.06), BAG)                     # ฝาช่องหน้า
part("Backpack", "box", (0, 0.35, 0.86), (0.05, 0.01, 0.05), GOLD)
for s in (-1, 1):
	part("Backpack", "box", (0.255 * s, 0.17, 0.8), (0.09, 0.15, 0.2), BAG2)           # กระเป๋าข้าง
	part("Backpack", "box", (0.302 * s, 0.17, 0.83), (0.01, 0.05, 0.05), GOLD)
	part("Straps", "box", (0.12 * s, -0.13, 0.84), (0.055, 0.02, 0.32), BAG)           # สายสะพายหน้าอก
	part("Straps", "box", (0.12 * s, -0.145, 0.85), (0.075, 0.02, 0.055), GOLD)       # หัวเข็มสาย
	part("Straps", "box", (0.12 * s, 0.0, 1.0), (0.055, 0.28, 0.03), BAG)             # ข้ามบ่า
	part("Straps", "box", (0.13 * s, -0.12, 0.69), (0.06, 0.03, 0.04), GOLD)          # ปลายสายล่าง

# ── หัว ── สัดส่วนจากภาพ (ยอดหมวก→คาง = 1): ขอบปีกหมวก .51 · คิ้ว .63 · ตา .71–.87 · ปาก .95
HZ = 1.37
part("Head", "sph", (0, 0, HZ), (0.72, 0.64, 0.66), SKIN)
for s in (-1, 1):
	part("Head", "sph", (0.355 * s, 0.02, HZ - 0.1), (0.08, 0.06, 0.11), SKIN)        # หู
# ผมยุ่ง: เปลือกครึ่งหลัง + หน้าม้าแหลมหลายปอย + จอน + ปอยชี้ออกข้าง + ท้ายทอย
part("Hair", "sph", (0, 0.01, HZ), (0.77, 0.71, 0.72), HAIR, cut=lambda c: c.y < 0.02 and c.z < 0.12)
for x, ln, tilt, yo in ((-0.27, 0.13, 32, 0), (-0.18, 0.17, 18, 0.01), (-0.09, 0.15, 8, 0), (-0.03, 0.21, 2, 0.012),
		(0.05, 0.24, -6, 0), (0.13, 0.17, -14, 0.01), (0.21, 0.15, -24, 0), (0.28, 0.12, -34, 0.01)):
	part("Hair", "cone", (x, -0.3 - yo, HZ + 0.07 - ln / 2), (0.14, 0.1, ln), HAIR, rot=(188, tilt, 0), v=6)
for s in (-1, 1):
	part("Hair", "cone", (0.325 * s, -0.03, HZ - 0.07), (0.09, 0.07, 0.22), HAIR, rot=(180, -8 * s, 0), v=6)   # จอน (หน้าหู · ไม่บังตาตอนหันข้าง)
	for z, ln, a, y in ((HZ + 0.03, 0.2, 72, 0.04), (HZ - 0.06, 0.18, 98, 0.1), (HZ - 0.17, 0.14, 122, 0.06), (HZ - 0.02, 0.15, 85, 0.2)):
		part("Hair", "cone", (0.36 * s, y, z), (0.11, 0.09, ln), HAIR, rot=(0, a * s, 0), v=6)
	part("Hair", "cone", (0.13 * s, 0.33, HZ - 0.22), (0.13, 0.08, 0.17), HAIR, rot=(-170, 0, 0), v=6)    # ท้ายทอย
part("Hair", "cone", (0, 0.34, HZ - 0.24), (0.13, 0.08, 0.19), HAIR, rot=(-172, 0, 0), v=6)

# ลายหน้า: แผ่นบางชิดผิว เอียงตามความโค้ง · ตาโต (ขอบเข้มหนาบน → ขาว → ม่านตาน้ำตาล → รูม่านตา → ประกาย 2 จุด)
EZ = HZ - 0.15
for s in (-1, 1):
	x = 0.13 * s; R = (22, 0, 22 * s)   # เอียงตามผิวหัวมากขึ้น → หันข้างยังเห็นตา
	part("Face", "sph", (x, -0.275, EZ + 0.014), (0.13, 0.012, 0.175), DARK, rot=R)
	part("Face", "sph", (x * 1.01, -0.281, EZ), (0.11, 0.012, 0.15), WHITE, rot=R)
	part("Face", "sph", (x * 0.97, -0.287, EZ - 0.008), (0.088, 0.012, 0.128), EYE, rot=R)
	part("Face", "sph", (x * 0.97, -0.292, EZ - 0.01), (0.05, 0.012, 0.076), DARK, rot=R)
	part("Face", "sph", (x * 0.97 + 0.02, -0.298, EZ + 0.026), (0.034, 0.008, 0.04), WHITE, rot=R)
	part("Face", "sph", (x * 0.97 - 0.02, -0.296, EZ - 0.04), (0.016, 0.008, 0.018), WHITE, rot=R)
	part("Face", "box", (0.13 * s, -0.325, HZ - 0.035), (0.11, 0.03, 0.026), DARK, rot=(0, 20 * s, 18 * s))   # คิ้วเฉียงมุ่งมั่น
	part("Face", "sph", (0.2 * s, -0.178, HZ - 0.215), (0.075, 0.01, 0.04), BLUSH, rot=(35, 0, 40 * s))
part("Face", "sph", (0, -0.262, HZ - 0.205), (0.012, 0.01, 0.012), DARK)                # จมูกจุด
part("Face", "torus", (0, -0.243, HZ - 0.232), (0.05, 0.05, 0.05), DARK, rot=(80, 0, 0), minor=0.16, cut=lambda c: c.y > -0.05)   # ยิ้ม

# หมวกแก๊ปน้ำเงินล้วน (ไม่มีแถบครีม/ขาว) ทรงสูง + ปีกหน้าสั้นโค้ง + ปุ่มบน
part("Cap", "sph", (0, 0.0, HZ + 0.04), (0.8, 0.76, 0.78), CAP, cut=lambda c: c.z < 0.0)
part("Cap", "sph", (0, -0.17, HZ + 0.05), (0.68, 0.62, 0.05), CAP, rot=(-6, 0, 0), cut=lambda c: c.y > -0.05)
part("Cap", "sph", (0, 0.0, HZ + 0.43), (0.09, 0.09, 0.06), CAP)
# แว่นกันลมทองเหลือง เลนส์ฟ้าสะท้อน วางบนหมวก + สายรัดรอบหมวก
GZ = HZ + 0.22
part("Goggles", "cyl", (0, 0.0, GZ), (0.73, 0.69, 0.05), STRAP_G)
for s in (-1, 1):
	x = 0.135 * s
	part("Goggles", "torus", (x, -0.325, GZ), (0.2, 0.2, 0.2), GOLD, rot=(64, 0, 0), minor=0.14)
	part("Goggles", "cyl", (x, -0.322, GZ), (0.18, 0.18, 0.02), LENS, rot=(64, 0, 0))
	part("Goggles", "sph", (x + 0.03, -0.345, GZ + 0.02), (0.05, 0.01, 0.03), "#d8ecff", rot=(64, 0, 0))   # แสงสะท้อนเลนส์
	part("Goggles", "box", (0.25 * s, -0.25, GZ), (0.05, 0.06, 0.07), GOLD, rot=(0, 0, -40 * s))
part("Goggles", "box", (0, -0.35, GZ), (0.07, 0.03, 0.05), GOLD)

# ── รวมเป็นวัตถุต่อชิ้น · ล้างสเกล · ลบมุม · เส้นขอบ ──
def join(name, objs):
	bpy.ops.object.select_all(action="DESELECT")
	for o in objs:
		o.select_set(True)
	bpy.context.view_layer.objects.active = objs[0]
	if len(objs) > 1:
		bpy.ops.object.join()
	o = bpy.context.active_object; o.name = o.data.name = name
	bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # ล้างสเกลชิ้นแรก → เส้นขอบ/ลบมุมหนาเท่ากันทุกชิ้น
	return o

PIVOT = {}
OBJS = {name: join(name, objs) for name, objs in GROUPS.items()}
# กางแขนออกจากตัว (หมุนรอบไหล่) — แขนเสื้อหมุนตามด้วย
for side, s in (("L", 1), ("R", -1)):
	piv = Vector((0.2 * s, 0, SHOULDER)); PIVOT[side] = piv
	rot = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-ARM_OUT * s), 4, "Y") @ Matrix.Translation(-piv)   # หมุนรอบ Y ติดลบ = ปลายแขนออกนอกตัว
	for n in ("Arm." + side, "Sleeve." + side) + (("Watch",) if side == "L" else ()):
		OBJS[n].data.transform(rot)

for name, o in OBJS.items():
	bpy.context.view_layer.objects.active = o; o.select_set(True)
	bpy.ops.object.shade_smooth(); o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(40)
	if name == "Face":
		continue   # ลายหน้าไม่มีเส้นขอบ/ลบมุม (ไม่งั้นปาก/จมูกบวมเป็นก้อนดำ)
	bev = o.modifiers.new("bevel", "BEVEL"); bev.width = 0.006; bev.segments = 2; bev.limit_method = "ANGLE"; bev.angle_limit = math.radians(35)
	o.data.materials.append(ink)
	sol = o.modifiers.new("outline", "SOLIDIFY"); sol.thickness = float(ARGS.get("LINE", 0.012)); sol.offset = 1.0
	sol.use_flip_normals = True; sol.material_offset = len(o.data.materials) - 1; sol.use_rim = False

# ── โครงกระดูก (พร้อมทำท่า): ชิ้นแข็งผูกกับกระดูก ──
arm_d = bpy.data.armatures.new("RionRig"); rig = bpy.data.objects.new("RionRig", arm_d); sc.collection.objects.link(rig)
rig.show_in_front = True; bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode="EDIT")
BONES = {}
def bone(name, head, tail, parent=None):
	b = arm_d.edit_bones.new(name); b.head = head; b.tail = tail
	if parent:
		b.parent = arm_d.edit_bones[parent]
	BONES[name] = b
bone("root", (0, 0, 0), (0, 0.3, 0))
bone("hips", (0, 0, 0.56), (0, 0, 0.66), "root")
bone("spine", (0, 0, 0.66), (0, 0, 0.98), "hips")
bone("head", (0, 0, 1.0), (0, 0, 1.6), "spine")
for side, s in (("L", 1), ("R", -1)):
	sh = PIVOT[side]; hand = Vector((0.245 * s + math.sin(math.radians(ARM_OUT)) * 0.36 * s, 0, 0.6))
	bone("arm." + side, tuple(sh), tuple(hand), "spine")
	bone("thigh." + side, (FX * 0.82 * s, 0, 0.56), (FX * s, 0, 0.32), "hips")
	bone("foot." + side, (FX * s, 0, 0.32), (FX * s, -0.15, 0.06), "thigh." + side)
bpy.ops.object.mode_set(mode="OBJECT")
PARENT = {"Head": "head", "Face": "head", "Hair": "head", "Cap": "head", "Goggles": "head",
	"Shirt": "spine", "Tie": "spine", "Backpack": "spine", "Straps": "spine", "Belt": "hips", "Shorts": "hips", "Watch": "arm.L"}
for side in ("L", "R"):
	PARENT.update({"Arm." + side: "arm." + side, "Sleeve." + side: "arm." + side, "Leg." + side: "thigh." + side, "Shorts." + side: "thigh." + side,
		"Sock." + side: "foot." + side, "Boot." + side: "foot." + side})
for name, o in OBJS.items():
	mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = "BONE"; o.parent_bone = PARENT[name]
	o.matrix_world = mw   # คงตำแหน่งเดิม (ผูกตอนท่าพัก)
bpy.context.view_layer.update()

# ── ฉาก: กล้องฉากตั้งตรงหน้า · แสงเดียวไม่มีเงาตกกระทบ · ไม่มีพื้น ──
sun_d = bpy.data.lights.new("key", "SUN"); sun_d.energy = 3.0; sun_d.use_shadow = False
sun = bpy.data.objects.new("key", sun_d); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-15))   # หน้า-บน-ซ้ายของภาพ
w = bpy.data.worlds.new("REBORNER_World"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Strength"].default_value = 0.0   # ไม่ให้สีพื้นหลังไปย้อมแสงตัว

pts = [o.matrix_world @ Vector(c) for o in OBJS.values() for c in o.bound_box]
zmin, zmax = min(p.z for p in pts), max(p.z for p in pts); zc = (zmin + zmax) / 2
cam_d = bpy.data.cameras.new("FrontCam"); cam_d.type = "ORTHO"; cam_d.sensor_fit = "VERTICAL"
cam_d.ortho_scale = (zmax - zmin + float(ARGS.get("LINE", 0.012)) * 2) / FILL; cam_d.clip_start = 1; cam_d.clip_end = 30
cam = bpy.data.objects.new("FrontCam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
el = math.radians(EL)
cam.location = (0, -12 * math.cos(el), zc + 12 * math.sin(el)); cam.rotation_euler = (math.radians(90) - el, 0, 0)

for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
	try:
		sc.render.engine = eng; break
	except TypeError:
		pass
sc.eevee.taa_render_samples = 32; sc.render.filter_size = 1.0; sc.render.dither_intensity = 0.0   # ไม่ใส่ noise → พื้นเขียวเป็นสีเดียวทั้งภาพ
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1145, 1374, 100 * SCALE
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"; sc.render.film_transparent = True

# พื้นเขียว #00B140 วางใน compositor (สีตรงเป๊ะ ไม่ย้อมแสงตัวละคร) · ปิด compositor = พื้นโปร่ง
sc.use_nodes = True; ct = sc.node_tree; ct.nodes.clear()
rl = ct.nodes.new("CompositorNodeRLayers"); ao = ct.nodes.new("CompositorNodeAlphaOver"); comp = ct.nodes.new("CompositorNodeComposite")
ao.inputs[1].default_value = lin("#00b140"); ct.links.new(rl.outputs["Image"], ao.inputs[2]); ct.links.new(ao.outputs[0], comp.inputs["Image"])

def render(path, green):
	ct.links.clear()
	if green:
		ct.links.new(rl.outputs["Image"], ao.inputs[2]); ct.links.new(ao.outputs[0], comp.inputs["Image"])
	else:
		ct.links.new(rl.outputs["Image"], comp.inputs["Image"])
	sc.render.filepath = path; bpy.ops.render.render(write_still=True)

sfx = "" if SCALE == 1 else "_x%d" % SCALE
if BG in ("green", "both"):
	render(os.path.join(OUT, "REBORNER_MainCharacter%s.png" % sfx), True)
if BG in ("alpha", "both"):
	render(os.path.join(OUT, "REBORNER_MainCharacter%s_transparent.png" % sfx), False)
face = OBJS["Face"]
for i in range(DIRS):   # หมุนทั้งโครงรอบแกนตั้ง · มุมหลัง/หลังเฉียงซ่อนลายหน้า (แผ่นแบนจะโผล่พ้นขอบหัว)
	a = 2 * math.pi * i / DIRS; rig.rotation_euler = (0, 0, a); face.hide_render = math.cos(a) < -0.5
	name = ("front", "right", "back", "left")[i] if DIRS == 4 else "dir_%d" % i   # right = หันไปทางขวาของภาพ
	bpy.context.view_layer.update(); render(os.path.join(OUT, "%s%s.png" % (name, sfx)), False)
rig.rotation_euler = (0, 0, 0); face.hide_render = False; ct.links.clear()
ct.links.new(rl.outputs["Image"], ao.inputs[2]); ct.links.new(ao.outputs[0], comp.inputs["Image"])
sc.render.filepath = "//REBORNER_MainCharacter.png"
if BLEND:
	bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
print("rion_model ok · objects", len(OBJS), sorted(OBJS), "· height %.3f" % (zmax - zmin), "· ortho %.3f" % cam_d.ortho_scale)
