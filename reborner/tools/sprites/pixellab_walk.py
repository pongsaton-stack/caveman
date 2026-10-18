"""Rion master v2 → PixelLab (API v2) → ท่าเดิน 4 ทิศ · kwan 18 ต.ค. 2026 "ถ้าใช้ pixellab จบไหม" → เลือก "1" ใส่คีย์ทดลอง

คีย์อ่านจาก env PIXELLAB_API_KEY เท่านั้น (ห้ามใส่ใน repo/แชท) · ทุกคำสั่งที่เสียเครดิตพิมพ์ยอดคงเหลือก่อน-หลัง
ขั้น:
  python3 tools/sprites/pixellab_walk.py ref          ทำภาพอ้างอิงหันหน้า (ไม่ต่อเน็ต · ไม่เสียเครดิต)
  python3 tools/sprites/pixellab_walk.py balance      ดูยอดคงเหลือ
  python3 tools/sprites/pixellab_walk.py character    สร้างตัวละครจากภาพอ้างอิง 4 ทิศ (/create-character-v3 · ~ceil(w*h*4/65536) gen)
  python3 tools/sprites/pixellab_walk.py walk [ทิศ…]  ท่าเดินของตัวละครที่สร้างแล้ว (ค่าเริ่ม east · /characters/animations)
  python3 tools/sprites/pixellab_walk.py prompt <ท่า> [ทิศ]  พิมพ์คำสั่งเต็มก่อนเสียเครดิต (ท่าใน MOVES)
  python3 tools/sprites/pixellab_walk.py anim <ท่า> [ทิศ…]   **ท่าใหม่ใช้คำสั่งนี้เท่านั้น** (คำสั่งละเอียด 8 ส่วน · docs/art-bible/rion_hires/PIXELLAB_PROMPTS.md)
  python3 tools/sprites/pixellab_walk.py slash/slash2 [ทิศ]  คำสั่งแบบเก่าที่ใช้ไปแล้ว (เก็บไว้รันซ้ำตามบันทึก)
  python3 tools/sprites/pixellab_walk.py fetch        ดึง ZIP ของตัวละคร แตกภาพลง OUT
  python3 tools/sprites/pixellab_walk.py vfx <ชื่อ>    เอฟเฟกต์จาก VFX_SPECS (/vfx · lite ~1 gen · พิมพ์คำสั่งเต็ม + ราคาที่ PixelLab เสนอ) → OUT/vfx/<ชื่อ>/
  python3 tools/sprites/pixellab_walk.py page         ท่าเดินจาก ZIP → px/ (ผืนเดียวกับ rion_pack_px) ให้หน้า animation test
ผลทั้งหมดอยู่ใน assets/sprites/pixellab_draft/ (.gdignore · ร่าง ยังไม่เข้าเกม) · state.json เก็บ character_id / job id
"""
import base64
import io
import shutil
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
MASTER = os.path.join(ROOT, "docs/art-bible/rion_hires/rion_master_v2.png")
OUT = os.path.join(ROOT, "assets/sprites/pixellab_draft")
STATE = os.path.join(OUT, "state.json")
API = "https://api.pixellab.ai/v2"
REF_H, CANVAS = 72, 96   # ตัวสูงเท่า Rion ในเกม (rion_pack_px PX_H) · ผืนจัตุรัส เท้าชิดล่างเว้น 4
DESC = ("chibi boy hero, blue cap with brass goggles, messy brown hair, white short-sleeve collared shirt, blue necktie, "
	"blue knee-length shorts, brown backpack, white socks, brown boots, no wristwatch, 32-bit pixel art")
