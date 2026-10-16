"""ไอคอนอาวุธ 30 ชิ้น พิกเซล จากชีตรอบ 12 (Google Flow · kwan 16 ต.ค. 2026)
  python3 tools/sprites/weapons_icons_px.py
ชีต docs/art-bible/weapons/weapon_icons_v12.jpg: 6 แถว (ตระกูล SL PC CR ST DV BD) x 5 ช่อง (ระดับ 1–5) ตามลำดับใน weapons_full.json
ทำ: ตัดพื้นด้วยระยะสีจากสีพื้นจริง → ช่องตามตาราง (แบ่งเท่า) เก็บทุกก้อนในช่อง (ประกายรอบชิ้นระดับ 5 ด้วย) →
ย่อ BOX ให้ด้านยาวพอดีผืน (ทุกชิ้นอัตราเดียวต่อขนาด = ชิ้นใหญ่ในชีตยังใหญ่) → ขอบ 1 จุดเข้ม → สีต่อชิ้น ≤ 16
ออก assets/sprites/weapons_icons_draft/<id>.png (32px · ขนาดไอคอนเดิม) และ <id>_48.png (.gdignore · ร่าง)"""
import glob, json, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHEET = os.path.join(ROOT, "docs/art-bible/weapons/weapon_icons_v12.jpg")
OUT = os.path.join(ROOT, "assets/sprites/weapons_icons_draft")
GAME = os.path.join(ROOT, "assets/sprites/weapon_icons")   # เข้าเกม (kwan 16 ต.ค. เลือก 48px): <id>.png · เมนู Esc แสดงอาวุธที่ถือ
EDGE = np.array([42, 26, 20])
SIZES = {"": 32, "_48": 48}
# แสงเรืองแบบพิกเซลของระดับ 5 (kwan 16 ต.ค. เลือก "เพิ่มแสงเรืองรอบชิ้นระดับ 5"): วงนอกเส้นขอบ 1 จุดทึบ + วงที่ 2 โปร่งครึ่ง · สีตามแสงในชีต
GLOW = {"SL-5": (255, 150, 40), "PC-5": (120, 220, 255), "CR-5": (255, 225, 110), "ST-5": (255, 210, 90), "DV-5": (110, 230, 255), "BD-5": (255, 140, 50)}
MARGIN = 3   # เผื่อขอบผืนให้วงแสง 2 ชั้น


def key(rgb):
	bg = np.median(np.concatenate([rgb[:10].reshape(-1, 3), rgb[-10:].reshape(-1, 3)]), 0)
	d = np.sqrt(((rgb - bg) ** 2).sum(-1)); a = np.clip((d - 20) / 40.0, 0, 1)
	mix = ((a > 0) & (a < 1))[..., None]
	out = np.where(mix, (rgb - (1 - a)[..., None] * bg) / np.maximum(a, 1e-3)[..., None], rgb).clip(0, 255)
	# ไม่มีอาวุธชิ้นไหนเขียว (มีแค่ DV-4 สีเขียวขี้ม้าอ่อน) → ตัดเขียวที่เกินแดง/น้ำเงินทุกจุด: แสงเรืองของระดับ 5 โปร่งทับพื้นเขียว ทำให้ทั้งชิ้นอมเขียว
	out[..., 1] = np.minimum(out[..., 1], np.maximum(out[..., 0], out[..., 2]) + 12)
	return out, a


def icon(rgb, al, k, S, glow=None):
	pre = np.dstack([rgb * al[..., None], al * 255]).clip(0, 255).astype(np.uint8)
	h, w = al.shape; nw, nh = max(1, round(w * k)), max(1, round(h * k))
	sm = np.array(Image.fromarray(pre, "RGBA").resize((nw, nh), Image.BOX)).astype(float)
	A = sm[..., 3] / 255; c = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	m = A > 0.5
	lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1))   # จุดโดด < 4 จุด (ประกายเล็กในชีตที่ย่อแล้วเหลือเม็ดเดียว) ทิ้ง
	m &= np.isin(lab, [i + 1 for i in range(n) if sz[i] >= 4])
	e = m & ~ndimage.binary_erosion(m); c[e] = c[e] * .35 + EDGE * .65
	px = c[m].astype(np.uint8)
	pal = np.array(Image.fromarray(px[None]).quantize(min(16, len(np.unique(px, axis=0))), method=Image.MEDIANCUT).convert("RGB")).reshape(-1, 3).astype(float)
	q = pal[((c[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)]
	img = np.zeros((nh, nw, 4), np.uint8); img[..., :3] = q; img[..., 3] = m * 255
	cv = Image.new("RGBA", (S, S)); im = Image.fromarray(img, "RGBA")
	cv.paste(im, ((S - nw) // 2, (S - nh) // 2), im)
	if glow:
		a = np.array(cv); m0 = a[..., 3] > 0
		r1 = ndimage.binary_dilation(m0) & ~m0
		r2 = ndimage.binary_dilation(m0, iterations=2) & ~m0 & ~r1
		a[r1] = glow + (255,); a[r2] = glow + (110,)
		cv = Image.fromarray(a, "RGBA")
	return cv


def main():
	ids = [w["id"] for f in json.load(open(os.path.join(ROOT, "docs/art-bible/weapons/weapons_full.json")))["families"] for w in f["weapons"]]
	rgb, a = key(np.array(Image.open(SHEET).convert("RGB")).astype(float))
	H, W = a.shape; ch, cw = H / 6, W / 5
	cells = []
	for r in range(6):
		for c in range(5):
			y0, y1, x0, x1 = int(r * ch), int((r + 1) * ch), int(c * cw), int((c + 1) * cw)
			al = a[y0:y1, x0:x1]; m = al > 0.5
			lab, n = ndimage.label(m); area = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
			keep = np.isin(lab, [i + 1 for i in range(n) if area[i] > 12])
			ys, xs = np.where(keep)
			cells.append((rgb[y0:y1, x0:x1][ys.min():ys.max() + 1, xs.min():xs.max() + 1], np.where(keep, al, 0)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]))
	big = max(max(al.shape) for _, al in cells)   # อัตราเดียวทุกชิ้น: ชิ้นใหญ่สุดในชีตเต็มผืน
	os.makedirs(OUT, exist_ok=True)
	for f in glob.glob(os.path.join(OUT, "*.png")): os.remove(f)
	for suf, S in SIZES.items():
		k = (S - 2 * MARGIN) / big
		for wid, (c, al) in zip(ids, cells):
			im = icon(c, al, k, S, GLOW.get(wid)); im.save(os.path.join(OUT, "%s%s.png" % (wid, suf)))
			if S == 48:
				os.makedirs(GAME, exist_ok=True); im.save(os.path.join(GAME, "%s.png" % wid))
	json.dump({"_doc": __doc__.split("\n")[0], "ids": ids, "sizes": list(SIZES.values())}, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	print("weapons_icons_px: %d ชิ้น · ขนาด %s" % (len(ids), list(SIZES.values())))


if __name__ == "__main__":
	main()
