# tools/blender/rion_scene.py — รันใน Blender (ผ่าน tools/blender/bl.py): ปั้น Rion แบบ chibi ตามภาพอ้างอิงของ kwan (docs/art-bible/rion3d/rion_ref_2026-10-14.png)
# แล้ว render รอบตัว 8 ทิศ (หน้า → ขวาของภาพ ... ทวนเข็ม) · ARGS: OUT=<โฟลเดอร์ผลดิบ> SIZE=<px> N=<จำนวนทิศ> PREVIEW=<px ภาพหน้าตรงใหญ่ 0 = ไม่ทำ>
# ปั้นจาก primitive ทั้งหมด (ไม่ใช้โมเดลสำเร็จรูป) · ตัวสูง 2 หน่วย · หันหน้าไปทาง -Y · ซ้ายของตัวละคร = +X
import bpy, bmesh, math, os

OUT = ARGS["OUT"]; SIZE = int(ARGS.get("SIZE", 256)); N = int(ARGS.get("N", 8)); PREVIEW = int(ARGS.get("PREVIEW", 0))
os.makedirs(OUT, exist_ok=True)

for o in list(bpy.data.objects):
	bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
	for m in list(coll):
		coll.remove(m)

MATS = {}
def mat(name, hexcol):
	if name not in MATS:
		c = tuple(int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5))
		m = bpy.data.materials.new(name); m.diffuse_color = (*[x ** 2.2 for x in c], 1.0); m.roughness = 0.9; MATS[name] = m
	return MATS[name]

# สีจากภาพอ้างอิง
SKIN, HAIR, CAP, GOLD, LENS, SHIRT, TIE, SHORTS, BELT, BAG, BOOT, SOLE, SOCK, EYE, DARK, BLUSH = (
	"#f8d6b8", "#7a4626", "#2f62c6", "#d8992e", "#4f8fe0", "#f4f3ee", "#2f62c6", "#2f6cd0", "#7a4a2a", "#8a5530", "#86562f", "#e6cfa0", "#f4f3ee",
	"#5a3418", "#2a1a14", "#f2a9a0")

PARTS = []; FACE = []
def part(kind, loc, scale, col, rot=(0, 0, 0), name="", **kw):
	if kind == "box":
		bpy.ops.mesh.primitive_cube_add(size=1)
	elif kind == "cyl":
		bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("v", 24), radius=0.5, depth=1)
	elif kind == "cone":
		bpy.ops.mesh.primitive_cone_add(vertices=kw.get("v", 12), radius1=kw.get("r1", 0.5), radius2=kw.get("r2", 0.0), depth=1)
	elif kind == "sph":
		bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5)
	elif kind == "torus":
		bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=kw.get("minor", 0.12), major_segments=32, minor_segments=8)
	o = bpy.context.active_object
	o.location = loc; o.scale = scale; o.rotation_euler = [math.radians(a) for a in rot]
	o.data.materials.append(mat(col, col)); bpy.ops.object.shade_smooth()
	if kw.get("cut"):   # ลบจุดยอดตามเงื่อนไข (พิกัดในวัตถุ ก่อนย่อขยาย) — ทำหมวก/ผมเป็นเปลือกครึ่งลูก
		bm = bmesh.new(); bm.from_mesh(o.data)
		bmesh.ops.delete(bm, geom=[v for v in bm.verts if kw["cut"](v.co)], context="VERTS"); bm.to_mesh(o.data); bm.free()
	if kw.get("face"):
		o["layer"] = kw["face"]
	(FACE if kw.get("face") else PARTS).append(o)   # รายละเอียดหน้าแยกชิ้น ไม่ใส่เส้นขอบ (ไม่งั้นปาก/จมูกบวมเป็นก้อนดำ)
	return o

# ── ขาและรองเท้าบูท ──
for s in (-1, 1):
	x = 0.13 * s
	part("box", (x, -0.04, 0.03), (0.2, 0.3, 0.06), SOLE)                       # พื้นรองเท้าสีทราย
	part("sph", (x, -0.05, 0.11), (0.21, 0.32, 0.17), BOOT)                     # หัวบูท
	part("cyl", (x, 0.0, 0.2), (0.17, 0.17, 0.16), BOOT)                        # ข้อบูท
	part("box", (x, -0.085, 0.2), (0.07, 0.02, 0.1), GOLD)                      # สายรัดทอง
	part("cyl", (x, 0.0, 0.31), (0.13, 0.13, 0.08), SOCK)                       # ถุงเท้า
	part("cyl", (x, 0.0, 0.41), (0.1, 0.1, 0.16), SKIN)                         # ขา
	part("cyl", (x, 0.0, 0.53), (0.21, 0.21, 0.16), SHORTS)                     # ขากางเกงขาสั้น
	part("cyl", (x, 0.0, 0.46), (0.22, 0.22, 0.03), "#2a5cb8")                  # ปลายขาพับ
