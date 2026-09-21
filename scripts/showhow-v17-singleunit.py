#!/usr/bin/env python3
# showhow-v17-singleunit.py — "รูปสินค้าอาจเป็นภาพโฆษณา ให้เล่าเป็นสินค้า 1 ชิ้นเสมอ" (พี่หมีเจอ 2026-09-21)
# ราก: รูปสินค้าจริงของลูกค้ามักเป็นภาพโฆษณา (แพ็กคู่ · ป้ายโปรโมชันทับ · พลาสติกหุ้ม)
#      mnPlan เห็นรูปแล้ว **เขียนบทตามที่เห็น** → "มือหยิบขวดน้ำยา Duck Pro แพ็คคู่" / "มือแกะพลาสติกหุ้มแพ็คคู่ออก"
#      ⇒ บอร์ดวาดแพ็กคู่ + ป้ายเหลืองตามบทอย่างถูกต้อง · ไล่แก้ที่ prompt บอร์ด 2 รอบไม่หาย เพราะต้นทางสั่งมาแบบนั้น
# แก้ที่ต้นทาง: กฎในบท (brain.mn.sys) + ย้ำใน imgNote ที่อธิบายลำดับรูป
# ลำดับรัน: base → v9-board-collage → v10-endshot → v11-board-order → v13-textstyle → ไฟล์นี้
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'showhow-dev.json')
raw = open(P, encoding='utf-8').read(); d = json.loads(raw)

OLD = '- สินค้าที่ผู้ใช้แนบรูปมาต้องตรงตามรูปจริง 100% ห้ามเปลี่ยนรูปทรง สี ฉลาก ดีไซน์'
NEW = ('- สินค้าที่ผู้ใช้แนบรูปมาต้องตรงตามรูปจริง 100% ห้ามเปลี่ยนรูปทรง สี ฉลาก ดีไซน์'
       ' · **รูปที่แนบมักเป็นภาพโฆษณา (แพ็กคู่ แพ็กมัดรวม ป้ายโปรโมชันทับ พลาสติกหุ้ม กล่อง) — ให้เล่าเป็นสินค้า 1 ชิ้นเสมอ'
       ' ห้ามเขียนฉากแกะแพ็ก แกะพลาสติก เปิดกล่อง หรือโชว์ป้ายโปรโมชัน/ราคา และห้ามเขียนคำว่าแพ็กคู่หรือจำนวนขวดลงในบท**')
assert OLD in d['brain']['mn']['sys']
d['brain']['mn']['sys'] = d['brain']['mn']['sys'].replace(OLD, NEW)

note = d['brain']['mn'].get('imgNote', '')
ADD = ' · รูปสินค้าเป็นภาพโฆษณาได้ ให้ดูเฉพาะตัวสินค้า มองข้ามป้ายโปรโมชัน พลาสติกหุ้ม และจำนวนชิ้นในรูป'
if ADD not in note: d['brain']['mn']['imgNote'] = note + ADD

open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1) + ('\n' if raw.endswith('\n') else ''))
print('✓ v17 singleunit · แก้ brain.mn.sys + imgNote ·', os.path.getsize(P), 'bytes')
