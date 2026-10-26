# tools/blender/weapons_scene.py — รันใน Blender (ผ่าน tools/blender/bl.py): ปั้นอาวุธตัวอย่าง 6 ชิ้นจาก primitive แล้ว render หมุนรอบตัว
# ARGS: OUT=<โฟลเดอร์ผลดิบ> N=<จำนวนมุม> SIZE=<px>
# ขนาดชิ้นอิงความยาวของจริงโดยประมาณ แล้วย่อให้พอดีกรอบเท่ากันทุกชิ้น (ภาพหน้าเทส ไม่ใช่ค่าเกม)
import bpy, math, os
from mathutils import Vector

OUT = ARGS["OUT"]; N = int(ARGS.get("N", 16)); SIZE = int(ARGS.get("SIZE", 96))
os.makedirs(OUT, exist_ok=True)

def clear():
	for o in list(bpy.data.objects):
		bpy.data.objects.remove(o, do_unlink=True)
	for m in list(bpy.data.meshes):
		bpy.data.meshes.remove(m)
	for m in list(bpy.data.materials):
		bpy.data.materials.remove(m)

MATS = {}
def mat(name, rgb, metal=0.0, rough=0.6):
	if name in MATS:
		return MATS[name]
	m = bpy.data.materials.new(name); m.diffuse_color = (*rgb, 1.0); m.metallic = 0.0; m.roughness = rough   # Workbench: โลหะ = ดำ จึงไม่ใช้ metallic (สีอ่อนแทน)
	MATS[name] = m
	return m

FAT = 1.8   # หน้าตัดหนากว่าของจริง (แกน x/y) — ย่อเหลือ 48px แล้วยังเห็นรูปทรง
def part(kind, loc, scale, m, rot=(0, 0, 0), **kw):
	loc = (loc[0] * FAT, loc[1] * FAT, loc[2]); scale = (scale[0] * FAT, scale[1] * FAT, scale[2])
	if kind == "box":
		bpy.ops.mesh.primitive_cube_add(size=1)
	elif kind == "cyl":
		bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("v", 16), radius=0.5, depth=1)
	elif kind == "cone":
		bpy.ops.mesh.primitive_cone_add(vertices=kw.get("v", 16), radius1=kw.get("r1", 0.5), radius2=kw.get("r2", 0.0), depth=1)
	elif kind == "sph":
		bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.5)
	o = bpy.context.active_object
	o.location = loc; o.scale = scale; o.rotation_euler = [math.radians(a) for a in rot]
	o.data.materials.append(m)
	if kw.get("smooth"):
		bpy.ops.object.shade_smooth()
	return o

def join(name):
	objs = [o for o in bpy.data.objects if o.type == "MESH"]
	bpy.ops.object.select_all(action="DESELECT")
	for o in objs:
		o.select_set(True)
	bpy.context.view_layer.objects.active = objs[0]
	bpy.ops.object.join()
	o = bpy.context.active_object; o.name = name
	bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
	o.location = (0, 0, 0)
	d = max(o.dimensions)
	o.scale = [s * 2.0 / d for s in o.scale]   # ยาวสุด = 2 หน่วยทุกชิ้น
	return o

# ── อาวุธ: แกนยาวตาม z (ปลายใช้งานขึ้นบน) ──
def knife():   # SL-1 มีดทำครัว ด้ามไม้ ใบบิ่นนิดๆ
	steel = mat("steel", (0.82, 0.85, 0.9)); wood = mat("wood", (0.45, 0.27, 0.13)); pin = mat("pin", (0.85, 0.75, 0.5), 0.8)
	part("box", (0, 0, 0.75), (0.32, 0.03, 1.2), steel)
	part("cone", (0.0, 0, 1.45), (0.32, 0.03, 0.3), steel, v=4, r1=0.5, r2=0.0)
	part("box", (0, 0, -0.25), (0.22, 0.12, 0.8), wood)
	for z in (-0.45, -0.1):
		part("cyl", (0, 0, z), (0.07, 0.07, 0.3), pin, rot=(90, 0, 0), v=8)

def bat():     # CR-2 ไม้เบสบอลอลูมิเนียม ด้ามพันผ้า
	alu = mat("alu", (0.66, 0.74, 0.84)); grip = mat("grip", (0.2, 0.18, 0.2)); cap = mat("cap", (0.3, 0.3, 0.35), 0.7)
	part("cone", (0, 0, 0.55), (1, 1, 1.9), alu, v=24, r1=0.07, r2=0.17, smooth=True)
	part("sph", (0, 0, 1.5), (0.34, 0.34, 0.2), alu, smooth=True)
	part("cyl", (0, 0, -0.65), (0.15, 0.15, 0.6), grip, v=16)
	part("cyl", (0, 0, -1.0), (0.24, 0.24, 0.08), cap, v=16)

