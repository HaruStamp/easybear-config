#!/usr/bin/env python3
"""showhow-v106 — modal โหลด/เซฟ การ์ด "รายการงาน": "สินค้า N รายการ" → "งาน N รายการ" (พี่หมีสั่ง 2026-09-24)
ของ minimal ติดมา — collection products ของเราคือ "งาน" ไม่ใช่สินค้า
ใช้: python3 scripts/showhow-v106-save-label.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['saveContent']['collLabels']
assert L['products'] == 'สินค้า {n} รายการ', L['products']
L['products'] = 'งาน {n} รายการ'
print('collLabels.products →', L['products'])
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
