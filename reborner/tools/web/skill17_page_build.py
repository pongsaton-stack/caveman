#!/usr/bin/env python3
"""หน้า "ต้นไม้ท่า 6 สาย" — ชื่อ ท่าทาง ศาสตร์อ้างอิง อาวุธที่เหมาะ + ท่าประจำอาวุธ (ร่าง ยังไม่เข้าเกม)
ใช้: python3 tools/data/skill17_proposal.py && python3 tools/data/skill17_content.py && python3 tools/web/skill17_page_build.py <out.html>
"""
import base64, csv, html, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
SCHOOLS = [("คม", "blade", "ฟัน · เลือดไหล · ตีหลายครั้ง", "เกราะ/กระดูก"), ("ทุบ", "crush", "เจาะเกราะ · ตรึง · หน่วงคิวศัตรู", "ช้า · ร่างนุ่ม"),
	("แทง", "pierce", "ทะลุแนวหน้า-หลัง · เบา", "ฝูงกระจายเต็มสนาม"), ("ยิง", "shoot", "ตีแถวหลังได้เต็ม", "ดาเมจต่อครั้งต่ำกว่า"),
	("กล", "device", "สถานะหลากหลาย", "ดาเมจดิบต่ำสุด"), ("มือเปล่า", "fist", "ตีหลายครั้งที่สุด · เบาที่สุด", "ค่าอาวุธต่ำ")]
BR = {"A": "ตีเดี่ยว", "B": "ตีหมู่", "C": "จังหวะ/ควบคุม"}
SCOPE = {"single": "เดี่ยว", "row": "ทั้งแถว", "column": "ทะลุแนว", "all": "ทั้งหมด", "self": "ตัวเอง"}
UNUSABLE = {"rg5", "dv5", "dv6", "fs3"}
PAPER = {"dv1": "ช่องคิวของอุปกรณ์", "dv2": "ช่องคิวของอุปกรณ์", "fs4": "แรงขึ้นตามดาเมจที่รับ", "rg6": "ต้องเล็งนิ่งก่อน"}
e = html.escape
LAB_PAGE = "https://claude.ai/artifact/5JNZaykSQiY9ghpD1V7BPp"   # ห้องทดลองฉากต่อสู้ Godot (หน้าเว็บ)
# ท่าที่มีฉากในห้องทดลองแล้ว: รายชื่ออ่านจากเมนู TECHS ใน tests/lab/lab_stage.gd (เพิ่มท่าใหม่ในเมนู = หน้านี้รู้เอง) · คำอธิบายสั้นของฉากที่ทำจริงเขียนไว้ที่นี่
LAB_NOTE = {
	"bl0": "วิ่งเข้า ง้างระหว่างวิ่ง ฟันตอนถึงตัว ไถลตามแรง → กระโดดถอย 2 สเต็ป",
	"bl1": "วิ่ง → เบรกย่อ → ถีบพุ่งยาวเกือบลอย แทงตอนเท้าแตะพื้น (ฟันดาบเซเบอร์ flèche)",
	"bl2": "ฟันหน้า → ตีลังกาข้ามหัวฟันหลัง → หมุนสว่านผ่านหลังมอนฟันหน้า · วงแสง 3 วงพันตัว (ครั้ง 2–3 ยังยืมภาพฟัน รอเจนท่าฟันย้อนขึ้น)",
	"bl7": "ย่อชาร์จ → พุ่งหมุนสว่านลอดใต้ขา (ภาพหมุน 4 มุม) → ไถลโผล่อีกฝั่ง → เงียบ → แผลเปิด มอนช้าลง (แบบ Attack on Titan)",
	"bl8": "กระโดดจามระดับหัว มีดฝังเกราะ ปล่อยมือ → กระทืบด้ามตอกเป็นลิ่ม → เกราะร้าว (คาบูโตะวาริ)",
	"bl9": "ตั้งท่าทมโบะ → กระโดดฟันจันทร์เสี้ยวกลางหาว → มอนแยกสองซีก ซีกที่ขาดหมุนคว่ำสลายเป็นผง",
	"bl3": "ม้วนเก็บระหว่างวิ่ง → คมกวาดเป็นวงรีรอบทั้งแถว ผ่านหน้ามอนทีละตัว แล้ววนอ้อมหลังแถว",
	"bl10": "วิ่งทะลุแถวไม่หยุด เหวี่ยงคมเลขแปดนอน → เบรก ตั้งการ์ดหลังแถว → กระโดดข้ามกลับ",
	"bl11": "ปั่นมีดบนปลายนิ้ว → ขว้างบินตัดผ่านแถว → วกกลับตัดซ้ำ → รับมีดคืน (2 ครั้ง)",
	"bl4": "หมุน 2 รอบกางแขนมีดออก (ภาพ PixelLab หมุน 8 มุม) → คมลมวงโค้งกวาดทั้งแถว → ค้างท่ากางแขนหันหน้า",
	"bl12": "ย่อหมุนเป็นลมหมุนทะลุแถว → ดีดตัวหมุนกลางอากาศข้ามกลับ (ภาพ PixelLab 8 มุม) · กรวยพายุเถ้า + ใบมีดเงินวน · 2 ครั้ง",
	"bl5": "วิ่ง → ไถลลงท่าย่อมือแตะด้ามในซอง → เงียบ (โลกหยุด) → ชักฟันพุ่งแว้บเดียว → สะบัดคม เก็บเข้าซอง แกร๊ก แผลวาบซ้ำ (ภาพ PixelLab State 2 ภาพ)",
	"bl6": "ตั้งท่าสองมีดระหว่างวิ่ง → ฟันมีดขวา → มีดซ้ายไขว้เป็น X ทิ้งเงาท่าแรก → ค้างท่าไขว้ · เลือดหยด (ภาพ PixelLab State 3 ภาพ · ข้อยกเว้นถือสองมือ)",
	"bl13": "ทรุดต่ำก้าวไขว้เลื้อยเข้า เงาเข้มตามพื้น → ปาดสั้นระดับเข่า → เลื้อยถอยเฉียงออก (ภาพ PixelLab State 1 ภาพ)",
	"bl14": "ก้าวเฉียงลงหน้า อ้อมแนวหน้า → ปาดตัวแถวหลัง → ย้อนก้าวสามเหลี่ยมกลับ (ภาพ PixelLab State 1 ภาพ)",
	"bl15": "รอในการ์ดผ่อน → มอนพุ่งใส่ → พลิกข้อมือปัดให้ไหล → ก้าวเฉียงฟันสวนทันที มอนกระเด็นหมุน (ภาพ PixelLab State 1 ภาพ)",
	"bt0": "ไม้เบสบอล: วิ่งเข้า ง้างกลางอากาศ ฟาดลงเฉียง ไม้จมค้าง → กระโดดถอย · ยืนหายใจ · เลือกอาวุธ Lv.1–10 (ภาพ PixelLab · มีฉากเทียบภาพ Flow)",
}


