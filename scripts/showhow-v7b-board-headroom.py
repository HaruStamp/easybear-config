#!/usr/bin/env python3
# showhow-v7b-board-headroom.py — ต่อจาก v7: headroom บอร์ดหลังแก้ = 243 (ต่ำกว่าเป้า 250 · สูงสุด 3,657 person-full-desk-20 · พากย์ · รูปหน้า)
# บีบคำอีก ~30 ตัว (ความหมายเท่าเดิม) ในทุก mnBoard*
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read()
REPL = [
    ('ห้ามวาดใหม่ ตีความใหม่ ทำเป็นการ์ตูน หรือเพิ่มลดรายละเอียด', 'ห้ามวาดใหม่ ทำเป็นการ์ตูน หรือเพิ่มลดรายละเอียด', 6),
    ('(สะอาดขึ้น เป็นระเบียบขึ้น ติดตั้งเสร็จ) · ช่องแรก = สภาพตามรูป', '(สะอาด เป็นระเบียบ ติดตั้งเสร็จ) · ช่องแรก = สภาพตามรูป', 6),
    ('\\n\\nปิดท้ายทุกภาพด้วย: ', '\\n\\nท้ายทุกภาพ: ', 6),
]
for a, b, n in REPL:
    c = raw.count(a); assert c == n, (a, c, n); raw = raw.replace(a, b)
json.loads(raw)
open(P, 'w', encoding='utf-8').write(raw); print('✓ v7b', os.path.getsize(P), 'bytes')
