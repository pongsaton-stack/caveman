#!/usr/bin/env python3
# สร้างหน้า "pixellab animation test" — เฉพาะภาพที่ PixelLab เจน · มาสเตอร์ของอนิเมชันทั้งเกม (kwan 18 ต.ค. 2026)
# ใช้: python3 tools/web/pixellab_test_build.py <out.html>
# แหล่งความจริง = docs/art-bible/pixellab_test/catalog.json · prompt อ่านจาก tools/sprites/pixellab_walk.py (ไม่พิมพ์ซ้ำ)
import base64, glob, json, os, sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = lambda *a: os.path.join(ROOT, *a)
CATALOG = P('docs/art-bible/pixellab_test/catalog.json')
TPL = P('tools/web/pixellab_test.tpl.html')
DIR_ORDER = ['south', 'south-east', 'east', 'north-east', 'north', 'north-west', 'west', 'south-west']

sys.path.insert(0, P('tools/sprites'))
import pixellab_walk as plw  # noqa: E402


def uri(path, mime):
	return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def frames_of(src):
	f = P(src)
	if os.path.isfile(f):
		return [f]
	out = sorted(glob.glob(os.path.join(f, 'frame_*.png')))
	if not out:
		raise SystemExit(f'ไม่มีเฟรม: {src}')
	return out


def foot_of(files):
	# แถวล่างสุดที่มีพิกเซลทึบ (ทุกเฟรมของทิศเดียวกันใช้ค่าเดียว → เท้าไม่กระโดด) · กลาง x ของตัวทั้งชุด
	bottom, xs = 0, []
	for f in files:
		a = np.asarray(Image.open(f).convert('RGBA'))[..., 3] > 0
		ys, x = np.nonzero(a)
		if len(ys):
			bottom = max(bottom, int(ys.max()))
			xs += [int(x.min()), int(x.max())]
	return bottom + 1, (min(xs) + max(xs) + 1) / 2 if xs else 0


def prompt_of(p):
	if p['type'] == 'description':
		return {'label': 'description (create-character-v3)', 'text': plw.DESC}
	if p['type'] == 'legacy':
		return {'label': f"ACTIONS['{p['key']}'] (คำสั่งแบบเก่า) + description", 'text': plw.ACTIONS[p['key']] + '\n\n— description —\n' + plw.DESC}
	if p['type'] == 'moves':
		d = p.get('dir') or plw.MOVES[p['key']]['dir']
		return {'label': f"MOVES['{p['key']}'] · {d} (คำสั่ง 8 ส่วน)", 'text': plw.build_action(p['key'], d) + '\n\n— description —\n' + plw.build_description()}
	raise SystemExit(f'prompt type ไม่รู้จัก: {p}')


def build():
	cat = json.load(open(CATALOG, encoding='utf-8'))
	data = {'categories': cat['categories'], 'backgrounds': [], 'entities': []}
	n_frames = 0
	for b in cat['backgrounds']:
		im = Image.open(P(b['file']))
		data['backgrounds'].append({**{k: b[k] for k in ('id', 'name', 'ground', 'scale')}, 'w': im.width, 'h': im.height,
			'src': uri(P(b['file']), 'image/jpeg' if b['file'].endswith('.jpg') else 'image/png'), 'file': b['file']})
	for e in cat['entities']:
		st = json.load(open(P(e['state']), encoding='utf-8')) if e.get('state') else {}
		ent = {k: e[k] for k in ('id', 'cat', 'name')}
		ent.update({'character_id': st.get('character_id', ''), 'master': e.get('master', ''), 'anims': []})
		for a in e['anims']:
			dirs = {}
			for d, src in a['dirs'].items():
				files = frames_of(src)
				foot, cx = foot_of(files)
				w, h = Image.open(files[0]).size
				dirs[d] = {'frames': [uri(f, 'image/png') for f in files], 'w': w, 'h': h, 'foot': foot, 'cx': cx, 'src': src}
				n_frames += len(files)
			for d, base in (a.get('mirror') or {}).items():
				dirs[d] = {**dirs[base], 'mirror': base}
			order = [d for d in DIR_ORDER if d in dirs]
			ent['anims'].append({**{k: a.get(k) for k in ('id', 'name', 'kind', 'status', 'date', 'gens', 'seed', 'ms', 'game_ms', 'travel', 'notes')},
				'dirs': {d: dirs[d] for d in order}, 'prompt': prompt_of(a['prompt'])})
		data['entities'].append(ent)
	return data, n_frames


def main():
	if len(sys.argv) != 2:
		raise SystemExit('ใช้: python3 tools/web/pixellab_test_build.py <out.html>')
	data, n = build()
	html = open(TPL, encoding='utf-8').read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
	open(sys.argv[1], 'w', encoding='utf-8').write(html)
	anims = sum(len(e['anims']) for e in data['entities'])
	print(f'{sys.argv[1]}: {len(html) / 1e6:.2f} MB · ตัวละคร {len(data["entities"])} · ท่า {anims} · เฟรม {n} · ฉาก {len(data["backgrounds"])}')


if __name__ == '__main__':
	main()