part("box", (0, 0, 0.66), (0.42, 0.26, 0.14), SHORTS)                           # สะโพก
part("cyl", (0, 0, 0.735), (0.44, 0.28, 0.045), BELT)                           # เข็มขัด
part("box", (0, -0.14, 0.735), (0.08, 0.02, 0.045), GOLD)                       # หัวเข็มขัด

# ── ลำตัว เสื้อเชิ้ตขาว เนคไทน้ำเงิน ──
part("cone", (0, 0, 0.88), (0.42, 0.28, 0.27), SHIRT, r1=0.5, r2=0.42, v=24)
part("box", (0, -0.135, 0.86), (0.055, 0.02, 0.17), TIE)                        # ตัวเนคไท
part("cone", (0, -0.135, 0.765), (0.055, 0.02, 0.04), TIE, r1=0.5, r2=0.0, v=4, rot=(180, 0, 0))   # ปลายแหลม
part("box", (0, -0.14, 0.96), (0.06, 0.03, 0.04), TIE)                          # ปมเนคไท
for s in (-1, 1):
	part("box", (0.06 * s, -0.12, 0.99), (0.08, 0.03, 0.04), SHIRT, rot=(0, 0, -25 * s))   # ปกเสื้อ
part("cyl", (0, 0, 1.03), (0.1, 0.1, 0.08), SKIN)                               # คอ

# ── แขน มือ นาฬิกา ──
for s in (-1, 1):
	part("sph", (0.21 * s, 0, 0.95), (0.17, 0.17, 0.15), SHIRT)                 # แขนเสื้อสั้น
	part("cyl", (0.24 * s, 0, 0.82), (0.085, 0.085, 0.2), SKIN, rot=(0, 8 * s, 0))   # แขน
	part("sph", (0.255 * s, -0.01, 0.69), (0.12, 0.11, 0.12), SKIN)              # กำมือ
part("cyl", (0.252, 0, 0.745), (0.1, 0.1, 0.04), "#2f62c6")                    # นาฬิกาข้อมือซ้าย (ขวาของภาพ)
part("box", (0.25, -0.05, 0.745), (0.04, 0.01, 0.03), "#4fa060")                # หน้าปัด

# ── เป้หลัง + สาย ──
part("box", (0, 0.2, 0.86), (0.4, 0.2, 0.34), BAG)
part("box", (0, 0.3, 0.86), (0.3, 0.06, 0.2), "#7a4826")                       # ช่องหน้าของเป้ (ด้านหลังตัว)
for s in (-1, 1):
	part("box", (0.24 * s, 0.17, 0.82), (0.08, 0.14, 0.18), BAG)               # กระเป๋าข้าง
	part("box", (0.29 * s, 0.17, 0.83), (0.01, 0.06, 0.05), GOLD)              # หัวเข็มกระเป๋าข้าง
	part("box", (0.12 * s, -0.135, 0.89), (0.05, 0.02, 0.26), BAG)             # สายสะพายหน้าอก
	part("box", (0.12 * s, -0.15, 0.86), (0.07, 0.02, 0.05), GOLD)             # หัวเข็มสาย
	part("box", (0.12 * s, -0.01, 1.0), (0.05, 0.27, 0.03), BAG)               # สายข้ามบ่า

# ── หัว ── สัดส่วนวัดจากภาพอ้างอิง (ยอดหมวก→คาง = 1): ขอบปีกหมวก .51 · คิ้ว .63 · ตา .71–.87 · ปาก .95
HZ = 1.33
part("sph", (0, 0, HZ), (0.72, 0.64, 0.66), SKIN)                           # หน้า
for s in (-1, 1):
	part("sph", (0.355 * s, 0.02, HZ - 0.1), (0.08, 0.06, 0.11), SKIN)          # หู
# ผม: เปลือกครึ่งหลัง (ตัดครึ่งหน้าล่างออก เห็นหน้าและหู) + หน้าม้าแหลม + จอนข้าง + ปอยชี้ออกข้าง
part("sph", (0, 0.01, HZ), (0.77, 0.71, 0.72), HAIR, cut=lambda c: c.y < 0.02 and c.z < 0.12)
for x, ln, tilt in ((-0.25, 0.14, 28), (-0.15, 0.17, 14), (-0.05, 0.2, 4), (0.04, 0.24, -6), (0.14, 0.18, -16), (0.25, 0.14, -28)):
	part("cone", (x, -0.3, HZ + 0.07 - ln / 2), (0.15, 0.1, ln), HAIR, rot=(188, tilt, 0), v=6)   # หน้าม้าแหลมลงมา
