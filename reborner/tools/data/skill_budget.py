#!/usr/bin/env python3
"""ตรวจงบท่าแบบหยาบ (ก่อน Sim) — ทุกสายต้องได้ "ค่าต่อหน่วยคิว" ใกล้กันในช่องเดียวกันของต้นไม้

ใช้: python3 tools/data/skill_budget.py [docs/design/skill_trees_17.csv]
ค่า V = พลัง × ครั้ง/100 × ขอบเขต × เจาะเกราะ × หน่วงเป้า × เร่งตัวเอง × สถานะ × ตำแหน่ง × สวน
คะแนน = V ÷ น้ำหนัก (ดาเมจต่อเวลาคิวที่เสีย) · ตัวคูณเป็นค่าประมาณสำหรับเทียบกันเอง ไม่ใช่สูตรเกม
**ตัวตัดสินจริง = Sim** (กฎข้อ 7) — ตารางนี้แค่หาท่าที่หลุดกลุ่มก่อนเสียเวลารัน
"""
import csv, os, sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "design", "skill_trees_17.csv")
SCOPE = {"single": 1.0, "column": 1.5, "row": 1.6, "all": 2.2}   # จำนวนเป้าเฉลี่ยที่โดนจริงในศึก ~1.5–2.5 ตัว
STATUS = {"เลือดไหล": 0.25, "หน่วง": 0.25, "พิษ": 0.25, "ตรึง": 0.6, "สับสน": 0.5, "ผนึก": 0.4}
SCHOOLS = ["คม", "ทุบ", "แทง", "ยิง", "กล", "มือเปล่า"]
SLOTS = ["R", "A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3", "C4", "C5", "U"]


def value(r):
	p = float(r["power"] or 0)
	if p <= 0:
		return None
	v = p * float(r["hits"] or 1) / 100 * SCOPE.get(r["scope"], 1.0)
	v *= 1 + 0.6 * float(r["ignore_def"] or 0)
	v *= 1 + 1.5 * (float(r["target_av_mult"] or 1) - 1)
	v *= 1 + 1.5 * (1 - float(r["self_av_mult"] or 1))
	v *= 1 + STATUS.get(r["status"], 0) * float(r["status_chance"] or 0)
	if r["ignore_pos"] == "1" or r["free_row"] == "1":
		v *= 1.1
	if r.get("effect") == "counter":
		v *= 0.8   # ตีได้เฉพาะเมื่อโดนตีก่อนตาถัดไป
	return v


def main():
	rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
	grid = defaultdict(dict)
	for r in rows:
		if r.get("slot"):
			grid[r["school"]][r["slot"]] = r
	print("ช่อง  " + "".join(f"{s:>16}" for s in SCHOOLS) + "   ต่างจากเฉลี่ยสูงสุด")
	worst = []
	tot = defaultdict(float)
	for sl in SLOTS:
		cells, scores = [], []
		for s in SCHOOLS:
			r = grid[s].get(sl)
			if not r:
				cells.append(f"{'—':>16}")
				continue
			v = value(r)
			if v is None:
				cells.append(f"{'ใช้ไม่ได้*':>16}")
				continue
			sc = v / float(r["weight"])
			scores.append((s, sc))
			tot[s] += sc
			cells.append(f"{r['req_prof']:>3}·{sc:5.2f}·{float(r['sp']) and v / float(r['sp']) * 10:4.2f}")
		avg = sum(x for _, x in scores) / len(scores) if scores else 0
		dev = max((abs(x - avg) / avg for _, x in scores), default=0) if avg else 0
		worst.append((dev, sl))
		print(f"{sl:<5} " + "".join(cells) + f"   {dev * 100:5.1f}%")
	print("\nรวมคะแนน/คิวทั้งต้นไม้: " + " · ".join(f"{s} {tot[s]:.1f}" for s in SCHOOLS))
	m = sum(tot.values()) / len(SCHOOLS)
	print("ต่างจากเฉลี่ย: " + " · ".join(f"{s} {(tot[s] - m) / m * 100:+.1f}%" for s in SCHOOLS))
	print("\nช่องละ: req · คะแนน (V ÷ น้ำหนัก) · ค่าต่อ SP ×10   *ใช้ไม่ได้ = พลัง 0 และไม่มี effect ที่โค้ดรองรับ (กดใช้ในเกมไม่ได้)")


if __name__ == "__main__":
	main()
