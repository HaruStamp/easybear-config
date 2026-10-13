#!/usr/bin/env python3
"""showhow-v130 — หัวเรื่องขึ้นซ้ำ 2 บรรทัด (บรรทัดที่ 2 สะกดเพี้ยน) ในคลิปจริง 20 วิ ตั้งค่าเริ่มต้น (2026-10-13)

ราก: v123 ย่อคำห้ามของ ON-SCREEN TEXT จาก "no second line or invented words" (v120) เหลือ "no second line"
  บอร์ดพิมพ์หัวเรื่องบรรทัดเดียวถูก แต่วิดีโอแต่งบรรทัดที่ 2 ขึ้นเอง = คำห้ามเฉพาะอาการหลวม (บทเรียน v124/v129)
แก้: คืน "or invented words" + "shown once" ในประโยคข้อความทั้ง 2 แบบของทุก mnVideo*
ใช้: python3 scripts/showhow-v130-title-once.py  (รันบน v129)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
REP = [('each on one line only — no second line,', 'each shown once on one line only — no second line or invented words,'),
       ('one fixed Thai title, one line only — no second line,', 'one fixed Thai title, shown once, one line only — no second line or invented words,')]
hits = [0, 0]
def fix(s):
    for i, (a, b) in enumerate(REP):
        if a in s: s = s.replace(a, b); hits[i] += 1
    return s
def walk(x):
    it = x.items() if isinstance(x, dict) else enumerate(x) if isinstance(x, list) else []
    for k, v in list(it):
        if isinstance(v, str): x[k] = fix(v)
        else: walk(v)
for o in c['ops']:
    if o['id'].startswith('mnVideo'): walk(o['prompt'])
print('hits', hits)
assert hits[0] >= 6 and hits[1] >= 1, hits
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v130')
