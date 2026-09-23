#!/usr/bin/env python3
"""showhow-v105 — 🐛 ตัวเลือก "สุ่มตัวละคร / ใช้รูปตัวละคร" โผล่ทุกโหมดผู้แสดง (บั๊กจาก v100)

v100 ย้ายตัวเลือกแหล่งหน้า (`peopleSrc`) ออกจากกล่องที่มีเงื่อนไข people=คนเดียวเต็มตัว มาไว้นอกกล่อง
แต่ไม่ได้ติดเงื่อนไขตามมา ⇒ ป้าย "ตัวละคร" กับกล่องรายละเอียดซ่อนถูก แต่ตัวเลือกโผล่ตลอด
ตั้งใจ: ทั้งชุด (ป้าย · ตัวเลือก · กล่อง) โชว์เฉพาะ "เห็นเต็มตัว" — โหมดอื่นไม่เห็นหน้า ตัวละคร/รูปหน้าไม่มีผล
ใช้: python3 scripts/showhow-v105-char-toggle-gate.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
FULL = {'op': 'eq', 'a': '{item.people}', 'b': 'คนเดียวเต็มตัว'}
col = next(x for x in c['phases'][0]['form'][2]['card'][0]['card'][0]['card'] if '"field": "peopleSrc"' in J(x))
col = next(x for x in col['card'] if '"field": "peopleSrc"' in J(x))
i = next(k for k, x in enumerate(col['card']) if x.get('field') == 'peopleSrc')
lab, grid, box = col['card'][i - 1], col['card'][i], col['card'][i + 1]
assert lab.get('value') == 'ตัวละคร' and lab['when'] == FULL and box['when'] == FULL and 'when' not in grid
grid['when'] = FULL
print('ตัวเลือกสุ่ม/ใช้รูปตัวละคร โชว์เฉพาะ "เห็นเต็มตัว" (เหมือนป้ายและกล่อง)')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
