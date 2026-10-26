"""Rion พิกเซลถืออาวุธ 6 สาย จากชีตรอบ 15-1 (Google Flow · kwan 16 ต.ค. 2026 · เดิมรอบ 9/13 หมวกครีม)
  python3 tools/sprites/rion_px_weapons.py   (รันหลัง rion_flow_cut.py + rion_px_game.py)
ชีต docs/art-bible/rion_hires/flow_trial_v15_1b.jpg: 6 แถว x 5 ช่อง หันขวา (JPG)
ทำ: ลบพื้นเขียว → แยกก้อนต่อแถว (ตัวใหญ่ = ตัวละคร · ก้อนเล็ก เช่น ส่วนโค้ง/ประกาย/ลูกหิน = ติดกับตัวที่ใกล้สุด) → พลิกหันซ้าย →
ย่ออัตราเดียวทั้งชีต ให้ท่ายืนสูงเท่า Rion ในเกม (west_w0 ท่าเดินยืนตรง) → ลดสีด้วยพาเลตต์ชุดหลัก 40 สี + สีใหม่ของอาวุธ ≤ 12 → ผืน 96x112 เท้าแถว 109 กลางหมวก = คอลัมน์ 48
ออก assets/sprites/rion_px_weapons_draft/<สาย>_<i>.png (.gdignore · ร่าง ยังไม่เข้าเกม) + index.json"""
import glob, json, os
import numpy as np
from PIL import Image
from scipy import ndimage
import flow_fix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# รอบ 15-1 (kwan 16 ต.ค. · Google Flow · แบบหมวกน้ำเงินทั้งใบ) แทนรอบ 9/13 (หมวกครีม · เลิกใช้): 6 แถว (คม ทุบ แทง ยิง กล มือเปล่า) x 5 ช่อง หันขวา
#   ก่อนตัดผ่าน flow_fix.fixed (แถวมีดช่อง 1 ถือมีด 2 เล่ม → ลบเล่มมือหลัง)
SHEETS = {"v15_1": os.path.join(ROOT, "docs/art-bible/rion_hires/flow_trial_v15_1b.jpg")}
OUT = os.path.join(ROOT, "assets/sprites/rion_px_weapons_draft")
GAME = os.path.join(ROOT, "assets/sprites/rion_px")
# 16 ต.ค. ปิดการเขียนเข้าเกม: ชีตรอบ 9/13 เป็น Rion หมวกครีม ไม่ตรงแบบที่ kwan ยึด (Flow หมวกน้ำเงินทั้งใบ) · เปิดคืนเมื่อเจนท่าถืออาวุธใหม่ด้วยแบบที่ถูกแล้ว
TO_GAME = False   # เข้าเกม (kwan 16 ต.ค. "ใส่เข้าเกม"): west_<สาย>_<i>.png ผืนเดียวกับ rion_px · BattleScreen เลือกตามสายของอาวุธที่ติดตั้ง
W, H, FEET, CX = 96, 112, 109, 48
EDGE = np.array([42, 26, 20])
# เลือกเฟรมด้วยตา (แถว, ช่อง) นับจาก 0 ตามที่ Flow วาด (หันขวา ก่อนพลิก)
# ชื่อ = ไฟล์ west_<ชื่อ>_<i> · ระดับ 1 = รหัสสาย (CR) ใช้เป็นค่าตั้งต้นของทั้งสาย · ระดับอื่น = รหัสอาวุธ (CR-2)
# 15-1: ช่อง 5 ของแถว 1–4 มือว่าง (ลืมอาวุธ) → kwan เลือก "1": ใช้ช่อง 1 (ยืนถืออาวุธ) แทน · เหลือภาพไม่ซ้ำ 4 ภาพ
CLIPS = [
	("SL", "มีดทำครัวบิ่น (คม)", "v15_1", [(0, 0), (0, 1), (0, 2), (0, 3), (0, 0)], 3),
	("CR", "ไม้เบสบอลร้าวพันเทป (ทุบ)", "v15_1", [(1, 0), (1, 1), (1, 2), (1, 3), (1, 0)], 3),
	("PC", "ดินสอ (แทง)", "v15_1", [(2, 0), (2, 1), (2, 2), (2, 3), (2, 0)], 3),
	("ST", "หนังสติ๊กกิ่งไม้ (ยิง)", "v15_1", [(3, 0), (3, 1), (3, 2), (3, 3), (3, 0)], 3),
	("DV", "ที่เย็บกระดาษ (กล)", "v15_1", [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)], 3),
	("BD", "ถุงมือผ้า (มือเปล่า)", "v15_1", [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4)], 2),
]   # ตัวเลขท้าย = ลำดับเฟรมกระทบ (ใช้ในหน้าเทส)
REF_CELL = {"v15_1": (4, 0)}   # ยืนถือที่เย็บกระดาษ: ไม่มีของเหนือหัว ใช้วัดความสูงตัว