for s in (-1, 1):
	part("cone", (0.31 * s, -0.12, HZ - 0.07), (0.1, 0.08, 0.24), HAIR, rot=(180, -8 * s, 0), v=6)   # จอนหน้าหู
	for z, ln, a in ((HZ + 0.03, 0.2, 75), (HZ - 0.08, 0.16, 105), (HZ - 0.2, 0.12, 130)):
		part("cone", (0.37 * s, 0.06, z), (0.11, 0.09, ln), HAIR, rot=(0, a * s, 0), v=6)   # ปอยข้างชี้ออก
	part("cone", (0.12 * s, 0.33, HZ - 0.22), (0.12, 0.08, 0.16), HAIR, rot=(-170, 0, 0), v=6)   # ปอยท้ายทอย
# หน้า: ตาโต (ขอบเข้มหนาด้านบน → ขาว → ม่านตาน้ำตาล → รูม่านตา → ประกาย) · คิ้วเข้มเฉียง · ปากยิ้ม · แก้มชมพู
EZ = HZ - 0.15
for s in (-1, 1):   # แผ่นบางวางชิดผิวหัว เอียงตามความโค้ง (หันข้าง/หันหลังแล้วไม่ลอยพ้นหัว)
	x = 0.125 * s; R = (22, 0, 12 * s)
	part("sph", (x, -0.275, EZ + 0.012), (0.13, 0.012, 0.175), DARK, rot=R, face=1)
	part("sph", (x * 1.01, -0.281, EZ), (0.11, 0.012, 0.15), "#ffffff", rot=R, face=2)
	part("sph", (x * 0.97, -0.287, EZ - 0.008), (0.085, 0.012, 0.125), EYE, rot=R, face=3)
	part("sph", (x * 0.97, -0.292, EZ - 0.01), (0.05, 0.012, 0.075), DARK, rot=R, face=4)
	part("sph", (x * 0.97 + 0.02, -0.298, EZ + 0.025), (0.034, 0.008, 0.04), "#ffffff", rot=R, face=5)
	part("box", (0.13 * s, -0.325, HZ - 0.035), (0.11, 0.03, 0.026), DARK, rot=(0, 20 * s, 18 * s), face=4)   # คิ้วเฉียงมุ่งมั่น
	part("sph", (0.2 * s, -0.185, HZ - 0.215), (0.075, 0.012, 0.04), BLUSH, rot=(40, 0, 45 * s), face=1)
part("sph", (0, -0.262, HZ - 0.205), (0.012, 0.01, 0.012), DARK, face=1)                   # จมูกจุด
part("torus", (0, -0.24, HZ - 0.235), (0.06, 0.06, 0.06), DARK, rot=(80, 0, 0), minor=0.2, cut=lambda c: c.y > -0.05, face=1)   # ยิ้ม (ครึ่งล่างของวง)
# หมวกแก๊ปน้ำเงินทรงสูง (ครึ่งลูกบน) + ปีกหน้าสั้นโค้ง + ปุ่มบน
part("sph", (0, 0.0, HZ + 0.04), (0.8, 0.76, 0.78), CAP, cut=lambda c: c.z < 0.0)
part("sph", (0, -0.17, HZ + 0.05), (0.68, 0.62, 0.05), CAP, rot=(-6, 0, 0), cut=lambda c: c.y > -0.05)
part("sph", (0, 0.0, HZ + 0.43), (0.09, 0.09, 0.06), CAP)
# แว่นกันลมบนหมวก: สายน้ำตาลรอบหมวก + กรอบทอง 2 วง + เลนส์ฟ้า + สะพานทอง
GZ = HZ + 0.22
part("cyl", (0, 0.0, GZ), (0.73, 0.69, 0.05), "#8a5a2a")
for s in (-1, 1):
	x = 0.135 * s
	part("torus", (x, -0.325, GZ), (0.2, 0.2, 0.2), GOLD, rot=(64, 0, 0), minor=0.14)
	part("cyl", (x, -0.322, GZ), (0.18, 0.18, 0.02), LENS, rot=(64, 0, 0))
	part("sph", (x + 0.03, -0.345, GZ + 0.02), (0.05, 0.01, 0.03), "#d8ecff")
	part("box", (0.25 * s, -0.25, GZ), (0.05, 0.06, 0.07), GOLD, rot=(0, 0, -40 * s))   # ข้อต่อสายข้าง
part("box", (0, -0.35, GZ), (0.07, 0.03, 0.05), GOLD)

# รวมเป็นชิ้นเดียว → หมุนรอบตัวได้
bpy.ops.object.select_all(action="DESELECT")
for o in PARTS:
	o.select_set(True)
