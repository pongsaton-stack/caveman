#!/usr/bin/env python3
"""tools/sprites/rion_poses.py — ตัดท่า Rion จากชีตท่าที่ kwan เจน (rion_pose_sheet_v1.png · 14 ต.ค. 2026) เป็นร่างภาพคม

kwan สั่ง "เอาที่ใช้ได้มาทำก่อน" → 8 ท่าที่ผ่านการดู: หลัง · หันซ้าย · ง้างมีด · ฟาด · โดนตี · นอนล้ม · ผลักปล่อยเวทย์ · วิ่ง
ไม่เอา: หันหน้า (ใช้ต้นฉบับแทน) · หันขวา (พลิกจากหันซ้าย นาฬิกาผิดข้าง) · พนมมือ (หันหน้าตรง) · ทรุดเข่า (คลานสี่ขา) → รอเจนใหม่

  python3 tools/sprites/rion_poses.py [--page OUT.html]

ขั้นตอนต่อท่า: กรอบในชีต → ตัดพื้นเขียว (สูตรเดียวกับ rion_ref.key) → ลบแสงเวทย์สีฟ้าอมเขียว (ท่าผลักปล่อย) →
  เก็บเฉพาะก้อนใหญ่สุด (ทิ้งประกายลอย) → ย่อทุกท่าอัตราเดียว (วัดจากท่าหันซ้ายยืนตรง = ตัวสูง 464) → ผืน 512 เท้าแถว 504
ผล: docs/art-bible/rion_hires/poses_v1/<ชื่อ>.png (ขนาดเดิมในชีต พื้นโปร่ง) · assets/sprites/rion_hires_draft/<ชื่อ>.png (ผืน 512)
"""
import argparse, base64, io, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rion_ref as R

ROOT = R.ROOT
SHEET = os.path.join(ROOT, "docs/art-bible/rion_hires/rion_pose_sheet_v1.png")
SRC_OUT = os.path.join(ROOT, "docs/art-bible/rion_hires/poses_v1")
OUT = os.path.join(ROOT, "assets/sprites/rion_hires_draft")
# กรอบในชีต (x0, y0, x1, y1) จากก้อนสีที่ไม่ใช่เขียว + เผื่อ 4 จุด · ชื่อไฟล์ตาม SHOTLIST
POSES = {
	"back":        ((262, 87, 440, 501), "หันหลัง (#2)"),
	"left":        ((448, 90, 630, 502), "หันซ้าย (#3)"),
	"left_windup": ((872, 131, 1140, 508), "ง้างมีด (#5)"),
	"left_strike": ((1173, 136, 1529, 510), "ฟาดมีด (#6)"),
	"left_hurt":   ((1, 583, 300, 938), "โดนตี (#7)"),
	"left_down":   ((490, 739, 805, 883), "นอนล้ม (#9)"),
	"left_cast":   ((943, 593, 1280, 944), "ผลักปล่อยเวทย์ (#11)"),
	"left_run":    ((1283, 571, 1526, 922), "วิ่ง (#12)"),
}
SCALE_REF = "left"     # ท่ายืนตรงหันซ้าย = ตัวสูงเต็ม → ตัวสูง 464 ในผืน 512


def cut(name, box, a_full):
	x0, y0, x1, y1 = box
	a = a_full[y0:y1, x0:x1].copy()
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	fx = (b - r > 90) & (g - r > 60) & (g > 150)            # แสงเวทย์ฟ้าอมเขียว (หมวก/เลนส์ g < 150 ไม่โดน)
	a, al = R.key(a)
	al[fx] = 0
	lab, n = ndimage.label(ndimage.binary_dilation(al > 0.5, iterations=2))
	if n > 1:   # ก้อนใหญ่สุด = ตัวละคร (มีด/แขนติดมาเพราะต่อกันที่มือ) · ประกาย/วงเวทย์ลอยถูกทิ้ง
		sizes = ndimage.sum(al > 0.5, lab, range(1, n + 1))
		al[lab != 1 + int(np.argmax(sizes))] = 0
	return a, al, int(fx.sum())


def main():
	ap = argparse.ArgumentParser(); ap.add_argument("--page"); args = ap.parse_args()
	os.makedirs(SRC_OUT, exist_ok=True)
	sheet = np.asarray(Image.open(SHEET).convert("RGB")).astype(np.int32)
	cuts = {n: cut(n, box, sheet) for n, (box, _) in POSES.items()}
	_, al_ref, _ = cuts[SCALE_REF]
	bx0, by0, bx1, by1 = R.body_box(al_ref)
	k = R.BODY_H / (by1 - by0 + 1)
	meta = {}
	for n, (a, al, fx) in cuts.items():
		rgba = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA")
		x0, y0, x1, y1 = R.body_box(al)
		rgba = rgba.crop((x0, y0, x1 + 1, y1 + 1)); rgba.save(os.path.join(SRC_OUT, n + ".png"))
		sm = rgba.resize((round(rgba.width * k), round(rgba.height * k)), Image.LANCZOS)
		cv = Image.new("RGBA", (R.CANVAS, R.CANVAS))
		cv.alpha_composite(sm, (round(R.CANVAS / 2 - sm.width / 2), R.FOOT_ROW - sm.height + 1))
		cv.save(os.path.join(OUT, n + ".png"))
		meta[n] = {"label": POSES[n][1], "src_h": int(y1 - y0 + 1), "canvas_w": sm.width, "canvas_h": sm.height, "fx_removed_px": fx,
			"clipped": bool(sm.width > R.CANVAS or sm.height > R.FOOT_ROW + 1)}
		print("%-12s ในชีตสูง %3d → ผืน %3dx%3d · ลบแสงเวทย์ %d จุด%s" % (n, y1 - y0 + 1, sm.width, sm.height, fx, " · ล้นผืน!" if meta[n]["clipped"] else ""))
	print("อัตราย่อ/ขยาย %.3f (จากท่า %s สูง %d → %d)" % (k, SCALE_REF, by1 - by0 + 1, R.BODY_H))
	if args.page:
		def uri(p):
			b = io.BytesIO(); Image.open(p).save(b, "WEBP", quality=92); return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
		data = {"front": uri(os.path.join(OUT, "stand_south.png")),
			"poses": [{"id": n, "label": POSES[n][1], "src": uri(os.path.join(OUT, n + ".png"))} for n in POSES],
			"sheet": uri(SHEET), "k": round(k, 3)}
		tpl = open(os.path.join(ROOT, "tools/web/rion_poses_test.tpl.html"), encoding="utf-8").read()
		open(args.page, "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(data)))
		print("หน้าเทส →", args.page, os.path.getsize(args.page), "bytes")


if __name__ == "__main__":
	main()
