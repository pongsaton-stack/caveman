"""ชีต VFX จาก Astra (kwan 19 ต.ค. · muse.ai "Reborner Vfx Designs") → พิกเซลขนาดเกม สำหรับแบบผสม (ภาพ Astra ช่วงกระทบ/หาง + โค้ดคุมการเคลื่อนที่)

ต้นฉบับ: docs/art-bible/vfx/astra/bk<n>-sheet-full.png (2240x1120 · 4x2 ช่อง ช่องละ 560 · พื้นเขียว · ทิศขวา → ซ้ายแล้ว) + sfx-bk<n>.wav
ลบพื้นเขียว · ลบกรอบดำที่วาดติดมา (แถว/คอลัมน์ใกล้ขอบที่มืดเกินครึ่งช่อง) · ล้างเขียวในควัน · ย่อ premultiplied BOX → 96 · ทึบ > 0.5 · สีร่วม ≤ 24 · ลบจุดโดด
  python3 tools/sprites/astra_vfx_cut.py → assets/sprites/astra_vfx_draft/bk<n>_<0-7>.png + index.json (ร่าง · .gdignore · หน้า animation test อ่านเอง)
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "docs/art-bible/vfx/astra")
OUT = os.path.join(ROOT, "assets/sprites/astra_vfx_draft")
CELL, SIZE, COLORS = 560, 96, 24
# เฟรมที่แบบผสมใช้ (ดูด้วยตา 19 ต.ค.): กระทบ = ระเบิด/หลุมวน · หาง = ควัน/เศษจาง · ช่วงเดินทางยังใช้โค้ด
SHEETS = {"bk1": {"hit": [5, 6], "tail": [7]}, "bk4": {"hit": [5, 6], "tail": [7]}}


def cell(im, i):
	x, y = (i % 4) * CELL, (i // 4) * CELL
	a = np.array(im.crop((x, y, x + CELL, y + CELL)).convert("RGB")).astype(int)
	r, g, b = a[..., 0], a[..., 1], a[..., 2]
	alpha = ~((g > r + 60) & (g > b + 60))
	dark = (a.sum(-1) < 150) & alpha
	frame = np.zeros_like(alpha)   # กรอบดำ: แถว/คอลัมน์ที่มืดเกินครึ่ง ± 3 จุด · เฉพาะใกล้ขอบช่อง (กลางช่องเป็นหลุมมืดของ BK-4 เอง)
	edge = lambda k: k < 40 or k >= CELL - 40
	for k in np.where(dark.mean(1) > 0.5)[0]:
		if edge(k): frame[max(0, k - 3):k + 4, :] = True
	for k in np.where(dark.mean(0) > 0.5)[0]:
		if edge(k): frame[:, max(0, k - 3):k + 4] = True
	alpha &= ~(frame & (a.sum(-1) < 200))
	a[..., 1] = np.minimum(g, np.maximum(r, b) + 12)   # ล้างเขียวที่ซึมในควันโปร่ง
	return a, alpha


def shrink(a, alpha):
	f = CELL // SIZE + (CELL % SIZE > 0)
	pad = f * SIZE - CELL
	a = np.pad(a, ((0, pad), (0, pad), (0, 0))); al = np.pad(alpha.astype(float), ((0, pad), (0, pad)))
	pre = (a * al[..., None]).reshape(SIZE, f, SIZE, f, 3).sum((1, 3))
	cov = al.reshape(SIZE, f, SIZE, f).sum((1, 3))
	rgb = np.where(cov[..., None] > 0, pre / np.maximum(cov, 1)[..., None], 0)
	keep = cov / (f * f) > 0.5
	lab, n = ndimage.label(keep)   # ลบจุดโดดเล็กกว่า 2 จุด
	if n:
		sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
		keep &= ~np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < 2])
	out = np.zeros((SIZE, SIZE, 4), np.uint8)
	out[..., :3] = rgb.clip(0, 255); out[..., 3] = keep * 255
	return Image.fromarray(out, "RGBA")


def main():
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	idx = {}
	for name, use in SHEETS.items():
		im = Image.open(os.path.join(SRC, f"{name}-sheet-full.png"))
		frames = [shrink(*cell(im, i)) for i in range(8)]
		pal = Image.new("RGB", (SIZE * 8, SIZE))   # สีร่วมทั้งชีต
		for i, f in enumerate(frames): pal.paste(f.convert("RGB"), (i * SIZE, 0), f)
		q = pal.quantize(COLORS, method=Image.MEDIANCUT)
		for i, f in enumerate(frames):
			rgb = f.convert("RGB").quantize(palette=q, dither=Image.NONE).convert("RGBA")
			rgb.putalpha(f.getchannel("A")); rgb.save(os.path.join(OUT, f"{name}_{i}.png"))
		idx[name] = dict(use, frames=[f"{name}_{i}" for i in range(8)], size=SIZE, sound=f"sfx-{name}.wav")
		print(name, "ok")
	json.dump({"_doc": "VFX จาก Astra ย่อเป็นพิกเซล 96 · tools/sprites/astra_vfx_cut.py · ร่าง", "sheets": idx},
		open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
	main()
