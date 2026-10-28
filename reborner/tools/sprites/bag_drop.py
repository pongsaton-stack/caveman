"""กระเป๋าเป้แยกชิ้น pls_bag_0 (kwan 28 ต.ค. "3" ปลดกระเป๋าก่อนหมุน windmill)
ตัดจากภาพยืน pls_idle_bl_0 (สีน้ำตาลฝั่งขวาของตัว = เป้ · ก้อนใหญ่สุด + เส้นขอบ) · จุดสีผิวที่ติดมาย้อมเป็นสีเป้
เรียกอัตโนมัติท้าย pixellab_rion_set.py (px_set ถูกล้างทุกครั้งที่สร้าง)
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage

PX = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), "assets/sprites/pixellab_draft/px_set")


def main():
	a = np.array(Image.open(os.path.join(PX, "pls_idle_bl_0.png")).convert("RGBA")).astype(int)
	r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
	brown = (al > 127) & (r > g + 15) & (g > b + 5) & (r > 90)
	xs = np.nonzero(al > 127)[1]
	m = brown & (np.arange(a.shape[1])[None, :] > (xs.min() + xs.max()) / 2 + 4)
	lab, n = ndimage.label(m)
	big = lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
	big = ndimage.binary_closing(big, iterations=1)
	keep = big | (ndimage.binary_dilation(big) & (al > 127))
	o = np.zeros_like(a)
	o[keep] = a[keep]
	skin = keep & (r > 200) & (g > 150) & (b > 120)
	o[skin, :3] = np.median(a[big & ~skin][:, :3], axis=0).astype(int)
	ys, xs = np.nonzero(keep)
	Image.fromarray(o.astype(np.uint8)).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(os.path.join(PX, "pls_bag_0.png"))
	print("pls_bag_0", xs.max() - xs.min() + 1, "x", ys.max() - ys.min() + 1)


if __name__ == "__main__":
	main()