def lab_techs():
	"""tech_id → [ไฟล์ฉาก] และ ชื่อท่า → [ไฟล์ฉากประกาย] จากเมนูห้องทดลอง"""
	import re
	src = open(P("tests/lab/lab_stage.gd"), encoding="utf-8").read()
	block = src[src.index("const TECHS"):src.index("]]", src.index("const TECHS")) + 2]
	moves, glim = {}, {}
	for tid, name, scene in re.findall(r'\["([^"]+)", "([^"]+)", "res://tests/lab/([\w]+)\.tscn"\]', block):
		if tid == "ทุบ":
			moves.setdefault("bt0", []).append(scene)
		elif tid == "★":
			glim.setdefault(name, []).append(scene)
		elif re.fullmatch(r"[a-z]{2}\d+", tid):
			moves.setdefault(tid, []).append(scene)
	return moves, glim


LAB, GLIM = lab_techs()
TEAM = json.load(open(P("docs/design/moves/moves_team_r2.json"), encoding="utf-8"))["moves"]   # รายงานวิจัยท่าของทีม (tools/data/moves_team_extract.py)


def md(t):
	"""ข้อความทีม → HTML ปลอดภัย: escape ก่อน แล้ว **ตัวหนา** · ขึ้นบรรทัด"""
	t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(t))
	return t.replace("\n", "<br>")


