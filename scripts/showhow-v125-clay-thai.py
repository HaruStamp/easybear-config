#!/usr/bin/env python3
"""showhow-v125 — สไตล์ดินน้ำมัน/ไทยท้องถิ่นไม่ออก (ทดสอบ 8 สไตล์จริง 2026-10-13 · docs/qa/2026-10-13-styles-v124)
ดินน้ำมัน: บอร์ดออกมาเป็นภาพถ่ายจริงทั้งใบ — คำ "ดินน้ำมันสต็อปโมชัน" อ่อน ⇒ ใส่ claymation + "ทุกอย่างปั้นจากดิน"
ไทยท้องถิ่น: สมจริงแต่บ้านไม่ไทย ⇒ ระบุของไทยที่เห็นได้ (ไม้ ผ้าลายไทย พัดลม)
ยังเป็นท่า "แทนที่" — ยาว ≤ ประโยคสมจริงเดิม (บอร์ด 86 · วิดีโอ 50)
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8')); L = c['lookups']
B_MAX, V_MAX = len(L['styleBoard']['real']), len(L['styleVideoEN']['real'])
L['styleBoard']['clay'] = 'claymation ทุกอย่างปั้นจากดินน้ำมัน ทั้งคน สัตว์ ห้อง มีรอยนิ้ว ห้ามเป็นภาพถ่ายจริง'
L['styleBoard']['thai'] = 'ภาพถ่ายจริง บ้านไทย: ไม้ ผ้าลายไทย พัดลม ของใช้แบบไทย ห้ามเป็นภาพวาดหรือการ์ตูน'
L['styleVideoEN']['clay'] = 'all-clay claymation stop-motion, fingerprint marks'
L['styleVideoEN']['thai'] = 'realistic Thai home look, local Thai decor, fans'
L['stylePlan']['clay'] = 'งานปั้นดินน้ำมัน (claymation) ทุกอย่างในฉากเป็นดินปั้น ทั้งคน สัตว์ ของ ห้อง'
L['stylePlan']['thai'] = 'สมจริง บ้านไทยท้องถิ่น เห็นของใช้แบบไทยชัด (ไม้ ผ้าลายไทย พัดลม)'
for k in ('clay', 'thai'):
    assert len(L['styleBoard'][k]) <= B_MAX, (k, len(L['styleBoard'][k]))
    assert len(L['styleVideoEN'][k]) <= V_MAX and L['styleVideoEN'][k].isascii(), k
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v125', {k: (len(L['styleBoard'][k]), len(L['styleVideoEN'][k])) for k in ('clay', 'thai')})
