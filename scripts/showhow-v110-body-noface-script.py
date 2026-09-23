#!/usr/bin/env python3
"""showhow-v110 — โหมด "เห็นตัว ไม่เห็นหน้า" หน้าหลุดในวิดีโอ (ผลิตจริงคืน 2026-09-24 เคส B2 · 20 วิ)

กฎในวิดีโอมีครบ (charVideoEN "framed from the neck down … never the face") แต่บทเขียน s7en =
"Medium shot, woman places the Monstera…" และ look = "Thai woman…" ⇒ โมเดลวิดีโอตามบท ไม่ตามกฎ → หน้าผู้หญิงเต็มหน้า 2 วิ
แก้ที่กฎบท (charPlan · mnPlan ไม่โดนตัด): s*en ทุกฉากที่มีคน ขึ้นต้นด้วย "neck-down framing:" · ห้ามคำ medium shot / full body /
wide shot ของคน · เรียกคนว่า "the worker's hands/body" ไม่ใช่ woman/man · look ห้ามมีรายละเอียดหน้า/ผม
ใช้: python3 scripts/showhow-v110-body-noface-script.py
"""
import json
P = 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
NEW = ('กฎคนในคลิป: เห็นตัวผู้ลงมือตั้งแต่คอลงมา (ครอปใต้คาง) ห้ามเห็นหน้าเด็ดขาด — ลำตัว แขน มือกำลังทำงานจริง ชุดเดิมทุกฉาก · ห้ามมองกล้อง ห้ามโพสท่า'
       ' · s*en ทุกฉากที่มีคนต้องขึ้นต้นด้วย "neck-down framing:" และเรียกคนว่า the worker\'s body/hands ห้ามเขียน woman/man'
       ' · ห้ามช็อต medium shot, full body, wide shot ที่เห็นคนทั้งตัว (ภาพกว้างให้เห็นแค่พื้นที่ ไม่มีคน)'
       ' · look บอกแค่ชุด/สีเสื้อ ห้ามบอกหน้า ผม อายุ')
n = 0
for k in list(c['lookups']['charPlan']):
    if k.startswith('เห็นตัว ไม่เห็นหน้า|'):
        c['lookups']['charPlan'][k] = NEW; n += 1
assert n == 3, n
print('charPlan เห็นตัวไม่เห็นหน้า ×3 ใหม่', len(NEW), 'ตัวอักษร · mnPlan ไม่โดนตัด')
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
