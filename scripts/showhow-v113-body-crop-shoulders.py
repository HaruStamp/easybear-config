#!/usr/bin/env python3
"""showhow-v113 — เห็นตัวไม่เห็นหน้า: ครอปที่ไหล่ แทนที่คอ (รอบซ้ำ R2 คืน 2026-09-24: ไม่มีหน้าเต็มแล้ว แต่คาง/ปากโผล่ ~4/20 เฟรม)
แก้วลีครอปทุกชั้น: บท (neck-down framing → shoulders-down framing) · บอร์ด (คอลงมา ครอปใต้คาง → ไหล่ลงมา) · วิดีโอ (neck → shoulders)
ใช้: python3 scripts/showhow-v113-body-crop-shoulders.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
L = c['lookups']
n = 0
for t, a, b in (('charPlan', 'neck-down framing:', 'shoulders-down framing:'),
                ('charPlan', 'ตั้งแต่คอลงมา (ครอปใต้คาง)', 'ตั้งแต่ไหล่ลงมา (ครอปที่ไหล่ ไม่เห็นคาง)'),
                ('charBoard', 'ตั้งแต่คอลงมา ครอปใต้คาง', 'ตั้งแต่ไหล่ลงมา ไม่เห็นคาง'),
                ('charVideoEN', 'framed from the neck down', 'framed from the shoulders down, no chin')):
    for k, v in L[t].items():
        if k.startswith('เห็นตัว ไม่เห็นหน้า|') and a in v:
            L[t][k] = v.replace(a, b); n += 1
assert n == 12, n
print('ครอปที่ไหล่', n, 'จุด')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