# ---- คำสั่งที่ใช้ไปแล้ว (เก็บไว้ให้รันซ้ำได้ตรงตามบันทึก · ห้ามใช้แบบนี้กับท่าใหม่) ----
# kwan 18 ต.ค.: "คุณต้องใส่คำสั่งให้ละเอียดที่สุด" → ท่าใหม่ใช้ MOVES + build_action() (กฎใน docs/art-bible/rion_hires/PIXELLAB_PROMPTS.md)
WALK_ACTION = "walking at a steady pace, arms swinging opposite to the legs, legs pass each other mid-step, body bobs slightly"
SEEDS = {"slash2": 27}
ACTIONS = {"walk": WALK_ACTION,
	"slash": "slashing with a small kitchen knife held in the front hand in every frame: raise the knife behind the shoulder, "
		"step forward and swing it down fast in an arc toward an enemy on the left, follow through, then recover to a ready stance",
	# รอบ 2 (kwan 18 ต.ค. "ลองอีกรอบ"): รอบแรกเฟรม 5–7 หมุนหันเข้ากล้อง + แทงตรง + ใบมีดยาว
	"slash2": "side view, the body stays facing LEFT in every frame and never turns toward the camera: nose, cap brim and toes point left, "
		"backpack on the right. A short small kitchen knife (blade about the length of the hand) stays in the front hand in every frame. "
		"Raise the knife up behind the shoulder, step forward with the front foot and slash it down in a curved arc in front of the body "
		"toward an enemy on the left, follow through low, then return to a ready stance still facing left"}

# ---- คำสั่งละเอียด 8 ส่วน (PIXELLAB_PROMPTS.md) ----
MASTER_MD = os.path.join(ROOT, "docs/art-bible/rion_hires/RION_MASTER.md")
DIR_BLOCK = {"west": "LEFT", "east": "RIGHT", "north": "BACK"}   # south = หน้าตรง (บล็อก "ภาพหน้าตรง" ไม่ใช้ เพราะบอกให้ยืนนิ่ง)
# ส่วนที่ต้องคงที่ทุกเฟรม (ข้อ 5) และสิ่งที่ห้ามทุกท่า (ข้อ 6) · ท่าเพิ่มของตัวเองได้ใน MOVES[ท่า]["not"]
KEEP = ("Keep identical in every frame: the whole cap is blue with the brass-gold goggles resting on its front, the brown backpack stays on the back, "
	"the blue necktie, the same head size and body height, the same proportions as the reference. Bare wrists, no wristwatch.")
NOT_ALWAYS = ["turning the body toward the camera unless this move says so", "a wristwatch", "extra characters", "ground, shadow, text or background",
	"large glowing effects, energy trails or speed lines (effects are added later in code)"]
MOMENTUM = ("Follow momentum: wind up while still moving, land the hit at the moment the weight comes down, "
	"let the follow-through carry forward, then settle. Never freeze in a held wind-up pose.")
# ท่า: dir = ทิศตั้งต้น · held = ของในมือ (None = มือว่าง) · beats = จังหวะ (≈ จำนวนเฟรม) · attack = ใส่หลักโมเมนตัม · not = ห้ามเพิ่ม · frames · seed
MOVES = {
	"walk": {"dir": "east", "held": None, "attack": False, "frames": 8, "seed": 18,
		"beats": [
			"contact: front heel touches the ground, back leg straight behind, arms swing opposite to the legs",
			"down: weight drops onto the front leg, knee bends slightly, body lowest",
			"passing: back leg swings forward past the standing leg, body rises, arms near the sides",
			"up: pushing off the toes of the standing leg, body highest",
			"contact with the other foot forward, arms swapped",
			"down on the other leg",
			"passing with the other leg",
			"up, ready to loop back to the first frame"],
		"not": ["both feet off the ground", "sliding feet"]},
	"slash": {"dir": "west", "attack": True, "frames": 8, "seed": 27,
		"held": "a short small kitchen knife, blade about the length of the hand, held by the handle in the front hand (the hand nearest the viewer)",
		"beats": [
			"ready stance facing left, knees slightly bent, knife held low in front",
			"step forward with the front foot while raising the knife back over the shoulder, blade pointing up and back",
			"wind-up at its peak behind the shoulder, body twisting back, weight on the back foot",
			"swing begins: arm comes forward over the head toward the left",
			"the knife slashes down in a curved arc in front of the body, front foot lands, weight shifts forward",
			"follow-through: knife low near the front knee, body leaning forward",
			"recover: pull the knife back up toward the chest",
			"back to the ready stance facing left, same as the first frame"],
		"not": ["the knife disappearing in any frame", "a second knife", "a long sword or dagger", "the knife sticking straight up above the cap"]},
}

