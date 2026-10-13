#!/usr/bin/env python3
"""showhow-v127 — ผลวาดจริง v126 10 ใบ (docs/qa/2026-10-13-styles-v126)
1) คำเสียงประกอบ (ครืน · ปึก · ตึ๊บ · thud) พิมพ์ลงบอร์ด — v123 ย่อ "ห้ามมีเส้นเอฟเฟกต์หรือคำเอฟเฟกต์" เป็น "ห้ามมีเส้นหรือคำเอฟเฟกต์" ความหมายหลวม
   ⇒ เขียนตรง ๆ ว่าห้ามเขียนคำเสียงประกอบ (ไม่ใส่ตัวอย่างคำ — บทเรียน v8.4 ตัวอย่างถูกวาดลงภาพ)
2) กล่องใสกลายเป็นทึบ 2/10 — เติมคำ "ความใส" ในบรรทัดสินค้า (บอร์ด) และ transparency ใน PRODUCT LOCK (วิดีโอ) — เติม ไม่ยุบ
3) ดินน้ำมันยังเหมือนการ์ตูน 3D — ขึ้นต้นด้วย claymation + ปั้นจากดินทั้งหมด + ผิวด้าน
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8')); L = c['lookups']
S = json.dumps(c, ensure_ascii=False)
REP = [('ห้ามมีเส้นหรือคำเอฟเฟกต์', 'ห้ามมีเส้นเอฟเฟกต์ ห้ามเขียนคำเสียงประกอบ'),
       ('ห้ามเปลี่ยนสี ทรง สัดส่วน ฉลาก โลโก้', 'ห้ามเปลี่ยนสี ความใส ทรง สัดส่วน ฉลาก โลโก้'),
       ('never change colour, shape, size, material', 'never change colour, transparency, shape, size, material')]
for a, b in REP:
    assert S.count(a) == 6, (a, S.count(a)); S = S.replace(a, b)
c = json.loads(S); L = c['lookups']
L['styleBoard']['clay'] = 'ภาพ claymation: คน สัตว์ ของ ห้อง ปั้นจากดินน้ำมันทั้งหมด ผิวด้าน ห้ามเป็นภาพถ่าย'
assert len(L['styleBoard']['clay']) <= len(L['styleBoard']['real']), len(L['styleBoard']['clay'])
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ v127 · clay', len(L['styleBoard']['clay']))