def key_green(rgb):
	r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
	bg = (g > 140) & (g > r + 60) & (g > b + 60)
	# ขอบนุ่ม: ยิ่งเขียวจัดยิ่งโปร่ง (JPG มีขอบเขียวปน)
	gness = np.clip((g - np.maximum(r, b) - 25) / 80.0, 0, 1)
	a = np.where(bg, 0.0, 1.0 - gness)
	out = rgb.astype(float).copy()
	spill = g > np.maximum(r, b)
	out[..., 1] = np.where(spill, np.maximum(r, b), g)   # ล้างเขียวที่ขอบ
	return out, a


def cells(rgb, a):
	"""คืน dict (แถว, ช่อง) → (rgb, alpha) ภาพต้นฉบับขนาดชีต ตัดตามกรอบก้อน"""
	m = a > 0.5
	rows = ndimage.find_objects(ndimage.label(ndimage.binary_dilation(m.any(1)[:, None].repeat(3, 1), iterations=8)[:, 0])[0])
	out = {}
	for ri, (rs,) in enumerate((r[0],) for r in rows):
		band = m[rs]
		lab, n = ndimage.label(ndimage.binary_closing(band, iterations=2))
		objs = ndimage.find_objects(lab)
		area = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
		big = sorted([i for i in range(n) if area[i] > 4000], key=lambda i: objs[i][1].start)
		while len(big) > 6:   # ตัวที่ขาดเป็นสองก้อน → รวมก้อนเล็กสุดเข้าก้อนใกล้สุด
			big.remove(min(big, key=lambda i: area[i]))
		owner = {}
		for i in range(n):
			cx = (objs[i][1].start + objs[i][1].stop) / 2
			owner[i] = min(range(len(big)), key=lambda k: abs(cx - (objs[big[k]][1].start + objs[big[k]][1].stop) / 2))
		for k in range(len(big)):
			sel = np.isin(lab, [i + 1 for i in range(n) if owner[i] == k and area[i] > 12])
			ys, xs = np.where(sel)
			y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
			al = np.where(sel, a[rs], 0)[y0:y1, x0:x1]
			out[(ri, k)] = (rgb[rs][y0:y1, x0:x1], al)
	return out


def shrink(rgb, al, k):
	h, w = al.shape
	pre = np.dstack([rgb * al[..., None], al * 255]).clip(0, 255).astype(np.uint8)
	nw, nh = max(1, round(w * k)), max(1, round(h * k))
	sm = np.array(Image.fromarray(pre, "RGBA").resize((nw, nh), Image.BOX)).astype(float)
	A = sm[..., 3] / 255
	c = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	m = A > 0.5
	e = m & ~ndimage.binary_erosion(m)
	c[e] = c[e] * .35 + EDGE * .65
	return c, m


