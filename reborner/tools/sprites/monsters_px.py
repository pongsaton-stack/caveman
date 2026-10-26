"""มอนภูมิภาค 1 พิกเซล 32-bit จากชีตรอบ 10 (Google Flow · kwan 16 ต.ค. 2026)
  python3 tools/sprites/monsters_px.py
ชีตรอบ 10 monster_trial_v10.jpg: สไลม์ หนอน (แถวละตัว 8 ช่อง) · ชีตรอบ 11 monster_trial_v11.jpg: หมาป่า ค้างคาว บอส (ตัวละ 2 แถว แถวละ 4) · หันขวาทั้งหมด
ทำ: ลบพื้นเขียว → ก้อนต่อแถว (ก้อนที่ช่วง x ซ้อนกัน = ตัวเดียว · ก้อนเล็กติดตัวที่ใกล้สุด) → ช่องตามตำแหน่ง x →
ย่อต่อตัว ให้สัดส่วนเทียบ Rion เท่ามอนในเกมเดิม (ความสูงเดิม × Rion ใหม่ 79 / Rion เดิม · ค้างคาวใช้ความกว้างปีก) →
พาเลตต์ร่วมทุกตัว 48 สี → ผืนต่อตัวขนาดเดียวทุกเฟรม: ตำแหน่งเทียบกลางช่องและเส้นพื้นของแถวเดิม (ท่ากระโดด/บินขึ้นลงยังอยู่)
ออก assets/sprites/monsters_px_draft/<id>_<i>.png + index.json (.gdignore · ร่าง ยังไม่เข้าเกม)"""
import glob, json, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHEETS = {"v10": os.path.join(ROOT, "docs/art-bible/rion_hires/monster_trial_v10.jpg"),
	"v11": os.path.join(ROOT, "docs/art-bible/rion_hires/monster_trial_v11.jpg"),
	# ชีตละตัว (kwan 19 ต.ค. ส่ง 5 ชีต "ใช้ได้ไหม" → "1" ตัดเป็นพิกเซลลงหน้าเทสคู่ชุดเดิม · 2 คอลัมน์ · โครงกระดูกแถวแรก 3)
	**{m: os.path.join(ROOT, "docs/art-bible/rion_hires/monster_sheet_%s.jpg" % m) for m in ("M02", "M04", "M05", "M07", "M08")}}   # รอบ 11 = เจนใหม่ หมาป่า/ค้างคาว/บอส ให้ตรงแบบ (แถวละ 4 ช่อง ตัวละ 2 แถว)