# ท่าต้นไม้ 17 ท่า × 6 สาย (102 ท่า · tools/sprites/pixellab_skills.py) — ใช้คำสั่งเดียวกัน: prompt <รหัสท่า> · anim <รหัสท่า>
try:
	import csv as _csv
	import pixellab_skills as _sk
	MOVES.update(_sk.skill_moves(list(_csv.DictReader(open(os.path.join(ROOT, "docs/design/skill_trees_17.csv"), encoding="utf-8")))))
except (ImportError, FileNotFoundError):
	pass


def master_blocks():
	"""อ่านบล็อกจาก RION_MASTER.md ตามตัวอักษร: CHARACTER · STYLE · LEFT/RIGHT/BACK"""
	t = open(MASTER_MD, encoding="utf-8").read()
	def code_after(head):
		i = t.index(head)
		a = t.index("```", i) + 3
		return " ".join(t[a:t.index("```", a)].split())
	out = {"CHARACTER": code_after("### ตัวละคร (CHARACTER)"), "STYLE": code_after("### สไตล์ (STYLE)")}
	for line in t.splitlines():
		for k in ("LEFT", "RIGHT", "BACK"):
			if line.startswith(k + ":"):
				out[k] = line[len(k) + 1:].strip()
	return out


def build_action(move, d):
	"""ประกอบ action_description 8 ส่วน · ส่วน 7–8 (CHARACTER + STYLE) ส่งเป็น description แยก (ดู build_description)"""
	m, mb = MOVES[move], master_blocks()
	parts = []
	if d in DIR_BLOCK:
		parts.append(mb[DIR_BLOCK[d]] + " The body keeps this exact facing in every frame and never turns toward the camera.")
	else:
		parts.append("Front view facing the viewer in every frame.")
	if m["held"]:
		parts.append("Held item: " + m["held"] + ". It stays in that same hand in every frame, never disappears, and there is never a second one.")
	else:
		parts.append("Both hands are empty in every frame.")
	parts.append(f"The animation is {m['frames']} frames, one beat per frame: "
		+ " ".join(f"{i + 1}) {b}." for i, b in enumerate(m["beats"])))
	if m["attack"]:
		parts.append(MOMENTUM)
	parts.append(KEEP)
	parts.append("Do NOT draw: " + "; ".join(NOT_ALWAYS + m.get("not", [])) + ".")
	return " ".join(parts)


def build_description():
	mb = master_blocks()
	return mb["CHARACTER"] + " " + mb["STYLE"]


def show_prompt(move, d=None):
	d = d or MOVES[move]["dir"]
	a, desc = build_action(move, d), build_description()
	print(f"ท่า {move} · ทิศ {d} · seed {MOVES[move]['seed']} · เฟรม {MOVES[move]['frames']}")
	print(f"\n[description {len(desc)} ตัวอักษร]\n{desc}\n\n[action_description {len(a)} ตัวอักษร]\n{a}")
	if len(desc) > 2000:
		sys.exit("description เกิน 2000 ตัวอักษร (ขีดจำกัด API)")


def key_green(rgb):
	r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
	return ~((g > 140) & (g > r + 60) & (g > b + 60))


