"""ชีตอาวุธ 300 ชิ้น (kwan ส่ง 18 ต.ค. 2026 · 6 ชีต × 10 ชนิด × 5 ระดับ · JPG พื้นเขียว) → ข้อมูล + ไอคอนพิกเซล
  python3 tools/sprites/weapons300_cut.py
ชีต docs/art-bible/weapons/sheet300/<สาย>.jpg (แถว = ชนิด · คอลัมน์ = ระดับ 1–5)
ตัด: ตัดพื้นเขียวตามระยะสีจากสีขอบชีต (แสงเรืองโปร่งแยกสีพื้นออก ไม่ตัดสีเขียวของตัวอาวุธ) → แยกก้อน → จัดเข้าช่องตามจุดกลางก้อน (ภาพที่ล้นเส้นตารางไม่ขาด)
ไอคอน: icon() ของ weapons_icons_px.py (ย่อ BOX อัตราเดียวทั้งชีต · ขอบเข้ม · ≤16 สี) → assets/sprites/weapons300_draft/<id>.png (32) + <id>_48.png (.gdignore · ร่าง)
ข้อมูล: docs/art-bible/weapons/weapons300.json — ชื่อเป็นร่าง (ชนิด + คำต่อท้ายระดับ) · ไม่มีค่าพลัง/ราคา (kwan กำหนด) · branch = กิ่งที่ชี้ทาง (skill17_content.py)
ภาพตรวจ docs/art-bible/weapons/weapons300_check.png
ข้อจำกัด: ระดับ 4–5 ราว 11 ชิ้น (CR06/08/09-5 · BD01/02/07/08/09/10-5 · BD09/10-4) แสงเรืองในชีตทับกับช่องข้างจนติดเศษมา — ต้องลบมือหรือขอชีต PNG ที่เว้นระยะ
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(ROOT, "tools", "data"))
from weapons_icons_px import icon  # noqa: E402
from skill17_content import WEAPONS  # noqa: E402

SHEETS = os.path.join(ROOT, "docs/art-bible/weapons/sheet300")
OUT = os.path.join(ROOT, "assets/sprites/weapons300_draft")
DATA = os.path.join(ROOT, "docs/art-bible/weapons/weapons300.json")
CHECK = os.path.join(ROOT, "docs/art-bible/weapons/weapons300_check.png")
SCHOOL = {"SL": "คม", "PC": "แทง", "CR": "ทุบ", "ST": "ยิง", "DV": "กล", "BD": "มือเปล่า"}
TYPES = {   # ลำดับแถวในชีต (ดูด้วยตา 18 ต.ค.)
	"SL": ["มีดครัว", "มีดสับ", "กรรไกร", "คัตเตอร์", "เลื่อย", "มีดโกน", "ขวาน", "เคียว", "มีดสั้น", "กรรไกรตัดกิ่ง"],
	"PC": ["หอกไม้ไผ่", "ส้อม", "ตะปู", "เข็มเย็บ", "ไขควง", "ตะเกียบ", "เข็มฉีดยา", "ดอกสว่าน", "ฉมวก", "ไม้เสียบ"],
	"CR": ["ค้อน", "ประแจ", "กระทะ", "ไม้นวดแป้ง", "ไม้กวาด", "อิฐ", "ดัมเบล", "ท่อเหล็ก", "หนังสือ", "ค้อนปอนด์"],
	"ST": ["ปืนฉีดน้ำ", "ธนู", "ไม้ซาง", "ขวดสเปรย์", "สายยางหัวฉีด", "ถังดับเพลิง", "ปืนพลุกระดาษ", "ปืนกล/ลูกซอง*", "ปืนพก*", "พลุจรวด"],
	"DV": ["โดรน", "คีม", "หัวเทียน", "แบตเตอรี่", "สายพาน", "แม่แรง", "กล่องเครื่องมือ", "เครื่องเจียร", "แขนกล", "สายพ่วงแบต"],
	"BD": ["สนับมือ", "ผ้าพันมือ", "กรงเล็บ", "ใบมีดคู่", "นวม MMA", "ถุงมือเกราะ", "สนับมือหนาม", "นวมมวย", "ถุงมือหนัง", "สายรัดข้อมือ"],
}
TIER = ["", "ชั้นดี", "ดัดแปลง", "ไฮเทค", "ตำนาน"]   # ระดับ 1–5 ตามภาพ: ธรรมดา · วัสดุดีขึ้น · หนาม/ดัดแปลง · เรืองแสง/กลไก · แสงเรืองระดับตำนาน
GRIP = {   # แบบการจับ → ท่าถือที่ต้องมี (ท่าที่ยังไม่มี = needs_pose)
	"มือเดียวสั้น": ["มีดครัว", "มีดสับ", "กรรไกร", "คัตเตอร์", "มีดโกน", "มีดสั้น", "กรรไกรตัดกิ่ง", "เคียว", "ส้อม", "ตะปู", "เข็มเย็บ", "ไขควง", "ตะเกียบ", "เข็มฉีดยา",
		"ค้อน", "ประแจ", "กระทะ", "ไม้นวดแป้ง", "คีม", "หัวเทียน", "ขวาน", "เลื่อย"],
	"ยาว/สองมือ": ["หอกไม้ไผ่", "ฉมวก", "ไม้เสียบ", "ดอกสว่าน", "ไม้กวาด", "ท่อเหล็ก", "ดัมเบล", "ค้อนปอนด์"],
	"เล็ง": ["ปืนฉีดน้ำ", "ไม้ซาง", "ขวดสเปรย์", "สายยางหัวฉีด", "ถังดับเพลิง", "ปืนพลุกระดาษ", "ปืนกล/ลูกซอง*", "ปืนพก*", "เครื่องเจียร"],
	"สวมมือ": ["สนับมือ", "ผ้าพันมือ", "กรงเล็บ", "ใบมีดคู่", "นวม MMA", "ถุงมือเกราะ", "สนับมือหนาม", "นวมมวย", "ถุงมือหนัง", "สายรัดข้อมือ"],
	"ง้างธนู (ยังไม่มีท่า)": ["ธนู"],
	"ขว้าง (ยังไม่มีท่า)": ["อิฐ", "หนังสือ", "พลุจรวด"],
	"ฟาดแบบแส้ (ยังไม่มีท่า)": ["สายพาน", "สายพ่วงแบต"],
	"ของลอย/ตั้งพื้น (ยังไม่มีท่า)": ["โดรน", "แขนกล", "แม่แรง", "กล่องเครื่องมือ", "แบตเตอรี่"],
}
GRIP_OF = {w: g for g, ws in GRIP.items() for w in ws}


def key(rgb):
	b = np.concatenate([rgb[:6].reshape(-1, 3), rgb[-6:].reshape(-1, 3), rgb[:, :6].reshape(-1, 3), rgb[:, -6:].reshape(-1, 3)])
	bg = np.median(b, 0)
	d = np.sqrt(((rgb - bg) ** 2).sum(-1)); a = np.clip((d - 28) / 50.0, 0, 1)
	# ขอบโปร่ง/แสงเรือง: แยกสีพื้นออก (unmix) · จุดทึบไม่แตะ → อาวุธสีเขียวจริง (ไผ่ ขวดพิษ) ยังเขียว
	out = np.where((a < 1)[..., None], (rgb - (1 - a)[..., None] * bg) / np.maximum(a, 1e-3)[..., None], rgb).clip(0, 255)
	return out, a


def cut(code):
	"""ทีละช่อง: ครอปเผื่อขอบ 18% → สีพื้นจากขอบครอปนั้น (พื้นชีต BD ไล่สี) → แกนทึบ (a>0.8) เป็นก้อน ·
	เก็บก้อนที่จุดกลางอยู่ในช่อง → ขยายกลับ 8 จุดให้ได้แสงเรือง/ขอบโปร่ง (แสงเรืองของช่องข้างไม่ติดมา)"""
	full = np.array(Image.open(os.path.join(SHEETS, code + ".jpg")).convert("RGB")).astype(float)
	H, W = full.shape[:2]; ch, cw = H / 10, W / 5
	out = {}
	for r in range(10):
		for c in range(5):
			py, px = int(ch * 0.18), int(cw * 0.18)
			y0, y1 = max(0, int(r * ch) - py), min(H, int((r + 1) * ch) + py)
			x0, x1 = max(0, int(c * cw) - px), min(W, int((c + 1) * cw) + px)
			rgb, a = key(full[y0:y1, x0:x1])
			lab, n = ndimage.label(ndimage.binary_closing(a > 0.8, iterations=2))   # ปิดรอยขาดของชิ้นบาง (เข็ม ตะเกียบ)
			cand = []
			for i, sl in enumerate(ndimage.find_objects(lab), 1):
				m = lab[sl] == i
				if m.sum() < 25: continue
				ys, xs = np.nonzero(m)
				cy, cx = ys.mean() + sl[0].start + y0, xs.mean() + sl[1].start + x0
				if r * ch <= cy < (r + 1) * ch and c * cw <= cx < (c + 1) * cw:
					d = np.hypot(cy - (r + 0.5) * ch, cx - (c + 0.5) * cw)
					cand.append((m.sum() / (1 + d / 30), i, sl))   # ใหญ่และใกล้กลางช่อง (แถวในชีตไม่เท่ากัน · ปลายชิ้นแถวข้างอาจใหญ่กว่า)
			if not cand: continue
			# ก้อนใหญ่สุด = ตัวอาวุธ · ก้อนอื่นเก็บเฉพาะที่อยู่ในกรอบตัวอาวุธ (+10) — ปลาย/ด้ามของชิ้นแถวข้างที่ล้นเข้ามาถูกทิ้ง
			_, i0, s0 = max(cand)
			by0, by1, bx0, bx1 = s0[0].start - 10, s0[0].stop + 10, s0[1].start - 10, s0[1].stop + 10
			keep = [i for _, i, sl in cand if i == i0 or (sl[0].start >= by0 and sl[0].stop <= by1 and sl[1].start >= bx0 and sl[1].stop <= bx1)]
			core = np.isin(lab, keep)
			soft, _ = ndimage.label(a > 0.08)   # ขอบโปร่ง/แสงเรือง: เฉพาะส่วนที่ต่อกับตัวอาวุธ (แสงของชิ้นข้างที่ไม่ต่อกันไม่ติดมา)
			m = ndimage.binary_dilation(core, iterations=8) & np.isin(soft, np.unique(soft[core]))
			# แสงเรืองระดับ 5 ในชีตเกยกับช่องข้าง → ส่วนโปร่งเก็บแค่ในช่องตัวเอง (+5%) · ตัวอาวุธทึบ (core) เก็บเต็มแม้ล้นช่อง
			yy, xx = np.mgrid[y0:y1, x0:x1]
			inside = (yy >= (r - .05) * ch) & (yy < (r + 1.05) * ch) & (xx >= (c - .05) * cw) & (xx < (c + 1.05) * cw)
			m = (m & inside) | core
			ys, xs = np.nonzero(m)
			out[(r, c)] = (rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], np.where(m, a, 0)[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
	return out


def main():
	os.makedirs(OUT, exist_ok=True)
	for f in os.listdir(OUT):
		if f.endswith(".png"): os.remove(os.path.join(OUT, f))
	allc = {code: cut(code) for code in TYPES}
	missing = [(code, r, c) for code in TYPES for r in range(10) for c in range(5) if (r, c) not in allc[code]]
	big = max(max(al.shape) for cs in allc.values() for _, al in cs.values())
	rows = []
	for code, types in TYPES.items():
		school = SCHOOL[code]
		for r, t in enumerate(types):
			branch = next(b for b, ws in WEAPONS[school].items() if t in ws)
			for tier in range(5):
				wid = f"{code}{r + 1:02d}-{tier + 1}"
				if (r, tier) not in allc[code]: continue
				px, al = allc[code][(r, tier)]
				for suf, S in (("", 32), ("_48", 48)):
					im = icon(px, al, (S - 6) / big, S)
					im.save(os.path.join(OUT, wid + suf + ".png"))
				rows.append({"id": wid, "school": school, "type": t.rstrip("*"), "type_no": r + 1, "tier": tier + 1,
					"name_th": t.rstrip("*") + TIER[tier], "branch": branch, "grip": GRIP_OF[t],
					"needs_decision": t.endswith("*"), "weapon_base": None, "price": None})
	open(os.path.join(OUT, ".gdignore"), "w").close()
	json.dump({"_doc": __doc__.strip().splitlines()[0] + " · ชื่อเป็นร่าง · ไม่มีค่าพลัง/ราคา (kwan กำหนด) · needs_decision = ปืนจริง รอ kwan",
		"tier_suffix": TIER, "grips": GRIP, "weapons": rows}, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	# ภาพตรวจ: 6 สาย × (10 แถว × 5 ระดับ) ไอคอน 48 ขยาย 2 เท่า
	cell = 100; sheet = Image.new("RGBA", (6 * 5 * cell + 5 * 20, 10 * cell + 30), (46, 50, 58, 255)); dr = ImageDraw.Draw(sheet)
	for si, code in enumerate(TYPES):
		x0 = si * (5 * cell + 20); dr.text((x0 + 4, 4), code, fill=(230, 230, 230))
		for r in range(10):
			for t in range(5):
				p = os.path.join(OUT, f"{code}{r + 1:02d}-{t + 1}_48.png")
				if os.path.exists(p):
					im = Image.open(p).resize((96, 96), Image.NEAREST); sheet.alpha_composite(im, (x0 + t * cell + 2, 30 + r * cell + 2))
	sheet.save(CHECK)
	print(f"weapons300: {len(rows)} ชิ้น · ช่องว่าง {missing or 'ไม่มี'} · ภาพตรวจ {CHECK}")


if __name__ == "__main__":
	main()