def main():
	# ความสูงอ้างอิง = ท่าเดินยืนตรงในเกม (west_i0 ตอนนี้เป็นท่าย่อถือมีด ใช้วัดไม่ได้)
	ref = np.array(Image.open(os.path.join(ROOT, "assets/sprites/rion_px/west_w0.png")))
	ys = np.where((ref[..., 3] > 0).any(1))[0]
	ref_h = ys[-1] - ys[0] + 1
	GOT, K = {}, {}
	for sk, path in SHEETS.items():   # ย่อต่อชีต ให้ท่ายืนสูงเท่า Rion ในเกม
		rgb, a = key_green(flow_fix.fixed(sk, np.array(Image.open(path).convert("RGB")).astype(float)))
		GOT[sk] = cells(rgb, a); K[sk] = ref_h / GOT[sk][REF_CELL[sk]][1].shape[0]
	k = K[next(iter(SHEETS))]
	# พาเลตต์ = 40 สีของชุดหลัก + สีใหม่ของอาวุธ (ไกลจากพาเลตต์เดิม) ≤ 8
	base = set()
	for f in glob.glob(os.path.join(ROOT, "assets/sprites/rion_flow_draft/main_px/*.png")):
		b = np.array(Image.open(f)); base |= set(map(tuple, b[b[..., 3] > 0][:, :3]))
	base = np.array(sorted(base), float)
	frames = {}
	for fam, _, sk, picks, _ in CLIPS:
		for rc in picks:
			c, m = shrink(*GOT[sk][rc], K[sk])
			frames[(fam, rc)] = (c[:, ::-1], m[:, ::-1])   # พลิกหันซ้าย
	px = np.concatenate([c[m] for c, m in frames.values()])
	d = np.sqrt(((px[:, None, :] - base[None]) ** 2).sum(-1)).min(1)
	far = px[d > 30]
	# สีใหม่ ≤ 12 · median cut แบบ "จำนวนพิกเซล" ทำให้ของชิ้นเล็กสีจัด (ดินสอเหลือง ยางลบชมพู) ไม่ได้สีของตัวเอง → นับสีไม่ซ้ำ (ปัด 16 ระดับ) แทน
	uq = np.unique((far // 16 * 16 + 8).astype(np.uint8), axis=0) if len(far) else np.zeros((0, 3), np.uint8)
	extra = np.array(Image.fromarray(uq[None]).quantize(min(12, len(uq)), method=Image.MEDIANCUT).convert("RGB")).reshape(-1, 3) if len(uq) >= 2 else uq
	pal = np.unique(np.vstack([base, np.array(sorted(set(map(tuple, extra))), float).reshape(-1, 3)]), axis=0)
	os.makedirs(OUT, exist_ok=True)
	for f in glob.glob(os.path.join(OUT, "*.png")) + [g for c in CLIPS for g in glob.glob(os.path.join(GAME, "west_%s_*.png" % c[0]))]: os.remove(f)
	idx = {"_doc": __doc__.split("\n")[0], "scale": round(k, 4), "palette": len(pal), "clips": []}
	for fam, label, sk, picks, hit in CLIPS:
		for i, rc in enumerate(picks):
			c, m = frames[(fam, rc)]
			q = pal[((c[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)]
			img = np.zeros(c.shape[:2] + (4,), np.uint8); img[..., :3] = q; img[..., 3] = m * 255
			ys, xs = np.where(m)
			top = ys.min(); cap = m[top:top + max(4, (ys.max() - top) // 4)]
			hx = int(round(np.where(cap)[1].mean()))   # กลางหมวก/หัว
			canvas = Image.new("RGBA", (W, H))
			canvas.paste(Image.fromarray(img, "RGBA"), (CX - hx, FEET - ys.max()), Image.fromarray(img, "RGBA"))
			canvas.save(os.path.join(OUT, "%s_%d.png" % (fam, i)))
			if TO_GAME: canvas.save(os.path.join(GAME, "west_%s_%d.png" % (fam, i)))
		idx["clips"].append({"family": fam, "label": label, "sheet": sk, "n": len(picks), "hit": hit, "src": [list(p) for p in picks]})
	json.dump(idx, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	print("rion_px_weapons: ย่อ ×%.3f · %d เฟรม · พาเลตต์ %d สี (เดิม %d + ใหม่ %d) · ช่องที่เจอ %d" % (k, len(frames), len(pal), len(base), len(pal) - len(base), sum(len(g) for g in GOT.values())))


if __name__ == "__main__":
	main()
