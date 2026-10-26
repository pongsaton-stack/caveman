#!/usr/bin/env python3
"""tools/sprites/rion_pose_refs.py — ภาพอ้างอิงท่าจากหุ่น 3D สำหรับแนบตอนเจนท่า Rion ที่ยังขาด (kwan 14 ต.ค. 2026 ลอง ActionForge → เลือก "1")

  python3 tools/sprites/rion_pose_refs.py <mannequin_rest_pose.glb>
      ต้องเปิด Blender ก่อน (start_blender_mcp.sh ที่ราก repo) และ Blender ต้องมี numpy (apt python3-numpy) ถึงนำเข้า glb ได้
      หุ่น = ปุ่ม "Character only (rest pose)" ใน https://actionforge.app (โครง+หุ่น Quaternius CC0)
      → docs/art-bible/rion_hires/pose_refs/<ท่า>_<มุม>.png + pose_refs_v1.png (ชีตรวม 3 ท่า ลำดับเดียวกับคำสั่งเจน)

ท่า = จุดที่ปลายกระดูกเล็งไป (พิกัดโลก · หุ่นหันหน้า -Y · แขนท่า T ตาม ±X) · มุม 0 = กล้อง +X หุ่นหันซ้ายของภาพ · 180 = หันขวา
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs/art-bible/rion_hires/pose_refs")
POSES = [   # (ชื่อ, ป้าย, มุมกล้อง, ลดตัว, จุดเล็ง)
	("right", "#4 RIGHT · standing, facing right", "180", 0, {
		"upperarm_l": [0.25, 0.07, 1.13], "lowerarm_l": [0.27, 0.03, 0.87], "hand_l": [0.27, 0.02, 0.80],
		"upperarm_r": [-0.25, 0.07, 1.13], "lowerarm_r": [-0.27, 0.03, 0.87], "hand_r": [-0.27, 0.02, 0.80]}),
	("pray", "#10 PRAY · palms together, facing left", "0", 0, {
		"upperarm_l": [0.29, -0.10, 1.17], "lowerarm_l": [0.012, -0.31, 1.25], "hand_l": [0.005, -0.33, 1.42],
		"upperarm_r": [-0.29, -0.10, 1.17], "lowerarm_r": [-0.012, -0.31, 1.25], "hand_r": [-0.005, -0.33, 1.42], "Head": [0, -0.06, 1.72]}),
	("kneel", "#8 KNEEL · one knee down, hand on ground, facing left", "0", -0.48, {
		"spine_01": [0, -0.06, 0.62], "spine_02": [0, -0.20, 0.76], "spine_03": [0, -0.36, 0.78], "neck_01": [0, -0.50, 0.80], "Head": [0, -0.58, 0.74],
		"thigh_l": [0.12, -0.40, 0.42], "calf_l": [0.12, -0.40, 0.0], "foot_l": [0.12, -0.56, 0.0],
		"thigh_r": [-0.10, 0.08, 0.04], "calf_r": [-0.10, 0.50, 0.03], "foot_r": [-0.10, 0.58, -0.04],
		"upperarm_l": [0.24, -0.50, 0.40], "lowerarm_l": [0.24, -0.62, 0.02], "hand_l": [0.24, -0.72, -0.02],
		"upperarm_r": [-0.12, -0.34, 0.56], "lowerarm_r": [0.02, -0.44, 0.48], "hand_r": [0.06, -0.48, 0.46]}),
]

def main():
	glb = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True); tiles = []
	for name, label, view, dz, pose in POSES:
		base = os.path.join(OUT, name)
		subprocess.run([sys.executable, os.path.join(ROOT, "tools/blender/bl.py"), os.path.join(ROOT, "tools/blender/pose_ref_scene.py"),
			"GLB=" + glb, "OUT=" + base, "POSE=" + json.dumps(pose), "VIEWS=" + view, "DZ=%s" % dz], check=True)
		tiles.append((Image.open("%s_%s.png" % (base, view)).convert("RGB"), label))
	w, h = tiles[0][0].size; sheet = Image.new("RGB", (w * len(tiles), h + 60), (34, 38, 48)); d = ImageDraw.Draw(sheet)
	try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
	except OSError: font = ImageFont.load_default()
	for i, (im, label) in enumerate(tiles):
		sheet.paste(im, (i * w, 60)); d.text((i * w + 16, 18), label, fill=(240, 240, 240), font=font)
	sheet.save(os.path.join(OUT, "pose_refs_v1.png")); print("ชีต →", os.path.join(OUT, "pose_refs_v1.png"), sheet.size)

if __name__ == "__main__":
	main()