bpy.context.view_layer.objects.active = PARTS[0]
bpy.ops.object.join()
rion = bpy.context.active_object; rion.name = "Rion3D"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # ชิ้นแรก (บูท) ถูกย่อ/ย้าย → ล้างออก: เส้นขอบไม่โดนย่อตาม + หมุนรอบแกนกลางตัว
bpy.ops.object.select_all(action="DESELECT")
for o in FACE:
	o.select_set(True)
bpy.context.view_layer.objects.active = FACE[0]; bpy.ops.object.join()
face = bpy.context.active_object; face.name = "Rion3D_face"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); face.parent = rion   # หมุนตามตัว
# เส้นขอบแบบการ์ตูน: เปลือกหนาออกนอกตัว กลับด้านหน้าผิว สีน้ำตาลเข้ม + ซ่อนด้านที่หันเข้ากล้อง (backface culling) → เห็นแค่ขอบรอบตัว
ink = bpy.data.materials.new("ink"); ink.use_nodes = True; ink.use_backface_culling = True
nt = ink.node_tree; nt.nodes.clear()
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.022, 0.011, 0.007, 1)
nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
rion.data.materials.append(ink)
sol = rion.modifiers.new("outline", "SOLIDIFY"); sol.thickness = float(ARGS.get("LINE", 0.014)); sol.offset = 1.0
sol.use_flip_normals = True; sol.material_offset = len(rion.data.materials) - 1

# แสงเงาแบบการ์ตูน 2 ระดับ (cel): Diffuse → Shader to RGB → ไล่สีแบบขั้น → คูณสีพื้น → Emission (สีไม่เพี้ยนตามแสง)
SHADOW = (0.70, 0.66, 0.82, 1)   # เงาอมม่วงฟ้า
FLAT = {"#ffffff", EYE, DARK, BLUSH}   # ตา/คิ้ว/แก้ม ไม่ลงเงา (ลายวาดบนหน้า)
for m in MATS.values():
	base = tuple(m.diffuse_color); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
	dif = nt.nodes.new("ShaderNodeBsdfDiffuse"); s2r = nt.nodes.new("ShaderNodeShaderToRGB")
	ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
	ramp.color_ramp.elements[0].color = (1, 1, 1, 1) if m.name in FLAT else SHADOW; ramp.color_ramp.elements[1].position = float(ARGS.get("TH", 0.15)); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
	mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1.0
	mix.inputs[6].default_value = base
	em = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
	nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs[0], ramp.inputs[0])
	nt.links.new(ramp.outputs[0], mix.inputs[7]); nt.links.new(mix.outputs[2], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs["Surface"])

sc = bpy.context.scene
try:
	sc.render.engine = "BLENDER_EEVEE"
except TypeError:
	sc.render.engine = "BLENDER_EEVEE_NEXT"
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
sc.eevee.taa_render_samples = int(ARGS.get("AA", 16)); sc.render.film_transparent = True; sc.render.image_settings.color_mode = "RGBA"
sc.render.filter_size = 1.0
if sc.world is None:
	sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs["Strength"].default_value = 0.0
for o in [o for o in bpy.data.objects if o.type == "LIGHT"]:
	bpy.data.objects.remove(o, do_unlink=True)
sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.energy = 3.0
sun = bpy.data.objects.new("sun", sun_d); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-15))   # แสงจากหน้า-บน-ซ้ายของภาพ คงที่ต่อกล้อง
cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam_d.clip_start = 5; cam_d.clip_end = 15; cam_d.ortho_scale = 2.2
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
el = math.radians(12)   # มองเฉียงลงนิดเดียว (ตัวละครเกมมุมเกือบตรง)
cam.location = (0, -10 * math.cos(el), 1.0 + 10 * math.sin(el)); cam.rotation_euler = (math.radians(90) - el, 0, 0)

def shot(path, size):
	sc.render.resolution_x = sc.render.resolution_y = size; sc.render.filepath = path
	bpy.ops.render.render(write_still=True)

for i in range(N):   # 0 = หน้า · ทวนเข็ม: 2 = หันขวาของภาพ (ซ้ายของตัว) · 4 = หลัง · 6 = หันซ้ายของภาพ
	rion.rotation_euler = (0, 0, 2 * math.pi * i / N)
	face.hide_render = math.cos(2 * math.pi * i / N) < -0.5   # มุมหลัง/หลังเฉียง: ซ่อนตา-ปาก (แผ่นแบนจะโผล่พ้นขอบหัว)
	shot(os.path.join(OUT, "dir_%d.png" % i), SIZE)
if PREVIEW:
	rion.rotation_euler = (0, 0, 0); face.hide_render = False; shot(os.path.join(OUT, "preview.png"), PREVIEW)
print("rion3d rendered", N, "dirs", "verts", len(rion.data.vertices))
