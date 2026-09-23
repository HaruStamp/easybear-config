#!/usr/bin/env python3
"""showhow-v103 — กล่องฉากตอนจบ "กำหนดเอง" = ช่องพิมพ์ + ช่องรูป มาด้วยกันเสมอ (พี่หมีสั่ง 2026-09-24)

เดิม (v102): ช่องพิมพ์ซ่อนเฉพาะทัวร์ แต่ช่องรูปซ่อนทั้งทัวร์และอัตโนมัติ ⇒ เรื่องอัตโนมัติ + กำหนดเอง เห็นแค่ช่องพิมพ์ (งง)
ใหม่: ภาพจบใช้เงื่อนไขเดียวกับช่องพิมพ์ทุกจุด — ซ่อน/ไม่ใช้เฉพาะเรื่องแบบทัวร์
   จุดที่แก้ = ทุกเงื่อนไข not(arc='' or arc=ทัวร์) ที่เหลืออยู่ (ล้วนเป็นของภาพจบ):
   ช่องรูปบนหน้างาน · บทเห็นรูป (mnPlan images + คำอธิบาย) · บอร์ดช่วงสุดท้าย (prompt + refs) ทุกความยาว
ใช้: python3 scripts/showhow-v103-end-photo-together.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
J = lambda x: json.dumps(x, ensure_ascii=False)
ARC = lambda v: {'op': 'eq', 'a': '{item.arc}', 'b': v}
OLD = J({'op': 'not', 'a': {'op': 'or', 'list': [ARC(''), ARC('ทัวร์จุดเด่น')]}})
NEW = J({'op': 'not', 'a': ARC('ทัวร์จุดเด่น')})
s = J(c)
n = s.count(OLD)
# ทุกจุดที่เหลือต้องเป็นของภาพจบ — เช็คก่อนแทน
for o in c['ops'] + [c['phases']]:
    t = J(o)
    if OLD in t:
        assert 'endRef' in t, (o.get('id') if isinstance(o, dict) else 'phases')
print(f'แทนเงื่อนไขภาพจบ {n} จุด')
c = json.loads(s.replace(OLD, NEW))
assert J(c).count(OLD) == 0 and n >= 20
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ ภาพจบซ่อนเฉพาะทัวร์ ทุกจุดเงื่อนไขเดียวกับช่องพิมพ์')