SHEET = SHEETS["v10"]
OUT = os.path.join(ROOT, "assets/sprites/monsters_px_draft")
GAME = os.path.join(ROOT, "assets/sprites/monsters_px")   # เข้าเกม (kwan 16 ต.ค. "ใส่เข้าเกม"): <id>_<บทบาท><ลำดับ>.png ตัดผืนให้ขอบล่าง = เส้นพื้น
EDGE = np.array([42, 26, 20])
# (id, ชื่อ, แถวในชีต [แถบที่ 0–5], จำนวนช่องต่อแถว (เลขเดียวหรือรายการต่อแถว), วัดขนาดด้วย [h สูง · w กว้าง · fit ด้านยาว = FIT],
#  ล้างขอบเขียวจาก JPG [none = ตัวเขียวเอง · edge = เฉพาะขอบ (มอสเขียวบนหลัง) · all = ทั้งตัว · glow = all + ลบแสงฟุ้งเหลืองเขียวรอบตะเกียง], บทบาทของแต่ละภาพตามลำดับ [skip = ไม่ใช้])
MONS = [
	("M01", "สไลม์เถ้า", [0], 8, "h", "none", ["idle", "idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	("M03", "หนอนหิน", [1], 8, "h", "edge", ["idle", "idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	("M06", "ค้างคาวเงา", ("v11", [2, 3]), 4, "w", "all", ["idle", "idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	("M15", "หมาป่า", ("v11", [0, 1]), 4, "h", "all", ["idle", "idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	("B1", "ราชาหนอนเถ้า", ("v11", [4, 5]), 4, "h", "all", ["idle", "idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	# ชุด 19 ต.ค. (ร่าง · ไม่เขียนลงเกม = NOT_GAME) · skip = ภาพที่เป็นเอฟเฟกต์ใหญ่/ของประกอบ (เมฆสปอร์ เป้าเล็ง กิ่งไม้ ควันตาย) — เอฟเฟกต์ทำด้วยโค้ด
	("M02", "หนูท่อ", ("M02", [0, 1, 2, 3]), 2, "fit", "all", ["idle", "wind", "idle", "wind", "atk", "follow", "hurt", "ko"]),
	("M04", "เห็ดพิษ", ("M04", [0, 1, 2, 3]), 2, "fit", "none", ["idle", "idle", "wind", "atk", "follow", "skip", "hurt", "ko"]),
	("M05", "กาสามตา", ("M05", [0, 1, 2, 3]), 2, "fit", "all", ["skip", "wind", "idle", "atk", "follow", "skip", "hurt", "ko"]),
	("M07", "ผีไฟป่า", ("M07", [0, 1, 2, 3]), 2, "fit", "all", ["idle", "skip", "hurt", "atk", "skip", "skip", "ko", "skip"]),
	("M08", "โครงกระดูกเดินเวร", ("M08", [0, 1, 2]), [3, 2, 2], "fit", "glow", ["idle", "idle", "wind", "atk", "follow", "hurt", "ko"]),
]
NOT_GAME = {"M02", "M04", "M05", "M07", "M08"}   # หน้าเทสเท่านั้น จนกว่า kwan อนุมัติ (เกมอ่าน assets/sprites/monsters_px เอง)
FIT = 47   # ด้านยาวของมอนช่อง S เดิม (monsters_ll กว้าง 47) ก่อนคูณสัดส่วน Rion · ตัวใหม่ไม่มีภาพเดิมให้เทียบ
OLD_RION = os.path.join(ROOT, "assets/sprites/rion_lastlight_draft/west.png")
NEW_RION = os.path.join(ROOT, "assets/sprites/rion_px/west_i0.png")
RATIO = 1.362   # = vis_h(NEW_RION) / vis_h(OLD_RION) ณ 16 ต.ค. (index.json rion_ratio)


def key_green(rgb):
	"""ตัดพื้นด้วยระยะสีจากสีพื้นจริง (มุมชีต) · สไลม์เขียวห่างจากพื้น ≥ 89 แต่พื้นห่างไม่เกิน ~4 → เกณฑ์ 20–60
	(สูตร "เขียวกว่าแดง/น้ำเงิน" แบบชีต Rion ลบตัวสไลม์ทิ้งทั้งตัว) · ขอบที่ผสมพื้นแยกสีพื้นออก"""
	bg = np.median(np.concatenate([rgb[:20].reshape(-1, 3), rgb[-20:].reshape(-1, 3)]), 0)
	d = np.sqrt(((rgb - bg) ** 2).sum(-1))
	a = np.clip((d - 20) / 40.0, 0, 1)
	am = np.maximum(a, 1e-3)[..., None]
	mix = ((a > 0) & (a < 1))[..., None]
	out = np.where(mix, (rgb - (1 - a)[..., None] * bg) / am, rgb).clip(0, 255)
	return out, a


def bands(m):
	on = m.sum(1) > 2; out = []; s = None
	for i, v in enumerate(on):
		if v and s is None: s = i
		if not v and s is not None: out.append((s, i)); s = None
	return [b for b in out if b[1] - b[0] > 40]


def figures(m, y0, y1, ncol, W):
	"""ก้อนในแถบ → [(ช่อง, mask เต็มแถบ)] · รวมก้อนที่ช่วง x ซ้อนกัน · ก้อนเล็กติดตัวที่ใกล้สุด"""
	band = m[y0:y1]
	lab, n = ndimage.label(ndimage.binary_closing(band, iterations=2))
	objs = ndimage.find_objects(lab); area = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
	ids = [i for i in range(n) if area[i] > 12]
	big = sorted([i for i in ids if area[i] > 1500], key=lambda i: objs[i][1].start)
	groups = []
	for i in big:   # ช่วง x ซ้อน = ตัวเดียว (เช่น สไลม์ยืดตัวกับแอ่งใต้ตัวแยกกัน)
		x0, x1 = objs[i][1].start, objs[i][1].stop
		ov = (groups[-1][1] - x0) if groups else 0   # ซ้อนเกิน 40% ของก้อนที่แคบกว่า = ตัวเดียว (ซ้อนนิดเดียว = หยดน้ำกระเด็นไปชนตัวข้าง ๆ)
		if groups and ov > 0.4 * min(x1 - x0, groups[-1][1] - groups[-1][0]): groups[-1][1] = max(groups[-1][1], x1); groups[-1][2].append(i)
		else: groups.append([x0, x1, [i]])
	for i in ids:
		if i in big: continue
		cx = (objs[i][1].start + objs[i][1].stop) / 2
		g = min(groups, key=lambda g: 0 if g[0] <= cx <= g[1] else min(abs(cx - g[0]), abs(cx - g[1])))
		if g[0] - 60 <= cx <= g[1] + 60: g[2].append(i)
	cw = W / ncol
	return [(int(((g[0] + g[1]) / 2) // cw), np.isin(lab, [i + 1 for i in g[2]])) for g in groups]


def shrink(rgb, al, k):
	pre = np.dstack([rgb * al[..., None], al * 255]).clip(0, 255).astype(np.uint8)
	h, w = al.shape; nw, nh = max(1, round(w * k)), max(1, round(h * k))
	sm = np.array(Image.fromarray(pre, "RGBA").resize((nw, nh), Image.BOX)).astype(float)
	A = sm[..., 3] / 255
	c = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	m = A > 0.5; e = m & ~ndimage.binary_erosion(m)
	c[e] = c[e] * .35 + EDGE * .65
	return c, m


def vis_h(path):
	m = np.array(Image.open(path).convert("RGBA"))[..., 3] > 0; ys, xs = np.where(m)
	return ys.max() - ys.min() + 1, xs.max() - xs.min() + 1


def main():
	SH = {}
	for sk, path in SHEETS.items():
		rgb, a = key_green(np.array(Image.open(path).convert("RGB")).astype(float))
		m = ndimage.binary_opening(a > 0.5, iterations=1)
		SH[sk] = (rgb, a, m, bands(m))
	# สัดส่วนล็อกไว้ที่ค่าตอนมอนเข้าเกม 16 ต.ค. (×1.362) · คิดใหม่จาก NEW_RION ตอนนี้ได้ ×1.07 (Rion ในเกมเปลี่ยนชุดภาพแล้ว) → มอนในเกมจะเปลี่ยนขนาดโดยไม่ได้ตั้งใจ (19 ต.ค.)
	ratio = RATIO
	cuts = {}
	for mid, name, rows, ncol, dim, spill, roles in MONS:
		sk, rows = rows if isinstance(rows, tuple) else ("v10", rows)   # แถวในชีตไหน
		rgb, a, m, bd = SH[sk]; H0, W0 = m.shape
		ncols = ncol if isinstance(ncol, list) else [ncol] * len(rows)
		fr = []
		for ri, r in enumerate(rows):
			y0, y1 = bd[r]
			for col, mk in sorted(figures(m, y0, y1, ncols[ri], W0), key=lambda t: t[0]):
				fr.append((ri * 100 + col, mk, y0, y1, ncols[ri]))   # ลำดับ = แถว·ช่อง · ช่อง = slot % 100 (แถวกว้างไม่เท่ากัน เช่น 3+2+2)
		assert len(fr) == len(roles), (mid, len(fr), len(roles))
		fr = [f for f, r in zip(fr, roles) if r != "skip"]; roles = [r for r in roles if r != "skip"]
		# เส้นพื้นต่อแถว = จุดต่ำสุดในแถว · ตัวบิน (dim "w"): แถวที่ไม่มีภาพล้ม (ทุกภาพลอย) ใช้ความสูงบินที่วัดจากแถวที่มีภาพล้มบนพื้น
		bot = lambda f: np.where(f[1])[0].max()
		bases = {y0: max(bot(f) for f in fr if f[2] == y0) for y0 in {f[2] for f in fr}}
		if dim == "w":
			ko_row = fr[roles.index("ko")][2]
			lift = bases[ko_row] - max(bot(f) for i, f in enumerate(fr) if f[2] == ko_row and roles[i] != "ko")
			for y0 in bases:
				if y0 != ko_row: bases[y0] += lift
		ys, xs = np.where(fr[0][1])
		if dim == "fit":
			k = FIT * ratio / max(ys.max() - ys.min() + 1, xs.max() - xs.min() + 1)
		else:
			oh, ow = vis_h(os.path.join(ROOT, "assets/sprites/monsters_ll/%s.png" % mid))
			k = (oh * ratio) / (ys.max() - ys.min() + 1) if dim == "h" else (ow * ratio) / (xs.max() - xs.min() + 1)
		out = []
		for slot, mk, y0, y1, ncol in fr:
			ys, xs = np.where(mk); bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
			crop = rgb[y0:y1][by0:by1, bx0:bx1].copy(); mc = mk[by0:by1, bx0:bx1]
			if spill != "none":   # สีเขียวเกิน แดง/น้ำเงิน → ตัดลง (พื้นเขียวซึมขอบตอนบีบ JPG)
				zone = mc if spill in ("all", "glow") else mc & ~ndimage.binary_erosion(mc, iterations=4)
				if spill == "glow":   # แสงฟุ้งรอบตะเกียง = เหลืองผสมพื้นเขียว (เขียว > แดง) · ไส้ตะเกียงจริงแดง ≥ เขียว ไม่โดน
					mk = mk.copy(); mk[by0:by1, bx0:bx1] &= ~(mc & (crop[..., 1] > crop[..., 0] + 10) & (crop[..., 1] > crop[..., 2] + 40))
					mc = mk[by0:by1, bx0:bx1]
				mx = np.maximum(crop[..., 0], crop[..., 2]) + 8
				crop[..., 1] = np.where(zone, np.minimum(crop[..., 1], mx), crop[..., 1])
			c, mm = shrink(crop, np.where(mk, a[y0:y1], 0)[by0:by1, bx0:bx1], k)
			cw = W0 / ncol; ccx = (slot % 100 + 0.5) * cw; base = bases[y0]
			out.append((c, mm, (bx0 - ccx) * k, (by0 - base) * k))   # มุมซ้ายบนเทียบ (กลางช่อง, เส้นพื้นของแถว)
		cuts[mid] = (name, roles, k, out)
	# พาเลตต์ต่อตัว 32 สี: 24 ตามจำนวนพิกเซล + 8 จากสีไม่ซ้ำ (ตาส้ม/ประกายจุดเล็กได้สีของตัวเอง)
	# (พาเลตต์ร่วมทุกตัว ทำให้ไฮไลต์ของหนอนไปได้สีเขียวอ่อนของสไลม์ เมื่อมอนชุดอื่นเปลี่ยน)
	def palette(o):
		px = np.concatenate([c[mm] for c, mm, _, _ in o]).astype(np.uint8)
		p1 = np.array(Image.fromarray(px[None]).quantize(24, method=Image.MEDIANCUT).convert("RGB")).reshape(-1, 3)
		uq = np.unique(px // 16 * 16 + 8, axis=0)
		p2 = np.array(Image.fromarray(uq[None]).quantize(min(8, len(uq)), method=Image.MEDIANCUT).convert("RGB")).reshape(-1, 3)
		return np.unique(np.vstack([p1, p2]), axis=0).astype(float)
	os.makedirs(OUT, exist_ok=True); os.makedirs(GAME, exist_ok=True)
	for f in glob.glob(os.path.join(OUT, "*.png")) + glob.glob(os.path.join(GAME, "*.png")): os.remove(f)   # GAME เขียนใหม่เฉพาะตัวที่ไม่อยู่ใน NOT_GAME
	idx = {"_doc": __doc__.split("\n")[0], "palette": "ต่อตัว ≤ 32", "rion_ratio": round(ratio, 3), "monsters": []}
	for mid, (name, roles, k, out) in cuts.items():
		pal = palette(out)
		L = min(ox for _, _, ox, _ in out); R = max(ox + c.shape[1] for c, _, ox, _ in out)
		T = min(oy for _, _, _, oy in out); B = max(oy + c.shape[0] for c, _, _, oy in out)
		pad = 2; W, H = int(np.ceil(R - L)) + 2 * pad, int(np.ceil(B - T)) + 2 * pad
		ax, fy = int(round(-L)) + pad, int(round(-T)) + pad   # จุดยึด = กลางช่อง · เส้นพื้น
		for i, (c, mm, ox, oy) in enumerate(out):
			q = pal[((c[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)]
			img = np.zeros(c.shape[:2] + (4,), np.uint8); img[..., :3] = q; img[..., 3] = mm * 255
			cv = Image.new("RGBA", (W, H)); im = Image.fromarray(img, "RGBA")
			cv.paste(im, (int(round(ax + ox)), int(round(fy + oy))), im)
			cv.save(os.path.join(OUT, "%s_%d.png" % (mid, i)))
			nth = roles[:i].count(roles[i])
			if mid not in NOT_GAME:
				cv.crop((0, 0, W, fy + 1)).save(os.path.join(GAME, "%s_%s%d.png" % (mid, roles[i], nth)))   # BattleScreen/WorldEnemy วางขอบล่างผืนบนพื้น
		idx["monsters"].append({"id": mid, "name": name, "n": len(out), "roles": roles, "scale": round(k, 4), "size": [W, H], "anchor": [ax, fy]})
	json.dump(idx, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	print("monsters_px: Rion ใหม่/เดิม ×%.2f · พาเลตต์ต่อตัว ≤ 32 สี · " % ratio + " · ".join("%s %d ภาพ ×%.3f %dx%d" % (x["id"], x["n"], x["scale"], *x["size"]) for x in idx["monsters"]))


if __name__ == "__main__":
	main()
