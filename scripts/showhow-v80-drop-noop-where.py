#!/usr/bin/env python3
# showhow v80 — ถอด op.where ที่ "ไม่ทำงาน" ออกจาก mnBoard2-6 (2026-09-23)
#
# 🔴 v79 ข้อ ① ใช้ไม่ได้ — ผมอ่าน engine ไม่ครบเอง
#    engine-run.ts:115 รองรับ `op.where` จริง (ประเมินกับ item)
#    **แต่เส้นทางจริงของเราเดินผ่าน `auto.productLoop`** ซึ่ง runProductLoop.ts:134 ทำแบบนี้:
#        return { ...gop, where: 'refs.' + ref + '~' + prod.id }     ← **เขียนทับ ไม่ได้ AND**
#    ⇒ `where` ของ op ถูกทิ้งทั้งดุ้น · บรรทัด 9 ของไฟล์นั้นเขียนกำกับไว้ด้วยซ้ำว่า "gens ห้ามมี op.where ของตัวเอง"
#    พิสูจน์จากของจริง: บอร์ดช่วง 2/3 ยังถูกวาดครบ แผนยังเป็น 6 ชิ้นสื่อ
#
# 🪤 บทเรียน: **"engine รองรับ" ≠ "เส้นทางที่เราใช้จริงรองรับ"**
#    ผมเห็นฟีเจอร์ในซอร์สแล้วรีบสรุป โดยไม่ได้ไล่ว่า op ของเราถูกเรียกผ่านทางไหน
#    (ตระกูลเดียวกับบทเรียน `op.when` ที่ประเมินโดยไม่มี item)
#
# ⇒ ถอดออกก่อน ไม่ปล่อยค้างไว้ให้คนอ่านรอบหน้าเข้าใจผิดว่ามีการกรองอยู่
#    ขอ starter แก้ productLoop ให้ **AND** แทนการเขียนทับ (matchWhereAll รับ array อยู่แล้ว):
#        where: [...(gop.where ? [gop.where] : []), 'refs.' + ref + '~' + prod.id]
#    พอ engine รองรับ ค่อยใส่กลับด้วยสคริปต์ v79 บรรทัดเดิม
# ✅ ข้อ ② ของ v79 (คำสั่งต่อเนื่องในช่วงต่อเฟรม) **ไม่ได้แตะ** — ส่วนนั้นทำงานปกติ
import json, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'showhow-dev.json'
c = json.load(open(P, encoding='utf-8'))
ARC = 'ไทม์แลปส์กล้องนิ่ง'

dropped = []
for op in c['ops']:
    if op['id'].startswith('mnBoard') and op.get('where') == 'arc!=' + ARC:
        del op['where']
        dropped.append(op['id'])
assert len(dropped) == 5, dropped

s = json.dumps(c, ensure_ascii=False)
assert '"where": "arc!=' not in s
assert s.count('CONTINUATION: the opening frame is supplied') == 5, 'ข้อ ② ต้องยังอยู่ครบ'
json.dump(c, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v80 ok · ถอด where ที่ไม่ทำงานออกจาก', dropped)
print('        ข้อ ② (CONTINUATION) ยังอยู่ครบ 5 ช่วง')
