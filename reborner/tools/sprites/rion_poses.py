#!/usr/bin/env python3
"""tools/sprites/rion_poses.py — ตัดท่า Rion จากชีตท่าที่ kwan เจน (rion_pose_sheet_v1.png · 14 ต.ค. 2026) เป็นร่างภาพคม

kwan สั่ง "เอาที่ใช้ได้มาทำก่อน" → 8 ท่าที่ผ่านการดู: หลัง · หันซ้าย · ง้างมีด · ฟาด · โดนตี · นอนล้ม · ผลักปล่อยเวทย์ · วิ่ง
ไม่เอา: หันหน้า (ใช้ต้นฉบับแทน) · หันขวา (พลิกจากหันซ้าย นาฬิกาผิดข้าง) · พนมมือ (หันหน้าตรง) · ทรุดเข่า (คลานสี่ขา) → รอเจนใหม่

  python3 tools/sprites/rion_poses.py [--page OUT.html]   (หน้าเทส = คลิปท่าขยับจากภาพนิ่ง + แกลเลอรี · เทมเพลต tools/web/rion_poses_test.tpl.html)

ขั้นตอนต่อท่า: กรอบในชีต → ตัดพื้นเขียว (สูตรเดียวกับ rion_ref.key) → ลบแสงเวทย์สีฟ้าอมเขียว (ท่าผลักปล่อย) →
  เก็บเฉพาะก้อนใหญ่สุด (ทิ้งประกายลอย) → ย่อทุกท่าอัตราเดียว (วัดจากท่าหันซ้ายยืนตรง = ตัวสูง 464) → ผืน 512 เท้าแถว 504
ผล: docs/art-bible/rion_hires/poses_v1/<ชื่อ>.png (ขนาดเดิมในชีต พื้นโปร่ง) · assets/sprites/rion_hires_draft/<ชื่อ>.png (ผืน 512)
"""
import argparse, base64, io, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
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
# ท่าที่ทำต่อจากท่าในชีต (ไม่ได้เจน · kwan 14 ต.ค. "วาดส่วนที่ขาดเองไม่ได้เหรอ")
# right = หันซ้ายพลิกภาพ + ลบนาฬิกา: หันขวาแขนใกล้ = แขนขวา นาฬิกา (ข้อมือซ้าย) ต้องอยู่แขนไกลที่มองไม่เห็น
#   แขนท่อนล่างช่วงนาฬิกาตั้งตรง กว้างเท่าเดิม → คัดลอกแถว 237 (เส้นขอบ x74–78 · ผิว 79–97 · เส้นขอบ 99–103 วัดจากภาพ) ทับแถว 239–259
WATCH_ROWS, WATCH_COLS, ARM_ROW = (239, 260), (74, 102), 237
DERIVED = {"right": ("left", "หันขวา (#4 · พลิกจากหันซ้าย + ลบนาฬิกา)"),
	"left_pray": ("left", "พนมมือ (#10 · ตัวอย่างแก้จากหันซ้าย · ไม่ได้เจน)")}
# left_pray (kwan เลือก "2" ลองวาดเอง): ยกแขนใกล้ (ผิว+นาฬิกา+เส้นขอบ ใต้ชายแขนเสื้อ แถว 212–292) หมุนรอบข้อศอก PRAY_PIVOT -110° ให้มือตั้งหน้าอก
#   ที่เดิมของแขนเติมสีตามแถบเสื้อ/ขอบ/เข็มขัด/ขอบ/กางเกง (วัดจากคอลัมน์ข้างแขน) · มือข้างไกล = ชิ้นเดียวกันเลื่อน (-3,-2) สีเข้ม 82% ·
#   แปะชายแขนเสื้อเดิมทับรอยตัด · หลับตา = ทาผิวทับตา (x41–62 y103–133) + เส้นโค้งลง
PRAY_BOX, PRAY_PIVOT, PRAY_ANG = (212, 293, 64, 104), (89, 216), -110
PRAY_HAND_ANG, PRAY_HAND_DY, PRAY_FAR_OFF = -170, 0, (-3, -1)   # มือ: นิ้วชี้ขึ้น เอียงไปหน้า 10° · มือไกลเลื่อนไปหน้า
PRAY_ELBOW, PRAY_CREASE, PRAY_SKIN = (90, 219), ((79, 214), (85, 208)), (246, 205, 170)
PRAY_BANDS = [((212, 236), (243, 232, 224)), ((236, 239), (12, 10, 10)), ((239, 247), (96, 62, 52)), ((247, 250), (12, 10, 10)), ((250, 293), (30, 101, 184))]


def derive_right(a, al):
	a, al = a.copy(), al.copy()
	for y in range(*WATCH_ROWS):
		a[y, WATCH_COLS[0]:WATCH_COLS[1]] = a[ARM_ROW, WATCH_COLS[0]:WATCH_COLS[1]]
		al[y, WATCH_COLS[0]:WATCH_COLS[1]] = al[ARM_ROW, WATCH_COLS[0]:WATCH_COLS[1]]
	return a[:, ::-1], al[:, ::-1]


