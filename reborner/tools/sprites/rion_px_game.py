"""Rion พิกเซล 32-bit → ไฟล์ที่เกมอ่าน (kwan 16 ต.ค. 2026 เลือก "เปลี่ยนแนวภาพเป็นพิกเซลขนาด 72 ทั้งเกม")
  python3 tools/sprites/rion_px_game.py   (รันหลัง rion_flow_cut.py ที่สร้าง rion_flow_draft/main_px/)
อ่านเฟรมชุดหลักแบบพิกเซล → วางลงผืนขนาดเดียวกันทุกเฟรม (เท้า = แถว FEET · กลางตัว = คอลัมน์ W/2) → assets/sprites/rion_px/
ชื่อไฟล์ตามแบบ rion_lastlight_draft: <ทิศ>_w<i> เดิน · west ยืนศึก · west_i<i> ยืนศึกวน · west_a<i> ฟัน · west_h<i> โดนตี · west_k<i> ล้ม"""
import json, os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "assets/sprites/rion_flow_draft/main_px")
OUT = os.path.join(ROOT, "assets/sprites/rion_px")
W, H, FEET = 96, 112, 110   # ผืนกว้างพอท่าล้มนอน/รอยมีด · สูงพอมีดชูเหนือหัว · เท้าแถว 110
# (ชื่อไฟล์ในเกม, แถวในชุดหลัก, เฟรมที่ใช้) — เฟรมที่ตัดตาม OMIT ของหน้าเทส (ฟันเฟรม 5 หมวกซ้อน · โดนตีเฟรม 0 มีดสองเล่ม · ล้มเฟรม 4 ตัวไม่มีขา)
# เดิน 4 ทิศ = ทุกเฟรมที่มี (16 ต.ค. ชีต Flow 14-2 = 6 เฟรม · เดิม GPT 8)
_n = lambda row: range(sum(1 for f in os.listdir(SRC) if f.startswith(row + "_") and f[len(row) + 1:-4].isdigit()))
MAP = [("south_w", "walk_front", _n("walk_front")), ("north_w", "walk_back", _n("walk_back")),
	("west_w", "walk_left", _n("walk_left")), ("east_w", "walk_right", _n("walk_right")),
	("west_i", "idle_battle", range(6)), ("west_a", "attack_knife", [0, 1, 2, 3, 4, 6]),
	("west_h", "hurt", [1, 2, 3, 4, 5, 6]), ("west_k", "death", [0, 1, 2, 3, 5])]


def main():
	os.makedirs(OUT, exist_ok=True)
	for f in os.listdir(OUT):
		# ลบเฉพาะไฟล์ของสคริปต์นี้ (west_<อาวุธ>_<i> เขียนโดย rion_px_weapons.py ห้ามลบ)
		stem = f[:-4].rstrip("0123456789")
		if f.endswith(".png") and (stem in [m[0] for m in MAP] or f == "west.png"): os.remove(os.path.join(OUT, f))
	clip, info = 0, {}
	for name, row, idx in MAP:
		for j, i in enumerate(idx):
			im = Image.open(os.path.join(SRC, "%s_%d.png" % (row, i)))
			# เฟรมในชุดหลัก: กลางผืน = กลางตัว · ขอบล่างผืน = พื้น
			x, y = W // 2 - im.width // 2, FEET - im.height
			c = Image.new("RGBA", (W, H)); c.paste(im, (x, y), im)
			bb = im.getchannel("A").getbbox()
			if x + bb[0] < 0 or x + bb[2] > W or y + bb[1] < 0: clip += 1; print("ล้นผืน", name, j)
			c.save(os.path.join(OUT, "%s%d.png" % (name, j)))
		info[name] = len(idx)
	Image.open(os.path.join(OUT, "west_i0.png")).save(os.path.join(OUT, "west.png"))
	json.dump({"size": [W, H], "feet": FEET, "frames": info}, open(os.path.join(OUT, "rion_px.json"), "w"), ensure_ascii=False, indent=1)
	print("rion_px:", sum(info.values()) + 1, "ไฟล์ · ล้นผืน", clip)


if __name__ == "__main__":
	main()
