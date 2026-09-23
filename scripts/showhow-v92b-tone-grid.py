#!/usr/bin/env python3
"""showhow-v92b — "แสงและบรรยากาศ" หน้าตั้งค่า เป็นการ์ดมีไอคอนแบบหน้างาน + "ตามค่ารวม" → "อัตโนมัติ" (พี่หมี 2026-09-24)

หน้าตั้งค่าใช้ `segmented` (ปุ่มแถบ + จุดสี) · หน้างานใช้ `grid-select` 3 คอลัมน์ มีไอคอน+คำอธิบาย ⇒ หน้าตาไม่เข้ากัน
แก้: หน้าตั้งค่าลอกทรงจากช่อง `tone` ของหน้างานทั้งชิ้น (ไอคอน/คำอธิบายชุดเดียวกัน) · field ยัง `svTone` · value ไม่แตะ
📌 จุดสีตัวอย่างแสงของ segmented เดิมหายไปจากจอ — พี่หมีสั่งเปลี่ยนรูปแบบเอง (กฎเดิม "ห้ามแตะสีตัวอย่าง" = ห้ามเปลี่ยนสีให้เป็น theme · ไม่ได้ห้ามเปลี่ยนรูปแบบ)
หน้างาน: ตัวเลือกแรก "ตามค่ารวม" → "อัตโนมัติ" (ความหมายเดิม: ใช้ค่าจากหน้าตั้งค่า ถ้าไม่ได้ตั้งหมีเลือกให้)
ใช้: python3 scripts/showhow-v92b-tone-grid.py
"""
import copy, json

P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))


def walk(n, parent=None, key=None):
    yield n, parent, key
    if isinstance(n, dict):
        for k, v in n.items(): yield from walk(v, n, k)
    elif isinstance(n, list):
        for i, v in enumerate(n): yield from walk(v, n, i)


job_tone = next(n for n, _, _ in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'tone' and n.get('el') == 'grid-select')
seg = [(n, p, k) for n, p, k in walk(c['phases']) if isinstance(n, dict) and n.get('field') == 'svTone' and n.get('el') == 'segmented']
assert len(seg) == 1, 'หา svTone แบบ segmented ไม่เจอ'
old, parent, key = seg[0]
new = copy.deepcopy(job_tone)
new['field'] = 'svTone'
assert [o['value'] for o in new['options']] == [o['value'] for o in old['options']], 'ตัวเลือก 2 หน้าไม่ตรงกัน — หยุดก่อน'
new['options'][0].update({'label': 'อัตโนมัติ', 'desc': 'หมีเลือกให้เข้ากับงาน', 'icon': 'auto_awesome'})
parent[key] = new
print('① หน้าตั้งค่า: แสงและบรรยากาศ segmented → การ์ดไอคอน 3 คอลัมน์ (ทรงเดียวกับหน้างาน)')

o0 = job_tone['options'][0]
assert o0['value'] == '' and o0['label'] == 'ตามค่ารวม'
o0.update({'label': 'อัตโนมัติ', 'desc': 'ตามหน้าตั้งค่า / หมีเลือกให้', 'icon': 'auto_awesome'})
n_hint = 0
for n, _, _ in walk(c['phases']):
    if isinstance(n, dict) and n.get('el') == 'text' and isinstance(n.get('value'), str) and 'ตามค่ารวม' in n['value']:
        n['value'] = n['value'].replace('"ตามค่ารวม"', '"อัตโนมัติ"'); n_hint += 1
assert n_hint == 1
print('② หน้างาน: "ตามค่ารวม" → "อัตโนมัติ" (ตัวเลือก + คำแนะนำใต้ช่อง)')

s = json.dumps(c['phases'], ensure_ascii=False)
assert 'ตามค่ารวม' not in s and '"el": "segmented", "field": "svTone"' not in s
for w in ('sm:', 'md:', 'min-['):
    assert w not in json.dumps(new, ensure_ascii=False)
print('✅ ยามผ่าน: ไม่เหลือ "ตามค่ารวม" · svTone เป็น grid-select · value ครบเท่าเดิม')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
