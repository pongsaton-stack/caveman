# tools/blender/pose_ref_scene.py — จัดท่าหุ่น ActionForge (โครง+ท่า Quaternius · CC0) ด้วย DAMPED_TRACK ไปจุดเป้าหมาย แล้ว render ภาพอ้างอิงท่า · ARGS: GLB OUT POSE(json) VIEWS DZ · เรียกผ่าน tools/sprites/rion_pose_refs.py
import bpy, math, json
from mathutils import Vector
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=ARGS['GLB'])
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm.location.z = float(ARGS.get('DZ', 0))   # ลดตัวลง (ท่าคุกเข่า) · จุดเป้าหมายเป็นพิกัดโลกหลังลดแล้ว
for o in bpy.data.objects:
    if o.name.startswith('Icosphere'): o.hide_render = True
P = json.loads(ARGS['POSE'])   # {bone: [x,y,z] จุดที่ปลายกระดูกเล็งไป} · ลำดับ = ลำดับในพจนานุกรม
for name, tgt in P.items():
    e = bpy.data.objects.new('t_' + name, None); e.location = Vector(tgt); bpy.context.scene.collection.objects.link(e)
    c = arm.pose.bones[name].constraints.new('DAMPED_TRACK'); c.target = e
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'; sc.display.shading.show_cavity = True
sc.render.resolution_x, sc.render.resolution_y = 700, 900; sc.render.film_transparent = False
sc.world = sc.world or bpy.data.worlds.new('W'); sc.display.shading.background_type = 'VIEWPORT'; sc.display.shading.background_color = (0.13, 0.15, 0.19)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.05
for v in ARGS['VIEWS'].split(','):
    az = math.radians(float(v)); d = 6   # az 0 = กล้องอยู่ +X (หุ่นหันซ้ายของภาพ) · 90 = กล้อง -Y (หน้าตรง) · 180 = หันขวา
    cam.location = (d * math.cos(az), -d * math.sin(az), 0.9 + 0.6); look = Vector((0, 0, 0.82)) - cam.location
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = ARGS['OUT'] + '_%s.png' % v; bpy.ops.render.render(write_still=True)
print('ok')
