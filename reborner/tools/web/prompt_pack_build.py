"""หน้า "ชุดคำสั่งเจนท่า Rion" — อ่าน docs/art-bible/rion_hires/PROMPT_PACK.md (แหล่งความจริง) → HTML หน้าเดียว
  python3 tools/web/prompt_pack_build.py <out.html>   แล้วเผยแพร่ทับลิงก์เดิม (ลิงก์อยู่ใน CLAUDE.md)
ภาพแนบ 2 ภาพฝังเป็นภาพย่อ + ลิงก์ไฟล์เต็มบน GitHub (repo public) · ติ๊ก "เจนแล้ว" เก็บใน localStorage ของเครื่องคนดู"""
import base64, html, io, json, os, re, sys
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "docs/art-bible/rion_hires")
GH = "https://github.com/pongsaton-stack/caveman/blob/claude/zealous-goldberg-50frc1/reborner/docs/art-bible/rion_hires/"
ATTACH = [("ภาพ 1", "flow_trial_v14b_3.jpg", "ชีตต้นแบบลายเส้นและสัดส่วน"), ("ภาพ 2", "rion_flow_ref.png", "หน้าตรง Rion")]


def thumb(name, w=260):
	im = Image.open(os.path.join(D, name)).convert("RGB")
	im.thumbnail((w, w * 2))
	b = io.BytesIO(); im.save(b, "JPEG", quality=82)
	return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def sheets():
	md = open(os.path.join(D, "PROMPT_PACK.md"), encoding="utf-8").read()
	out = []
	for m in re.finditer(r"^## (\S+) · ([^\n]+)\n<!-- note: ([^\n]*?) \| cells: (\d+) -->\n```\n(.*?)\n```", md, re.S | re.M):
		out.append({"id": m[1], "title": m[2], "note": m[3], "cells": int(m[4]), "text": m[5]})
	return out


def main(path):
	S = sheets()
	att = "".join(f'<figure class="att"><img src="{thumb(f)}" alt="{html.escape(n)}: {html.escape(d)}"><figcaption><b>{n}</b> {d}<br><a href="{GH}{f}" target="_blank" rel="noopener">{f}</a></figcaption></figure>' for n, f, d in ATTACH)
	cards = []
	for i, s in enumerate(S):
		grp = "ท่าที่มี prompt อยู่แล้ว" if s["id"].startswith(("14", "15")) else "ท่าใหม่"
		cards.append(f'''<article class="sheet" id="s{s["id"].replace("-", "_")}" data-id="{s["id"]}">
<header><span class="step">{i + 1}/{len(S)}</span><h2><span class="sid">{s["id"]}</span> {html.escape(s["title"])}</h2>
<label class="done"><input type="checkbox" id="done_{s["id"].replace("-", "_")}"> เจนแล้ว</label></header>
<p class="note">{html.escape(s["note"])}</p>
<p class="meta">{s["cells"]} ช่อง · แนบภาพ 1 + ภาพ 2 ตามลำดับ · {grp}</p>
<div class="actions"><button type="button" class="copy">คัดลอก prompt</button><span class="msg" role="status"></span></div>
<details><summary>ดูข้อความ</summary><pre>{html.escape(s["text"])}</pre></details></article>''')
	tpl = open(os.path.join(os.path.dirname(__file__), "prompt_pack.tpl.html"), encoding="utf-8").read()
	page = tpl.replace("%%ATTACH%%", att).replace("%%CARDS%%", "\n".join(cards)).replace("%%N%%", str(len(S))).replace("%%CELLS%%", str(sum(s["cells"] for s in S)))
	open(path, "w", encoding="utf-8").write(page)
	print(path, len(page), "bytes ·", len(S), "ชีต")


if __name__ == "__main__":
	main(sys.argv[1])
