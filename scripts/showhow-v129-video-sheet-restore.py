#!/usr/bin/env python3
"""showhow-v129 — เลขช่องบอร์ด (วงกลม "11") หลุดเข้าวิดีโอช่วง 3 (ผลิตจริง 30 วิ บน v128 · 2026-10-13)

ราก: v123 ย่อประโยคกันแผ่นบอร์ดของวิดีโอจาก
  "Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene."
  เหลือ "Never show sheets, panels or numbers" — คำห้ามเฉพาะอาการ ("number marks" + NEVER) หลวมลง
  (บทเรียนเดียวกับ v124 "no second line": ห้ามย่อคำห้ามเฉพาะอาการ)
แก้: คืนประโยค sheet ของ v122 ทั้งประโยคทุก mnVideo* (ทางไม่ใช่ไทม์แลปส์) + Negative เติม "no numbered circles or panel borders"
ใช้: python3 scripts/showhow-v129-video-sheet-restore.py  (รันบน v128)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
NEW = ("\n\nThe attached sheet (image 1) is a silent guide to this part's 5 scenes; other images = same room. Copy its room, framing and light. "
       "Never show sheets, panels or numbers — the first frame already shows the scene itself.")
OLD = ("\n\nAttached sheets are a silent guide: image 1 = this part's 5 scenes — copy its room, fixtures, surfaces, framing, lighting; "
       "others = same room, same light. Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene.")
NEG_A = 'Negative: no storyboard sheet, no tripod'
NEG_B = 'Negative: no storyboard sheet, no numbered circles or panel borders, no tripod'
n1 = n2 = 0
def walk(x):
    global n1, n2
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, str):
                if v == NEW: x[k] = OLD; n1 += 1
                elif NEG_A in v and NEG_B not in v: x[k] = v.replace(NEG_A, NEG_B); n2 += 1
            else: walk(v)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v, str):
                if v == NEW: x[i] = OLD; n1 += 1
                elif NEG_A in v and NEG_B not in v: x[i] = v.replace(NEG_A, NEG_B); n2 += 1
            else: walk(v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk(o['prompt'])
assert n1 == 6 and n2 == 6, (n1, n2)
print(f'✅ v129: คืนประโยค sheet {n1} op · Negative เลขวงกลม {n2} op')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
