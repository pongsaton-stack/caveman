#!/usr/bin/env python3
"""tools/sprites/rion3d.py — Rion 3D (tools/blender/rion_model.py · ตามภาพ kwan 14 ต.ค. 2026) → ร่างภาพคม 8 ทิศ + สไปรต์ชีต

  python3 tools/sprites/rion3d.py            render ใหม่ผ่าน Blender (ต้องเปิด tools/blender/start_blender_mcp.sh ก่อน) แล้วจัดผืน
  python3 tools/sprites/rion3d.py --raw DIR  ข้าม render ใช้ dir_*.png ที่มีอยู่ใน DIR
  --page OUT.html                            สร้างหน้าเทสหมุนรอบตัว (ภาพฝังเป็น webp)

ผล: assets/sprites/rion3d_draft/dir_0–7.png (ผืน 512 ตัวสูง 464 เท้าแถว 504 กลาง x256 — เท่า rion_hires_draft)
    0 = หน้า · ทวนเข็ม: 2 = หันขวาของภาพ · 4 = หลัง · 6 = หันซ้ายของภาพ · ทุกทิศใช้สเกลเดียวกัน (วัดจากทิศหน้า)
    sheet_4dir.png (หน้า ขวา หลัง ซ้าย แถวเดียว) · sheet_8dir.png (4x2 ตามลำดับทิศ) · sheet.json (ขนาดช่อง ลำดับ จุดเท้า)
"""
import argparse, base64, io, json, os, subprocess, sys, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets/sprites/rion3d_draft")
REF = os.path.join(ROOT, "docs/art-bible/rion3d/rion_ref_2026-10-14.png")
CANVAS, HEIGHT, FOOT, N = 512, 464, 504, 8


def render(raw):
	subprocess.run([sys.executable, os.path.join(ROOT, "tools/blender/bl.py"), os.path.join(ROOT, "tools/blender/rion_model.py"),
		"OUT=" + raw, "BG=alpha", "DIRS=%d" % N], check=True)


def normalize(raw):
	ims = [Image.open(os.path.join(raw, "dir_%d.png" % i)).convert("RGBA") for i in range(N)]
	l, t, r, b = ims[0].getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
	k = HEIGHT / (b - t); cx = (l + r) / 2   # สเกล+จุดยึดจากทิศหน้า ใช้กับทุกทิศ (ตัวไม่ยืด/หดตอนหัน)
	out = []
	for i, im in enumerate(ims):
		sm = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
		cv = Image.new("RGBA", (CANVAS, CANVAS)); cv.alpha_composite(sm, (round(CANVAS / 2 - cx * k), round(FOOT - b * k)))
		cv.save(os.path.join(OUT, "dir_%d.png" % i)); out.append(cv)
	return out


def sheets(ims):
	"""สไปรต์ชีตพื้นโปร่ง ช่องละ 512 · ลำดับและจุดเท้าเขียนใน sheet.json ให้ตัวตัดเฟรมฝั่งเกมอ่าน"""
	four = [0, 2, 4, 6]
	s4 = Image.new("RGBA", (CANVAS * 4, CANVAS))
	for c, i in enumerate(four):
		s4.alpha_composite(ims[i], (CANVAS * c, 0))
	s4.save(os.path.join(OUT, "sheet_4dir.png"))
	s8 = Image.new("RGBA", (CANVAS * 4, CANVAS * 2))
	for i, im in enumerate(ims):
		s8.alpha_composite(im, (CANVAS * (i % 4), CANVAS * (i // 4)))
	s8.save(os.path.join(OUT, "sheet_8dir.png"))
	json.dump({"cell": CANVAS, "foot_y": FOOT, "center_x": CANVAS // 2, "body_h": HEIGHT,
		"sheet_4dir": ["front", "right", "back", "left"], "sheet_8dir": ["front", "front_right", "right", "back_right", "back", "back_left", "left", "front_left"],
		"note": "right = หันไปทางขวาของภาพ · 8 ทิศเรียงซ้าย→ขวา บน→ล่าง"}, open(os.path.join(OUT, "sheet.json"), "w"), ensure_ascii=False, indent=1)


def uri(im, q=90):
	bio = io.BytesIO(); im.save(bio, "WEBP", quality=q); return "data:image/webp;base64," + base64.b64encode(bio.getvalue()).decode()


def page(ims, path):
	ref = Image.open(REF).convert("RGB"); ref.thumbnail((480, 576))
	tpl = open(os.path.join(ROOT, "tools/web/rion3d_test.tpl.html"), encoding="utf-8").read()
	open(path, "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps({"dirs": [uri(i) for i in ims], "ref": uri(ref, 85)})))


if __name__ == "__main__":
	ap = argparse.ArgumentParser(); ap.add_argument("--raw"); ap.add_argument("--page"); a = ap.parse_args()
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, ".gdignore"), "a").close()
	raw = a.raw or tempfile.mkdtemp(prefix="rion3d_")
	if not a.raw:
		render(raw)
	ims = normalize(raw); sheets(ims)
	print("rion3d:", N, "ทิศ →", OUT)
	if a.page:
		page(ims, a.page); print("หน้าเทส →", a.page, os.path.getsize(a.page), "bytes")
