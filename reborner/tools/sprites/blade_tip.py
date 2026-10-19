"""หาปลายอาวุธคมในภาพท่าฟันทีละเฟรม (ไม่เสียเครดิต) → ใช้ทำรอยอาวุธตามปลายจริงในหน้า animation test (BLC_SWING)

ใบอาวุธ = ก้อนพิกเซลสีซีด (เทา/ขาวเงิน) ที่ผอมยาว ยื่นออกนอกตัว ใกล้มือ · ปลาย = ปลายก้อนข้างที่ไกลจุดศูนย์ถ่วงตัว
ใช้: python3 tools/sprites/blade_tip.py <ภาพ...> [--pivot X,Y] [--check out.png]
  --pivot  จุดหมุน (เช่น ไหล่) → พิมพ์มุม/รัศมีเป็นค่าแบบ BLC_SWING
  --dir    neg = มุมลดลงตลอด (หันซ้ายแล้วฟันข้ามหัวลงหน้า แบบ bl0) · pos = เพิ่มตลอด · ไม่ใส่ = หมุนทางที่สั้นกว่า (ข้ามหัวจะผิดทาง ต้องใส่ทิศ)
  --check  ภาพตรวจ ขยาย 4 เท่า: ใบที่เจอ = ชมพู · ปลาย = กากบาทแดง
เฟรมที่ไม่เจอใบ (มือบัง) พิมพ์ว่า "ไม่เห็น" — ห้ามเดาค่าแทน
"""
import colorsys, math, sys
from PIL import Image, ImageDraw

SKIN_HUE = (0.02, 0.11)
MAX_PTS = 24   # ใบมีดในผืน 120 ใหญ่สุด 17 จุด · เสื้อซีดท่ากระโดดเข่าพับ 31 จุด · อาวุธใบใหญ่ (ดาบ/ขวาน) ต้องขยายค่านี้


def is_skin(r, g, b):
	h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
	return SKIN_HUE[0] <= h <= SKIN_HUE[1] and 0.12 <= s <= 0.45 and v >= 0.85


def is_blade(r, g, b):   # เทา/เงิน/ขาวซีด (ไม่รวมผิว)
	h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
	return s < 0.22 and v > 0.4


def find_tip(path):
	"""คืน (ปลาย, ความยาว, จุดของใบ) หรือ None · ใบ = ก้อนซีด (≤ MAX_PTS จุด ยาว ≥ 4) ที่ปลายยื่นออกที่โล่ง และอยู่ห่างผิวไม่เกิน 9 จุด (ด้ามคั่นมือกับใบ · มือบางเฟรมอยู่หลังหัว)
	ปลาย = ปลายก้อนข้างที่ไกลจุดศูนย์ถ่วงตัว (ใบชี้ออกจากตัวเสมอ · ใช้ระยะจากมือไม่ได้ เพราะมีดชี้ลงแล้วปลายไปชิดผิวขา)"""
	im = Image.open(path).convert('RGBA'); W, H = im.size; px = im.load()
	op = lambda x, y: 0 <= x < W and 0 <= y < H and px[x, y][3] >= 128
	body = [(x, y) for y in range(H) for x in range(W) if op(x, y)]
	if not body: return None
	cx, cy = sum(p[0] for p in body) / len(body), sum(p[1] for p in body) / len(body); foot = max(p[1] for p in body)
	skin = [p for p in body if is_skin(*px[p][:3])]
	blade = {p for p in body if is_blade(*px[p][:3]) and not is_skin(*px[p][:3])}
	seen, best = set(), None
	for p in sorted(blade):
		if p in seen: continue
		comp, st = [], [p]; seen.add(p)
		while st:
			q = st.pop(); comp.append(q)
			for dx in (-1, 0, 1):
				for dy in (-1, 0, 1):
					n = (q[0] + dx, q[1] + dy)
					if n in blade and n not in seen: seen.add(n); st.append(n)
		if not 3 <= len(comp) <= MAX_PTS or not skin or min(math.hypot(q[0] - s[0], q[1] - s[1]) for q in comp for s in skin) > 9: continue
		a, b = max(((u, v) for u in comp for v in comp), key=lambda uv: math.hypot(uv[0][0] - uv[1][0], uv[0][1] - uv[1][1]))
		L = math.hypot(a[0] - b[0], a[1] - b[1])
		if L < 4: continue
		if max(q[1] for q in comp) > foot - 14 and abs(a[0] - b[0]) > abs(a[1] - b[1]): continue   # แถบนอนใกล้เท้า = ถุงเท้า (มีดชี้ลงแถวขาเป็นแนวตั้ง)
		tip = max((a, b), key=lambda t: math.hypot(t[0] - cx, t[1] - cy))
		# ปลายใบยื่นออกที่โล่ง: สัดส่วนพื้นโปร่งในกรอบ 7x7 รอบปลาย · วัดชุด bl (23 ภาพ): ใบจริง 0.33–0.67 · เสื้อ/ตา/ถุงเท้า ≤ 0.35 (ส่วนใหญ่ < 0.25)
		opn = sum(1 for i in range(-3, 4) for j in range(-3, 4) if not op(tip[0] + i, tip[1] + j)) / 49
		if opn < 0.3: continue
		score = opn * opn * L
		if best is None or score > best[3]: best = (tip, L, comp, score)
	return best and best[:3]


def main():
	args = sys.argv[1:]; pivot = check = sign = None
	if '--pivot' in args: i = args.index('--pivot'); pivot = tuple(map(float, args[i + 1].split(','))); del args[i:i + 2]
	if '--dir' in args: i = args.index('--dir'); sign = -1 if args[i + 1] == 'neg' else 1; del args[i:i + 2]
	if '--check' in args: i = args.index('--check'); check = args[i + 1]; del args[i:i + 2]
	res, prev = [], None
	for p in args:
		b = find_tip(p); res.append((p, b))
		if not b: print(p, 'ไม่เห็น'); continue
		(x, y), L, comp = b; line = f'{p} ปลาย ({x},{y}) ใบยาว {L:.1f} · {len(comp)} จุด'
		if pivot:
			a = math.degrees(math.atan2(y - pivot[1], x - pivot[0]))
			if prev is not None:
				if sign is None:
					while a > prev + 180: a -= 360
					while a < prev - 180: a += 360
				else:
					while sign * (a - prev) < 0: a += 360 * sign
					while sign * (a - prev) >= 360: a -= 360 * sign
			prev = a; line += f' · มุม {a:.1f} รัศมี {math.hypot(x - pivot[0], y - pivot[1]):.1f}'
		print(line)
	if check:
		ims = [Image.open(p).convert('RGBA') for p, _ in res]; W, H = ims[0].size; Z = 4
		out = Image.new('RGB', (W * Z * len(ims), H * Z), (200, 220, 200))
		for k, (im, (_, b)) in enumerate(zip(ims, res)):
			bg = Image.new('RGBA', im.size, (200, 220, 200, 255)); bg.alpha_composite(im); bg = bg.convert('RGB')
			if b:
				for q in b[2]: bg.putpixel(q, (255, 0, 255))
			bg = bg.resize((W * Z, H * Z), Image.NEAREST); d = ImageDraw.Draw(bg)
			if b: x, y = b[0]; cx, cy = x * Z + 2, y * Z + 2; d.line((cx - 8, cy, cx + 8, cy), fill=(255, 0, 0), width=2); d.line((cx, cy - 8, cx, cy + 8), fill=(255, 0, 0), width=2)
			out.paste(bg, (k * W * Z, 0))
		out.save(check)


if __name__ == '__main__':
	main()
