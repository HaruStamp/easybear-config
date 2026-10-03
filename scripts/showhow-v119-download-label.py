#!/usr/bin/env python3
"""showhow-v119 (พี่หมีสั่ง 2026-10-03) — ป้ายปุ่มคลังคลิป "ดาวน์โหลดทั้งหมด (ZIP)" → "ดาวน์โหลดทั้งหมด"
engine v1.17.0: ปุ่ม zip-export เปิดหน้าต่างรายการ .mp4 ทีละคลิปแทน ZIP (Flow ไม่รับ .zip แล้ว) ⇒ คำว่า ZIP ผิดความจริง
ใช้: python3 scripts/showhow-v119-download-label.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
n = 0
def walk(x):
    global n
    if isinstance(x, dict):
        for k, v in x.items():
            if v == 'ดาวน์โหลดทั้งหมด (ZIP)': x[k] = 'ดาวน์โหลดทั้งหมด'; n += 1
            else: walk(v)
    elif isinstance(x, list):
        for v in x: walk(v)
walk(c)
assert n == 1, n
assert 'ZIP)' not in json.dumps(c, ensure_ascii=False)
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v119: แก้ป้าย', n, 'จุด')