def team_block(tid):
	t = TEAM.get(tid)
	if not t:
		return "", ""
	tag = '<span class="tag tok">ทีม: เข้ากัน</span>' if t["verdict"] == "ok" else '<span class="tag tfix">ทีม: ต้องปรับ</span>'
	rows = f'<dt>ทีมแนะนำ</dt><dd>{md(t["compare"])}</dd>'
	if t["fix"]:
		rows += f'<dt>ต้องแก้</dt><dd class="tfixt">{md(t["fix"])}</dd>'
	if t["segments"] and t["frames_total"]:
		tot = float(t["frames_total"])
		num = [g for g in t["segments"] if isinstance(g.get("from"), (int, float)) and isinstance(g.get("to"), (int, float))]
		segs = "".join(f'<span style="flex:{max(1, g["to"] - g["from"])}" title="{e(str(g["from"]) + "–" + str(g["to"]) + " · " + g["label"])}"></span>' for g in num)
		hits = "".join(f'<i style="left:{min(100, h / tot * 100):.1f}%"></i>' for h in t["hits"] if isinstance(h, (int, float)))
		steps = "".join((f'<li><b>{g["from"]}–{g["to"]}</b> ' if g in num else '<li>') + f'{e(g["label"])}</li>' for g in t["segments"])
		rows += (f'<dt>แผนเฟรม</dt><dd><div class="tl">{segs}{hits}</div><small class="scn">{int(tot)} เฟรม × 60 ms ≈ {tot * 0.06:.1f} วิ · '
			f'โดนที่ {", ".join(str(h) for h in t["hits"]) or "–"}</small><details><summary>ทีละช่วง</summary><ol class="steps">{steps}</ol></details></dd>')
	prop, refs = t["proposal"], ""
	cut = prop.find("**แหล่งอ้างอิง")
	if cut >= 0:
		prop, refs = prop[:cut].strip(), prop[cut:]
	links = " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{e(re.sub(r"^https?://(www\.)?", "", u)[:48])}</a>' for u in t["urls"])
	more = (f'<details class="team"><summary>รายละเอียดจากทีม (ข้อเสนอปรับ · ศาสตร์จริง · อนิเมะอ้างอิง)</summary>'
		f'<h5>ข้อเสนอปรับ</h5><p>{md(prop)}</p><h5>ศาสตร์จริง</h5><p>{md(t["science_text"])}</p>'
		f'<h5>อนิเมะ/สื่ออ้างอิง</h5><p>{md(t["anime"])}</p>'
		+ (f'<h5>แหล่งอ้างอิง</h5><p class="refs">{links}</p>' if links else "") + '</details>')
	return tag, rows + "</dl>" + more + "<dl>"
sys.path.insert(0, P("tools/sprites"))
import pixellab_walk as plw  # noqa: E402  (โหลดคำสั่ง 102 ท่าจาก pixellab_skills.py)