def pencil():  # PC-1 ดินสอเหลือง มียางลบ เหลาแหลม
	yel = mat("yel", (0.95, 0.75, 0.15)); wood = mat("pwood", (0.9, 0.72, 0.5)); lead = mat("lead", (0.15, 0.15, 0.17)); band = mat("band", (0.75, 0.72, 0.65), 0.8); eras = mat("eras", (0.95, 0.5, 0.55))
	part("cyl", (0, 0, 0), (0.22, 0.22, 2.2), yel, v=6)
	part("cone", (0, 0, 1.3), (0.22, 0.22, 0.4), wood, v=6, r1=0.5, r2=0.12)
	part("cone", (0, 0, 1.55), (0.06, 0.06, 0.12), lead, v=6, r1=0.5, r2=0.0)
	part("cyl", (0, 0, -1.17), (0.23, 0.23, 0.16), band, v=12)
	part("cyl", (0, 0, -1.35), (0.21, 0.21, 0.22), eras, v=12, smooth=True)

def sling():   # ST-1 หนังสติ๊กกิ่งไม้ + ยางวง
	br = mat("branch", (0.42, 0.26, 0.12)); rub = mat("rubber", (0.75, 0.25, 0.2)); pouch = mat("pouch", (0.35, 0.22, 0.15))
	part("cyl", (0, 0, -0.5), (0.13, 0.13, 1.1), br, v=10)
	pouch_at = Vector((0, -0.3, 0.55))
	for s in (-1, 1):
		part("cyl", (s * 0.18, 0, 0.35), (0.11, 0.11, 0.85), br, rot=(0, s * 25, 0), v=10)
		tip = Vector((s * 0.36, 0, 0.72))   # ปลายง่าม (ก่อนคูณ FAT ใน part)
		mid = (tip + pouch_at) / 2; d = pouch_at - tip
		o = part("cyl", tuple(mid), (0.035, 0.035, d.length), rub, v=6)
		o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((d.x * FAT, d.y * FAT, d.z)).to_track_quat("Z", "Y")
	part("box", tuple(pouch_at), (0.16, 0.06, 0.12), pouch)

def stapler():  # DV-1 ที่เย็บกระดาษตั้งโต๊ะ (วางนอน หัวขึ้นบน)
	body = mat("stap", (0.7, 0.12, 0.12), 0.2, 0.4); metal = mat("smetal", (0.7, 0.72, 0.75), 0.9, 0.3); base = mat("sbase", (0.15, 0.15, 0.17))
	part("box", (0, -0.05, 0), (0.42, 0.18, 2.0), base)
	part("box", (0, 0.2, 0.1), (0.38, 0.22, 1.8), body)
	part("box", (0, 0.06, 0.95), (0.3, 0.06, 0.2), metal)
	part("cyl", (0, 0.1, -0.85), (0.12, 0.12, 0.46), metal, rot=(0, 90, 0), v=10)

def glove():   # BD-1 ถุงมือผ้าทำสวน เปื้อนดิน
	cloth = mat("cloth", (0.86, 0.8, 0.66)); dirt = mat("dirt", (0.5, 0.4, 0.28)); cuff = mat("cuff", (0.35, 0.55, 0.4))
	part("sph", (0, 0, 0), (0.75, 0.32, 0.85), cloth, smooth=True)
	for i, (x, h) in enumerate([(-0.27, 0.62), (-0.09, 0.72), (0.09, 0.7), (0.27, 0.58)]):
		part("cyl", (x, 0, 0.42 + h / 2), (0.17, 0.17, h), cloth if i % 2 else dirt, v=10, smooth=True)
	part("cyl", (0.48, 0, 0.1), (0.17, 0.17, 0.55), cloth, rot=(0, -50, 0), v=10, smooth=True)
	part("cyl", (0, 0, -0.55), (0.72, 0.36, 0.45), cuff, v=16)

WEAPONS = [("SL-1", knife), ("CR-2", bat), ("PC-1", pencil), ("ST-1", sling), ("DV-1", stapler), ("BD-1", glove)]

def setup_scene():
	sc = bpy.context.scene
	sc.render.engine = "BLENDER_WORKBENCH"
	sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
	sc.display.shading.show_cavity = True; sc.display.shading.cavity_type = "WORLD"
	sc.display.render_aa = "OFF"   # ขอบคม ไม่เบลอ — ย่อเป็นพิกเซลทีหลัง
	sc.render.film_transparent = True
	sc.render.resolution_x = sc.render.resolution_y = SIZE
	sc.render.image_settings.color_mode = "RGBA"
	cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.25
	cam = bpy.data.objects.new("cam", cam_data); sc.collection.objects.link(cam); sc.camera = cam
	el = math.radians(28)   # มองเฉียงลง 28°
	cam.location = (0, -10 * math.cos(el), 10 * math.sin(el))
	cam.rotation_euler = (math.radians(90) - el, 0, 0)

out = []
for wid, build in WEAPONS:
	clear(); MATS.clear()
	build()
	o = join(wid)
	o.rotation_mode = "ZXY"
	setup_scene()
	for i in range(N):
		# เอียงอาวุธ 35° (แบบถือ) แล้วหมุนรอบแกนตั้งของโลก
		o.rotation_euler = (0, math.radians(35), 2 * math.pi * i / N)
		bpy.context.scene.render.filepath = os.path.join(OUT, f"{wid}_{i:02d}.png")
		bpy.ops.render.render(write_still=True)
	out.append(wid)
print("rendered", len(out), "x", N, out)
