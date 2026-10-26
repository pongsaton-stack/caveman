# tools/sprites/sheet_cut_test.py — ตรวจ sheet_cut.py แบบไป-กลับ (ไม่ต้องมีชีตจริง)
#
#   python3 tools/sprites/sheet_cut_test.py [--keep]
#
# ทำชีตจำลองแบบที่ตัวเจนภาพให้มา จากเฟรม Rion จริงใน poses64_draft: ขยาย k เท่า · วางห่างไม่เท่ากัน สูงต่ำไม่เท่ากัน ·
# พื้นสีเรียบ / ตารางหมากรุกปลอม · สีเพี้ยนสุ่ม ±jitter → ตัดด้วย sheet_cut → เทียบกับต้นฉบับทีละพิกเซล (ตำแหน่ง + สีตรงเป๊ะ)
# ผ่าน = จำนวนเฟรมเท่าเดิม และตรง ≥ MIN_MATCH · --keep = เก็บผลไว้ที่ assets/sprites/sheet_cut_draft/ ให้หน้า animation test เล่นเทียบ
import argparse, glob, os, random, sys, tempfile
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet_cut as sc

MIN_MATCH = 0.93   # สีเพี้ยนใกล้ขอบระหว่างสองเฉดของพาเลตต์ปัดผิดเฉดได้บ้าง — ตัวเลขนี้คือเกณฑ์ของเทสต์ ไม่ใช่ค่าเกม
CASES = [   # (คลิป, ขยาย k เท่า, พื้น, สีเพี้ยน ±)
	('rion_walk_west_v2', 6, 'flat', 6),
	('rion_attack_v2', 5, 'checker', 8),
	('rion_run_south', 7, 'flat', 0),
]
SIZE, BASE = (64, 76), 74   # ผืน Rion ใน poses64 (หัวเผื่อ 12px)

def frames(clip, n=8):
	fs = sorted(glob.glob(os.path.join(sc.ROOT, f'assets/sprites/poses64_draft/{clip}_[0-9]*.png')), key=lambda p: int(p.rsplit('_', 1)[1][:-4]))
	return [np.asarray(Image.open(p).convert('RGBA')) for p in fs][:n]

def synth(fr, k, bg, jitter, path, rnd):
	W = 60 + sum(f.shape[1] * k + 60 for f in fr); H = fr[0].shape[0] * k + 140
	can = np.zeros((H, W, 3), int)
	if bg == 'checker':
		yy, xx = np.mgrid[:H, :W]; c = ((yy // 16 + xx // 16) % 2).astype(bool)
		can[c] = (204, 204, 204); can[~c] = (255, 255, 255)
	else: can[:] = (236, 228, 212)
	x = 40
	for f in fr:
		big = f.repeat(k, 0).repeat(k, 1); y = 50 + rnd.randint(-18, 18)
		m = big[..., 3] > 0
		rgb = big[..., :3].astype(int) + np.random.default_rng(rnd.randint(0, 1 << 30)).integers(-jitter, jitter + 1, big[..., :3].shape)
		reg = can[y:y + big.shape[0], x:x + big.shape[1]]; reg[m] = rgb[m]
		x += big.shape[1] + 30 + rnd.randint(0, 30)
	Image.fromarray(np.clip(can, 0, 255).astype(np.uint8)).save(path)

def match(orig, got):
	ref, _ = sc.place([o[o[..., 3].any(1)][:, o[..., 3].any(0)] for o in orig], SIZE, BASE)
	ok = tot = 0
	for r, g in zip(ref, got):
		ro, go = r[..., 3] > 0, g[..., 3] > 0; m = ro | go; tot += m.sum()
		ok += (ro & go & (np.abs(r[..., :3].astype(int) - g[..., :3]).max(2) == 0)).sum()
	return ok / tot

def main():
	ap = argparse.ArgumentParser(); ap.add_argument('--keep', action='store_true'); g = ap.parse_args()
	rnd = random.Random(3); bad = 0
	with tempfile.TemporaryDirectory() as tmp:
		for clip, k, bg, jit in CASES:
			fr = frames(clip); p = os.path.join(tmp, f'{clip}.png'); synth(fr, k, bg, jit, p, rnd)
			out = sc.OUT_DEFAULT if g.keep else tmp
			rep, got = sc.cut(p, f'demo_{clip}', out=out, size=SIZE, baseline=BASE, palette='rion', ms=80, verbose=False)
			s = match(fr, got); ok = len(got) == len(fr) and s >= MIN_MATCH; bad += not ok
			print(f'{"ok  " if ok else "FAIL"} {clip}: ชีต x{k} พื้น{bg} สีเพี้ยน±{jit} → {rep["scale_mode"]} · เฟรม {len(fr)}→{len(got)} · ตรงต้นฉบับ {s * 100:.1f}%')
			if g.keep:   # ให้หน้าเทสเล่นคู่กับต้นฉบับ
				import json
				jp = os.path.join(out, f'demo_{clip}.json'); d = json.load(open(jp, encoding='utf-8'))
				d.update(source=f'ชีตจำลอง (x{k} · พื้น{bg} · สีเพี้ยน±{jit}) จาก poses64_draft/{clip}', compare_with=clip, match=round(s * 100, 1))
				json.dump(d, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print(f'FAILS {bad}')
	sys.exit(1 if bad else 0)

if __name__ == '__main__':
	main()