def card(r, c, school, wide=False):
	tid, slot = r["tech_id"], r["slot"]
	new = r["note"].startswith("[เสนอ]") and school != "คม"
	if tid in UNUSABLE:
		tag = '<span class="tag bad">ยังใช้ไม่ได้ในเกม</span>'
	elif new:
		tag = '<span class="tag new">ใหม่ · ร่าง</span>'
	elif r["note"].startswith("[เสนอ]"):
		tag = '<span class="tag wait">ในเกม · ตัวเลขรอยืนยัน</span>'
	else:
		tag = '<span class="tag old">มีในเกม</span>'
	fx = []
	if float(r["ignore_def"] or 0): fx.append(f"เจาะเกราะ {int(float(r['ignore_def']) * 100)}%")
	if float(r["target_av_mult"] or 1) != 1: fx.append(f"เป้าช้าลง {round((float(r['target_av_mult']) - 1) * 100)}%")
	if float(r["self_av_mult"] or 1) != 1: fx.append("ตัวเองเร็วขึ้น")
	if r["ignore_pos"] == "1": fx.append("ทะลุแนว")
	if r["free_row"] == "1": fx.append("ตีแถวหลังเต็ม")
	if r["status"]: fx.append(f"{r['status']} {int(float(r['status_chance']) * 100)}%")
	if r["effect"] == "counter": fx.append("ท่าสวน")
	if tid in PAPER: fx.append(f"เขียนว่า '{PAPER[tid]}' แต่โค้ดยังไม่มี")
	ttag, trows = team_block(tid)
	tag += ttag
	lab = ""
	if tid in LAB:
		tag += f'<a class="tag lab" href="{LAB_PAGE}" target="_blank" rel="noopener">ลองได้ในห้องทดลอง</a>'
		lab = f'<dt>ฉากที่ทำแล้ว</dt><dd>{e(LAB_NOTE.get(tid, ""))} <small class="scn">{e(" · ".join(LAB[tid]))}</small></dd>'
	if r["name_th"] in GLIM:
		lab += f'<dt>ประกาย</dt><dd>มีฉากเกิดประกายได้ท่านี้ <small class="scn">{e(" · ".join(GLIM[r["name_th"]]))}</small></dd>'
	hits = f"×{r['hits']}" if r["hits"] not in ("1", "") else ""
	pw = f"พลัง {r['power']}{hits}" if float(r["power"] or 0) else "ไม่โจมตี"
	br = slot[0] if slot[0] in "ABC" else ""
	wpn = c["weapons"][school][br] if br else [w for b in "ABC" for w in c["weapons"][school][b]]
	wtxt = "ทุกอาวุธในสาย" if not br else " · ".join(wpn)
	return f'''<article class="card{' wide' if wide else ''}{' done' if tid in LAB else ''}" id="{tid}">
<header><span class="slot">{e(slot)}</span><h3>{e(r['name_th'])}</h3>{tag}</header>
<p class="stats"><span>ปลดที่ {r['req_prof']}</span><span>{pw}</span><span>{SCOPE.get(r['scope'], r['scope'])}</span><span>น้ำหนัก {r['weight']}</span><span>SP {r['sp']}</span></p>
{'<p class="fx">' + ''.join(f'<span>{e(x)}</span>' for x in fx) + '</p>' if fx else ''}
<dl><dt>ท่าทาง</dt><dd>{e(c['motion'][tid])}</dd>{lab}{trows}<dt>ศาสตร์</dt><dd>{e(r['art'])}</dd><dt>เหมาะกับ</dt><dd>{e(wtxt)}</dd></dl>
<details><summary>คำสั่ง PixelLab ({plw.MOVES[tid]['frames']} เฟรม · หันซ้าย)</summary><pre class="pr">{e(plw.build_action(tid, 'west'))}</pre></details>
</article>'''


