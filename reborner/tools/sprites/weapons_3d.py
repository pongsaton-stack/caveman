# tools/sprites/weapons_3d.py — อาวุธปั้นใน Blender แล้ว render หมุนรอบตัว → พิกเซล 48px (kwan 7 ต.ค. 2026 "render อาวุธ ลงเทส")
#
#   python3 tools/sprites/weapons_3d.py        (ต้องเปิด Blender MCP ก่อน: tools/blender/start_blender_mcp.sh ที่ราก repo)
#
# 1) tools/blender/weapons_scene.py ปั้นตัวอย่าง 6 ชิ้น (ตระกูลละ 1) จาก primitive · Workbench · กล้องตั้งฉากเฉียงลง 28° · หมุน 16 มุม · 96px ขอบคม
# 2) ลดสีต่อชิ้น ≤ 12 สี (ทุกมุมใช้พาเลตต์เดียวกัน ไม่กะพริบ) → ย่อ ×2 ด้วยสีส่วนใหญ่ในบล็อก → เส้นขอบ hue-shift (ตัวช่วยเดียวกับ weapons_held.py)
# ออก assets/sprites/weapons_3d_draft/<id>_<00-15>.png + index.json (.gdignore · ร่าง ยังไม่เข้าเกม) · ภาพตรวจ docs/art-bible/weapons/weapons_3d_preview.png
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from weapons_held import mode_downscale, outline

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets/sprites/weapons_3d_draft')
N, RAW, COLORS = 16, 96, 12
IDS = ['SL-1', 'CR-2', 'PC-1', 'ST-1', 'DV-1', 'BD-1']

def render(raw):
	r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/blender/bl.py'), os.path.join(ROOT, 'tools/blender/weapons_scene.py'),
		'OUT=' + raw, 'N=%d' % N, 'SIZE=%d' % RAW], capture_output=True, text=True)
	if r.returncode:
		sys.exit('Blender: ' + (r.stderr or r.stdout).strip() + '\n(เปิด Blender ก่อน: tools/blender/start_blender_mcp.sh)')
	print(r.stdout.strip())

def pixelize(frames):
	"""พาเลตต์ร่วมทุกมุม → ย่อ ×2 → เส้นขอบ"""
	solid = []
	for im in frames:
		a = np.asarray(im.convert('RGBA')).copy(); a[..., 3] = np.where(a[..., 3] > 127, 255, 0); solid.append(a)
	strip = np.concatenate([a[..., :3] for a in solid], axis=1)
	pal = Image.fromarray(strip, 'RGB').quantize(COLORS, method=Image.Quantize.MEDIANCUT)
	out = []
	for a in solid:
		q = np.asarray(Image.fromarray(a[..., :3], 'RGB').quantize(palette=pal, dither=Image.Dither.NONE).convert('RGB'))
		rgba = np.dstack([q, a[..., 3]]).astype(np.uint8)
		out.append(outline(mode_downscale(Image.fromarray(rgba, 'RGBA'), 2)))
	return out

def main():
	os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, '.gdignore'), 'a').close()
	names = {r['weapon_id']: r for r in __import__('csv').DictReader(open(os.path.join(ROOT, 'data/weapons.csv'), encoding='utf-8'))}
	with tempfile.TemporaryDirectory() as raw:
		render(raw)
		items = []
		sheet = Image.new('RGBA', (48 * 4 * 8, 48 * 4 * len(IDS)), (60, 64, 70, 255))
		for r, wid in enumerate(IDS):
			px = pixelize([Image.open(os.path.join(raw, f'{wid}_{i:02d}.png')) for i in range(N)])
			for i, im in enumerate(px):
				im.save(os.path.join(OUT, f'{wid}_{i:02d}.png'))
				if i % 2 == 0:
					sheet.alpha_composite(im.resize((192, 192), Image.NEAREST), (i // 2 * 192, r * 192))
			w = names.get(wid, {})
			items.append({'id': wid, 'name': w.get('name', ''), 'school': w.get('school', ''), 'frames': N})
	json.dump({'_doc': 'อาวุธ render จาก Blender (tools/sprites/weapons_3d.py) · 48px · หมุน %d มุม · ร่าง ยังไม่เข้าเกม' % N, 'size': 48, 'items': items},
		open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	sheet.save(os.path.join(ROOT, 'docs/art-bible/weapons/weapons_3d_preview.png'))
	print('ok', len(items), 'ชิ้น ×', N, 'มุม →', OUT)

if __name__ == '__main__':
	main()
