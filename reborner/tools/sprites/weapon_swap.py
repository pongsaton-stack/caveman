"""เปลี่ยนอาวุธในท่าที่ PixelLab วาดถือมีดแล้ว → อาวุธชิ้นอื่นด้วยโค้ด (ไม่เสียเครดิต · kwan 20 ต.ค. "ขอดูฝีมือ" ทดลองวิธี "วางอาวุธทับมือด้วยโค้ด")

ทางแรกที่ลอง = เจนท่าฟันมือเปล่ากำหมัด (slash_fist · 2 gen) → PixelLab วาดเป็นเดิน 5 เฟรม แล้วหันเข้ากล้อง + วาดดาบเอง → ใช้ไม่ได้
ทางนี้: ใช้ท่าฟัน bl0 ที่ผ่านแล้ว (px_set pls_atk_bl) · ใบมีดเดิม = ก้อนที่ blade_tip.find_tip หาเจอ → ลบใบ+เส้นขอบ →
  มือ = ผิวที่ใกล้โคนใบที่สุด · มุม = โคนใบ → ปลายใบ · วางไอคอนอาวุธ (weapons300_draft) ด้วย rion_rig.weapon_sprite ให้ด้ามอยู่ที่มือ
เฟรมที่มีดอยู่หลังหัว (BEHIND) วาดอาวุธก่อนตัว · เฟรมที่หาใบไม่เจอ (มือ/อาวุธถูกหัวบัง) ไม่วาด
  python3 tools/sprites/weapon_swap.py → assets/sprites/pixellab_draft/px_set/swap_<อาวุธ>_<i>.png + px_set/swap.json · ภาพตรวจ docs/art-bible/pixellab_test/weapon_swap_check.png
"""
import json, math, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import blade_tip as BT
import rion_rig as R

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PX = os.path.join(ROOT, "assets/sprites/pixellab_draft/px_set")
ICON = os.path.join(ROOT, "assets/sprites/weapons300_draft")
CLIP, N = "pls_atk_bl", 8
BEHIND = {3}   # bl0 เฟรม 3: ง้างสุด มีดโผล่หลังหัว
# อาวุธ → (ชื่อ, ความยาวทั้งชิ้นในผืน 120 · มีดเดิมยาว ~9–12 รวมด้าม)
WEAPONS = {"SL01-1": ("มีดครัว", 15), "SL02-1": ("มีดสับ", 15), "SL08-1": ("เคียว", 16)}


def strip_blade(im, comp):
	"""ลบใบมีด + เส้นขอบเข้มที่ติดใบ (ไม่ใช่ผิว) · คืนจุดที่ลบ"""
	px = im.load(); W, H = im.size; gone = set(comp)
	for (x, y) in comp:
		for dx in (-1, 0, 1):
			for dy in (-1, 0, 1):
				q = (x + dx, y + dy)
				if 0 <= q[0] < W and 0 <= q[1] < H and q not in gone:
					r, g, b, a = px[q]
					if a and (r * 299 + g * 587 + b * 114) // 1000 < 90 and not BT.is_skin(r, g, b): gone.add(q)
	for q in gone: px[q] = (0, 0, 0, 0)
	return gone


def hand_and_angle(im, tip, comp):
	"""มือ = ผิวที่ใกล้โคนใบ (ปลายใบอีกข้าง) · มุมจอ (y ลง) จากมือไปปลาย"""
	base = max(comp, key=lambda q: math.hypot(q[0] - tip[0], q[1] - tip[1]))
	px = im.load(); W, H = im.size
	skin = [(x, y) for y in range(H) for x in range(W) if px[x, y][3] > 127 and BT.is_skin(*px[x, y][:3])
		and math.hypot(x - base[0], y - base[1]) <= 5]
	if skin: hand = (sum(p[0] for p in skin) / len(skin), sum(p[1] for p in skin) / len(skin))
	else: hand = base
	return hand, math.degrees(math.atan2(-(tip[1] - hand[1]), tip[0] - hand[0]))


