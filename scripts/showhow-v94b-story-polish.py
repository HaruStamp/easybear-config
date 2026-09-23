#!/usr/bin/env python3
"""showhow-v94b — เก็บ 2 จุดที่ยังไม่เข้าชุด (เห็นจาก UI Lab 390px หลัง v94)
① ป้าย "หรือใส่รูปตัวอย่าง" หนาเข้ม 15px — ป้ายนำอื่นในกล่องรายละเอียดเป็นสไตล์ SUB ⇒ ใช้ SUB
② "อยากให้มีอะไรพิเศษหลังงานเสร็จ" ใต้ "ลูกเล่นตอนท้าย" ใหญ่/เข้มกว่าหัวข้อตัวเอง ⇒ เป็นคำอธิบายเล็ก
ใช้: python3 scripts/showhow-v94b-story-polish.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
SUB = '!text-[13px] @[640px]:!text-[12.5px] font-bold opacity-70 px-0.5'
HINT = '!text-[13px] @[640px]:!text-[12.5px] opacity-50 px-0.5 -mt-1'


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


job = c['phases'][0]['form'][2]['card'][0]['card'][0]
hit = 0
for n in walk(job):
    if isinstance(n, dict) and n.get('el') == 'text':
        if n.get('value') == 'หรือใส่รูปตัวอย่าง': n['className'] = SUB; hit += 1
        elif n.get('value') == 'อยากให้มีอะไรพิเศษหลังงานเสร็จ': n['className'] = HINT; hit += 10
assert hit == 11, hit
print('① ป้ายรูปตัวอย่าง = สไตล์ป้ายนำ · ② คำอธิบายลูกเล่นตอนท้าย = ตัวเล็ก')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
