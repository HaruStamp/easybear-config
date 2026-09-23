#!/usr/bin/env python3
"""showhow-v107 — ถอดไอคอนตกใจสีเหลืองหลังชื่องานในหน้าจัดการงาน (พี่หมีสั่ง 2026-09-24)
ของ minimal ติดมา: เตือน "ยังไม่มีรูปสินค้า" (when item.slots.image=) — แอปนี้รูปไม่บังคับ
(กฎ "ห้ามกลับไปบังคับรูปสินค้า" · การ์ดเตือนยังไม่มีรูปถูกถอดไปแล้วตั้งแต่ v2.1) ⇒ ไอคอนนี้คือเศษที่เหลือ
และโผล่แม้งานแบบ "ไม่มีสินค้า" ซึ่งไม่มีทางมีรูปสินค้าได้เลย
ใช้: python3 scripts/showhow-v107-no-image-warning.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
row = c['phases'][0]['form'][1]['card'][2]['card'][2]['card'][1]['card'][0]['card'][4]['card'][0]
assert row['card'][0].get('value') == '{item.name}'
ic = row['card'][1]
assert ic.get('el') == 'icon' and ic.get('icon') == 'warning' and ic.get('when') == 'item.slots.image='
row['card'].pop(1)
assert len(row['card']) == 1
print('ถอดไอคอนเตือนไม่มีรูปหลังชื่องานแล้ว')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