def main():
	rows = list(csv.DictReader(open(P("docs/design/skill_trees_17.csv"), encoding="utf-8")))
	c = json.load(open(P("docs/design/skill_trees_17_content.json"), encoding="utf-8"))
	tabs, panels = [], []
	for name, key, good, bad in SCHOOLS:
		rs = {r["slot"]: r for r in rows if r["school"] == name and r["slot"]}
		cols = ""
		for b in "ABC":
			branch = rs[b + "1"]["branch"]
			nd = sum(1 for i in range(1, 6) if rs[f"{b}{i}"]["tech_id"] in LAB)
			cols += f'<section class="branch"><h4>กิ่ง{e(branch)} <small>{BR[b]} · ทำฉากแล้ว {nd}/5</small></h4><p class="wl">อาวุธที่ชี้ทางมากิ่งนี้: {e(" · ".join(c["weapons"][name][b]))}</p>' + \
				"".join(card(rs[f"{b}{i}"], c, name) for i in range(1, 6)) + "</section>"
		tabs.append(f'<button role="tab" data-t="{key}" style="--sc:var(--{key})">{name}</button>')
		panels.append(f'''<div class="panel" id="p-{key}" style="--sc:var(--{key})" hidden>
<p class="lede"><b>เด่น</b> {e(good)} · <b>ด้อย</b> {e(bad)} · <b>ห้องทดลอง</b> ทำฉากแล้ว {sum(1 for r in rs.values() if r["tech_id"] in LAB)}/17 ท่า</p>
{card(rs["R"], c, name, True)}<div class="cols">{cols}</div>{card(rs["U"], c, name, True)}</div>''')
	# ท่าประจำอาวุธ
	sp = ""
	for name, key, *_ in SCHOOLS:
		items = "".join(f'<li><b>{e(x["weapon"])}</b> — <span class="sn">{e(x["name"])}</span><br><small>{e(x["motion"])} · {e(x["effect"])} · งบเท่าช่อง {e(x["budget"])}</small></li>' for x in c["special"][name])
		sp += f'<section class="sp" style="--sc:var(--{key})"><h4>{name}</h4><ul>{items}</ul></section>'
	tabs.append('<button role="tab" data-t="weapon">ท่าประจำอาวุธ</button>')
	panels.append(f'''<div class="panel" id="p-weapon" hidden><p class="lede">อาวุธแต่ละชนิดมีท่าพิเศษ 1 ท่า ได้จากการใช้อาวุธชนิดนั้นจนชำนาญ · 60 ท่า (สายละ 10)</p>
<ol class="rules">{''.join(f'<li>{x}</li>' for x in c['special_rules'])}</ol><div class="spgrid">{sp}</div><p class="note">{e(c['weapon_note'])}</p></div>''')
	w300 = json.load(open(P("docs/art-bible/weapons/weapons300.json"), encoding="utf-8"))
	ic = lambda wid: "data:image/png;base64," + base64.b64encode(open(P("assets/sprites/weapons300_draft", wid + "_48.png"), "rb").read()).decode()
	wt = ""
	for name, key, *_ in SCHOOLS:
		rowsw = [w for w in w300["weapons"] if w["school"] == name]
		trs = ""
		for t in sorted({w["type_no"] for w in rowsw}):
			ws = [w for w in rowsw if w["type_no"] == t]
			w0 = ws[0]
			flag = ' <span class="tag bad">รอตัดสิน</span>' if w0["needs_decision"] else ""
			trs += f'<tr><th>{e(w0["type"])}{flag}<br><small>กิ่ง {w0["branch"]} · {e(w0["grip"])}</small></th>' + "".join(
				f'<td><img src="{ic(w["id"])}" width="48" height="48" alt="{e(w["name_th"])}" title="{e(w["id"] + " " + w["name_th"])}"></td>' for w in ws) + "</tr>"
		wt += f'<section class="wt" style="--sc:var(--{key})"><h4>{name}</h4><div class="tw"><table><thead><tr><th>ชนิด</th>' + "".join(f"<th>ระดับ {i}</th>" for i in range(1, 6)) + f"</tr></thead><tbody>{trs}</tbody></table></div></section>"
	tabs.append('<button role="tab" data-t="arms">อาวุธ 300</button>')
	panels.append(f'''<div class="panel" id="p-arms" hidden><p class="lede">ตัดจากชีต 6 แผ่นที่ kwan ส่ง (ไอคอนพิกเซล 48) · ชื่อเป็นร่าง (ชนิด + ชั้นดี/ดัดแปลง/ไฮเทค/ตำนาน) · ยังไม่มีค่าพลัง/ราคา · "แบบการจับ" ที่วงเล็บว่ายังไม่มีท่า = ต้องทำท่าถือใหม่</p>
<p class="note">ข้อจำกัด: ระดับ 4–5 ราว 11 ชิ้น (ค้อนปอนด์/อิฐ/ท่อ/หนังสือระดับ 5 · ถุงมือสายมือเปล่าระดับ 4–5) แสงเรืองในชีตทับช่องข้าง ติดเศษมาเล็กน้อย</p>{wt}</div>''')
	budget = open(P("docs/design/skill_trees_17_budget.txt"), encoding="utf-8").read()
	tabs.append('<button role="tab" data-t="balance">หลักสมดุล</button>')
	panels.append(f'''<div class="panel" id="p-balance" hidden>
<ol class="rules"><li>ทุกสายใช้โครงเดียวกับสายคม: ราก + 3 กิ่ง กิ่งละ 5 ท่า + ไม้ตาย</li><li>ช่องเดียวกันปลดที่ความชำนาญเท่ากัน และใช้งบใกล้กัน (ท่าใหม่ต่างกันไม่เกิน 9.3%)</li>
<li>ทุกสายมีท่าสวน 1 ท่าที่ช่อง C5 · ไม้ตาย ปลดที่ 68 SP 40 ทุกสาย</li><li>ความต่างอยู่ที่ "เก่งตอนไหน" (ร่างกายมอน แถว เกราะ ความเร็ว สถานะ) ไม่ใช่ "แรงกว่า"</li>
<li>ตัวเลขทั้งหมดเป็นร่าง ต้องรัน Sim ก่อนใส่เกม</li></ol>
<div class="pre"><pre>{e(budget)}</pre></div></div>''')
	done = [r["tech_id"] for r in rows if r["slot"] and r["tech_id"] in LAB]
	tok = sum(1 for v in TEAM.values() if v["verdict"] == "ok")
	prog_team = f'<br>คำแนะนำทีมวิจัย (Muse · รอบ 2 · 25 ต.ค.): เข้ากัน {tok} · ต้องปรับ {len(TEAM) - tok} ท่า · การ์ดทุกใบมี "ทีมแนะนำ" + แผนเฟรม (แถบ = ช่วงท่า · ขีดดำ = จังหวะโดน) + รายละเอียดกดเปิดได้'
	prog = f'ห้องทดลองฉากต่อสู้: ทำฉากแล้ว {len(done)}/{sum(1 for r in rows if r["slot"])} ท่า · <a href="{LAB_PAGE}" target="_blank" rel="noopener">เปิดห้องทดลอง</a> · การ์ดที่มีขอบเขียว = ลองเล่นได้แล้ว (ร่าง ยังไม่เข้าเกม)' + prog_team
	out = TPL.replace("%TABS%", "".join(tabs)).replace("%PANELS%", "".join(panels)).replace("%PROG%", prog)
	open(sys.argv[1], "w", encoding="utf-8").write(out)
	print(sys.argv[1], f"{len(out) / 1024:.0f} KB")


