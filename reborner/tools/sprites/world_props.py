# tools/sprites/world_props.py — สิ่งก่อสร้าง + ยานพาหนะ (ร่าง · ยังไม่เข้าเกม)
# รายชื่อ/ที่มา: docs/art-bible/world/structures.json · vehicles.json (ไม่มีตัวเลขเกม)
# วาดด้วย pixkit (ลงเงาแสงบนซ้าย) · บางชิ้นมี 2-4 เฟรม (ไฟ/ควัน/ลอยน้ำ)
# ผล: assets/sprites/structures_draft/<id>_<i>.png · assets/sprites/vehicles_draft/<id>_<i>.png
import json, math, os
from pixkit import Sprite, ramp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STONE, WOOD, RUST, TIN, ASH, CLOTH = (128, 122, 112), (140, 98, 62), (150, 82, 50), (128, 136, 138), (96, 90, 84), (176, 150, 110)
FIRE = [(255, 246, 190), (255, 200, 80), (240, 120, 40), (190, 60, 30)]

def flame(s, cx, base, h, t):
	"""เปลวไฟ 3 ชั้น ไหวตาม t"""
	for i, (col, k) in enumerate(zip(FIRE[::-1], (1.0, 0.75, 0.5, 0.28))):
		hh = h * k + (1 if (t + i) % 2 else 0); w = max(1, round(h * k * 0.45))
		dx = (1 if t % 3 == 1 else -1 if t % 3 == 2 else 0) * (i > 1)
		s.flat(col, lambda d, w=w, hh=hh, dx=dx: d.polygon([(cx - w, base), (cx + w, base), (cx + dx, base - hh)]))

def smoke(s, x, y, t):
	for i in range(3):
		yy = y - 5 * i - (t % 2) * 2; r = 2 + i
		s.flat((150, 146, 140), lambda d, yy=yy, r=r, i=i: d.ellipse([x + i - r, yy - r, x + i + r, yy + r]), alpha=150 - 35 * i)

