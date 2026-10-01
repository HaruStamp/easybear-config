#!/usr/bin/env python3
"""showhow-v117 — หน้าตั้งค่า §2 สไตล์คลิป: ลบหัวข้อ "ผู้แสดงเห็นแค่ไหน" ที่ค้าง (พี่หมีทัก 2026-10-01)

ตัวเลือกย้ายไปหน้างานตั้งแต่ v82 (item.people) — เหลือแค่หัวข้อ+คำอธิบาย กดอะไรไม่ได้
ลบ 2 กล่อง: กล่องหัวข้อค้าง (icon emoji_people) + กล่องว่าง (card: []) ที่เหลือจากรอบเดียวกัน
ใช้: python3 scripts/showhow-v117-setup-drop-people-heading.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
box = c['phases'][0]['form'][0]['card'][0]['card'][2]['card']
s = json.dumps(box, ensure_ascii=False)
assert 'แสงและบรรยากาศ' in s and 'ข้อความบนคลิป' in s, 'หาส่วน §2 ไม่เจอ — โครงเปลี่ยน'
keep, drop = [], 0
for b in box:
    t = json.dumps(b, ensure_ascii=False)
    stale = 'emoji_people' in t and 'ผู้แสดงเห็นแค่ไหน' in t and '"field"' not in t
    empty = b.get('el') == 'box' and b.get('card') == []
    if stale or empty: drop += 1; continue
    keep.append(b)
assert drop == 2, f'คาดว่าลบ 2 กล่อง ได้ {drop}'
box[:] = keep
assert 'ผู้แสดงเห็นแค่ไหน' not in json.dumps(c['phases'][0]['form'][0], ensure_ascii=False)  # หน้างาน (form[2]) ยังมีของจริง
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v117: ลบ', drop, 'กล่อง')
