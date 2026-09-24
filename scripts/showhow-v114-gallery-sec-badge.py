#!/usr/bin/env python3
"""showhow-v114 — หน้าคลังคลิป: เพิ่มป้าย "n วิ / คลิป" ในการ์ดสรุป ให้เหมือนหน้าผลิต (พี่หมีสั่ง 2026-09-24)
หน้าผลิต = Omni 1.1 Flash · n วิ / คลิป · 9:16 แนวตั้ง · คลังคลิปเดิมมีแค่ 2 ป้าย ⇒ ก๊อปป้ายเวลาจากหน้าผลิตทุกไบต์ วางตรงกลาง
ใช้: python3 scripts/showhow-v114-gallery-sec-badge.py
"""
import copy, json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
prod_row = c['phases'][0]['form'][3]['card'][0]['card'][4]['card'][0]['card'][4]['card'][9]
badge = prod_row['card'][1]
assert badge.get('icon') == 'timer' and ' วิ / คลิป' in J(badge['value'])
gal_row = c['phases'][0]['form'][4]['card'][0]['card'][1]['card'][0]['card'][1]['card'][2]
assert [x.get('value') for x in gal_row['card']] == ['Omni 1.1 Flash', '9:16 แนวตั้ง']
gal_row['card'].insert(1, copy.deepcopy(badge))
assert [x.get('icon') for x in gal_row['card']][1] == 'timer' and J(gal_row['card'][1]) == J(badge)
print('คลังคลิป: Omni 1.1 Flash · n วิ / คลิป · 9:16 แนวตั้ง (ป้ายเวลาเหมือนหน้าผลิตทุกไบต์)')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
