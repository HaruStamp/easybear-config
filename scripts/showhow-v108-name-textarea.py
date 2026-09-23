#!/usr/bin/env python3
"""showhow-v108 — ช่อง "งานนี้ทำอะไรให้ดู" (field name) input → textarea (พี่หมีสั่ง 2026-09-24)
ขนาดตัวอักษรเท่าเดิม (20/19) · ทรงเดียวกับ textarea ช่องอื่นในหน้างาน · field/placeholder ไม่แตะ
ใช้: python3 scripts/showhow-v108-name-textarea.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
n = c['phases'][0]['form'][2]['card'][0]['card'][0]['card'][2]['card'][1]
assert n['el'] == 'input' and n['field'] == 'name'
n['el'] = 'textarea'
n['className'] = '!p-4 !rounded-xl !text-[20px] @[640px]:!text-[19px] !leading-relaxed !min-h-[136px] @[560px]:!min-h-[104px]'
print('name: input → textarea')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
