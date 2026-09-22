#!/usr/bin/env python3
# showhow v58 — แผ่นบอร์ดยังโผล่เต็มจอ 2 วินาทีแรก "ของคลิปที่ 2" ทั้งที่ v56/v57 แก้ไปแล้ว
#
# หลักฐาน (2 รอบ · คนละงาน · ทั้งคู่เป็น "คลิปที่ 2" ของงานเดียวกัน · 10 วิ ช่วงเดียว):
#   2026-09-22 จัดตู้เย็น  คลิป 2 → วิ 0-2 เป็นตารางบอร์ด 5 ช่อง + วงกลมเลข
#   2026-09-22 จัดชั้นรองเท้า คลิป 2 → อาการเดียวกันเป๊ะ (หลัง v56+v57)
#   🔎 ข้อสังเกต: บอร์ดของคลิปที่ 2 ทั้ง 2 รอบ **วาดช่องมีเส้นคั่นขาว** ส่วนคลิป 1 ช่องชิดกัน
#      ⇒ สมมติฐาน: บอร์ดที่ "ดูเป็นกราฟิกออกแบบ" ยิ่งชวนให้โมเดลวิดีโอลอกทั้งแผ่น
#
# ที่ v56/v57 ยังไม่พอ:
#   - v56 เขียน "Never copy or show a sheet" = ห้ามแบบผ่าน ๆ ท้ายประโยคยาว
#   - v57 ใส่ใน Negative = Negative เป็นบรรทัดท้ายสุด น้ำหนักน้อยกับโมเดลวิดีโอ
#   - **ไม่มีประโยคไหนบอกว่า "เฟรมแรกต้องเป็นฉากจริงแล้ว"** ซึ่งคืออาการที่เกิดจริง (โผล่เฉพาะ 2 วิ แรก)
#
# v58: เขียนบล็อกนี้ใหม่ทั้งก้อน — ยืมสำนวน "silent guide" ของทีม minimal (ของเขาไม่เคยมีอาการนี้)
#      + ระบุ "panels and number marks" ชัด ๆ + **เพิ่มคำสั่งเรื่องเฟรมแรกโดยเฉพาะ**
#      ยาวขึ้นแค่ 4 ตัวอักษร (ตัดคำฟุ่มเฟือย "storyboard"/"other parts of the"/"the plan" มาแลก)
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
raw = open(P, encoding='utf-8').read()
c = json.loads(raw)

OLD = ("Attached storyboard sheets are the plan: image 1 = this part's 5 scenes — copy its room, fixtures, "
       "surfaces, framing and lighting; other sheets = other parts of the same room, same light. "
       "Never copy or show a sheet; its markings are annotation.")
NEW = ("Attached sheets are a silent guide: image 1 = this part's 5 scenes — copy its room, fixtures, "
       "surfaces, framing, lighting; others = same room, same light. "
       "Sheets, panels and number marks must NEVER appear on screen; frame 1 is already a live scene.")

ops = json.dumps(c['ops'], ensure_ascii=False)
n = ops.count(OLD)
assert n == 6, f'คาด 6 จุด เจอ {n}'
assert NEW not in ops, 'รันซ้ำ'
c['ops'] = json.loads(ops.replace(OLD, NEW))

before = json.loads(raw)
for k in before:
    if k != 'ops':
        assert json.dumps(before[k], ensure_ascii=False) == json.dumps(c[k], ensure_ascii=False), f'v58 แตะ {k}'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'v58 ok · 6 จุด · {len(OLD)} → {len(NEW)} ตัวอักษร ({len(NEW)-len(OLD):+d})')
