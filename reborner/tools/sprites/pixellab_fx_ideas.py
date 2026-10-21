"""เอฟเฟกต์ที่ PixelLab วาดติดมาในท่า Rion → เก็บแยกเป็นคลังไอเดีย (kwan 21 ต.ค. "พวกเอฟเฟคโจมตีที่ pixellab เจน แยกเก็บไว้ที่ pixellab animation test ไว้ด้วย ไว้เป็นไอเดีย")

clean() ใน pixellab_rion_set.py ลบเส้นฟาด/วงหมัด/ประกายออกจากตัวละคร · ที่นี่เก็บส่วนที่ถูกลบ (ตัวละครไม่เอา) ทุกเฟรม ตำแหน่งเดิมในผืน
อ่านทุกท่าของ Rion ใน catalog.json (ภาพดิบ ไม่ใช่ภาพนิ่ง) · ก้อนเล็กกว่า MIN_BLOB จุด = เศษขอบ ทิ้ง · ท่าที่เอฟเฟกต์รวมน้อยกว่า MIN_TOTAL ไม่เก็บ
  python3 tools/sprites/pixellab_fx_ideas.py → assets/sprites/pixellab_draft/fx_ideas/<ท่า>/west/frame_XXX.png + แถว catalog (หมวดเอฟเฟกต์ · entity fx_ideas)
แล้วสร้างหน้ามาสเตอร์ใหม่: python3 tools/web/pixellab_test_build.py <out.html> · ร่าง (ไอเดียเท่านั้น ไม่ใช่ VFX ของเกม · VFX เกมทำด้วยโค้ด kwan 18 ต.ค.)
"""
import glob, json, os, shutil, sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(__file__))
from pixellab_rion_set import clean

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets/sprites/pixellab_draft/fx_ideas")
CAT = os.path.join(ROOT, "docs/art-bible/pixellab_test/catalog.json")
MIN_BLOB, MIN_TOTAL = 6, 120
SKIP = {"walk", "walk_ns", "idle_bl", "idle_bt", "idle_pt", "idle_rg", "idle_dv", "idle_fs"}   # ท่าเดิน/ยืน ไม่มีเอฟเฟกต์โจมตี (ที่ลบเป็นเศษขอบ/แว่น)


def effect(im, ref):
	a = np.array(im)
	kept = np.array(clean(im, ref)[0])[..., 3] > 0
	fx = (a[..., 3] > 127) & ~kept
	lab, n = ndimage.label(fx, structure=np.ones((3, 3)))
	if n:   # ก้อนเล็ก = เศษขอบ · ก้อนที่สีอิ่มส่วนใหญ่ตรงสีตัว Rion (หมวก ผม เป้ ผิว มีด) = ชิ้นตัวที่ clean() ตัดทิ้ง ไม่ใช่เอฟเฟกต์
		r = np.array(ref); pal = np.unique(r[r[..., 3] > 127][:, :3], axis=0).astype(int); rgb = a[..., :3].astype(int)
		near = np.min(((rgb.reshape(-1, 1, 3) - pal[None]) ** 2).sum(-1), axis=1).reshape(a.shape[:2]) < 20 ** 2
		bodyish = near & (rgb.max(-1) - rgb.min(-1) > 40)
		keep = [i for i in range(1, n + 1) if (lab == i).sum() >= MIN_BLOB and bodyish[lab == i].mean() < 0.4]
		fx = np.isin(lab, keep)
	out = a.copy(); out[~fx] = 0
	return Image.fromarray(out, "RGBA"), int(fx.sum())


def main():
	cat = json.load(open(CAT, encoding="utf-8"))
	rion = next(e for e in cat["entities"] if e["id"] == "rion")
	shutil.rmtree(OUT, ignore_errors=True)
	rows = []
	for an in rion["anims"]:
		if an["kind"] == "still" or an["id"] in SKIP: continue
		for d, folder in an["dirs"].items():
			src = os.path.join(ROOT, folder)
			files = sorted(glob.glob(os.path.join(src, "frame_*.png")))
			rot = os.path.join(src, "..", "..", "..", "rotations", d + ".png")
			if not files or not os.path.exists(rot): continue
			ref = Image.open(rot).convert("RGBA")
			res = []
			for f in files:
				im = Image.open(f).convert("RGBA")
				res.append(effect(im, ref if ref.size == im.size else ref.resize(im.size)))
			total = sum(n for _, n in res)
			if total < MIN_TOTAL: print("ข้าม", an["id"], total); continue
			dst = os.path.join(OUT, an["id"], d); os.makedirs(dst)
			for i, (im, _) in enumerate(res): im.save(os.path.join(dst, f"frame_{i:03d}.png"))
			busy = [i for i, (_, n) in enumerate(res) if n >= MIN_BLOB]
			rows.append({"id": f"fx_{an['id']}", "name": f"เอฟเฟกต์จาก {an['name']}", "kind": "attack", "status": "draft",
				"date": "2026-10-21", "gens": 0, "seed": an.get("seed"), "dirs": {d: os.path.relpath(dst, ROOT)}, "mirror": an.get("mirror"),
				"prompt": an.get("prompt"), "ms": an.get("ms", 90), "game_ms": None,
				"notes": f"ส่วนที่ clean() ลบออกจากท่า {an['id']} (ภาพดิบ {folder}) · {total} จุด · มีเอฟเฟกต์เฟรม {busy} · ไอเดียเท่านั้น ไม่เสียเครดิตเพิ่ม"})
			print(an["id"], d, total, busy)
	cat["entities"] = [e for e in cat["entities"] if e["id"] != "fx_ideas"] + [{"id": "fx_ideas", "cat": "vfx",
		"name": "คลังไอเดีย · เอฟเฟกต์ที่ PixelLab วาดติดมา", "anims": rows}]
	with open(CAT, "w", encoding="utf-8") as fh:
		json.dump(cat, fh, ensure_ascii=False, indent=2); fh.write("\n")
	print(len(rows), "ท่า")


if __name__ == "__main__":
	main()