TPL = '''<title>ต้นไม้ท่า 6 สาย</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mitr:wght@400;500&family=IBM+Plex+Sans+Thai:wght@400;600&display=swap">
<style>
/* หน้าอ่านอ้างอิง: แท็บสาย → ราก · 3 กิ่งเป็นคอลัมน์ · ไม้ตาย · สีประจำสายเป็นแถบบนการ์ด */
:root{--bg:#eef1f4;--panel:#fff;--ink:#1b2430;--muted:#5d6876;--line:#d6dce3;--chip:#e7ecf1;
--blade:#c2412d;--crush:#b7791f;--pierce:#16827a;--shoot:#4d7c2a;--device:#6b4fbf;--fist:#c25a1a;--new:#1f6fd1;--bad:#b42318;--wait:#8a6d00;--lab:#1d7a46;
--fd:"Mitr","IBM Plex Sans Thai",system-ui,sans-serif;--fb:"IBM Plex Sans Thai",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12161c;--panel:#1b2129;--ink:#e6ebf1;--muted:#9aa6b4;--line:#2c3540;--chip:#252d37;
--blade:#ef7a63;--crush:#e0a948;--pierce:#4cc2b6;--shoot:#8cc463;--device:#a68cf0;--fist:#f0904f;--new:#6aa8f5;--bad:#f2786b;--wait:#e2c25a;--lab:#5cc98a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12161c;--panel:#1b2129;--ink:#e6ebf1;--muted:#9aa6b4;--line:#2c3540;--chip:#252d37;
--blade:#ef7a63;--crush:#e0a948;--pierce:#4cc2b6;--shoot:#8cc463;--device:#a68cf0;--fist:#f0904f;--new:#6aa8f5;--bad:#f2786b;--wait:#e2c25a;--lab:#5cc98a;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.6 var(--fb)}
.wrap{max-width:1180px;margin:0 auto;padding-block:20px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font:500 1.7rem/1.2 var(--fd);margin:0 0 4px;text-wrap:balance} .sub{color:var(--muted);margin:0 0 16px}
[role=tablist]{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
[role=tab]{font:500 .95rem var(--fd);color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:6px 14px;cursor:pointer}
[role=tab][aria-selected=true]{background:var(--sc,var(--ink));border-color:var(--sc,var(--ink));color:var(--panel)}
[role=tab]:focus-visible{outline:2px solid var(--new);outline-offset:2px}
.lede{margin:0 0 12px} .cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:14px 0}
@media (max-width:900px){.cols{grid-template-columns:minmax(0,1fr)}}
.branch{display:flex;flex-direction:column;gap:10px;min-width:0}
.branch h4{font:500 1.1rem var(--fd);margin:0;color:var(--sc)} .branch h4 small{color:var(--muted);font:400 .85rem var(--fb)}
.wl{margin:0;font-size:.85rem;color:var(--muted)}
.card{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--sc);border-radius:8px;padding:10px 12px;min-width:0}
.card header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 8px}
.card h3{font:500 1.05rem var(--fd);margin:0}
.slot{font:600 .75rem var(--fb);letter-spacing:.05em;color:var(--sc)}
.tag{font-size:.72rem;border-radius:999px;padding:1px 8px;border:1px solid currentColor;margin-left:auto}
.tag.tok{color:var(--lab);margin-left:0} .tag.tfix{color:var(--wait);margin-left:0} .tfixt{color:var(--wait)}
.tl{position:relative;display:flex;gap:1px;height:8px;margin:4px 0 2px;border-radius:4px;overflow:hidden} .tl span{background:color-mix(in srgb,var(--sc) 45%,var(--chip))}
.tl span:nth-child(even){background:color-mix(in srgb,var(--sc) 25%,var(--chip))} .tl i{position:absolute;top:0;bottom:0;width:2px;background:var(--ink)}
.steps{margin:4px 0 0;padding-left:1.2em;font-size:.82rem} .team h5{font:500 .85rem var(--fd);margin:8px 0 2px} .team p{margin:0;font-size:.85rem} .refs a{color:var(--muted);overflow-wrap:anywhere}
.tag.lab{color:var(--lab);text-decoration:none;margin-left:0} .card.done{box-shadow:inset 3px 0 0 var(--lab)} .scn{color:var(--muted)}
.prog{margin:0 0 14px;padding:8px 12px;border:1px solid var(--line);border-left:3px solid var(--lab);border-radius:8px;background:var(--panel);font-size:.9rem} .prog a{color:var(--lab)}
.tag.new{color:var(--new)} .tag.bad{color:var(--bad)} .tag.wait{color:var(--wait)} .tag.old{color:var(--muted)}
.stats{display:flex;flex-wrap:wrap;gap:4px 10px;margin:4px 0;font-size:.82rem;color:var(--muted);font-variant-numeric:tabular-nums}
.fx{display:flex;flex-wrap:wrap;gap:4px;margin:4px 0} .fx span{background:var(--chip);border-radius:4px;padding:0 6px;font-size:.8rem}
dl{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 8px;margin:6px 0 0;font-size:.88rem}
dt{color:var(--muted)} dd{margin:0}
.wide{margin:0} .rules{padding-left:1.2em;max-width:70ch} .rules li{margin:4px 0}
.spgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:14px}
.sp{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--sc);border-radius:8px;padding:10px 14px;min-width:0}
.sp h4{font:500 1.1rem var(--fd);margin:0 0 6px;color:var(--sc)} .sp ul{margin:0;padding:0;list-style:none;display:grid;gap:8px}
.sp small{color:var(--muted)} .sn{font-family:var(--fd)}
.note{color:var(--muted);font-size:.85rem}
details summary{cursor:pointer;color:var(--muted);font-size:.82rem;margin-top:6px} .pr{white-space:pre-wrap;font-size:.75rem;background:var(--bg);border-radius:6px;padding:8px;margin:6px 0 0}
.wt{margin-bottom:18px} .wt h4{font:500 1.1rem var(--fd);color:var(--sc);margin:0 0 6px} .tw{overflow-x:auto} .wt table{border-collapse:collapse;background:var(--panel)}
.wt th,.wt td{border:1px solid var(--line);padding:4px 8px;text-align:left;font-weight:400;font-size:.85rem} .wt td img{image-rendering:pixelated;display:block}
.pre{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px} .pre pre{margin:0;padding:12px;font-size:.78rem}
</style>
<div class="wrap">
<h1>ต้นไม้ท่า 6 สาย</h1>
<p class="sub">สายละ 17 ท่า · ท่าทางตอนใช้ · ศาสตร์การต่อสู้อ้างอิง · อาวุธที่เหมาะ · ท่าประจำอาวุธ — ร่าง ยังไม่เข้าเกม ตัวเลขรอ Sim</p>
<p class="prog">%PROG%</p>
<div role="tablist">%TABS%</div>
%PANELS%
</div>
<script>
const tabs=[...document.querySelectorAll('[role=tab]')];
function show(t){tabs.forEach(b=>b.setAttribute('aria-selected',b.dataset.t===t));document.querySelectorAll('.panel').forEach(p=>p.hidden=p.id!=='p-'+t);
try{history.replaceState(null,'','#'+t)}catch(e){}}
tabs.forEach(b=>b.onclick=()=>show(b.dataset.t));
const h=location.hash.slice(1);show(tabs.some(b=>b.dataset.t===h)?h:'blade');
</script>
'''

if __name__ == "__main__":
	main()
