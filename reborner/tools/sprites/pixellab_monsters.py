"""มอนสำหรับเทสท่าตามร่างกาย 9 แบบ → PixelLab (API v2) · kwan 19 ต.ค. 2026 "ควรเพิ่มมอนให้ครบร่างกาย" → เลือก "4" (5 ตัว)

ร่างกายที่ยังไม่มีภาพ: วิญญาณ M07 · กระดูก M08 · ไม้ M09 (ภูมิภาค 1) · กลไก M17 · หิน M29 (ภูมิภาค 2)
หน้าตาจาก docs/art-bible/monster_visual_master.json (visual_description + palette) แปลเป็นคำสั่งอังกฤษละเอียด + บล็อก STYLE ของ RION_MASTER ตามตัวอักษร
คีย์จาก env PIXELLAB_API_KEY เท่านั้น · ทุกคำสั่งที่เสียเครดิตพิมพ์ยอดก่อน-หลัง (ใช้ call/wait/balance ของ pixellab_walk.py)
  python3 tools/sprites/pixellab_monsters.py prompt <id>     พิมพ์คำสั่งเต็ม (ไม่เสียเครดิต)
  python3 tools/sprites/pixellab_monsters.py create <id…>    /create-character-v3 (ไม่มีภาพอ้างอิง · หันขวา = east ใช้ในจอศึก)
  python3 tools/sprites/pixellab_monsters.py hurt <id…>      ท่าโดนตี 4 เฟรม หันขวา (/characters/animations v3)
  python3 tools/sprites/pixellab_monsters.py fetch <id…>     ZIP → OUT/<id>/
  python3 tools/sprites/pixellab_monsters.py page            → OUT/px/<id>_<i>.png + index.json (รูปแบบเดียวกับ monsters_px_draft · หน้า animation test อ่านต่อท้าย)
ผลอยู่ใน assets/sprites/pixellab_draft/monsters/ (ร่าง ยังไม่เข้าเกม) · state.json["monsters"][id]
"""
import io
import json
import os
import shutil
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import pixellab_walk as plw  # noqa: E402

OUT = os.path.join(plw.OUT, "monsters")
SIZE = 96
# ส่วนที่ทุกตัวใช้ร่วม: ฉากหลัง/สิ่งที่ห้าม · ตัวละครมีชีวิตแบบจิบลิ ไม่น่ากลัว (ตาม archetype_justification ใน visual master)
COMMON = ("A single monster for a turn-based JRPG battle, full body, centered. "
	"Cute and warm Ghibli-like creature design, readable chunky silhouette, thick dark outline. "
	"No background, no ground, no shadow, no text, no extra characters, no weapons other than those described.")
MONSTERS = {
	"M07": {"template": "custom", "name": "ผีไฟป่า", "body": "วิญญาณ", "float": True, "seed": 41,
		"desc": "A small floating forest will-o'-the-wisp spirit. Its body is a teardrop-shaped flame that hovers above the ground with the pointed tip up, "
			"warm orange-brown flame shading from a darker brown-orange core to pale tan at the soft wavy edges. A tiny cute face in the middle of the flame: "
			"two round glowing eyes and a tiny mouth. A few small ember sparks float around it. No arms, no legs. Warm and mysterious, not scary. "
			"Palette: #92552D, #B37A55, #D4B08A, outline #2F1B10."},
	"M08": {"template": "mannequin", "name": "โครงกระดูกเดินเวร", "body": "กระดูก", "float": False, "seed": 41,
		"desc": "A short, round little skeleton night-watchman. Cream and warm light-brown bones, a big round skull with small warm orange lights glowing inside "
			"the eye sockets, a tattered triangular grey-brown hooded cloak over the shoulders, an old brass lantern held in one bony hand at its side, "
			"short bony arms and legs in a waddling stance. A diligent old guard, cute rather than scary. Palette: #D2BD9A, #A2927B, #6F4B33, #92552D."},
	"M09": {"template": "mannequin", "name": "ตุ๊กตาไม้", "body": "ไม้", "float": False, "seed": 41,
		"desc": "A small round carved wooden doll like a folk toy. Light brown wood with visible grain, the head bigger than the body, a simple painted face "
			"(dot eyes, brownish pink cheeks), short stick arms and legs joined by round wooden pegs at the shoulders, hips and knees, a few small age cracks. "
			"Stiff wind-up-toy stance. Palette: #B37A55, #92552D, #523624, #D4B08A."},
	"M17": {"template": "custom", "name": "ทหารกลไก", "body": "กลไก", "float": True, "seed": 41,
		"desc": "A small round clockwork toy soldier robot hovering above the ground. Old brass round body, one big round eye in the middle of the face glowing "
			"warm yellow, a wind-up key sticking out of its back, short jointed mechanical arms holding a small round brass shield, a little soldier helmet crest on top. "
			"An old toy soldier come alive, endearing. Palette: #B37A55, #92552D, #8A7460, outline #2F1B10."},
	"M29": {"template": "mannequin", "name": "โกลเลมสลัก", "body": "หิน", "float": False, "seed": 41,
		"desc": "A big stocky golem made of carved stone, larger and heavier than the other monsters and filling most of the frame. Body built from stacked rounded "
			"stone blocks, broad shoulders, two huge stone fists hanging low, warm softly glowing orange rune letters carved all over the body, eyes are small fire "
			"lights inside a slot in the stone head, short thick legs. Strong but slow and gentle looking. Palette: #6C5947, #8A7460, #523624, rune glow #92552D."},
}
HURT = ("Side view facing RIGHT in every frame (toward an enemy on the right); it never turns toward the camera. Hit reaction, 4 frames, one beat per frame: "
	"1) struck from the right: the whole body jerks back to the LEFT, eyes squeezed shut. 2) the biggest recoil, body leaning back to the left and squashed. "
	"3) wobbling back toward the start. 4) back to the starting pose. Keep identical in every frame: the same design, colors, size and proportions as the reference. "
	"Do NOT draw: sparks, impact stars, motion lines, blood, text, ground, shadow or a second character.")


