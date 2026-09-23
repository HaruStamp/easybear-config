#!/usr/bin/env python3
"""showhow-v112 — สไตล์ "บางมินิมอล" อ่านไม่ออกบนพื้นสว่าง (ผลิตจริงคืน 2026-09-24 เคส S5: ตัวบางสีขาวเกือบหายหน้าหน้าต่าง)
"very soft shadow" อ่อนเกิน → เงาเข้มนุ่มเพื่อคอนทราสต์ · ยาวไม่เกินสไตล์ที่ยาวสุด (ตัววัดใช้ค่ายาวสุดอยู่แล้ว)
🔴 value ของ svText ต้องอังกฤษล้วน (v21) · แก้ทั้งตัวเลือกและค่าตั้งต้นถ้าตรงกัน
ใช้: python3 scripts/showhow-v112-thin-style-contrast.py
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


g = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'svText' and n.get('options'))
o = next(o for o in g['options'] if o['label'] == 'บางมินิมอล')
old = o['value']
new = old.replace('very soft shadow', 'clear dark shadow')
assert new != old and new.isascii()
longest = max(len(x['value']) for x in g['options'] if x is not o)
assert len(new) <= longest, (len(new), longest)
o['value'] = new
n = 0
for x in walk(c):
    if isinstance(x, dict) and x.get('svText') == old: x['svText'] = new; n += 1
print(f'บางมินิมอล: {len(old)} → {len(new)} ตัวอักษร (ยาวสุดของชุด {longest}) · ค่าอ้างอิงอื่นที่แก้ตาม {n}')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
