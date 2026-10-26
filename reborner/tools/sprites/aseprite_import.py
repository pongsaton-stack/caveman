# tools/sprites/aseprite_import.py — ดึงไฟล์ .aseprite (ที่ kwan แก้ใน Aseprite) กลับเป็น PNG ทีละเฟรม
# รัน: python3 tools/sprites/aseprite_import.py <ไฟล์.aseprite> [--out โฟลเดอร์] [--into โฟลเดอร์เกม]
#   ชื่อไฟล์ตามแท็ก: แท็ก 1 เฟรม → <แท็ก>.png · หลายเฟรม → <แท็ก><i>.png (ตรงกับชื่อสไปรต์ในเกม เช่น south_w0)
#   ไม่มีแท็ก → frame_<i>.png · เขียน meta.json (ขนาด จังหวะ แท็ก เลเยอร์ ข้อสังเกต) คู่กันเสมอ
#   ค่าเริ่ม --out = docs/art-bible/aseprite/imported/<ชื่อไฟล์>/ (พื้นที่พัก ไม่แตะเกม)
#   --into = เขียนทับสไปรต์ในเกมตรง ๆ — ใช้เมื่อ kwan อนุมัติแล้วเท่านั้น (กฎ CLAUDE.md: ภาพทดลองห้ามเข้าเกมก่อนอนุมัติ)
import argparse, json, os
import aseprite_io as A

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def export_frames(spr, out):
	os.makedirs(out, exist_ok=True); names = {}
	for name, a, z, _ in spr.tags:
		for i in range(a, z + 1): names.setdefault(i, name if a == z else '%s%d' % (name, i - a))
	written = []
	for i, f in enumerate(spr.frames):
		n = names.get(i, 'frame_%d' % i); f.save(os.path.join(out, n + '.png')); written.append(n)
	return written

if __name__ == '__main__':
	ap = argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--out'); ap.add_argument('--into')
	a = ap.parse_args()
	spr = A.read(a.file)
	out = a.into or a.out or os.path.join(ROOT, 'docs/art-bible/aseprite/imported', os.path.splitext(os.path.basename(a.file))[0])
	names = export_frames(spr, out)
	meta = {'source': os.path.basename(a.file), 'size': [spr.width, spr.height], 'frames': names, 'durations_ms': spr.durations,
		'tags': [{'name': t[0], 'from': t[1], 'to': t[2], 'direction': t[3]} for t in spr.tags], 'layers': spr.layers, 'notes': spr.notes}
	if not a.into: json.dump(meta, open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print('ok', len(names), 'เฟรม →', out)
	for n in spr.notes: print('  หมายเหตุ:', n)
