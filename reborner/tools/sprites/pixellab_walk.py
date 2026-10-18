"""Rion master v2 → PixelLab (API v2) → ท่าเดิน 4 ทิศ · kwan 18 ต.ค. 2026 "ถ้าใช้ pixellab จบไหม" → เลือก "1" ใส่คีย์ทดลอง

คีย์อ่านจาก env PIXELLAB_API_KEY เท่านั้น (ห้ามใส่ใน repo/แชท) · ทุกคำสั่งที่เสียเครดิตพิมพ์ยอดคงเหลือก่อน-หลัง
ขั้น:
  python3 tools/sprites/pixellab_walk.py ref          ทำภาพอ้างอิงหันหน้า (ไม่ต่อเน็ต · ไม่เสียเครดิต)
  python3 tools/sprites/pixellab_walk.py balance      ดูยอดคงเหลือ
  python3 tools/sprites/pixellab_walk.py character    สร้างตัวละครจากภาพอ้างอิง 4 ทิศ (/create-character-v3 · ~ceil(w*h*4/65536) gen)
  python3 tools/sprites/pixellab_walk.py walk [ทิศ…]  ท่าเดินของตัวละครที่สร้างแล้ว (ค่าเริ่ม east · /characters/animations)
  python3 tools/sprites/pixellab_walk.py fetch        ดึง ZIP ของตัวละคร แตกภาพลง OUT
ผลทั้งหมดอยู่ใน assets/sprites/pixellab_draft/ (.gdignore · ร่าง ยังไม่เข้าเกม) · state.json เก็บ character_id / job id
"""
import base64
import io
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
	try:
		with urllib.request.urlopen(req, timeout=120) as r:
			data = r.read()
	except urllib.error.HTTPError as e:
		sys.exit(f"{method} {path} → HTTP {e.code}: {e.read().decode()[:2000]}")
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


def walk(dirs):
	s = state()
	if "character_id" not in s:
		sys.exit("ยังไม่มีตัวละคร: รัน character ก่อน")
	balance()
	r = call("POST", "/characters/animations", {"character_id": s["character_id"], "animation_name": "walk",
		"mode": "v3", "action_description": WALK_ACTION, "frame_count": 8, "keep_first_frame": False, "directions": dirs, "seed": 18})
	s.setdefault("walk", []).append(r)
	save_state(s)
	print(json.dumps(r, ensure_ascii=False)[:800])
	for jid in r.get("background_job_ids") or ([r["background_job_id"]] if r.get("background_job_id") else []):
		j = wait(jid, "ท่าเดิน")
		s.setdefault("walk_jobs", {})[jid] = j.get("status")
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


if __name__ == "__main__":
	cmd = sys.argv[1] if len(sys.argv) > 1 else "ref"
	{"ref": make_ref, "balance": balance, "character": character, "fetch": fetch,
	 "walk": lambda: walk(sys.argv[2:] or ["east"])}[cmd]()