def sprite(icon, grip, idir, length, angle):
	"""แบบ rion_rig.weapon_sprite แต่ย่อโดยให้สีเนื้อ (เงิน/ไม้) ชนะเส้นขอบ · weapon_sprite ใช้สีมากสุดในบล็อก → ไอคอน 32 ขอบหนาย่อเหลือ ~13 จุดแล้วดำทั้งชิ้น"""
	K = 8; s = length / max(1.0, R.axis(icon)[2])
	big = icon.resize((32 * K, 32 * K), Image.NEAREST); pad = 32 * K * 2
	can = Image.new("RGBA", (pad, pad)); can.paste(big, (int(pad / 2 - grip[0] * K), int(pad / 2 - grip[1] * K)), big)
	# กลับด้านไอคอนครั้งเดียวทั้งท่า แล้วหมุนอย่างเดียว (kwan 20 ต.ค. "โจมตีแล้วอาวุธในมือสลับด้าน" → "ยังผิดนะดูดีๆ"):
	#   รอบแรก weapon_sprite พลิกเฉพาะเฟรมที่ชี้ซ้าย → คมกลับข้างกลางท่า · รอบสองหมุนล้วนไม่พลิก → คมอยู่ข้างตามเข็มของแกน (ไอคอน SL ทุกชิ้น คม/ตะขออยู่ล่างขวาของด้าม)
	#   แต่ bl0 ฟาดข้ามไหล่ = หมุนทวนเข็ม (มุม −24 → ผ่าน 90 บนหัว → 221 หน้าล่าง) → สันนำ และท่ายืนคมหันขึ้นเข้าหน้า · กลับด้าน = คมอยู่ข้างทวนเข็ม: ยืนคมหันลง-หน้า · ฟาดคมนำ
	can = can.transpose(Image.FLIP_LEFT_RIGHT); rot = angle - (180 - idir)
	a = np.asarray(can.rotate(rot, Image.NEAREST)); k = max(1, round(K / s)); h = a.shape[0] // k
	out = np.zeros((h, h, 4), np.uint8)
	for y in range(h):
		for x in range(h):
			blk = a[y * k:(y + 1) * k, x * k:(x + 1) * k].reshape(-1, 4); op = blk[blk[:, 3] > 0]
			if len(op) * 2 < len(blk) * 0.8: continue
			lit = op[op[:, :3].astype(int) @ np.array([299, 587, 114]) // 1000 >= 70]
			use = lit if len(lit) >= len(op) * 0.3 else op
			cols, cnt = np.unique(use, axis=0, return_counts=True); out[y, x] = cols[cnt.argmax()]
	small = R.WH.outline(Image.fromarray(out, "RGBA"))
	return small, (small.size[0] / 2.0, small.size[1] / 2.0)


def main():
	frames = []
	for i in range(N):
		p = os.path.join(PX, f"{CLIP}_{i}.png"); f = BT.find_tip(p)
		frames.append((Image.open(p).convert("RGBA"), f))
	out = {}
	for code, (name, L) in WEAPONS.items():
		icon = Image.open(os.path.join(ICON, code + ".png")).convert("RGBA"); grip, idir, _ = R.axis(icon)
		names = []
		for i, (src, f) in enumerate(frames):
			body = src.copy(); c = Image.new("RGBA", body.size)
			if f:
				tip, _, comp = f
				hand, ang = hand_and_angle(src, tip, comp)
				strip_blade(body, comp)
				spr, (cx, cy) = sprite(icon, grip, idir, L, ang)
				at = (int(round(hand[0] - cx)), int(round(hand[1] - cy)))
				if i in BEHIND: c.alpha_composite(spr, at); c.alpha_composite(body)
				else: c.alpha_composite(body); c.alpha_composite(spr, at)
			else: c.alpha_composite(body)
			n = f"swap_{code}_{i}"; c.save(os.path.join(PX, n + ".png")); names.append(n)
		out[code] = {"name": name, "frames": names}
	json.dump({"_doc": "bl0 เปลี่ยนอาวุธด้วยโค้ด · tools/sprites/weapon_swap.py · ร่าง", "clip": CLIP, "weapons": out},
		open(os.path.join(PX, "swap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	# ภาพตรวจ ขยาย 4 เท่า: แถว = ของเดิม + อาวุธ 3 ชิ้น · ครอปช่วงตัว
	Z, box = 4, (10, 40, 100, 112)
	bw, bh = box[2] - box[0], box[3] - box[1]
	rows = [[f"{CLIP}_{i}" for i in range(N)]] + [v["frames"] for v in out.values()]
	S = Image.new("RGBA", (N * bw * Z, len(rows) * bh * Z), (150, 190, 150, 255))
	for r, row in enumerate(rows):
		for i, n in enumerate(row):
			S.alpha_composite(Image.open(os.path.join(PX, n + ".png")).crop(box).resize((bw * Z, bh * Z), Image.NEAREST), (i * bw * Z, r * bh * Z))
	S.convert("RGB").save(os.path.join(ROOT, "docs/art-bible/pixellab_test/weapon_swap_check.png"))
	for code, v in out.items(): print(code, v["name"], len(v["frames"]))
	# คลิปเทียบในหน้า animation test (px_set/index.json · pixellab_rion_set.py ล้าง px_set ทุกครั้ง แล้วเรียก main() นี้ต่อ)
	ix = os.path.join(PX, "index.json"); d = json.load(open(ix, encoding="utf-8"))
	d["clips"] = [c for c in d["clips"] if not c["id"].startswith("swap_")] + [{"group": "★ ทดลอง · เปลี่ยนอาวุธด้วยโค้ด (bl0 · ร่าง)",
		"id": f"swap_{code}", "label": f"{v['name']} {code} · ท่าฟัน bl0 ลบมีดแล้ววางไอคอนอาวุธที่มือ · 8 เฟรม (ไม่เสียเครดิต)",
		"frames": v["frames"], "ms": 90, "loop": False, "w": 120, "travel": 0, "src": [f"weapon_swap {CLIP} + weapons300_draft/{code}"]}
		for code, v in out.items()]
	json.dump(d, open(ix, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
	main()