def derive_pray(a, al):
	H, W = al.shape; y0, y1, x0, x1 = PRAY_BOX
	rgba = np.dstack([a, al * 255]).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
	box = np.zeros((H, W), bool); box[y0:y1, x0:x1] = True
	skin = box & (al > .8) & (r > 190) & (g > 140) & (b > 100) & (r - b > 35)
	watch = np.zeros_like(box); watch[WATCH_ROWS[0]:WATCH_ROWS[1], WATCH_COLS[0]:WATCH_COLS[1]] = True
	core = ndimage.binary_closing(skin | watch, iterations=2) & box
	arm = core | (ndimage.binary_dilation(core, iterations=3) & box & (r + g + b < 260) & (al > .8))
	piece = np.zeros_like(rgba); piece[arm] = rgba[arm]
	out = rgba.copy(); zone = ndimage.binary_dilation(arm, iterations=5) & box
	for (ya, yb), col in PRAY_BANDS:
		col = np.array(col)
		for y in range(ya, yb):
			for x in np.nonzero(zone[y])[0]:
				if arm[y, x] or np.abs(rgba[y, x, :3] - col).max() > 30: out[y, x, :3] = col; out[y, x, 3] = 255
	img = Image.fromarray(out.astype(np.uint8), "RGBA")
	# แยกท่อนแขน (ใต้ชายแขนเสื้อ → ใต้นาฬิกา) กับมือ (ใต้นาฬิกาลงไป) · ท่อนแขนหมุนรอบข้อศอก · มือหมุนรอบข้อมือให้นิ้วตั้งขึ้น แล้วย้ายไปปลายท่อนแขน
	wy = WATCH_ROWS[1]; fore = piece.copy(); fore[wy:] = 0; hand = piece.copy(); hand[:wy + 1] = 0
	hand[(hand[..., 2] > hand[..., 0] + 20)] = 0   # ตัดเศษสายนาฬิกาสีฟ้าออกจากชิ้นมือ
	px, py = PRAY_PIVOT; th = np.radians(PRAY_ANG); wx0 = WATCH_COLS[0] + (WATCH_COLS[1] - WATCH_COLS[0]) // 2 - 2
	wx, wyy = px + (wx0 - px) * np.cos(th) + (wy - py) * np.sin(th), py - (wx0 - px) * np.sin(th) + (wy - py) * np.cos(th)
	fim = Image.fromarray(fore.astype(np.uint8), "RGBA").rotate(PRAY_ANG, center=PRAY_PIVOT, resample=Image.BICUBIC)
	him = Image.fromarray(hand.astype(np.uint8), "RGBA").rotate(PRAY_HAND_ANG, center=(wx0, wy), resample=Image.BICUBIC)
	hl = Image.new("RGBA", img.size); hl.alpha_composite(him, (int(round(wx - wx0)), int(round(wyy - wy)) + PRAY_HAND_DY))
	near = Image.new("RGBA", img.size); near.alpha_composite(hl); near.alpha_composite(fim)   # ท่อนแขน (มีนาฬิกา) ทับโคนมือ
	far = np.array(hl).astype(int); far[..., :3] = far[..., :3] * 82 // 100
	sh = Image.new("RGBA", img.size); sh.alpha_composite(Image.fromarray(far.astype(np.uint8), "RGBA"), PRAY_FAR_OFF)
	# ข้อพับ: ศอกกลมใต้ชายแขนเสื้อ (ปลายศอกชี้ลง-หลัง) วาดก่อนท่อนแขน + เส้นข้อพับด้านในตรงมุมที่ท่อนแขนพับขึ้น
	d = ImageDraw.Draw(img); ex, ey0 = PRAY_ELBOW
	d.ellipse((ex - 9, ey0 - 7, ex + 8, ey0 + 8), fill=PRAY_SKIN + (255,), outline=(20, 12, 10, 255), width=2)
	img.alpha_composite(sh); img.alpha_composite(near)
	d = ImageDraw.Draw(img); d.line(PRAY_CREASE, fill=(170, 96, 72, 255), width=2)   # เส้นข้อพับด้านใน
	sm = np.zeros((H, W), bool); sm[170:213, 72:106] = True; sm &= (al > .8) & ~arm   # ชายแขนเสื้อทับรอยตัด
	sleeve = np.zeros_like(rgba); sleeve[sm] = rgba[sm]; img.alpha_composite(Image.fromarray(sleeve.astype(np.uint8), "RGBA"))
	o = np.array(img).astype(int); sk = o[128, 66].copy()
	ey = np.zeros((H, W), bool); ey[103:134, 41:63] = True
	eye = ey & ((o[..., :3].sum(-1) < 420) | ((o[..., 0] > 225) & (o[..., 1] > 225) & (o[..., 2] > 225)))
	o[ndimage.binary_dilation(eye, iterations=1) & ey] = sk
	img = Image.fromarray(o.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(img)
	d.arc((41, 108, 62, 128), 20, 160, fill=(58, 34, 24, 255), width=3); d.line((42, 117, 39, 113), fill=(58, 34, 24, 255), width=2)
	o = np.array(img).astype(np.float64)
	return o[..., :3], o[..., 3] / 255


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
	labels = {n: lab for n, (_, lab) in POSES.items()}
	_, al_ref, _ = cuts[SCALE_REF]
	bx0, by0, bx1, by1 = R.body_box(al_ref)
	k = R.BODY_H / (by1 - by0 + 1)
	meta = {}
	for n, (base, lab) in DERIVED.items():   # ทำหลังตัด (พิกัดลบนาฬิกาเป็นพิกัดของภาพที่ครอปตัวแล้ว)
		a0, al0, _ = cuts[base]; x0, y0, x1, y1 = R.body_box(al0)
		a1, al1 = (derive_right if n == "right" else derive_pray)(a0[y0:y1 + 1, x0:x1 + 1], al0[y0:y1 + 1, x0:x1 + 1])
		cuts[n] = (a1, al1, 0); labels[n] = lab
	for n, (a, al, fx) in cuts.items():
		rgba = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8), "RGBA")
		x0, y0, x1, y1 = R.body_box(al)
		rgba = rgba.crop((x0, y0, x1 + 1, y1 + 1)); rgba.save(os.path.join(SRC_OUT, n + ".png"))
		sm = rgba.resize((round(rgba.width * k), round(rgba.height * k)), Image.LANCZOS)
		cv = Image.new("RGBA", (R.CANVAS, R.CANVAS))
		cv.alpha_composite(sm, (round(R.CANVAS / 2 - sm.width / 2), R.FOOT_ROW - sm.height + 1))
		cv.save(os.path.join(OUT, n + ".png"))
		meta[n] = {"label": labels[n], "src_h": int(y1 - y0 + 1), "canvas_w": sm.width, "canvas_h": sm.height, "fx_removed_px": fx,
			"clipped": bool(sm.width > R.CANVAS or sm.height > R.FOOT_ROW + 1)}
		print("%-12s ในชีตสูง %3d → ผืน %3dx%3d · ลบแสงเวทย์ %d จุด%s" % (n, y1 - y0 + 1, sm.width, sm.height, fx, " · ล้นผืน!" if meta[n]["clipped"] else ""))
	print("อัตราย่อ/ขยาย %.3f (จากท่า %s สูง %d → %d)" % (k, SCALE_REF, by1 - by0 + 1, R.BODY_H))
	if args.page:
		def uri(p):
			b = io.BytesIO(); Image.open(p).save(b, "WEBP", quality=92); return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
		data = {"front": uri(os.path.join(OUT, "stand_south.png")),
			"poses": [{"id": n, "label": labels[n], "src": uri(os.path.join(OUT, n + ".png"))} for n in cuts],
			"sheet": uri(SHEET), "k": round(k, 3),
			"bg": uri(os.path.join(ROOT, "assets/sprites/battle_bg_hires_draft/act1.png")), "bg_ground": 0.734,   # เส้นพื้นของฉาก (battle_bg_hires.GROUND)
			"seq": seqs(uri)}
		tpl = open(os.path.join(ROOT, "tools/web/rion_poses_test.tpl.html"), encoding="utf-8").read()
		open(args.page, "w", encoding="utf-8").write(tpl.replace("__DATA__", json.dumps(data)))
		print("หน้าเทส →", args.page, os.path.getsize(args.page), "bytes")