def make_ref():
	"""master (พื้นเขียว 1438x2576) → ตัดพื้น → ย่อ BOX ให้ตัวสูง REF_H → ผืน CANVAS พื้นโปร่ง"""
	rgb = np.array(Image.open(MASTER).convert("RGB")).astype(int)
	m = key_green(rgb)
	ys, xs = np.nonzero(m)
	crop = np.dstack([rgb, m * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
	k = REF_H / crop.shape[0]
	im = Image.fromarray(crop, "RGBA")
	pre = np.array(im).astype(float)
	pre[..., :3] *= pre[..., 3:] / 255
	w = max(1, round(crop.shape[1] * k))
	sm = np.array(Image.fromarray(pre.astype(np.uint8), "RGBA").resize((w, REF_H), Image.BOX)).astype(float)
	A = sm[..., 3] / 255
	rgb2 = np.where(A[..., None] > 0, sm[..., :3] / np.maximum(A[..., None], 1e-6), 0).clip(0, 255)
	out = np.zeros((CANVAS, CANVAS, 4), np.uint8)
	x0, y0 = (CANVAS - w) // 2, CANVAS - 4 - REF_H
	out[y0:y0 + REF_H, x0:x0 + w, :3] = rgb2
	out[y0:y0 + REF_H, x0:x0 + w, 3] = np.where(A > .5, 255, 0)
	os.makedirs(OUT, exist_ok=True)
	open(os.path.join(OUT, ".gdignore"), "w").close()
	p = os.path.join(OUT, "ref_south.png")
	Image.fromarray(out, "RGBA").save(p)
	print("ภาพอ้างอิง", p, out.shape[1], "x", out.shape[0], "ตัวสูง", REF_H)
	return p


def key():
	k = os.environ.get("PIXELLAB_API_KEY", "")
	if not k:
		sys.exit("ไม่มี PIXELLAB_API_KEY ใน session นี้ (ตั้งในหน้าตั้งค่า environment แล้วเปิด session ใหม่)")
	return k


def call(method, path, body=None, raw=False):
	req = urllib.request.Request(API + path, method=method,
		data=json.dumps(body).encode() if body is not None else None,
		headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json"})
	# proxy ของ session ตัดการเชื่อมต่อบ่อย · URLError = หลุดก่อนส่งคำขอครบ ลองใหม่ได้ไม่เสียเครดิตซ้ำ
	for i in range(5):
		try:
			with urllib.request.urlopen(req, timeout=120) as r:
				data = r.read()
			break
		except urllib.error.HTTPError as e:
			sys.exit(f"{method} {path} → HTTP {e.code}: {e.read().decode()[:2000]}")
		except urllib.error.URLError as e:
			print(f"  เน็ตหลุด ({e.reason}) ลองใหม่ครั้งที่ {i + 1}", flush=True)
			time.sleep(2 ** (i + 1))
	else:
		sys.exit(f"{method} {path} → เชื่อมต่อไม่ได้ 5 ครั้ง")
	return data if raw else json.loads(data)


def state():
	return json.load(open(STATE)) if os.path.isfile(STATE) else {}


def save_state(s):
	json.dump(s, open(STATE, "w"), indent=1, ensure_ascii=False)


def balance():
	b = call("GET", "/balance")
	print("ยอดคงเหลือ", json.dumps(b, ensure_ascii=False))
	return b


def wait(job_id, label):
	t0 = time.time()
	while True:
		j = call("GET", f"/background-jobs/{job_id}")
		st = j.get("status")
		print(f"  {label} {st} {int(time.time() - t0)} วิ", flush=True)
		if st in ("completed", "failed"):
			return j
		time.sleep(10)


def b64(path):
	return {"type": "base64", "base64": base64.b64encode(open(path, "rb").read()).decode(), "format": "png"}


def character():
	ref = os.path.join(OUT, "ref_south.png")
	if not os.path.isfile(ref):
		make_ref()
	balance()
	r = call("POST", "/create-character-v3", {"description": DESC, "name": "Rion master v2", "reference_image": b64(ref),
		"n_directions": 4, "view": "low top-down", "no_background": True, "seed": 18})
	s = state()
	s.update(character_id=r["character_id"], character_job=r.get("background_job_id"), character_usage=r.get("usage"))
	save_state(s)
	print("character_id", r["character_id"], "ค่าใช้", r.get("usage"))
	if r.get("background_job_id"):
		j = wait(r["background_job_id"], "สร้างตัวละคร")
		s["character_status"] = j.get("status")
		save_state(s)
	balance()


def walk(dirs, name="walk"):
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	balance()
	r = call("POST", "/characters/animations", {"character_id": s["character_id"], "animation_name": name,
		"mode": "v3", "action_description": ACTIONS[name], "frame_count": 8, "keep_first_frame": False, "directions": dirs, "seed": SEEDS.get(name, 18)})
	s.setdefault(name, []).append(r)
	save_state(s)
	print(json.dumps(r, ensure_ascii=False)[:800])
	for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
		j = wait(jid, name)
		s.setdefault(name + "_jobs", {})[jid] = j.get("status")
		save_state(s)
	balance()


def anim(move, dirs=None):
	"""ท่าใหม่ทุกท่าใช้ทางนี้: คำสั่ง 8 ส่วนจาก MOVES · description = CHARACTER + STYLE ของ RION_MASTER ตามตัวอักษร"""
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	m = MOVES[move]
	dirs = dirs or [m["dir"]]
	balance()
	for d in dirs:
		show_prompt(move, d)
		body = {"character_id": s["character_id"], "animation_name": f"{move}_v", "mode": "v3",
			"description": build_description(), "action_description": build_action(move, d),
			"frame_count": m["frames"], "keep_first_frame": False, "directions": [d], "seed": m["seed"]}
		r = call("POST", "/characters/animations", body)
		s.setdefault("anim", []).append({"move": move, "dir": d, "seed": m["seed"], "response": r})
		save_state(s)
		for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
			j = wait(jid, f"{move} {d}")
			s.setdefault("anim_jobs", {})[jid] = j.get("status")
			save_state(s)
	balance()


def fetch():
	s = state()
	data = call("GET", f"/characters/{s['character_id']}/zip", raw=True)
	z = zipfile.ZipFile(io.BytesIO(data))
	dst = os.path.join(OUT, "zip")
	os.makedirs(dst, exist_ok=True)
	z.extractall(dst)
	names = [n for n in z.namelist() if n.lower().endswith(".png")]
	print("แตก", len(names), "ภาพ →", dst)
	for n in sorted(names)[:40]:
		print(" ", n, Image.open(os.path.join(dst, n)).size)


# ---- เอฟเฟกต์ (/vfx · kwan 18 ต.ค. "vfx ก็ทำใน pixellab ได้หรือเปล่า" → ลอง lite 1 ท่า) ----
# คำสั่งละเอียดแบบเดียวกับท่า: อะไร · สี · ขยับยังไง · จังหวะเทียบเฟรมของสไปรต์ · สิ่งที่ห้าม · สไปรต์ = เฟรมท่าที่ PixelLab เจนแล้ว (เรียงแนวนอน)
VFX_SPECS = {
	"slash2_trail": {"sprite": "zip/Idle/animations/slash2/west", "artist": "lite", "fps": 9,
		"description": (
			"A knife slash trail for a small kitchen knife, in 32-bit pixel art that matches the sprite: hard pixel edges, no anti-aliasing, "
			"no blur, no soft glow gradients, a small palette. The sprite is an 8-frame attack: a chibi boy seen from the side, facing LEFT "
			"in every frame, raises a short kitchen knife behind his shoulder (frames 1-4), slashes it down in a curved arc in front of his body "
			"toward an enemy on the LEFT (frames 5-6), follows through low and recovers (frames 7-8). "
			"Make the effect follow the knife tip exactly: nothing during the wind-up except a 1-2 pixel glint on the blade at frame 4; "
			"at frames 5-6 a thick crescent arc trail swept from above the cap down to knee height on the LEFT side of the body, "
			"3 pixels thick at its middle and tapering to 1 pixel at both ends, colours from the edge inward: dark navy #21508A outline, "
			"blue #4184C9, pale sky blue, and a white core line along the leading edge; 4-6 small white and pale-blue spark pixels fly "
			"off the arc to the left at frame 6; at frames 7-8 the arc breaks into pixel fragments that fade out and drift slightly left and down. "
			"The effect is about as wide as the character and never covers his face. "
			"Do NOT redraw, recolour, move or resize the character; do NOT add a second knife, a big explosion, smoke, a ground, a shadow, "
			"a background, text or numbers. Keep the same timing as the sprite and end with an empty frame so the attack can loop.")},
}


def vfx(name):
	spec = VFX_SPECS[name]
	src = os.path.join(OUT, spec["sprite"])
	files = sorted(f for f in os.listdir(src) if f.startswith("frame_"))
	ims = [Image.open(os.path.join(src, f)).convert("RGBA") for f in files]
	strip = Image.new("RGBA", (ims[0].width * len(ims), ims[0].height), (0, 0, 0, 0))
	for i, im in enumerate(ims):
		strip.paste(im, (i * im.width, 0))
	buf = io.BytesIO()
	strip.save(buf, "PNG")
	print(f"เอฟเฟกต์ {name} · {spec['artist']} · สไปรต์ {len(ims)} เฟรม {ims[0].size} · คำสั่ง {len(spec['description'])} ตัวอักษร")
	print(spec["description"])
	balance()
	r = call("POST", "/vfx", {"description": spec["description"], "artist": spec["artist"], "name": f"Rion {name}",
		"sprite": {"type": "base64", "base64": base64.b64encode(buf.getvalue()).decode(), "format": "png"},
		"sprite_frames": len(ims), "sprite_fps": spec["fps"], "game_pack": True})
	print("ตอบรับ", json.dumps(r, ensure_ascii=False)[:600])
	s = state()
	s.setdefault("vfx", []).append({"name": name, "response": r})
	save_state(s)
	jid = r.get("background_job_id")
	if not jid:
		sys.exit("ไม่มี background_job_id")
	j = wait(jid, "vfx " + name)
	last = j.get("last_response") or {}
	s["vfx"][-1].update(status=j.get("status"), result={k: v for k, v in last.items() if k != "conversation"}, conversation=last.get("conversation"))
	save_state(s)
	dst = os.path.join(OUT, "vfx", name)
	os.makedirs(dst, exist_ok=True)
	fl = last.get("files") or {}
	for fname, url in (fl.items() if isinstance(fl, dict) else [(f.get("name") or os.path.basename(f.get("url", "")), f.get("url")) for f in fl]):
		for i in range(4):
			try:
				data = urllib.request.urlopen(url, timeout=120).read()
				break
			except urllib.error.URLError as e:
				print(f"  โหลด {fname} หลุด ({e.reason}) ลองใหม่", flush=True)
				time.sleep(2 ** (i + 1))
		else:
			continue
		open(os.path.join(dst, os.path.basename(fname)), "wb").write(data)
		print("  ได้", fname, len(data), "ไบต์")
	print("ข้อความศิลปิน:", last.get("message"))
	vfx_frames(name)
	balance()


def vfx_frames(name):
	"""ผล /vfx → เฟรมแยกให้หน้า pixellab animation test: with_sprite/ (ตามที่ PixelLab ทำ) · fx/ (เอฟเฟกต์ล้วน ผืน/จังหวะเท่าสไปรต์ จาก game pack)"""
	dst = os.path.join(OUT, "vfx", name)
	base = [f for f in os.listdir(dst) if f.endswith(".json") and not f.endswith("manifest.json")][0][:-5]
	meta = json.load(open(os.path.join(dst, base + ".json")))
	sheet = Image.open(os.path.join(dst, base + ".png")).convert("RGBA")
	for sub in ("with_sprite", "fx"):
		shutil.rmtree(os.path.join(dst, sub), ignore_errors=True)
		os.makedirs(os.path.join(dst, sub))
	for i, fr in enumerate(meta["frames"]):
		r = fr["frame"]
		sheet.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"])).save(os.path.join(dst, "with_sprite", f"frame_{i:03d}.png"))
	z = zipfile.ZipFile(os.path.join(dst, base + "-game.zip"))
	man = json.loads(z.read("manifest.json"))
	clip = next(c for c in man["clips"] if c["name"] == "whole")
	w, h = man["canvas"]["w"], man["canvas"]["h"]
	ox, oy = man["anchor"]["x"] + clip["offset"]["x"], man["anchor"]["y"] + clip["offset"]["y"]
	cells = {}
	for sh in clip["sheets"]:
		im = Image.open(io.BytesIO(z.read(sh["file"]))).convert("RGBA")
		for k in range(sh["frames"]):
			cx, cy = (k % sh["columns"]) * clip["frame"]["w"], (k // sh["columns"]) * clip["frame"]["h"]
			cells[sh["first_frame"] + k] = im.crop((cx, cy, cx + clip["frame"]["w"], cy + clip["frame"]["h"]))
	for i in range(man["frames"]):
		out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
		k = i - clip["start_frame"]
		if k in cells:
			out.alpha_composite(cells[k], (ox, oy))
		out.save(os.path.join(dst, "fx", f"frame_{i:03d}.png"))
	print("  เฟรมแยก", len(meta["frames"]), "→", dst, "(with_sprite/ fx/)")


PAGE_H, PAGE_FEET = 112, 108   # ผืน/แถวเท้าเดียวกับ rion_pack_px (CANVAS_H · FEET) → เทียบกับชีต B ได้ตรง
G_WALK = "★ Rion master v2 · เดินหลัก (ชีต B · kwan เลือก 18 ต.ค.)"


PAGE_CLIPS = {   # ท่าที่ลงหน้าเทส: (กลุ่ม, ชื่อ, ms ความเร็วดู, ms ในเกมหรือ None, พื้นเลื่อน/รอบ)
	"walk": (G_WALK, "เดิน", 90, 37.5, 48),
	"slash2": ("Rion พิกเซล · ชุดครบ · ท่าศึก", "ฟันมีด (PixelLab รอบ 2 · หันซ้ายทุกเฟรม)", 110, None, 0),
}


def page():
	"""ZIP → OUT/px/<คลิป>_<i>.png + index.json (รูปแบบคลิปเดียวกับ rion_pack_px) ให้หน้า animation test วางคู่ชุดเดิม
	เลื่อนทุกเฟรมของท่าเท่ากัน (เท้าต่ำสุด = แถว PAGE_FEET · กลางกรอบรวม) → คงการขึ้นลง/ส่ายตัวที่ PixelLab วาดมา
	ท่าที่ไม่อยู่ใน PAGE_CLIPS (เช่น slash รอบแรกที่ตัวหมุนเข้ากล้อง) ไม่ลงหน้า"""
	base = os.path.join(OUT, "zip", "Idle/animations")
	dst = os.path.join(OUT, "px")
	shutil.rmtree(dst, ignore_errors=True)
	os.makedirs(dst)
	clips = []
	for anim in sorted(os.listdir(base)):
		if anim not in PAGE_CLIPS:
			continue
		group, th, ms, game_ms, travel = PAGE_CLIPS[anim]
		for d in sorted(os.listdir(os.path.join(base, anim))):
			src = os.path.join(base, anim, d)
			fs = [Image.open(os.path.join(src, f)).convert("RGBA") for f in sorted(os.listdir(src)) if f.endswith(".png")]
			bb = [f.getchannel("A").getbbox() for f in fs]
			x0, y1 = min(b[0] for b in bb), max(b[3] for b in bb)
			W = max(b[2] for b in bb) - x0 + 24
			names = []
			for i, f in enumerate(fs):
				c = Image.new("RGBA", (W, PAGE_H))
				c.alpha_composite(f, (12 - x0, PAGE_FEET - y1))
				n = f"pixellab_{anim}_{d}_{i}"
				c.save(os.path.join(dst, n + ".png"))
				names.append(n)
			sign = {"east": 1, "west": -1}.get(d, 0)
			for cid, label, t in ((f"pixellab_{anim}_{d}", "ความเร็วดู", ms), (f"pixellab_{anim}_{d}_game", "ความเร็วในเกม", game_ms)):
				if t is None:
					continue
				clips.append({"group": group, "id": cid, "label": f"PixelLab · {th} · {d} · {label} (ทดลอง 18 ต.ค. · จาก master v2)",
					"frames": names, "ms": t, "loop": True, "w": W, "travel": travel * sign, "src": [f"pixellab {anim} {d}"]})
	json.dump({"_doc": "PixelLab ท่าจาก master v2 · tools/sprites/pixellab_walk.py page · ร่าง ยังไม่เข้าเกม", "clips": clips},
		open(os.path.join(dst, "index.json"), "w"), ensure_ascii=False, indent=1)
	print("คลิป", [c["id"] for c in clips], "→", dst)


if __name__ == "__main__":
	cmd = sys.argv[1] if len(sys.argv) > 1 else "ref"
	{"ref": make_ref, "balance": balance, "character": character, "fetch": fetch, "page": page,
	 "walk": lambda: walk(sys.argv[2:] or ["east"]),
	 "slash": lambda: walk(sys.argv[2:] or ["west"], "slash"),
	 "slash2": lambda: walk(sys.argv[2:] or ["west"], "slash2"),
	 "prompt": lambda: show_prompt(sys.argv[2], (sys.argv[3:] or [None])[0]),
	 "anim": lambda: anim(sys.argv[2], sys.argv[3:] or None),
	 "vfx_frames": lambda: vfx_frames(sys.argv[2] if len(sys.argv) > 2 else "slash2_trail"),
	 "vfx": lambda: vfx(sys.argv[2] if len(sys.argv) > 2 else "slash2_trail")}[cmd]()
