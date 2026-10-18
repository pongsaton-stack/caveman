"""Rion master v2 → PixelLab (API v2) → ท่าเดิน 4 ทิศ · kwan 18 ต.ค. 2026 "ถ้าใช้ pixellab จบไหม" → เลือก "1" ใส่คีย์ทดลอง

คีย์อ่านจาก env PIXELLAB_API_KEY เท่านั้น (ห้ามใส่ใน repo/แชท) · ทุกคำสั่งที่เสียเครดิตพิมพ์ยอดคงเหลือก่อน-หลัง
ขั้น:
  python3 tools/sprites/pixellab_walk.py ref          ทำภาพอ้างอิงหันหน้า (ไม่ต่อเน็ต · ไม่เสียเครดิต)
  python3 tools/sprites/pixellab_walk.py balance      ดูยอดคงเหลือ
  python3 tools/sprites/pixellab_walk.py character    สร้างตัวละครจากภาพอ้างอิง 4 ทิศ (/create-character-v3 · ~ceil(w*h*4/65536) gen)
  python3 tools/sprites/pixellab_walk.py walk [ทิศ…]  ท่าเดินของตัวละครที่สร้างแล้ว (ค่าเริ่ม east · /characters/animations)
  python3 tools/sprites/pixellab_walk.py slash [ทิศ…] ฟันมีด (ค่าเริ่ม west · ท่าในศึกหันซ้าย)
  python3 tools/sprites/pixellab_walk.py fetch        ดึง ZIP ของตัวละคร แตกภาพลง OUT
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
WALK_ACTION = "walking at a steady pace, arms swinging opposite to the legs, legs pass each other mid-step, body bobs slightly"
# ท่าในศึกหันซ้าย (RION_MASTER) · มีดทำครัวในมือหน้าทุกเฟรม (Flow ทำมีดหายกลางท่า 3 รอบติด → จุดที่ต้องทดสอบ)
SEEDS = {"slash2": 27}
ACTIONS = {"walk": WALK_ACTION,
	"slash": "slashing with a small kitchen knife held in the front hand in every frame: raise the knife behind the shoulder, "
		"step forward and swing it down fast in an arc toward an enemy on the left, follow through, then recover to a ready stance",
	# รอบ 2 (kwan 18 ต.ค. "ลองอีกรอบ"): รอบแรกเฟรม 5–7 หมุนหันเข้ากล้อง + แทงตรง + ใบมีดยาว
	"slash2": "side view, the body stays facing LEFT in every frame and never turns toward the camera: nose, cap brim and toes point left, "
		"backpack on the right. A short small kitchen knife (blade about the length of the hand) stays in the front hand in every frame. "
		"Raise the knife up behind the shoulder, step forward with the front foot and slash it down in a curved arc in front of the body "
		"toward an enemy on the left, follow through low, then return to a ready stance still facing left"}


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
	 "slash2": lambda: walk(sys.argv[2:] or ["west"], "slash2")}[cmd]()