# ท่าขยับจากชุดหลัก (rion_flow_cut.py · ชีต GPT รอบ 8 ขนาดเต็ม ตัวสูง ~360) ใช้ในคลิป SL01 · หันซ้ายแล้ว
# ช่อง = กรอบรวมทั้งแถว: ล่างช่อง − 5 = พื้น (เฟรมลอยคงความสูงเดิม) · กลางช่อง = กลางตัว
# k = ขยายเข้าผืน 512 แบบเดียวกับท่าอื่น: อัตราที่ชุดหลักย่อ (เทียบเดินชีต A) × BODY_H ÷ ความสูงเดินชีต A
SEQ = {"idle": ("v8a", "idle_battle", ()), "atk": ("v8a", "attack_knife", (5,)), "roll": ("v8b", "jump_roll", ()),
	"kneel": ("v8b", "kneel", ())}


def seqs(uri):
	d = os.path.join(ROOT, "assets/sprites/rion_flow_draft")
	sc = json.load(open(os.path.join(d, "main", "scale.json")))
	out = {}
	for name, (src, row, omit) in SEQ.items():
		fs, lift, i = [], [], 0
		while os.path.exists(os.path.join(d, src, "%s_%d.png" % (row, i))):
			if i not in omit:
				p = os.path.join(d, src, "%s_%d.png" % (row, i)); a = np.array(Image.open(p))[..., 3] > 128
				fs.append(uri(p)); lift.append(int(a.shape[0] - 5 - 1 - np.nonzero(a.any(1))[0].max()))   # ระยะเท้าลอยจากพื้นช่อง (หน้าเทสวางเท้าบนพื้นเอง)
			i += 1
		out[name] = {"k": round(sc["k"][src] * R.BODY_H / sc["ref_h"], 4), "frames": fs, "lift": lift}
	return out


if __name__ == "__main__":
	main()
