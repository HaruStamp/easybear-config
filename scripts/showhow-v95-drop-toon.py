#!/usr/bin/env python3
"""showhow-v95 — ตัดตัวเลือก "สัตว์การ์ตูน" ออกจาก "ผู้แสดงเป็นอะไร" (พี่หมีสั่ง 2026-09-24)

เหลือ 4 ตัว: อัตโนมัติ · คน · สัตว์จริง · สัตว์ทำตัวเหมือนคน (= กริด 2×2 พอดี)
🔑 งานที่เคยเลือก animalToon ไว้ (งานทดสอบ) — ปุ่มหายแต่ค่ายังอยู่ ⇒ ถ้าไม่จัดการ ระบบจะแอบวาดการ์ตูนต่อ
   ⇒ ให้ animalToon ทำงานแบบอัตโนมัติ: lookup ทุกตาราง = '' · เงื่อนไข "ไม่ใช่สัตว์" ทุก op นับ animalToon ด้วย (36 จุด)
ใช้: python3 scripts/showhow-v95-drop-toon.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


cast = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'castKind' and n.get('options'))
before = [o['value'] for o in cast['options']]
cast['options'] = [o for o in cast['options'] if o['value'] != 'animalToon']
assert [o['value'] for o in cast['options']] == ['', 'human', 'animalReal', 'animalAnthro'], before
for t in ('castPlan', 'castBoard', 'castVideoEN', 'castOverrideTH', 'castNegEN'):
    c['lookups'][t]['animalToon'] = ''
n = 0
for x in walk(c['ops']):
    if isinstance(x, dict) and x.get('op') == 'or' and isinstance(x.get('list'), list) \
            and {'op': 'eq', 'a': '{item.castKind}', 'b': 'human'} in x['list']:
        x['list'].append({'op': 'eq', 'a': '{item.castKind}', 'b': 'animalToon'}); n += 1
assert n == 36, n
print(f'ตัด "สัตว์การ์ตูน" · เหลือ 4 ตัวเลือก · งานเก่าที่เลือกไว้ = อัตโนมัติ (lookup ว่าง 5 ตาราง · เงื่อนไข {n} จุด)')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