# ── สิ่งก่อสร้าง ──
def ash_kiln(t):
	s = Sprite(64, 64, 'kiln'); s.shadow(32, 60, 26, 3)
	s.part(STONE, lambda d: d.polygon([(10, 60), (14, 26), (22, 16), (42, 16), (50, 26), (54, 60)]), tex=0.3)
	s.part((112, 104, 96), lambda d: d.rectangle([24, 4, 34, 18]), tex=0.3)                                     # ปล่องควัน
	for y in (28, 38, 48):
		s.px([(x, y) for x in range(14, 51) if (x + y // 10) % 7], ramp(STONE)[1])                            # รอยก้อนหิน
	s.part((40, 30, 26), lambda d: d.pieslice([22, 36, 42, 64], 180, 360), tex=0)                               # ปากเตา
	s.flat(FIRE[3], lambda d: d.rectangle([24, 49, 40, 51]))
	flame(s, 32, 50, 9, t)
	smoke(s, 29, 2, t)
	return s

def rest_camp(t):
	s = Sprite(64, 48, 'camp'); s.shadow(32, 40, 26, 4)
	s.part(WOOD, lambda d: d.rounded_rectangle([4, 30, 22, 36], 3), tex=0.3)                                    # ท่อนไม้นั่ง
	s.part(WOOD, lambda d: d.rounded_rectangle([42, 30, 60, 36], 3), tex=0.3)
	for a in range(0, 360, 45):
		x, y = 32 + 10 * math.cos(math.radians(a)), 38 + 4 * math.sin(math.radians(a))
		s.part(STONE, lambda d, x=x, y=y: d.ellipse([x - 2, y - 2, x + 2, y + 2]), tex=0)
	s.part((90, 60, 40), lambda d: (d.line([(26, 40), (38, 34)], fill=255, width=2), d.line([(26, 34), (38, 40)], fill=255, width=2)))
	flame(s, 32, 37, 14, t)
	s.part((70, 70, 74), lambda d: (d.line([(23, 22), (32, 8), (41, 22)], fill=255, width=1)), light=False)     # ขาตั้งหม้อ
	s.part((60, 60, 64), lambda d: d.pieslice([27, 14, 37, 26], 0, 180), tex=0)
	return s

def scrap_stall(t):
	s = Sprite(80, 64, 'stall'); s.shadow(40, 61, 34, 3)
	s.part(WOOD, lambda d: (d.rectangle([10, 22, 12, 60]), d.rectangle([66, 22, 68, 60])))
	s.part((70, 120, 140), lambda d: d.polygon([(4, 24), (14, 10), (66, 10), (76, 24)]), tex=0.15)              # ผ้าใบ
	for x in range(8, 74, 8): s.px([(x + i, 24 + (i % 2)) for i in range(4)], (230, 220, 190))
	s.part(WOOD, lambda d: d.rectangle([8, 40, 70, 46]), tex=0.3)                                                # โต๊ะ
	s.part((110, 76, 48), lambda d: d.rectangle([10, 46, 68, 58]), tex=0.3)
	s.part((200, 170, 70), lambda d: d.ellipse([14, 32, 22, 40]))                                                # ของบนโต๊ะ: นาฬิกา
	s.part(TIN, lambda d: d.rectangle([26, 30, 36, 40]))                                                         # วิทยุ
	s.px([(28, 32), (30, 32), (32, 32), (34, 32)], (40, 40, 40))
	s.part((90, 170, 90), lambda d: d.rectangle([40, 33, 44, 40]))                                               # ขวด
	s.part((180, 60, 50), lambda d: d.rectangle([48, 34, 60, 40]))                                               # กล่อง
	s.part(CLOTH, lambda d: d.polygon([(62, 46), (74, 46), (72, 54), (64, 54)]))                                 # ป้ายราคา (ไม่มีตัวเลข)
	return s

def chest(t):
	s = Sprite(32, 32, 'chest'); s.shadow(16, 29, 13, 2)
	s.part(WOOD, lambda d: d.rectangle([4, 15, 28, 28]), tex=0.25)
	if t == 0: s.part((120, 80, 50), lambda d: d.pieslice([4, 6, 28, 24], 180, 360), tex=0.2)
	else:
		s.part((120, 80, 50), lambda d: d.polygon([(4, 15), (28, 15), (30, 6), (6, 4)]), tex=0.2)
		s.flat((255, 230, 140), lambda d: d.rectangle([7, 15, 25, 17]), alpha=220)
	s.part((200, 170, 70), lambda d: (d.rectangle([4, 15, 28, 16]), d.rectangle([14, 13, 18, 20])), tex=0)
	return s

def stone_gate(t):
	s = Sprite(80, 80, 'gate'); s.shadow(40, 77, 36, 3)
	s.part(STONE, lambda d: (d.rectangle([6, 14, 22, 76]), d.rectangle([58, 14, 74, 76])), tex=0.3)
	s.part((110, 104, 96), lambda d: d.rectangle([2, 4, 78, 16]), tex=0.3)
	s.part((70, 64, 60), lambda d: d.rectangle([22, 16, 58, 76]), tex=0.1, light=False)
	s.flat((120, 200, 230) if t else (80, 150, 180), lambda d: (d.ellipse([36, 6, 44, 14]), d.line([(40, 20), (40, 70)], fill=255)), alpha=230)   # อักขระเรือง
	for y in (30, 44, 58): s.flat((120, 200, 230) if t else (80, 150, 180), lambda d, y=y: d.line([(34, y), (46, y)], fill=255), alpha=200)
	return s

def well(t):
	s = Sprite(48, 56, 'well'); s.shadow(24, 53, 18, 3)
	s.part(STONE, lambda d: d.rectangle([6, 34, 42, 52]), tex=0.35)
	s.part((40, 50, 60), lambda d: d.ellipse([8, 30, 40, 38]), tex=0, light=False)
	s.part(WOOD, lambda d: (d.rectangle([7, 8, 10, 36]), d.rectangle([38, 8, 41, 36])))
	s.part((110, 76, 48), lambda d: d.polygon([(2, 12), (24, 2), (46, 12)]), tex=0.3)
	s.px([(24, y) for y in range(10, 22 + (t % 2))], (200, 190, 160))
	s.part(TIN, lambda d, t=t: d.rectangle([21, 22 + t, 27, 28 + t]))
	return s

def radio_tower(t):
	s = Sprite(48, 96, 'tower'); s.shadow(24, 93, 16, 3)
	s.part(RUST, lambda d: (d.line([(8, 92), (22, 6)], fill=255, width=2), d.line([(40, 92), (26, 6)], fill=255, width=2)), tex=0.2)
	for y in range(16, 92, 10):
		x0 = 8 + (92 - y) * 14 / 86; x1 = 40 - (92 - y) * 14 / 86
		s.part(RUST, lambda d, y=y, x0=x0, x1=x1: (d.line([(x0, y), (x1, y)], fill=255), d.line([(x0, y), (x1 - 2, y - 9)], fill=255)), light=False, outline=False)
	s.flat((255, 70, 60) if t else (110, 40, 36), lambda d: d.ellipse([21, 1, 27, 7]))     # ไฟเตือนกะพริบ
	s.part(TIN, lambda d: d.rectangle([28, 30, 36, 36]), tex=0)                            # จานเอียงหลุด
	return s

def signpost(t):
	s = Sprite(40, 48, 'sign'); s.shadow(20, 46, 10, 2)
	s.part(WOOD, lambda d: d.rectangle([18, 8, 22, 46]), tex=0.3)
	s.part(CLOTH, lambda d: d.polygon([(4, 12), (30, 12), (36, 17), (30, 22), (4, 22)]), tex=0.2)
	s.part(CLOTH, lambda d: d.polygon([(36, 26), (10, 26), (4, 31), (10, 36), (36, 36)]), tex=0.2)
	s.px([(8 + i, 17) for i in range(0, 18, 2)] + [(14 + i, 31) for i in range(0, 18, 2)], (70, 50, 36))
	return s

def power_pole(t):
	s = Sprite(56, 96, 'pole'); s.shadow(20, 93, 10, 2)
	s.part((110, 104, 96), lambda d: d.polygon([(16, 94), (22, 94), (36, 8), (31, 7)]), tex=0.25)            # เสาเอียง
	s.part(WOOD, lambda d: d.line([(22, 22), (50, 30)], fill=255, width=3))
	s.px([(50 - i // 3, 30 + i) for i in range(0, 50)], (40, 36, 34))                                     # สายไฟห้อย
	return s

def vending(t):
	s = Sprite(40, 64, 'vend'); s.shadow(20, 61, 16, 2)
	s.part((170, 60, 50), lambda d: d.rectangle([4, 4, 34, 60]), tex=0.3)
	s.part((70, 90, 100), lambda d: d.rectangle([8, 8, 24, 40]), tex=0.05, light=False)
	for y in (12, 22, 32):
		for x in (10, 15, 20): s.part((200, 190, 120) if (x + y) % 3 else (90, 160, 200), lambda d, x=x, y=y: d.rectangle([x, y, x + 3, y + 5]), tex=0, outline=False)
	s.part(TIN, lambda d: d.rectangle([26, 14, 31, 30]), tex=0)
	s.part((40, 36, 34), lambda d: d.rectangle([8, 46, 30, 54]), tex=0)
	s.flat((255, 240, 160) if t else (90, 90, 70), lambda d: d.rectangle([26, 10, 31, 12]))               # ไฟสถานะกะพริบ
	s.px([(6 + (i * 7) % 26, 6 + (i * 11) % 52) for i in range(14)], ramp(RUST)[1])                    # สนิม
	return s

def tin_fence(t):
	s = Sprite(80, 48, 'fence'); s.shadow(40, 45, 38, 2)
	cols = [TIN, RUST, (120, 140, 120), TIN, RUST]
	for i, c in enumerate(cols):
		x = 2 + i * 15; tilt = (i % 2) * 2
		s.part(c, lambda d, x=x, tilt=tilt: d.polygon([(x, 44), (x + 15, 44), (x + 15 + tilt, 8 + tilt), (x + tilt, 10)]), tex=0.2)
		for k in range(x + 2, x + 15, 3): s.px([(k + tilt // 2, y) for y in range(12, 43)], ramp(c)[2])
	s.part(WOOD, lambda d: d.rectangle([0, 22, 79, 24]), tex=0.2)
	return s

def bridge(t):
	s = Sprite(96, 48, 'bridge')
	s.flat((60, 100, 130), lambda d: d.rectangle([0, 30, 95, 47]))
	for x in range(0, 96, 6): s.px([(x + (t * 2) % 6, 34 + (x // 6) % 3 * 4)], (150, 200, 220))
	for x in (8, 30, 64, 86): s.part(WOOD, lambda d, x=x: d.rectangle([x, 22, x + 3, 46]), tex=0.3)
	s.part(WOOD, lambda d: d.polygon([(0, 20), (42, 20), (46, 26), (0, 26)]), tex=0.3)
	s.part(WOOD, lambda d: d.polygon([(58, 22), (95, 20), (95, 26), (54, 28)]), tex=0.3)                      # ช่วงที่หัก
	s.part((110, 76, 48), lambda d: d.line([(44, 26), (50, 40)], fill=255, width=2))                         # แผ่นไม้ห้อย
	return s

def garden(t):
	s = Sprite(64, 40, 'garden')
	s.part((90, 74, 60), lambda d: d.rectangle([2, 14, 62, 38]), tex=0.4)
	for r, y in enumerate((18, 26, 34)):
		for x in range(8, 60, 9):
			s.part((110, 150, 70) if r != 1 else (150, 140, 60), lambda d, x=x, y=y: d.polygon([(x, y), (x - 3, y - 6 - t), (x + 3, y - 6 + t)]), tex=0.1)
	s.part(WOOD, lambda d: (d.rectangle([0, 10, 2, 38]), d.rectangle([61, 10, 63, 38])))
	return s

def shrine(t):
	s = Sprite(48, 56, 'shrine'); s.shadow(24, 53, 18, 3)
	s.part(STONE, lambda d: d.rectangle([8, 40, 40, 52]), tex=0.3)
	s.part((150, 60, 50), lambda d: d.rectangle([12, 20, 36, 40]), tex=0.2)
	s.part((80, 60, 50), lambda d: d.polygon([(4, 22), (24, 6), (44, 22)]), tex=0.2)
	s.part((40, 30, 26), lambda d: d.rectangle([20, 28, 28, 40]), tex=0, light=False)
	s.flat(FIRE[1], lambda d: d.rectangle([23, 31 + (t % 2), 25, 34]))                                       # เทียน
	s.flat(FIRE[0], lambda d: d.point((24, 30 + (t % 2))))
	return s

# ── ยานพาหนะ ──
def wheel(s, cx, cy, r, t, col=(40, 38, 36)):
	s.part(col, lambda d: d.ellipse([cx - r, cy - r, cx + r, cy + r]), tex=0)
	s.part(TIN, lambda d: d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2]), tex=0)
	a = math.radians(t * 45); s.px([(round(cx + (r - 1) * math.cos(a)), round(cy + (r - 1) * math.sin(a)))], (150, 150, 150))

def cart(t):
	s = Sprite(48, 40, 'cart'); s.shadow(24, 38, 18, 2)
	s.part(TIN, lambda d: d.polygon([(6, 8), (42, 8), (38, 28), (10, 28)]), tex=0.1, light=False)
	for x in range(10, 40, 4): s.px([(x, y) for y in range(10, 27)], ramp(TIN)[1])
	s.part((190, 50, 40), lambda d: d.rectangle([2, 4, 10, 7]))                                              # ด้ามจับ
	s.part(TIN, lambda d: d.line([(10, 28), (12, 34)], fill=255, width=2))
	s.part((90, 140, 90), lambda d: d.ellipse([16, 2, 26, 10]))                                              # ของในรถ
	s.part(CLOTH, lambda d: d.rectangle([26, 2, 36, 10]))
	wheel(s, 12, 34, 3, t); wheel(s, 36, 34, 3, t)
	return s

def bicycle(t):
	s = Sprite(56, 40, 'bike'); s.shadow(28, 37, 22, 2)
	wheel(s, 12, 28, 9, t); wheel(s, 44, 28, 9, t)
	s.part(RUST, lambda d: (d.line([(12, 28), (24, 16), (38, 16), (44, 28)], fill=255, width=2), d.line([(24, 16), (28, 28), (38, 16)], fill=255, width=2)))
	s.part((40, 36, 34), lambda d: d.rectangle([20, 11, 28, 13]))                                           # อาน
	s.part(TIN, lambda d: d.line([(38, 16), (36, 8), (42, 8)], fill=255, width=2))
	s.part(WOOD, lambda d: d.rectangle([2, 14, 12, 20]))                                                     # ตะกร้าหลัง
	return s

def bus(t):
	s = Sprite(96, 56, 'bus'); s.shadow(48, 52, 46, 3)
	s.part((200, 160, 60), lambda d: d.rounded_rectangle([2, 8, 94, 46], 5), tex=0.3)
	s.part((60, 70, 70), lambda d: d.rectangle([8, 14, 90, 26]), tex=0.05, light=False)
	for x in range(8, 90, 12): s.px([(x, y) for y in range(14, 27)], ramp((200, 160, 60))[1])
	s.px([(30, 16), (31, 17), (32, 18), (33, 19), (66, 20), (67, 21), (68, 20)], (210, 220, 220))              # กระจกแตก
	s.part(RUST, lambda d: (d.ellipse([12, 30, 30, 44]), d.ellipse([60, 32, 80, 46]), d.rectangle([40, 38, 54, 44])), tex=0.4)
	s.part((110, 150, 70), lambda d: (d.polygon([(70, 8), (82, 2), (90, 8)]), d.ellipse([84, 30, 94, 44])), tex=0.3)   # หญ้าขึ้นบนหลังคา/ข้าง
	s.part((40, 38, 36), lambda d: (d.pieslice([10, 38, 28, 56], 180, 360), d.pieslice([66, 38, 84, 56], 180, 360)), tex=0)   # ล้อจมดิน
	return s

def pickup(t):
	s = Sprite(96, 48, 'truck'); s.shadow(48, 45, 44, 3)
	s.part((120, 130, 110), lambda d: d.polygon([(4, 34), (4, 22), (40, 22), (40, 34)]), tex=0.3)            # กระบะ
	s.part((120, 130, 110), lambda d: d.polygon([(40, 34), (44, 10), (70, 10), (82, 22), (92, 24), (92, 36), (40, 36)]), tex=0.3)
	s.part((60, 70, 70), lambda d: d.polygon([(47, 13), (66, 13), (74, 22), (47, 22)]), tex=0.05, light=False)
	s.part(RUST, lambda d: (d.ellipse([8, 24, 24, 32]), d.ellipse([60, 26, 74, 34])), tex=0.4)
	s.part(WOOD, lambda d: d.rectangle([10, 14, 30, 22]), tex=0.3)                                           # ลังในกระบะ
	wheel(s, 22, 38, 7, 0); wheel(s, 76, 38, 7, 0)
	if t: smoke(s, 4, 26, t)
	return s

def ox_cart(t):
	s = Sprite(80, 48, 'oxcart'); s.shadow(40, 45, 34, 3)
	s.part(WOOD, lambda d: d.rectangle([20, 18, 72, 32]), tex=0.3)
	for x in range(22, 72, 6): s.px([(x, y) for y in range(19, 32)], ramp(WOOD)[1])
	s.part(CLOTH, lambda d: d.chord([22, 2, 70, 30], 180, 360), tex=0.2)                                    # หลังคาผ้า
	s.part(WOOD, lambda d: d.line([(20, 28), (2, 30)], fill=255, width=2))                                   # คานลาก
	wheel(s, 34, 36, 9, t, (110, 76, 48)); wheel(s, 60, 36, 9, t, (110, 76, 48))
	return s

def raft(t):
	s = Sprite(64, 40, 'raft'); b = t % 2
	s.flat((60, 100, 130), lambda d: d.rectangle([0, 24, 63, 39]))
	for x in range(0, 64, 7): s.px([(x + 3 * b, 28 + (x // 7) % 2 * 5)], (150, 200, 220))
	for i in range(7): s.part(WOOD, lambda d, i=i: d.rounded_rectangle([6 + i * 7, 18 + b, 12 + i * 7, 30 + b], 2), tex=0.3)
	s.part(WOOD, lambda d: d.rectangle([30, 2 + b, 32, 20 + b]))
	s.part(CLOTH, lambda d: d.polygon([(33, 3 + b), (50, 10 + b), (33, 17 + b)]), tex=0.2)                   # ใบเรือผ้าปะ
	return s

def boat(t):
	s = Sprite(80, 40, 'boat'); b = t % 2
	s.flat((60, 100, 130), lambda d: d.rectangle([0, 26, 79, 39]))
	for x in range(0, 80, 8): s.px([(x + 4 * b, 30 + (x // 8) % 2 * 5)], (150, 200, 220))
	s.part((70, 110, 150), lambda d: d.polygon([(4, 16 + b), (76, 16 + b), (68, 30 + b), (12, 30 + b)]), tex=0.25)
	s.part(TIN, lambda d: d.rectangle([4, 15 + b, 76, 17 + b]), tex=0)
	s.part((40, 38, 36), lambda d: d.rectangle([66, 8 + b, 74, 18 + b]))                                     # เครื่องยนต์ (ไม่มีน้ำมัน)
	s.part(WOOD, lambda d: d.line([(20, 10 + b), (34, 24 + b)], fill=255, width=2))                          # ไม้พาย
	return s

def mine_cart(t):
	s = Sprite(48, 40, 'minecart'); s.shadow(24, 37, 20, 2)
	s.part((80, 70, 60), lambda d: (d.rectangle([0, 34, 47, 35]), d.rectangle([0, 37, 47, 38])), tex=0, light=False)
	for x in range(2 - t % 4, 48, 8): s.part(WOOD, lambda d, x=x: d.rectangle([x, 33, x + 3, 39]), tex=0, outline=False)
	s.part(RUST, lambda d: d.polygon([(6, 12), (42, 12), (38, 30), (10, 30)]), tex=0.3)
	s.part(STONE, lambda d: (d.ellipse([10, 6, 22, 16]), d.ellipse([20, 4, 34, 16]), d.ellipse([30, 8, 40, 16])), tex=0.3)
	wheel(s, 14, 31, 3, t); wheel(s, 34, 31, 3, t)
	return s

def scooter(t):
	s = Sprite(56, 40, 'scooter'); s.shadow(28, 37, 22, 2)
	s.part((90, 150, 160), lambda d: d.polygon([(12, 30), (16, 18), (34, 16), (42, 28)]), tex=0.3)
	s.part((90, 150, 160), lambda d: d.polygon([(40, 28), (44, 8), (48, 8), (46, 28)]), tex=0.2)
	s.part((40, 36, 34), lambda d: d.rectangle([16, 14, 30, 17]))
	s.part(TIN, lambda d: d.line([(42, 6), (52, 4)], fill=255, width=2))
	s.part(RUST, lambda d: d.ellipse([20, 20, 30, 28]), tex=0.4)
	wheel(s, 12, 32, 5, 0); wheel(s, 46, 32, 5, 0)
	return s

def tank(t):
	s = Sprite(96, 56, 'tank'); s.shadow(48, 52, 46, 3)
	s.part((80, 90, 70), lambda d: d.rounded_rectangle([4, 32, 92, 50], 8), tex=0.3)                        # สายพาน
	for x in range(12, 90, 10): s.part((60, 64, 56), lambda d, x=x: d.ellipse([x - 4, 36, x + 4, 46]), tex=0)
	s.part((96, 104, 80), lambda d: d.polygon([(10, 32), (16, 22), (84, 22), (88, 32)]), tex=0.3)
	s.part((96, 104, 80), lambda d: d.rounded_rectangle([30, 10, 66, 24], 4), tex=0.3)
	s.part((80, 90, 70), lambda d: d.polygon([(30, 15), (2, 22), (2, 25), (30, 19)]), tex=0.2)              # ลำกล้องเอียงลงดิน
	s.part(RUST, lambda d: (d.ellipse([40, 12, 56, 20]), d.ellipse([18, 24, 34, 30])), tex=0.4)
	s.part((110, 150, 70), lambda d: (d.ellipse([60, 2, 72, 12]), d.polygon([(62, 10), (70, 10), (66, 2)])), tex=0.3)   # ต้นไม้งอกจากป้อม
	s.part((120, 160, 80), lambda d: d.polygon([(4, 50), (10, 40), (14, 50)]), tex=0.2)
	return s

# id → (ฟังก์ชัน, จำนวนเฟรม)
STRUCT = {'ST-kiln': (ash_kiln, 3), 'ST-camp': (rest_camp, 3), 'ST-stall': (scrap_stall, 1), 'ST-chest': (chest, 2), 'ST-gate': (stone_gate, 2),
	'ST-well': (well, 2), 'ST-tower': (radio_tower, 2), 'ST-sign': (signpost, 1), 'ST-pole': (power_pole, 1), 'ST-vend': (vending, 2),
	'ST-fence': (tin_fence, 1), 'ST-bridge': (bridge, 3), 'ST-garden': (garden, 2), 'ST-shrine': (shrine, 2)}
VEH = {'VH-cart': (cart, 4), 'VH-bike': (bicycle, 4), 'VH-bus': (bus, 1), 'VH-truck': (pickup, 2), 'VH-oxcart': (ox_cart, 4),
	'VH-raft': (raft, 2), 'VH-boat': (boat, 2), 'VH-minecart': (mine_cart, 4), 'VH-scooter': (scooter, 1), 'VH-tank': (tank, 1)}

if __name__ == '__main__':
	for folder, table in (('structures_draft', STRUCT), ('vehicles_draft', VEH)):
		out = os.path.join(ROOT, 'assets/sprites', folder); os.makedirs(out, exist_ok=True); open(os.path.join(out, '.gdignore'), 'w').close()
		for f in os.listdir(out):
			if f.endswith('.png'): os.remove(os.path.join(out, f))
		for pid, (fn, n) in table.items():
			for t in range(n): fn(t).im.save(os.path.join(out, '%s_%d.png' % (pid, t)))
	print('ok', len(STRUCT), 'structures', len(VEH), 'vehicles')
