"""ท่าเดินแผนที่จาก PixelLab (kwan 30 ต.ค. "ท่าเดินก็ไม่ผ่าน") — แทนชุด rion_px เดิม (ขาแทบไม่ขยับ)
ต้นทาง: assets/sprites/pixellab_draft/zip/Idle/animations/walk*/<ทิศ>/frame_*.png (8 เฟรม · ผืน 124–128)
→ assets/sprites/rion_walk_pl/<ทิศ>_w<n>.png ผืน 96x112 เท้าแถว 110 (ตำแหน่งเดียวกับ rion_px · Overworld ใช้ HERO_FEET_OFFSET เดิมได้)
ตะวันตก = พลิกตะวันออก · จัดกลางทั้งชุดด้วยค่าเฉลี่ยกึ่งกลาง (ไม่จัดทีละเฟรม กันตัวสั่น)
"""
import glob
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "assets/sprites/pixellab_draft/zip/Idle/animations")
OUT = os.path.join(ROOT, "assets/sprites/rion_walk_pl")
W, H, FEET = 96, 112, 110
DIRS = {"east": "walk/east", "south": "walk_v-eb599d32/south", "north": "walk_v/north"}


def load(d):
	return [Image.open(f).convert("RGBA") for f in sorted(glob.glob(os.path.join(SRC, d, "frame_*.png")))]


def place(frames):
	boxes = [f.getbbox() for f in frames]
	cx = sum((b[0] + b[2]) / 2 for b in boxes) / len(boxes)
	bot = max(b[3] for b in boxes)
	out = []
	for f in frames:
		c = Image.new("RGBA", (W, H))
		c.alpha_composite(f, (int(round(W / 2 - cx)), FEET - bot))
		out.append(c)
	return out


def main():
	os.makedirs(OUT, exist_ok=True)
	sets = {k: place(load(v)) for k, v in DIRS.items()}
	sets["west"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in sets["east"]]
	for d, frames in sets.items():
		for i, f in enumerate(frames):
			f.save(os.path.join(OUT, "%s_w%d.png" % (d, i)))
		print(d, len(frames))


if __name__ == "__main__":
	main()
