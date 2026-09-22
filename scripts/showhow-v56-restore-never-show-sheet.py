#!/usr/bin/env python3
# showhow v56 — คืนคำว่า "ห้ามโชว์แผ่นบอร์ดบนจอ" ที่หายไปตอน v44/v45
#
# อาการจริง (2026-09-22 · เคส 2 คลิปต่องาน · คลิปที่ 2 ยาว 10 วิ):
#   วินาทีที่ 0-2 ของวิดีโอ = **แผ่นสตอรีบอร์ดเต็มจอ** (ตาราง 5 ช่อง + วงกลมเลข ①-⑤ + หัวเรื่องทับ)
#   แล้วค่อยตัดเข้าฉากจริงที่ ~2.4 วิ
#
# ราก = การถอยหลังที่เราทำเอง:
#   v26 (2026-09-21) เขียนว่า  "Never copy a sheet or show one on screen."   ← มี 2 ข้อห้าม
#   v44/v45 เขียนประโยคนี้ใหม่เพื่อกันวงกลมเลข เหลือ "Never copy a sheet; its markings are annotation."
#   ⇒ **ข้อห้าม "ห้ามโชว์บนจอ" หายไปเงียบ ๆ** ทั้งที่ v26 เพิ่มมาเพราะทีม minimal เจออาการนี้มาก่อน
#
# แก้: รวมทั้ง 3 ความหมายในประโยคเดียวให้สั้นที่สุด — ห้ามลอก · ห้ามโชว์ · เครื่องหมายบนแผ่นคือคำอธิบาย
#      ยาวกว่าเดิมแค่ 8 ตัวอักษร (headroom วิดีโอ p95 เหลือ 17 ⇒ ยังผ่าน)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
raw = open(P, encoding='utf-8').read()
c = json.loads(raw)

OLD = 'Never copy a sheet; its markings are annotation.'
NEW = 'Never copy or show a sheet; its markings are annotation.'
ops = json.dumps(c['ops'], ensure_ascii=False)
n = ops.count(OLD)
assert n > 0, 'ไม่เจอประโยคของ v45 (โครงเปลี่ยน — หยุด)'
assert NEW not in ops, 'รันซ้ำ'
print('เจอ', n, 'จุด')
c['ops'] = json.loads(ops.replace(OLD, NEW))

before = json.loads(raw)
for k in before:
    if k != 'ops':
        assert json.dumps(before[k], ensure_ascii=False) == json.dumps(c[k], ensure_ascii=False), f'v56 แตะ {k} โดยไม่ตั้งใจ'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v56 ok · +{len(NEW)-len(OLD)} ตัวอักษรต่อ prompt ที่มีประโยคนี้')
