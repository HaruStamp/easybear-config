#!/usr/bin/env python3
"""showhow-v95b — ไอคอนปุ่ม "กำหนดเอง" ของฉากตอนจบ = ไอคอนเดียวกับของฉาก (พี่หมีสั่ง 2026-09-24)"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


def custom(field):
    g = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == field and n.get('options'))
    return next(o for o in g['options'] if o['value'] == 'custom')


custom('endMode')['icon'] = custom('sceneMode')['icon']
assert custom('endMode')['icon'] == 'add_photo_alternate'
print('ฉากตอนจบ · กำหนดเอง: ไอคอน flag → add_photo_alternate (เหมือนปุ่มฉาก)')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
