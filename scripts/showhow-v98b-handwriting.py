#!/usr/bin/env python3
"""showhow-v98b — สไตล์ตัวอักษร "แถบดำโปร่ง" → "ลายมือน่ารัก" (พี่หมีสั่ง 2026-09-24 · แนวเดียวกับของแอปมินิมอล)

ของมินิมอล: "ตัวอักษรลายมือภาษาไทยเส้นโค้งนุ่มหัวกลม (cute Thai handwritten script) สีขาว มีเงานุ่มรองรับ (soft shadow) + doodle ลายเส้นวาดมือเล็กๆ"
ยกมาแค่แนว ไม่ยกถ้อยคำ เพราะ 2 ข้อชนกฎของ showhow:
  ① ค่าต้องอังกฤษล้วน (ยาม G6 · v21: ค่าไทยถูกพิมพ์ลงจอเป็นบรรทัดบนของหัวเรื่อง)
  ② ห้ามคำ doodle (ข้อเสนอตั้งแต่ 2026-09-17 — โมเดลวาดลายเส้นเพิ่มลงคลิป)
และต้องไม่ยาวกว่าสไตล์ที่ยาวสุด 77 ตัวอักษร (บอร์ดเหลือที่ว่าง 13 เมื่อวัดด้วยสไตล์ยาวสุด)
ใช้: python3 scripts/showhow-v98b-handwriting.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
NEW = {'value': 'cute rounded Thai handwritten letters, soft curvy strokes, white, soft shadow',
       'label': 'ลายมือน่ารัก', 'desc': 'อบอุ่น เป็นกันเอง'}


def walk(n):
    yield n
    if isinstance(n, dict):
        for v in n.values(): yield from walk(v)
    elif isinstance(n, list):
        for v in n: yield from walk(v)


g = next(n for n in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'svText' and n.get('options'))
old = next(o for o in g['options'] if o['label'] == 'แถบดำโปร่ง')
longest = max(len(o['value']) for o in g['options'] if o is not old)
assert NEW['value'].isascii() and len(NEW['value']) <= longest, (len(NEW['value']), longest)
for bad in ('doodle', '4k', 'tripod', 'line', 'fps', 'frame', 'box', 'icon'):
    assert bad not in NEW['value'].lower(), bad
if c['values'].get('svText') == old['value']:
    c['values']['svText'] = NEW['value']
old.clear(); old.update(NEW)
assert len(g['options']) == 6
print(f'แถบดำโปร่ง → ลายมือน่ารัก · value {len(NEW["value"])} ตัวอักษร (ยาวสุดของที่เหลือ {longest}) · ไม่มี doodle')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