STYLE_REF = os.path.join(plw.ROOT, "assets/sprites/monsters_px_draft/M15_0.png")   # หมาป่า ชุด Flow รอบ 11 ที่เข้าเกมแล้ว


def style_ref():
	im = Image.open(STYLE_REF).convert("RGBA")
	w, h = -(-im.width // 4) * 4, -(-im.height // 4) * 4   # API ต้องการพหุคูณ 4
	c = Image.new("RGBA", (w, h)); c.alpha_composite(im, (0, 0))
	b = io.BytesIO(); c.save(b, "PNG")
	import base64
	return {"image": {"type": "base64", "base64": base64.b64encode(b.getvalue()).decode(), "format": "png"}, "size": {"width": w, "height": h},
		"usage_description": "Copy only the pixel-art rendering style of this monster sprite: outline thickness and color, shading, detail level. Do not copy the subject, pose or colors."}


def description(mid):
	return COMMON + " " + MONSTERS[mid]["desc"] + " " + plw.master_blocks()["STYLE"]


def show(mid):
	d, h = description(mid), HURT
	print(f"{mid} {MONSTERS[mid]['name']} ({MONSTERS[mid]['body']}) · seed {MONSTERS[mid]['seed']} · ผืน {SIZE}\n\n[description {len(d)} ตัวอักษร]\n{d}\n\n[ท่าโดนตี action {len(h)} ตัวอักษร]\n{h}\n")


def create(mid):
	s = plw.state()
	show(mid)
	plw.balance()
	m = MONSTERS[mid]
	# รอบแรก /create-character-v3 (M07 · 3 gen): โครงตัวคนบังคับ → ผีไฟออกมามีแขนขา ทั้งที่สั่งห้าม
	# → /create-character-pro-flash: template "custom" ให้ตัวไม่มีแขนขา + ภาพแนวลายเส้น = มอนพิกเซลชุดเดิม (STYLE_REF) คัดเฉพาะเส้นขอบ/เงา/รายละเอียด ไม่เอาสี
	r = plw.call("POST", "/create-character-pro-flash", {"description": description(mid), "name": f"{mid} {m['name']}", "image_size": {"width": SIZE, "height": SIZE},
		"view": "low top-down", "seed": m["seed"], "template_id": m["template"], "style_image": style_ref(),
		"style_options": {"color_palette": False, "outline": True, "detail": True, "shading": True}})
	s.setdefault("monsters", {})[mid] = {"character_id": r["character_id"], "create": r}
	plw.save_state(s)
	if r.get("background_job_id"):
		j = plw.wait(r["background_job_id"], f"สร้าง {mid}")
		s["monsters"][mid]["status"] = j.get("status")
		plw.save_state(s)
	plw.balance()


def hurt(mid):
	s = plw.state()
	plw.balance()
	body = {"character_id": s["monsters"][mid]["character_id"], "animation_name": "hurt", "mode": "v3", "description": description(mid),
		"action_description": HURT, "frame_count": 4, "keep_first_frame": False, "directions": ["east"], "seed": MONSTERS[mid]["seed"]}
	r = plw.call("POST", "/characters/animations", body)
	s["monsters"][mid]["hurt"] = r
	plw.save_state(s)
	for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
		j = plw.wait(jid, f"โดนตี {mid}")
		s["monsters"][mid]["hurt_status"] = j.get("status")
		plw.save_state(s)
	plw.balance()


def fetch(mid):
	s = plw.state()
	data = plw.call("GET", f"/characters/{s['monsters'][mid]['character_id']}/zip", raw=True)
	dst = os.path.join(OUT, mid)
	shutil.rmtree(dst, ignore_errors=True)
	zipfile.ZipFile(io.BytesIO(data)).extractall(dst)
	for root, _, fs in os.walk(dst):
		for f in sorted(fs):
			if f.endswith(".png"):
				im = Image.open(os.path.join(root, f))
				print(" ", os.path.relpath(os.path.join(root, f), dst), im.size, im.getchannel("A").getbbox())


def _find(mid, *parts):
	for root, _, fs in os.walk(os.path.join(OUT, mid)):
		if root.replace("\\", "/").endswith("/".join(parts)):
			return sorted(os.path.join(root, f) for f in fs if f.endswith(".png"))
	return []


def _fit(im, size):
	"""ท่าขยับบางตัวได้ผืนใหญ่กว่าภาพหมุน (M29 120 vs 96) → วางกลางผืนขนาดเดียวกัน (ขอบเพิ่มรอบตัวเท่ากันทุกด้าน)"""
	if im.size == size:
		return im
	c = Image.new("RGBA", size)
	c.alpha_composite(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2)) if im.width <= size[0] else c.paste(im.crop(((im.width - size[0]) // 2, (im.height - size[1]) // 2, (im.width + size[0]) // 2, (im.height + size[1]) // 2)))
	return c


def _clean_hurt(idle, frames):
	"""ท่าโดนตีที่ PixelLab วาดประกาย/ลำแสงติดมา (สั่งห้ามแล้วก็ยังวาด · 19 ต.ค.) และบางเฟรมเป็นก้อนเบลอ (M17)
	→ เลือกเฟรมที่สีแปลกปลอมน้อยสุดและตัวขยับจากท่ายืนจริง → ลบพิกเซลที่สีห่างจากสีของท่ายืน → เก็บก้อนใหญ่สุด"""
	import numpy as np
	from scipy import ndimage
	ia = np.array(idle)
	pal = np.unique(ia[ia[..., 3] > 127][:, :3], axis=0).astype(int)
	lum = lambda a: a[..., :3].astype(int) @ np.array([299, 587, 114]) // 1000
	hi = np.percentile(lum(ia)[ia[..., 3] > 127], 99) + 12   # ประกายสว่างกว่าจุดสว่างสุดของตัว
	area0 = (ia[..., 3] > 127).sum()
	def far(a):
		px = a[..., :3].reshape(-1, 1, 3).astype(int)
		d = np.min(((px - pal[None]) ** 2).sum(-1), axis=1).reshape(a.shape[:2])
		return ((d > 40 ** 2) | ((lum(a) > hi) & (d > 15 ** 2))) & (a[..., 3] > 127)   # สว่าง + สีไม่ตรงตัว = ประกาย (หัวกะโหลกขาวของ M08 ไม่โดน)
	def score(im):
		a = np.array(im); body = a[..., 3] > 127
		moved = np.abs(a[..., 3].astype(int) - ia[..., 3].astype(int)).sum() / 255
		blob = 1 if body.sum() > 1.5 * area0 else 0   # ก้อนเบลอ (M17) ใหญ่กว่าตัวจริงมาก
		return far(a).sum() / max(1, body.sum()) + (1 if moved < 20 else 0) + blob
	a = np.array(min(frames, key=score)).copy()
	a[far(a)] = 0
	lab, n = ndimage.label(a[..., 3] > 127)
	if n > 1:
		keep = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
		a[lab != keep] = 0
	return Image.fromarray(a, "RGBA")


def page():
	"""ภาพหันขวา (east) = ยืน · ท่าโดนตีเฟรมที่ถอยมากสุด = โดน → ครอปกรอบรวม เว้นขอบ 4 · ตัวลอย (float) เว้นใต้ตัว 12 ให้ลอยเหนือพื้นแบบค้างคาว"""
	dst = os.path.join(OUT, "px")
	shutil.rmtree(dst, ignore_errors=True)
	os.makedirs(dst)
	out = []
	for mid, m in MONSTERS.items():
		rot = _find(mid, "rotations")
		east = [p for p in rot if p.endswith("east.png")]
		hurt = _find(mid, "hurt", "east") or _find(mid, "animations", "east")
		if not east:
			continue
		ims = [Image.open(east[0]).convert("RGBA")]
		if hurt:
			ims.append(_clean_hurt(ims[0], [_fit(Image.open(p).convert("RGBA"), ims[0].size) for p in hurt]))
		bb = [im.getchannel("A").getbbox() for im in ims]
		x0, y0, x1, y1 = min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb)
		pad = 12 if m["float"] else 0
		w, h = x1 - x0 + 8, y1 - y0 + 4 + pad
		for i, im in enumerate(ims):
			c = Image.new("RGBA", (w, h))
			c.alpha_composite(im.crop((x0, y0, x1, y1)), (4, 4))
			c.save(os.path.join(dst, f"{mid}_{i}.png"))
		out.append({"id": mid, "name": m["name"], "body": m["body"], "n": len(ims), "roles": ["idle", "hurt"][:len(ims)], "size": [w, h], "src": "pixellab"})
	json.dump({"_doc": "มอนเทสร่างกาย 9 แบบ จาก PixelLab (tools/sprites/pixellab_monsters.py · ร่าง ยังไม่เข้าเกม)", "monsters": out},
		open(os.path.join(dst, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	print("มอน", [(o["id"], o["size"], o["n"]) for o in out], "→", dst)


if __name__ == "__main__":
	cmd, ids = sys.argv[1], sys.argv[2:] or list(MONSTERS)
	if cmd == "page":
		page()
	else:
		for mid in ids:
			{"prompt": show, "create": create, "hurt": hurt, "fetch": fetch}[cmd](mid)
