#!/usr/bin/env python3
"""ดึงข้อมูลรายงานวิจัยท่า 102 ท่าของทีม (Muse R2) จากหน้า HTML → docs/design/moves/moves_team_r2.json
ให้หน้า "ต้นไม้ท่า 6 สาย" (tools/web/skill17_page_build.py) แสดงคำแนะนำของทีมบนการ์ดแต่ละท่า (kwan 27 ต.ค. "เอาที่ทีม แนะนำมาใส่ด้วย")
ใช้: python3 tools/data/moves_team_extract.py
ข้อความจากรายงานเก็บเป็นตัวหนังสือล้วน (ตัดแท็ก HTML ออก) · ** ตัวหนา ** เก็บไว้ให้ตัวสร้างหน้าแปลงเอง
"""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "docs/design/moves/MOVES_RESEARCH_102_R2.html")
OUT = os.path.join(ROOT, "docs/design/moves/moves_team_r2.json")


def grab(s, name):
	i = s.index("const " + name + " = ") + len("const " + name + " = ")
	return json.JSONDecoder().raw_decode(s[i:])[0]


def text(h):
	"""HTML ของรายงาน → ตัวหนังสือ: ย่อหน้า/ข้อย่อยขึ้นบรรทัดใหม่ · ตัวหนาเป็น ** **"""
	h = re.sub(r"<\s*(strong|b)\s*>", "**", h)
	h = re.sub(r"<\s*/\s*(strong|b)\s*>", "**", h)
	h = re.sub(r"<\s*li[^>]*>", "\n• ", h)
	h = re.sub(r"<\s*(p|br|ol|ul|h\d)[^>]*>", "\n", h)
	h = re.sub(r"<[^>]+>", "", h)
	h = html.unescape(h)
	return re.sub(r"\n\s*\n+", "\n", h).strip()


def main():
	s = open(SRC, encoding="utf-8").read()
	data = grab(s, "DATA")
	deep = grab(s, "DEEP")
	deep.update(grab(s, "DEEP2"))
	fixes = {f["code"]: f for b in data["fixlist"].values() for f in b}
	out = {}
	for m in data["moves"]:
		c = m["code"]
		fr = m.get("frames") or {}
		secs = {d["t"]: text(d["h"]) for d in deep.get(c, [])}
		f = fixes.get(c, {})
		out[c] = {
			"verdict": m["verdict"],   # ok = เข้ากัน · fix = ต้องปรับ
			"science": m.get("science_head", ""),
			"science_text": m.get("science", ""),
			"anime": m.get("anime", ""),
			"compare": m.get("compare", ""),
			"fix": f.get("text", "") or m.get("fix", ""),
			"fix_note": f.get("note", ""),
			"frames_total": fr.get("total"),
			"hits": fr.get("hits", []),
			"segments": fr.get("segments", []),
			"frames_raw": fr.get("raw", ""),
			"proposal": secs.get("ข้อเสนอปรับ", ""),
			"urls": m.get("urls", []),
		}
	json.dump({"_doc": "สกัดจาก MOVES_RESEARCH_102_R2.html ด้วย tools/data/moves_team_extract.py · ห้ามแก้มือ", "moves": out},
		open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
	ok = sum(1 for v in out.values() if v["verdict"] == "ok")
	print(OUT, len(out), "ท่า · เข้ากัน", ok, "· ต้องปรับ", len(out) - ok, "· มีข้อเสนอปรับ", sum(1 for v in out.values() if v["proposal"]))


if __name__ == "__main__":
	main()
