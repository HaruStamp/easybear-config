#!/usr/bin/env python3
"""showhow-v96b — คำในส่วนรูปของกล่องกำหนดเอง (พี่หมีสั่ง 2026-09-24)
· ย้าย "ไม่บังคับ" จากคำอธิบาย ไปไว้ท้ายป้าย
· "รูปสถานที่ (1-2 รูป)" → "หรือใส่รูปฉาก 1-2 รูป (ไม่บังคับ)" · "หรือใส่รูปตัวอย่าง" → "หรือใส่รูปตัวอย่าง (ไม่บังคับ)"
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
MAP = {
    'รูปสถานที่ (1-2 รูป)': 'หรือใส่รูปฉาก 1-2 รูป (ไม่บังคับ)',
    'หรือใส่รูปตัวอย่าง': 'หรือใส่รูปตัวอย่าง (ไม่บังคับ)',
    'ไม่บังคับ · ใช้เป็นฉากเริ่ม และห้องจะไม่เปลี่ยนระหว่างคลิป': 'ใช้เป็นฉากเริ่ม และห้องจะไม่เปลี่ยนระหว่างคลิป',
    'ไม่บังคับ · ใช้รูปจากที่อื่นได้ ห้องยังเป็นห้องของงานนี้': 'ใช้รูปจากที่อื่นได้ ห้องยังเป็นห้องของงานนี้',
}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


hit = {k: 0 for k in MAP}
for n in walk(c['phases']):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str) and n['value'] in MAP:
        hit[n['value']] += 1; n['value'] = MAP[n['value']]
assert all(v == 1 for v in hit.values()), hit
print('\n'.join(f'  {a}  →  {b}' for a, b in MAP.items()))
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
