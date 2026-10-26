#!/usr/bin/env python3
# ภาพ master ไม่มีนาฬิกา (kwan 18 ต.ค. 2026 เลือก "1": เอานาฬิกาออกจากแบบ Rion)
# แถบข้อมือที่มีนาฬิกา วาดแขนใหม่แบบเดียวกับต้นฉบับ: เส้นขอบเข้มซ้าย/ขวา + สีผิว · ขอบแขนเลื่อนเป็นเส้นตรงจากแถวเหนือแถบถึงแถวใต้แถบ (วัดจากภาพ)
# ส่วนหน้าปัดที่ยื่นนอกแขน → สีพื้นเขียว
import os
import numpy as np
from PIL import Image

D = os.path.join(os.path.dirname(__file__), "..", "..", "docs/art-bible/rion_hires")
SRC, OUT = os.path.join(D, "rion_master_v1.jpg"), os.path.join(D, "rion_master_v2.png")
YA, YB = 1585, 1702                       # แถวแขนสะอาดเหนือ/ใต้นาฬิกา (นาฬิกาสีน้ำเงิน y 1600–1682)
LA, RA, LB, RB = 1000, 1142, 1046, 1185   # ขอบนอกแขน ซ้าย/ขวา ที่ YA และ YB
OL = 15                                   # ความหนาเส้นขอบ
X_END = 1230                              # ขวาสุดที่หน้าปัดยื่นไปถึง

a = np.array(Image.open(SRC).convert("RGB")).astype(np.int32)
skin, ink, bg = a[1580, 1070].copy(), a[1585, 1007].copy(), a[1640, 1225].copy()
for y in range(YA + 1, YB):
	t = (y - YA) / (YB - YA)
	L, R = round(LA + (LB - LA) * t), round(RA + (RB - RA) * t)
	a[y, L:L + OL] = ink
	a[y, L + OL:R - OL] = skin
	a[y, R - OL:R] = ink
	a[y, R:X_END] = bg
Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(OUT)
print(OUT)
